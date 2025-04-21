'''
Mounts the mountaintop_mining bucket as a directory in the VM.
Should only need to be run once per VM instance.
'''

import os
import subprocess

from Canopy_Height.code.ch_variables import (
    GCLOUD_BUCKET,
    GCS_MOUNT,
)

os.makedirs(GCS_MOUNT, exist_ok=True)
subprocess.run(['gcsfuse', '--implicit-dirs', GCLOUD_BUCKET, GCS_MOUNT])