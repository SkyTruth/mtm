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

2. annualThresholdImages.py.py --> creates annual threshold images and exports them to GCS.
```shell
poetry run python MTM_Annual_Extent/code/annualThresholdImages.py.py
```

3. annualMiningArea.py --> creates annual mining footprint rasters and exports them to GCS.
```shell
poetry run python MTM_Annual_Extent/code/annualMiningArea.py
```

4. annualMiningArea_vectorCreation.py --> creates annual mining footprint vectorss and exports them to GCS.
```shell
poetry run python MTM_Annual_Extent/code/annualMiningArea_vectorCreation.py
```

5. data_cleanup.py --> Cleans up footprint data, removes provisional data from final GCS directory if the data is no longer provisional.
```shell
poetry run python MTM_Annual_Extent/code/data_cleanup.py
```