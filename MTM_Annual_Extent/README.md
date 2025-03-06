# Note
All code should be run from the `mtm/` directory

# Mask Creation Steps
1. mask_creation.py --> downloads USCB Tiger/Line data, processes it (buffer then rasterize), and uploads the raster to GCS
```shell
poetry run python MTM_Annual_Extent/mask_creation.py
```