'''
Decompresses LAZ files into LAS files by county, iterating through a list of counties.
Additionally reprojects all LAS files to EPSG:6350. Used for West Virginia counties.
'''

import os
import subprocess
import laspy
from multiprocessing import Pool
import pandas as pd
import time
import pyproj
from pyproj import CRS, Proj, transform
from functools import partial

from mtm_utils.variables import (
    LIDAR_DIR,
    TILE_IDS_DIR,
    WV_COUNTIES
)

# Define function to assign source CRS based on lidar project
def get_source_crs(fn):
    if "VA_NRCS_South_Central_B1" in fn:
        return pyproj.CRS("EPSG:6346")
    elif "VA_R3_Southwest_A" in fn:
        return pyproj.CRS("EPSG:6346")
    elif "WV_R3_East" in fn:
        return pyproj.CRS("EPSG:26917")
    else:
        return pyproj.CRS("EPSG:6350")

# Define function to reproject LAS files
def reproject(las, source_crs):
    target_crs = pyproj.CRS('EPSG:6350')
    transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)
    xyz = transformer.transform(las.x, las.y, las.z)
    las.x, las.y, las.z = xyz
    las.header.add_crs(target_crs)

def decompress(fn, state_dir, county, tile_IDs, county_las_dir):
    for ID in tile_IDs:
        if fn.endswith(f'_{ID}.laz'):
            name = fn.replace('.laz', '.las')
            path = f'{county_las_dir}{county}_{name}'
            if not os.path.exists(path):
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        # Read the LAZ file
                        print(f"Reading {fn}...")
                        laz = laspy.read(f'{state_dir}{fn}')
                        las = laspy.convert(laz)
                        
                        # Get source CRS and reproject if necessary
                        source_crs = get_source_crs(fn)
                        if source_crs != pyproj.CRS("EPSG:6350"):
                            reproject(las, source_crs)
                        
                        # Write directly to gcsfuse mount
                        print(f"Writing to {path}...")
                        las.write(path)
                        
                        print(f"Successfully processed {fn}")
                        break  # Success, exit retry loop
                            
                    except InterruptedError as e:
                        retry_count += 1
                        if retry_count == max_retries:
                            print(f"Failed to process {fn} after {max_retries} attempts due to interrupted system call")
                            print(f"Error details: {str(e)}")
                        else:
                            print(f"Retry {retry_count}/{max_retries} for {fn}")
                            print(f"Waiting 5 seconds before retry...")
                            time.sleep(5)  # Increased delay to 5 seconds
                    except IOError as e:
                        retry_count += 1
                        if retry_count == max_retries:
                            print(f"Failed to process {fn} after {max_retries} attempts: {str(e)}")
                            print(f"Error details: {str(e)}")
                        else:
                            print(f"Retry {retry_count}/{max_retries} for {fn}")
                            print(f"Waiting 5 seconds before retry...")
                            time.sleep(5)  # Increased delay to 5 seconds
                    except Exception as e:
                        print(f"Unexpected error processing {fn}: {str(e)}")
                        print(f"Error type: {type(e).__name__}")
                        print(f"Error details: {str(e)}")
                        break  # Don't retry for unexpected errors

def process_county(county):
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

    # Create county directory and subdirectories for storing files
    dir = f'{LIDAR_DIR}/{state}/'
    county_dir = f'{dir}{county}/las'
    os.makedirs(f'{dir}{county}', exist_ok=True)
    os.makedirs(f'{dir}{county}/las', exist_ok=True)
    os.makedirs(f'{dir}{county}/dsm', exist_ok=True)
    os.makedirs(f'{dir}{county}/dtm', exist_ok=True)
    os.makedirs(f'{dir}{county}/chm', exist_ok=True)

    # Iterate through the state laz bucket and decompress to las, reprojecting if necessary
    start_time = time.time()

    # Process files
    num_processes = 16
    print(f"Decompressing tiles from {county} county...")
    with Pool(num_processes) as pool:
        pool.map(partial(decompress, state_dir=dir, county=county, tile_IDs=tile_IDs, county_las_dir=county_dir), os.listdir(dir))

    # Print results and elapsed time
    print(f'Successfully converted {len(os.listdir(county_dir))} LAS files for {county} county.')
    print(f'Successfully converted {len(set(os.listdir(county_dir)))} unique LAS files for {county} county.')
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Elapsed time: {elapsed_time} mins')

    # Check to ensure list of tile IDs is identical to list of decompressed files,
    # and print any exceptions
    def extract_ID(county_dir):
        decompressed_IDs = []
        for fn in os.listdir(county_dir):
            last_underscore_index = fn.rfind("_")
            start_index = last_underscore_index + 1
            end_index = fn.rfind(".")
            tile_ID = fn[start_index:end_index]
            decompressed_IDs.append(tile_ID)
        return set(decompressed_IDs)

    decompressed_IDs = extract_ID(county_dir)
    tile_IDs = set(tile_IDs)

    unique_to_IDs = tile_IDs - decompressed_IDs
    unique_to_decompressed = decompressed_IDs - tile_IDs

    print(f'Only in tile IDs: {unique_to_IDs}')
    print(f'Only in decompressed bucket: {unique_to_decompressed}')

if __name__ == '__main__':
    state = 'wv'
    counties = WV_COUNTIES
    start_time = time.time()

    # Iterate over each county in list
    for county in counties:
        process_county(county)

    print('All counties complete.')
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')