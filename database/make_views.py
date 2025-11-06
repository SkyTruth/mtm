import sqlalchemy
from mtm_utils.cloud_sql_utils import connect_tcp_socket


def create_test_view():
    engine = connect_tcp_socket()

    create_view_sql = """
    -- Create public.v_annual_mining_by_huv
    CREATE OR REPLACE VIEW public.TEST_VIEW AS (
    SELECT
        m.id,
        m.mining_year,
        m.area,
        m.data_status,
        m.geom AS mine_geom,
        -- the columns from huc_boundaries, that can be used to filter the mines
        h.objectid,
        h.tnmid,
        h.huc2,
        h.huc4,
        h.huc6,
        h.huc8,
        h.huc10,
        h.huc12

    FROM "public"."annual_mining" m
    JOIN "public"."huc_boundaries" h

    -- This is a coarse check
    ON m.geom && h.geom

    -- This is a finer check, and may remove some results registered as overlapping by && above that don't truly intersect
    AND ST_Intersects(
        CASE WHEN ST_SRID(m.geom) = ST_SRID(h.geom) THEN m.geom
        ELSE ST_Transform(m.geom, ST_SRID(h.geom)) END,
        h.geom
        )
    )
    """
    print("This has been tested, and is not intended to be re-run; it creates a simpler version of the view created by create_annual_mining_by_huc_view")
    # with engine.connect() as conn:
    #     conn.execute(sqlalchemy.text(create_view_sql))
    #     conn.commit()
    #     print("View created successfully.")


def create_annual_mining_by_huc_view():
    engine = connect_tcp_socket()

    create_view_sql = """
    -- Create public.v_annual_mining_by_huv
    CREATE OR REPLACE VIEW public.v_annual_mining_by_huc AS (
        SELECT
            m.id,
            m.mining_year,
            m.area,
            m.data_status,
            m.geom AS mine_geom,
            -- the columns from huc_boundaries, that can be used to filter the mines
            h.st_id,
            h.objectid,
            h.tnmid,
            h.areaacres,
            h.areasqkm,
            h.states,
            h.name,
            h.globalid,
            h.huc2,
            h.huc4,
            h.huc6,
            h.huc8,
            h.huc10,
            h.huc12
            -- h.geom AS huc_geom,
        
        FROM "public"."annual_mining" m
        JOIN "public"."huc_boundaries" h

        -- This is a coarse check
        ON m.geom && h.geom

        -- This is a finer check, and may remove some results registered as overlapping by && above that don't truly intersect
        AND ST_Intersects(
            CASE WHEN ST_SRID(m.geom) = ST_SRID(h.geom) THEN m.geom
            ELSE ST_Transform(m.geom, ST_SRID(h.geom)) END,
            h.geom
        )
    )
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_view_sql))
        conn.commit()
        print("View created successfully.")


def create_annual_mining_by_county_view():
    engine = connect_tcp_socket()

    create_view_sql = """
    -- Create public.v_annual_mining_by_county
    CREATE OR REPLACE VIEW public.v_annual_mining_by_county AS (
        SELECT
            m.id,
            m.mining_year,
            m.area,
            m.data_status,
            m.geom AS mine_geom,
            -- the columns from counties, that can be used to filter the mines
            c.statefp,
            c.countyfp,
            c.countyns, 
            c.geoid, 
            c.geoidfq, 
            c.name 
            -- c.geom AS county_geom
        
        FROM "public"."annual_mining" m
        JOIN "public"."counties" c

        -- This is a coarse check
        ON m.geom && c.geom

        -- This is a finer check, and may remove some results registered as overlapping by && above that don't truly intersect
        AND ST_Intersects(
            CASE WHEN ST_SRID(m.geom) = ST_SRID(c.geom) THEN m.geom
            ELSE ST_Transform(m.geom, ST_SRID(c.geom)) END,
            c.geom
        )
    )
    """

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text(create_view_sql))
        conn.commit()
        print("View created successfully.")


if __name__ == "__main__":
    # create_test_view()
    # create_annual_mining_by_huc_view()
    create_annual_mining_by_county_view()