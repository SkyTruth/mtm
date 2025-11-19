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
# The path to the most recent set of annual MTM detections
annual_mining_input_directory = "Users/USER_NAME/PATH/TO/MINING/YEARLY/GEOJSON/FILES/"

# Define the dtype format dictionaries for appending dataframes to sql.
annual_mining_format_dict = {
    "id": TEXT(),
    "mining_year": INTEGER(),
    "area": DOUBLE_PRECISION(),
    "data_status": TEXT(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

highwall_detection_format_dict = {
    "highwall_id": INTEGER(),
    "rec_status": TEXT(),
    "rec_status_yr": INTEGER(),
    "earliest_vis_yr": INTEGER(),
    "first_mined_yr": INTEGER(),
    "last_mined_yr": INTEGER(),
    "max_age": INTEGER(),
    "min_age": INTEGER(),
    "mid_age": DOUBLE_PRECISION(),
    "age_uncertainty": DOUBLE_PRECISION(),
    "lidar_project": TEXT(),
    "lidar_yr": INTEGER(),
    "mean_slope": DOUBLE_PRECISION(),
    "med_slope": DOUBLE_PRECISION(),
    "max_slope": DOUBLE_PRECISION(),
    "all_permit_ids": TEXT(),
    "segment_id": INTEGER(),
    "raw_length": DOUBLE_PRECISION(),
    "length": DOUBLE_PRECISION(),
    "base_elevation": DOUBLE_PRECISION(),
    "top_elevation": DOUBLE_PRECISION(),
    "height": DOUBLE_PRECISION(),
    "min_cost": DOUBLE_PRECISION(),
    "mid_cost": DOUBLE_PRECISION(),
    "max_cost": DOUBLE_PRECISION(),
    "permit_id": TEXT(),
    "state": TEXT(),
    "permittee": TEXT(),
    "mine_name": TEXT(),
    "mine_status": TEXT(),
    "bond_status": TEXT(),
    "avail_bond": DOUBLE_PRECISION(),
    "full_bond": DOUBLE_PRECISION(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

counties_format_dict = {
    "geoid": INTEGER(),
    "statefp": INTEGER(),
    "countyfp": INTEGER(),
    "countyns": INTEGER(),
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
    "access_date": TEXT(),
}

huc_format_dict = {
    "st_id": TEXT(),
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
    "shape_length": DOUBLE_PRECISION(),
    "shape_area": DOUBLE_PRECISION(),
    "hutype_description": TEXT,
    "huc12": TEXT(),
    "tohuc": TEXT(),
    "noncontributingareaacres": DOUBLE_PRECISION(),
    "noncontributingareasqkm": DOUBLE_PRECISION(),
    "huc2": TEXT(),
    "huc4": TEXT(),
    "huc6": TEXT(),
    "huc8": TEXT(),
    "geom": Geometry("MultiPolygon", srid=4326),
    "access_date": TEXT(),
}

eamlis_format_dict = {
    "objectid": INTEGER(),
    "amlis_key": TEXT(),
    "state_key": TEXT(),
    "pa_number": TEXT(),
    "pa_name": TEXT(),
    "pu_number": TEXT(),
    "pu_name": TEXT(),
    "est_latitude": DOUBLE_PRECISION(),
    "est_longitude": DOUBLE_PRECISION(),
    "lat_deg": INTEGER(),
    "lat_min": INTEGER(),
    "lon_deg": INTEGER(),
    "lon_min": INTEGER(),
    "county": TEXT(),
    "fips_code": TEXT(),
    "cong_dist": DOUBLE_PRECISION(),
    "quad_name": TEXT(),
    "huc_code": DOUBLE_PRECISION(),
    "watershed": TEXT(),
    "mine_type": TEXT(),
    "ore_types": TEXT(),
    "owner_private": DOUBLE_PRECISION(),
    "owner_state": DOUBLE_PRECISION(),
    "owner_indian": DOUBLE_PRECISION(),
    "owner_blm": DOUBLE_PRECISION(),
    "owner_forest": DOUBLE_PRECISION(),
    "owner_national": DOUBLE_PRECISION(),
    "owner_other": DOUBLE_PRECISION(),
    "population": TEXT(),
    "date_prepared": DATE(),
    "date_revised": DATE(),
    "priority": TEXT(),
    "prob_ty_cd": TEXT(),
    "prob_ty_name": TEXT(),
    "program": TEXT(),
    "unfd_units": TEXT(),
    "unfd_meters": TEXT(),
    "unfd_cost": TEXT(),
    "unfd_gpra": TEXT(),
    "fund_units": TEXT(),
    "fund_meters": TEXT(),
    "fund_cost": TEXT(),
    "fund_gpra": TEXT(),
    "comp_units": TEXT(),
    "comp_meters": TEXT(),
    "comp_cost": TEXT(),
    "comp_gpra": TEXT(),
    "total_units": TEXT(),
    "total_cost": TEXT(),
    "x": DOUBLE_PRECISION(),
    "y": DOUBLE_PRECISION(),
    "geom": Geometry("Point", srid=4326),
    "access_date": TEXT(),
}

ky_permit_format_dict = {
    "st_id": TEXT(),
    "permit_id": TEXT(),
    "feat_cls": TEXT(),
    "source": TEXT(),
    "type_flag": TEXT(),
    "acres": DOUBLE_PRECISION(),
    "quadrangle": TEXT(),
    "status_code1": TEXT(),
    "permittee1": TEXT(),
    "region": TEXT(),
    "activity": TEXT(),
    "act_rel": TEXT(),
    "issue_date": DATE(),
    "orig_id": TEXT(),
    "national_id": TEXT(),
    "shape_length": DOUBLE_PRECISION(),
    "per_type": TEXT(),
    "shape_area": DOUBLE_PRECISION(),
    "permittee2": TEXT(),
    "status_code2": TEXT(),
    "status_desc": TEXT(),
    "inspectable": TEXT(),
    "curr_bond": DOUBLE_PRECISION(),
    "orig_bond": DOUBLE_PRECISION(),
    "highwall_total": INTEGER(),
    "highwall_comp": INTEGER(),
    "highwall_viol": INTEGER(),
    "permittee3": TEXT(),
    "mine_name": TEXT(),
    "post_smcra": INTEGER(),
    "op_status": TEXT(),
    "gm_bond_status": TEXT(),
    "prep_ref": TEXT(),
    "avail_bond": DOUBLE_PRECISION(),
    "full_bond": DOUBLE_PRECISION(),
    "permittee": TEXT(),
    "mine_status": TEXT(),
    "bond_status": TEXT(),
    "surf_mine": INTEGER(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

wv_permit_format_dict = {
    "st_id": TEXT(),
    "permit_id": TEXT(),
    "map_date": DATE(),
    "map_type": TEXT(),
    "active_vio": INTEGER(),
    "total_vio": INTEGER(),
    "mine_name": TEXT(),
    "acres_orig": DOUBLE_PRECISION(),
    "acres_curr": DOUBLE_PRECISION(),
    "acres_dist": DOUBLE_PRECISION(),
    "acres_recl": DOUBLE_PRECISION(),
    "mstatus": TEXT(),
    "mdate": DATE(),
    "issue_date": DATE(),
    "expir_date": DATE(),
    "permittee": TEXT(),
    "operator": TEXT(),
    "last_update": DATE(),
    "comments": TEXT(),
    "pstatus": TEXT(),
    "area": TEXT(),
    "contour": TEXT(),
    "mtntop": TEXT(),
    "steepslope": TEXT(),
    "auger": TEXT(),
    "room_pillar": TEXT(),
    "longwall": TEXT(),
    "refuse": TEXT(),
    "loadout": TEXT(),
    "prep_plant": TEXT(),
    "haul_road": TEXT(),
    "rockfill": TEXT(),
    "impoundment": TEXT(),
    "tipple": TEXT(),
    "pmlu1": TEXT(),
    "pmlu2": TEXT(),
    "weblink": TEXT(),
    "st_area": DOUBLE_PRECISION(),
    "st_length": DOUBLE_PRECISION(),
    "status_desc": TEXT(),
    "permit_status": TEXT(),
    "bond_amount": DOUBLE_PRECISION(),
    "type": TEXT(),
    "current_status": TEXT(),
    "post_smcra": TEXT(),
    "op_status": TEXT(),
    "gm_bond_status": TEXT(),
    "prep_ref": TEXT(),
    "avail_bond": DOUBLE_PRECISION(),
    "full_bond": DOUBLE_PRECISION(),
    "mine_status": TEXT(),
    "bond_status": TEXT(),
    "surf_mine": INTEGER(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

va_permit_format_dict = {
    "st_id": TEXT(),
    "permit_id": TEXT(),
    "permittee": TEXT(),
    "release_date": DATE(),
    "trans_from": TEXT(),
    "comment": TEXT(),
    "acres": DOUBLE_PRECISION(),
    "permit_type": TEXT(),
    "global_id": TEXT(),
    "created_user": TEXT(),
    "created_date": DATE(),
    "last_edit_user": TEXT(),
    "last_edit_date": DATE(),
    "st_area": DOUBLE_PRECISION(),
    "st_length": DOUBLE_PRECISION(),
    "bond_code": TEXT(),
    "app_no": TEXT(),
    "permittee_code": TEXT(),
    "operation": TEXT(),
    "county": TEXT(),
    "seams": TEXT(),
    "quads": TEXT(),
    "mine_types": TEXT(),
    "permit_status": TEXT(),
    "permit_status_date": DATE(),
    "orig_issue": DATE(),
    "anniversary": DATE(),
    "bond_type": TEXT(),
    "remining": TEXT(),
    "remining_acres": DOUBLE_PRECISION(),
    "underground": TEXT(),
    "mtntop": TEXT(),
    "steepslope": TEXT(),
    "auger": TEXT(),
    "non_aoc": TEXT(),
    "tbl_os_code": TEXT(),
    "tbl_os_desc": TEXT(),
    "pe_os_date": DATE(),
    "rec_status": TEXT(),
    "layer": TEXT(),
    "gm_mine_name": TEXT(),
    "post_smcra": INTEGER(),
    "op_status": TEXT(),
    "gm_bond_status": TEXT(),
    "app_date": DATE(),
    "prep_ref": TEXT(),
    "bond_method": TEXT(),
    "permitted_acres": DOUBLE_PRECISION(),
    "bonded_acres": DOUBLE_PRECISION(),
    "bond_amount": DOUBLE_PRECISION(),
    "mine_name": TEXT(),
    "mine_status": TEXT(),
    "bond_status": TEXT(),
    "issue_date": DATE(),
    "surf_mine": INTEGER(),
    "full_bond": DOUBLE_PRECISION(),
    "avail_bond": DOUBLE_PRECISION(),
    "geom": Geometry("MultiPolygon", srid=4326),
}

tn_permit_format_dict = {
    "st_id": TEXT(),
    "permittee": TEXT(),
    "op_status": TEXT(),
    "mine_name": TEXT(),
    "permit_id": TEXT(),
    "msha_id": TEXT(),
    "national_id": TEXT(),
    "coal_beds": TEXT(),
    "inspectable": INTEGER(),
    "post_smcra": INTEGER(),
    "acres": DOUBLE_PRECISION(),
    "issue_date": DATE(),
    "edit_date": DATE(),
    "area": INTEGER(),
    "contour": INTEGER(),
    "mtntop": INTEGER(),
    "steepslope": INTEGER(),
    "highwall": INTEGER(),
    "auger": INTEGER(),
    "comment": TEXT(),
    "contact": INTEGER(),
    "info": TEXT(),
    "bond_type": TEXT(),
    "status": TEXT(),
    "bond_amount": DOUBLE_PRECISION(),
    "land_req_bond": DOUBLE_PRECISION(),
    "water_req_bond": DOUBLE_PRECISION(),
    "total_req_bond": DOUBLE_PRECISION(),
    "shortfall": DOUBLE_PRECISION(),
    "notes": TEXT(),
    "prep_ref": TEXT(),
    "gm_bond_status": TEXT(),
    "mine_status": TEXT(),
    "bond_status": TEXT(),
    "surf_mine": INTEGER(),
    "full_bond": DOUBLE_PRECISION(),
    "avail_bond": DOUBLE_PRECISION(),
    "geom": Geometry("MultiPolygon", srid=4326),
}