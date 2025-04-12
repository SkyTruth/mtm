import os
import subprocess

from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCS_MOUNT,
)

# Mount GCS bucket
os.makedirs(GCS_MOUNT, exist_ok=True)
subprocess.run(['gcsfuse', '--implicit-dirs', GCLOUD_BUCKET, GCS_MOUNT])