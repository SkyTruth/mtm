/*///////////////////////////////////////////////////////////////////////////////////////
   This script was created by SkyTruth to identify possible active mountaintop removal 
   and other surface coal mining. This script is the full, complete version for analysis,
   meaning it will take a long time to run. 
   
   Playground code: https://code.earthengine.google.com/27b9023ebb9257895e9e3a3ff62401d0
///////////////////////////////////////////////////////////////////////////////////////*/

/* ------------------------------------- SCRIPT TASKS ------------------------------- */
// Trigger this to true to display yearly mining extent layers on run (will always be added to layer selector)
var yearlyLayers = true;
// Trigger this to true to run image exporting via Tasks
var exportImages = false;
// Trigger this to true to run video exporting via tasks
var exportVideo = false;
// Trigger this to true to run area calculation
var areaCalc = false;

/*------------------------------------ IMPORT STUDY AREA ---------------------------- */
var studyArea = ee.FeatureCollection('ft:1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U');
// Get the link here: https://www.google.com/fusiontables/DataSource?docid=1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U

/*------------------------------------ SET NDVI THRESHOLDS --------------------------*/
// These thresholds set per each year (and associated sensor) using Otsu method; 
// see https://github.com/SkyTruth/MTR/blob/master/EE-scripts/OtsuThresholds.js
// Note: The first four are a series of years; 1983 is omitted due to lack of quality imagery
//    1974 = 1972-1974      1977 = 1975-1977
//    1980 = 1978-1980      1982 = 1981-1982

var NDVI_Threshold = {
  1974: 0.4699,   1977: 0.5950,   1980: 0.5749,   1982: 0.5375,   1984: 0.5154,
  1985: 0.5120,   1986: 0.5425,   1987: 0.5199,   1988: 0.5290,   1989: 0.4952,
  1990: 0.5022,   1991: 0.4940,   1992: 0.4892,   1993: 0.5237,   1994: 0.5467,
  1995: 0.5494,   1996: 0.5574,   1997: 0.5327,   1998: 0.5229,   1999: 0.5152,
  2000: 0.5063,   2001: 0.5456,   2002: 0.5242,   2003: 0.5239,   2004: 0.5821,
  2005: 0.5401,   2006: 0.5552,   2007: 0.5609,   2008: 0.5454,   2009: 0.5443,
  2010: 0.5250,   2011: 0.5305,   2012: 0.5465,   2013: 0.5812,   2014: 0.5750,   
  2015: 0.5927
};

/*------------------------------------- IMPORT MASKS --------------------------------*/
var mask_input_60m_2015 = ee.Image('users/jerrilyn/2015mask-PM-fullstudy-area');
// Roads, water bodies, urban areas, etc., buffered 60 m
// Get the link here: https://drive.google.com/file/d/0B_MArPTqurHudFp6STU4ZzJHRmc/view

var miningPermits = ee.Image('users/andrewpericak/allMinePermits');
// All surface mining permits, buffered 1000 m
// Get the link here: https://drive.google.com/file/d/0B_PTuMKVy7beSWdZUkJIS3hneW8/view

var miningPermits_noBuffer = ee.Image('users/andrewpericak/allMinePermits_noBuffer');
// All surface mining permits, without any buffer

// This unmasks previously-masked areas within the mine permits
var mask_input_excludeMines = mask_input_60m_2015.where(miningPermits_noBuffer.eq(1),0);

/* ----------------------------------- VISUALIZATION / SETUP ------------------------------
Adds study area; various areas of interest  */

Map.addLayer(studyArea, {}, "Study area");

// Choose your favorite area of interest! Comment out all but one:
//Map.centerObject(studyArea);        // Full study extent
Map.setCenter(-81.971744, 38.094253, 12);     // Near Spurlockville, WV
//Map.setCenter(-82.705444, 37.020257, 12);     // Near Addington, VA
//Map.setCenter(-83.224567, 37.355144, 11);     // Near Dice, KY
//Map.setCenter(-83.931184, 36.533646, 12);     // Near Log Mountain, TN

// This list will contain all output images, so as to build an ImageCollection later for video export
var allMTR_list = [];

// This empty 2D array will be used for area calculation later (if performed)
var MTR_area = [[],[]];

// Subregions for exporting images/videos
var geometryI   = ee.Geometry.Rectangle([-79.612, 37.3525, -82.421, 39.037]).toGeoJSON();
var geometryII  = ee.Geometry.Rectangle([-82.421, 37.3525, -84.993, 38.942]).toGeoJSON();
var geometryIII = ee.Geometry.Rectangle([-82.421, 35.637,  -85.811, 37.3525]).toGeoJSON();
var geometryIV  = ee.Geometry.Rectangle([-79.849, 35.763,  -82.421, 37.3525]).toGeoJSON();
var exportbounds =studyArea.geometry().bounds().getInfo();

/*--------------------------------- IMAGE PROCESSING ---------------------------------*/

// This function will clean input, raw Landsat data for errors / edge contamination
// Function modified from Matt Hancher, https://code.earthengine.google.com/8c36dfab4f496b230cd7109f959089ff
var cleaner = function(image){
    // Compute the minimum mask across all bands, to eliminate known-risky edge pixels.
    var min_mask = image.mask().reduce(ee.Reducer.min()).gt(0);
    // Compute a mask that eliminates fully-saturated (likey non-physical) sensor values.
    var sat_mask = image.reduce(ee.Reducer.max()).lt(outlierValue);
    // Combine these masks and erode neighboring pixels just a bit.
    var new_mask = min_mask.min(sat_mask).focal_min(3);
    // Turn raw images into TOA images.
    return ee.Algorithms.Landsat.TOA(image).updateMask(new_mask);
};

// This function, used for Landsat 1 & 2, cleans imagery of errors and attempts to remove clouds
// Once it does that cleaning, it calculates NDVI for the image
var earlyLScleaner = function(image){
    var B4 = image.select("B4");
    var B5 = image.select("B5");
    var B7 = image.select("B7");
    var errorMask = ee.Image(0).where((B4.gte(0.065)).and(B5.gte(0)).and(B7.lte(0.32)),1); 
    var cleanedImage = image.updateMask(errorMask);
    
    // See Braaten, Cohen, and Yang 2015, "Automated Cloud and Cloud Shadow Identification in Landsat MSS Imagery for Temperate Ecosystems", Remote Sensing of Environment 169
    var NDGR = cleanedImage.normalizedDifference(["B4","B5"]); // Not NDVI
    var B4img = cleanedImage.select("B4");
    var cloud1 = ee.Image(0).where((NDGR.gt(0).and(B4img.gt(0.175))).or(B4img.gt(0.39)),1);
    var cloud2 = cloud1.updateMask(cloud1);
    var cloud3 = cloud2.connectedPixelCount().reproject("EPSG:3857", undefined, 60);
    var cloud4 = cloud3.where(cloud3.gte(9),1).where(cloud3.lt(9),0);
    var cloud5 = cloud4.updateMask(cloud4);
    var cloud6 = cloud5.reduceNeighborhood(ee.call("Reducer.max"), ee.call("Kernel.square", 150, "meters"), undefined, false);
    var cloudMask = cloud5.unmask().remap([0,1],[1,0]);
    
    var ndvi = cleanedImage.updateMask(cloudMask).normalizedDifference(["B7", "B5"]);
    return cleanedImage.addBands(ndvi).clip(studyArea);
};

// This function, used for Landsat 5-8, just creates an NDVI band
var ndCalc = function(image){
  var calc = image
    .normalizedDifference([IRband,Rband])
    .clip(studyArea);
  return image.addBands(calc);
};

// This loop runs processing for each year between 1972 and 2015, performing certain code based off
// whatever year it's looking at. Note some early years get excluded.
for (var year = 2015; year >= 1972; year--){ // Years of interest for the study
  
  // Determine what imagery dataset to use
  // NDVIbands is a flag for later, to decide what NDVI calculation to perform
  // outlierValue is used in the cleaner function (above) for removing erroneously high values
  if (year <= 1974){
    var imagery = ee.ImageCollection("LANDSAT/LM1_L1T");  // Landsat 1: 1972 - 1974
    var NDVIbands = 75;
    var outlierValue = 250; // ~98% of [0-255]
  }
  else if (year > 1974 && year <= 1983){
    var imagery = ee.ImageCollection("LANDSAT/LM2_L1T");  // Landsat 2: 1975 - 1982 [omit 1983]
    var NDVIbands = 75;
    var outlierValue = 250;
  }
  else if (year > 1983 && year <= 2011){
    var imagery = ee.ImageCollection("LANDSAT/LT5_L1T");  // Landsat 5: 1984 - 2011
    var NDVIbands = 43;
    var outlierValue = 250;
  }
  else if (year == 2012){
    var imagery = ee.ImageCollection("LANDSAT/LE7_L1T");  // Landsat 7: 2012
    var NDVIbands = 43;
    var outlierValue = 250;
  }
  else if (year >= 2013){
    var imagery = ee.ImageCollection("LANDSAT/LC8_L1T");  // Landsat 8: 2013 - 2015
    var NDVIbands = 54;
    var outlierValue = 64256; // ~98% of [0-65535]
  }

  // Calculate NDVI and create greenest pixel composite; this varies based on both the year of the
  // imagery and on what Landsat bands are used to perform NDVI calcuation
  if (NDVIbands == 75){
    if (year >= 1972 && year <= 1973){continue;}  // Three-year analysis, so "skip" 1972 and 1973
    else if (year == 1974){
      var yearImgs = imagery
        .filterDate("1972-01-01", "1974-12-31") // Note these early years are hard-coded in
        .filterBounds(studyArea)
        .map(cleaner)
        .map(earlyLScleaner);
      var NDVI = yearImgs.select("nd").qualityMosaic("nd");
    }
    else if (year >= 1975 && year <= 1976){continue;}
    else if (year == 1977){
      var yearImgs = imagery
        .filterDate("1975-01-01", "1977-12-31")
        .filterBounds(studyArea)
        .map(cleaner)
        .map(earlyLScleaner);
      var NDVI = yearImgs.select("nd").qualityMosaic("nd");
    }
    else if (year >= 1978 && year <= 1979){continue;}
    else if (year == 1980){
      var yearImgs = imagery
        .filterDate("1978-01-01", "1980-12-31")
        .filterBounds(studyArea)
        .map(cleaner)
        .map(earlyLScleaner);
      var NDVI = yearImgs.select("nd").qualityMosaic("nd");
    }
    else if (year == 1981){continue;}
    else if (year == 1982){
      var yearImgs = imagery
        .filterDate("1981-01-01", "1982-12-31")
        .filterBounds(studyArea)
        .map(cleaner)
        .map(earlyLScleaner);
      var NDVI = yearImgs.select("nd").qualityMosaic("nd");
    }
    else if (year == 1983){continue;}
  }
  
  else if (NDVIbands == 54){
    var IRband = "B5";
    var Rband = "B4";
    var yearImgs = imagery
      .filterDate(year+"-01-01", year+"-12-31") // These later sensors don't need hard-coded years
      .filterBounds(studyArea)
      .map(cleaner)
      .map(ndCalc);
    var NDVI = yearImgs.select("nd").qualityMosaic("nd");
  }
  else if (NDVIbands == 43){
    var IRband = "B4";
    var Rband = "B3";
    var yearImgs = imagery
      .filterDate(year+"-01-01", year+"-12-31")
      .filterBounds(studyArea)
      .map(cleaner)
      .map(ndCalc);
    var NDVI = yearImgs.select("nd").qualityMosaic("nd");
  }
  
  // Create a mask of areas that ARE NOT mines (value of 1 to locations where NDVI is <= threshold)
  // This pulls the specific threshold for that year from the dictionary above
  var lowNDVI = NDVI.where(NDVI.lte(NDVI_Threshold[year]),1).where(NDVI.gt(NDVI_Threshold[year]),0);
  
  // Create binary image containing the intersection between the LowNDVI and anywhere the inverted mask is 1
  var MTR = lowNDVI.and(mask_input_excludeMines.eq(0));
  
  // Erode/dilate MTR sites to remove outliers (pixel clean-up)
  var MTR_cleaning = MTR
    .reduceNeighborhood(ee.Reducer.min(), ee.Kernel.euclidean(30, 'meters'))  // erode
    .reduceNeighborhood(ee.Reducer.max(), ee.Kernel.euclidean(60, 'meters'))  // dilate
    //.reduceNeighborhood(ee.Reducer.max(), ee.Kernel.euclidean(60, 'meters'))  // dilate
    .reduceNeighborhood(ee.Reducer.min(), ee.Kernel.euclidean(30, 'meters')); // erode

  // Mask MTR by the erosion/dilation, and by mining permit locations buffered 1 km
  var MTR_masked = MTR_cleaning.updateMask(MTR_cleaning).updateMask(miningPermits);

  /*--------------------------------- IMAGE VISUALIZATION ---------------------------------*/
  
  // Set color palette by year (http://colorbrewer2.org/?type=sequential&scheme=OrRd&n=8)
  // Currently every five years are a different color (dark -> light over time)
  if (year <= 1977){
    var palette = "990000";
  }
  else if (year > 1977 && year <= 1982){
    var palette = "d7301f";
  }
  else if (year > 1982 && year <= 1988){
    var palette = "ef6548";
  }
  else if (year > 1988 && year <= 1993 ){
    var palette = "fc8d59";
  }
  else if (year > 1993 && year <= 1998){
    var palette = "fdbb84";
  }
  else if (year > 1998 && year <= 2003){
    var palette = "fdd49e";
  }
  else if (year > 2003 && year <= 2008){
    var palette = "fee8c8";
  }
  else if (year > 2008){
    var palette = "fff7ec";
  }
  
  // Add each layer to the map; 
  // only years divisible by 5 turned on by default because this takes a while to display
  if (year % 5 === 0 && yearlyLayers === true){
    Map.addLayer(MTR_masked, {palette: palette}, ("MTM "+ year), true);
  }
  else if ((year % 5 !== 0 && yearlyLayers === true) || yearlyLayers === false){
     Map.addLayer(MTR_masked, {palette: palette}, ("MTM "+ year), false);
  }
  
  /* --------------------------------- AREA CALCULATION --------------------------------- */
  
  if (areaCalc === true){
    // Get a pixel area image, which will apply to any scale you provide
    var Area = ee.Image.pixelArea();
    // The area calculation
    var areaAll = MTR_masked.multiply(Area).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: geometryI,
      scale: 30,
      crs: 'EPSG:5072', // Equal-area projection; http://epsg.io/5072
      maxPixels: 1e9
    });
    var areaKmSq = ee.Number(areaAll.get('constant')).divide(1000*1000);
    
    // Add these areas and their corresponding year to 2D array
    // This doesn't quite do what I want it to yet
    MTR_area[0].push(year);
    MTR_area[1].push(areaKmSq);
    
    // No code yet for actually executing this, since it takes forever / crashes
  }
  
  /* -------------------------------- EXPORTING ------------------------------------------- */
  
  if (exportImages === true) {

  /*// Export entire study region to GDrive (many images; one per year!)
  Export.image.toDrive({
      image: MTR_masked.unmask(0),
      description: "MTR_"+year,
      region: exportbounds,
      scale: 900,
      crs: 'EPSG:5072',
    });*/
    
  // OR, export one or some of the subregions to GDrive (many images!) 
  Export.image.toDrive({
      image: MTR_masked.unmask(0),
      description: "MTR"+year+"reg1",
      region: geometryI,
      maxPixels: 1e9,
      scale: 30,
      crs: 'EPSG:5072',
    });
  Export.image.toDrive({
      image: MTR_masked.unmask(0),
      description: "MTR"+year+"reg2",
      region: geometryII,
      maxPixels: 1e9,
      scale: 30,
      crs: 'EPSG:5072'
    });
  Export.image.toDrive({
      image: MTR_masked.unmask(0),
      description: "MTR"+year+"reg3",
      region: geometryIII,
      maxPixels: 1e9,
      scale: 30,
      crs: 'EPSG:5072'
    });
      
  Export.image.toDrive({
      image: MTR_masked.unmask(0),
      description: "MTR"+year+"reg4",
      region: geometryIV,
      maxPixels: 1e9,
      scale: 30,
      crs: 'EPSG:5072'
    });
  }  
    
  // Add each layer to a list, so as to build an ImageCollection for Video
  allMTR_list.push(MTR_masked);
}

/* ------------------------- VIDEO OUTPUT --------------------------------------------- */

if (exportVideo === true) {
// Create an ImageCollection of all images and use that to export a video
var reversedList = allMTR_list.reverse();
var allMTR = ee.ImageCollection(reversedList).map(function(image){
  return image.visualize({
    forceRgbOutput: true,
    palette: ["000000", "fdbb84"],
    min: 0,
    max: 1
  });
});
var HobetBounds = ee.Geometry.Rectangle([-82.015, 38.0413, -81.8447, 38.137]);
Export.video.toDrive({
  collection: allMTR,
  description: "MTRtimelapse",    // Filename, no spaces allowed
  framesPerSecond: 1,             // I.e., 1 year / second
  region: HobetBounds,
  scale: 60,                     // Scale in m
  });
//
}


//------------------------------------ Work in Progress ------------------------------------
// Code below this point is still being tested, run at your own risk...
// This is all copied from old code, so variable references are likely broken 

/* ------------------- Total Reclaimed Mine Classification: -------------------
 Areas which are classified as mine land in earlier image but not later image, are now
 classified as reclaimed mine land.
      Early Date - Later Date 
//var reclaimed = MTR_1984.subtract(MTR_2014);
//Map.addLayer(reclaimed.sldStyle(sld_intervals5), {min:0, max:1}, 'Reclaimed Mine Land');
//---------------------------------------------------------------------------------------------------
// ------------------------- VECTORIZATION OF MTR SITES: *** IN PROGRESS *** ------------------------
var vector_MTR = MTR_1_clipped.reduceToVectors({
  geometry: studyArea,
  geometryType: 'polygon',
  crs: lsat8_crs,
  crsTransform: lsat8_crs_transform,
  eightConnected: false,
  maxPixels: 1e9,
  labelProperty: '1',
});
//Map.addLayer(vector_MTR);
//Export.image(final_buffer_out, '2015_MTR_Dilated_Scene-1', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordI});
//Export.table(vector_MTR,'vector_MTR1_minmax',{crs: lsat8_crs, crs_transform: lsat8_crs_transform, min:0, max:1});
      // ^^^ Needs to be exported as GeoJson, include min/max values
*/

//---------------------------------------------------------------------------------------------------
// UPDATES
// - 5/25: Clip output to Campagna Study Area
// - 5/25: Area calculation slipped to Campagna Study Area
// - 5/25: Export.image() is depricated, changed to Export.image.toDrive()
// - 5/26: Erosion/Dilation of MTR sites is now possible to remove artifact pixels
// - 5/31: Export polygonized MTR sites
// - 6/02: Script Cleanup to simpify for work currently In-Progress
// - 6/06: Script Cleanup for overall simplification
// - 6/24: Lots of cleaning/optimization
// - 7/07: Add new mask/study area; code for own greenest pixel composite
// - 7/13: Updated Erode/Dilate order and buffer distance
// - 7/14: Add yearly thresholds; add buffered mine permits
// - 7/15: Improve image/video exporting
// - 7/19: Add ability to process early landsat (now runs excruciatingly slow)
// - 7/27: General cleaning; triggers for certain processing; unmasking mine permit areas
