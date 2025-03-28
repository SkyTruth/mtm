# Import necessary modules
import os
import laspy
from multiprocessing import Pool
import subprocess
from osgeo import gdal, ogr, osr
import pyproj
from pyproj import CRS, Proj, transform

state = 'wv'
county = 'putnam'
tile_IDs = ['17SMC20005100', '17SMC20005250', '17SMC20005400', '17SMC20005850', '17SMC18505850', '17SMC17005850', '17SMC17006000', '17SMC17006150', '17SMC15506150', '17SMC14006150', '17SMC12506150', '17SMC11006150', '17SMC11006450', '17SMC09506450', '17SMC06506600', '17SMC08006600', '17SMC08006750', '17SMC08006900', '17SMC08007200', '17SMC08007350', '17SMC08007500', '17SMC09507500', '17SMC09507350', '17SMC11007500']
rasters = [['dsm', 'dsm_mosaic'], ['dtm', 'dtm_mosaic'], ['chm', 'chm']]

# Define function to assign source CRS based on lidar project (for WV tiles only)
if state == 'wv':
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

# Decompress tiles, reprojecting if necessary
dir = f'/home/alanal/gcs/lidar_data/{state}/'
def decompress(fn, source_crs):
        for ID in tile_IDs:
                if fn.endswith(f'_{ID}.laz'):
                        name = fn.replace('.laz', '.las')
                        path = f'{dir}{county}/las/{county}_{name}'
                        if not os.path.exists(path):
                            laz = laspy.read(f'{dir}{fn}')
                            las = laspy.convert(laz)
                            if state == 'wv':
                                if source_crs != pyproj.CRS("EPSG:6350"):
                                    reproject(las, source_crs)
                            las.write(path)

# Parallelize over 16 CPU cores
print('Decompressing tiles...')
num_processes = 16
if state == 'wv':
    with Pool(num_processes) as pool:
            pool.starmap(decompress, [(filename, get_source_crs(filename)) for filename in os.listdir(dir)])
else:
     with Pool(num_processes) as pool:
        pool.map(decompress, os.listdir(dir))

print('All tiles decompressed.')

# Assign source CRS based on state
if state == 'tn':
    source_crs = 'EPSG:6576'
elif state == 'va':
    source_crs = 'EPSG:6346'
elif state == 'ky':
    source_crs = 'EPSG:3089'
elif state == 'wv':
    source_crs = 'EPSG:6350'

# Assign resolution based on state
if state == 'tn' or state == 'ky':
    res = 32.8084
else:
    res = 10

whitebox_executable = os.path.abspath('whitebox-tools-master/target/release/whitebox_tools')

dir = f"/home/alanal/gcs/lidar_data/{state}/{county}/"

os.makedirs(f'{dir}hole_dsms', exist_ok=True)
os.makedirs(f'{dir}hole_dtms', exist_ok=True)

def dsm_dtm(fn):
        for ID in tile_IDs:
                if fn.endswith(f'_{ID}.las'):
                    outfile = fn.replace(".las", ".tif")
                    # Create DSM using all surface points.
                    dsm = [
                        whitebox_executable,
                        '--run="lidar_digital_surface_model"',
                        f'--i="{dir}las/{fn}"',
                        f'--o="{dir}hole_dsms/{outfile}"',
                        f'--resolution={res}',
                        '--radius=0.5'
                    ]
                    process = subprocess.run(dsm)
                    
                    # Create DTM using all ground points
                    dtm = [
                        whitebox_executable,
                        '--run="lidar_tin_gridding"',
                        f'--i="{dir}las/{fn}"',
                        f'--o="{dir}hole_dtms/{outfile}"',
                        '--parameter="elevation"',
                        '--returns="all"',
                        f'--resolution={res}',
                        '--exclude_cls="0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"'
                    ]
                    process = subprocess.run(dtm)

print(f"Creating DSMs and DTMs...")
num_processes = 16
with Pool(num_processes) as pool:
        pool.map(dsm_dtm, os.listdir(f'{dir}las/'))
print("DSMs and DTMs created successfully.")

# Mosaic all DSMs into one continuous surface model
mosaic_dsm = [
    whitebox_executable,
    '--run="mosaic"',
    f'--wd="{dir}hole_dsms"',
    f'--output="{dir}dsm/{county}_holes_dsm_mosaic.tif"'
]

print(f"Mosaicking DSMs...")
process = subprocess.run(mosaic_dsm)
print(f"DSM mosaic created successfully.")

# Mosaic all DTMs into one continous terrain model
mosaic_dtm = [
    whitebox_executable,
    '--run="mosaic"',
    f'--wd="{dir}hole_dtms"',
    f'--output="{dir}dtm/{county}_holes_dtm_mosaic.tif"'
]

print(f"Mosaicking DTMs...")
process = subprocess.run(mosaic_dtm)
print(f"DTM mosaic created successfully.")
    
# Subtract DTM from DSM to get Canopy Height Model (CHM)
subtract = [
    whitebox_executable,
    '--run="subtract"',
    f'--input1="{dir}dsm/{county}_holes_dsm_mosaic.tif"',
    f'--input2="{dir}dtm/{county}_holes_dtm_mosaic.tif"',
    f'--output="{dir}chm/{county}_holes_chm.tif"'
]

print(f"Creating CHM...")
process = subprocess.run(subtract)
print(f"CHM created successfully.")

# Reproject holes CHM, DSM, and DTM to 3857
for raster in rasters:
    print(f"Reprojecting {raster[0]}...")
    gdal.Warp(destNameOrDestDS=f"{dir}{raster[0]}/{county}_holes_{raster[1]}_3857.tif", srcDSOrSrcDSTab=f"{dir}{raster[0]}/{county}_holes_{raster[1]}.tif",
                    options=f"-overwrite -s_srs {source_crs} -t_srs EPSG:3857 -tr 10.0 10.0 -r near -of GTiff")
    print(f"{raster[0]} reprojected.")

for raster in rasters:
    # For Kentucky and Tennessee: must convert feet to meters for all 3 data products
    suffix = '3857'
    if state == 'ky' or state == 'tn':
        convert = [
            whitebox_executable,
            '--run="multiply"',
            f'--input1="{dir}{raster[0]}/{county}_holes_{raster[1]}_3857.tif"',
            '--input2=0.3048',
            f'--output="{dir}{raster[0]}/{county}_holes_{raster[1]}_meters.tif"'
        ]
        print(f"Converting {raster[0]} to meters...")
        process = subprocess.run(convert)
        print(f"{raster[0]} converted to meters.")
        suffix = 'meters'

    # Mosaic the holes into the original raster
    patch_holes = [
        whitebox_executable,
        '--run="mosaic"',
        f'--inputs="{dir}{raster[0]}/{county}_{raster[1]}_{suffix}.tif", "{dir}{raster[0]}/{county}_holes_{raster[1]}_{suffix}.tif"',
        f'--output="{dir}{raster[0]}/{county}_patched_{raster[1]}_{suffix}.tif"',
        '--method="nn"'
    ]
    print(f"Patching holes in {raster[0]}...")
    process = subprocess.run(patch_holes)
    print(f"Holes in {raster[0]} patched.")

    # Interpolate any remaining gaps, including bodies of water
    fill_gaps = [
        whitebox_executable,
        '--run="FillMissingData"',
        f'--i="{dir}{raster[0]}/{county}_patched_{raster[1]}_{suffix}.tif"', 
        f'--output="{dir}{raster[0]}/{county}_FINAL_{raster[1]}.tif"', 
        '--filter=25', 
        '--weight=3.0', 
        '--no_edges=True',
    ]

    print(f"Filling gaps in {raster[0]} ...")
    process = subprocess.run(fill_gaps)
    print(f"Gaps in {raster[0]} filled.")