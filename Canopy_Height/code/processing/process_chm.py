'''
Produces a mosaicked CHM, DTM, and DSM for each county from the county's set of LAS files,
iterating through a list of counties. Reprojects all rasters to EPSG:3857.
'''

import os
import time
from osgeo import gdal, ogr, osr
import whitebox
wbt = whitebox.WhiteboxTools()

from mtm_utils.variables import (
    LIDAR_DIR,
    TN_COUNTIES,
    KY_COUNTIES,
    VA_COUNTIES,
    WV_COUNTIES
)

# Select state
state = 'tn'

# Assign counties and source CRS based on state
if state == 'tn':
    counties = TN_COUNTIES
    source_crs = 'EPSG:6576'
elif state == 'ky':
    counties = KY_COUNTIES
    source_crs = 'EPSG:3089'
elif state == 'va':
    counties = VA_COUNTIES
    source_crs = 'EPSG:6346'
elif state == 'wv':
    counties = WV_COUNTIES
    source_crs = 'EPSG:6350'

# Assign resolution based on state
# Because KY and TN are in feet, while WV and VA are in meters
if state == 'ky' or state == 'tn':
    res = 32.8084
else:
    res = 10

# Iterate over each county in list
for county in counties:
    start_time = time.time()

    # Define variables
    dir = f"{LIDAR_DIR}/{state}/{county}/"
    os.makedirs(f'{dir}{county}/dsm', exist_ok=True)
    os.makedirs(f'{dir}{county}/dtm', exist_ok=True)
    os.makedirs(f'{dir}{county}/chm', exist_ok=True)

    # Set working directory for whitebox
    las_dir = os.path.abspath(f"{dir}las")
    wbt.set_working_dir(las_dir)

    # Create DSM using all surface points
    print(f"Creating DSMs for {county} county...")
    wbt.lidar_digital_surface_model(
        resolution=res,
        radius=0.5,
        maxz=555
    )
    print(f"DSMs for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Mosaic all DSMs into one continuous surface model
    print(f"Mosaicking DSMs for {county} county...")
    wbt.mosaic(
        output=f"{dir}dsm/{county}_dsm_mosaic.tif"
    )
    print(f"DSM mosaic for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Remove individual DSM tiles
    os.chdir(las_dir)
    for fn in os.listdir():
        if fn.endswith(".tif"):
            os.remove(fn)

    # Reproject DSM mosaic to 3857
    print(f"Reprojecting DSM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{dir}dsm/{county}_dsm_mosaic_3857.tif", 
              srcDSOrSrcDSTab=f"{dir}dsm/{county}_dsm_mosaic.tif",
              options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("DSM reprojected.")

    # Create DTM using all ground points
    print(f"Creating DTMs for {county} county...")
    wbt.lidar_tin_gridding(
        parameter="elevation",
        returns="all",
        resolution=res,
        exclude_cls="0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"
    )
    print(f"DTMs for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Mosaic all DTMs into one continuous terrain model
    print(f"Mosaicking DTMs for {county} county...")
    wbt.mosaic(
        output=f"{dir}dtm/{county}_dtm_mosaic.tif"
    )
    print(f"DTM mosaic for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Remove individual DTM tiles
    os.chdir(las_dir)
    for fn in os.listdir():
        if fn.endswith(".tif"):
            os.remove(fn)

    # Reproject DTM mosaic to 3857
    print(f"Reprojecting DTM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{dir}dtm/{county}_dtm_mosaic_3857.tif", 
              srcDSOrSrcDSTab=f"{dir}dtm/{county}_dtm_mosaic.tif",
              options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("DTM reprojected.")

    # Subtract DTM from DSM to get Canopy Height Model (CHM)
    print(f"Creating CHM for {county} county...")
    wbt.subtract(
        input1=f"{dir}dsm/{county}_dsm_mosaic.tif",
        input2=f"{dir}dtm/{county}_dtm_mosaic.tif",
        output=f"{dir}chm/{county}_chm.tif"
    )
    print(f"CHM for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Reproject CHM to 3857
    print(f"Reprojecting CHM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{dir}chm/{county}_chm_3857.tif", 
              srcDSOrSrcDSTab=f"{dir}chm/{county}_chm.tif",
              options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("CHM reprojected.")
    
    # For Kentucky and Tennessee: must convert feet to meters for all 3 data products
    if state == 'ky' or state == 'tn':
        print("Converting DSM to meters...")
        wbt.multiply(
            input1=f"{dir}dsm/{county}_dsm_mosaic_3857.tif",
            input2=0.3048,
            output=f"{dir}dsm/{county}_dsm_mosaic_meters.tif"
        )
        print("DSM converted to meters.")

        print("Converting DTM to meters...")
        wbt.multiply(
            input1=f"{dir}dtm/{county}_dtm_mosaic_3857.tif",
            input2=0.3048,
            output=f"{dir}dtm/{county}_dtm_mosaic_meters.tif"
        )
        print("DTM converted to meters.")

        print("Converting CHM to meters...")
        wbt.multiply(
            input1=f"{dir}chm/{county}_chm_3857.tif",
            input2=0.3048,
            output=f"{dir}chm/{county}_chm_meters.tif"
        )
        print("CHM converted to meters.")
    
print("All counties complete.")
current_time = time.time()
elapsed_time = (current_time - start_time) // 60
print(f'Total elapsed time: {elapsed_time} mins')