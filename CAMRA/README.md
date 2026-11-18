# Note
Code for the project was originally written as ipython notebooks, these are preserved in CAMRA/Archive. Some changes have been made to adapt the codes to .py files

1. run sr_annualLastMinedMetrics.py
```shell
uv run python CAMRA/sr_annualLastMinedMetrics.py
```

2. Run ARM_calculation.py
```shell
uv run python CAMRA/ARM_calculation.py --file_type geojson --to_gcs True --clean_tmp True
```