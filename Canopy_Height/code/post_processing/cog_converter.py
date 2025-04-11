'''
Converts a raster into a Cloud Optimized GeoTIFF so that it can be imported as an Earth Engine asset.
'''

import os
import subprocess
from osgeo import gdal

from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCS_MOUNT,
    FINAL_MOSAICS_DIR
)

# Mount GCS bucket
os.makedirs(GCS_MOUNT, exist_ok=True)
subprocess.run(['gcsfuse', '--implicit-dirs', GCLOUD_BUCKET, GCS_MOUNT])

# Create progress callback
def progress_callback(complete, message, unknown):
    print(f'Progress: {complete * 100:.2f}% - {message}')

# Paths to input and output files
input_tif = f'{FINAL_MOSAICS_DIR}/complete_dtm_gap_filled_3857.tif'
output_tif = f'{FINAL_MOSAICS_DIR}/complete_dtm_gap_filled_3857_cog.tif'

# Convert to Cloud Optimized GeoTIFF using gdal_translate
gdal.Translate(
    output_tif,
    input_tif,
    creationOptions=['TILED=YES', 'COMPRESS=LZW', 'COPY_SRC_OVERVIEWS=YES', 'BIGTIFF=YES'],
    callback=progress_callback
)

'''
subprocess.run([
    'gdal_translate', input_tif, output_tif,
    '-co', 'TILED=YES',
    '-co', 'COPY_SRC_OVERVIEWS=YES',
    '-co', 'COMPRESS=LZW'
])
'''