'''
Extracts centerline branches from highwall geometries by iteratively extracting the longest spine
from a centerline graph.
'''

import centerline.geometry as cl
import geopandas as gpd
import os
import networkx as nx
from shapely.geometry import LineString, Polygon, MultiPolygon

from mtm_utils.variables import (
    HW_TEMP_DIR,
    HW_OUTPUT_DIR,
    INPUT_HIGHWALLS_TESTING,
    INPUT_HIGHWALLS_FULL,
    TEMP_CLEANED_HIGHWALLS,
    MIN_AREA,
    INTERP_DISTANCE,
    MIN_SPUR_LENGTH,
    MIN_BRANCH_LENGTH
)

# Set  = INPUT_HIGHWALLS_TESTING to test code with a smaller subset of highwalls
# or  = INPUT_HIGHWALLS_FULL to process full dataset of highwalls
INPUT_HIGHWALLS = INPUT_HIGHWALLS_FULL


def data_dir_creation():
    """
    Makes temp and output directories if they do not exist.
    """
    os.makedirs(HW_TEMP_DIR, exist_ok=True)
    os.makedirs(HW_OUTPUT_DIR, exist_ok=True)


def clean_highwalls(gdf):
    """
    Reprojects, removes small holes, and buffers highwall polygons to maintain 8-connectivity.
    """
    # Reproject to EPSG:32617
    repro_gdf = gdf.to_crs(epsg=32617)

    def remove_holes(geom):
        if isinstance(geom, Polygon):
            if geom.interiors:
                new_interiors = [
                    ring for ring in geom.interiors 
                    if Polygon(ring).area >= MIN_AREA
                ]
                return Polygon(geom.exterior, new_interiors)
            return geom
        # Handle MultiPolygon case
        elif isinstance(geom, MultiPolygon):
            return MultiPolygon([remove_holes(poly) for poly in geom.geoms])
        return geom

    # Apply the hole removal function to each geometry
    repro_gdf["geometry"] = repro_gdf["geometry"].apply(remove_holes)
    
    # Buffer to maintain 8-connectivity
    repro_gdf["geometry"] = repro_gdf["geometry"].buffer(1.0)

    repro_gdf.to_file(TEMP_CLEANED_HIGHWALLS)
    
    return repro_gdf


def get_centerlines(row):
    """
    Extracts (messy) centerlines from a highwall polygon.
    """
    try:
        poly = row.geometry

        try:
            c_line = cl.Centerline(poly,
                                interpolation_distance=INTERP_DISTANCE,
                                interpolation_options={'qhull_options': 'QJ Qbb'})
        except:
            try: # If that fails, try with a smaller interpolation distance
                c_line = cl.Centerline(poly,
                                    interpolation_distance=max(0.5,INTERP_DISTANCE/2),
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB'})
            except: # If that still fails, try with minimum settings
                c_line = cl.Centerline(poly,
                                    interpolation_distance=0.5,
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB Qs'})
        return c_line
        
    except Exception as e:
        print(f"Warning: Could not process polygon with ID {row['ID']}: {str(e)}")
        return None

def find_longest_spine(graph):
    """
    Finds the longest continuous path from a graph and returns the spine as a subgraph.
    Returns:
        networkx.Graph: Subgraph containing the longest spine, or None if no valid spine is found
    """
    # If graph is empty or has no edges, return None
    if len(graph.edges) == 0:
        return None
    
    def farthest_node(graph, start_node):
        """
        Helper function to find the farthest node and its distance from a given start node.
        Uses a stack to perform a depth-first search (DFS) to find the farthest node.
        """
        # Store distances from start node to all other visited nodes
        distances = {}
        # Initialize stack with start node and distance 0
        stack = [(start_node, 0)]  # (current_node, current_distance)
        # Until the stack is empty:
        while stack:
            # Remove and return the last node from the stack
            node, dist = stack.pop()
            # If the node has not been visited yet:
            if node not in distances:
                # Store the node and its distance from the start node
                distances[node] = dist
                # For each neighbor of the current node:
                for neighbor, edge_data in graph[node].items():
                    # Add the neighbor and its distance to the stack
                    stack.append(
                        (neighbor, dist + edge_data.get("weight", 1))
                    )  # Default weight is 1
        # Find the node with the maximum distance from the start node
        farthest = max(distances, key=distances.get)
        # Return the farthest node and its distance from the start node
        return farthest, distances[farthest]
    
    try:
        # Step 1: Find one endpoint of the longest path
        start_node = list(graph.nodes)[0] # Pick a start node
        farthest, _ = farthest_node(graph, start_node) # Find the farthest node from the start node

        # Step 2: Find the other endpoint of the longest path
        other_farthest, _ = farthest_node(graph, farthest)

        # Step 3: Extract the path from farthest to other_farthest
        path_nodes = nx.shortest_path(
            graph, source=farthest, target=other_farthest, weight="weight"
        )

        # Create a new graph for the longest path
        longest_path_graph = nx.Graph()
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            # Add edge to the new graph with its weight
            edge_data = graph.get_edge_data(u, v)
            longest_path_graph.add_edge(u, v, **edge_data)

        # If spine has no edges, return None
        if len(longest_path_graph.edges) == 0:
            return None
        
        return longest_path_graph
    
    except Exception as e:
        print(f"Error in find_longest_spine: {str(e)}")
        return None

def extract_all_spines(cl):
    """
    Iteratively extracts all spines above minimum length from a centerline
    """
    # Initialize an empty graph
    graph = nx.Graph()
    
    # Build initial graph from centerline
    for linestring in cl.geometry.geoms:
        coords = list(linestring.coords)
        for i in range(len(coords) - 1):
            # Add edge with length as weight
            length = LineString([coords[i], coords[i+1]]).length
            graph.add_edge(coords[i], coords[i+1], weight=length)
    
    print(f"Initial graph has {len(graph.edges)} edges")
    
    # Find and remove short spurs
    endpoints = [node for node, degree in graph.degree() if degree == 1]
    edges_to_remove = set()  # Use a set to avoid duplicates
    
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
                if path_length < MIN_SPUR_LENGTH:
                    for i in range(len(path)-1):
                        edges_to_remove.add((path[i], path[i+1]))
                        edges_to_remove.add((path[i+1], path[i]))  # Add reverse edge too
                break
            elif len(neighbors) == 1 and current != endpoint:  # Another endpoint
                break
            else:  # Regular point with 2 neighbors or starting point
                # Move to the neighbor we haven't visited
                next_point = neighbors[0] if neighbors[0] not in path else neighbors[1]
                edge_length = graph[current][next_point]['weight']
                path_length += edge_length
                path.append(next_point)
                current = next_point
    
    # Remove short spurs and isolated nodes
    graph.remove_edges_from(edges_to_remove)
    graph.remove_nodes_from([n for n in graph.nodes() if graph.degree(n) == 0])
            
    print(f"Graph has {len(graph.edges)} edges after spur removal")
    
    all_spines = nx.Graph()
    iteration = 1
    
    # Iteratively find the longest spine in the remaining graph
    while True:
        # Split graph into connected components
        components = list(nx.connected_components(graph))
        if not components:
            break
            
        # Find the largest component by edge count and make it a subgraph
        largest_component = max(components, key=lambda c: len(graph.subgraph(c).edges))
        subgraph = graph.subgraph(largest_component).copy()
        
        # If subgraph is too small, skip it
        total_length = sum(data['weight'] for _, _, data in subgraph.edges(data=True))
        if total_length < MIN_BRANCH_LENGTH:
            break
            
        # Find the longest spine in this component
        spine_graph = find_longest_spine(subgraph)
        if spine_graph is None:
            break
            
        # Calculate spine length
        spine_length = sum(data['weight'] for _, _, data in spine_graph.edges(data=True))
        if spine_length < MIN_BRANCH_LENGTH:
            break
        
        # Add spine edges to all_spines graph
        all_spines.add_edges_from(spine_graph.edges(data=True))
        
        # Remove the longest spine from the main graph
        graph.remove_edges_from(spine_graph.edges())
        graph.remove_nodes_from([n for n in graph.nodes() if graph.degree(n) == 0])
        
        iteration += 1
    
    print(f"Finished extracting spines: found spines with {len(all_spines.edges)} total edges.")
    
    return all_spines if len(all_spines.edges) > 0 else None


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
                        if branch_length >= MIN_BRANCH_LENGTH:
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
                if branch_length >= MIN_BRANCH_LENGTH:
                    branches.append(branch)
    
    return branches

def graph_to_linestring(graph):
    """Convert a path graph to a LineString"""
    if len(graph.edges) == 0:
        return None
        
    # Get edges in order
    edges = list(nx.dfs_edges(graph))
    coords = [edges[0][0]]
    coords.extend(edge[1] for edge in edges)
    return LineString(coords)

def get_skeletons():
    """
    Takes a shapefile of highwall polygons and extracts skeletons and branches.
    """
    gdf = gpd.read_file(INPUT_HIGHWALLS)
    cleaned_gdf = clean_highwalls(gdf)
    ex_gdf = cleaned_gdf.explode(index_parts=False)

    features = []
    
    for _, row in ex_gdf.iterrows():
        c_line = get_centerlines(row)
        if c_line is not None:
            spine_graph = extract_all_spines(c_line)
            
            if spine_graph is not None:
                # Check if the graph has any junctions
                has_junctions = any(degree > 2 for _, degree in spine_graph.degree())
                
                if has_junctions:
                    # Split at junctions and process branches
                    branch_graphs = split_at_junctions(spine_graph)
                    for branch in branch_graphs:
                        branch_geom = graph_to_linestring(branch)
                        if branch_geom is not None:
                            features.append({
                                "id": row["ID"],
                                "geometry": branch_geom
                            })
                else:
                    # Convert unbranched centerline graph to LineString
                    skeleton_geom = graph_to_linestring(spine_graph)
                    if skeleton_geom is not None:
                        features.append({
                            "id": row["ID"],
                            "geometry": skeleton_geom
                        })

    # Save all features
    if len(features) > 0:
        # Create GeoDataFrame from features
        features_gdf = gpd.GeoDataFrame(features, geometry="geometry", crs=cleaned_gdf.crs)
        
        # Create a single polygon from all cleaned highwalls
        highwall_union = ex_gdf.union_all()
        
        # Clip all skeletons to the highwall union
        clipped_gdf = features_gdf.copy()
        clipped_gdf['geometry'] = clipped_gdf.intersection(highwall_union)
        
        # Remove any empty or invalid geometries
        clipped_gdf = clipped_gdf[clipped_gdf.geometry.length > 0]
        
        clipped_gdf.to_file(HW_OUTPUT_DIR + "spine_extraction_test.shp")
        print(f"Saved {len(clipped_gdf)} features after clipping")


if __name__ == "__main__":
    data_dir_creation()
    get_skeletons()