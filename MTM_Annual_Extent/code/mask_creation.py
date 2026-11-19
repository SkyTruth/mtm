import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd
import geopandas as gpd
from google.cloud import storage
import requests
import numpy as np
import rasterio
from rasterio import features
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import Window, bounds as window_bounds
from shapely.geometry import box

from mtm_utils.variables import (
    PROCESSING_YEAR,
    MASK_DIR,
    MASK_INTERIM,
    MASK_FINAL,
    FIPS_CODES,
    STUDY_AREA_ZIP,
    USCB_YEAR,
    USCB_ZIP,
    GCLOUD_BUCKET,
    GCLOUD_MASK_DIR,
)

# To Process mask data for a year that is not the current yearm change the variables in mtm_utils/variables.py


def url_exists(url):
    return requests.head(url, timeout=30).status_code == 200


def fetch(url, out_dir=USCB_ZIP):
    # Skip files already downloaded; write to .part first so an interrupted download isn't kept
    dest = out_dir + url.rsplit("/", 1)[-1]
    if os.path.exists(dest):
        return dest
    tmp = dest + ".part"
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    os.replace(tmp, dest)
    return dest


def data_dir_creation():
    # Check if Data Directories exist for USCB data for PROCESSING_YEAR, and making them if they do not
    os.makedirs(USCB_YEAR, exist_ok=True)
    os.makedirs(USCB_ZIP, exist_ok=True)

    # Check if Data Directories exist for Mask Directories data for PROCESSING_YEAR, and making them if they do not
    os.makedirs(MASK_DIR, exist_ok=True)
    os.makedirs(MASK_INTERIM, exist_ok=True)
    os.makedirs(MASK_FINAL, exist_ok=True)


def data_download():
    print(
        f"Beginning the MTM Mask creation process; downloading data from the USCB for the year {PROCESSING_YEAR}."
    )
    base = f"https://www2.census.gov/geo/tiger/TIGER{PROCESSING_YEAR}"

    """
    Download USCB data for Area water, linear water, and roads.
    """
    urls = [
        f"{base}/{folder}/tl_{PROCESSING_YEAR}_{fips}_{layer}.zip"
        for fips in FIPS_CODES
        for folder, layer in (
            ("ROADS", "roads"),
            ("AREAWATER", "areawater"),
            ("LINEARWATER", "linearwater"),
        )
    ]

    """
    Download USCB data for Urban Areas data. Check to see if data using the 2010 UAC is available for the current year,
    which included smaller areas called urban clusters, and if it is not available, download it from 2022 which is a
    year where it is known to be provided.
    """
    uac_url = f"{base}/UAC20/tl_{PROCESSING_YEAR}_us_uac20.zip"
    if not url_exists(uac_url):
        uac_url = f"{base}/UAC/tl_{PROCESSING_YEAR}_us_uac20.zip"
        print(f"     > UAC for {PROCESSING_YEAR} listed as UAC and not UAC20.")
    urls.append(uac_url)

    uac_10_url = f"{base}/UAC/tl_{PROCESSING_YEAR}_us_uac10.zip"
    if not url_exists(uac_10_url):
        uac_10_url = "https://www2.census.gov/geo/tiger/TIGER2022/UAC/tl_2022_us_uac10.zip"
        print("     > 2010 UAC will be downloaded from 2022 Directory.")
    urls.append(uac_10_url)

    print(f"     > Downloading {len(urls)} USCB files (existing files are skipped)...")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(fetch, urls))
    print("     > Done")


def buffer_layer(path, study_area=None):
    """Read one USCB layer from its zip and return 60 m buffers in EPSG:3857."""
    gdf = gpd.read_file(path, columns=[])
    if study_area is not None:
        gdf = gdf.to_crs(4326).clip(study_area)
    buffered = gdf.to_crs(5072).buffer(60)
    return gpd.GeoDataFrame(geometry=buffered, crs=5072).to_crs(3857)


def mask_creation():
    print("\n\nBEGINNING MASK CREATION PROCESS - BUFFER\n\n")
    outfile = f"{PROCESSING_YEAR}_USCB_data_buffered_3857.fgb"

    if os.path.isfile(MASK_INTERIM + outfile):
        print("Mask file exists.")
        return gpd.read_file(MASK_INTERIM + outfile)

    mtm_study_area = gpd.read_file(f"zip://{STUDY_AREA_ZIP}Study-Area.zip!Study-Area.shp")
    zips = sorted(f for f in os.listdir(USCB_ZIP) if f.endswith(".zip"))
    paths = [USCB_ZIP + f for f in zips]
    study_areas = [mtm_study_area if "uac" in f else None for f in zips]

    with ProcessPoolExecutor(max_workers=8) as pool:
        layers = list(pool.map(buffer_layer, paths, study_areas))

    merged = gpd.GeoDataFrame(pd.concat(layers, ignore_index=True), crs=3857)
    merged.to_file(MASK_INTERIM + outfile, driver="FlatGeobuf")
    return merged


def mask_rasterization_pt1(gdf=None):
    print("\n\nBEGINNING MASK RASTERIZATION PROCESS\n\n")
    outfile = f"{PROCESSING_YEAR}_Input-Mask_interim_3857_v2.tiff"

    if os.path.isfile(MASK_INTERIM + outfile):
        print(f"Outfile, {outfile}, already exists")
        return

    if gdf is None:
        gdf = gpd.read_file(MASK_INTERIM + f"{PROCESSING_YEAR}_USCB_data_buffered_3857.fgb")

    xmin, ymin, xmax, ymax = gdf.total_bounds

    print(f"X-Min: {xmin}\nX-Max: {xmax}")
    print(f"Y-Min: {ymin}\nY-Max: {ymax}")

    pixel_size = 15
    width = int(round((xmax - xmin) / pixel_size))
    height = int(round((ymax - ymin) / pixel_size))
    transform = from_origin(xmin, ymax, pixel_size, pixel_size)

    profile = {
        "driver": "GTiff",
        "width": width,
        "height": height,
        "count": 1,
        "dtype": "uint8",
        "crs": "EPSG:3857",
        "transform": transform,
        "compress": "deflate",
        "nodata": None,
    }

    print("Starting rasterization...")
    strip = 1024  # rows per chunk, so the whole raster is never held in memory
    with rasterio.open(MASK_INTERIM + outfile, "w", **profile) as dst:
        for row in range(0, height, strip):
            window = Window(0, row, width, min(strip, height - row))
            hits = gdf.sindex.query(box(*window_bounds(window, transform)))
            if len(hits) == 0:
                burned = np.zeros((window.height, window.width), dtype="uint8")
            else:
                burned = features.rasterize(
                    ((geom, 1) for geom in gdf.geometry.iloc[hits]),
                    out_shape=(window.height, window.width),
                    transform=dst.window_transform(window),
                    fill=0,
                    all_touched=True,
                    dtype="uint8",
                )
            dst.write(burned, 1, window=window)
    print("Rasterization finished.")


def mask_rasterization_pt2():
    infile = f"{PROCESSING_YEAR}_Input-Mask_interim_3857_v2.tiff"
    outfile = f"{PROCESSING_YEAR}_Input-Mask_4326_v2.tiff"

    if os.path.isfile(MASK_FINAL + outfile):
        print(f"Outfile, {outfile}, already exists")
        return

    print("\n\nFINALIZING MASK RASTERIZATION\n\n")
    print("Beginning raster mask reprojection.\n")
    dst_crs = "EPSG:4326"
    with rasterio.open(MASK_INTERIM + infile) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        profile = src.profile.copy()
        profile.update(
            crs=dst_crs,
            transform=transform,
            width=width,
            height=height,
            tiled=True,
            blockxsize=256,
            blockysize=256,
            compress="deflate",
            predictor=2,
            interleave="band",
        )
        with rasterio.open(MASK_FINAL + outfile, "w", **profile) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                resampling=Resampling.nearest,
            )
    print("FINISHED RASTER MASK REPROJECTION.")


def mask_upload():
    print(f"\n\nBEGINNING MASK UPLOAD TO GCS...")

    infile = f"{PROCESSING_YEAR}_Input-Mask_4326_v2.tiff"
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
    gdf = mask_creation()
    mask_rasterization_pt1(gdf)
    mask_rasterization_pt2()
    mask_upload()
