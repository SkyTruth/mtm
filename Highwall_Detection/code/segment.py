'''
Splits skeletons into segments of approximately 100m, with no segment shorter than 50m.
Run this after get_skeletons.py.
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
#  Processing
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def split_line(line, target_length=100, min_length=50):
    """
    Split a LineString into segments of approximately target_length,
    ensuring no segment is shorter than min_length.
    """
    total_length = line.length
    
    # If line is shorter than 150m, return it as is
    if total_length <= 150:
        return [line]
    
    # Calculate number of segments needed
    n_segments = int(np.ceil(total_length / target_length))
    
    # Check if last segment would be too short
    remainder = total_length % target_length
    if remainder < min_length and n_segments > 1:
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
    # Define input and output paths
    input_shp = outputs+"unreclaimed_skeletons.shp"
    output_shp = outputs+"segmented_skeletons.shp"
    
    # Read input file
    gdf = gpd.read_file(input_shp)
    
    # Create new features list
    new_features = []
    
    # Process each line
    for _, row in gdf.iterrows():
        segments = split_line(row.geometry)
        
        # Add each segment to new features
        for segment in segments:
            new_features.append({
                'id': row['id'],
                'geometry': segment,
                'length': segment.length
            })
    
    # Create new GeoDataFrame
    new_gdf = gpd.GeoDataFrame(new_features, crs=gdf.crs)
    
    # Save to file
    new_gdf.to_file(output_shp)
    print(f"Processed {len(gdf)} features into {len(new_features)} segments")

if __name__ == "__main__":
    segment_lines()
