# Note
All code should be run from the `mtm/` directory

# Highwall Skeletonization
**centerline_segments.py** --> Reduces highwall geometries into centerlines, split at their junctions into individual branches. Divides longer branches into shorter segments.
```shell
poetry run python Highwall_Detection/code/centerline_segments.py
```
# Highwall Data
**highwalls_1m.shp** --> Full set of 1m highwall detection geometries for the MTM study region.

**testing_subset_highwalls.shp** --> Small subset of 1m highwall detection geometries for testing code with reduced processing time.