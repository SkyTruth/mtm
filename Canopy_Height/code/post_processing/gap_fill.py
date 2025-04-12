'''
Interpolates small gaps in rasters, typically from water features.
'''

import os
import whitebox
wbt = whitebox.WhiteboxTools()

from mtm_utils.variables import (
    LIDAR_DIR,
    WV_COUNTIES,
    TN_COUNTIES,
    KY_COUNTIES,
    VA_COUNTIES
)

state = 'tn'

if state == 'wv':
    counties = WV_COUNTIES
elif state == 'tn':
    counties = TN_COUNTIES
elif state == 'ky':
    counties = KY_COUNTIES
elif state == 'va':
    counties = VA_COUNTIES

rasters = [['dsm', 'dsm_mosaic'], ['dtm', 'dtm_mosaic'], ['chm', 'chm']]

if state == 'ky' or state == 'tn':
    suffix = 'meters'
else:
    suffix = '3857'

for county in counties:
    dir = os.path.abspath(f"{LIDAR_DIR}{state}/{county}/")
    for raster in rasters:

        print(f"Filling gaps in {raster[0]} ...")
        input_raster = f"{dir}/{raster[0]}/{county}_{raster[1]}_{suffix}.tif"
        wbt.fill_missing_data(
            i=input_raster,
            output=f"{dir}/{raster[0]}/{county}_FINAL_{raster[1]}.tif",
            filter=50,
            weight=3.0,
            no_edges=True
        )

        print(f"Gaps in {raster[0]} filled.")