/* Export Landsat and NAIP Imagery for Accuracy Assessment
Andrew Pericak, July 2016

This script will create GEE Export tasks for you to download R-G-B-IR imagery from Landsat and NAIP, to 
match the years we're using in the MTR analysis script. This imagery can then be used for running the 
accuracy assessment. Note that (obviously) Landsat covers all years, but that NAIP only starts in 2006, 
and it only selectively covers some states each year.

This script will export imagery only falling directly underneath given sample areas (plots), plus a 1 km
buffer around those sample plots. */

// CHANGE THE YEAR for whatever year you need imagery
var year = 2015;

var sampleAreas = ee.FeatureCollection('ft:1EBwSxnU5VLmgZl_yv_4HNgVhUb08N9A_spz69oOf'); // Updated sample areas (Omega added, Kappa removed) in EPSG:5072
var sampleAreaBuffer = sampleAreas.geometry().buffer(1000); // Sample areas buffered 1 km to get surroundings
var exportbounds = sampleAreaBuffer.bounds();

/* ------------------------- LANDSAT EXPORTING ------------------------------------------------------- */

// These if-else if statements will select the proper imagery based on whatever year you're looking at
// and run the TOA conversion, and then a median filter (per the GEE tutorials; they look nice.)

if (year <= 1974){
  var LSimagery = ee.Image(ee.ImageCollection("LANDSAT/LM1_L1T")  // Landsat 1: 1972 - 1974
    .filterDate("1972-01-01", "1974-12-31")
    .filterMetadata("CLOUD_COVER", "less_than", 10)
    .map(function(image){
      var toa = ee.Algorithms.Landsat.TOA(image);
      var clipped = toa.clip(sampleAreaBuffer);
      return clipped;
  })
  //.median());
  .reduce(ee.Reducer.percentile([15])));
}
else if (year > 1974 && year <= 1983){
  var LSimagery = ee.Image(ee.ImageCollection("LANDSAT/LM2_L1T")  // Landsat 2: 1975 - 1982 [omit 1983]
    .filterDate(year+"-01-01", (year+2)+"-12-31") // You may have to change this line a bit
    .filterMetadata("CLOUD_COVER", "less_than", 10)
    .map(function(image){
      var toa = ee.Algorithms.Landsat.TOA(image);
      var clipped = toa.clip(sampleAreaBuffer);
      return clipped;
  })
  //.median());
  .reduce(ee.Reducer.percentile([15])));
}
else if (year > 1983 && year <= 2011){
  var LSimagery = ee.Image(ee.ImageCollection("LANDSAT/LT5_L1T_TOA")  // Landsat 5: 1984 - 2011
    .filterDate(year+"-01-01", year+"-12-31")
    .filterMetadata("CLOUD_COVER", "less_than", 10)
    .map(function(image){
      var clipped = image.clip(sampleAreaBuffer);
      return clipped.select("B1","B2","B3","B4");
    })
    //.median());
    .reduce(ee.Reducer.percentile([15])));
}
else if (year == 2012){
  var LSimagery = ee.Image(ee.ImageCollection("LANDSAT/LE7_L1T_TOA")  // Landsat 7: 2012
    .filterDate(year+"-01-01", year+"-12-31")
    .filterMetadata("CLOUD_COVER", "less_than", 10)
    .map(function(image){
      var clipped = image.clip(sampleAreaBuffer);
      return clipped.select("B1","B2","B3","B4");
    })
    //.median());
    .reduce(ee.Reducer.percentile([15])));
}
else if (year >= 2013){
  var LSimagery = ee.Image(ee.ImageCollection("LANDSAT/LC8_L1T_TOA")  // Landsat 8: 2013 - 
    .filterDate(year+"-01-01", year+"-12-31")
    .filterMetadata("CLOUD_COVER", "less_than", 10)
    .map(function(image){
      var clipped = image.clip(sampleAreaBuffer);
      return clipped.select("B2","B3","B4","B5");
    })
    //.median());
    .reduce(ee.Reducer.percentile([15])));
}

// This exports the Landsat imagery
Export.image.toDrive({
  image: LSimagery,
  description: "REVISED_Landsat_"+year,
  region: exportbounds,
  scale: 30,
  crs: "EPSG:5072",
  maxPixels: 1e10,
  folder: "MTR_LANDSAT_IMAGES"  // Whatever GDrive folder you're using; note you don't need a "file path"
});

//Map.addLayer(LSimagery);

/* --------------------------- NAIP EXPORTNG -------------------------------------------- 

// This function adds the geometry of each sample area as a property to each feature
var looper = sampleAreas.map(function(feature){
  var areaGeo = feature.geometry();
  var setProperties = feature.set({"geometry": areaGeo});
  return setProperties;
});

// This selects the correct imagery for the given year, and medians it if necessary
var NAIPimagery = ee.Image(ee.ImageCollection("USDA/NAIP/DOQQ")
  .filterDate(year+"-01-01", year+"-12-31")
  .filterBounds(sampleAreas)
  //.select(["R","G","B"])   <-- If you get a band error in the Console, uncomment this line
  .median());

// This loop will look at each feature (study area) and create a separate Export task for each study
// Note that the features require a field called "newID" that has sequential numbers from 10 to 19
//    Andrew manually added that newID field to the Fusion Table of the original sample sites
for (var i = 10; i <= 19; i++){
  var id = ee.Feature(looper.filterMetadata("newID", "equals", i).first());
  var zone = id.get("Area_Name").getInfo();
  var geo = id.get("geometry");
  Export.image.toDrive({
    image: NAIPimagery,
    description: "NAIP_"+year+"_"+zone,
    region: geo,
    scale: 5, // Not NAIP's default resolution (1 m), but you probably don't need that for getting mines
    crs: "EPSG:5072",
    maxPixels: 1e13,
    folder: "MTR_LANDSAT_IMAGES" // Whatever GDrive folder you're using; note you don't need a "file path"
  });
}
// Note that GEE exports NAIP imagery with a 64-bit pixel depth (why, tho?) This may not display in ArcGIS
// by default, so in Arc use Copy Raster to save this as an 8-bit unsigned raster

// By adding the imagery and sample areas for your given year, you can see what sample areas you
// would need to run the Export tasks for -- no use in exporting imagery over sample areas without 
// NAIP coverage!
//Map.addLayer(NAIPimagery);
//Map.addLayer(sampleAreas);
*/
