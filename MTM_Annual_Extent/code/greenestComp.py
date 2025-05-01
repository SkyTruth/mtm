import ee
import datetime
import time
from ee import batch
from google.cloud import storage

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIALS
from mtm_utils.variables import GCLOUD_BUCKET, GCLOUD_EE_GPC_DIR


processing_year = datetime.date.today().year

# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
print(f"STORAGE BUCKET:{storage_bucket}\n\n")

credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)
ee.Initialize(credentials)
########################################################################################################################
########################################################################################################################
"""DEFINE FUNCTIONS"""


def cleaner(outlierValue):
    def data_mask(image):
        min_mask = image.mask().reduce(ee.Reducer.min())
        sat_mask = image.reduce(ee.Reducer.max()).lt(outlierValue)
        new_mask = min_mask.mask(sat_mask).focal_min(3)
        final = ee.Algorithms.Landsat.TOA(image).updateMask(new_mask)
        return final

    return data_mask


def maskClouds(image):
    scored = ee.Algorithms.Landsat.simpleCloudScore(image)
    cloudScored = image.updateMask(scored.select(["cloud"]).lt(20))
    return cloudScored


def addBands_l4(image):
    fin = image.addBands(
        image.expression(
            "( NIR - R ) / ( NIR + R )",
            {"R": image.select("B3"), "NIR": image.select("B4")},
        ).rename("NDVI")
    )

    fin = fin.select(l4_input_list).rename(l4_output_list)
    return fin


def addBands_l5(image):
    fin = image.addBands(
        image.expression(
            "( NIR - R ) / ( NIR + R )",
            {"R": image.select("B3"), "NIR": image.select("B4")},
        ).rename("NDVI")
    )

    fin = fin.select(l5_input_list).rename(l5_output_list)
    return fin


def addBands_l7(image):
    fin = image.addBands(
        image.expression(
            "(NIR - R) / (NIR + R)",
            {"R": image.select("B3"), "NIR": image.select("B4")},
        ).rename("NDVI")
    )

    fin = fin.select(l7_input_list).rename(l7_output_list)
    return fin


def addBands_l8(image):
    fin = image.addBands(
        image.expression(
            "(NIR - R) / (NIR + R)",
            {"R": image.select("B4"), "NIR": image.select("B5")},
        ).rename("NDVI")
    )

    fin = fin.select(l8_input_list).rename(l8_output_list)
    return fin


def addBands_l9(image):
    fin = image.addBands(
        image.expression(
            "(NIR - R) / (NIR + R)",
            {"R": image.select("B4"), "NIR": image.select("B5")},
        ).rename("NDVI")
    )

    fin = fin.select(l8_input_list).rename(l8_output_list)
    return fin


########################################################################################################################
########################################################################################################################
studyArea = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/studyArea"
)
studyAreaGeom = studyArea.geometry().getInfo()["coordinates"]
exportBounds = ee.Geometry.Polygon(studyAreaGeom)

exportAreaBoundingBox = ee.Geometry.Polygon(
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

# Image Collections
lt4_raw = ee.ImageCollection("LANDSAT/LT04/C02/T1").select(
    "B1", "B2", "B3", "B4", "B5", "B6", "B7"
)
lt5_raw = ee.ImageCollection("LANDSAT/LT05/C02/T1").select(
    "B1", "B2", "B3", "B4", "B5", "B6", "B7"
)
le7_raw = ee.ImageCollection("LANDSAT/LE07/C02/T1").select(
    "B1", "B2", "B3", "B4", "B5", "B6_VCID_1", "B6_VCID_2", "B7", "B8"
)
lc8_raw = ee.ImageCollection("LANDSAT/LC08/C02/T1").select(
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11"
)
lc9_raw = ee.ImageCollection("LANDSAT/LC09/C02/T1").select(
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11"
)

# Create the empty mask images which will be used to create matching bands
# between sensors.
blank = ee.Image().mask()
newMaskBand = (
    ee.Image().updateMask(blank).toFloat()
)  # Ran into an issue w/ toInt, trying to Float now

l4_input_list = ["B1", "B2", "B3", "B4", "NDVI"]
l4_output_list = ["B", "G", "R", "NIR", "NDVI"]

l5_input_list = ["B1", "B2", "B3", "B4", "NDVI"]
l5_output_list = ["B", "G", "R", "NIR", "NDVI"]

l7_input_list = ["B1", "B2", "B3", "B4", "NDVI"]
l7_output_list = ["B", "G", "R", "NIR", "NDVI"]

l8_input_list = ["B2", "B3", "B4", "B5", "NDVI"]
l8_output_list = ["B", "G", "R", "NIR", "NDVI"]

l9_input_list = ["B2", "B3", "B4", "B5", "NDVI"]
l9_output_list = ["B", "G", "R", "NIR", "NDVI"]


# Create Image Collection
lt4Collection = (
    lt4_raw.filterBounds(studyArea)
    .filterDate("1984-01-01", "1993-12-31")
    .map(cleaner(250))
    .map(maskClouds)
    .map(addBands_l4)
)
lt5Collection = (
    lt5_raw.filterBounds(studyArea)
    .filterDate("1984-01-01", "2011-12-31")
    .map(cleaner(250))
    .map(maskClouds)
    .map(addBands_l5)
)
le7Collection = (
    le7_raw.filterBounds(studyArea)
    .filterDate("1999-01-01", datetime.datetime.now())
    .filter(ee.Filter.date("2012-08-03", "2012-08-04").Not())
    .map(cleaner(250))
    .map(maskClouds)
    .map(addBands_l7)
)
lc8Collection = (
    lc8_raw.filterBounds(studyArea)
    .filterDate("2013-01-01", datetime.datetime.now())
    .map(cleaner(64256))
    .map(maskClouds)
    .map(addBands_l8)
)
lc9Collection = (
    lc9_raw.filterBounds(studyArea)
    .filterDate("2021-10-31", datetime.datetime.now())
    .map(cleaner(64256))
    .map(maskClouds)
    .map(addBands_l9)
)

lsCollection = ee.ImageCollection(
    (lt4Collection)
    .merge(lt5Collection)
    .merge(le7Collection)
    .merge(lc8Collection)
    .merge(lc9Collection)
)

########################################################################################################################
########################################################################################################################

for i in range(1984, processing_year + 1):
    year = i
    print(f"Processing Imagery for {year}")
    export_desc = "composite_" + str(year)
    outfile_name = GCLOUD_EE_GPC_DIR + export_desc + ".tif"

    # The export to cloud storage splits imagery into two pieces, the outfile_test_name checks if one of the two exists
    outfile_test_name = GCLOUD_EE_GPC_DIR + export_desc + "0000000000-0000000000.tif"

    out_blob = storage_bucket.blob(outfile_name)
    out_blob_test = storage_bucket.blob(outfile_test_name)

    if out_blob_test.exists():
        print(f"  > {GCLOUD_EE_GPC_DIR + export_desc}.tif ALREADY EXISTS. PASSING.")
        pass
    else:
        print(
            f"  > Starting export for {i}, saving to cloud storage @ {GCLOUD_EE_GPC_DIR}"
        )
        composite = (
            lsCollection.filter(ee.Filter.calendarRange(year, year, "year"))
            .filter(ee.Filter.calendarRange(5, 9, "month"))
            .qualityMosaic("NDVI")
            .set("year", year)
        )

        export = batch.Export.image.toCloudStorage(
            image=composite,
            description=export_desc,
            bucket=GCLOUD_BUCKET,
            fileNamePrefix=GCLOUD_EE_GPC_DIR + export_desc,
            region=exportAreaBoundingBox.getInfo()["coordinates"],
            scale=30,
            crs="EPSG:4326",
            maxPixels=1e13,
            fileFormat="GeoTIFF",
        )

        export.start()

        while export.active():
            print(
                f"     > Logging task for {year}  (id: {export.id}). Checks every 5 min."
            )
            time.sleep(300)
        print(f"    > Outfile Status: {ee.data.getTaskStatus(export.id)}")
        print(f"        > {outfile_name} written")
