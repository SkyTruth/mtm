'''
Takes a random sample of 50 LAZ tiles from a LiDAR project and calculates the average point density.
'''

# Import necessary modules
import os
import re
import statistics
import random
from multiprocessing import Pool
from functools import partial
import whitebox
wbt = whitebox.WhiteboxTools()

from mtm_utils.variables import (
    LIDAR_DIR
)

# Calculate point density and extract it from the output html file
def process_file(fn, dir):
    print(f'{dir}/{fn}')
    output_html = os.path.join(dir, fn.replace('.laz', '.html'))

    wbt.lidar_info(
        i=f"{dir}/{fn}",
        output=output_html,
        density=True,
        vlr=False,
        geokeys=False
    )

    with open(output_html, 'r') as file:
        for line in file:
            if "Average point density" in line:
                # Extract the average point density value using regex to match the number before "pts/m²"
                match = re.search(r'Average point density: (\d+\.\d+)', line)
                if match:
                    point_density = float(match.group(1))
                    return point_density

def main():
    # Select state and lidar acquisition project
    state = "tn"
    project = "B3"

    # Take a random sample of 50 tiles
    dir = os.path.abspath(f'{LIDAR_DIR}/{state}')
    all_files = [fn for fn in os.listdir(dir) if project in fn]
    sample_files = random.sample(all_files, 50)

    # Process files in parallel
    with Pool() as pool:
        point_densities = pool.map(partial(process_file, dir=dir), sample_files)

    # Remove None values (files where average point density couldn't be found)
    point_densities = [density for density in point_densities if density is not None]

    print(point_densities)

    # Calculate and print summary statistics
    mean_density = statistics.mean(point_densities)
    median_density = statistics.median(point_densities)
    min_density = min(point_densities)
    max_density = max(point_densities)
    std_dev_density = statistics.stdev(point_densities)

    print(f"Summary Statistics:")
    print(f"Mean: {mean_density}")
    print(f"Median: {median_density}")
    print(f"Min: {min_density}")
    print(f"Max: {max_density}")
    print(f"Standard Deviation: {std_dev_density}")

if __name__ == '__main__':
    main()