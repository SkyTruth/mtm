'''
Decompresses LAZ files into LAS files by county, iterating through a list of counties.
Used for Tennessee, Kentucky, and Virginia counties.
'''

import os
import laspy
from multiprocessing import Pool
import pandas as pd
import time
from functools import partial

from mtm_utils.variables import (
    LIDAR_DIR,
    TILE_IDS_DIR,
    TN_COUNTIES,
    KY_COUNTIES,
    VA_COUNTIES
)

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

    # Organize directories
    county_las_dir = f'{state_dir}test_{county}/las/'
    os.makedirs(county_las_dir, exist_ok=True)

    # Iterate through the state laz bucket and decompress to las
    start_time = time.time()

    # Process files
    num_processes = 1
    with Pool(num_processes) as pool:
        pool.map(partial(decompress, state_dir=state_dir, county=county, tile_IDs=tile_IDs, county_las_dir=county_las_dir), os.listdir(state_dir))

    # Print results and elapsed time
    print(f'Successfully converted {len(os.listdir(county_las_dir))} LAS files for {county} county.')
    print(f'Successfully converted {len(set(os.listdir(county_las_dir)))} unique LAS files for {county} county.')
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Elapsed time: {elapsed_time} mins')

    # Check to ensure list of tile IDs is identical to list of decompressed files,
    # and print any exceptions
    def extract_ID(county_las_dir):
        decompressed_IDs = []
        for fn in os.listdir(county_las_dir):
            last_underscore_index = fn.rfind("_")
            start_index = last_underscore_index + 1
            end_index = fn.rfind(".")
            tile_ID = fn[start_index:end_index]
            decompressed_IDs.append(tile_ID)
        return set(decompressed_IDs)

    decompressed_IDs = extract_ID(county_las_dir)
    tile_IDs = set(tile_IDs)

    unique_to_IDs = tile_IDs - decompressed_IDs
    unique_to_decompressed = decompressed_IDs - tile_IDs

    print(f'Only in tile IDs: {unique_to_IDs}')
    print(f'Only in decompressed bucket: {unique_to_decompressed}')

if __name__ == '__main__':
    # Select state
    state = 'tn'
    if state == 'tn':
        counties = TN_COUNTIES
    elif state == 'ky':
        counties = KY_COUNTIES
    elif state == 'va':
        counties = VA_COUNTIES

    # Set up state directory
    state_dir = f'{LIDAR_DIR}/{state}/'
    start_time = time.time()

    # Iterate over each county in list
    for county in counties:
        process_county(county)

    print('All counties complete.')
    current_time = time.time()
    elapsed_time = (current_time - start_time) // 60
    print(f'Total elapsed time: {elapsed_time} mins')