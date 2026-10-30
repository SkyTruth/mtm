# Moutaintop Removal Mining
This repository contains code, data, and documentation for SkyTruth's Mountaintop Removal Mining (MTM) related work. 

This project is primarily Python based, and uses [uv](https://docs.astral.sh/uv/) as its default Python environment manager. The checked-in environment contract is `pyproject.toml`, `uv.lock`, and `.python-version`. There are some Javascript codes included, written using the [Google Earth Engine Code Editor](https://code.earthengine.google.com/), and intended to be run in the same. 

The repo also uses Google Cloud Platform resources (Google Cloud Storage) in this repo. Instructions on getting set up are [here](#google-cloud-platform-gcp).

There are a variety of sub-projects under the broader MTM program, each project has a separate directory which contains the documentation relevant to that work. Projects are outlined broadly in [Repository Layout](#repository-layout), below, please see specific ReadMe files in each directory for additional information

## Repository Directories
- **MTM2009_Archive** : Data and documentaion related to the 2009 SkyTruth Decadal mine detection model
- **MTM2018_Archive** : Code, data, and documentaion related to the 2018 paper ["Mapping the yearly extent of surface coal mining in Central Appalachia using Landsat and Google Earth Engine"](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197758), published in PLOS One, which identified mines at annual intervals from 1985 - 2015.
- **MTM_Annual_Mining** : Code, data, and documentaion related to the current version of SkyTruth's Annual mine detection model; which is run annually and has been updated from the code in MTM2018_Archive
- **CAMRA** : Code, data, and documentation related to the [Central Appalachian Mine Reforestation Assessment Tool](https://appvoices.org/reports/central-appalachian-mine-reforestation-assessment-tool/)
- **Highwall_Detection** : Code, data, and documentation related to highwall detection model
- **Post-mining_Recovery** : Code, data, and documentation related to the 2022 paoer ["Mines to forests? Analyzing long-term recovery trends for surface coal mines in Central Appalachia"](https://onlinelibrary.wiley.com/doi/abs/10.1111/rec.13827), published in Restoration Ecology
- **data** : key datasets utilized across MTM projects
- **utils** : General purpose code which is project agnostic 


# uv: Installation and Set-up
`uv` downloads the Python version used by this repo (and pins it in `.python-version`) the first time you sync.

## Mac / Linux
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), either with Homebrew:
  ```shell
  brew install uv
  ```
  or with the standalone installer:
  ```shell
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
## Windows
1. Install uv by running the following in PowerShell:
  ```shell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
2. Restart PowerShell and check that it worked:
  ```shell
  uv --version
  ```

## Using uv
### Working in the uv environment
This repo has a `pyproject.toml` and a `uv.lock` file. These define the virtual environment. uv creates the environment in a `.venv` folder at the root of the repo.

To work in the uv virtual environment, prepend all command line statements with uv run (i.e. instead of `python hello_world.py` you would run `uv run python hello_world.py`). `uv run` also installs anything that is missing or out of date before running.

Alternatively, you can work entirely in the environment (similar to `conda activate`) by activating it with `source .venv/bin/activate` (Mac / Linux) or `.venv\Scripts\activate` (Windows), and then you can just run `python hello_world.py`

### Install environment
Do this each time you pull the repo in case there have been changes to the lockfile:
```shell
uv sync
```
  - `uv sync` installs the exact versions listed in `uv.lock` (and Python itself, if needed)
  - You only need `uv lock` if you edit `pyproject.toml` by hand; `uv add` and `uv remove` update the lockfile for you

### Updating the environment
Adding a new library:
  ```shell
  uv add <new-package>
  ```
Deleting a library
  ```shell
  uv remove <old-package>
  ```

# License
This work is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). See LICENSE.txt