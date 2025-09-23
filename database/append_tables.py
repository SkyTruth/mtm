import json
import geopandas as gpd
import pandas as pd
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, INTEGER, TEXT, FLOAT
from geoalchemy2 import Geometry
from google.cloud import storage
from mtm_utils.cloud_sql_utils import connect_tcp_socket
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

    engine = connect_tcp_socket()

    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "annual_mining"
    d_status = "final"

    file_path_name = GCLOUD_FINAL_DATA_GEOJSON+"1985_activeMining.geojson"
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


def append_to_highwall_centerline_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/centerline_segments_SAMPLE.geojson"
    
    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "highwall_centerlines"

    gdf = gpd.read_file(infile)
    df = gdf

    df = df.rename(columns={
        "ID": "id",
        "length": "detect_length",
        "geometry": "geom",
    })
    print(df.head(3))

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
                "detect_length": FLOAT(),
                "geom": Geometry("MultiLineString", srid=4326)
             },
        )
    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_counties_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/tl_2024_us_county_WV_SAMPLE.geojson"
    
    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "counties"

    gdf = gpd.read_file(infile)
    df = gdf
    print(df.head(3))

    df = df.rename(columns={
        "STATEFP": "statefp",
        "COUNTYFP": "countyfp",
        "COUNTYNS": "countyns",
        "GEOID": "geoid",
        "GEOIDFQ": "geoidfq",
        "NAME": "name",
        "NAMELSAD": "namelsad",
        "LSAD": "lsad",
        "CLASSFP": "classfp",
        "MTFCC": "mtfcc",
        "CSAFP": "csafp",
        "CBSAFP": "cbsafp",
        "METDIVFP": "metdivfp",
        "FUNCSTAT": "funcstat",
        "ALAND": "aland",
        "AWATER": "awater",
        "INTPTLAT": "intptlat",
        "INTPTLON": "intptlon",
        "geometry": "geom",
    })
    
    # Clean lat/lon (remove '+' and cast to float)
    for col in ("intptlat", "intptlon"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace("+", "", regex=False), errors="coerce")

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,          # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype={
                "statefp": INTEGER(),
                "countyfp": INTEGER(),
                "countyns": INTEGER(),
                "geoid": INTEGER(),
                "geoidfq": TEXT(),
                "name": TEXT(),
                "namelsad": TEXT(),
                "lsad": INTEGER(),
                "classfp": TEXT(),
                "mtfcc": TEXT(),
                "csafp": INTEGER(),
                "cbsafp": INTEGER(),
                "metdivfp": INTEGER(),
                "funcstat": TEXT(),
                "aland": DOUBLE_PRECISION(),
                "awater": DOUBLE_PRECISION(),
                "intptlat": DOUBLE_PRECISION(),
                "intptlon": DOUBLE_PRECISION(),
                "geom": Geometry("MultiPolygon", srid=4326)
             },
        )

    print(f"Data from: {infile} apppended to {table_name}.")




if __name__ == "__main__":
    append_to_annual_mining_table_from_local()
    append_to_annual_mining_table_from_gcs()
    append_to_highwall_centerline_table_from_local()
    append_to_counties_table_from_local()

