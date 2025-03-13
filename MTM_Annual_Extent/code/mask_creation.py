import os
import pandas as pd
import geopandas as gpd
import glob
from google.cloud import storage
import requests
import wget
from zipfile import ZipFile
from osgeo import gdal, ogr, osr


from mtm_utils.variables import (
    PROCESSING_YEAR,
    MASK_DIR,
    MASK_INTERIM,
    MASK_FINAL,
    FIPS_CODES,
    STUDY_AREA_GJS,
    STUDY_AREA_SHP,
    STUDY_AREA_ZIP,
    USCB_YEAR,
    USCB_GJS,
    USCB_SHP,
    USCB_ZIP,
    GCLOUD_BUCKET,
    GCLOUD_MASK_DIR,
)

# To Process mask data for a year that is not the current yearm change the variables in mtm_utils/variables.py


def url_exists(url):
    response = requests.head(url)
    return response.status_code == 200


def data_dir_creation():
    # Check if Data Directories exist for USCB data for PROCESSING_YEAR, and making them if they do not
    os.makedirs(USCB_YEAR, exist_ok=True)
    os.makedirs(USCB_GJS, exist_ok=True)
    os.makedirs(USCB_SHP, exist_ok=True)
    os.makedirs(USCB_ZIP, exist_ok=True)

    # Check if Data Directories exist for Mask Directories data for PROCESSING_YEAR, and making them if they do not
    os.makedirs(MASK_DIR, exist_ok=True)
    os.makedirs(MASK_INTERIM, exist_ok=True)
    os.makedirs(MASK_FINAL, exist_ok=True)


def data_download():
    print(
        f"Beginning the MTM Mask creation process; downloading data from the USCB for the year {PROCESSING_YEAR}."
    )
    max_fips_codes = len(FIPS_CODES)

    """
    Download USCB data for Area water, linear water, and roads.
    """
    print("     > Downloading Roads, Area Water, and Linear Water data...")
    for i in range(max_fips_codes):
        # Define file names using processing year and FIPS codes
        roads_file = f"tl_{PROCESSING_YEAR}_{FIPS_CODES[i]}_roads.zip"
        areaW_file = f"tl_{PROCESSING_YEAR}_{FIPS_CODES[i]}_areawater.zip"
        lineW_file = f"tl_{PROCESSING_YEAR}_{FIPS_CODES[i]}_linearwater.zip"

        # Define the URLs for the data stored by USCB for download
        rd_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/ROADS/{roads_file}"
        aw_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/AREAWATER/{areaW_file}"
        lw_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/LINEARWATER/{lineW_file}"

        # Download the data from USCB
        wget.download(rd_url, out=USCB_ZIP)
        wget.download(aw_url, out=USCB_ZIP)
        wget.download(lw_url, out=USCB_ZIP)
    print("     > Done")

    """
    Download USCB data for Urban Areas data. Check to see if data using the 2010 UAC is available for the current year,
    which included smaller areas called urban clusters, and if it is not available, download it from 2022 which is a
    year where it is known to be provided.
    """
    print("     > Downloading Urban Areas data...")
    uac_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/UAC20/tl_{PROCESSING_YEAR}_us_uac20.zip"
    # https://www2.census.gov/geo/tiger/TIGER2024/UAC20/tl_2024_us_uac20.zip
    uac_10_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/UAC/tl_{PROCESSING_YEAR}_us_uac10.zip"

    # Check if the UAC is listed as UAC or UAC20
    if url_exists(uac_url):
        print(f"URL Exists: {uac_url}")
        wget.download(uac_url, out=USCB_ZIP)
        print("     > Done")
    else:
        uac_url = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}/UAC/tl_{PROCESSING_YEAR}_us_uac20.zip"
        wget.download(uac_url, out=USCB_ZIP)
        print(f"     > UAC for {PROCESSING_YEAR} listed as UAC and not UAC20.")

    # Check if the UAC10 exists
    if url_exists(uac_10_url):
        print(f"URL Exists: {uac_10_url}")
        wget.download(uac_10_url, out=USCB_ZIP)
        print("     > Done")
    else:
        uac_10_url = (
            "https://www2.census.gov/geo/tiger/TIGER2022/UAC/tl_2022_us_uac10.zip"
        )
        wget.download(uac_10_url, out=USCB_ZIP)
        print("     > 2010 UAC downloaded from 2022 Directory.")

    """
    Download the SkyTruth MTM Study Area bounds, if they have not been downloaded.
    """
    study_area_url = "https://skytruth.org/MTR/MTR_Data/Other-Data/Study-Area.zip"

    print(STUDY_AREA_ZIP + "Study-Area.zip")
    if os.path.exists(STUDY_AREA_ZIP + "Study-Area.zip"):
        print("     > MTM Study Area boundary already downloaded...")
        print("     > Done")
    else:
        print("     > Downloading MTM Study Area boundary...")
        wget.download(study_area_url, out=STUDY_AREA_ZIP)
        print("     > Done")


def data_processing():
    print(f"Processing the data from the USCB for the year {PROCESSING_YEAR}.")
    uscb_zip_list = sorted(
        list(filter(lambda zip: ".zip" in zip, os.listdir(USCB_ZIP)))
    )

    for i in uscb_zip_list:
        infile = glob.glob(USCB_ZIP + i)[0]
        outfile = i.strip(".zip") + ".shp"

        # Check if the outfiles already exist, if they don't unzip them, if they do pass
        if os.path.isfile(USCB_SHP + outfile):
            pass
        else:
            print(f" > Unzipping {i} writing to {USCB_SHP+outfile}")
            ZipFile(infile).extractall(path=USCB_SHP)

    print("\nFINISHED UNZIPPING FILES\n")

    # Unzip the MTM Study Area
    study_area_zip_list = sorted(
        list(filter(lambda zip: ".zip" in zip, os.listdir(STUDY_AREA_ZIP)))
    )
    for i in study_area_zip_list:
        infile = glob.glob(STUDY_AREA_ZIP + i)[0]
        outfile = i.strip(".zip") + ".shp"

        # Check if the outfiles already exist, if they don't unzip them, if they do pass
        if os.path.isfile(STUDY_AREA_SHP + outfile):
            pass
        else:
            print(f" > Unzipping {i} writing to {STUDY_AREA_SHP+outfile}")
            ZipFile(infile).extractall(path=STUDY_AREA_SHP)

    print("\nBEGINNING CONVERSION TO GEOJSON\n")

    # Convert the Shapefiles to GeoJSON
    uscb_shp_list = sorted(
        list(filter(lambda shp: ".shp" in shp, os.listdir(USCB_SHP)))
    )
    uscb_shp_list = [x for x in uscb_shp_list if ".iso" not in x]
    study_area_shp_list = sorted(
        list(filter(lambda shp: ".shp" in shp, os.listdir(STUDY_AREA_SHP)))
    )

    for i in uscb_shp_list:
        infile = glob.glob(USCB_SHP + i)[0]
        outfile = i.strip(".shp") + ".geojson"

        if os.path.isfile(USCB_GJS + outfile):
            pass
        else:
            gdf = gpd.read_file(USCB_SHP + i)
            gdf.to_file(USCB_GJS + outfile, driver="GeoJSON")

    for i in study_area_shp_list:
        infile = glob.glob(STUDY_AREA_SHP + i)[0]
        outfile = i.strip(".shp") + ".geojson"

        if os.path.isfile(STUDY_AREA_GJS + outfile):
            pass
        else:
            gdf = gpd.read_file(STUDY_AREA_SHP + i)
            # print(gdf.head(1))
            gdf.to_file(STUDY_AREA_GJS + outfile, driver="GeoJSON")

    print("\nFINISHED CONVERSION TO GEOJSON\n")


def mask_creation():
    print("\n\nBEGINNING MASK CREATION PROCESS - GEOJSON MERGE\n\n")
    geojson_list = sorted(
        list(filter(lambda geojson: ".geojson" in geojson, os.listdir(USCB_GJS)))
    )

    mtm_study_area = gpd.read_file(STUDY_AREA_GJS + "Study-Area.geojson")
    outfile = f"{PROCESSING_YEAR}_USCB_data_buffered_merged_3857.geojson"
    outfile_2 = f"{PROCESSING_YEAR}_USCB_data_buffered_merged_3857.shp"

    if os.path.isfile(MASK_INTERIM + outfile):
        print("Mask file exists.")
        pass

    else:
        processed_geojson = []
        for i in geojson_list:
            if "uac" in i:
                print("Processing Urban Areas data, clipping to study area bounds")
                gdf = gpd.read_file(USCB_GJS + i)
                reproj_gdf = gdf.to_crs(4326)
                gdf_clipped = reproj_gdf.clip(mtm_study_area)  # , keep_geom_type=True)
                reproj = gdf_clipped.to_crs(5072)
                exploded_gdf = reproj.explode(index_parts=False)
                exploded_gdf["geometry"] = exploded_gdf.geometry.buffer(60)
                dissolved = exploded_gdf.dissolve()
                processed_geojson.append(dissolved)
            else:
                gdf = gpd.read_file(USCB_GJS + i)
                reproj = gdf.to_crs(5072)
                exploded_gdf = reproj.explode(index_parts=False)
                exploded_gdf["geometry"] = exploded_gdf.geometry.buffer(60)
                dissolved = exploded_gdf.dissolve()
                processed_geojson.append(dissolved)
        merged = pd.concat(processed_geojson)
        final_merge = gpd.GeoDataFrame(merged)
        final_merge_reproj = final_merge.to_crs(3857)
        final_merge_reproj.to_file(MASK_INTERIM + outfile, driver="GeoJSON")
        final_merge_reproj.to_file(MASK_INTERIM + outfile_2)


def mask_rasterization_pt1():
    print("\n\nBEGINNING MASK RASTERIZATION PROCESS\n\n")
    infile = f"{PROCESSING_YEAR}_USCB_data_buffered_merged_3857.shp"
    outfile = f"{PROCESSING_YEAR}_Input-Mask_interim_3857.tiff"

    if os.path.isfile(MASK_INTERIM + outfile):
        print(f"Outfile, {outfile}, already exists")
        pass
    else:
        # open the shapefile.
        try:
            geojson = ogr.Open(MASK_INTERIM + infile)
            print("Opened")
            # print(geojson)
        except RuntimeError as e:
            print("Error: Could not open shapefile. Please try again.")

        geojson_layer = geojson.GetLayer()
        xmin, xmax, ymin, ymax = geojson_layer.GetExtent()

        print(f"X-Min: {xmin}\nX-Max: {xmax}")
        print(f"Y-Min: {ymin}\nY-Max: {ymax}")

        pixel_size = 15
        no_data_value = -9999
        # rdtype = gdal.GDT_Float32
        rdtype = gdal.GDT_Byte
        projection = 3857

        x_res = int(round((xmax - xmin) / pixel_size))
        y_res = int(round((ymax - ymin) / pixel_size))

        target_ds = gdal.GetDriverByName("GTiff").Create(
            MASK_INTERIM + outfile,
            x_res,
            y_res,
            1,
            eType=rdtype,
            options=["COMPRESS=DEFLATE"],
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
            geojson_layer,
            None,
            None,
            burn_values=[1],
            options=["ALL_TOUCHED=TRUE"],
        )
        target_ds = None
        print("Rasterization finished.")


def mask_rasterization_pt2():
    infile = f"{PROCESSING_YEAR}_Input-Mask_interim_3857.tiff"
    outfile = f"{PROCESSING_YEAR}_Input-Mask_4326.tiff"
    input_raster = gdal.Open(MASK_INTERIM + infile)

    if os.path.isfile(MASK_FINAL + outfile):
        print(f"Outfile, {outfile}, already exists")
        pass
    else:
        print("\n\nFINALIZING MASK RASTERIZATION\n\n")
        print("Beginning raster mask reprojection.\n")
        input_raster = gdal.Open(MASK_INTERIM + infile)
        gdal.Warp(
            destNameOrDestDS=MASK_FINAL + outfile,
            srcDSOrSrcDSTab=input_raster,
            options="-co TILED=YES -co COMPRESS=DEFLATE -co INTERLEAVE=BAND -co PREDICTOR=2 -t_srs EPSG:4326 -wo CUTLINE_ALL_TOUCHED=TRUE",
        )

        print("FINISHED RASTER MASK REPROJECTION.")


def mask_upload():
    print(f"\n\nBEGINNING MASK UPLOAD TO GCS...")

    infile = f"{PROCESSING_YEAR}_Input-Mask_4326.tiff"
    outfile_name = infile
    infile_path = MASK_FINAL + infile

    bucket_name = GCLOUD_BUCKET
    storage_bucket = storage.Client("skytruth-tech").bucket(bucket_name)

    out_blob = storage_bucket.blob(GCLOUD_MASK_DIR + outfile_name)

    # Check if the outfile already exists. If it does: pass. If it doesn't: write it.
    if out_blob.exists():
        print("  > OUTFILE ALREADY EXISTS. PASSING.")
        pass
    else:
        print("  > OUTFILE DOESN'T EXIST. UPLOADING.")
        blob = out_blob
        blob.upload_from_filename(infile_path, content_type="image/tiff")
        print(
            f"  > Outfile {outfile_name} uploaded to gs://{GCLOUD_BUCKET}/{GCLOUD_MASK_DIR}{outfile_name}"
        )


if __name__ == "__main__":
    data_dir_creation()
    data_download()
    data_processing()
    mask_creation()
    mask_rasterization_pt1()
    mask_rasterization_pt2()
    mask_upload()
