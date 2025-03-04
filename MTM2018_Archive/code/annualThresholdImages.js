// Create annual, county-scale NDVI thresholds

// This script is a different way to set NDVI thresholds than the Otsu method we
// had previously been using. The Otsu method created one, yearly threshold for
// the entire study extent, but issues with number of images per area and with
// cloud contamination meant this threshold overestimated in some locations and
// underestimated in others. 

// To remedy the issues with Otsu, this script looks at each county individually
// (or, alternatively, the WRS footprints), collects all the NDVI values within
// that county's borders per year, masks out urban/water areas as well as mine
// permit areas, and sets the threshold at the mean value of the 0th - 1st 
// percentiles of the remaining NDVI values. The script then creates a yearly
// image by mosaicking all those county-scale thresholds together into one
// image, creating a raster showing each county with its unique threshold. These
// yearly, county-scale threshold images are then used in the mine analysis to
// compare the NDVI threshold with the NDVI values presented in the greenest 
// pixel composites.



/*------------------ IMPORT GREENEST COMPOSITE FEATURE COLLECTION ----------- */
var greenestComposites = ee.ImageCollection("users/andrewpericak/greenestComposites");

/*------------------------- IMPORT STUDY AREA ------------------------------- */
// https://www.google.com/fusiontables/DataSource?docid=1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U
var studyArea = ee.FeatureCollection('ft:1Lphn5PR9YbneoY4sPkKGMUOJcurihIcCx0J82h7U');

var fips_codes = [21013,21019,21025,21043,21051,21053,21063,21065,21071,21089,
                  21095,21109,21115,21119,21121,21125,21127,21129,21131,21133,
                  21135,21147,21153,21159,21165,21175,21189,21193,21195,21197,
                  21199,21203,21205,21231,21235,21237,47001,47013,47025,47035,
                  47049,47129,47133,47137,47141,47145,47151,51027,51051,51105,
                  51167,51169,51185,51195,51720,54005,54011,54015,54019,54025,
                  54039,54043,54045,54047,54053,54055,54059,54067,54075,54079,
                  54081,54089,54099,54101,54109];

var allCounties =  ee.FeatureCollection('ft:1S4EB6319wWW2sWQDPhDvmSBIVrD3iEmCLYB7nMM');
var features = allCounties.filter(ee.Filter.inList('FIPS', fips_codes));
var features_WRS1 = ee.FeatureCollection('ft:1t-5Te1pObpB1bllcF4Xf3eGjzLg58wce-Q_1tPPc');
var features_WRS2 = ee.FeatureCollection('ft:1kY7lrNs7vR_aptGZxvEklvTs8jHAT5aGsITbhtd9');

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

/*------------------------- CREATE THRESHOLD IMAGES ---------------------------*/
// SET THE YEAR for the threshold image you want to make
var year = 2012;
var description = "thresholds_"+year;


// This will make the threshold  by getting interval mean from 0th to 1st 
// percentile of NDVI values per county, for whatever year specified above
var yearImg = ee.Image(greenestComposites
  .filterMetadata("year", "equals", year).first())
  .select("NDVI")
  .updateMask(miningPermits_noBuffer.unmask().not())
  .updateMask(mask_input_60m_2015.not());

var reduceAll = ee.ImageCollection(features.map(function(feature){
  return yearImg.reduceRegion({
    reducer: ee.Reducer.intervalMean(0,3),
    geometry: feature.geometry(),
    scale: 30,
    maxPixels: 1e10
  }).toImage().toFloat().clip(feature);
})).mosaic();


// This exports the mosaicked percentile image, creating an image in which each
// county has its unique NDVI threshold value.
Export.image.toAsset({
  image: reduceAll.set({"year": year}),
  description: "thresholds_"+year,
  assetId: "ATIs_IM/"+description,
  region: studyArea.geometry(),
  scale: 30,
  maxPixels: 1e10
});
