import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Point
import os
import networkx as nx
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

input_shp = outputs+"unreclaimed_skeletons.shp"
output_shp = outputs+"unreclaimed_branches.shp"

gdf = gpd.read_file(input_shp)

def geometry_to_graph(geom):
    """
    Convert a LineString or MultiLineString geometry to a NetworkX graph.
    """
    if not isinstance(geom, (LineString, MultiLineString)):
        return None
        
    G = nx.Graph()
    
    # Add all line segments to the graph
    if isinstance(geom, LineString):
        coords = list(geom.coords)
        for i in range(len(coords)-1):
            G.add_edge(coords[i], coords[i+1])
    else:  # MultiLineString
        for line in geom.geoms:
            coords = list(line.coords)
            for i in range(len(coords)-1):
                G.add_edge(coords[i], coords[i+1])
    
    return G

def split_at_junctions(geom, G=None):
    """Split a MultiLineString at junction points where degree > 2"""
    if not isinstance(geom, (LineString, MultiLineString)):
        return None
        
    # Use existing graph if provided, otherwise create new one
    if G is None:
        G = geometry_to_graph(geom)
    
    # Find junction points (nodes with degree > 2)
    junctions = [node for node, degree in G.degree() if degree > 2]
    
    # If no junctions found, return the original geometry segments
    if not junctions:
        if isinstance(geom, LineString):
            return [geom]
        return list(geom.geoms)
    
    # Get all nodes with degree 1 (endpoints)
    endpoints = [node for node, degree in G.degree() if degree == 1]
    
    # Get all significant points (endpoints and junctions)
    significant_points = endpoints + junctions
    
    # Find all paths between pairs of significant points that are directly connected
    branches = []
    for i in range(len(significant_points)):
        for j in range(i + 1, len(significant_points)):
            start = significant_points[i]
            end = significant_points[j]
            try:
                # Find all simple paths between the points
                for path in nx.all_simple_paths(G, start, end):
                    # Check if the path goes through any other junction points
                    intermediate_junctions = [p for p in path[1:-1] if p in junctions]
                    
                    # If the path is direct (no intermediate junctions), add it
                    if not intermediate_junctions:
                        branches.append(LineString(path))
            except nx.NetworkXNoPath:
                continue
    
    return branches

# Create graphs for all geometries and find branched ones
graphs = {idx: geometry_to_graph(geom) for idx, geom in enumerate(gdf.geometry)}
branched_mask = [G is not None and any(degree > 2 for node, degree in G.degree()) for G in graphs.values()]
branched_gdf = gdf[branched_mask].copy()
print(f"Found {len(branched_gdf)} branched skeletons out of {len(gdf)} total")

# Split each branched skeleton at junctions and create new rows
exploded_rows = []
for idx, row in branched_gdf.iterrows():
    branches = split_at_junctions(row.geometry, graphs[idx])
    if branches:
        for branch in branches:
            new_row = row.copy()
            new_row.geometry = branch
            exploded_rows.append(new_row)

# Create new GeoDataFrame with the exploded branches
exploded_gdf = gpd.GeoDataFrame(exploded_rows, crs=branched_gdf.crs)
print(f"Created {len(exploded_gdf)} individual branches")

# Save the exploded branches
exploded_gdf.to_file(output_shp)
print(f"Saved exploded branches to {output_shp}")

