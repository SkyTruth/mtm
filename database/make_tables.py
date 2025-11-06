import sqlalchemy
from mtm_utils.cloud_sql_utils import connect_tcp_socket


def create_test_table():
    engine = connect_tcp_socket()

    # Example table schema
    create_stmt = """
    CREATE TABLE IF NOT EXISTS local_test_table_other_FINAL (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print("Table created successfully.")


def create_annual_mining_table():
    engine = connect_tcp_socket()
    table_name = "annual_mining"

    # SQL statement for creating table
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id              TEXT,
            mining_year     INT,
            area            DOUBLE PRECISION,
            data_status     TEXT,
            geom            geometry(MultiPolygon, 4326),
            -- This line below, assigns primary key based on id and mining year, 
            -- allowing for duplicate id values.
            CONSTRAINT {table_name}_pkey PRIMARY KEY (id, mining_year)
        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_table_sql))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_highwall_detections_table():
    engine = connect_tcp_socket()
    table_name = "highwall_detections"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            highwall_id         INT,
            rec_status          TEXT,
            rec_status_yr       INT,
            earliest_vis_yr     INT,
            first_mined_yr      INT,
            last_mined_yr       INT,
            max_age             INT,
            min_age             INT,
            mid_age             DOUBLE PRECISION,
            age_uncertainty     DOUBLE PRECISION,
            lidar_project       TEXT,
            lidar_yr            INT,
            mean_slope          DOUBLE PRECISION,
            med_slope           DOUBLE PRECISION,
            max_slope           DOUBLE PRECISION,
            all_permit_ids      TEXT,
            segment_id          INT,
            raw_length          DOUBLE PRECISION,
            length              DOUBLE PRECISION,
            base_elevation      DOUBLE PRECISION,
            top_elevation       DOUBLE PRECISION,
            height              DOUBLE PRECISION,
            min_cost            DOUBLE PRECISION,
            mid_cost            DOUBLE PRECISION,
            max_cost            DOUBLE PRECISION,
            permit_id           TEXT,
            state               TEXT,
            permittee           TEXT,
            mine_name           TEXT,
            mine_status         TEXT,
            bond_status         TEXT,
            avail_bond          DOUBLE PRECISION,
            full_bond           DOUBLE PRECISION,
            post_smcra          INT,
            geom                geometry(MultiLineString, 4326)
        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_counties_table():
    engine = connect_tcp_socket()
    table_name = "counties"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            geoid	        INT PRIMARY KEY,
            statefp         INT,
            countyfp	    INT,
            countyns	    INT,
            geoidfq	        TEXT,
            name	        TEXT,
            namelsad	    TEXT,
            lsad	        INT,
            classfp         TEXT,
            mtfcc	        TEXT,
            csafp	        INT,
            cbsafp          INT,
            metdivfp	    INT,
            funcstat	    TEXT,
            aland	        DOUBLE PRECISION,
            awater	        DOUBLE PRECISION,
            intptlat	    DOUBLE PRECISION,
            intptlon        DOUBLE PRECISION,
            geom            geometry(MultiPolygon, 4326),
            access_date     TEXT

        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_huc_table():
    engine = connect_tcp_socket()
    table_name = "huc_boundaries"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id                       TEXT PRIMARY KEY,
            objectid                    INT,
            tnmid                       TEXT,
            metasourceid                TEXT,
            sourcedatadesc              TEXT,
            sourceoriginator            TEXT,
            sourcefeatureid             TEXT,
            loaddate                    DATE,
            referencegnis_ids           TEXT,
            areaacres                   DOUBLE PRECISION,
            areasqkm                    DOUBLE PRECISION,
            states                      TEXT,
            huc10                       TEXT,
            name                        TEXT,
            hutype                      TEXT,
            humod                       TEXT,
            globalid                    TEXT,
            shape_Length                DOUBLE PRECISION,
            shape_Area                  DOUBLE PRECISION,
            hutype_description          TEXT,
            huc12                       TEXT,
            tohuc                       TEXT,
            noncontributingareaacres    DOUBLE PRECISION,
            noncontributingareasqkm     DOUBLE PRECISION,
            huc2                        TEXT,
            huc4                        TEXT,
            huc6                        TEXT,
            huc8                        TEXT,
            geom                        geometry(MultiPolygon, 4326),
            access_date                 TEXT
        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_eamlis_table():
    engine = connect_tcp_socket()
    table_name = "eamlis"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            OBJECTID        INT PRIMARY KEY,
            AMLIS_KEY       TEXT,
            STATE_KEY       TEXT,
            PA_NUMBER       TEXT,
            PA_NAME         TEXT,
            PU_NUMBER       TEXT,
            PU_NAME         TEXT,
            EST_LATITUDE    DOUBLE PRECISION,
            EST_LONGITUDE   DOUBLE PRECISION,
            LAT_DEG         INT,
            LAT_MIN         INT,
            LON_DEG         INT,
            LON_MIN         INT,
            COUNTY          TEXT,
            FIPS_CODE       TEXT,
            CONG_DIST       DOUBLE PRECISION,
            QUAD_NAME       TEXT,
            HUC_CODE        DOUBLE PRECISION,
            WATERSHED       TEXT,
            MINE_TYPE       TEXT,
            ORE_TYPES       TEXT,
            OWNER_PRIVATE   DOUBLE PRECISION,
            OWNER_STATE     DOUBLE PRECISION,
            OWNER_INDIAN    DOUBLE PRECISION,
            OWNER_BLM       DOUBLE PRECISION,
            OWNER_FOREST    DOUBLE PRECISION,
            OWNER_NATIONAL  DOUBLE PRECISION,
            OWNER_OTHER     DOUBLE PRECISION,
            POPULATION      TEXT,
            DATE_PREPARED   DATE,
            DATE_REVISED    DATE,
            PRIORITY        TEXT,
            PROB_TY_CD      TEXT,
            PROB_TY_NAME    TEXT,
            PROGRAM         TEXT,
            UNFD_UNITS      TEXT,
            UNFD_METERS     TEXT,
            UNFD_COST       TEXT,
            UNFD_GPRA       TEXT,
            FUND_UNITS      TEXT,
            FUND_METERS     TEXT,
            FUND_COST       TEXT,
            FUND_GPRA       TEXT,
            COMP_UNITS      TEXT,
            COMP_METERS     TEXT,
            COMP_COST       TEXT,
            COMP_GPRA       TEXT,
            TOTAL_UNITS     TEXT,
            TOTAL_COST      TEXT,
            x               DOUBLE PRECISION,
            y               DOUBLE PRECISION,
            geom            geometry(Point, 4326),
            access_date     TEXT
        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


"""
def create_wv_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits_wv"

    # SQL statement for creating table
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id       TEXT PRIMARY KEY,
            permit_id   TEXT,
            mapdate	    DATE,
            maptype     TEXT,
            active_vio	INT,
            total_vio	INT,
            facility_n  TEXT,
            acres_orig	DOUBLE PRECISION,
            acres_curr	DOUBLE PRECISION,
            acres_dist	DOUBLE PRECISION,
            acres_recl	DOUBLE PRECISION,
            mstatus     TEXT,
            mdate	    DATE,
            issue_date	DATE,
            expire_dat	DATE,
            permittee   TEXT,
            operator    TEXT,
            last_updat	DATE,
            comments    TEXT,
            pstatus     TEXT,
            ma_area     TEXT,
            ma_contour  TEXT,
            ma_mtntop   TEXT,
            ma_steepsl  TEXT,
            ma_auger    TEXT,
            ma_roompil  TEXT,
            ma_longwal  TEXT,
            ma_refuse   TEXT,
            ma_loadout  TEXT,
            ma_preppla  TEXT,
            ma_haulroa  TEXT,
            ma_rockfil  TEXT,
            ma_impound  TEXT,
            ma_tipple   TEXT,
            pmlu1       TEXT,
            pmlu2       TEXT,
            weblink1    TEXT,
            st_area_sh  FLOAT,
            st_length_  FLOAT,
            geom        geometry(MultiPolygon, 4326)
        );
    '''

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


"""

# TODO: rewrite functions for creating permit tables

if __name__ == "__main__":
    create_annual_mining_table()
    create_highwall_detections_table()
    create_counties_table()
    create_huc_table()
    create_eamlis_table()
