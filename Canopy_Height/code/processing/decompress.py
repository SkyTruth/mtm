'''
Decompresses LAZ files into LAS files by county, iterating through a list of counties.
For WV counties, additionally reprojects all LAS files to EPSG:6350 for consistency.

Inputs: 
    - List of tile IDs for each county (e.g. gcs/lidar_data/tile_IDs/anderson.csv)
    - Compressed LAZ files in the state directory (e.g. gcs/lidar_data/tn/TN_27_County_B1_2248661NE.laz)

Outputs:
    - Decompressed LAS files for each county in the corresponding county directory (e.g. gcs/lidar_data/tn/anderson/las/anderson_TN_27_County_B1_2430677NE.las)
'''

import os
import laspy
from multiprocessing import Pool
import pandas as pd
import time
import pyproj
from pyproj import CRS, Proj, transform

from Canopy_Height.code.ch_variables import (
    TN_COUNTIES,
    KY_COUNTIES,
    VA_COUNTIES,
    WV_COUNTIES,
    MAIN_DIR,
    TILE_IDS_DIR,
    CPU_CORES,
)

# Specify state
state = 'tn'
state_dir = f'{MAIN_DIR}/{state}'

if state == 'tn':
    counties = TN_COUNTIES
elif state == 'ky':
    counties = KY_COUNTIES
elif state == 'va':
    counties = VA_COUNTIES
elif state == 'wv':
    counties = WV_COUNTIES

# Decompress all the tiles in each county
for county in counties:

    # Get list of tile IDs from county
    df = pd.read_csv(f'{TILE_IDS_DIR}/{county}.csv', header=0)
    tile_IDs = df.iloc[:, 0].tolist()

    # Count tile IDs and check for duplicates
    print(f'{len(tile_IDs)} tile IDs in {county} county.')
    print(f'{len(set(tile_IDs))} unique tile IDs in {county} county.')

    # Identify any duplicate tile IDs
    uniques = set()
    duplicates = set()
    for tile_ID in tile_IDs:
        if tile_ID in uniques:
            duplicates.add(tile_ID)
        else:
            uniques.add(tile_ID)
    print("Duplicates:")
    print(list(duplicates))

    # Create directory to store decompressed las files for the county
    county_las_dir = f'{state_dir}/{county}/las'
    os.makedirs(county_las_dir, exist_ok=True)

    # Iterate through the state laz bucket and decompress to las
    start_time = time.time()

    def decompress(fn):
        for ID in tile_IDs:
            if fn.endswith(f'_{ID}.laz'):
                name = fn.replace('.laz', '.las')
                path = f'{county_las_dir}/{county}_{name}'
                if not os.path.exists(path):
                    laz = laspy.read(f'{state_dir}/{fn}')
                    las = laspy.convert(laz)
                    
                    if state == 'wv':
                        # Define function to assign source CRS based on lidar project (for WV tiles only)
                        def get_source_crs(fn):
                            if "VA_NRCS_South_Central_B1" in fn:
                                return pyproj.CRS("EPSG:6346")
                            elif "VA_R3_Southwest_A" in fn:
                                return pyproj.CRS("EPSG:6346")
                            elif "WV_R3_East" in fn:
                                return pyproj.CRS("EPSG:26917")
                            else:
                                return pyproj.CRS("EPSG:6350")

                        # Define function to reproject LAS files (for WV tiles only)
                        def reproject(las, source_crs):
                            target_crs = pyproj.CRS('EPSG:6350')
                            transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)
                            xyz = transformer.transform(las.x, las.y, las.z)
                            las.x, las.y, las.z = xyz
                            las.header.add_crs(target_crs)
                        
                        source_crs = get_source_crs(fn)
                        if source_crs != pyproj.CRS("EPSG:6350"):
                            reproject(las, source_crs)
                    
                    las.write(path)

    # Parallelize over all CPU cores
    num_processes = CPU_CORES
    print(f"Decompressing tiles from {county} county...")
    with Pool(num_processes) as pool:
        pool.map(decompress, os.listdir(state_dir))

    # Print results and elapsed time
    print(f'Successfully converted {len(os.listdir(county_las_dir))} LAS files for {county} county.')
    print(f'Successfully converted {len(set(os.listdir(county_las_dir)))} unique LAS files for {county} county.')
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Elapsed time: {elapsed_time} mins')

    # Check to ensure list of tile IDs is identical to list of decompressed files
    # Print any exceptions
    def extract_IDs(las_files):
        decompressed_IDs = []
        for fn in las_files:
            last_underscore_index = fn.rfind("_")
            start_index = last_underscore_index + 1
            end_index = fn.rfind(".")
            tile_ID = fn[start_index:end_index]
            decompressed_IDs.append(tile_ID)
        return set(decompressed_IDs)

    decompressed_IDs = extract_IDs(os.listdir(county_las_dir))
    tile_IDs = set(tile_IDs)

    unique_to_IDs = tile_IDs - decompressed_IDs
    unique_to_decompressed = decompressed_IDs - tile_IDs

    print(f'Only in tile IDs: {unique_to_IDs}')
    print(f'Only in decompressed bucket: {unique_to_decompressed}')

print('All counties complete.')
current_time = time.time()
elapsed_time = (current_time - start_time) // 60
print(f'Total elapsed time: {elapsed_time} mins')