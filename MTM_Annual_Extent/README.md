# Note
All code should be run from the `mtm/` directory

# Mask Creation Steps
1. mask_creation.py --> downloads USCB Tiger/Line data, processes it (buffer then rasterize), and uploads the raster to GCS
```shell
poetry run python MTM_Annual_Extent/code/mask_creation.py
```

# Annual Mine Footprint Detection
1. greenestComp.py --> creates annual greenest pixel composites and exports them to GCS.
```shell
poetry run python MTM_Annual_Extent/code/greenestComp.py
```