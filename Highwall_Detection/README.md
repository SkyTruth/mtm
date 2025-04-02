# Note
All code should be run from the `mtm/` directory

# Highwall Skeletonization Steps
1. get_skeletons.py --> reduces highwall geometries into skeleton lines, split at their junctions into branches
```shell
poetry run python Highwall_Detection/code/get_skeletons.py
```
2. segment.py --> splits skeletons into segments of approximately 100m
```shell
poetry run python Highwall_Detection/code/segment.py
```