import os
import subprocess

state = 'wv'
counties = [
'lincoln'
]

rasters = [['dsm', 'dsm_mosaic'], ['dtm', 'dtm_mosaic'], ['chm', 'chm']]
whitebox_executable = os.path.abspath('whitebox-tools-master/target/release/whitebox_tools')

if state == 'ky' or state == 'tn':
    suffix = 'meters'
else:
    suffix = '3857'

for county in counties:
    dir = f"/home/alanal/gcs/lidar_data/{state}/{county}/"
    for raster in rasters:
        fill_gaps = [
            whitebox_executable,
            '--run="FillMissingData"',
            f'--i="{dir}{raster[0]}/{county}_{raster[1]}_{suffix}.tif"', 
            f'--output="{dir}{raster[0]}/{county}_FINAL_{raster[1]}.tif"', 
            '--filter=50', 
            '--weight=3.0', 
            '--no_edges=True',
        ]

        print(f"Filling gaps in {raster[0]} ...")
        process = subprocess.run(fill_gaps)
        print(f"Gaps in {raster[0]} filled.")