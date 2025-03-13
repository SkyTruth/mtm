# About These Scripts
This work is the continuation of SkyTruth's 2007 MTR mining project, which you can see on [cartoDB](https://skytruth-org.cartodb.com/viz/3c75f4b8-f5be-11e5-bfc2-0ef7f98ade21/public_map) or read about [here] (http://blog.skytruth.org/2009/12/measuring-mountaintop-removal-mining-in.html), and relied upon a time-intensive manual classification of spectral imagery. By using Earth Engine we are able to automate the classification of active MTR sites.

Goals:
======
1. To produce a comprehensive map of MTR mining activity in Appalachia
2. To effectively measure the burden of reclamation
3. To infill gaps in the 2007 SkyTruth study, as well as update it with data from after 2005
4. To create an automated method of classifying MTR mining activity, in such a manner that it will be easily updated in the future.

**What scripts are in this folder? Describe here.**

`annualMiningArea.js`: Part 2 of the analysis script, which generates mining area per year

`annualThresholdImages.js`: Script to generate annual, county-scale threshold images and save as Assets

`countInputImagesPerYear.js`: Script to determine how much raw Landsat imagery there is across study area

`export-imagery-accuracy-assessment.js`: Script to create RGB images for accuracy assessment classification

`greenestCompositesToAssets.js`: Part 1 of the analysis script, which creates an ImageCollection of annual greenest pixel composites

# Other Snippets

6/24/2016: An example of a more efficent way to create the mtr mask, and also erode and dilate it:
https://code.earthengine.google.com/383ea607340d39a7aca81bfd75b16575

8/3/2016: The code Andrew used to generate a visualization of each year with a different color:
https://code.earthengine.google.com/11f0adc0bb5e87c6f4d624dcd51f1842

# License
This work is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)