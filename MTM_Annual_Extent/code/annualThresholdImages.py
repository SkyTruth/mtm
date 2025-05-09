import ee
import datetime
import time
from ee import batch
from google.cloud import storage

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIALS
from mtm_utils.variables import (
    PROCESSING_YEAR, 
    GCLOUD_BUCKET,
    GCLOUD_EE_GPC_DIR,
    GCLOUD_MASK_DIR,
    GCLOUD_EE_THRESHOLD_DIR,
    FIPS_CODES,
)


processing_year = PROCESSING_YEAR

# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
print(f"STORAGE BUCKET:{storage_bucket}\n\n")

credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)
ee.Initialize(credentials)

########################################################################################################################
########################################################################################################################
"""Preparing the Greenest Pixel Composites"""
img_name_list = []

# Get all the images produced from greenestPixelComp.py
for img in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_GPC_DIR):
    img_name = img.name
    img_name_list.append(img_name)

# The img.name also grabs the folder the images are stored in, use .pop(0) to remove this so we can create the GS
# URLs for all the images (that are used to make a GEE image collection later).
img_name_list.pop(0)

img_url_list = []
img_date_list = []

for i in img_name_list:
    img_url = "gs://" + bucket_name + "/" + i
    img_url_list.append(img_url)

greenestPixelCompositeList = []

for i in range(1984, processing_year + 1):
    year = i
    annual_urls = []
    
    # Merging the split GPC images into single GEE Images
    for url in img_url_list:
        url_year = url.split("composite_")[1].split("0000000000-")[0]
        if str(year) in url_year:
            img_url = url
            annual_urls.append(img_url)

    image_1 = annual_urls[0]
    image_2 = annual_urls[1]
    # print(f"Year - {year}\n    > GPC pt1: {image_1}\n    > GPC pt1: {image_2}")

    ee_image_pt1 = ee.Image.loadGeoTIFF(image_1)
    ee_image_pt2 = ee.Image.loadGeoTIFF(image_2)

    # There isn't overlap of the images, so a median reducer works well to create an image.
    ee_image = ee.ImageCollection([ee_image_pt1, ee_image_pt2]).median()
    ee_image = ee_image.set("year", year)
    greenestPixelCompositeList.append(ee_image)

########################################################################################################################
########################################################################################################################

greenestComposites = ee.ImageCollection.fromImages(greenestPixelCompositeList)
studyArea = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/studyArea"
)
studyAreaGeom = studyArea.geometry().getInfo()["coordinates"]
exportBounds = ee.Geometry.Polygon(studyAreaGeom)

fips_codes = FIPS_CODES

allCounties = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/allCounties"
)
features = allCounties.filter(ee.Filter.inList("FIPS", fips_codes))

mask_url = (
    "gs://"
    + bucket_name
    + "/"
    + GCLOUD_MASK_DIR
    + str(processing_year)
    + "_Input-Mask_4326.tiff"
)
mask_input_60m = ee.Image.loadGeoTIFF(mask_url).unmask()

miningPermits = ee.Image("users/andrewpericak/allMinePermits")
miningPermits_noBuffer = ee.Image("users/andrewpericak/allMinePermits_noBuffer")

mask_input_excludeMines = mask_input_60m.where(miningPermits_noBuffer.eq(1), 0)


def reduce_region(feature):
    final = (
        yearImage.reduceRegion(
            reducer=ee.Reducer.intervalMean(0, 3),
            geometry=feature.geometry(),
            scale=30,
            maxPixels=1e10,
        )
        .toImage()
        .toFloat()
        .clip(feature)
    )
    return final


for i in range(1984, processing_year + 1):
    year = i
    export_desc = "threshold_0-3_" + str(year)

    yearImage = (
        ee.Image(greenestComposites.filterMetadata("year", "equals", year).first())
        .select("NDVI")
        .updateMask(miningPermits_noBuffer.unmask().Not())
        .updateMask(mask_input_60m.Not())
    )
    exportArea = ee.Geometry.Polygon(
        [
            [
                [-85.80934903683277, 35.64442402256219],
                [-79.61790603657893, 35.64442402256219],
                [-79.61790603657893, 39.02981799180214],
                [-85.80934903683277, 39.02981799180214],
                [-85.80934903683277, 35.64442402256219],
            ]
        ]
    )

    outfile_test_name = GCLOUD_EE_THRESHOLD_DIR + export_desc + ".tif"
    out_blob_test = storage_bucket.blob(outfile_test_name)

    if out_blob_test.exists():
        print(
            f"  > {GCLOUD_EE_THRESHOLD_DIR + export_desc}.tif ALREADY EXISTS. PASSING."
        )
        pass
    else:
        reduceAll = ee.ImageCollection(features.map(reduce_region)).mosaic()

        export = batch.Export.image.toCloudStorage(
            image=reduceAll,
            description=export_desc,
            bucket=GCLOUD_BUCKET,
            fileNamePrefix=GCLOUD_EE_THRESHOLD_DIR + export_desc,
            region=exportArea.getInfo()["coordinates"],
            scale=30,
            crs="EPSG:4326",
            maxPixels=1e13,
            fileFormat="GeoTIFF",
        )
        print(f"writing to {GCLOUD_EE_THRESHOLD_DIR + export_desc}")
        export.start()
        while export.active():
            print(
                f"     > Logging task for {year}  (id: {export.id}). Checks every 1 min."
            )
            time.sleep(60)
        print(f"    > Outfile Status: {ee.data.getTaskStatus(export.id)}")
        print(f"        > {year} threshold image written")
