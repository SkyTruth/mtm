# Initialize Google Cloud Storage client
from google.cloud import storage
project_id = 'skytruth-tech'
client = storage.Client(project=project_id)

# Access bucket
bucket_name = 'mountaintop_mining'
bucket = client.get_bucket(bucket_name)

# List all counties to decompress
state = 'wv'

counties = [
'boone',
'cabell',
'clay',
'fayette',
'greenbrier',
'kanawha',
'lincoln',
'logan',
'mason',
'mcdowell',
'mercer'
'mingo',
'nicholas',
'pocahontas',
'putnam',
'raleigh',
'summers',
'wayne',
'webster',
'wyoming'
]

# Import necessary modules
import os
import laspy
from multiprocessing import Pool
import pandas as pd
import time
import pyproj
from pyproj import CRS, Proj, transform

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

# Iterate over each county in list
for county in counties:

        # Get list of tile IDs from county
        df = pd.read_csv(f'/home/alanal/gcs/lidar_data/tile_IDs/{county}.csv', header=0)
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
        dir = f'/home/alanal/gcs/lidar_data/{state}/'
        county_dir = f'{dir}{county}/las'
        os.makedirs(f'{dir}{county}', exist_ok=True)
        os.makedirs(f'{dir}{county}/las', exist_ok=True)
        os.makedirs(f'{dir}{county}/dsm', exist_ok=True)
        os.makedirs(f'{dir}{county}/dtm', exist_ok=True)
        os.makedirs(f'{dir}{county}/chm', exist_ok=True)

        # Iterate through the state laz bucket and decompress to las, reprojecting if necessary
        start_time = time.time()

        def decompress(fn, source_crs):
                for ID in tile_IDs:
                        if fn.endswith(f'{ID}.laz'):
                                name = fn.replace('.laz', '.las')
                                path = f'{dir}{county}/las/{county}_{name}'
                                if not os.path.exists(path):
                                        laz = laspy.read(f'{dir}{fn}')
                                        las = laspy.convert(laz)
                                        # Reproject LAS file if not already in EPSG 6350
                                        if source_crs != pyproj.CRS("EPSG:6350"):
                                            reproject(las, source_crs)
                                        las.write(path)

        # Parallelize over 16 CPU cores
        num_processes = 16
        print(f"Decompressing tiles from {county} county...")
        with Pool(num_processes) as pool:
                pool.starmap(decompress, [(filename, get_source_crs(filename)) for filename in os.listdir(dir)])

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
                for fn in county_dir:
                        last_underscore_index = fn.rfind("_")
                        start_index = last_underscore_index + 1
                        end_index = fn.rfind(".")
                        tile_ID = fn[start_index:end_index]
                        decompressed_IDs.append(tile_ID)
                return set(decompressed_IDs)

        decompressed_IDs = extract_ID(os.listdir(county_dir))
        tile_IDs = set(tile_IDs)

        unique_to_IDs = tile_IDs - decompressed_IDs
        unique_to_decompressed = decompressed_IDs - tile_IDs

        print(f'Only in tile IDs: {unique_to_IDs}')
        print(f'Only in decompressed bucket: {unique_to_decompressed}')

print('All counties complete.')
current_time = time.time()
elapsed_time = (current_time - start_time) // 60
print(f'Total elapsed time: {elapsed_time} mins')