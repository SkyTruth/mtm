# Using LiDAR Data to Model Canopy Height in Central Appalachia
This project creates a wall-to-wall 10m canopy height model (CHM) for 73 counties in Central Appalachia using high-resolution aerial LiDAR point cloud data collected between 2015 and 2023 and made available through the USGS 3D Elevation Program (3DEP). Canopy height is a useful metric of post-mining ecological performance, and this data can facilitate improved reclamation monitoring efforts and management strategies.

[Read the full report here.](https://docs.google.com/document/d/1bMBGrUBo6LNwxNrPXTVW6mD1SCKbbWqQ_B9PEYEKGdk/edit?usp=sharing)

## Note
Due to the large data volume and processing requirements for creating a CHM across 73 counties, this code was developed and tested in specialized computational environments (detailed below) separate from the poetry-managed environment used for the rest of the MTM repository.

## Scraping LAZ Files
The scraper scripts are Jupyter notebooks that are intended to be run in Google Colab for compatibility with GCS. The tile ID files used in these scripts can be found in Canopy_Height/data/. Each tile ID file consists of a list of the subset of tile IDs in a lidar acquisition project that intersect the study region.

1. scraper.ipynb --> Uses a list of tile IDs to scrape the corresponding LAZ files from the USGS database into a GCS bucket. Used for Tennessee, West Virginia, and Virginia lidar acquisition projects.
2. scraper_ky.ipynb --> Uses a list of tile IDs to scrape the corresponding LAZ files from Kentucky’s LiDAR database into a GCS bucket.

## CHM Processing and Post-Processing
The remainder of the code was developed and tested in the following virtual machine setup:

### VM Environment Details

- **Platform:** Google Cloud Compute Engine
- **Distribution:** Debian GNU/Linux 12 (Bookworm)
- **Architecture:** amd64 (x86_64)
- **Machine Type:** e2-highmem-16
- **vCPUs:** 16
- **RAM:** 128 GB
- **Disk Space:** 50 GB
- **Python Version:** 3.11

### Virtual Environment
All required packages and their versions (with the exception of gcsfuse and whitebox) are contained in req.txt and installed in a virtual environment.
```shell
sudo apt install python3.11-venv
python3 -m venv env
source env/bin/activate
pip install -r req.txt
```

### Setting up gcsfuse and mounting GCS bucket
Gcsfuse is used to mount a GCS bucket to the VM directory, allowing the user to work directly with files in the bucket as if they exist locally in the directory.

1. Download gcsfuse v2.0.0 [here.](https://github.com/GoogleCloudPlatform/gcsfuse/releases/tag/v2.0.0)
2. Install fuse and the gcsfuse package to the VM.
```shell
sudo apt-get update
sudo apt-get install fuse
sudo dpkg -i gcsfuse_2.0.0_amd64.deb
```
3. Use mount.py to mount the GCS bucket as a directory in the VM.
```shell
python3 Canopy_Height/code/mount.py
```

### Setting up WhiteboxTools
WhiteboxTools is a set of open-source geospatial tools (including LiDAR tools) that can be integrated directly into Python scripts.
[Follow these instructions to build WhiteboxTools from source code.](https://www.whiteboxgeo.com/manual/wbt_book/install.html#building-whiteboxtools-from-source-code)


### Scripts in order of use
To avoid memory limitations, tiles must be processed from one county at a time. Lists of tile IDs for each county can be found in Canopy_Height/data/.

1. decompress.py --> Decompresses LAZ files into LAS files by county.
```shell
python3 Canopy_Height/code/processing/decompress.py
```
2. process_chm.py --> Produces a mosaicked CHM, DTM, and DSM for each county from the county’s set of LAS files.
```shell
python3 Canopy_Height/code/processing/process_chm.py
```

Manually inspect the output rasters for each county for gaps and missing tiles. Use hole_patch.py and gap_fill.py as needed for post-processing.

3. hole_patch.py --> Fills holes from missing tiles in a county's rasters by re-processing those tiles and mosaicking them into the original raster. Additionally interpolates any remaining small gaps. Requires manually inspecting a raster and listing the missing tiles.
```shell
python3 Canopy_Height/code/post_processing/hole_patch.py
```
4. gap_fill.py --> Interpolates small gaps in rasters, typically from water features.
```shell
python3 Canopy_Height/code/post_processing/gap_fill.py
```

At this stage, clip each county raster to its border to eliminate overlapping data between counties and mosaic them into region-wide rasters in QGIS, then re-upload to the FINAL_MOSACS_DIR in GCS. gap_fill.py may be used again to interpolate any single-pixel gaps between counties resulting from raster misalignment.

5. cog_converter.py --> Converts a raster into a Cloud Optimized GeoTIFF so that it can be imported as an Earth Engine asset.
```shell
python3 Canopy_Height/code/post_processing/cog_converter.py
```

The CHM does not perform well on water features and does not differentiate between vegetation and built structures, so the final product is optionally masked with a water / urban mask layer from the US Census Bureau. This mask is an unbuffered version of the mask used for the MTM detection model.

6. point_density.py --> Takes a random sample of 50 LAZ tiles from a LiDAR project and calculates the average point density.
```shell
python3 Canopy_Height/code/post_processing/point_density.py
```