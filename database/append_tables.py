from mtm_utils.cloud_sql_utils import connect_tcp_socket
import sqlalchemy
import os
import csv
import json
import pandas as pd
import geopandas as gpd
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, INTEGER, TEXT
from geoalchemy2 import Geometry

from google.cloud import storage
from mtm_utils.variables import GCLOUD_BUCKET, GCLOUD_FINAL_DATA_GEOJSON


def append_to_annual_mining_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/2024_activeMining_SAMPLE.geojson"
    
    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "annual_mining"
    d_status = "provisional"

    gdf = gpd.read_file(infile)
    df = gdf.assign(data_status=d_status)

    df = df.rename(columns={
        "id": "id",
        "AREA": "area",
        "year": "mining_year",
        "data_status": "data_status",
        "geometry": "geom",
    })
    print(df.head(3))

    # # print(type(df))
    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,          # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype={
                "id": TEXT(),
                "mining_year": INTEGER(),
                "area": DOUBLE_PRECISION(),
                "data_status": TEXT(),
                "geom": Geometry("MultiPolygon", srid=4326)
             },
        )
    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_annual_mining_table_from_gcs():
    # The ID of your GCS bucket
    storage_client = storage.Client()
    bucket_name = GCLOUD_BUCKET
    storage_bucket = storage_client.bucket(bucket_name)

    # # Get all the images produced from greenestPixelComp.py
    # for f in storage_client.list_blobs(bucket_name, prefix=GCLOUD_FINAL_DATA_GEOJSON):
    #     fName = f.name
    #     mine_names.append(fName)

    # mine_names.pop(0)
    # final_file_index = len(mine_names)


    engine = connect_tcp_socket()
    # for i in mine_names[0:1]:
    #     print(i)
    table_name = "annual_mining"
    d_status = "final"

    file_path_name = "gee_data/FINAL_DATA/GEOJSON/1985_activeMining.geojson"
    blob = storage_bucket.blob(file_path_name)

    # Download the blob as a string and decode it
    blob_string = blob.download_as_string().decode('utf-8')

    # Use json.loads() to parse the GeoJSON string into a Python object
    geojson_data = json.loads(blob_string)

    # Create a GeoDataFrame from the parsed GeoJSON
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    df = gdf.assign(data_status=d_status)

    df = df.rename(columns={
        "id": "id",
        "AREA": "area",
        "year": "mining_year",
        "data_status": "data_status",
        "geometry": "geom",
        
    })
    print(df)

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,          # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype={
                "id": TEXT(),
                "mining_year": INTEGER(),
                "area": DOUBLE_PRECISION(),
                "data_status": TEXT(),
                "geom": Geometry("MultiPolygon", srid=4326)
             },
        )
    print(f"Data from: {file_path_name} apppended to {table_name}.")


if __name__ == "__main__":
    # append_to_annual_mining_table_from_local()
    append_to_annual_mining_table_from_gcs()

