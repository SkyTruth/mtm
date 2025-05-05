'''
For testing and modifying just the get_centerlines function.
'''

import centerline.geometry as cl
import geopandas as gpd
import os
from shapely.geometry import Polygon, MultiPolygon
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
output_shp = outputs+"test_centerlines_4_clipped.shp"

interp_distance = 4


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

    repro_gdf.to_file(temps+"cleaned_highwalls.shp")
    
    return repro_gdf


def get_centerlines():
    # Read in highwall polygons

    gdf = gpd.read_file(input_shp)
    cleaned_gdf = clean_highwalls(gdf)
    ex_gdf = cleaned_gdf.explode(index_parts=False)

    c_lines = []
    for _, row in ex_gdf.iterrows(): # Iterate through each highwall polygon
        try:
            poly = row.geometry
            
            # Add a buffer of 1 meter since we're in UTM coordinates
            poly = poly.buffer(1.0)

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

            '''
            # Adjust interpolation distance based on polygon size (in square meters)
            area = poly.area
            if area < 500:  # Very small
                interp_distance = 2
            elif area < 2000:  # Small
                interp_distance = 3
            elif area < 5000:  # Medium
                interp_distance = 4
            elif area < 10000:  # Large
                interp_distance = 5
            else:  # Very large
                interp_distance = max(6, min(8, area/1500))
            
            # First try with default settings
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
            '''
            c_lines.append({"id": row["ID"], "geometry": c_line.geometry})
            
        except Exception as e:
            print(f"Warning: Could not process polygon with ID {row['ID']}: {str(e)}")
            continue

    if not c_lines:
        raise Exception("No centerlines could be generated!")

    # Save the final skeletons to a shapefile
    centerline_gdf = gpd.GeoDataFrame(c_lines, geometry="geometry", crs=gdf.crs)
    centerline_gdf.to_file(output_shp)
    print(f"Saved final centerlines to {output_shp}")

if __name__ == "__main__":
    get_centerlines()