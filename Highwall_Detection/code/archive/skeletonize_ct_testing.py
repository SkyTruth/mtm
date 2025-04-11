from whitebox_workflows import WbEnvironment


from osgeo import gdal, ogr, osr
import rasterio
import numpy as np
from skimage.morphology import skeletonize


def inital_rasterize():
    # highwall = "unreclaimed_cleaned.shp"
    highwall = "test_set.shp"

    infile = ogr.Open(highwall)
    highwall_layer = infile.GetLayer()
    xmin, xmax, ymin, ymax = highwall_layer.GetExtent()
    print(xmin, xmax, ymin, ymax)

    pixel_size = 0.1
    no_data_value = -9999
    # rdtype = gdal.GDT_Float32
    rdtype = gdal.GDT_Byte
    projection = 32617

    x_res = int(round((xmax - xmin) / pixel_size))
    y_res = int(round((ymax - ymin) / pixel_size))

    # outfile = "unreclaimed_cleaned.tiff"
    outfile = "FINAL_test_set.tiff"

    target_ds = gdal.GetDriverByName("GTiff").Create(
        outfile, x_res, y_res, 1, eType=rdtype, options=["COMPRESS=DEFLATE"]
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


def initial_skeletonize():
    # with rasterio.open("unreclaimed_cleaned.tiff") as src:
    with rasterio.open("FINAL_test_set.tiff") as src:
        raster = src.read(1)  # Read the first band
        transform = src.transform
        crs = src.crs

    # Step 2: Convert to binary mask (assuming it's a grayscale image)
    binary_raster = (raster > 0).astype(np.uint8)  # Convert non-zero values to 1

    # Step 3: Skeletonize the binary image
    skeleton = skeletonize(binary_raster, method="zhang")

    # Step 4: Save skeletonized raster to a new TIFF
    output_tiff = "FINAL_skeletonized_test_set_zhang.tif"
    # output_tiff = "skeletonized_unreclaimed_cleaned_zhang.tif"
    with rasterio.open(
        output_tiff,
        "w",
        driver="GTiff",
        height=skeleton.shape[0],
        width=skeleton.shape[1],
        count=1,
        dtype=rasterio.uint8,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(skeleton.astype(rasterio.uint8), 1)


def final_cleaning():
    print("Running coded from the best processing library in the world...")
    wbe = WbEnvironment()
    # print(wbe.version()) # Print the version number

    # raster = wbe.read_raster('skeletonized_unreclaimed_cleaned_zhang.tif') # Read some kind of data
    raster = wbe.read_raster(
        "FINAL_skeletonized_test_set_zhang.tif"
    )  # Read some kind of data
    # print(raster)

    # def remove_spurs(self, raster: Raster, max_iterations: int = 10) -> Raster: ...
    # Remove Spur, Thin, and Convert to Vector
    despurred = wbe.remove_spurs(raster, 6)
    thinned = wbe.line_thinning(despurred)
    vectorized = wbe.raster_to_vector_lines(thinned)

    # Write Outfiles
    wbe.write_raster(despurred, "skeletonized_test_set_zhang_depurred.tif", True)
    wbe.write_raster(thinned, "skeletonized_test_set_zhang_depurred_thinned.tif", True)
    wbe.write_vector(vectorized, "FULLY_CLEANED.shp")


if __name__ == "__main__":
    # testing()
    inital_rasterize()
    initial_skeletonize()
    final_cleaning()