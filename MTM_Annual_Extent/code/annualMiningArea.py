import ee
import datetime
import time
from ee import batch
from google.cloud import storage

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIALS
from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCLOUD_EE_GPC_DIR,
    GCLOUD_MASK_DIR,
    GCLOUD_EE_THRESHOLD_DIR,
    GCLOUD_EE_ANNUAL_MINES_TIFF,
    GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF,
    GCLOUD_FINAL_DATA_DIR,
    FIPS_CODES,
)


credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)
ee.Initialize(credentials)
########################################################################################################################
########################################################################################################################
"""
INITIAL SET-UP
"""
# Defining the processing year, which is the current year minus 1 (THIS WILL NEED TO BE CHANGED WHEN SETTING UP THE
# FINAL CRON, SINCE USCB DATA WILL BE UPDATED). IN FUTURE THIS WILL EQUAL CURRENT YEAR
# processing_year = (datetime.date.today().year)
processing_year = 2024

# Our cleaning process relies on the use of dummy images, these are used to clean the years immediately before and after
# the years for which we have Landsat scenes. We need images of value 0 so that the nullCleaning2 function will work.
# NOTE: SET initialCleaningYear to 1972 WHEN MSS PROCESSING IS ADDED
initialCleaningYear = 1983
finalCleaningYear = processing_year + 1

# print(f"Processing Year: {processing_year}. Initial Cleaning Year: {initialCleaningYear}, Final Cleaning Year: {finalCleaningYear}")

# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
print(f"STORAGE BUCKET:{storage_bucket}\n\n")
########################################################################################################################
########################################################################################################################
"""
PREPARING THE GREENEST PIXEL AND ANNUAL THRESHOLD IMAGE COLLECTIONS FOR USE BY EARTH ENGINE
"""

gpc_image_names = []
threshold_image_names = []

# Get all the images produced from greenestPixelComp.py
for img in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_GPC_DIR):
    img_name = img.name
    gpc_image_names.append(img_name)

# Get all the images produced from greenestPixelComp.py
for img in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_THRESHOLD_DIR):
    img_name = img.name
    threshold_image_names.append(img_name)

# The img.name also grabs the folder the images are stored in, use .pop(0) to remove this so we can create the GS URLs
# for all the images that are used to make a GEE image collections.
gpc_image_names.pop(0)
threshold_image_names.pop(0)

# Write the image URLs to a list so that Earth Engine can read them, set the year attribute for images as well
gpc_url_list = []
threshold_url_list = []

for i in gpc_image_names:
    img_url = "gs://" + bucket_name + "/" + i
    gpc_url_list.append(img_url)
for i in threshold_image_names:
    img_url = "gs://" + bucket_name + "/" + i
    threshold_url_list.append(img_url)

greenestPixelCompositeList = []
thresholdCompositeList = []

for i in range(1984, finalCleaningYear):
    year = i
    annual_gpc_urls = []
    annual_threshold_urls = []

    # Merging the split GPC images into single GEE Images
    for url in gpc_url_list:
        url_year = url.split("composite_")[1].split("0000000000-")[0]
        if str(year) in url_year:
            img_url = url
            annual_gpc_urls.append(img_url)

    gpc_image_1 = annual_gpc_urls[0]
    gpc_image_2 = annual_gpc_urls[1]

    ee_gpc_image_pt1 = ee.Image.loadGeoTIFF(gpc_image_1)
    ee_gpc_image_pt2 = ee.Image.loadGeoTIFF(gpc_image_2)

    # There isn't overlap of the images, so a median reducer works well to create an image.
    ee_gpc_image = ee.ImageCollection([ee_gpc_image_pt1, ee_gpc_image_pt2]).median()
    ee_gpc_image = ee_gpc_image.set("year", year)
    greenestPixelCompositeList.append(ee_gpc_image)

    # Reading the annual threshold images into GEE Images
    for url in threshold_url_list:
        if str(year) in url:
            img_url = url
            annual_threshold_urls.append(img_url)

    threshold_image = annual_threshold_urls[0]
    threshold_ee_image = ee.Image.loadGeoTIFF(threshold_image)
    threshold_ee_image = threshold_ee_image.set("year", year)
    thresholdCompositeList.append(threshold_ee_image)
    print(f"  > {year}\n        > GPCs: {gpc_image_1} & {gpc_image_2}\n        > THRESHOLD: {threshold_image}")

########################################################################################################################
########################################################################################################################
"""
INITAL GEE DATA SET-UP
"""
greenestComposites = ee.ImageCollection.fromImages(greenestPixelCompositeList)
thresholds = ee.ImageCollection.fromImages(thresholdCompositeList)
studyArea = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/studyArea"
)

# MSS Accuracy Points are included so that they will be available when MSS implementation is added to the automation.
MSS_points = ee.FeatureCollection(
    "users/skytruth-data/MTR/Classification_Points/accuracyAssessmentPoints_1972-1984_created_20230707"
).filter(ee.Filter.neq("YEAR", 1984))
TM_points = ee.FeatureCollection(
    "users/skytruth-data/MTR/Classification_Points/accuracyAssessmentPoints_1984-2022_created_20221201"
)
accuracyPoints = MSS_points.merge(TM_points)

# All the FIPS codes for counties in the study area
fips_codes = FIPS_CODES
allCounties = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/allCounties"
)
features = allCounties.filter(ee.Filter.inList("FIPS", fips_codes))

# Create an image where each pixel is labeled with its FIPS code
countyImg = features.reduceToImage(
    properties=["FIPS"], reducer=ee.Reducer.first()
).rename("FIPS")

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

# INITIAL MINE THRESHOLDING
# Create a list of yearly threshold images, and a list of years associated with those images, for image selection within
# the loop.
threshImgList = thresholds.sort("year").toList(100)
threshImgYrList = ee.List(thresholds.aggregate_array("year")).sort()
########################################################################################################################
########################################################################################################################
"""
DEFINING GEE FUNCTIONS
"""


def raw_mining_fx(image):
    """
    Raw Mining f(x) > This compares the NDVI at each pixel to the given threshold. The resulting images are 1 = mine
    and 0 = non-mine.
    """
    year = image.get("year")
    mineCandidate = image.select("NDVI").rename("mineCandidate")

    # This pulls the specific threshold image for the given year
    index = ee.Number(threshImgYrList.indexOf(year))
    threshold = ee.Image(threshImgList.get(index))

    # This compares the NDVI per pixel to the NDVI threshold
    lowNDVI = mineCandidate.lte(threshold)
    return lowNDVI.set("year", year)


def null_cleaning_fx1(image):
    """
    Null-value Cleaning f(x)1 > This is the first step of the null-value cleaning (i.e., where there are no pixel values
    for that year due to cloud cover or a lack of raw imagery). This function first creates a binary image where
    1 = values that were null in the rawMining image, and 0 = everything else.
    """
    year = image.get("year")
    unmasked = image.lt(2).unmask().Not().clip(studyArea)
    return unmasked.set("year", year)


def null_cleaning_fx2(image):
    """
    Null-value Cleaning f(x)2 > This is the second step of the null-value cleaning. For each year, pull the raw mining
    images for the years immediately prior and future, where in those images 1 = mine and 0 = non-mine. Add those three
    images together; areas where the sum is 3 indicate that the null pixel is likely a mine, because that pixel was a
    mine in the prior and future years.
    """
    year = ee.Number(image.get("year"))

    rm2Index = ee.Number(
        rm2YrList.indexOf(year)
    )  # Get the index of the year that is being looked at
    priorIndex = rm2Index.subtract(1)  # The previous year index
    futureIndex = rm2Index.add(1)  # The future year index

    imgPrevious = ee.Image(rm2List.get(priorIndex)).unmask()
    imgNext = ee.Image(rm2List.get(futureIndex)).unmask()

    # Since the indices are the same for rm2List and rm2YrList, essentially use the index of the year to select the
    # corresponding image, which has the same index. In other words, if a null in current year (1) and a mine in past
    # and future years (also 1), the pixel in the current year will sum to 3.
    summation = image.add(imgPrevious).add(imgNext)
    potentialMine = summation.eq(3)
    return potentialMine.set("year", year)


def null_cleaning_fx3(image):
    """
    Null-value Cleaning f(x)3 > This is the third step of the null-value cleaning. Use the results of the previous
    operation to turn any null values in the rawMining imagery into a value of 1 if they were also a value of 1 from the
    nullCleaning_2 imagery.
    """
    year = image.get("year")
    nc2Index = ee.Number(nc2YrList.indexOf(year))
    cleaningImg = ee.Image(nc2List.get(nc2Index))
    updatedRaw = image.unmask().add(cleaningImg)
    return updatedRaw.set("year", year)


def noise_cleaning_fx1(image):
    """
    Noise Cleaning f(x)1 > Noise cleaning to eliminate pixels that go from unmined->mine->unmined, since  the mine pixel
    is likely incorrect. We need dummy years for years without LS coverage, except this time the dummy images have
    values of 1 because otherwise all the pixels near these years would get removed.
    """
    year = ee.Number(image.get("year"))
    rm3Index = ee.Number(rm3YrList.indexOf(year))
    priorIndex = rm3Index.subtract(1)
    futureIndex = rm3Index.add(1)
    imgPrevious = ee.Image(rm3List.get(priorIndex))
    imgNext = ee.Image(rm3List.get(futureIndex))

    # Relabel images so that pixels that are mine in current year but not mine in previous/next years are labeled 111
    # when summed
    relabelPrevious = imgPrevious.remap([0, 1], [100, -10])
    relabelNext = imgNext.remap([0, 1], [10, -10])
    summation = image.add(relabelPrevious).add(relabelNext)
    potentialNoise = summation.eq(111)

    # Mine in current year = 1; non-mine in past year = 100; non-mine in future year = 10; therefore we want sum of 111
    potentialNoise_2 = image.where(potentialNoise.eq(1), 0).set("year", year)
    return potentialNoise_2


def noise_cleaning_fx2(image):
    """
    Noise Cleaning f(x)2 > More noise cleaning to eliminate pixels that go from mined->unmined->mined, since the unmined
    pixel is likely incorrect. We need the 0-value dummy images from above.
    """
    year = ee.Number(image.get("year"))
    rm4Index = ee.Number(rm4YrList.indexOf(year))
    priorIndex = rm4Index.subtract(1)
    futureIndex = rm4Index.add(1)
    imgPrevious = ee.Image(rm4List.get(priorIndex))
    imgNext = ee.Image(rm4List.get(futureIndex))

    # Relabel images so that pixels that are mine in current year but not mine in previous/next years are labeled 111
    # when summed.
    relabelPrevious = imgPrevious.remap([0, 1], [-10, 900])
    relabelNext = imgNext.remap([0, 1], [-10, 90])
    summation = image.add(relabelPrevious).add(relabelNext)
    potentialNoise = summation.eq(990)

    # Mine in current year = 1; non-mine in past year = 100; non-mine in future year = 10; therefore we want sum of 111
    potentialNoise_2 = image.where(potentialNoise.eq(1), 1).set("year", year)
    return potentialNoise_2


def final_mine_processing_fx(image):
    year = ee.Number(image.get("year"))

    # Create binary image containing the intersection between the LowNDVI and anywhere the inverted mask is 0
    mines = image.select("mineCandidate").And(mask_input_excludeMines.eq(0))

    # Test setting default PROJ
    mines = mines.reproject(crs="EPSG:5072", scale=30)

    # Mask mine layer by itself; label with specific year (for viz)
    minesMasked = mines.updateMask(mines).multiply(year).rename("year").toInt()

    # Remove small, noisy pixel areas (remember, this is dependent on zoom level)
    smallAreaMask = minesMasked.connectedPixelCount().gte(10)
    noSmall = minesMasked.updateMask(smallAreaMask)

    # Compute area per pixel
    area = ee.Image.pixelArea().multiply(noSmall).divide(year).rename("area").toFloat()
    final = image.addBands(noSmall).addBands(area).addBands(countyImg)
    return final


########################################################################################################################
########################################################################################################################
"""
DATA PROCESSING - INITIAL AND INTERMEDIATE STEPS
"""
rawMining = ee.ImageCollection(greenestComposites.map(raw_mining_fx))
nullCleaned_1 = ee.ImageCollection(rawMining.map(null_cleaning_fx1))

# Create dummy images so the null cleaning will work; essentially for 1983 and 2022 (the years immediately before and
# after the years for which we have Landsat scenes), we need images of value 0 so that the nullCleaning2 function below
# actually works.
dummy_start = ee.Image(0).rename("NDVI").set("year", initialCleaningYear)
dummy_end = ee.Image(0).rename("NDVI").set("year", finalCleaningYear)
rawMining2 = ee.ImageCollection(
    rawMining.merge(ee.ImageCollection([dummy_start, dummy_end]))
)

# Create two lists in order to help choose the immediate prior and future images for a given year. The first is a list
# of each image in the rawMining2 ImageCollection, sorted by year; the second is just a list of each year present in our
# dataset. These lists, used below, make running the code much more efficient than using filterMetadata() or anything
# like that. Similar lists seen below are achieving the same effect.
rm2List = rawMining2.sort("year").toList(100)
rm2YrList = ee.List(rawMining2.aggregate_array("year")).sort()

nullCleaned_2 = ee.ImageCollection(nullCleaned_1.map(null_cleaning_fx2))
nc2List = nullCleaned_2.sort("year").toList(100)
nc2YrList = ee.List(nullCleaned_2.aggregate_array("year")).sort()

nullCleaned_3 = ee.ImageCollection(rawMining.map(null_cleaning_fx3))

# The Dummy_A years need to be the same as the dummy_ years
dummy_start_a = ee.Image(1).rename("NDVI").set("year", initialCleaningYear)
dummy_end_a = ee.Image(1).rename("NDVI").set("year", finalCleaningYear)

rawMining3 = ee.ImageCollection(
    nullCleaned_3.merge(ee.ImageCollection([dummy_start_a, dummy_end_a]))
)
rm3List = rawMining3.sort("year").toList(100)
rm3YrList = ee.List(rawMining3.aggregate_array("year")).sort()

# Noise cleaning begins
noiseCleaned_1 = ee.ImageCollection(nullCleaned_3.map(noise_cleaning_fx1))

rawMining4 = ee.ImageCollection(
    noiseCleaned_1.merge(ee.ImageCollection([dummy_start, dummy_end]))
)
rm4List = rawMining4.sort("year").toList(100)
rm4YrList = ee.List(rawMining4.aggregate_array("year")).sort()

noiseCleaned_2 = ee.ImageCollection(noiseCleaned_1.map(noise_cleaning_fx2))
########################################################################################################################
########################################################################################################################
"""
DATA PROCESSING - FINAL CLEANING AND EXPORT
"""
mining = ee.ImageCollection(noiseCleaned_2.map(final_mine_processing_fx))
cumulative_image = ee.ImageCollection([])

# Since issues have been encountered properly area-filtering the data in raster space, we now filter the data in vector
# space. This area filtered vector is likewise used to clean the imagery.
for i in range(initialCleaningYear + 2, processing_year + 1):
    year = i
    annual_export_desc = str(year) + "_activeMining"

    # All File-Exists Tests are run on vector data.
    if i in range(initialCleaningYear + 2, processing_year):
        print(f"YEAR: {i}")
        raster_test_name = GCLOUD_EE_ANNUAL_MINES_TIFF + annual_export_desc + ".tif"
        outfile_raster_fin_name = GCLOUD_EE_ANNUAL_MINES_TIFF + annual_export_desc
        out_blob_raster_test = storage_bucket.blob(raster_test_name)
        print(f"{year} -- {raster_test_name}")

    if i in range(processing_year, processing_year + 1):
        print(f"\n\nEND YEAR: {i}")
        raster_test_name = (
            GCLOUD_EE_ANNUAL_MINES_TIFF + annual_export_desc + "_PROVISIONAL.tif"
        )
        outfile_raster_fin_name = (
            GCLOUD_EE_ANNUAL_MINES_TIFF + annual_export_desc + "_PROVISIONAL"
        )
        out_blob_raster_test = storage_bucket.blob(raster_test_name)
        print(f"{year} -- {raster_test_name}")

    # PROCESSING RASTER DATA
    # Data is still processed so that cumulative mining can be created however
    if out_blob_raster_test.exists():
        print(
            f"  > {GCLOUD_EE_ANNUAL_MINES_TIFF + annual_export_desc}.tif ALREADY EXISTS. PASSING ALL EXPORTS FOR {year}. PREPPING CUMULATIVE_MINING_IMAGE"
        )
        yearly_active_mining = (
            ee.Image(mining.filterMetadata("year", "equals", year).first())
            .select("year", "area")
            .unmask()
        )
        yearly_active_mining_vector = yearly_active_mining.reduceToVectors(
            reducer=ee.Reducer.sum(),
            geometry=features.geometry(),
            scale=30,
            crs="EPSG:4326",
            labelProperty="year",
            maxPixels=1e10,
        ).set("year", year)

        # Filter out any detections < 9000m2 (10px), then double-check the raster output by clipping it with the vector
        annual_mine_vector_area_filtered = yearly_active_mining_vector.filter(
            ee.Filter.gte("sum", 9000)
        )
        annual_mine_raster_area_filtered = (
            yearly_active_mining.clip(annual_mine_vector_area_filtered)
            .unmask()
            .clip(studyArea)
            .toInt()
            .select("year")
        )

        # Merge the processed raster to the cumulative_image, so that the cumulative data can be exported later
        cumulative_image = cumulative_image.merge(annual_mine_raster_area_filtered)
        pass
    else:
        yearly_active_mining = (
            ee.Image(mining.filterMetadata("year", "equals", year).first())
            .select("year", "area")
            .unmask()
        )
        yearly_active_mining_vector = yearly_active_mining.reduceToVectors(
            reducer=ee.Reducer.sum(),
            geometry=features.geometry(),
            scale=30,
            crs="EPSG:4326",
            labelProperty="year",
            maxPixels=1e10,
        ).set("year", year)

        # Filter out any detections < 9000m2 (10px), then double-check the raster output by clipping it with the vector
        annual_mine_vector_area_filtered = yearly_active_mining_vector.filter(
            ee.Filter.gte("sum", 9000)
        )
        annual_mine_raster_area_filtered = (
            yearly_active_mining.clip(annual_mine_vector_area_filtered)
            .unmask()
            .clip(studyArea)
            .toInt()
            .select("year")
        )
        # annual_mine_raster_area_filtered = yearly_active_mining.unmask().clip(studyArea).toInt().select("year")

        # Merge the processed raster to the cumulative_image, so that the cumulative data can be exported later
        # cumulative_image = cumulative_image.merge(annual_mine_raster_area_filtered)
        # EXPORTS
        raster_export = batch.Export.image.toCloudStorage(
            image=annual_mine_raster_area_filtered,
            description=annual_export_desc,
            bucket=GCLOUD_BUCKET,
            fileNamePrefix=outfile_raster_fin_name,
            region=studyArea.geometry(),
            scale=30,
            crs="EPSG:4326",
            maxPixels=1e13,
            fileFormat="GeoTIFF",
        )
        print(f"  > Writing raster data to {outfile_raster_fin_name}")
        raster_export.start()
        while raster_export.active():
            print(
                f"     > Logging task for {year} raster export (id: {raster_export.id}). Checks every 1 min."
            )
            time.sleep(60)
        print(f"    > Outfile Status: {ee.data.getTaskStatus(raster_export.id)}")
        print(f"        > {year} active mining geotiff created.")
########################################################################################################################
########################################################################################################################
"""
CUMULATIVE MINING - EXPORT
"""
cumulativeArea = (cumulative_image.filter(ee.Filter.gt("year", initialCleaningYear + 1)).filter(ee.Filter.lt("year", processing_year))).select("year")
cumulativeArea_provisional = (cumulative_image.filter(ee.Filter.gt("year", initialCleaningYear + 1)).filter(ee.Filter.lte("year", processing_year))).select("year")
cumulative_export_desc = ("CumulativeMineArea_" + str(initialCleaningYear + 2) + "-" + str(processing_year - 1))
cumulative_provisional_export_desc = ("CumulativeMineArea_" + str(initialCleaningYear + 2) + "-" + str(processing_year))
cumulativeArea_test_name = (GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + cumulative_export_desc + ".tif")
cumulativeArea_provisional_test_name = (GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + cumulative_provisional_export_desc + "_PROVISIONAL.tif")
cumulativeArea_fin_name = (GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + cumulative_export_desc)
cumulativeArea_provisional_fin_name = (GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF+ cumulative_provisional_export_desc+ "_PROVISIONAL")

out_blob_raster_test_cumulative = storage_bucket.blob(cumulativeArea_test_name)
out_blob_raster_test_cumulative_provisional = storage_bucket.blob(cumulativeArea_provisional_test_name)
print(f"{cumulativeArea_test_name} & {cumulativeArea_provisional_test_name}")

if out_blob_raster_test_cumulative.exists():
    print(f"  > {GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + cumulative_export_desc}.tif ALREADY EXISTS. PASSING.")
    pass
else:
    cumulativeMiningFootprint = cumulativeArea.qualityMosaic("year")
    raster_export = batch.Export.image.toCloudStorage(
        image=cumulativeMiningFootprint,
        description=cumulative_export_desc,
        bucket=GCLOUD_BUCKET,
        fileNamePrefix=cumulativeArea_fin_name,
        region=studyArea.geometry(),
        scale=30,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    print(f"  > Writing raster data to {cumulativeArea_test_name}")
    raster_export.start()
    while raster_export.active():
        print(
            f"     > Logging task for {cumulativeArea_test_name} raster export (id: {raster_export.id}). Checks every 1 min."
        )
        time.sleep(60)
    print(f"    > Outfile Status: {ee.data.getTaskStatus(raster_export.id)}")
    print(f"        > {cumulativeArea_test_name} cumulative mining image created.")


if out_blob_raster_test_cumulative_provisional.exists():
    print(f"  > {GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + cumulative_provisional_export_desc}.tif ALREADY EXISTS. PASSING.")
    pass
else:
    cumulativeMiningFootprint = cumulativeArea_provisional.qualityMosaic("year")
    raster_export = batch.Export.image.toCloudStorage(
        image=cumulativeMiningFootprint,
        description=cumulative_provisional_export_desc,
        bucket=GCLOUD_BUCKET,
        fileNamePrefix=cumulativeArea_provisional_fin_name,
        region=studyArea.geometry(),
        scale=30,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    print(f"  > Writing raster data to {cumulativeArea_provisional_test_name}")
    raster_export.start()
    while raster_export.active():
        print(
            f"     > Logging task for {cumulativeArea_provisional_test_name} raster export (id: {raster_export.id}). Checks every 1 min."
        )
        time.sleep(60)
    print(f"    > Outfile Status: {ee.data.getTaskStatus(raster_export.id)}")
    print(
        f"        > {cumulativeArea_provisional_test_name} cumulative mining image created."
    )

#######################################################################################################################
#######################################################################################################################
"""
ACCURACY ASSESSMENT
"""


def calculate_accuracy(image):
    year = image.get("year")
    image = image.gt(0).unmask()
    points = accuracyPoints.filterMetadata("YEAR", "equals", year)
    output = image.sampleRegions(points, ["CLASS"], 30)
    error_matrix = output.errorMatrix("CLASS", "year")
    final = image.set(
        "accuracy",
        error_matrix.accuracy(),
        "kappa",
        error_matrix.kappa(),
        "user",
        error_matrix.consumersAccuracy().toList().flatten(),
        "producer",
        error_matrix.producersAccuracy().toList().flatten(),
        "year",
        year,
    )
    return final


accuracy = mining.select("year").map(calculate_accuracy)


def create_accuracy_collection(image):
    """
    This turns the accuracy assessement values into blank geometries, so that they can be exported into tables.
    """
    blank_dict = ee.Dictionary()
    year = image.get("year")
    accuracy = image.get("accuracy")
    kappa = image.get("kappa")
    user = image.get("user")
    producer = image.get("producer")

    blank_dict = ee.Dictionary(
        ee.Dictionary(
            ee.Dictionary(
                ee.Dictionary(blank_dict.set("accuracy", accuracy)).set("kappa", kappa)
            ).set("user", user)
        ).set("producer", producer)
    ).set("year", year)

    final = ee.Feature(ee.Geometry.Point(0, 0), blank_dict)
    return final


accuracyCollection = ee.FeatureCollection(accuracy.map(create_accuracy_collection))
annual_accuracy_desc = "accuracyAssessmentResults_" + str(processing_year)
outfile_accuracy_test_name = GCLOUD_FINAL_DATA_DIR + annual_accuracy_desc + ".csv"
outfile_accuracy_fin_name = GCLOUD_FINAL_DATA_DIR + annual_accuracy_desc
out_blob_accuracy_test = storage_bucket.blob(outfile_accuracy_test_name)

if out_blob_accuracy_test.exists():
    print(
        f"  > {GCLOUD_FINAL_DATA_DIR + annual_accuracy_desc}.csv ALREADY EXISTS. PASSING."
    )
    pass
else:
    accuracy_export = batch.Export.table.toCloudStorage(
        collection=accuracyCollection,
        description=annual_accuracy_desc,
        bucket=GCLOUD_BUCKET,
        fileNamePrefix=outfile_accuracy_fin_name,
        fileFormat="CSV",
    )
    print(f"  > Writing accuracy data to {outfile_accuracy_test_name}")
    accuracy_export.start()
    while accuracy_export.active():
        print(
            f"     > Logging task for {processing_year} accuracy export (id: {accuracy_export.id}). Checks every 1 min."
        )
        time.sleep(60)
    print(f"    > Outfile Status: {ee.data.getTaskStatus(accuracy_export.id)}")
    print(f"        > {processing_year} accuracy data created.")
