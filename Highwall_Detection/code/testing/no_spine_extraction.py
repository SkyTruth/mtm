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

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Working directories
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define directory root
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

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
output_shp = outputs+"no_spine_extraction.shp"

# Variables
min_area = 100
interp_distance = 4
min_spur_length = 10
min_branch_length = 20

def clean_highwalls(gdf):
    """
    Reprojects, removes small holes, and buffers highwall polygons to maintain 8-connectivity.
    """
    # Reproject to EPSG:32617
    repro_gdf = gdf.to_crs(epsg=32617)

    def remove_holes(geom, min_area=min_area):
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

    # Buffer to maintain 8-connectivity
    repro_gdf["geometry"] = repro_gdf["geometry"].buffer(1.0)

    # Apply the hole removal function to each geometry
    repro_gdf["geometry"] = repro_gdf["geometry"].apply(remove_holes)

    repro_gdf.to_file(temps+"cleaned_highwalls.shp")
    
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

def split_at_junctions(graph):
    """
    Split a graph at junction nodes (degree > 2) into individual branches
    Returns a list of subgraphs, each representing a branch between endpoints
    and junctions, with no intermediate junctions. Branches shorter than min_branch_length are removed.
    """
    # If no edges, return empty list
    if len(graph.edges) == 0:
        return []
        
    # Find junction nodes (degree > 2)
    junctions = [node for node, degree in graph.degree() if degree > 2]
    
    # If no junctions, return the original graph as a single branch
    if not junctions:
        return [graph]
    
    # Get endpoints (degree 1)
    endpoints = [node for node, degree in graph.degree() if degree == 1]
    
    # Get all significant points (endpoints and junctions)
    significant_points = endpoints + junctions
    
    # Create a copy of the original graph to track unused edges
    remaining_graph = graph.copy()
    
    # Find all direct paths between significant points and create subgraphs
    branches = []
    for i in range(len(significant_points)):
        for j in range(i + 1, len(significant_points)):
            start = significant_points[i]
            end = significant_points[j]
            try:
                # Find all simple paths between the points
                for path in nx.all_simple_paths(graph, start, end):
                    # Check if path goes through any other junction points
                    intermediate_junctions = [p for p in path[1:-1] if p in junctions]
                    
                    # If the path is direct (no intermediate junctions)
                    if not intermediate_junctions:
                        # Create a new graph for this branch
                        branch = nx.Graph()
                        branch_length = 0
                        # Add edges with their weights
                        for k in range(len(path) - 1):
                            u, v = path[k], path[k + 1]
                            edge_data = graph.get_edge_data(u, v)
                            branch.add_edge(u, v, **edge_data)
                            branch_length += edge_data['weight']
                            # Remove these edges from remaining_graph
                            if remaining_graph.has_edge(u, v):
                                remaining_graph.remove_edge(u, v)
                        
                        # Only add branch if it's longer than min_branch_length
                        if branch_length >= min_branch_length:
                            branches.append(branch)
            except nx.NetworkXNoPath:
                continue
    
    # Handle remaining edges (potential loops)
    remaining_edges = list(remaining_graph.edges(data=True))
    if remaining_edges:
        # Create a new graph for each continuous chain of remaining edges
        while remaining_edges:
            branch = nx.Graph()
            edge_stack = [remaining_edges[0]]  # Start with first remaining edge
            
            while edge_stack:
                u, v, data = edge_stack.pop()
                if not branch.has_edge(u, v):
                    branch.add_edge(u, v, **data)
                    remaining_edges.remove((u, v, data))
                    
                    # Find connected edges
                    for edge in remaining_edges[:]:  # Use slice to allow removal
                        if edge[0] in (u, v) or edge[1] in (u, v):
                            edge_stack.append(edge)
            
            # Only add branch if it's longer than min_branch_length
            if len(branch.edges) > 0:
                branch_length = sum(data['weight'] for _, _, data in branch.edges(data=True))
                if branch_length >= min_branch_length:
                    branches.append(branch)
    
    return branches

def graph_to_linestring(graph):
    """Convert a path graph to a LineString"""
    if len(graph.edges) == 0:
        return None
        
    # Find endpoints (degree 1)
    endpoints = [node for node, degree in graph.degree() if degree == 1]
    
    if endpoints:
        # Start from an endpoint
        start = endpoints[0]
    else:
        # If no endpoints, start from any node
        start = list(graph.nodes())[0]
    
    # Use a simple path traversal
    path = [start]
    current = start
    
    while True:
        neighbors = list(graph.neighbors(current))
        if not neighbors:
            break
            
        # Find the neighbor we haven't visited yet
        next_node = None
        for neighbor in neighbors:
            if neighbor not in path:
                next_node = neighbor
                break
                
        if next_node is None:
            break
            
        path.append(next_node)
        current = next_node
    
    print('Graph converted to LineString.')
    return LineString(path)

def get_skeletons():
    gdf = gpd.read_file(input_shp)
    
    cleaned_gdf = clean_highwalls(gdf)
    
    ex_gdf = cleaned_gdf.explode(index_parts=False)

    features = []
    
    for _, row in ex_gdf.iterrows():
        c_line = get_centerlines(row)
        
        if c_line is not None:
            # Convert centerline to graph
            graph = build_graph_from_centerline(c_line)
            
            # Remove short spurs
            graph = remove_short_spurs(graph, min_length=min_spur_length)
            
            if len(graph.edges) > 0:
                # Check if the graph has any junctions
                has_junctions = any(degree > 2 for _, degree in graph.degree())
                
                if has_junctions:
                    # Split at junctions and process branches
                    branch_graphs = split_at_junctions(graph)
                    
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

    # Save all features
    if len(features) > 0:
        features_gdf = gpd.GeoDataFrame(features, geometry="geometry", crs=cleaned_gdf.crs)
        features_gdf.to_file(output_shp)
    


if __name__ == "__main__":
    get_skeletons()