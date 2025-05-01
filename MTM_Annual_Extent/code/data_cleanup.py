import fnmatch
import geopandas as gpd
import numpy as np
from google.cloud import storage


from mtm_utils.variables import (
    GCLOUD_BUCKET,
    GCLOUD_EE_ANNUAL_MINES_TIFF,
    GCLOUD_EE_ANNUAL_MINES_GEOJSON,
    GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF,
    GCLOUD_FINAL_DATA_GEOTIFF,
    GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE,
    GCLOUD_FINAL_DATA_GEOJSON
)


# The ID of your GCS bucket
storage_client = storage.Client()
bucket_name = GCLOUD_BUCKET
storage_bucket = storage_client.bucket(bucket_name)
print(f"STORAGE BUCKET:{storage_bucket}\n\n")


def file_copy():
    print("\nCOPYING DATA TO THE FINAL OUTPUT DIRECTORIES, REMOVING UNNEEDED COLUMNS\n")

    geojson_urls = []
    geotiff_urls = []
    cumulative_urls = []

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_ANNUAL_MINES_GEOJSON):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        geojson_urls.append(file_url)

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_ANNUAL_MINES_TIFF):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        geotiff_urls.append(file_url)

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        cumulative_urls.append(file_url)

    # Remove the first entry from the list, which corresponds to the data folder
    geojson_urls.pop(0)
    geotiff_urls.pop(0)
    cumulative_urls.pop(0)

    # Sort the data, just to be safe
    geojson = sorted(geojson_urls)
    geotiff = sorted(geotiff_urls)
    geotiff_c = sorted(cumulative_urls)

    # Check the list of files for files with the same year, but one is a PROVISIONAL file
    geojson_update_list = [s.split('_activeMining', 1)[0] for s in geojson]
    geotiff_update_list = [s.split('_activeMining', 1)[0] for s in geotiff]
    geotiff_c_update_list = [s.split('CumulativeMineArea_', 1)[0] for s in geotiff_c]

    # Check which months have multiple files, use np.unique(to get 1 record per month)
    duplicate_geojson = np.unique([x for n, x in enumerate(geojson_update_list) if x in geojson_update_list[:n]])
    duplicate_geotiff = np.unique([x for n, x in enumerate(geotiff_update_list) if x in geotiff_update_list[:n]])
    duplicate_geotiff_c = np.unique([x for n, x in enumerate(geotiff_c_update_list) if x in geotiff_c_update_list[:n]])

    # Loop through the duplicates, remove the one which has a lower count value.
    for f in range(len(duplicate_geojson)):
        str = duplicate_geojson[f]
        item = fnmatch.filter(geojson, str + "*")
        # Get the item that is PROVISIONAL out of a pair and remove it from the sorted file list
        provisional_item = item[-1]
        # Use the stable item to extract PROVISIONAL items, then remove those from the sorted file list.
        stable_item = [x for x in item if x == provisional_item]
        for i in stable_item:
            geojson.remove(i)

    for f in range(len(duplicate_geotiff)):
        str = duplicate_geotiff[f]
        item = fnmatch.filter(geotiff, str + "*")
        # Get the item that is PROVISIONAL out of a pair and remove it from the sorted file list
        provisional_item = item[-1]
        # Use the stable item to extract PROVISIONAL items, then remove those from the sorted file list.
        stable_item = [x for x in item if x == provisional_item]
        for i in stable_item:
            geotiff.remove(i)

    for year in duplicate_geotiff_c:
        items = fnmatch.filter(geotiff_c, f"CumulativeMineArea_{year}*")
        # Get the item that is PROVISIONAL out of a pair and remove it from the sorted file list
        provisional_item = next((item for item in items if "_PROVISIONAL" in item), None)
        # Use the stable item to extract PROVISIONAL items, then remove those from the sorted file list.
        if provisional_item:
            stable_item = [item for item in items if "_PROVISIONAL" not in item]
            for i in stable_item:
                geotiff_c.remove(i)

    # Move the files to the Final Directories
    for i in range(len(geojson)):
        infile = geojson[i]
        infile_name = infile.split("ANNUAL_MINE_GEOJSON/")[1]  # .strip(".geojson")

        # Check if the file exists in the Final Directory, if it does: pass. If it doesn't: write it.
        out_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOJSON + infile_name)

        if out_blob.exists():
            print("  > OUTFILE ALREADY EXISTS. PASSING.")
            pass
        else:
            print(f"  > Processing {infile}")
            source_file = storage_bucket.blob(GCLOUD_EE_ANNUAL_MINES_GEOJSON + infile_name)
            output_file = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOJSON + infile_name)
            gdf = gpd.read_file(infile)
            # Drop "count" and "label" columns
            drop_cols = ["count", "label"]
            gdf = gdf.drop(columns=[col for col in drop_cols if col in gdf.columns])
            json = gdf.to_json()
            print(f"        > Copying + Column Processing:{source_file} to :{output_file}")
            blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOJSON + infile_name)
            blob.upload_from_string(json, content_type="application/geojson")
            print(f"    > Outfile: {infile_name} written.")

    # Move the files to the Final Directories
    for i in range(len(geotiff)):
        infile = geotiff[i]
        infile_name = infile.split("ANNUAL_MINE_GEOTIFF/")[1]  # .strip(".geojson")

        # Check if the file exists in the Final Directory, if it does: pass. If it doesn't: write it.
        out_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF + infile_name)

        if out_blob.exists():
            print("  > OUTFILE ALREADY EXISTS. PASSING.")
            pass
        else:
            print(f"  > Processing {infile}")
            source_image = storage_bucket.blob(GCLOUD_EE_ANNUAL_MINES_TIFF + infile_name)
            output_image = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF + infile_name)
            print(f"        > Copying:{source_image} to :{output_image}")
            copy = storage_bucket.copy_blob(source_image, storage_bucket, GCLOUD_FINAL_DATA_GEOTIFF + infile_name)
            print(f"    > Outfile: {infile_name} written.")

    # Move the files to the Final Directories
    for i in range(len(geotiff_c)):
        infile = geotiff_c[i]
        infile_name = infile.split("CUMULATIVE_MINE_GEOTIFF/")[1]  # .strip(".geojson")

        # Check if the file exists in the Final Directory, if it does: pass. If it doesn't: write it.
        out_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE + infile_name)

        if out_blob.exists():
            print("  > OUTFILE ALREADY EXISTS. PASSING.")
            pass
        else:
            print(f"  > Processing {infile}")
            source_image = storage_bucket.blob(GCLOUD_EE_ANNUAL_MINES_CUMULATIVE_TIFF + infile_name)
            output_image = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE + infile_name)
            print(f"        > Copying:{source_image} to :{output_image}")
            copy = storage_bucket.copy_blob(source_image, storage_bucket, GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE + infile_name)
            print(f"    > Outfile: {infile_name} written.")

    print("\nFINISHED COPYING DATA TO THE FINAL OUTPUT DIRECTORIES\n")


def final_cleanup():
    print("\nBEGINNING FINAL DATA CLEANUP, REMOVING OUT-OF-DATE DATA FROM THE FINAL OUTPUT DIRECTORIES\n")
    geojson_urls = []
    geotiff_urls = []
    geotiff_urls_c = []

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_FINAL_DATA_GEOJSON):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        geojson_urls.append(file_url)

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_FINAL_DATA_GEOTIFF):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        geotiff_urls.append(file_url)

    for file in storage_client.list_blobs(bucket_name, prefix=GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE):
        file_name = file.name
        file_url = "gs://" + bucket_name + "/" + file_name
        geotiff_urls_c.append(file_url)

    # Remove the first entry from the list, which corresponds to the data folder
    geojson_urls.pop(0)
    geotiff_urls.pop(0)
    geotiff_urls_c.pop(0)

    # Sort the data, just to be safe
    geojson = sorted(geojson_urls)
    geotiff = sorted(geotiff_urls)
    geotiff_c = sorted(geotiff_urls_c)

    # Check the list of files for files with the same year, but one is a PROVISIONAL file
    geojson_update_list = [s.split('_activeMining', 1)[0] for s in geojson]
    geotiff_update_list = [s.split('_activeMining', 1)[0] for s in geotiff]
    geotiff_update_list_c = [s.split('CumulativeMineArea_', 1)[1] for s in geotiff_c]

    # Check which months have multiple files, use np.unique(to get 1 record per month)
    duplicate_geojson = np.unique([x for n, x in enumerate(geojson_update_list) if x in geojson_update_list[:n]])
    duplicate_geotiff = np.unique([x for n, x in enumerate(geotiff_update_list) if x in geotiff_update_list[:n]])

    # Remove any provisional files, if a non-provisional version of the data is available
    for f in range(len(duplicate_geojson)):
        str = duplicate_geojson[f]
        item = fnmatch.filter(geojson, str + "*")

        # Get the item that is PROVISIONAL out of a pair and remove it from the sorted file list
        provisional_item = item[-1]

        # Use the stable item to extract PROVISIONAL items, then remove those from the sorted file list.
        stable_item = [x for x in item if x != provisional_item]
        provisional_file_name = provisional_item.split("GEOJSON/")[1]  # .strip(".geojson")
        print(f"  > Provisional file: {provisional_file_name} found to have updated stable version: {stable_item}.\n  > deleting the provisonal data.")

        delete_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOJSON + provisional_file_name)
        delete_blob.delete()
        print("      > PROVISIONAL FILE DELETED")

    for f in range(len(duplicate_geotiff)):
        str = duplicate_geotiff[f]
        item = fnmatch.filter(geotiff, str + "*")

        # Get the item that is PROVISIONAL out of a pair and remove it from the sorted file list
        provisional_item = item[-1]

        # Use the stable item to extract PROVISIONAL items, then remove those from the sorted file list.
        stable_item = [x for x in item if x != provisional_item]
        provisional_file_name = provisional_item.split("GEOTIFF/")[1]  # .strip(".geojson")
        print(f"  > Provisional file: {provisional_file_name} found to have updated stable version: {stable_item}.\n  > deleting the provisonal data.")

        delete_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF + provisional_file_name)
        delete_blob.delete()
        print("      > PROVISIONAL FILE DELETED")

    # Cleaning the Cumulative Mining Data
    # Create a dictionary to group files by the first 9 characters
    cumulative_file_group = {}

    # Iterate through the file list
    for file_name in geotiff_update_list_c:
        key = file_name[:9]  # Extract the first 9 characters as the key
        if key not in cumulative_file_group:
            cumulative_file_group[key] = []  # Initialize an empty list for the key
        cumulative_file_group[key].append(file_name)

    cumulative_file_list = [group[0] for group in cumulative_file_group.values()]

    cumulative_keep_list = []
    for f in range(len(cumulative_file_list)):
        str = cumulative_file_list[f]
        item = fnmatch.filter(geotiff_c,
                              "gs://mountaintop_mining/gee_data/FINAL_DATA/GEOTIFF_CUMULATIVE/CumulativeMineArea_" + str + "*")
        cumulative_keep_list.append(item[0])

    cumulative_discard_list = [x for x in geotiff_c if x not in cumulative_keep_list]

    for i in cumulative_discard_list:
        file_name = i.split("GEOTIFF_CUMULATIVE/")[1]  # .strip(".geojson")
        print(file_name)
        delete_blob = storage_bucket.blob(GCLOUD_FINAL_DATA_GEOTIFF_CUMULATIVE + file_name)
        print(delete_blob)
        delete_blob.delete()
        print("      > PROVISIONAL FILE DELETED")

    print("\nFINAL DATA CLEANUP FINISHED, OUT-OF-DATE DATA REMOVED FROM THE FINAL OUTPUT DIRECTORIES\n")


if __name__ == "__main__":
    file_copy()