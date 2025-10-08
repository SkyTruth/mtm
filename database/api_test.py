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


def permit_test():
    mtm_url = (
        "https://tipg-896778192680.us-central1.run.app/collections/public.state_permits/items"
        "?filter=permit_id='S300116'"
        "&limit=5"
    )
    
    data = requests.get(mtm_url).json()  # This is the response from the API
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    gdf.crs = "EPSG:4326"
    print(gdf)


def permit_test_v2():
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


def fp_permit_test():
    test_permit_id = 'S501889'

    url_base = "https://tipg-896778192680.us-central1.run.app"
    permit_url = f"{url_base}/collections/public.state_permits/items/"

    # Define Filter Params (OGC API CQL)
    fitler_params = {
        "filter": "permit_id='S501889'",
        "limit": 5
    }

    permit_data = requests.get(permit_url, params=fitler_params).json()
    permit_gdf = gpd.GeoDataFrame.from_features(permit_data["features"])
    # permit_geom = permit_feat["geometry"]  # GeoJSON geometry
    print(permit_gdf)
    print(permit_gdf["geometry"])
    permit_geom =shape(permit_gdf["geometry"][0])
    #TODO: test if the [0] is needed, or how to handle issues where multi permits are defined


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



if __name__ == "__main__":
    # testing_access()
    # permit_test()
    # permit_test_v2()
    # fp_id_test()
    # fp_bbox_test()
    fp_permit_test()