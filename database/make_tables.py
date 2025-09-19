from mtm_utils.cloud_sql_utils import connect_tcp_socket
import sqlalchemy


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


def create_cumulative_mining_table():
    engine = connect_tcp_socket()
    table_name = "cumulative_mining"

    # SQL statement for creating table
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id              TEXT,
            mining_year     INT,
            area            DOUBLE PRECISION,
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


def create_highwall_centerlines_table():
    engine = connect_tcp_socket()
    table_name = "highwall_centerlines"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id              TEXT PRIMARY KEY,
            detect_length   FLOAT,
            geom            geometry(MultiPolygon, 4326)
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
            STATEFP   INT,
            COUNTYFP	INT,
            COUNTYNS	INT,
            GEOID	    INT,
            GEOIDFQ	    TEXT,
            NAME	    TEXT,
            NAMELSAD	TEXT,
            LSAD	    INT,
            CLASSFP     TEXT,
            MTFCC	    TEXT,
            CSAFP	    INT,
            CBSAFP      INT,
            METDIVFP	TEXT,
            FUNCSTAT	TEXT,
            ALAND	    INT,
            AWATER	    INT,
            INTPTLAT	FLOAT,
            INTPTLON    FLOAT,
            geom        geometry(MultiPolygon, 4326)
        );
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits"

    # SQL statement for creating table
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            permit_id   TEXT,
            mapdate	    DATE,
            maptype     TEXT,
            active_vio	INT,
            total_vio	INT,
            facility_n  TEXT,
            acres_orig	INT,
            acres_curr	INT,
            acres_dist	INT,
            acres_recl	INT,
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
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


if __name__ == "__main__":
    create_annual_mining_table()
    # create_cumulative_mining_table()
    # create_highwall_centerlines_table()
    # create_counties_table()
    # create_permits_table()
