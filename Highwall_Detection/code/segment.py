'''
Splits centerline branches into segments of approximately 100m, with no segment shorter than 50m.
'''

import geopandas as gpd
import os
from shapely.geometry import LineString
import numpy as np

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Working directories
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define directory root
root = os.path.dirname(os.path.abspath(__file__))

# Set up input, temp, and output directories
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
#  Setup
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define input and output paths
input_shp = inputs+"centerline_branches.shp"
output_shp = outputs+"centerline_segments.shp"

# Set variables
target_segment_length = 100
max_segment_length = 150
min_segment_length = 50 

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Processing
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def split_line(line, target_segment_length=target_segment_length, max_segment_length=max_segment_length, min_segment_length=min_segment_length):
    """
    Split a LineString into segments of approximately target_segment_length,
    ensuring no segment is shorter than min_segment_length.
    """
    total_length = line.length
    # If line is shorter than max_segment_length, return it as is
    if total_length <= max_segment_length:
        return [line]
    # Calculate number of segments needed
    n_segments = int(np.ceil(total_length / target_segment_length))
    # Check if last segment would be too short
    remainder = total_length % target_segment_length
    if remainder < min_segment_length and n_segments > 1:
        n_segments -= 1
    # Calculate actual segment length
    segment_length = total_length / n_segments
    # Create segments
    segments = []
    coords = list(line.coords)
    current_length = 0
    segment_coords = [coords[0]]  # Start with first point
    for i in range(1, len(coords)):
        # Add length of current line segment
        segment = LineString([coords[i-1], coords[i]])
        current_length += segment.length
        if current_length < segment_length:
            # Keep adding points to current segment
            segment_coords.append(coords[i])
        else:
            # Add the last point and create the segment
            segment_coords.append(coords[i])
            segments.append(LineString(segment_coords))
            # Start new segment from this point
            segment_coords = [coords[i]]
            current_length = 0
    # Add any remaining coordinates as the final segment
    if len(segment_coords) >= 2:
        segments.append(LineString(segment_coords))
    return segments


def segment_lines():
    # Read input shapefile of centerline branches
    gdf = gpd.read_file(input_shp)
    # Initialize list to store centerline segment features
    centerline_segment_features = []
    # Process each centerline branch
    for _, row in gdf.iterrows():
        segments = split_line(row.geometry)
        # Add each segment to list of features
        for segment in segments:
            centerline_segment_features.append({
                'id': row['id'],
                'geometry': segment,
                'length': segment.length
            })
    # Create new GeoDataFrame
    segments_gdf = gpd.GeoDataFrame(centerline_segment_features, crs=gdf.crs)
    # Save to file
    segments_gdf.to_file(output_shp)
    print(f"Processed {len(gdf)} features into {len(segments_gdf)} segments")

if __name__ == "__main__":
    segment_lines()
