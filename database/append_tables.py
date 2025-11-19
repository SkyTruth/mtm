import json
import geopandas as gpd
import os
import pandas as pd
from google.cloud import storage
from mtm_utils.cloud_sql_utils import connect_tcp_socket, geom_convert_3d_to_2d
from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCLOUD_FINAL_DATA_GEOJSON,
    annual_mining_input_directory,
    annual_mining_format_dict,
    highwall_detection_format_dict,
    counties_format_dict,
    ky_permit_format_dict,
    wv_permit_format_dict,
    va_permit_format_dict,
    tn_permit_format_dict,
    huc_format_dict,
    eamlis_format_dict,
)


def append_to_annual_mining_table_from_local():
    """
    This is for appending single files to the annual_mining table
    """
    engine = connect_tcp_socket()

    infile = "PATH/TO/INFILE.geojson"

    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "annual_mining"
    d_status = "final"

    gdf = gpd.read_file(infile)
    df = gdf.assign(data_status=d_status)

    # Remove extra columns not needed for the Database
    df = df.rename(
        columns={
            "id": "id",
            "AREA": "area",
            "year": "mining_year",
            "data_status": "data_status",
            "geometry": "geom",
        }
    ).drop(["count", "label"], axis=1)
    print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=annual_mining_format_dict,
        )
    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_annual_mining_table_from_local_directory():
    engine = connect_tcp_socket()

    table_name = "annual_mining"

    indir = os.listdir(annual_mining_input_directory)
    for i in sorted(indir):
        fpath = annual_mining_input_directory + i        
        
        # Check if the data is provisional
        if "PROVISIONAL" in i:
            d_status = "provisional"
        else:
            d_status = "final"
        
        print(f"{i}  > {d_status}")

        gdf = gpd.read_file(fpath)
        df = gdf.assign(data_status=d_status)

        # Remove extra columns not needed for the Database
        df = df.rename(
            columns={
                "id": "id",
                "AREA": "area",
                "year": "mining_year",
                "data_status": "data_status",
                "geometry": "geom",
            }
        ).drop(["count", "label"], axis=1)
        # print(df.head(3))

        with engine.begin() as conn:
            df.to_sql(
                table_name,
                con=conn,
                if_exists="append",
                index=False,  # avoid stray index column
                method="multi",
                chunksize=1000,
                dtype=annual_mining_format_dict,
            )
        print(f"Data from: {fpath} apppended to {table_name}.")


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

    file_path_name = GCLOUD_FINAL_DATA_GEOJSON + "1985_activeMining.geojson"
    blob = storage_bucket.blob(file_path_name)

    # Download the blob as a string and decode it
    blob_string = blob.download_as_string().decode("utf-8")

    # Use json.loads() to parse the GeoJSON string into a Python object
    geojson_data = json.loads(blob_string)

    # Create a GeoDataFrame from the parsed GeoJSON
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    df = gdf.assign(data_status=d_status)

    df = df.rename(
        columns={
            "id": "id",
            "AREA": "area",
            "year": "mining_year",
            "data_status": "data_status",
            "geometry": "geom",
        }
    ).drop(["count", "label"], axis=1)
    print(df)

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=annual_mining_format_dict,
        )
    print(f"Data from: {file_path_name} apppended to {table_name}.")


"""def append_to_highwall_detections_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/MTM_API_SANDBOX/HIGHWALL_DETECTION_FILE.geojson"

    table_name = "highwall_detections"

    gdf = gpd.read_file(infile)
    df = gdf

    df = df.rename(
        columns={
            "ID": "id",
            "length": "detect_length",
            "geometry": "geom",
        }
    )
    print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=highwall_centerline_format_dict,
        )
    print(f"Data from: {infile} apppended to {table_name}.")
"""

def append_to_counties_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/tl_2025_us_county/tl_2025_us_county_central_appalachia.geojson"

    # Options for d_status are: "final" for fully cleaned products or "provisional" for
    # partially cleaned products. This is written into the data_status column of the table
    # during upload.
    table_name = "counties"

    gdf = gpd.read_file(infile)
    df = gdf.assign(access_date="2025-11-06")

    df = df.rename(
        columns={
            "GEOID": "geoid",
            "STATEFP": "statefp",
            "COUNTYFP": "countyfp",
            "COUNTYNS": "countyns",
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
            "access_date": "access_date"
        }
    )

    # Clean lat/lon (remove '+' and cast to float)
    for col in ("intptlat", "intptlon"):
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace("+", "", regex=False), errors="coerce"
            )

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=counties_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_huc_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Desktop/WBD_National_GPKG/WBD_HUC_2_to_12_central_appalachia.geojson"

    table_name = "huc_boundaries"

    gdf = gpd.read_file(infile)
    gdf.insert(0, "st_id", gdf["objectid"].astype(str) + "_" + (gdf.index + 1).astype(str))

    df = gdf.assign(access_date="2025-11-06")

    df = df.rename(
        columns={
            "st_id": "st_id",
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
            "access_date": "access_date",
        }
    )

    print(df.head(3))
    print(df.dtypes)

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=huc_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_eamlis_table_from_local():
    engine = connect_tcp_socket()

    infile = ("~/Desktop/eAMLIS/eAMLIS_data_accessed_2025-10-24_4326.geojson")

    table_name = "eamlis"

    gdf = gpd.read_file(infile)
    df = gdf.assign(access_date="2025-10-24")

    df = df.rename(
        columns={
            "OBJECTID": "objectid",
            "AMLIS_KEY": "amlis_key",
            "STATE_KEY": "state_key",
            "PA_NUMBER": "pa_number",
            "PA_NAME": "pa_name",
            "PU_NUMBER": "pu_number",
            "PU_NAME": "pu_name",
            "EST_LATITUDE": "est_latitude",
            "EST_LONGITUDE": "est_longitude",
            "LAT_DEG": "lat_deg",
            "LAT_MIN": "lat_min",
            "LON_DEG": "lon_deg",
            "LON_MIN": "lon_min",
            "COUNTY": "county",
            "FIPS_CODE": "fips_code",
            "CONG_DIST": "cong_dist",
            "QUAD_NAME": "quad_name",
            "HUC_CODE": "huc_code",
            "WATERSHED": "watershed",
            "MINE_TYPE": "mine_type",
            "ORE_TYPES": "ore_types",
            "OWNER_PRIVATE": "owner_private",
            "OWNER_STATE": "owner_state",
            "OWNER_INDIAN": "owner_indian",
            "OWNER_BLM": "owner_blm",
            "OWNER_FOREST": "owner_forest",
            "OWNER_NATIONAL": "owner_national",
            "OWNER_OTHER": "owner_other",
            "POPULATION": "population",
            "DATE_PREPARED": "date_prepared",
            "DATE_REVISED": "date_revised",
            "PRIORITY": "priority",
            "PROB_TY_CD": "prob_ty_cd",
            "PROB_TY_NAME": "prob_ty_name",
            "PROGRAM": "program",
            "UNFD_UNITS": "unfd_units",
            "UNFD_METERS": "unfd_meters",
            "UNFD_COST": "unfd_cost",
            "UNFD_GPRA": "unfd_gpra",
            "FUND_UNITS": "fund_units",
            "FUND_METERS": "fund_meters",
            "FUND_COST": "fund_cost",
            "FUND_GPRA": "fund_gpra",
            "COMP_UNITS": "comp_units",
            "COMP_METERS": "comp_meters",
            "COMP_COST": "comp_cost",
            "COMP_GPRA": "comp_gpra",
            "TOTAL_UNITS": "total_units",
            "TOTAL_COST": "total_cost",
            "x": "x",
            "y": "y",
            "geometry": "geom",
            "access_date": "access_date"
        }
    )


    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=eamlis_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_ky_permits_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Documents/full_permit_dataset/ky_permits_final.geojson"
    state = "ky"

    table_name = "state_permits_" + state

    gdf = gpd.read_file(infile)
    df = gdf
    df = df.rename(
        columns={
            "geometry": "geom",
        }
    )

    # Add a new, SkyTruth ID, which is unique to each record, handles issues where there are multiple records
    # that share a permit_id.
    df = df.reset_index(drop=True)
    df["st_id"] = [f"st_{state}_" + str(i) for i in range(1, len(df) + 1)]

    # Reorder so unique_id is the first column
    cols = ["st_id"] + [c for c in df.columns if c != "st_id"]
    df = df[cols]

    # print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=ky_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_tn_permits_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Documents/full_permit_dataset/tn_permits_final.geojson"
    state = "tn"

    table_name = "state_permits_" + state

    gdf = gpd.read_file(infile)
    df = gdf
    df = df.rename(
        columns={
            "geometry": "geom",
        }
    )

    # Add a new, SkyTruth ID, which is unique to each record, handles issues where there are multiple records
    # that share a permit_id.
    df = df.reset_index(drop=True)
    df["st_id"] = [f"st_{state}_" + str(i) for i in range(1, len(df) + 1)]

    # Reorder so unique_id is the first column
    cols = ["st_id"] + [c for c in df.columns if c != "st_id"]
    df = df[cols]

    # print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=tn_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_va_permits_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Documents/full_permit_dataset/va_permits_final.geojson"
    state = "va"

    table_name = "state_permits_" + state

    gdf = gpd.read_file(infile)
    df = gdf
    df = df.rename(
        columns={
            "geometry": "geom",
        }
    )

    # Add a new, SkyTruth ID, which is unique to each record, handles issues where there are multiple records
    # that share a permit_id.
    df = df.reset_index(drop=True)
    df["st_id"] = [f"st_{state}_" + str(i) for i in range(1, len(df) + 1)]

    # Reorder so unique_id is the first column
    cols = ["st_id"] + [c for c in df.columns if c != "st_id"]
    df = df[cols]

    # Format release date column
    df["release_date"] = pd.to_datetime(df["release_date"], format="%m/%d/%Y", errors="coerce")

    # Fix integer columns
    integer_cols = ["post_smcra", "surf_mine"]
    for col in integer_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
            df[col] = df[col].astype("Int64")

    # Format date columns
    date_cols = ["created_date", "last_edit_date", "permit_status_date", "orig_issue", "anniversary", "pe_os_date", "app_date", "issue_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=va_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


def append_to_wv_permits_table_from_local():
    engine = connect_tcp_socket()

    infile = "~/Documents/full_permit_dataset/wv_permits_final.geojson"
    state = "wv"

    table_name = "state_permits_" + state

    gdf = gpd.read_file(infile)
    df = gdf
    df = df.rename(
        columns={
            "geometry": "geom",
        }
    )

    # Add a new, SkyTruth ID, which is unique to each record, handles issues where there are multiple records
    # that share a permit_id.
    df = df.reset_index(drop=True)
    df["st_id"] = [f"st_{state}_" + str(i) for i in range(1, len(df) + 1)]

    # Reorder so unique_id is the first column
    cols = ["st_id"] + [c for c in df.columns if c != "st_id"]
    df = df[cols]

    # Convert to 2D Geoms
    df["geom"] = df["geom"].apply(geom_convert_3d_to_2d)

    # Clean numeric columns by removing commas
    numeric_cols = ["bond_amount", "avail_bond", "full_bond"]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False), 
                errors="coerce"
            )

    # Fix integer columns
    integer_cols = ["active_vio", "total_vio", "surf_mine"]
    for col in integer_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
            df[col] = df[col].astype("Int64")

    # Format date columns
    date_cols = ["map_date", "mdate", "issue_date", "expir_date", "last_update"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # print(df.head(3))

    with engine.begin() as conn:
        df.to_sql(
            table_name,
            con=conn,
            if_exists="append",
            index=False,  # avoid stray index column
            method="multi",
            chunksize=1000,
            dtype=wv_permit_format_dict,
        )

    print(f"Data from: {infile} apppended to {table_name}.")


if __name__ == "__main__":
    append_to_annual_mining_table_from_local()
    append_to_annual_mining_table_from_local_directory()
    append_to_annual_mining_table_from_gcs()
    # append_to_highwall_detections_table_from_local()
    append_to_counties_table_from_local()
    append_to_huc_table_from_local()
    append_to_eamlis_table_from_local()
    append_to_ky_permits_table_from_local()
    append_to_tn_permits_table_from_local()
    append_to_va_permits_table_from_local()
    append_to_wv_permits_table_from_local()