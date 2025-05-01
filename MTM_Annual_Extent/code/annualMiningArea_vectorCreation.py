import ee
import time
from ee import batch
from google.cloud import storage

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIALS
from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCLOUD_EE_ANNUAL_MINES_TIFF,
    GCLOUD_EE_ANNUAL_MINES_GEOJSON,
)

credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)
ee.Initialize(credentials)
########################################################################################################################
########################################################################################################################
"""
INITIAL SET-UP
"""
# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
print(f"STORAGE BUCKET:{storage_bucket}\n\n")
########################################################################################################################
########################################################################################################################
mine_image_names = []

# Get all the images produced from greenestPixelComp.py
for img in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_ANNUAL_MINES_TIFF):
    img_name = img.name
    mine_image_names.append(img_name)

mine_image_names.pop(0)
final_img_index = len(mine_image_names)

for i in mine_image_names:
    year = (i.split("/")[-1]).split("_")[0]
    export_desc =(i.split("/")[-1]).split(".tif")[0]
    annual_export_desc = export_desc
    outfile_vector_fin_name = GCLOUD_EE_ANNUAL_MINES_GEOJSON + annual_export_desc
    outfile_vector_test_name = outfile_vector_fin_name + ".geojson"
    out_blob_vector_test = storage_bucket.blob(outfile_vector_test_name)

    image_url = f"gs://mountaintop_mining/{i}"

    def add_year_prop(feature):
        return feature.set("year", year)

    def getArea(feature):
        area = feature.area(maxError=1, proj="EPSG:5072")
        return feature.set("AREA", area)

    # Check if the Outfile has already been created (in an earlier year), and pass if it has
    if out_blob_vector_test.exists():
        print(f"  > {outfile_vector_fin_name}.geojson ALREADY EXISTS. PASSING CONVERSION FOR {year}.")
        pass
    else:
        print(f"  > {outfile_vector_fin_name}.geojson DNE. CONVERTING GeoTIFF to GeoJSON FOR {year}.")
        mining = ee.Image(ee.Image.loadGeoTIFF(image_url)).rename("mine").divide(int(year)).toFloat()
        mining = mining.updateMask(mining)

        vector = mining.toInt().reduceToVectors(reducer=ee.Reducer.countEvery(), scale=30, eightConnected=True, crs="EPSG:4326", maxPixels=1e13)
        vector = vector.map(add_year_prop)
        vector = vector.map(getArea)

        # EXPORTS
        vector_export = batch.Export.table.toCloudStorage(
            collection=vector,
            description=annual_export_desc,
            bucket=GCLOUD_BUCKET,
            fileNamePrefix=outfile_vector_fin_name,
            fileFormat="GeoJSON"
        )

        print(f"      > {year} writing vector data: {i}  >>>>  {outfile_vector_test_name}\n")
        vector_export.start()
        while vector_export.active():
            print(f"        > Logging task for {year} vector export (id: {vector_export.id}). Checks every 15 sec.")
            time.sleep(15)
        print(f"        > Outfile Status: {ee.data.getTaskStatus(vector_export.id)}")
        print(f"          > {year} active mining geojson created.")