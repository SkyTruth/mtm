# Note
All code should be run from the `mtm/` directory.

# Highwall Skeletonization
**centerline_segments.py** --> Reduces highwall geometries into centerlines, split at their junctions into individual branches. Divides longer branches into shorter segments.
```shell
poetry run python Highwall_Detection/code/centerline_segments.py
```
# Data Analysis
**data_clean.R** --> Cleans highwall datasets into analysis-ready dataframes and calculates additional attributes. Cleaned data is saved in `data_analysis/cleaned/`.
**summary_stats.R** --> Calculates basic summary statistics by state for highwalls, segments, and permits. Results are saved in `data_analysis/results/`.
**make_figures.R** --> Produces bar charts used in the manuscript. These are saved in `data_analysis/figures/`.
**analysis_questions.R** --> Analyzes data to answer basic research questions.
**case_studies.R** --> Analyzes data related to specific case studies in each state.