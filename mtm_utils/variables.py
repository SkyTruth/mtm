import datetime
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, INTEGER, TEXT, FLOAT, DATE


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
FIPS_CODES = [
    21013,
    21019,
    21025,
    21043,
    21051,
    21053,
    21063,
    21065,
    21071,
    21089,
    21095,
    21109,
    21115,
    21119,
    21121,
    21125,
    21127,
    21129,
    21131,
    21133,
    21135,
    21147,
    21153,
    21159,
    21165,
    21175,
    21189,
    21193,
    21195,
    21197,
    21199,
    21203,
    21205,
    21231,
    21235,
    21237,
    47001,
    47013,
    47025,
    47035,
    47049,
    47129,
    47133,
    47137,
    47141,
    47145,
    47151,
    51027,
    51051,
    51105,
    51167,
    51169,
    51185,
    51195,
    51720,
    54005,
    54011,
    54015,
    54019,
    54025,
    54039,
    54043,
    54045,
    54047,
    54053,
    54055,
    54059,
    54067,
    54075,
    54079,
    54081,
    54089,
    54099,
    54101,
    54109,
]


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


"""
Highwall Detection Variables
"""

# Set up directories and filenames for storing temp and output files
HW_DATA_DIR = DATA_DIR + "highwalls/"
HW_INPUT_DIR = HW_DATA_DIR + "inputs/"
HW_TEMP_DIR = HW_DATA_DIR + "temps/"
HW_OUTPUT_DIR = HW_DATA_DIR + "outputs/"

INPUT_HIGHWALLS_TESTING = HW_INPUT_DIR + "testing_subset_highwalls.shp"
INPUT_HIGHWALLS_FULL = HW_INPUT_DIR + "highwalls_1m.shp"
TEMP_CLEANED_HIGHWALLS = HW_TEMP_DIR + "cleaned_highwalls.shp"
TEMP_CENTERLINE_BRANCHES = HW_TEMP_DIR + "centerline_branches.shp"
OUTPUT_CENTERLINE_SEGMENTS = HW_OUTPUT_DIR + "centerline_segments.shp"

# Define variables for processing
MIN_AREA = 100
INTERP_DISTANCE = 4
MIN_SPUR_LENGTH = 10
MIN_BRANCH_LENGTH = 20
TARGET_SEGMENT_LENGTH = 100
MAX_SEGMENT_LENGTH = 150
MIN_SEGMENT_LENGTH = 50

"""
SQL Database Variables
"""

# Define the dtype format dictionaries for appending dataframes to sql.
annual_mining_format_dict = {
    "id": TEXT(),
    "mining_year": INTEGER(),
    "area": DOUBLE_PRECISION(),
    "data_status": TEXT(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

highwall_centerline_format_dict = {
    "id": TEXT(),
    "detect_length": FLOAT(),
    "geom": Geometry("MultiLineString", srid=4326),
}

counties_format_dict = {
    "statefp": INTEGER(),
    "countyfp": INTEGER(),
    "countyns": INTEGER(),
    "geoid": INTEGER(),
    "geoidfq": TEXT(),
    "name": TEXT(),
    "namelsad": TEXT(),
    "lsad": INTEGER(),
    "classfp": TEXT(),
    "mtfcc": TEXT(),
    "csafp": INTEGER(),
    "cbsafp": INTEGER(),
    "metdivfp": INTEGER(),
    "funcstat": TEXT(),
    "aland": DOUBLE_PRECISION(),
    "awater": DOUBLE_PRECISION(),
    "intptlat": DOUBLE_PRECISION(),
    "intptlon": DOUBLE_PRECISION(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

wv_permit_format_dict = {
    "permit_id": TEXT(),
    "mapdate": DATE(),
    "maptype": TEXT(),
    "active_vio": INTEGER(),
    "total_vio": INTEGER(),
    "facility_n": TEXT(),
    "acres_orig": DOUBLE_PRECISION(),
    "acres_curr": DOUBLE_PRECISION(),
    "acres_dist": DOUBLE_PRECISION(),
    "acres_recl": DOUBLE_PRECISION(),
    "mstatus": TEXT(),
    "mdate": DATE(),
    "issue_date": DATE(),
    "expire_dat": DATE(),
    "permittee": TEXT(),
    "operator": TEXT(),
    "last_updat": DATE(),
    "comments": TEXT(),
    "pstatus": TEXT(),
    "ma_area": TEXT(),
    "ma_contour": TEXT(),
    "ma_mtntop": TEXT(),
    "ma_steepsl": TEXT(),
    "ma_auger": TEXT(),
    "ma_roompil": TEXT(),
    "ma_longwal": TEXT(),
    "ma_refuse": TEXT(),
    "ma_loadout": TEXT(),
    "ma_preppla": TEXT(),
    "ma_haulroa": TEXT(),
    "ma_rockfil": TEXT(),
    "ma_impound": TEXT(),
    "ma_tipple": TEXT(),
    "pmlu1": TEXT(),
    "pmlu2": TEXT(),
    "weblink1": TEXT(),
    "st_area_sh": FLOAT(),
    "st_length_": FLOAT(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

huc_format_dict = {
    "objectid": INTEGER(),
    "tnmid": TEXT(),
    "metasourceid": TEXT(),
    "sourcedatadesc": TEXT(),
    "sourceoriginator": TEXT(),
    "sourcefeatureid": TEXT(),
    "loaddate": DATE(),
    "referencegnis_ids": TEXT(),
    "areaacres": DOUBLE_PRECISION(),
    "areasqkm": DOUBLE_PRECISION(),
    "states": TEXT(),
    "huc10": TEXT(),
    "name": TEXT(),
    "hutype": TEXT(),
    "humod": TEXT(),
    "globalid": TEXT(),
    "shape_Length": DOUBLE_PRECISION(),
    "shape_Area": DOUBLE_PRECISION(),
    "hutype_description": TEXT,
    "huc12": TEXT(),
    "tohuc": TEXT(),
    "noncontributingareaacres": DOUBLE_PRECISION(),
    "noncontributingareasqkm": DOUBLE_PRECISION(),
    "huc2": TEXT(),
    "huc4": TEXT(),
    "huc6": TEXT(),
    "huc8": TEXT(),
    "geom": Geometry("Point", srid=4326),
}

eamlis_format_dict = {
    "objectid": INTEGER(),
    "amlis_key": TEXT(),
    "state_key": TEXT(),
    "pa_number": TEXT(),
    "pa_name": TEXT(),
    "pu_number": TEXT(),
    "pu_name": TEXT(),
    "est_latitu": DOUBLE_PRECISION(),
    "est_longit": DOUBLE_PRECISION(),
    "lat_deg": INTEGER(),
    "lat_min": INTEGER(),
    "lon_deg": INTEGER(),
    "lon_min": INTEGER(),
    "county": TEXT(),
    "fips_code": TEXT(),
    "cong_dist": INTEGER(),
    "quad_name": TEXT(),
    "huc_code": INTEGER(),
    "watershed": TEXT(),
    "mine_type": TEXT(),
    "ore_types": TEXT(),
    "owner_priv": DOUBLE_PRECISION(),
    "owner_stat": DOUBLE_PRECISION(),
    "owner_indi": DOUBLE_PRECISION(),
    "owner_blm": DOUBLE_PRECISION(),
    "owner_fore": DOUBLE_PRECISION(),
    "owner_nati": DOUBLE_PRECISION(),
    "owner_othe": DOUBLE_PRECISION(),
    "population": TEXT(),
    "date_prepa": DATE(),
    "date_revis": DATE(),
    "priority": TEXT(),
    "prob_ty_cd": TEXT(),
    "prob_ty_na": TEXT(),
    "program": TEXT(),
    "unfd_units": TEXT(),
    "unfd_meter": TEXT(),
    "unfd_cost": TEXT(),
    "unfd_gpra": TEXT(),
    "fund_units": TEXT(),
    "fund_meter": TEXT(),
    "fund_cost": TEXT(),
    "fund_gpra": TEXT(),
    "comp_units": TEXT(),
    "comp_meter": TEXT(),
    "comp_cost": TEXT(),
    "comp_gpra": TEXT(),
    "total_unit": TEXT(),
    "total_cost": TEXT(),
    "x": DOUBLE_PRECISION(),
    "y": DOUBLE_PRECISION(),
    "geom": Geometry("MultiPolygon", srid=4326),
}