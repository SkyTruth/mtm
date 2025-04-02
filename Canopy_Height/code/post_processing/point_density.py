# Import necessary modules
import os
import re
import statistics
import random
from multiprocessing import Pool
import subprocess
import whitebox

whitebox_executable = os.path.abspath('whitebox-tools-master/target/release/whitebox_tools')

# Select state and lidar acquisition project
state = "tn"
project = "B3"

# Calculate point density and extract it from the output html file
def process_file(fn):
    print(f'{dir}{fn}')
    output_html = os.path.join(dir, fn.replace('.laz', '.html'))
    lidar_info = [
        whitebox_executable,
        '--run="LidarInfo"',
        f'--input="{dir}{fn}"',
        f'--output="{output_html}"',
        '--density=True',
        '--vlr=False',
        'geokeys=False'
    ]
    process = subprocess.run(lidar_info)

    with open(output_html, 'r') as file:
        for line in file:
            if "Average point density" in line:
                # Extract the average point density value using regex to match the number before "pts/m²"
                match = re.search(r'Average point density: (\d+\.\d+)', line)
                if match:
                    point_density = float(match.group(1))
                    return point_density

# Take a random sample of 50 tiles
dir = f'/home/alanal/gcs/lidar_data/{state}/'
all_files = [fn for fn in os.listdir(dir) if project in fn]
sample_files = random.sample(all_files, 50)

with Pool() as pool:
    point_densities = pool.map(process_file, sample_files)

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