'''
A version where I attempted to simplify the process by removing the spine extraction.
The idea was that if we can just prune all the short spurs, then that does basically
the same thing as extracting the spines. Not working yet and actually seems to be
running slower? But could still be a useful approach.

The code runs but the output is really broken up.
'''

import centerline.geometry as cl
import geopandas as gpd
import os
import networkx as nx
from shapely.geometry import LineString, Polygon, MultiPolygon
import time

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

# Define paths to input highwall polygons and final output centerlines
input_shp = inputs+"unreclaimed_uncleaned.shp"
output_shp = outputs+"unreclaimed_skeletons.shp"

# Variables
interp_distance = 2
min_spur_length = 10
min_branch_length = 10

def clean_highwalls(gdf):
    """
    Reprojects, removes small holes, and buffers highwall polygons to maintain 8-connectivity.
    """
    # Reproject to EPSG:32617
    repro_gdf = gdf.to_crs(epsg=32617)

    def remove_holes(geom, min_area=100):
        if isinstance(geom, Polygon):
            if geom.interiors:
                new_interiors = [
                    ring for ring in geom.interiors 
                    if Polygon(ring).area >= min_area
                ]
                return Polygon(geom.exterior, new_interiors)
            return geom
        # Handle MultiPolygon case
        elif isinstance(geom, MultiPolygon):
            return MultiPolygon([remove_holes(poly, min_area) for poly in geom.geoms])
        return geom

    # Apply the hole removal function to each geometry
    repro_gdf["geometry"] = repro_gdf["geometry"].apply(remove_holes)
    
    # Buffer to maintain 8-connectivity
    repro_gdf["geometry"] = repro_gdf["geometry"].buffer(1.0)
    
    print(f'{len(repro_gdf)} highwalls cleaned.')
    return repro_gdf


def get_centerlines(row):
    """
    Extracts (messy) centerlines from a highwall polygon.
    """
    try:
        poly = row.geometry

        try:
            c_line = cl.Centerline(poly,
                                interpolation_distance=interp_distance,
                                interpolation_options={'qhull_options': 'QJ Qbb'})
        except:
            try: # If that fails, try with a smaller interpolation distance
                c_line = cl.Centerline(poly,
                                    interpolation_distance=max(0.5,interp_distance/2),
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB'})
            except: # If that still fails, try with minimum settings
                c_line = cl.Centerline(poly,
                                    interpolation_distance=0.5,
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB Qs'})
        print(f'Centerline extracted for polygon {row["ID"]}')
        return c_line
        
    except Exception as e:
        print(f"Warning: Could not process polygon with ID {row['ID']}: {str(e)}")
        return None

def build_graph_from_centerline(cl):
    """
    Converts a centerline to a networkx graph with edge weights based on length.
    """
    graph = nx.Graph()
    
    # Build initial graph from centerline
    for linestring in cl.geometry.geoms:
        coords = list(linestring.coords)
        for i in range(len(coords) - 1):
            # Add edge with length as weight
            length = LineString([coords[i], coords[i+1]]).length
            graph.add_edge(coords[i], coords[i+1], weight=length)
    
    print(f'Graph built from centerline.')
    return graph

def remove_short_spurs(graph, min_length):
    """
    Removes spurs (paths from endpoint to junction) shorter than min_length
    """
    # Find and remove short spurs
    endpoints = [node for node, degree in graph.degree() if degree == 1]
    edges_to_remove = set()
    
    # Check each endpoint
    for endpoint in endpoints:
        current = endpoint
        path = [current]
        path_length = 0
        
        # Follow the path from the endpoint until we hit a junction or another endpoint
        while True:
            neighbors = list(graph.neighbors(current))
            if len(neighbors) == 0:  # Dead end
                break
            elif len(neighbors) > 2:  # Junction
                # Mark short spurs for removal
                if path_length < min_length:
                    for i in range(len(path)-1):
                        edges_to_remove.add((path[i], path[i+1]))
                        edges_to_remove.add((path[i+1], path[i]))
                break
            elif len(neighbors) == 1 and current != endpoint:  # Another endpoint
                break
            else:  # Regular point with 2 neighbors or starting point
                next_point = neighbors[0] if neighbors[0] not in path else neighbors[1]
                edge_length = graph[current][next_point]['weight']
                path_length += edge_length
                path.append(next_point)
                current = next_point
    
    # Remove short spurs and isolated nodes
    graph.remove_edges_from(edges_to_remove)
    graph.remove_nodes_from([n for n in graph.nodes() if graph.degree(n) == 0])
    
    print(f'Short spurs removed.')
    return graph

def graph_to_linestring(graph):
    """Convert a path graph to a LineString"""
    if len(graph.edges) == 0:
        return None
        
    # Get edges in order
    edges = list(nx.dfs_edges(graph))
    coords = [edges[0][0]]
    coords.extend(edge[1] for edge in edges)
    
    print(f'Graph converted to linestring.')
    return LineString(coords)

def split_at_junctions(graph):
    """
    Split a graph at junction nodes (degree > 2) into individual branches
    using a simpler traversal approach.
    """
    if len(graph.edges) == 0:
        return []
        
    # Find junction nodes (degree > 2)
    junctions = [node for node, degree in graph.degree() if degree > 2]
    
    # If no junctions, return the original graph as a single branch
    if not junctions:
        return [graph]
    
    # Get endpoints (degree 1)
    endpoints = [node for node, degree in graph.degree() if degree == 1]
    
    # Start points for our traversal
    start_points = endpoints + junctions
    
    # Keep track of used edges
    used_edges = set()
    branches = []
    
    # Process each start point
    for start in start_points:
        # Get neighbors we haven't fully explored yet
        neighbors = [n for n in graph.neighbors(start) 
                    if (start, n) not in used_edges and (n, start) not in used_edges]
        
        for neighbor in neighbors:
            # Create a new branch
            branch = nx.Graph()
            current = start
            next_node = neighbor
            
            # Follow the path until we hit a junction or endpoint
            while True:
                # Add the current edge to the branch
                edge_data = graph.get_edge_data(current, next_node)
                branch.add_edge(current, next_node, **edge_data)
                used_edges.add((current, next_node))
                used_edges.add((next_node, current))
                
                # If we've hit a junction or endpoint, stop
                if next_node in start_points:
                    break
                    
                # Get the next node (the one we haven't visited)
                current = next_node
                next_neighbors = list(graph.neighbors(current))
                next_node = [n for n in next_neighbors 
                           if (current, n) not in used_edges and (n, current) not in used_edges]
                
                if not next_node:  # No unvisited neighbors
                    break
                next_node = next_node[0]
            
            # Only keep branches above minimum length
            if len(branch.edges) > 0:
                branch_length = sum(data['weight'] for _, _, data in branch.edges(data=True))
                if branch_length >= min_branch_length:
                    branches.append(branch)
    
    return branches

def get_skeletons():
    start_time = time.time()
    gdf = gpd.read_file(input_shp)
    print(f"Read file: {time.time() - start_time:.2f}s")
    
    cleaned_gdf = clean_highwalls(gdf)
    print(f"Cleaned highwalls: {time.time() - start_time:.2f}s")
    
    ex_gdf = cleaned_gdf.explode(index_parts=False)
    print(f"Exploded: {time.time() - start_time:.2f}s")

    features = []
    
    for _, row in ex_gdf.iterrows():
        iter_start = time.time()
        c_line = get_centerlines(row)
        print(f"Got centerline for row {row['ID']}: {time.time() - iter_start:.2f}s")
        
        if c_line is not None:
            # Convert centerline to graph
            graph_start = time.time()
            graph = build_graph_from_centerline(c_line)
            print(f"Built graph for row {row['ID']}: {time.time() - graph_start:.2f}s")
            
            # Remove short spurs
            spur_start = time.time()
            graph = remove_short_spurs(graph, min_length=min_spur_length)
            print(f"Removed spurs for row {row['ID']}: {time.time() - spur_start:.2f}s")
            
            if len(graph.edges) > 0:
                # Check if the graph has any junctions
                has_junctions = any(degree > 2 for _, degree in graph.degree())
                
                if has_junctions:
                    # Split at junctions and process branches
                    split_start = time.time()
                    branch_graphs = split_at_junctions(graph)
                    print(f"Split at junctions for row {row['ID']}: {time.time() - split_start:.2f}s")
                    
                    for branch in branch_graphs:
                        branch_geom = graph_to_linestring(branch)
                        if branch_geom is not None:
                            features.append({
                                "id": row["ID"],
                                "geometry": branch_geom
                            })
                else:
                    # Convert unbranched centerline graph to LineString
                    skeleton_geom = graph_to_linestring(graph)
                    if skeleton_geom is not None:
                        features.append({
                            "id": row["ID"],
                            "geometry": skeleton_geom
                        })
        print(f"Total time for row {row['ID']}: {time.time() - iter_start:.2f}s")
        print("----------------------------------------")

    # Save all features
    save_start = time.time()
    if len(features) > 0:
        features_gdf = gpd.GeoDataFrame(features, geometry="geometry", crs=cleaned_gdf.crs)
        features_gdf.to_file(output_shp)
        print(f"Saved {len(features)} features: {time.time() - save_start:.2f}s")
    
    print(f"Total execution time: {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    get_skeletons()