import centerline.geometry as cl
import geopandas as gpd
import os
import networkx as nx
from shapely.geometry import LineString, MultiLineString
from shapely.geometry import Polygon, MultiPolygon

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


def clean_highwalls(gdf):
    """
    Reprojects and removes small holes from highwall polygons.
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
    return repro_gdf


def get_centerlines(row):
    """
    Extracts (messy) centerlines from a highwall polygon.
    """
    try:
        poly = row.geometry
        poly = poly.buffer(1.0)
        
        # Adjust interpolation distance based on polygon size (in square meters)
        area = poly.area
        if area < 1000:  # Small polygons (< 1000 m²)
            interp_distance = 3
        elif area < 5000:  # Medium polygons (1000-5000 m²)
            interp_distance = 4
        else:  # Large polygons (> 5000 m²)
            interp_distance = max(5, min(7, area/1000))  # Between 4-6m based on size
        
        try:
            c_line = cl.Centerline(poly,
                                interpolation_distance=interp_distance,
                                interpolation_options={'qhull_options': 'QJ Qbb'})
        except:
            # If that fails, try with a smaller interpolation distance
            try:
                c_line = cl.Centerline(poly,
                                    interpolation_distance=interp_distance/2,
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB'})
            except:
                # If that still fails, try with minimum settings
                c_line = cl.Centerline(poly,
                                    interpolation_distance=2,  # minimum 2 meters
                                    interpolation_options={'qhull_options': 'QJ Qbb QbB Qs'})
        return c_line
        
    except Exception as e:
        print(f"Warning: Could not process polygon with ID {row['ID']}: {str(e)}")
        return None

def longest_path_tree(graph):
    """
    Finds the longest path in a weighted tree graph and returns a subgraph containing only the longest path.

    Parameters:
        graph (networkx.Graph): A connected graph (assumed to be a tree).

    Returns:
        networkx.Graph: A subgraph of the input graph containing only the longest path.
    """

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

    return longest_path_graph


def find_longest_spine(graph):
    """
    Finds the longest continuous line from a graph and returns the spine and its edges
    Returns:
        tuple: (spine_linestring, spine_edges) or (None, None) if no valid spine is found
    """
    # If graph is empty or has no edges, return None
    if len(graph.edges) == 0:
        return None, None
    
    try:
        # Get the longest spine
        spine_graph = longest_path_tree(graph)
        
        # If spine has no edges, return None
        if len(spine_graph.edges) == 0:
            return None, None
        
        # Get the spine edges
        spine_edges = set(spine_graph.edges())

        # Spine should only have one connected component, but this processes multiple components just in case
        connected_components = [list(component) for component in nx.connected_components(spine_graph)]
        if len(connected_components) > 1:
            print(f"Warning: spine has {len(connected_components)} components when 1 was expected")

        # Convert spine to LineString
        linestrings = []
        for component in connected_components:
            subgraph = spine_graph.subgraph(component)
            if len(subgraph.edges) > 0:
                edges = list(nx.dfs_edges(subgraph)) # Get edges in DFS order
                if edges:
                    coords = [edges[0][0]]
                    coords.extend(edge[1] for edge in edges)
                    linestrings.append(LineString(coords))
        
        # If no valid linestrings were created, return None
        if not linestrings:
            return None, None

        # If there are multiple linestrings, combine them into a MultiLineString
        spine_geometry = MultiLineString(linestrings) if len(linestrings) > 1 else linestrings[0]

        # Return the spine geometry and the edges that make up the spine
        return spine_geometry, spine_edges
    
    except Exception as e:
        print(f"Error in find_longest_spine: {str(e)}")
        return None, None

def extract_all_spines(cl, min_length=30):
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
    
    all_spines = []
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
        if total_length < min_length:
            break
            
        # Find the longest spine in this component
        spine, spine_edges = find_longest_spine(subgraph)
        if spine is None or spine.length < min_length:
            break
            
        print(f"Iteration {iteration}: Found spine of length {spine.length}")
        all_spines.append(spine)
        
        # Remove the longest spine from the main graph
        graph.remove_edges_from(spine_edges)
        graph.remove_nodes_from([n for n in graph.nodes() if graph.degree(n) == 0])
        
        print(f"Remaining graph has {len(graph.edges)} edges")
        iteration += 1
    
    print(f"Finished: found {len(all_spines)} spines in total.")
    
    # If no spines were found, return None
    if not all_spines:
        return None
        
    # Combine all spines into a single MultiLineString
    return MultiLineString(all_spines)

def get_skeletons():
    """
    Takes a shapefile of highwall polygons and extracts a skeleton from each polygon.
    """
    # Read in highwall polygons
    gdf = gpd.read_file(input_shp)
    cleaned_gdf = clean_highwalls(gdf)
    print(cleaned_gdf.crs)
    ex_gdf = cleaned_gdf.explode(index_parts=False)

    c_lines = []
    for _, row in ex_gdf.iterrows(): # Iterate through each highwall polygon
        c_line = get_centerlines(row) # Extract centerlines
        if c_line is not None:
            c_line.geometry = extract_all_spines(c_line) # Clean up centerlines by only getting the main spines
            c_lines.append({"id": row["ID"], "geometry": c_line.geometry})


    if len(c_lines) > 0:
        centerline_gdf = gpd.GeoDataFrame(c_lines, geometry="geometry", crs=cleaned_gdf.crs)
        centerline_gdf.to_file(output_shp)
        print(f"Saved final skeletons to {output_shp}")
    else:
        print("No valid centerlines were generated!")


if __name__ == "__main__":
    get_skeletons()