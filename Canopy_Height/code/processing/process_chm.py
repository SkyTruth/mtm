'''
Produces a mosaicked CHM, DTM, and DSM for each county from the county's set of LAS files,
iterating through a list of counties. Reprojects all rasters to EPSG:3857.
'''

import os
import subprocess
import time
from osgeo import gdal, ogr, osr
whitebox_executable = os.path.abspath('whitebox-tools-master/target/release/whitebox_tools')

from Canopy_Height.code.ch_variables import (
    TN_COUNTIES,
    VA_COUNTIES,
    KY_COUNTIES,
    WV_COUNTIES,
    MAIN_DIR,
)

# Select state
state = 'wv'

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

    # Create directories to store DSM, DTM, and CHM mosaics
    county_dir = f"{MAIN_DIR}/{state}/{county}"
    os.makedirs(f'{county_dir}/dsm', exist_ok=True)
    os.makedirs(f'{county_dir}/dtm', exist_ok=True)
    os.makedirs(f'{county_dir}/chm', exist_ok=True)

    # Create DSM using all surface points
    dsm = [
        whitebox_executable,
        '--run="lidar_digital_surface_model"',
        f'--wd="{county_dir}/las"',
        f'--resolution={res}',
        '--radius=0.5',
        '--maxz=555'
    ]

    print(f"Creating DSMs for {county} county...")
    process = subprocess.run(dsm)
    if process.returncode != 0:
        print("Error:", process.stderr.decode())
    else:
        print(f"DSMs for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Mosaic all DSMs into one continuous surface model
    mosaic_dsm = [
        whitebox_executable,
        '--run="mosaic"',
        f'--wd="{county_dir}/las"',
        f'--output="{county_dir}/dsm/{county}_dsm_mosaic.tif"'
    ]

    print(f"Mosaicking DSMs for {county} county...")
    process = subprocess.run(mosaic_dsm)
    if process.returncode != 0:
        print("Error:", process.stderr.decode())
    else:
        print(f"DSM mosaic for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Remove individual DSM tiles
    os.chdir(f'{county_dir}/las')
    for fn in os.listdir():
        if fn.endswith(".tif"):
            os.remove(fn)

    # Reproject DSM mosaic to 3857
    print(f"Reprojecting DSM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{county_dir}/dsm/{county}_dsm_mosaic_3857.tif", srcDSOrSrcDSTab=f"{county_dir}/dsm/{county}_dsm_mosaic.tif",
                  options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("DSM reprojected.")

    # Create DTM using all ground points
    dtm = [
        whitebox_executable,
        '--run="lidar_tin_gridding"',
        f'--wd="{county_dir}/las"',
        '--parameter="elevation"',
        '--returns="all"',
        f'--resolution={res}',
        '--exclude_cls="0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"'
    ]

    print(f"Creating DTMs for {county} county...")
    process = subprocess.run(dtm)
    if process.returncode != 0:
        print("Error:", process.stderr.decode())
    else:
        print(f"DTMs for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Mosaic all DTMs into one continous terrain model
    mosaic_dtm = [
        whitebox_executable,
        '--run="mosaic"',
        f'--wd="{county_dir}/las"',
        f'--output="{county_dir}/dtm/{county}_dtm_mosaic.tif"'
    ]

    print(f"Mosaicking DTMs for {county} county...")
    process = subprocess.run(mosaic_dtm)
    if process.returncode != 0:
        print("Error:", process.stderr.decode())
    else:
        print(f"DTM mosaic for {county} county created successfully.")

    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Remove individual DTM tiles
    os.chdir(f'{county_dir}/las')
    for fn in os.listdir():
        if fn.endswith(".tif"):
            os.remove(fn)

    # Reproject DTM mosaic to 3857
    print(f"Reprojecting DTM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{county_dir}/dtm/{county}_dtm_mosaic_3857.tif", srcDSOrSrcDSTab=f"{county_dir}/dtm/{county}_dtm_mosaic.tif",
                  options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("DTM reprojected.")

    # Subtract DTM from DSM to get Canopy Height Model (CHM)
    subtract = [
        whitebox_executable,
        '--run="subtract"',
        f'--input1="{county_dir}/dsm/{county}_dsm_mosaic.tif"',
        f'--input2="{county_dir}/dtm/{county}_dtm_mosaic.tif"',
        f'--output="{county_dir}/chm/{county}_chm.tif"'
    ]

    print(f"Creating CHMs for {county} county...")
    process = subprocess.run(subtract)
    if process.returncode != 0:
        print("Error:", process.stderr.decode())
    else:
        print(f"CHM for {county} county created successfully.")
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')

    # Reproject CHM to 3857
    print(f"Reprojecting CHM for {county} county...")
    gdal.Warp(destNameOrDestDS=f"{county_dir}/chm/{county}_chm_3857.tif", srcDSOrSrcDSTab=f"{county_dir}/chm/{county}_chm.tif",
                  options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print("CHM reprojected.")
    
    # For Kentucky and Tennessee: must convert feet to meters for all 3 data products
    if state == 'ky' or state == 'tn':
        convert_dsm = [
            whitebox_executable,
            '--run="multiply"',
            f'--input1="{county_dir}/dsm/{county}_dsm_mosaic_3857.tif"',
            '--input2=0.3048',
            f'--output="{county_dir}/dsm/{county}_dsm_mosaic_meters.tif"'
        ]

        print("Executing command:")
        print(" ".join(convert_dsm))
        process = subprocess.run(convert_dsm)
        if process.returncode != 0:
            print("Error:", process.stderr.decode())
        else:
            print("DSM converted to meters.")

        convert_dtm = [
            whitebox_executable,
            '--run="multiply"',
            f'--input1="{county_dir}/dtm/{county}_dtm_mosaic_3857.tif"',
            '--input2=0.3048',
            f'--output="{county_dir}/dtm/{county}_dtm_mosaic_meters.tif"'
        ]

        print("Executing command:")
        print(" ".join(convert_dtm))
        process = subprocess.run(convert_dtm)
        if process.returncode != 0:
            print("Error:", process.stderr.decode())
        else:
            print("DTM converted to meters.")

        convert_chm = [
            whitebox_executable,
            '--run="multiply"',
            f'--input1="{county_dir}/chm/{county}_chm_3857.tif"',
            '--input2=0.3048',
            f'--output="{county_dir}/chm/{county}_chm_meters.tif"'
        ]

        print("Executing command:")
        print(" ".join(convert_chm))
        process = subprocess.run(convert_chm)
        if process.returncode != 0:
            print("Error:", process.stderr.decode())
        else:
            print("CHM converted to meters.")
    
print("All counties complete.")
current_time = time.time()
elapsed_time = (current_time - start_time) // 60
print(f'Total elapsed time: {elapsed_time} mins')