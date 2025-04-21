import os

GCLOUD_BUCKET = 'mountaintop_mining'
GCS_MOUNT = 'gcs'

CPU_CORES = 16

MAIN_DIR = os.path.abspath('gcs/lidar_data')
TILE_IDS_DIR = MAIN_DIR + '/tile_IDs'
FINAL_MOSAICS_DIR = MAIN_DIR + '/final_mosaics'

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

RASTERS = [['dsm', 'dsm_mosaic'], ['dtm', 'dtm_mosaic'], ['chm', 'chm']]

MISSING_TILES = ['17SMC20005100', '17SMC20005250', '17SMC20005400', '17SMC20005850', '17SMC18505850',
                 '17SMC17005850', '17SMC17006000', '17SMC17006150', '17SMC15506150', '17SMC14006150',
                 '17SMC12506150', '17SMC11006150', '17SMC11006450', '17SMC09506450', '17SMC06506600',
                 '17SMC08006600', '17SMC08006750', '17SMC08006900', '17SMC08007200', '17SMC08007350',
                 '17SMC08007500', '17SMC09507500', '17SMC09507350', '17SMC11007500']