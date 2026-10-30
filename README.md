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
  - This repo is primarily Python-based (Python 3.13) and is set up with [uv](https://docs.astral.sh/uv/), which installs Python for you. Learn how to set up and use uv in [this](#uv-installation-and-set-up) section.
    - There are some Javascript codes included, written using the [Google Earth Engine Code Editor](https://code.earthengine.google.com/), and intended to be run in the same.
  - We use Google Cloud Platform resources (Google Cloud Storage) in this repo. Instructions on getting set up are [here](#google-cloud-platform-gcp)
  - In this repo we use [pre-commit-hooks](#pre-commit-hooks)
  - Git/GitHub instructions are found in this [repo](https://github.com/SkyTruth/github_practice)
  - In this repo, each MTM related project has a separate directory which contains documentation about the project. Projects are outlined broadly in [Repository Layout](#repository-layout), please see specific ReadMe files in each directory for additional information


# uv Installation and Set-up
You do not need to install Python first: uv downloads the Python version this repo uses (pinned in `.python-version`) the first time you sync.

## Mac / Linux
1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/), either with Homebrew:
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
This repo already has a `pyproject.toml` and a `uv.lock` file. These define the virtual environment (sort of like how requirements.txt defines a pip environment, but these files resolve dependencies and ensure everyone has the same dependencies, since those are defined in the lockfile). uv creates the environment in a `.venv` folder at the root of the repo.

To work in the uv virtual environment, you just need to prepend all command line statements with uv run (i.e. instead of `python hello_world.py` you would simply run `uv run python hello_world.py`). `uv run` also installs anything that is missing or out of date before running.

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