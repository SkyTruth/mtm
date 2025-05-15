# Note
All code should be run from the `mtm/` directory

# Highwall Skeletonization Steps
1. extract_centerlines.py --> Reduces highwall geometries into skeleton lines, split at their junctions into branches
```shell
poetry run python Highwall_Detection/code/extract_centerlines.py
```
2. segment.py --> Splits longer branches into segments of approximately 100m
```shell
poetry run python Highwall_Detection/code/segment.py
```