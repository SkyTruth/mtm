'''
For testing and modifying just the get_centerlines function.
'''

import centerline.geometry as cl
import geopandas as gpd
import os

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
input_shp = inputs+"test_set.shp"
output_shp = outputs+"test_centerlines.shp"

interp_distance = 2

def get_centerlines():
    # Read in highwall polygons
    gdf = gpd.read_file(input_shp)
    ex_gdf = gdf.explode(index_parts=False)
    print(gdf.crs)

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