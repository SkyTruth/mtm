import ee
from ee import batch

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIAL_DIR, EE_CREDENTIALS
from mtm_utils.variables import GCLOUD_BUCKET, GCLOUD_CAMRA_DIR

"""
This code is a .py equivalent of the original code found at CAMRA/Archive/2021-03-09_sr_annualLastMinedMetrics.ipynb

This script was created by Christian Thomas at SkyTruth to aggregate index and band values for last-mined polygons. It 
also supports this processing for custom polygons. The code processes RMA harmonized, Surface Reflectance Median pixel 
composites. The code does not identify EPA Level 4 ecoregions (US_L4CODE) which is an attribute used in other processing 
scripts, this data is added locally.

https://code.earthengine.google.com/a92026e76f77c3c49244e22c81065304
"""


print(f"GEE Service Account: {EE_SERVICE_ACCOUNT}\n  > Credentials: {EE_CREDENTIALS}")
credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)
print(credentials)

ee.Initialize(credentials)


"""
Prepare Global Variables
"""
# Specify the study area and define the export geometry
studyArea = ee.FeatureCollection(
    "users/skytruth-data/Plos_MTM_Fusion_Table_Backup/plosScriptFusionTableBackup/studyArea"
)
exportGeometry = studyArea.geometry()

# Define EPA Level-4 Ecoregion Sample Sites (selected sites which did not experience mining activity and serve as a
# baseline for undisturbed forest).
epaEcoregionTestSites = ee.FeatureCollection(
    "users/skytruth-data/MTR/allEcoregionTestSites_update"
)

# Specify the Last Mined and Median Pixel Imagery
lastMinedRaw = ee.Image("users/skytruth-data/MTR/LastMined_Raw")
medianPixelComposite = ee.ImageCollection(
    "users/skytruth-data/MTR/SR_RMA_Harmonized_medianComposite"
)

# Get the scale of a landsat pixel
lsScale = medianPixelComposite.first().projection().nominalScale()

# A list whose length is equal to the number of years of imagery to process.
yearSequence = ee.List.sequence(
    0, 35
)  # 0,35 > 1984-2019 ; 0,10 > 1984-1994; 11,21 > 1995-2005; 26,35 > 2010-2019

# A list of all bands
bands = [
    "B",
    "G",
    "R",
    "NIR",
    "SWIR1",
    "SWIR2",
    "NDVI",
    "NDMI",
    "EVI",
    "SAVI",
    "MSAVI",
    "NBR",
    "NBR2",
]

# For processing of pre-filtered, or partially processed data, define the input on line 30, samples provided.
# NOTE : This data is derived from partially processed output of the lastMinedRaw data.
lastMinedCleaned = ee.FeatureCollection(
    "users/skytruth-data/MTR/20201026_lastMined_before_2015_gte_10px"
)


# For processing of custom polygon data which has not been pre or partially processed and is not derived from
# lastMinedRaw data, samples provided.
inputPolygons = ee.FeatureCollection("users/christian/2021-03-08_mtm_test_data")


"""
Prepare Processing Functions
"""


def clipping(image):
    clippedImg = image.clip(studyArea)
    return clippedImg


def cleanup(image):
    year = ee.Number(image.get("year"))
    pxArea = (
        ee.Image.pixelArea().multiply(image).divide(year).rename("area_cal").toFloat()
    )
    return image.addBands(pxArea)


def pixelAreaGPC(image):
    scale = image.projection().nominalScale()
    scaleArea = scale.multiply(scale)
    final = image.addBands(scaleArea).rename(
        "B",
        "G",
        "R",
        "NIR",
        "SWIR1",
        "SWIR2",
        "NDVI",
        "NDMI",
        "EVI",
        "SAVI",
        "MSAVI",
        "NBR",
        "NBR2",
        "pxArea",
    )
    return final


def pixelAreaLM(image):
    year = ee.Number(image.get("year"))
    scaleArea = lsScale.multiply(lsScale)
    final = image.addBands(scaleArea).rename("lastMined", "area")
    return final


def vectorize(image):
    year = image.get("year")
    vector = image.reduceToVectors(
        reducer=ee.Reducer.sum(),
        geometry=exportGeometry,
        scale=30,
        crs="EPSG:5072",
        labelProperty="lastMined",
        maxPixels=1e10,
    ).set("year", year)
    filteredVector = vector.filterMetadata("lastMined", "not_equals", 0)
    return filteredVector


def featID(feature):
    fid = feature.id()
    featureID = feature.set("ID", fid)
    return featureID


def areaCalcVector(feat):
    calculatedArea = feat.area().toFloat()
    fin = feat.set("sum", calculatedArea)
    return fin


"""
Processing Data
"""
# 5 Year Bucket
lastMined_5yr_1984 = (
    ee.ImageCollection([lastMinedRaw.eq(1984)])
    .max()
    .multiply(1984)
    .toInt()
    .rename("lastMined")
    .set("year", 1984)
)
lastMined_5yr_1985 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(1985),
            lastMinedRaw.eq(1986),
            lastMinedRaw.eq(1987),
            lastMinedRaw.eq(1988),
            lastMinedRaw.eq(1989),
        ]
    )
    .max()
    .multiply(1985)
    .toInt()
    .rename("lastMined")
    .set("year", 1985)
)
lastMined_5yr_1990 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(1990),
            lastMinedRaw.eq(1991),
            lastMinedRaw.eq(1992),
            lastMinedRaw.eq(1993),
            lastMinedRaw.eq(1994),
        ]
    )
    .max()
    .multiply(1990)
    .toInt()
    .rename("lastMined")
    .set("year", 1990)
)
lastMined_5yr_1995 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(1995),
            lastMinedRaw.eq(1996),
            lastMinedRaw.eq(1997),
            lastMinedRaw.eq(1998),
            lastMinedRaw.eq(1999),
        ]
    )
    .max()
    .multiply(1995)
    .toInt()
    .rename("lastMined")
    .set("year", 1995)
)
lastMined_5yr_2000 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(2000),
            lastMinedRaw.eq(2001),
            lastMinedRaw.eq(2002),
            lastMinedRaw.eq(2003),
            lastMinedRaw.eq(2004),
        ]
    )
    .max()
    .multiply(2000)
    .toInt()
    .rename("lastMined")
    .set("year", 2000)
)
lastMined_5yr_2005 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(2005),
            lastMinedRaw.eq(2006),
            lastMinedRaw.eq(2007),
            lastMinedRaw.eq(2008),
            lastMinedRaw.eq(2009),
        ]
    )
    .max()
    .multiply(2005)
    .toInt()
    .rename("lastMined")
    .set("year", 2005)
)
lastMined_5yr_2010 = (
    ee.ImageCollection(
        [
            lastMinedRaw.eq(2010),
            lastMinedRaw.eq(2011),
            lastMinedRaw.eq(2012),
            lastMinedRaw.eq(2013),
            lastMinedRaw.eq(2014),
        ]
    )
    .max()
    .multiply(2010)
    .toInt()
    .rename("lastMined")
    .set("year", 2010)
)
lastMined_5yr_2015 = (
    ee.ImageCollection([lastMinedRaw.eq(2015)])
    .max()
    .multiply(2015)
    .toInt()
    .rename("lastMined")
    .set("year", 2015)
)

# Create the Image Collections from the created bucketed images
lastMined_5yr_IC = ee.ImageCollection(
    [
        lastMined_5yr_1984,
        lastMined_5yr_1985,
        lastMined_5yr_1990,
        lastMined_5yr_1995,
        lastMined_5yr_2000,
        lastMined_5yr_2005,
        lastMined_5yr_2010,
        lastMined_5yr_2015,
    ]
)


# Map the functions to add area data to images as bands
medianPixelCompositeArea = medianPixelComposite.map(pixelAreaGPC)

# Map the functions to add area data to images as bands
lastMinedArea_5yr = lastMined_5yr_IC.map(pixelAreaLM)

# Vectorize the Last Mined Image Collections
vectorLastMined_5yr = lastMinedArea_5yr.map(vectorize).flatten()

# Generate an ID for each polygon in the vectorized last mine file
vectorLastMined_5yr_ID = vectorLastMined_5yr.map(featID)

# Generate an ID for each polygon in the EPA Ecoregion Site file
epaEcoregionTestSites_ID = epaEcoregionTestSites.map(featID)

# Add Area and ID to the custom inputPolygons
inputPolygons_area = inputPolygons.map(areaCalcVector)
inputPolygons_ID = inputPolygons_area.map(featID)


# Filter Input Polygons to only preserve the calculated ID and sum attribute, for easier processing later.
inputPolygons_ID_only = inputPolygons_ID.select("ID", "sum")

# # print(inputPolygons_ID.first().getInfo())
# print(inputPolygons_ID_only.first().getInfo())
# print(vectorLastMined_5yr_ID.first().getInfo())
# print(epaEcoregionTestSites_ID.first().getInfo())

"""
Iterate through the vectorized Last Mined Collections
-----------------------------------------------------

Function to Process every polygon in a vector layer, generating mean statistics
for all indices, for each year in the specified yearSequence range.

The featureProcessing function iterates through the yearSequence list, for each
feature in the feature collection specified by polygonProcessing. For each feature
the function is applied for every year in the year sequence list.

featureProcessing takes 2 arguments, year and feat. Year is provided by yearSequence,
feat comes from the feature in a feature collection being processed. For the first
iteration of the code, feat comes from the first feature in a featureCollection 
specified by the polygonProcessing function. Then it gets the next feature from that
collection the next time it is iterated.
"""


def polygonProcessing(feature):

    # Feature Processing
    def featureProcessing(year, feat):
        year = ee.Number(year).toInt()
        feat = ee.Feature(feat)

        realYearNumeric = ee.Number(1984).toInt().add(year)
        # realYearString = str(realYearNumeric)

        annualImage = medianPixelCompositeArea.filterMetadata(
            "year", "equals", realYearNumeric
        )

        reduction = (
            annualImage.first()
            .select(bands)
            .reduceRegion(
                geometry=feature.geometry(),
                reducer=ee.Reducer.mean(),
                scale=30,
                maxPixels=1e13,
            )
        )

        b_mean = ee.Number(reduction.get("B"))
        g_mean = ee.Number(reduction.get("G"))
        r_mean = ee.Number(reduction.get("R"))
        nir_mean = ee.Number(reduction.get("NIR"))
        swir1_mean = ee.Number(reduction.get("SWIR1"))
        swir2_mean = ee.Number(reduction.get("SWIR2"))
        ndvi_mean = ee.Number(reduction.get("NDVI"))
        ndmi_mean = ee.Number(reduction.get("NDMI"))
        evi_mean = ee.Number(reduction.get("EVI"))
        savi_mean = ee.Number(reduction.get("SAVI"))
        msavi_mean = ee.Number(reduction.get("MSAVI"))
        nbr_mean = ee.Number(reduction.get("NBR"))
        nbr2_mean = ee.Number(reduction.get("NBR2"))

        b_mean_field_pt1 = ee.String("B_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        g_mean_field_pt1 = ee.String("G_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        r_mean_field_pt1 = ee.String("R_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        nir_mean_field_pt1 = ee.String("NIR_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        swir1_mean_field_pt1 = ee.String("SWIR1_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        swir2_mean_field_pt1 = ee.String("SWIR2_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        ndvi_mean_field_pt1 = ee.String("NDVI_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        ndmi_mean_field_pt1 = ee.String("NDMI_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        evi_mean_field_pt1 = ee.String("EVI_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        savi_mean_field_pt1 = ee.String("SAVI_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        msavi_mean_field_pt1 = ee.String("MSAVI_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        nbr_mean_field_pt1 = ee.String("NBR_").cat(
            ee.Number(realYearNumeric).int().format()
        )
        nbr2_mean_field_pt1 = ee.String("NBR2_").cat(
            ee.Number(realYearNumeric).int().format()
        )

        b_mean_field_pt2 = ee.String(b_mean_field_pt1)
        g_mean_field_pt2 = ee.String(g_mean_field_pt1)
        r_mean_field_pt2 = ee.String(r_mean_field_pt1)
        nir_mean_field_pt2 = ee.String(nir_mean_field_pt1)
        swir1_mean_field_pt2 = ee.String(swir1_mean_field_pt1)
        swir2_mean_field_pt2 = ee.String(swir2_mean_field_pt1)
        ndvi_mean_field_pt2 = ee.String(ndvi_mean_field_pt1)
        ndmi_mean_field_pt2 = ee.String(ndmi_mean_field_pt1)
        evi_mean_field_pt2 = ee.String(evi_mean_field_pt1)
        savi_mean_field_pt2 = ee.String(savi_mean_field_pt1)
        msavi_mean_field_pt2 = ee.String(msavi_mean_field_pt1)
        nbr_mean_field_pt2 = ee.String(nbr_mean_field_pt1)
        nbr2_mean_field_pt2 = ee.String(nbr2_mean_field_pt1)

        return feat.set(
            b_mean_field_pt2,
            b_mean,
            g_mean_field_pt2,
            g_mean,
            r_mean_field_pt2,
            r_mean,
            nir_mean_field_pt2,
            nir_mean,
            swir1_mean_field_pt2,
            swir1_mean,
            swir2_mean_field_pt2,
            swir2_mean,
            ndvi_mean_field_pt2,
            ndvi_mean,
            ndmi_mean_field_pt2,
            ndmi_mean,
            evi_mean_field_pt2,
            evi_mean,
            savi_mean_field_pt2,
            savi_mean,
            msavi_mean_field_pt2,
            msavi_mean,
            nbr_mean_field_pt2,
            nbr_mean,
            nbr2_mean_field_pt2,
            nbr2_mean,
        )

    finalFeature = ee.Feature(yearSequence.iterate(featureProcessing, feature))
    return finalFeature


# Map polygonProcessing to vectorized Last Mined collections
processedLastMined_5yr = lastMinedCleaned.map(polygonProcessing)

# Map polygonProcessing to EPA Ecoregion Sites
fullyProcessed_EPA_ER_Sites = epaEcoregionTestSites_ID.map(polygonProcessing)

# Map polygonProcessing to custom input Polygons
fullyProcessedCustomPolygons = inputPolygons_ID_only.map(polygonProcessing)


"""
Inspect Size and First Feature of Processed Datasets
"""
print(
    f"Last Mined Polygon Data\n  > Size: {str(processedLastMined_5yr.size().getInfo())}"  # \n  > First: {str(processedLastMined_5yr.first().getInfo())}"
)
print(
    f"EPA Ecoregion Sample Site Data\n  > Size: {str(fullyProcessed_EPA_ER_Sites.size().getInfo())}"  # \n  > First: {str(fullyProcessed_EPA_ER_Sites.first().getInfo())}"
)
print(
    f"Custom Polygon Data\n  > Size: {str(fullyProcessedCustomPolygons.size().getInfo())}"  # \n  > First: {str(fullyProcessedCustomPolygons.first().getInfo())}"
)

"""
Export Data
-----------
Data should be exported as both CSV and GeoJSON
"""

# Define Export File Names
lastMined_outfile_name = '2025-03-07_lastMined_srHarmonizedMed_metricProcessed'
epaEcoregion_outfile_name = '2025-03-07_epaEcoregionSite_srHarmonizedMed_metricProcessed' 
customPolygon_outfile_name = '2025-03-07_customPolygon_srHarmonizedMed_metricProcessed'

# Prepare Output Tasks
lastMined_csv = batch.Export.table.toCloudStorage(collection=processedLastMined_5yr, description=lastMined_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + lastMined_outfile_name, fileFormat="CSV")
lastMined_gjs = batch.Export.table.toCloudStorage(collection=processedLastMined_5yr, description=lastMined_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + lastMined_outfile_name, fileFormat="GeoJSON")

ecoRegion_csv = batch.Export.table.toCloudStorage(collection=fullyProcessed_EPA_ER_Sites, description=epaEcoregion_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + epaEcoregion_outfile_name, fileFormat="CSV")
ecoRegion_gjs = batch.Export.table.toCloudStorage(collection=fullyProcessed_EPA_ER_Sites, description=epaEcoregion_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + epaEcoregion_outfile_name, fileFormat="GeoJSON")

customPoly_csv = batch.Export.table.toCloudStorage(collection=fullyProcessedCustomPolygons, description=customPolygon_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + customPolygon_outfile_name, fileFormat="CSV")
customPoly_gjs = batch.Export.table.toCloudStorage(collection=fullyProcessedCustomPolygons, description=customPolygon_outfile_name, bucket=GCLOUD_BUCKET, fileNamePrefix=GCLOUD_CAMRA_DIR + customPolygon_outfile_name, fileFormat="GeoJSON")


exporting_lastMined_csv = batch.Task.start(lastMined_csv)
exporting_lastMined_gjs = batch.Task.start(lastMined_gjs)

exporting_ecoRegion_csv = batch.Task.start(ecoRegion_csv)
exporting_ecoRegion_gjs = batch.Task.start(ecoRegion_gjs)

exporting_customPoly_csv = batch.Task.start(customPoly_csv)
exporting_customPoly_gjs = batch.Task.start(customPoly_gjs)

print("Export started, process(es) sent to cloud")