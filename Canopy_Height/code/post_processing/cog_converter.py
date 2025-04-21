'''
Converts a raster into a Cloud Optimized GeoTIFF so that it can be imported as an Earth Engine asset.
'''

from osgeo import gdal

from Canopy_Height.code.ch_variables import (
    FINAL_MOSAICS_DIR
)

# Specify which raster to convert (chm, dsm, or dtm)
raster = 'chm'

# Create progress callback
def progress_callback(complete, message):
    print(f'Progress: {complete * 100:.2f}% - {message}')

# Paths to input and output files
input_tif = f'{FINAL_MOSAICS_DIR}/complete_{raster}_gap_filled_3857.tif'
output_tif = f'{FINAL_MOSAICS_DIR}/complete_{raster}_gap_filled_3857_cog.tif'

# Convert to Cloud Optimized GeoTIFF using gdal_translate
gdal.Translate(
    output_tif,
    input_tif,
    creationOptions=['TILED=YES', 'COMPRESS=LZW', 'COPY_SRC_OVERVIEWS=YES', 'BIGTIFF=YES'],
    callback=progress_callback
)