from whitebox_workflows import WbEnvironment
wbe = WbEnvironment()

from osgeo import gdal, ogr, osr
import rasterio
import numpy as np
from skimage.morphology import skeletonize
import os
import geopandas as gpd
import pandas as pd
import multiprocessing as mp
import pyogrio

from mtm_utils.variables import (
    HW_DATA_DIR,
    HW_TEMP_DIR,
    HW_OUTPUT_DIR,
    INPUT_HIGHWALLS
)

wbe.working_directory = HW_DATA_DIR


def data_dir_creation():
    """
    Makes temp and output directories if they do not exist.
    """
    os.makedirs(HW_TEMP_DIR, exist_ok=True)
    os.makedirs(HW_OUTPUT_DIR, exist_ok=True)


vector_lines = []

# Skeletonize and vectorize a single highwall geometry
def process_highwall(args):
    idx, row, proj_crs = args

    # Define file paths
    highwall_id = f'highwall_{idx}'
    polygon_path = HW_TEMP_DIR + f"{highwall_id}_polygon.shp"
    raster_path = HW_TEMP_DIR + f"{highwall_id}_raster.tif"
    skeleton_path = HW_TEMP_DIR + f"{highwall_id}_skeleton.tif"
    despurred_path = HW_TEMP_DIR + f"{highwall_id}_despurred.tif"
    line_path = HW_TEMP_DIR + f"{highwall_id}_lines.shp"

    if not os.path.exists(line_path):

        # Convert single highwall geometry to its own shapefile
        geom = gpd.GeoDataFrame([row], crs=proj_crs)
        geom.to_file(polygon_path)
        
        # Rasterize polygon at 1m resolution
        infile = ogr.Open(polygon_path)
        highwall_layer = infile.GetLayer()
        xmin, xmax, ymin, ymax = highwall_layer.GetExtent()
        # print(xmin, xmax, ymin, ymax)

        pixel_size = 0.1
        no_data_value = -9999
        rdtype = gdal.GDT_Byte
        projection = 32617

        x_res = int(round((xmax - xmin) / pixel_size))
        y_res = int(round((ymax - ymin) / pixel_size))

        target_ds = gdal.GetDriverByName("GTiff").Create(
            raster_path, x_res, y_res, 1, eType=rdtype, options=["COMPRESS=DEFLATE"]
        )
        target_ds.SetGeoTransform(
            (xmin, pixel_size, 0.0, ymax, 0.0, -pixel_size)
        )  # specify boundaries of output raster

        # Specify projection of intermediate output raster
        srse = osr.SpatialReference()  # srse represents a SpatialReference instance
        srse.ImportFromEPSG(projection)  # import projection of output raster
        target_ds.SetProjection(
            srse.ExportToWkt()
        )  # set the projection of the output raster

        # Bands
        band = target_ds.GetRasterBand(1)  # only 1 band in our raster
        target_ds.GetRasterBand(1).SetNoDataValue(no_data_value)
        band.Fill(no_data_value)

        print("Starting rasterization...")
        gdal.RasterizeLayer(
            target_ds,
            [1],
            highwall_layer,
            None,
            None,
            burn_values=[1],
            options=["ALL_TOUCHED=TRUE"],
        )
        target_ds = None
        print("Rasterization finished.")

        # Delete intermediate files.
        os.remove(polygon_path)
        os.remove(HW_TEMP_DIR + f"{highwall_id}_polygon.cpg")
        os.remove(HW_TEMP_DIR + f"{highwall_id}_polygon.dbf")
        os.remove(HW_TEMP_DIR + f"{highwall_id}_polygon.prj")
        os.remove(HW_TEMP_DIR + f"{highwall_id}_polygon.shx")
        print('Polygon files deleted.')
        
        # Skeletonize
        with rasterio.open(raster_path) as src:
            raster = src.read(1)  # Read the first band
            transform = src.transform
            crs = proj_crs

        # Step 2: Convert to binary mask (assuming it's a grayscale image)
        binary_raster = (raster > 0).astype(np.uint8)  # Convert non-zero values to 1

        # Step 3: Skeletonize the binary image
        print('Starting skeletonization...')
        skeleton = skeletonize(binary_raster, method="zhang")

        # Step 4: Save skeletonized raster to a new TIFF
        with rasterio.open(
            skeleton_path,
            "w",
            driver="GTiff",
            height=skeleton.shape[0],
            width=skeleton.shape[1],
            count=1,
            dtype=rasterio.uint8,
            crs=proj_crs,
            transform=transform,
        ) as dst:
            dst.write(skeleton.astype(rasterio.uint8), 1)

        print('Skeletonization finished.')
    
        # Delete intermediate files.
        os.remove(raster_path)
        print('Raster deleted.')

        # Remove spurs
        print('Removing spurs...')
        raster = wbe.read_raster(skeleton_path)
        despurred = wbe.remove_spurs(raster, 6)
        wbe.write_raster(despurred, despurred_path, True)
        print('Spurs removed.')
        
        # Delete intermediate files.
        os.remove(skeleton_path)
        print('Skeleton deleted.')

        # Vectorize skeleton
        print('Vectorizing...')
        vectorized = wbe.raster_to_vector_lines(despurred)
        wbe.write_vector(vectorized, line_path)
        print('Vectorizing finished.')
        
        # Delete intermediate files.
        os.remove(despurred_path)
        print('Despurred deleted.')

        # return line_path
    vector_lines.append(gpd.read_file(line_path))
    # print(f'Vector lines list: {vector_lines}')
    return vector_lines


# Iterate through all polygons in a shapefile
def parallelize():
    gdf = gpd.read_file(INPUT_HIGHWALLS)
    proj_crs = gdf.crs
    
    # Process highwalls
    with mp.Pool(mp.cpu_count()) as pool:
        # results = 
        final_list = pool.map(process_highwall, [(idx, row, proj_crs) for idx, row in gdf.iterrows()])
    
    print(f'Processed {len(final_list)} files and appended to list.')
    print(final_list)
    print('All highwalls processed. Merging vectors...')

    # Merge results into one shapefile    
    
    series = pd.Series(final_list)
    merged = pd.concat(series)
    merged_gdf = gpd.GeoDataFrame(merged)
    
    # merged_gdf = gpd.GeoDataFrame(pd.concat([gpd.read_file(f) for f in results], ignore_index=True), crs=proj_crs)

    # Alt method using pyogio instead of geopandas to read files (potentially faster?)
    # shapefiles = [os.path.join(temps, f) for f in os.listdir(temps) if f.endswith(".shp")]
    # gdfs = [gpd.GeoDataFrame(pyogrio.read_dataframe(shp)) for shp in shapefiles]
    # merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    output_shp = HW_OUTPUT_DIR + "skeletonize_al_test.shp"
    merged_gdf.to_file(output_shp)
    print(f"Processing complete. Output saved to {output_shp}")


if __name__ == "__main__":
    data_dir_creation()
    parallelize()