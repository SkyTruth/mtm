# Using LiDAR Data to Model Canopy Height in Central Appalachia
The goal of this project was to create a wall-to-wall 10m canopy height model (CHM) for 73 counties in Central Appalachia by processing high-resolution aerial LiDAR point cloud data collected between 2015 and 2023. As byproducts of this process, I also created a digital terrain model (DTM) and digital surface model (DSM) of the study region. Canopy height is a useful metric of vegetation loss and recovery in mined areas, as well as an accurate proxy for above-ground biomass.

## Code
The code in this repository is not yet ready to be replicated by other users. The scraper scripts were run in Colab, while the remainder of the scripts were run in a VM (e2-highmem-16, 128 GB, 16 CPU cores) that was built specifically for this project. All required packages and their versions are contained in req.txt and installed in a virtual environment in this VM. The exceptions are gcsfuse and whitebox, both of which were built from source code. The script mount.py uses gcsfuse to mount the GCS bucket to the VM directory, allowing the user to work directly with files in the bucket as if they exist locally in the directory.

[Read the full report and documentation here.](https://docs.google.com/document/d/1bMBGrUBo6LNwxNrPXTVW6mD1SCKbbWqQ_B9PEYEKGdk/edit?usp=sharing)

### Scripts in order of use
1. scraper.ipynb --> Uses a list of tile IDs to scrape the corresponding LAZ files from the USGS database into a GCS bucket.
2. scraper_ky.ipynb --> Uses a list of tile IDs to scrape the corresponding LAZ files from Kentucky’s LiDAR database into a GCS bucket.
3. req.txt --> Contains all packages to install to the virtual environment, with the exception of whitebox and gcsfuse.
4. mount.py --> Mounts the mountaintop_mining bucket as a directory in the VM.
5. decompress.py --> Decompresses LAZ files into LAS files by county, iterating through a list of counties.
6. decompress_reproject.py --> Decompresses LAZ files into LAS files by county, iterating through a list of counties. Additionally reprojects all LAS files to EPSG:6350. Used for West Virginia counties.
7. process_chm.py --> Produces a mosaicked CHM, DTM, and DSM for each county from the county’s set of LAS files, iterating through a list of counties. Reprojects all rasters to EPSG:3857.
8. hole_patch.py --> Fills holes from missing tiles in county rasters by re-processing those tiles and mosaicking them into the original raster. Additionally interpolates any remaining small gaps. Requires identifying and listing the missing tiles using a tile index.
9. gap_fill.py --> Interpolates small gaps in rasters, typically from water features.
10. point_density.py --> Takes a random sample of 50 LAZ tiles from a LiDAR project and calculates the average point density.
11. cog_converter.py --> Converts a raster into a Cloud Optimized GeoTIFF so that it can be imported as an Earth Engine asset.
