import sqlalchemy
from mtm_utils.cloud_sql_utils import connect_tcp_socket


def create_test_table():
    engine = connect_tcp_socket()

    # Example table schema
    create_stmt = """
    CREATE TABLE IF NOT EXISTS alana_table_test (
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
            highwall_id         INT PRIMARY KEY,
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
            geom                geometry(MultiPolygon, 4326)
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


def create_ky_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits_ky"

    # SQL statement for creating table
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id           TEXT PRIMARY KEY,
            permit_id       TEXT,
            feat_cls        TEXT,
            source          TEXT,
            type_flag       TEXT,
            acres           DOUBLE PRECISION,
            quadrangle      TEXT,
            status_code1    TEXT,
            permittee1      TEXT,
            region          TEXT,
            activity        TEXT,
            act_rel         TEXT,
            issue_date      DATE,
            orig_id         TEXT,
            national_id     TEXT,
            shape_length    DOUBLE PRECISION,
            per_type        TEXT,
            shape_area      DOUBLE PRECISION,
            permittee2      TEXT,
            status_code2    TEXT,
            status_desc     TEXT,
            inspectable     TEXT,
            curr_bond       DOUBLE PRECISION,
            orig_bond       DOUBLE PRECISION,
            highwall_total  INT,
            highwall_comp   INT,
            highwall_viol   INT,
            permittee3      TEXT,
            mine_name       TEXT,
            post_smcra      INT,
            op_status       TEXT,
            gm_bond_status  TEXT,
            prep_ref        TEXT,
            avail_bond      DOUBLE PRECISION,
            full_bond       DOUBLE PRECISION,
            permittee       TEXT,
            mine_status     TEXT,
            bond_status     TEXT,
            surf_mine       INT,
            geom            geometry(MultiPolygon, 4326)
        );
    '''

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_wv_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits_wv"

    # SQL statement for creating table
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id           TEXT PRIMARY KEY,
            permit_id       TEXT,
            map_date        DATE,
            map_type        TEXT,
            active_vio      INT,
            total_vio       INT,
            mine_name       TEXT,
            acres_orig      DOUBLE PRECISION,
            acres_curr      DOUBLE PRECISION,
            acres_dist      DOUBLE PRECISION,
            acres_recl      DOUBLE PRECISION,
            mstatus         TEXT,
            mdate           DATE,
            issue_date      DATE,
            expir_date      DATE,
            permittee       TEXT,
            operator        TEXT,
            last_update     DATE,
            comments        TEXT,
            pstatus         TEXT,
            area            TEXT,
            contour         TEXT,
            mtntop          TEXT,
            steepslope      TEXT,
            auger           TEXT,
            room_pillar     TEXT,
            longwall        TEXT,
            refuse          TEXT,
            loadout         TEXT,
            prep_plant      TEXT,
            haul_road       TEXT,
            rockfill        TEXT,
            impoundment     TEXT,
            tipple          TEXT,
            pmlu1           TEXT,
            pmlu2           TEXT,
            weblink         TEXT,
            st_area         DOUBLE PRECISION,
            st_length       DOUBLE PRECISION,
            status_desc     TEXT,
            permit_status   TEXT,
            bond_amount     DOUBLE PRECISION,
            type            TEXT,
            current_status  TEXT,
            post_smcra      TEXT,
            op_status       TEXT,
            gm_bond_status  TEXT,
            prep_ref        TEXT,
            avail_bond      DOUBLE PRECISION,
            full_bond       DOUBLE PRECISION,
            mine_status     TEXT,
            bond_status     TEXT,
            surf_mine       INT,
            geom            geometry(MultiPolygon, 4326)
        );
    '''

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_va_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits_va"

    # SQL statement for creating table
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id               TEXT PRIMARY KEY,
            permit_id           TEXT,
            permittee           TEXT,
            release_date        DATE,
            trans_from          TEXT,
            comment             TEXT,
            acres               DOUBLE PRECISION,
            permit_type         TEXT,
            global_id           TEXT,
            created_user        TEXT,
            created_date        DATE,
            last_edit_user      TEXT,
            last_edit_date      DATE,
            st_area             DOUBLE PRECISION,
            st_length           DOUBLE PRECISION,
            bond_code           TEXT,
            app_no              TEXT,
            permittee_code      TEXT,
            operation           TEXT,
            county              TEXT,
            seams               TEXT,
            quads               TEXT,
            mine_types          TEXT,
            permit_status       TEXT,
            permit_status_date  DATE,
            orig_issue          DATE,
            anniversary         DATE,
            bond_type           TEXT,
            remining            TEXT,
            remining_acres      DOUBLE PRECISION,
            underground         TEXT,
            mtntop              TEXT,
            steepslope          TEXT,
            auger               TEXT,
            non_aoc             TEXT,
            tbl_os_code         TEXT,
            tbl_os_desc         TEXT,
            pe_os_date          DATE,
            rec_status          TEXT,
            layer               TEXT,
            gm_mine_name        TEXT,
            post_smcra          INT,
            op_status           TEXT,
            gm_bond_status      TEXT,
            app_date            DATE,
            prep_ref            TEXT,
            bond_method         TEXT,
            permitted_acres     DOUBLE PRECISION,
            bonded_acres        DOUBLE PRECISION,
            bond_amount         DOUBLE PRECISION,
            mine_name           TEXT,
            mine_status         TEXT,
            bond_status         TEXT,
            issue_date          DATE,
            surf_mine           INT,
            full_bond           DOUBLE PRECISION,
            avail_bond          DOUBLE PRECISION,
            geom                geometry(MultiPolygon, 4326)
        );
    '''

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")


def create_tn_permits_table():
    engine = connect_tcp_socket()
    table_name = "state_permits_tn"

    # SQL statement for creating table
    create_stmt = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            st_id           TEXT PRIMARY KEY,
            permittee       TEXT,
            op_status       TEXT,
            mine_name       TEXT,
            permit_id       TEXT,
            msha_id         TEXT,
            national_id     TEXT,
            coal_beds       TEXT,
            inspectable     INT,
            post_smcra      INT,
            acres           DOUBLE PRECISION,
            issue_date      DATE,
            edit_date       DATE,
            area            INT,
            contour         INT,
            mtntop          INT,
            steepslope      INT,
            highwall        INT,
            auger           INT,
            comment         TEXT,
            contact         INT,
            info            TEXT,
            bond_type       TEXT,
            status          TEXT,
            bond_amount     DOUBLE PRECISION,
            land_req_bond   DOUBLE PRECISION,
            water_req_bond  DOUBLE PRECISION,
            total_req_bond  DOUBLE PRECISION,
            shortfall       DOUBLE PRECISION,
            notes           TEXT,
            prep_ref        TEXT,
            gm_bond_status  TEXT,
            mine_status     TEXT,
            bond_status     TEXT,
            surf_mine       INT,
            full_bond       DOUBLE PRECISION,
            avail_bond      DOUBLE PRECISION,
            geom            geometry(MultiPolygon, 4326)
        );
    '''

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_stmt))
        conn.commit()
        print(f"Successfully created table: {table_name}.")

if __name__ == "__main__":
    create_annual_mining_table()
    create_highwall_detections_table()
    create_counties_table()
    create_huc_table()
    create_eamlis_table()
    create_test_table()
    create_ky_permits_table()
    create_wv_permits_table()
    create_va_permits_table()
    create_tn_permits_table()
