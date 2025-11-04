# Note
All code should be run from the `mtm/` directory

# Getting Started
1. Run the following code to connect to the cloud-sql-proxy
```shell
./cloud-sql-proxy --port NNNN --address NNN.N.N.N skytruth-tech:us-central1:mining-sb &
```
2. Check the connection
```shell
jobs
```

# Prepare the database
This will ensure the postgis extension is enabled
```shell
poetry run python database/prepare_db.py
```

# Creating Tables
This will create all tables, if they do not already exist.
```shell
poetry run python database/make_tables.py
```

# Append data to tables
This code is currently only able to write data from local files, or a GCS file path to an existing, annual mining table.
```shell
poetry run python database/append_tables.py
```

# API Guide
This colab notebook: [MTM Test API Guide v2.ipynb](https://colab.research.google.com/drive/1eWf8Fsr_-NgXM_YyI-WSHIWejfhToXDp#scrollTo=381wUU-Na6WM) provides examples of how to interact with the API.
