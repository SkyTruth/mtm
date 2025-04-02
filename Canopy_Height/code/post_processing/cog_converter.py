import subprocess
import os
from osgeo import gdal

# Create progress callback
def progress_callback(complete, message, unknown):
    print(f'Progress: {complete * 100:.2f}% - {message}')

# Paths to input and output files
input_tif = '/home/alanal/gcs/lidar_data/final_mosaics/complete_dtm_gap_filled_3857.tif'
output_tif = '/home/alanal/gcs/lidar_data/final_mosaics/complete_dtm_gap_filled_3857_cog.tif'

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