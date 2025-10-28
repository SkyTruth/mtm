import json
import geopandas as gpd
import pandas as pd
from google.cloud import storage
from mtm_utils.cloud_sql_utils import connect_tcp_socket, geom_convert_3d_to_2d
from mtm_utils.variables import GCLOUD_BUCKET, GCLOUD_FINAL_DATA_GEOJSON, annual_mining_format_dict, highwall_centerline_format_dict, counties_format_dict, wv_permit_format_dict, huc_format_dict


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
            dtype=annual_mining_format_dict,
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
            dtype=annual_mining_format_dict,
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
            dtype=highwall_centerline_format_dict,
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
            dtype=counties_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_wv_permits_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/WVDEP_GIS_data_mining_reclamation_permit_boundary_SAMPLE.geojson"
    state = "wv"
    
    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "state_permits_"+state

    gdf = gpd.read_file(infile)
    df = gdf
    df = df.rename(columns={"geometry": "geom",})
    
    # Add a new, SkyTruth ID, which is unique to each record, handles issues where there are multiple records
    # that share a permit_id. Set the state on line 187.
    df = df.reset_index(drop=True)
    df["st_id"] = [f"st_{state}_" + str(i) for i in range(1, len(df) + 1)]
    
    # Reorder so unique_id is the first column
    cols = ["st_id"] + [c for c in df.columns if c != "st_id"]
    df = df[cols]

    # Convert to 2D Geoms if needed
    df["geom"] = df["geom"].apply(geom_convert_3d_to_2d)
    # print(df.head(3))

    # Formate date columns, for reference, native formats for WV Permit data are:
    #       mapdate     = YYYYMMDD
    #       mdate       = MM/DD/YY
    #       issue_date  = MM/DD/YY
    #       expire_dat  = MM/DD/YY
    #       last_updat  = MM/DD/YY
    
    df["mapdate"] = pd.to_datetime(df["mapdate"], format="%Y%m%d", errors="coerce")

    # mdate, issue_date, expire_dat, last_updat: MM/DD/YY
    for col in ["mdate", "issue_date", "expire_dat", "last_updat"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%m/%d/%y", errors="coerce")
    # print(df[["mapdate","mdate", "issue_date", "expire_dat", "last_updat"]].head(3)) 

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,          # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype= wv_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_huc_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/NHD_HUC/NHD_HUC_2_to_12_sample.geojson"
    
    table_name = "huc_boundaries"

    gdf = gpd.read_file(infile)
    df = gdf
    print(df.head(3))

    df = df.rename(columns={
        "objectid": "objectid",
        "tnmid": "tnmid",
        "metasourceid": "metasourceid",
        "sourcedatadesc": "sourcedatadesc",
        "sourceoriginator": "sourceoriginator",
        "sourcefeatureid": "sourcefeatureid",
        "loaddate": "loaddate",
        "referencegnis_ids": "referencegnis_ids",
        "areaacres": "areaacres",
        "areasqkm": "areasqkm",
        "states": "states",
        "huc10": "huc10",
        "name": "name",
        "hutype": "hutype",
        "humod": "humod",
        "globalid": "globalid",
        "shape_Length": "shape_length",
        "shape_Area": "shape_area",
        "hutype_description": "hutype_description",
        "huc12": "huc12",
        "tohuc": "tohuc",
        "noncontributingareaacres": "noncontributingareaacres",
        "noncontributingareasqkm": "noncontributingareasqkm",
        "huc2": "huc2",
        "huc4": "huc4",
        "huc6": "huc6",
        "huc8": "huc8",
        "geometry": "geom",
    })


    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,          # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype= wv_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


if __name__ == "__main__":
    append_to_annual_mining_table_from_local()
    append_to_annual_mining_table_from_gcs()
    append_to_highwall_centerline_table_from_local()
    append_to_counties_table_from_local()
    append_to_wv_permits_table_from_local()
    append_to_huc_table_from_local()
