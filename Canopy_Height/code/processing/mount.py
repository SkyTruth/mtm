'''
Mounts the mountaintop_mining bucket as a directory in the VM.
'''

from mtm_utils.variables import (
    GCLOUD_BUCKET,
    PROJECT_ID
)

import os
import subprocess
# from google.cloud import storage

# client = storage.Client(project=PROJECT_ID)
# bucket = client.get_bucket(GCLOUD_BUCKET)

# Mount GCS bucket
os.makedirs('data/gcs', exist_ok=True)
subprocess.run(['gcsfuse', '--implicit-dirs', GCLOUD_BUCKET, 'data/gcs'])