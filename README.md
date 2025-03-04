# Moutaintop Removal Mining
This repository contains code, data, and documentation for SkyTruth's Mountaintop Removal Mining (MTM) related work. 

## Repository Layout
Directories:
    - **MTM2009_Archive** : Data and documentaion related to the 2009 SkyTruth Decadal mine detection model
    - **MTM2018_Archive** : Code, data, and documentaion related to the 2018 paper ["Mapping the yearly extent of surface coal mining in Central Appalachia using Landsat and Google Earth Engine"](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197758), published in PLOS One, which identified mines at annual intervals from 1985 - 2015.
    - **MTM_Annual_Mining** : Code, data, and documentaion related to the current version of SkyTruth's Annual mine detection model; which is run annually and has been updated from the code in MTM2018_Archive
    - **CAMRA** : Code, data, and documentation related to the [Central Appalachian Mine Reforestation Assessment Tool](https://appvoices.org/reports/central-appalachian-mine-reforestation-assessment-tool/)
    - **Post-mining_Recovery** : Code, data, and documentation related to the 2022 paoer ["Mines to forests? Analyzing long-term recovery trends for surface coal mines in Central Appalachia"](https://onlinelibrary.wiley.com/doi/abs/10.1111/rec.13827), published in Restoration Ecology
    - **Highwall_Detection** : Code, data, and documentation related to detecting highwall mining operations
    - **data** : key datasets utilized across MTM projects
    - **utils** : General purpose code which is project agnostic 


# Working in this repo:
  - This repo is primarily Python-based, so ensure you have python set up. if not, follow the [Python setup](#python-setup) instructions.
    - There are some Javascript codes included, written using the [Google Earth Engine Code Editor](https://code.earthengine.google.com/), and intended to be run in the same.
  - This repo is set up with [Poetry](https://python-poetry.org/). Learn how to set up and use Poetry in [this](#poetry) section, which mainly re-format data.
  - We use Google Cloud Platform resources (Google Cloud Storage) in this repo. Instructions on getting set up are [here](#google-cloud-platform-gcp)
  - In this repo we use [pre-commit-hooks](#pre-commit-hooks)
  - Git/GitHub instructions are found in this [repo](https://github.com/SkyTruth/github_practice)


# Python Setup
- Python should come built in on Mac, but you can also get it from the Python downloads page. These instructions are only for Windows though.
- Install the latest stable Python version (if you do not already have it)
  - Download and install from [Python](https://www.python.org/downloads/)
- Add the Python path to your environment variables (be sure to update YourUsername and the correct python version [in this example, the version is Python3.9]) by running the following in Powershell:
```shell
$env:Path += ";C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python39\"
```
- Test that python is set up correctly. First restart your Powershell and then run:
```shell
py --version
```

# License
This work is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). See LICENSE.txt


We are using Google's `Earth Engine <https://earthengine.google.com/>`_ to identify active MTR mines on Landsat Satellite Imagery using a Normalized Differenced Vegetation Index (NDVI) threshold. To eliminate locations with NDVI reflectance values similar to mine sites a mask was created to block roads, rivers and streams, and urban areas from the analysis. Earth Engine is a cloud-based geospatial computing platform which we are utilizing to automate the process of mine identification.
 