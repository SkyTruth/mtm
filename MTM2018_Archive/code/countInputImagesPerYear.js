/*//////////////////////////////////////////////////////////////////////////////
   This script was created by SkyTruth to count the number of Landsat images 
   per each year of analysis, to identify where there are few if any input 
   images when making the greenest-pixel composite. This script will output a
   .tif image to your Google Drive, where each pixel is the count of the number 
   of input images found at that pixel.
   
   Note: to avoid for loops, you must manually input the year for which you want
   to create the composite (see below).

/*------------------------------ IMPORT STUDY AREA -------------------------- */
// https://www.google.com/fusiontables/DataSource?docid=1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U
var studyArea = ee.FeatureCollection('ft:1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U');
var exportbounds = studyArea.geometry().bounds();

// These are the WRS paths/rows (i.e., the footprints of a Landsat scene)
// WRS1 is for MSS satellites (Landsat 1-3), and WRS2 is for non-MSS (LS 4-8)
var wrs1_areas = ee.FeatureCollection("ft:1t-5Te1pObpB1bllcF4Xf3eGjzLg58wce-Q_1tPPc", "geometry");
var wrs2_areas = ee.FeatureCollection("ft:1kY7lrNs7vR_aptGZxvEklvTs8jHAT5aGsITbhtd9", "geometry");

/* ----------------------------- IMPORT IMAGERY ------------------------------*/
// These are all raw, orthorectified datasets, for each Landsat sensor

var lm1 = ee.ImageCollection("LANDSAT/LM1_L1T"),
    lm2 = ee.ImageCollection("LANDSAT/LM2_L1T"),
    lm3 = ee.ImageCollection("LANDSAT/LM3_L1T"),
    lt4 = ee.ImageCollection("LANDSAT/LT4_L1T"),
    lt5 = ee.ImageCollection("LANDSAT/LT5_L1T"),
    le7 = ee.ImageCollection("LANDSAT/LE7_L1T"),
    lc8 = ee.ImageCollection("LANDSAT/LC8_L1T");

/*------------------------------ SET NDVI THRESHOLDS -------------------------*/
// These thresholds set per each year using the Otsu method; 
// see https://github.com/SkyTruth/MTR/blob/master/EE-scripts/OtsuThresholds.js
// Note: For the period [1974 - 1982], the script runs on three years' worth of
// imagery at a time; this table indicates which three-year periods:
//     Key  = 3-year period
//    -------------------
//    1974  =   1972-1974
//    1977  =   1975-1977
//    1980  =   1978-1980
//    1982  =   1981-1982
// Note: 1983 is omitted due to lack of quality imagery

var thresholds = ee.Dictionary({
  1974: 0.4699,   1977: 0.5950,   1980: 0.5749,   1982: 0.5375,   1984: 0.5154,
  1985: 0.5120,   1986: 0.5425,   1987: 0.5199,   1988: 0.5290,   1989: 0.4952,
  1990: 0.5022,   1991: 0.4940,   1992: 0.4892,   1993: 0.5237,   1994: 0.5467,
  1995: 0.5494,   1996: 0.5574,   1997: 0.5327,   1998: 0.5229,   1999: 0.5152,
  2000: 0.5063,   2001: 0.5456,   2002: 0.5242,   2003: 0.5239,   2004: 0.5821,
  2005: 0.5401,   2006: 0.5552,   2007: 0.5609,   2008: 0.5454,   2009: 0.5443,
  2010: 0.5250,   2011: 0.5305,   2012: 0.5465,   2013: 0.5812,   2014: 0.5750,   
  2015: 0.5927
});
// Other note: by using the full set of Landsat data (all sensors), then we 
// need to run this Otsu analysis again. Alternatively, we may need to scrap
// Otsu altogether since using multiple sensors for one year may not give us
// the bimodal distribution necessary for Otsu.

/*------------------------------ IMPORT MASKS --------------------------------*/
var mask_input_60m_2015 = ee.Image('users/jerrilyn/2015mask-PM-fullstudy-area');
// Roads, water bodies, urban areas, etc., buffered 60 m
// Get the link here: https://drive.google.com/file/d/0B_MArPTqurHudFp6STU4ZzJHRmc/view

var miningPermits = ee.Image('users/andrewpericak/allMinePermits');
// All surface mining permits, buffered 1000 m
// Get the link here: https://drive.google.com/file/d/0B_PTuMKVy7beSWdZUkJIS3hneW8/view

var miningPermits_noBuffer = ee.Image('users/andrewpericak/allMinePermits_noBuffer');
// All surface mining permits, without any buffer

// This excludes from the 60 m mask (mask_input_60m_2015) any areas within the
// the mine permit boundaries. Since the 60 m mask is "inversed" (i.e., 0 means
// keep and 1 means eventually mask), this line sets the mine permit areas
// (labeled as 1) to 0.
var mask_input_excludeMines = mask_input_60m_2015.where(miningPermits_noBuffer.eq(1), 0);

// Choose your favorite area of interest! Comment out all but one:
//Map.centerObject(studyArea);        // Full study extent
//Map.setCenter(-81.971744, 38.094253, 12);     // Near Spurlockville, WV
//Map.setCenter(-82.705444, 37.020257, 12);     // Near Addington, VA
//Map.setCenter(-83.224567, 37.355144, 11);     // Near Dice, KY
//Map.setCenter(-83.931184, 36.533646, 12);     // Near Log Mountain, TN


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
    var cloud6 = cloud5.reduceNeighborhood(ee.Reducer.max(), ee.Kernel.square(150, "meters"), undefined, false);
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


/*------------------ EXPORTING INPUT IMAGE COUNT IMAGES ----------------------*/

// Imagery year to export, or for MSS, first year of multi-year period. If we
// want to avoid for loops, there isn't a way to run through each year 
// automatically, so we have to manually change this number each time.
// Although maybe the new UI API could help with this...
var year = 1985; 

// Create an Image where each pixel is the count of images in the stack for
// the year noted above
var exportImg = lsCollection
    .filter(ee.Filter.calendarRange(year, year, 'year'))
    //.filter(ee.Filter.calendarRange(year, year+2, 'year')) // Three-year MSS
    //.filter(ee.Filter.calendarRange(year, year+1, 'year')) // Two-year MSS
    
    //.filter(ee.Filter.calendarRange(5, 9, 'month')) // For summer images only
    .select("B")
    .reduce(ee.Reducer.count());

// Save each count image to your Google Drive
Export.image.toDrive({
  image: exportImg,
  description: "imgCount_"+year, // Be careful here with multi-year MSS
  region: wrs2_areas.geometry().bounds(), // Landsat 4 - 8; year >= 1984
  //region: wrs1_areas.geometry().bounds(), // Landat 1 - 3; year < 1983
  scale: 300, // Note the large scale; using the original scale didn't work
  maxPixels: 1e9
});
