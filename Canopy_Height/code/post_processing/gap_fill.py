'''
Interpolates small gaps in rasters, typically from water features.
'''

import os
import subprocess
whitebox_executable = os.path.abspath('whitebox-tools-master/target/release/whitebox_tools')

from Canopy_Height.code.ch_variables import (
    RASTERS,
    MAIN_DIR
)

# Specify state and counties that need gap filling
state = 'wv'
counties = []

if state == 'ky' or state == 'tn':
    suffix = 'meters'
else:
    suffix = '3857'

for county in counties:
    county_dir = f"{MAIN_DIR}/{state}/{county}"
    for raster in RASTERS:
        fill_gaps = [
            whitebox_executable,
            '--run="FillMissingData"',
            f'--i="{county_dir}/{raster[0]}/{county}_{raster[1]}_{suffix}.tif"', 
            f'--output="{county_dir}/{raster[0]}/{county}_FINAL_{raster[1]}.tif"', 
            '--filter=50', 
            '--weight=3.0', 
            '--no_edges=True',
        ]

        print(f"Filling gaps in {raster[0]} ...")
        process = subprocess.run(fill_gaps)
        print(f"Gaps in {raster[0]} filled.")