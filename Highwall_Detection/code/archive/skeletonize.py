# Import tools from WBT module
import os, sys
sys.path.insert(1, '/Users/alanalutz/Documents/SkyTruth')   # path points to WBT directory
from WBT.whitebox_tools import WhiteboxTools

# Declare a name for the tools
wbt = WhiteboxTools()

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Working directories
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define personal storage root
root = "/Users/alanalutz/Documents/SkyTruth/highwall_scripts"

# Set up input and output directories
inputs = root+"/inputs/"
temps = root+"/temps/" 
outputs = root+"/outputs/"

# Create directories if they do not already exist
if os.path.isdir(inputs) != True:
        os.mkdir(inputs)
if os.path.isdir(temps) != True:
        os.mkdir(temps)
if os.path.isdir(outputs) != True:
        os.mkdir(outputs)

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Analysis
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

input_polygons = inputs+'test_set.shp'

wbt.vector_polygons_to_raster(
    i=input_polygons, 
    output=temps+'raster.tif',
    field='ID',
    nodata=False, 
    cell_size=1
)

wbt.remove_spurs(
    i=temps+'raster.tif', 
    output=temps+'spurs_removed.tif', 
    iterations=100
)

wbt.line_thinning(
    i=temps+'spurs_removed.tif', 
    output=temps+'thinned.tif'
)

wbt.raster_to_vector_lines(
    i=temps+'thinned.tif', 
    output=outputs+'vectors.shp'
)