import click
import ee
import geopandas as gpd
import pandas as pd
import os
from google.cloud import storage

from config import EE_SERVICE_ACCOUNT, EE_CREDENTIALS
from mtm_utils.variables import GCLOUD_BUCKET, GCLOUD_CAMRA_CSV, GCLOUD_CAMRA_GJS, GCLOUD_CAMRA_ARM, TEMP_DIR

"""
This code is a .py equivalent of the original codes found at CAMRA/Archive/

This script was created by Christian Thomas at SkyTruth to calculate the Aggregated Recovery Metric (ARM), which is
calculated with the following formula:
        ARM = ((((NDVI + NBR) / 2) + NDMI) / 2)

The script processes the outputs of CAMRA/sr_annualLastMinedMetrics.py

If you encounter issues please contact christian@skytruth.org.
"""

# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
credentials = ee.ServiceAccountCredentials(EE_SERVICE_ACCOUNT, EE_CREDENTIALS)

YEARS = list(range(1984, 2020))
BANDS = ['B', 'EVI', 'G', 'MSAVI', 'NBR2', 'NBR', 'NDMI', 'NDVI', 'NIR', 'R', 'SAVI', 'SWIR1', 'SWIR2']

base_order = [f"{b}_{y}" for b in BANDS for y in YEARS]
cOrder = base_order + ['sum', 'sum_rnd', 'km2_rnd', 'US_L4CODE', 'lastMined', 'ID', 'geometry']
eOrder = base_order + ['US_L4CODE', 'ID', 'geometry']
cOrder2 = base_order + [f"arm_{y}" for y in YEARS] + ['sum', 'sum_rnd', 'km2_rnd', 'US_L4CODE', 'lastMined', 'ID', 'geometry']


def tmp_download(file_type: str):
    """
    Download the data to a temp dir for processing, delete after final upload
    """
    os.makedirs(TEMP_DIR, exist_ok=True)

    if file_type == "csv":
        for f in storage_client.list_blobs(bucket_name, prefix=GCLOUD_CAMRA_CSV):
            fName = f.name
            outfile_name = "TMP_"+fName.split("csv/")[1]
            outfile_path = TEMP_DIR + outfile_name
            
            # Check if the file already exists before downloading
            if not os.path.exists(outfile_path):
                print(f"  > Downloading {f.name} to\n    --> {outfile_name}\n")
                blob = storage_bucket.blob(f.name)
                blob.download_to_filename(outfile_path)
            else:
                print(f"  > Skipping {outfile_name} (already exists)\n")
    
    else:
        for f in storage_client.list_blobs(bucket_name, prefix=GCLOUD_CAMRA_GJS):
            fName = f.name
            outfile_name = "TMP_"+fName.split("geojson/")[1]
            outfile_path = TEMP_DIR + outfile_name
            
            # Check if the file already exists before downloading
            if not os.path.exists(outfile_path):
                print(f"  > Downloading {f.name} to\n    --> {outfile_name}\n")
                blob = storage_bucket.blob(f.name)
                blob.download_to_filename(outfile_path)
            else:
                print(f"  > Skipping {outfile_name} (already exists)\n")


def arm_processing():
    """
    Calculate ARM for Mine Sites
    """
    print("Processing ARM data...")

    er = gpd.read_file("data/ecoregions/geojson/EPA_Ecoregions_level_4.geojson")
    epa_df = gpd.read_file(TEMP_DIR+"TMP_2025-03-07_epaEcoregionSite_srHarmonizedMed_metricProcessed.geojson")
    mine_df = gpd.read_file(TEMP_DIR+"TMP_2025-03-07_lastMined_srHarmonizedMed_metricProcessed.geojson")

    # Add Level 4 Ecoregion data tp mine_df based on intersection
    mine_df = gpd.overlay(mine_df, er[['geometry', 'US_L4CODE']], how="intersection")

    # Clean-up
    epa_df = epa_df.drop(['id'], axis=1, errors='ignore')
    mine_df = mine_df.drop(['id'], axis=1, errors='ignore')
    epa_df['US_L4CODE'] = epa_df.ECOREGION

    # Create a column with the values from 'sum' rounded to 2 decimal places ('sum_rnd'), create a column which converts the
    # 'sum_rnd' to kilometers called 'km2_rnd', if it doesn't already exist
    mine_df = mine_df.assign(sum_rnd=round(mine_df['sum'], 2))
    mine_df = mine_df.assign(km2_rnd=mine_df['sum_rnd'] / 1000000)

    # Ensure Band Columns are in the correct order
    mine_df = mine_df.reindex(columns=cOrder)
    epa_df = epa_df.reindex(columns=eOrder)

    """
    ARM CALCULATION
    Note:   If your file is processed or ordered differntly, the values in the BAND_DICT may not work.
    """

    BAND_DICT = {
        'BLUE':  {'titleName': 'BLUE', 'year': YEARS, 'start': 0, 'end': 36},
        'EVI':   {'titleName': 'EVI', 'year': YEARS, 'start': 36, 'end': 72},
        'GREEN': {'titleName': 'GREEN', 'year': YEARS, 'start': 72, 'end': 108},
        'MSAVI': {'titleName': 'MSAVI', 'year': YEARS, 'start': 108, 'end': 144}, 
        'NBR2':  {'titleName': 'NBR2', 'year': YEARS, 'start': 144, 'end': 180},
        'NBR':   {'titleName': 'NBR', 'year': YEARS, 'start': 180, 'end': 216},
        'NDMI':  {'titleName': 'NDMI', 'year': YEARS, 'start': 216, 'end': 252},
        'NDVI':  {'titleName': 'NDVI', 'year': YEARS, 'start': 252, 'end': 288},
        'NIR':   {'titleName': 'NIR', 'year': YEARS, 'start': 288, 'end': 324},
        'RED':   {'titleName': 'RED', 'year': YEARS, 'start': 324, 'end': 360},
        'SAVI':  {'titleName': 'SAVI', 'year': YEARS, 'start': 360, 'end': 396},
        'SWIR1': {'titleName': 'SWIR1', 'year': YEARS, 'start': 396, 'end': 432},
        'SWIR2': {'titleName': 'SWIR2', 'year': YEARS, 'start': 432, 'end': 468}
    }

    # Set Input Dataframes
    arm_input_df = pd.DataFrame(mine_df)
    epaER_dF = pd.DataFrame(epa_df)

    # The Aggregated Recovery Metric (ARM) is calculated: ( ( ( ( NDVI + NBR ) / 2) + NDMI ) / 2 )
    band1 = 'NDVI'
    band2 = 'NBR'
    band3 = 'NDMI'
    band1_input = BAND_DICT[band1]
    band2_input = BAND_DICT[band2]
    band3_input = BAND_DICT[band3]
    col_start1 = band1_input['start']
    col_start2 = band2_input['start']
    col_start3 = band3_input['start']
    col_end1 = band1_input['end']
    col_end2 = band2_input['end']
    col_end3 = band3_input['end']

    x = arm_input_df
    id_list = []
    x2 = pd.DataFrame()
    for i in range(0, len(x.ID)):
        site_id = x.ID[i]
        id_list.append(site_id)
        single_id = arm_input_df[arm_input_df.ID == site_id]
        ecoregion = single_id.US_L4CODE.values[0]
        ######################################################################################################################
        er_epa = epaER_dF[epaER_dF['US_L4CODE'] == ecoregion]
        epa_1 = er_epa[er_epa.columns[col_start1:col_end1]]
        epa_2 = er_epa[er_epa.columns[col_start2:col_end2]]
        epa_3 = er_epa[er_epa.columns[col_start3:col_end3]]
        transposed_epa_1 = epa_1.T
        transposed_epa_2 = epa_2.T
        transposed_epa_3 = epa_3.T
        epa_1_vis = []
        epa_2_vis = []
        epa_3_vis = []
        epa_1_yis = []
        epa_2_yis = []
        epa_3_yis = []

        for row in transposed_epa_1.index:
            epa_er_vegi_index = row.rsplit('_', 1)[0]
            epa_er_year_index = row.rsplit('_', 1)[1]
            epa_1_vis.append(epa_er_vegi_index)
            epa_1_yis.append(epa_er_year_index)
        for row in transposed_epa_2.index:
            epa_er_vegi_index = row.rsplit('_', 1)[0]
            epa_er_year_index = row.rsplit('_', 1)[1]
            epa_2_vis.append(epa_er_vegi_index)
            epa_2_yis.append(epa_er_year_index)
        for row in transposed_epa_3.index:
            epa_er_vegi_index = row.rsplit('_', 1)[0]
            epa_er_year_index = row.rsplit('_', 1)[1]
            epa_3_vis.append(epa_er_vegi_index)
            epa_3_yis.append(epa_er_year_index)
        
        transposed_epa_1.insert(loc=0, column='e_veg_index', value=epa_1_vis)
        transposed_epa_1.insert(loc=1, column='e_index_year', value=epa_1_yis)
        transposed_epa_2.insert(loc=0, column='e_veg_index', value=epa_2_vis)
        transposed_epa_2.insert(loc=1, column='e_index_year', value=epa_2_yis)
        transposed_epa_3.insert(loc=0, column='e_veg_index', value=epa_3_vis)
        transposed_epa_3.insert(loc=1, column='e_index_year', value=epa_3_yis)
        processed_epa_1 = transposed_epa_1.pivot(index='e_index_year', columns='e_veg_index')
        processed_epa_2 = transposed_epa_2.pivot(index='e_index_year', columns='e_veg_index')
        processed_epa_3 = transposed_epa_3.pivot(index='e_index_year', columns='e_veg_index')
        epa_1_mean = processed_epa_1.mean(axis=1)
        epa_2_mean = processed_epa_2.mean(axis=1)
        epa_3_mean = processed_epa_3.mean(axis=1)
        epa_arm_mean = ((((epa_1_mean + epa_2_mean) / 2) + epa_3_mean) / 2)
        ######################################################################################################################
        site_1 = single_id[single_id.columns[col_start1:col_end1]]
        site_2 = single_id[single_id.columns[col_start2:col_end2]]
        site_3 = single_id[single_id.columns[col_start3:col_end3]]
        transposed_site_1 = site_1.T
        transposed_site_2 = site_2.T
        transposed_site_3 = site_3.T
        site_1_vis = []
        site_2_vis = []
        site_3_vis = []
        site_1_yis = []
        site_2_yis = []
        site_3_yis = []
        for row in transposed_site_1.index:
            vegi_index = row.rsplit('_', 1)[0]
            year_index = row.rsplit('_', 1)[1]
            site_1_vis.append(vegi_index)
            site_1_yis.append(year_index)
        for row in transposed_site_2.index:
            vegi_index = row.rsplit('_', 1)[0]
            year_index = row.rsplit('_', 1)[1]
            site_2_vis.append(vegi_index)
            site_2_yis.append(year_index)
        for row in transposed_site_3.index:
            vegi_index = row.rsplit('_', 1)[0]
            year_index = row.rsplit('_', 1)[1]
            site_3_vis.append(vegi_index)
            site_3_yis.append(year_index)
        transposed_site_1.insert(loc=0, column='e_veg_index', value=site_1_vis)
        transposed_site_1.insert(loc=1, column='e_index_year', value=site_1_yis)
        transposed_site_2.insert(loc=0, column='e_veg_index', value=site_2_vis)
        transposed_site_2.insert(loc=1, column='e_index_year', value=site_2_yis)
        transposed_site_3.insert(loc=0, column='e_veg_index', value=site_3_vis)
        transposed_site_3.insert(loc=1, column='e_index_year', value=site_3_yis)
        processed_site_1 = transposed_site_1.pivot(index='e_index_year', columns='e_veg_index')
        processed_site_2 = transposed_site_2.pivot(index='e_index_year', columns='e_veg_index')
        processed_site_3 = transposed_site_3.pivot(index='e_index_year', columns='e_veg_index')
        site_1_mean = processed_site_1.mean(axis=1)
        site_2_mean = processed_site_2.mean(axis=1)
        site_3_mean = processed_site_3.mean(axis=1)
        site_arm_mean = ((((site_1_mean + site_2_mean) / 2) + site_3_mean) / 2)
        ######################################################################################################################  
        arm_recovery = site_arm_mean.divide(epa_arm_mean)

        # IF THE ARM IS NOT DIVIDED BY THE ECOREGION ARM, IT IS RAW_ARM
        arm_recovery_transposed = pd.DataFrame(arm_recovery).T
        arm_recovery_transposed.columns = ['arm_'+str(col) for col in arm_recovery_transposed.columns]
        id_arm = arm_recovery_transposed.assign(sid=site_id)
        xdf = x[['sum', 'sum_rnd', 'km2_rnd', 'ID','US_L4CODE']]

        ww = pd.merge(xdf, id_arm, left_on='ID', right_on='sid', how='left').drop('sid', axis=1)
        # x2 = x2.append(pd.DataFrame(id_arm))
        x2 = pd.concat([x2, pd.DataFrame(id_arm)], ignore_index=True)
        df = pd.concat([xdf.reset_index(drop=True), arm_recovery_transposed.reset_index(drop=True)], axis=1) # (drop=Tru‌​e)], axis=1)
        fin = pd.merge(xdf, x2, left_on='ID', right_on='sid', how='left').drop('sid', axis=1)

    
    mine_df['id'] = mine_df.ID
    joined_df = mine_df.merge(fin, left_on='id', right_on='ID', how='left')

    finalDataframe = joined_df.drop(['id', 'ID_y', 'sum_y', 'sum_rnd_y', 'km2_rnd_y', 'US_L4CODE_y'], axis=1, errors='ignore').rename(columns={'ID_x': 'ID', 'sum_x': 'sum', 'sum_rnd_x': 'sum_rnd', 'km2_rnd_x': 'km2_rnd', 'US_L4CODE_x': 'US_L4CODE'})
    finalDataframe = finalDataframe.reindex(columns=cOrder2)

    finalDataframe.to_file(TEMP_DIR+"2025-03-07_lastMined_srHarmonizedMed_rawARM.geojson", driver="GeoJSON")


def arm_upload(to_gcs: bool):
    infile_name = "2025-03-07_lastMined_srHarmonizedMed_rawARM.geojson"
    infile = TEMP_DIR + infile_name
    bucket_name = GCLOUD_BUCKET
    storage_bucket = storage.Client("skytruth-tech").bucket(bucket_name)
    
    if to_gcs == False:
        print(
            f"Not writing {infile_name} to: {GCLOUD_CAMRA_ARM + infile_name}"
        )
    else:
        out_blob = storage_bucket.blob(GCLOUD_CAMRA_ARM + infile_name)
        if out_blob.exists():
            print("  > OUTFILE ALREADY EXISTS. PASSING.")
            pass
        else:
            print("  > OUTFILE DOESN'T EXIST. UPLOADING.")
            blob = out_blob
            blob.upload_from_filename(infile, content_type="application/geojson")
            print(f"  > Outfile {infile_name} uploaded to gs://{GCLOUD_BUCKET}/{GCLOUD_CAMRA_ARM}{infile_name}")


def tmp_cleanup(clean_tmp: bool):
    if clean_tmp == True:
        print("TMP files can be fairly large, removing them...")
        files = os.listdir(TEMP_DIR)
        for file in files:
            print(f"  Removing: {file}")
            os.remove(TEMP_DIR + file) # delete all files
    else:
        print("Keeping all tmp files.")


@click.command()
@click.option(
    "--file_type",
    type=click.Choice(["csv", "geojson"], case_sensitive=False),
    help="Type of data to downloas. Choose 'csv' or 'geojson' to download. arm_processing() only processes GeoJSON files currently.",
    required=True,
    default="geojson"
)
@click.option(
    "--to_gcs",
    required=True,
    help="Specify if data will be written to GCS",
    default=False,
)
@click.option(
    "--clean_tmp",
    required=True,
    help="Specify if data in data/tmp/ will be erased after processing is done.",
    default=True,
)

def main(file_type: str, to_gcs: bool, clean_tmp: bool):
    tmp_download(file_type=file_type)
    arm_processing()
    arm_upload(to_gcs=to_gcs)
    tmp_cleanup(clean_tmp=clean_tmp)


if __name__ == "__main__":
    main()
