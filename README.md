# Moutaintop Removal Mining
This repository contains code, data, and documentation for SkyTruth's Mountaintop Removal Mining (MTM) related work. 

## Repository Directories
- **MTM2009_Archive** : Data and documentaion related to the 2009 SkyTruth Decadal mine detection model
- **MTM2018_Archive** : Code, data, and documentaion related to the 2018 paper ["Mapping the yearly extent of surface coal mining in Central Appalachia using Landsat and Google Earth Engine"](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197758), published in PLOS One, which identified mines at annual intervals from 1985 - 2015.
- **MTM_Annual_Mining** : Code, data, and documentaion related to the current version of SkyTruth's Annual mine detection model; which is run annually and has been updated from the code in MTM2018_Archive
- **CAMRA** : Code, data, and documentation related to the [Central Appalachian Mine Reforestation Assessment Tool](https://appvoices.org/reports/central-appalachian-mine-reforestation-assessment-tool/)
- **Highwall_Detection** : Code, data, and documentation related to highwall detection model
- **Post-mining_Recovery** : Code, data, and documentation related to the 2022 paoer ["Mines to forests? Analyzing long-term recovery trends for surface coal mines in Central Appalachia"](https://onlinelibrary.wiley.com/doi/abs/10.1111/rec.13827), published in Restoration Ecology
- **data** : key datasets utilized across MTM projects
- **utils** : General purpose code which is project agnostic 

# Working in this repo:
  - This repo is primarily Python-based, so ensure you have python set up. if not, follow the [Python setup](#python-setup) instructions.
    - There are some Javascript codes included, written using the [Google Earth Engine Code Editor](https://code.earthengine.google.com/), and intended to be run in the same.
  - This repo is set up with [Poetry](https://python-poetry.org/). Learn how to set up and use Poetry in [this](#poetry) section, which mainly re-format data.
  - We use Google Cloud Platform resources (Google Cloud Storage) in this repo. Instructions on getting set up are [here](#google-cloud-platform-gcp)
  - In this repo we use [pre-commit-hooks](#pre-commit-hooks)
  - Git/GitHub instructions are found in this [repo](https://github.com/SkyTruth/github_practice)
  - In this repo, each MTM related project has a separate directory which contains documentation about the project. Projects are outlined broadly in [Repository Layout](#repository-layout), please see specific ReadMe files in each directory for additional information


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

# Poetry Installation and Set-up
Note: Python needs to be installed before poetry

## Mac / Linux
1. [Install Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. After installing poetry, add the Poetry bin to PATH by adding the following line to .zshrc:
```shell
export PATH="$HOME/.local/bin:$PATH"
```
## Windows
1. Open PowerShell in Administrator mode (windows menu > Powershell > right click > Administrator)
2. Install Poetry:
  ```shell
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
  ```
- It is probably possible (and better) to add the PATH to the Poetry app to your environment somehow, but we could not figure out how to make that work so instead we set up an Alias so that we could run poetry commands

3. Set execution policy (this makes your computer slightly less secure, but if you aren't downloading potential malware via Powershell, you're alright)
  ```shell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```
4. create user profile: open $PROFILE in notepad:
  ```shell
  notepad $PROFILE
  ```
5. Add the following to that file (replace YourUsername with the correct identifier):
  ```
  Set-Alias poetry "C:\Users\<YourUsername>\AppData\Roaming\Python\Scripts\poetry.exe"
  ```

## Using Poetry
### Working in the poetry environment
This repo already has a `pyproject.toml` and a `poetry.lock` file. These define the virtual environment (sort of like how requirements.txt defines a pip environment, but these files resolve dependencies and ensure everyone has the same dependencies, since those are defined in the lockfile)

To work in the poetry virtual environment, you just need to prepend all command line statements with poetry run (i.e. instead of `python hello_world.py` you would simply run `poetry run python hello_world.py`)

Alternatively, you can work work entirely in the environment (similar to `conda activate`) with the command `poetry shell`, and then you can just run `python hello_world.py`

### Build lockfile and install environment
Do this each time you pull the repo in case there have been changes to the lockfiles:
```shell
poetry lock
poetry install
```
  - `poetry lock` builds the lockfile, which is the list of dependencies based on pyproject.toml (core dependencies)
  - `poetry install` installs those dependencies

### Updating the environment
Adding a new library:
  ```shell
  poetry add <new-package>
  ```
Deleting a library
  ```shell
  poetry remove <old-package>
  ```

# License
This work is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). See LICENSE.txt