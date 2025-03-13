/*//////////////////////////////////////////////////////////////////////////////
   This script was created by SkyTruth to create annual greenest-pixel (maximum
   NDVI) composites and to save those composites as an Earth Engine 
   ImageCollection. This collection will then be used as input data for the
   annual coal surface mining extent analysis.
   
   Note: to avoid for loops, you must manually input the year for which you want
   to create the composite (see below).

/*------------------------------ IMPORT STUDY AREA -------------------------- */

// https://www.google.com/fusiontables/DataSource?docid=1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U
var studyArea = ee.FeatureCollection('ft:1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U');
var exportbounds = studyArea.geometry().bounds();

/* ----------------------------- IMPORT IMAGERY ------------------------------*/

// These are all raw, orthorectified datasets, for each Landsat sensor

var lm1 = ee.ImageCollection("LANDSAT/LM1_L1T"),
    lm2 = ee.ImageCollection("LANDSAT/LM2_L1T"),
    lm3 = ee.ImageCollection("LANDSAT/LM3_L1T"),
    lt4 = ee.ImageCollection("LANDSAT/LT4_L1T"),
    lt5 = ee.ImageCollection("LANDSAT/LT5_L1T"),
    le7 = ee.ImageCollection("LANDSAT/LE7_L1T"),
    lc8 = ee.ImageCollection("LANDSAT/LC8_L1T");

/*----------------------------- IMAGE PROCESSING -----------------------------*/

// This function will clean input, raw Landsat data for errors / edge
// contamination. Function modified from Matt Hancher, 
// https://code.earthengine.google.com/8c36dfab4f496b230cd7109f959089ff
var cleaner = function(outlierValue) {
  return function(image){
      // Compute the minimum mask across all bands, to eliminate known-risky edge pixels.
      var min_mask = image.mask().reduce(ee.Reducer.min());
      // Compute a mask that eliminates fully-saturated (likey non-physical) sensor values.
      var sat_mask = image.reduce(ee.Reducer.max()).lt(outlierValue);
      // Combine these masks and erode neighboring pixels just a bit.
      var new_mask = min_mask.min(sat_mask).focal_min(3);
      // Turn raw images into TOA images.
      return ee.Algorithms.Landsat.TOA(image).updateMask(new_mask);
  };
};

// Function for Landsat 1 & 2 & 3, cleans imagery of errors 
// and attempts to remove clouds.
var earlyLScleaner = function(image){
    var B4 = image.select('B4');
    var B5 = image.select('B5');
    var B7 = image.select('B7');
    var errorMask = B4.gte(0.065).and(B5.gte(0)).and(B7.lte(0.32)); 
    var cleanedImage = image.updateMask(errorMask);
    
    // See Braaten, Cohen, and Yang 2015, "Automated Cloud and Cloud Shadow 
    // Identification in Landsat MSS Imagery for Temperate Ecosystems", 
    // Remote Sensing of Environment 169
    var NDGR = cleanedImage.normalizedDifference(['B4', 'B5']); // Not NDVI
    var B4img = cleanedImage.select('B4');
    var cloud1 = NDGR.gt(0).and(B4img.gt(0.175)).or(B4img.gt(0.39));
    var cloud2 = cloud1.updateMask(cloud1);
    var cloud3 = cloud2.connectedPixelCount().reproject("EPSG:3857", undefined, 60);
    //var cloud3 = cloud2.connectedPixelCount(); <- [AAP] This was Nick's
    // sugguestion; this doesn't work because the algorithm needs the actual
    // number of connected pixels, and if you don't reproject then the zoom 
    // level of the viewport will affect this number (usually much too large).
    // I'm not totally sure, though, if this makes a difference when running 
    // exports. Tl;dr, projections are still really confusing (to me) in GEE.
    var cloud4 = cloud3.gte(9);
    var cloud5 = cloud4.updateMask(cloud4);
    var cloud6 = cloud5.reduceNeighborhood(
      ee.Reducer.max(), ee.Kernel.square(150, "meters"), undefined, false);
    var cloudMask = cloud6.unmask().not();
    
    return cleanedImage.updateMask(cloudMask);
};

// Cloud removal function for TM and later sensors.
var maskClouds = function(image) {
  var scored = ee.Algorithms.Landsat.simpleCloudScore(image);
  return image.updateMask(scored.select(['cloud']).lt(20));
      // Lower the number in the above line to more-strictly find clouds
};

// Below, build separate ImageCollections containing all imagery chosen from
// the specific sensor; run various cleaning algorithms on each image within
// collection.
var lm1Collection = lm1
  .filterBounds(studyArea)
  .filterDate('1972-01-01', '1974-12-31')
  .map(cleaner(250))
  .map(earlyLScleaner)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B7', 'B5']).rename('NDVI'))
  .select(["B4", "B5", "B6", "B7", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });

var lm2Collection = lm2
  .filterBounds(studyArea)
  .filterDate('1975-01-01', '1982-12-31')
  .map(cleaner(250))
  .map(earlyLScleaner)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B7', 'B5']).rename('NDVI'))
  .select(["B4", "B5", "B6", "B7", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });
  
var lm3Collection = lm3
  .filterBounds(studyArea)
  .filterDate('1978-01-01', '1982-12-31')
  .map(cleaner(250))
  .map(earlyLScleaner)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B7', 'B5']).rename('NDVI'))
  .select(["B4", "B5", "B6", "B7", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });  

var lt4Collection = lt4
  .filterBounds(studyArea)
  .filterDate('1984-01-01', '1993-12-31')
  .map(cleaner(250))
  .map(maskClouds)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B4', 'B3']).rename('NDVI'))
  .select(["B1", "B2", "B3", "B4", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });

var lt5Collection = lt5
  .filterBounds(studyArea)
  .filterDate('1984-01-01', '2011-12-31')
  .map(cleaner(250))
  .map(maskClouds)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B4', 'B3']).rename('NDVI'))
  .select(["B1", "B2", "B3", "B4", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });

var le7Collection = le7
  .filterBounds(studyArea)
  .filterDate('1999-01-01', Date.now())
  .filter(ee.Filter.date("2012-08-03","2012-08-04").not())
    // The above line removes a specific image that had too many errors
  .map(cleaner(250))
  .map(maskClouds)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B4', 'B3']).rename('NDVI'))
  .select(["B1", "B2", "B3", "B4", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });
  
var lc8Collection = lc8
  .filterBounds(studyArea)
  .filterDate('2013-01-01', Date.now())
  .map(cleaner(64256))
  .map(maskClouds)
  .map(function(image) {
    return image.addBands(image.normalizedDifference(['B5', 'B4']).rename('NDVI'))
  .select(["B2", "B3", "B4", "B5", "NDVI"])
  .rename(["B", "G", "R", "IR", "NDVI"]);
  });

// Merge all the collections into one.
var lsCollection = ee.ImageCollection((lm1Collection)
    .merge(lm2Collection)
    .merge(lm3Collection)
    .merge(lt4Collection)
    .merge(lt5Collection)
    .merge(le7Collection)
    .merge(lc8Collection));


/*------------------------ EXPORTING YEARLY COMPOSITES -----------------------*/

// Imagery year to export, or for MSS, first year of multi-year period. If we
// want to avoid for loops, there isn't a way to run through each year 
// automatically, so we have to manually change this number each time.
// Although maybe the new UI API could help with this...
var year = 2012; 

// Make the annual composite for the year noted above
var composite = lsCollection
      .filter(ee.Filter.calendarRange(year, year, 'year'))
      //.filter(ee.Filter.calendarRange(year, year+2, 'year')) // Three-year MSS
      //.filter(ee.Filter.calendarRange(year, year+1, 'year')) // Two-year MSS
      
      .filter(ee.Filter.calendarRange(5, 9, 'month'))
        // The above line is for restricting imagery to summer months. The first
        // number is the starting month, and the latter number is the ending 
        // month inclusive. I don't know if May - September is the best choice.
      .qualityMosaic('NDVI')
      .set({"year": year}); // This adds the year as a property to the image

// Export to GEE asset
var description = "composite_"+year; // Be careful here with multi-year MSS

Export.image.toAsset({
  image: composite,
  description: description,
  assetId: ("users/andrewpericak/greenestPixelComposites/"+description),
  region: exportbounds,
  scale: 30, // Change to 60 for MSS
  maxPixels: 1e10
});


// NOTE: there isn't a way to automatically turn all these Images into an
// ImageCollection, so you have to manually create that ImageCollection via the
// Asset manager in the GEE playground (the Asset tab on the top-left of the
// screen.) 
