'''
For testing and modifying just the get_centerlines() function.
'''

import centerline.geometry as cl
import geopandas as gpd
import os
from shapely.geometry import Polygon, MultiPolygon

from mtm_utils.variables import (
    HW_TEMP_DIR,
    HW_OUTPUT_DIR,
    INPUT_HIGHWALLS_TESTING,
    INPUT_HIGHWALLS_FULL,
    INTERP_DISTANCE,
    TEMP_CLEANED_HIGHWALLS,
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

    repro_gdf.to_file(TEMP_CLEANED_HIGHWALLS)
    
    return repro_gdf


def get_centerlines():
    # Read in highwall polygons

    gdf = gpd.read_file(INPUT_HIGHWALLS)
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
    output_shp = HW_TEMP_DIR + "test_centerlines.shp"
    centerline_gdf.to_file(output_shp)
    print(f"Saved final centerlines to {output_shp}")

if __name__ == "__main__":
    data_dir_creation()
    get_centerlines()