import requests
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import shape

def testing_access():
    
    mtm_url = (
        "https://tipg-896778192680.us-central1.run.app/collections/public.state_permits/items"
        "?filter=acres_curr<=100"
        "&limit=50"
    )

    data = requests.get(mtm_url).json()  # This is the response from the API
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    gdf.crs = "EPSG:4326"
    print(gdf)
    gdf.to_file("../../Desktop/api_permit_test.geojson", driver="GeoJSON")


# Get Permit By ID
def permit_test():
    url = ("https://tipg-896778192680.us-central1.run.app/collections/public.state_permits/items")

    # Define Filter Params (OGC API CQL)
    fitler_params = {
        "filter": "permit_id='S300116'",
        "limit": 5
    }
    data = requests.get(url, params=fitler_params).json()
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    gdf.crs = "EPSG:4326"
    print(gdf)

# Get Mine Footprint by ID
def fp_id_test():
    url = "https://tipg-896778192680.us-central1.run.app/collections/public.annual_mining/items"

    # This uses the OGC API "CQL" filter parameter
    fitler_params = {
        "filter": "id='-303538+140420'",
        "limit": 5
    }

    data = requests.get(url, params=fitler_params).json()
    gdf = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
    print(gdf)


# Get Mine FPs by BBOX
def fp_bbox_test():
    url = "https://tipg-896778192680.us-central1.run.app/collections/public.annual_mining/items"

    # BBOX Params are LL_X, LL_Y, UR_X, UR_Y (min_x, min_y, max_x, max_y)
    # This uses the OGC API "CQL" filter parameter
    fitler_params = {
        "bbox":"-81.8156,37.7981,-81.7882,37.8484",
        "limit": 5
    }

    data = requests.get(url, params=fitler_params).json()
    gdf = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
    print(gdf)


# Get Mine FPs intersecting Permit (specified by ID)
def fp_permit_test():
    test_permit_id = 'S501889'

    url_base = "https://tipg-896778192680.us-central1.run.app"
    permit_url = f"{url_base}/collections/public.state_permits/items/"

    # Define Filter Params (OGC API CQL)
    fitler_params = {
        "filter": f"permit_id='{test_permit_id}'",
        "limit": 5
    }

    permit_data = requests.get(permit_url, params=fitler_params).json()
    permit_gdf = gpd.GeoDataFrame.from_features(permit_data["features"])
    # permit_geom = permit_feat["geometry"]  # GeoJSON geometry
    print(permit_gdf)
    print(permit_gdf["geometry"])
    permit_geom =shape(permit_gdf["geometry"][0])
    # TODO: test if the [0] is needed, or how to handle issues where multi permits are defined > Will this even be an issue if the options are polygon/multipolygon


    # 3) Intersect against annual_mining
    mining_url = f"{url_base}/collections/public.annual_mining/items"
    mining_filter = {
        "filter-lang": "cql2-text",
        "filter": f"data_status!='provisional' AND s_intersects(geom,{permit_geom})",   # pass raw; requests will encode once
        "limit": 50,
    }
    mine_data = requests.get(mining_url, params=mining_filter).json()
    gdf = gpd.GeoDataFrame.from_features(mine_data["features"], crs="EPSG:4326")
    print(gdf)


# Get Permits intersecing Mine FP (specified by ID)
def permit_fp_test():
    test_mine_id = '-303538+140420'

    url_base = "https://tipg-896778192680.us-central1.run.app"
    mine_url = f"{url_base}/collections/public.annual_mining/items/"

    # Define Filter Params (OGC API CQL)
    fitler_params = {
        "filter": f"id='{test_mine_id}'",
        "limit": 5
    }

    mine_data = requests.get(mine_url, params=fitler_params).json()
    mine_gdf = gpd.GeoDataFrame.from_features(mine_data["features"])
    print(mine_gdf)
    print(mine_gdf["geometry"])
    mine_geom =shape(mine_gdf["geometry"][0])
    # TODO: test if the [0] is needed, or how to handle issues where multi permits are defined > Will this even be an issue if the options are polygon/multipolygon


    # 3) Intersect against annual_mining
    permit_url = f"{url_base}/collections/public.state_permits/items"
    permit_filter = {
        "filter-lang": "cql2-text",
        "filter": f"s_intersects(geom,{mine_geom})",   # pass raw; requests will encode once
        "limit": 50,
    }
    permit_data = requests.get(permit_url, params=permit_filter).json()
    permit_gdf = gpd.GeoDataFrame.from_features(permit_data["features"], crs="EPSG:4326")
    print(permit_gdf)

    # mine_gdf.to_file("../../Desktop/mine_sample.geojson",driver="GeoJSON")
    # permit_gdf.to_file("../../Desktop/permit_sample.geojson",driver="GeoJSON")

if __name__ == "__main__":
    testing_access()
    permit_test()
    fp_id_test()
    fp_bbox_test()
    fp_permit_test()
    permit_fp_test()