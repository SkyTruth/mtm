import datetime

PROCESSING_YEAR = datetime.date.today().year
# PROCESSING_YEAR = 2023

"""
Setting Up Local Directories For Mask Creation
"""
DATA_DIR = "data/"

# UPDATED DIRS
# Set the directories for the initial downloads
MASK_DATA = DATA_DIR + "USCB_Data/"
USCB_YEAR = MASK_DATA + str(PROCESSING_YEAR) + "/"
USCB_ZIP = USCB_YEAR + "zipped/"
USCB_SHP = USCB_YEAR + "shapefile/"
USCB_GJS = USCB_YEAR + "geojson/"

# Study Area Dirs
STUDY_AREA_DIR = DATA_DIR + "studyArea"
STUDY_AREA_ZIP = STUDY_AREA_DIR + "zipped/"
STUDY_AREA_SHP = STUDY_AREA_DIR + "shapefile/"
STUDY_AREA_GJS = STUDY_AREA_DIR + "geojson/"

# Dir for Mask
MASK_DIR = DATA_DIR + "maskData/"
MASK_INTERIM = MASK_DIR + "interimMask/"
MASK_FINAL = MASK_DIR + "finalMask/"





# # Set the directories for the initial downloads
# USCB_DIR = LOCAL_ROOT_DIR + "uscb_data/"
# USCB_YEAR = USCB_DIR + str(PROCESSING_YEAR) + "/"
# USCB_ZIP = USCB_YEAR + "zipped/"
# USCB_SHP = USCB_YEAR + "shapefile/"
# USCB_GJS = USCB_YEAR + "geojson/"


# MISC_DIR = LOCAL_ROOT_DIR + "misc_data/"
# MISC_ZIP = MISC_DIR + "misc_zip/"
# MISC_SHP = MISC_DIR + "misc_shp/"
# MISC_GJS = MISC_DIR + "misc_gjs/"

# MASK_DIR = LOCAL_ROOT_DIR + "mask_data/"
# MASK_INTERIM = MASK_DIR + "interim_mask/"
# MASK_FINAL = MASK_DIR + "final_mask/"

# # Set the Cloud Bucket for the Project
# GCLOUD_BUCKET = "mountaintop_mining"

# # Set the Cloud Folder where annual masks are stored
# GCLOUD_MASK_DIR = "mask_data/"
# # Name for the folder in the Cloud Bucket for the annual mask data
# GCLOUD_EE_DIR = "gee_data/"
# GCLOUD_EE_GPC_DIR = GCLOUD_EE_DIR + "GPC/"
# GCLOUD_EE_THRESHOLD_DIR = GCLOUD_EE_DIR + "ANNUAL_THRESHOLD_IMAGES/"

# GCLOUD_EE_ANNUAL_MINES_TIFF = GCLOUD_EE_DIR + "ANNUAL_MINE_GEOTIFF/"
# GCLOUD_EE_ANNUAL_MINES_GEOJSON = GCLOUD_EE_DIR + "ANNUAL_MINE_GEOJSON/"
# GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF = GCLOUD_EE_DIR + "CUMULATIVE_MINE_GEOTIFF/"

# GCLOUD_FINAL_DATA_DIR = GCLOUD_EE_DIR + "FINAL_DATA/"
# GCLOUD_FINAL_DATA_GEOJSON = GCLOUD_FINAL_DATA_DIR + "GEOJSON/"
# GCLOUD_FINAL_DATA_GEOTIFF = GCLOUD_FINAL_DATA_DIR + "GEOTIFF/"
# GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE = GCLOUD_FINAL_DATA_DIR + "GEOTIFF_CUMULATIVE/"


# ########################################################################################################################
# ########################################################################################################################
# """
# Setting Up GCS Directories
# """
# # Root Directory that is home to input files and processing output
# # FOR GENERAL USE : ROOT_DIR = "/PATH/TO/DATA/DIRECTORY/"
# # ROOT_DIR = "/home/christian/mtm/"

# # Set the Cloud Bucket for the Project
# GCLOUD_BUCKET = "mountaintop_mining"

# # List of files to process
# FILE_PROCESS_LIST = []

# # # GEE Authentication
# # EE_SERVICE_ACCOUNT = "skytruth-tech@skytruth-tech.iam.gserviceaccount.com"
# # # EE_CREDENTIAL_DIR = "EE_KEY/"
# # EE_CREDENTIAL_DIR = "/Users/christian/code/inambari_automation/EE_KEY/"
# # EE_CREDENTIALS = "skytruth-tech-d18f5b018d76.json"
# #
# # EE_ASSET_PATH = "projects/skytruth-tech/assets/INAMBARI/"

# # GEE Authentication
# EE_SERVICE_ACCOUNT = "skytruth-ee@skytruth-storage.iam.gserviceaccount.com"
# EE_CREDENTIAL_DIR = "config_files/"
# EE_CREDENTIALS = "skytruth-storage-0d6998431888.json"

# EE_ASSET_PATH = "projects/skytruth-tech/assets/MTM/"

# # /////////


# # #GEE Authentication
# # EE_SERVICE_ACCOUNT = "skytruth-tech@skytruth-tech.iam.gserviceaccount.com"
# # EE_CREDENTIAL_DIR = ROOT_DIR + "EE_KEY/"
# # EE_CREDENTIALS = "skytruth-tech-bcdd1082dd54.json"
