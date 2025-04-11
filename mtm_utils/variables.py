import datetime

PROCESSING_YEAR = datetime.date.today().year
# Uncomment line below to set the processing year, otherwise processing_year = current year
# PROCESSING_YEAR = 2022
"""
Setting Up Local Directories For Mask Creation
"""
DATA_DIR = "data/"
TEMP_DIR = DATA_DIR + "tmp/"

# UPDATED DIRS
# Set the directories for the initial downloads
MASK_DATA = DATA_DIR + "USCB_Data/"
USCB_YEAR = MASK_DATA + str(PROCESSING_YEAR) + "/"
USCB_ZIP = USCB_YEAR + "zipped/"
USCB_SHP = USCB_YEAR + "shapefile/"
USCB_GJS = USCB_YEAR + "geojson/"

# Study Area Dirs
STUDY_AREA_DIR = DATA_DIR + "studyArea/"
STUDY_AREA_ZIP = STUDY_AREA_DIR + "zipped/"
STUDY_AREA_SHP = STUDY_AREA_DIR + "shapefile/"
STUDY_AREA_GJS = STUDY_AREA_DIR + "geojson/"

# Dir for Mask
MASK_DIR = DATA_DIR + "maskData/"
MASK_INTERIM = MASK_DIR + "interimMask/"
MASK_FINAL = MASK_DIR + "finalMask/"

# FIPS Codes for Counties in the Study Area
FIPS_CODES = [21013, 21019, 21025, 21043, 21051, 21053, 21063, 21065, 21071, 21089, 21095,
              21109, 21115, 21119, 21121, 21125, 21127, 21129, 21131, 21133, 21135, 21147,
              21153, 21159, 21165, 21175, 21189, 21193, 21195, 21197, 21199, 21203, 21205,
              21231, 21235, 21237, 47001, 47013, 47025, 47035, 47049, 47129, 47133, 47137,
              47141, 47145, 47151, 51027, 51051, 51105, 51167, 51169, 51185, 51195, 51720,
              54005, 54011, 54015, 54019, 54025, 54039, 54043, 54045, 54047, 54053, 54055,
              54059, 54067, 54075, 54079, 54081, 54089, 54099, 54101, 54109]


# Set the Cloud Bucket for the Project
GCLOUD_BUCKET = "mountaintop_mining"

# Set the Cloud Folder where annual masks are stored
GCLOUD_MASK_DIR = "mask_data/"

# Set the Cloud Folder where CAMRA data are stored
GCLOUD_CAMRA_DIR = "CAMRA/"
GCLOUD_CAMRA_CSV = GCLOUD_CAMRA_DIR + "csv/"
GCLOUD_CAMRA_GJS = GCLOUD_CAMRA_DIR + "geojson/"
GCLOUD_CAMRA_ARM = GCLOUD_CAMRA_DIR + "ARM_Data/"

# Name for the folder in the Cloud Bucket for the annual mask data
GCLOUD_EE_DIR = "gee_data/"
GCLOUD_EE_GPC_DIR = GCLOUD_EE_DIR + "GPC/"
GCLOUD_EE_THRESHOLD_DIR = GCLOUD_EE_DIR + "ANNUAL_THRESHOLD_IMAGES/"

GCLOUD_EE_ANNUAL_MINES_TIFF = GCLOUD_EE_DIR + "ANNUAL_MINE_GEOTIFF/"
GCLOUD_EE_ANNUAL_MINES_GEOJSON = GCLOUD_EE_DIR + "ANNUAL_MINE_GEOJSON/"
GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF = GCLOUD_EE_DIR + "CUMULATIVE_MINE_GEOTIFF/"

GCLOUD_FINAL_DATA_DIR = GCLOUD_EE_DIR + "FINAL_DATA/"
GCLOUD_FINAL_DATA_GEOJSON = GCLOUD_FINAL_DATA_DIR + "GEOJSON/"
GCLOUD_FINAL_DATA_GEOTIFF = GCLOUD_FINAL_DATA_DIR + "GEOTIFF/"
GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE = GCLOUD_FINAL_DATA_DIR + "GEOTIFF_CUMULATIVE/"

# TODO: add remaining variables


"""
Canopy Height Variables
"""

GCS_MOUNT = 'data/gcs'
LIDAR_DIR = GCS_MOUNT + '/lidar_data/'
TILE_IDS_DIR = LIDAR_DIR + 'tile_IDs/'
FINAL_MOSAICS_DIR = LIDAR_DIR + 'final_mosaics/'

WV_COUNTIES = ['boone','cabell','clay','fayette','greenbrier','kanawha','lincoln','logan',
               'mason','mcdowell','mercer','mingo','nicholas','pocahontas','putnam','raleigh',
               'summers','wayne','webster','wyoming']
TN_COUNTIES = ['anderson','campbell','claiborne','cumberland','fentress','morgan_tn',
               'overton','pickett','putnam_tn','roane',]
KY_COUNTIES = ['bell','boyd','breathitt','carter','clay_ky','clinton','elliott',
               'estill','floyd','greenup','harlan','jackson','johnson','knott','knox',
               'laurel','lawrence','lee_ky','leslie','letcher','lewis','magoffin', 
               'martin','mccreary','menifee','morgan_ky','owsley','perry','pike',
               'powell','pulaski','rockcastle','rowan','wayne_ky','whitley','wolfe']
VA_COUNTIES = ['buchanan', 'dickenson', 'lee', 'russell', 'scott', 'tazewell', 'wise']

MISSING_TILES = ['17SMC20005100', '17SMC20005250', '17SMC20005400', '17SMC20005850', '17SMC18505850',
                 '17SMC17005850', '17SMC17006000', '17SMC17006150', '17SMC15506150', '17SMC14006150',
                 '17SMC12506150', '17SMC11006150', '17SMC11006450', '17SMC09506450', '17SMC06506600',
                 '17SMC08006600', '17SMC08006750', '17SMC08006900', '17SMC08007200', '17SMC08007350',
                 '17SMC08007500', '17SMC09507500', '17SMC09507350', '17SMC11007500']


