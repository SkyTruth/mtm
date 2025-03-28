# Initialize Google Cloud Storage client
from google.cloud import storage
project_id = 'skytruth-tech'
client = storage.Client(project=project_id)

# Access bucket
bucket_name = 'mountaintop_mining'
bucket = client.get_bucket(bucket_name)

# Mount bucket as a directory in VM
import os
import subprocess
os.makedirs('gcs', exist_ok=True)
subprocess.run(['gcsfuse', '--implicit-dirs', 'mountaintop_mining', 'gcs'])