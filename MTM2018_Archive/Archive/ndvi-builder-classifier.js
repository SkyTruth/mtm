/*///////////////////////////////////////////////////////////////////////////////////////
   This script was created by SkyTruth to identify possible active mountaintop removal
   and other surface coal mining.
///////////////////////////////////////////////////////////////////////////////////////*/
/*------------------------------------ Set NDVI Thresholds ----------------------------*/
/* Sets a threshold value that may be applied to the NDVI layers to seperate the values
  into two classes: '1' where possible mining is <= threshold, and '0' where vegetation
  is > threshold.  */
var NDVI_Threshold = 0.51;
/*------------------------------------- Create Mask -------------------------------------
Imports 60 meter mask/creates variable containing imported mask */
var mask_input_60m = ee.Image('users/christian/60m-mask-total-area');
    // Takes an empty image and applies a 1 to everything outside of the
    // masked area (inverts mask_input) ie. New image returns everything
    // that isn't a road, river, etc.
var blank_mask = ee.Image(0);
var mask_inverted_60m = blank_mask.where(mask_input_60m.lte(0),1);
/*------------------------------ Import Greenest Pixel Composite --------------------------
Imports greenest pixel composites for Landsat imagery (L5, L7, & L8). */
var L8_composite = ee.Image(ee.ImageCollection('LANDSAT/LC8_L1T_ANNUAL_GREENEST_TOA')
  .filterDate('2015-01-01', '2015-12-31')
  .mean()
  .toFloat());
var L7_composite = ee.Image(ee.ImageCollection('LANDSAT/LE7_L1T_ANNUAL_GREENEST_TOA')
  .filterDate('2012-01-01', '2012-12-31')
  .first());
var L5_composite = ee.Image(ee.ImageCollection('LANDSAT/LT5_L1T_ANNUAL_GREENEST_TOA')
  .filterDate('2011-01-01', '2011-12-31')
  .first());
/* -------------------------- Calculate NDVI ----------------------------------------------
              NORMALIZED DIFFERENCE VEGETATION INDEX
        Formula: NDVI =   (NIR - RED)
                        --------------
                          (NIR + RED)
NDVI is measured on scale of -1 to 1, though values below 0 are uncommon; the
scale used here is from 0 to 1. Lower values correspond to less dense vegetation
and are more likely to be bare ground.
------------------------------------------------------------------------------------------*/
var ndvi_2015 = L8_composite.expression(
  '(Band5 - Band4) / (Band5 + Band4)',
  {
    Band5: L8_composite.select('B5'),
    Band4: L8_composite.select('B4')
  }
  );
var ndvi_2012 = L7_composite.expression(
  '(Band4 - Band3) / (Band4 + Band3)',
  {
    Band4: L7_composite.select('B4'),
    Band3: L7_composite.select('B3')
  }
  );
var ndvi_2011 = L5_composite.expression(
  '(Band4 - Band3) / (Band4 + Band3)',
  {
    Band4: L5_composite.select('B4'),
    Band3: L5_composite.select('B3')
  }
  );
/* ----------------------------------------- Mask ---------------------------------------------------
Take an empty image and applies a 1 to where the NDVI values fall below the previously set threshold. */
var blank = ee.Image(0);
var LowNDVI_L8_2015 = blank.where(ndvi_2015.lte(NDVI_Threshold),1);
var LowNDVI_L7_2012 = blank.where(ndvi_2012.lte(NDVI_Threshold),1);
var LowNDVI_L5_2011 = blank.where(ndvi_2011.lte(NDVI_Threshold),1);
//-------------------------- VISUALIZE IN MAP DISPLAY --------------------------------------------
/* Creates styles which can be applied by the Map.addLayer function for the purpose of
   visualizing map layers inside this API.*/
var sld_intervals1 = '\
<RasterSymbolizer>\
  <ColorMap  type="intervals" extended="false" >\
    <ColorMapEntry color="#ff0000" quantity="0" label="lte 0" opacity="0"/>\
    <ColorMapEntry color="#ff0000" quantity="0.5" label="0.5" />\
    <ColorMapEntry color="#ff0000" quantity="1" label="1" />\
  </ColorMap>\
</RasterSymbolizer>'; //RED
var sld_intervals2 = '\
<RasterSymbolizer>\
  <ColorMap  type="intervals" extended="false" >\
    <ColorMapEntry color="#ff8700" quantity="0" label="lte 0" opacity="0"/>\
    <ColorMapEntry color="#ff8700" quantity="0.5" label="0.5" />\
    <ColorMapEntry color="#ff8700" quantity="1" label="1" />\
  </ColorMap>\
</RasterSymbolizer>'; //YELLOW
var sld_intervals3 = '\
<RasterSymbolizer>\
  <ColorMap  type="intervals" extended="false" >\
    <ColorMapEntry color="#00fff9" quantity="0" label="lte 0" opacity="0"/>\
    <ColorMapEntry color="#00fff9" quantity="0.5" label="0.5" />\
    <ColorMapEntry color="#00fff9" quantity="1" label="1" />\
  </ColorMap>\
</RasterSymbolizer>'; //BLUE
var sld_intervals4 = '\
<RasterSymbolizer>\
  <ColorMap  type="intervals" extended="false" >\
    <ColorMapEntry color="#00d600" quantity="0" label="lte 0" opacity="0"/>\
    <ColorMapEntry color="#00d600" quantity="0.5" label="0.5" />\
    <ColorMapEntry color="#00d600" quantity="1" label="1" />\
  </ColorMap>\
</RasterSymbolizer>'; //GREEN
// Create binary image containing the intersection between the LowVI and anything
// where the inverted mask is 1.
var MTR_1 = LowNDVI_L8_2015.and(mask_inverted_60m);
var MTR_2 = LowNDVI_L7_2012.and(mask_inverted_60m);
var MTR_3 = LowNDVI_L5_2011.and(mask_inverted_60m);
//Centers map and sets zoom for this API display
Map.setCenter(-81.58,37.92,12);
Map.addLayer(MTR_1.sldStyle(sld_intervals1), {min:0, max:1}, 'MTR 2015');
Map.addLayer(MTR_2.sldStyle(sld_intervals2), {min:0, max:1}, 'MTR 2012');
Map.addLayer(MTR_3.sldStyle(sld_intervals3), {min:0, max:1}, 'MTR 2011');
/*-------------------------- EXPORTING RESULTS --------------------------------------------
Cuts AOI into quadrants for faster export time
Creates variables that contain geometry for AOIs*/
                                      //[   lower right,     upper left   ]
var geometryI   = ee.Geometry.Rectangle([-79.849, 37.3525, -82.421, 38.942]);
var geometryII  = ee.Geometry.Rectangle([-82.421, 37.3525, -84.993, 38.942]);
var geometryIII = ee.Geometry.Rectangle([-82.421, 35.763,  -84.993, 37.3525]);
var geometryIV  = ee.Geometry.Rectangle([-79.849, 35.763,  -82.421, 37.3525]);
/* Creates variables that contain the geometries in geoJson format
   when exporting, region must be specified in geoJson format*/
var jsonCoordI   = geometryI.toGeoJSON();
var jsonCoordII  = geometryII.toGeoJSON();
var jsonCoordIII = geometryIII.toGeoJSON();
var jsonCoordIV  = geometryIV.toGeoJSON();
/* Creates variables containing CRS, CRS_TRANSFORM, and SCALE/RESOLUTION from IMAGE and
   MASK which is used by Export.image function. */
var lsat5_crs = L5_composite.projection().atScale(30).getInfo()['crs'];
var lsat5_crs_transform = L5_composite.projection().atScale(30).getInfo()['transform'];
var lsat7_crs = L7_composite.projection().atScale(30).getInfo()['crs'];
var lsat7_crs_transform = L7_composite.projection().atScale(30).getInfo()['transform'];
var lsat8_crs = L8_composite.projection().atScale(30).getInfo()['crs'];
var lsat8_crs_transform = L8_composite.projection().atScale(30).getInfo()['transform'];
  //.atScale() -- pixel size of image ie. for landsat .atScale(30) because landsat pixels are 30m,
  //.getinfo() extracts the data; .getInfo()['crs'] extracts the crs data from the composite
var mask60m_crs = mask_input_60m.projection().atScale(30).getInfo()['crs'];
var mask60m_crs_transform = mask_input_60m.projection().atScale(30).getInfo()['transform'];

/*----------------------------- Exports images -----------------------------
                                // LANDSAT 5 Images
Export.image(L5_composite, 'L5_composite-SceneI', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordI});
Export.image(L5_composite, 'L5_composite-SceneII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordII});
Export.image(L5_composite, 'L5_composite-SceneIII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIII});
Export.image(L5_composite, 'L5_composite-SceneIV', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIV});
                                // LANDSAT 7 Images
Export.image(L7_composite, 'L7_composite-SceneI', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordI});
Export.image(L7_composite, 'L7_composite-SceneII', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordII});
Export.image(L7_composite, 'L7_composite-SceneIII', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordIII});
Export.image(L7_composite, 'L7_composite-SceneIV', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordIV});
                                // LANDSAT 8 Images
Export.image(L8_composite, 'L8_composite-SceneI', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordI});
Export.image(L8_composite, 'L8_composite-SceneII', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordII});
Export.image(L8_composite, 'L8_composite-SceneIII', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIII});
Export.image(L8_composite, 'L8_composite-SceneIV', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIV});

                        // Exporting NDVI Data as Scenes
                                // LANDSAT 5 NDVI
Export.image(ndvi_L5, 'L5-NDVI-SceneI', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordI});
Export.image(ndvi_L5, 'L5-NDVI-SceneII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordII});
Export.image(ndvi_L5, 'L5-NDVI-SceneIII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIII});
Export.image(ndvi_L5, 'L5-NDVI-SceneIV', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIV});
                                // LANDSAT 7 NDVI
Export.image(ndvi_L7, 'L7-NDVI-SceneI', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordI});
Export.image(ndvi_L7, 'L7-NDVI-SceneII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordII});
Export.image(ndvi_L7, 'L7-NDVI-SceneIII', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIII});
Export.image(ndvi_L7, 'L7-NDVI-SceneIV', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIV});
                                // LANDSAT 8 NDVI
Export.image(ndvi_L8, 'L8-NDVI-SceneI', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordI});
Export.image(ndvi_L8, 'L8-NDVI-SceneII', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordII});
Export.image(ndvi_L8, 'L8-NDVI-SceneIII', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIII});
Export.image(ndvi_L8, 'L8-NDVI-SceneIV', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIV});

                              // Exporting MTR Sites
//Export.image(MTR_1, '2015-MTR_Scene-1', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordI});
//Export.image(MTR_1, '2015-MTR_Scene-2', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordII});
//Export.image(MTR_1, '2015-MTR_Scene-3', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIII});
//Export.image(MTR_1, '2015-MTR_Scene-4', {crs: lsat8_crs, crs_transform: lsat8_crs_transform, region: jsonCoordIV});
          // USE ^^ for any Landsat 8 based MTR classification
//Export.image(MTR_4, '2012-MTR_Scene-1', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordI});
//Export.image(MTR_4, '2012-MTR_Scene-2', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordII});
//Export.image(MTR_4, '2012-MTR_Scene-3', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordIII});
//Export.image(MTR_4, '2012-MTR_Scene-4', {crs: lsat7_crs, crs_transform: lsat7_crs_transform, region: jsonCoordIV});
          // USE ^^ for any Landsat 7 based MTR classification
//Export.image(MTR_8, '1995-MTR_Scene-1', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordI});
//Export.image(MTR_8, '1995-MTR_Scene-2', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordII});
//Export.image(MTR_8, '1995-MTR_Scene-3', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIII});
//Export.image(MTR_8, '1995-MTR_Scene-4', {crs: lsat5_crs, crs_transform: lsat5_crs_transform, region: jsonCoordIV});
          // USE ^^ for any Landsat 5 based MTR classification
*/
//Note: When running export from Tasks tab, make sure to specify a google drive folder that already exists
//      in the user's Google Drive. Alternatively, add a driveFolder parameter to the Export.image function
//      with existing Google Drive folder name for more convenient exporting.


//------------------------------------ Work in Progress ------------------------------------
// Code below this point is still being tested, run at your own risk...

// Reclaimed Mine Classification (this works):
//      Early Date - Later Date
// Areas which are classified as mine land in earlier image but not later image, are now
// classified as reclaimed mine land.
var reclaimed = MTR_2.subtract(MTR_1);
Map.addLayer(reclaimed.sldStyle(sld_intervals4), {min:0, max:1}, 'reclaim');

// Vectorizing MTR Sites
// Derived from: https://developers.google.com/earth-engine/reducers_reduce_to_vectors
// Define thresholds on the MTR image.
/*
var zones = MTR_1.gt(0).add(MTR_1.gt(1));
zones = zones.updateMask(zones.neq(0));
var Vectorized_MTR_1 = MTR_1.reduceToVectors({
  geometry: TEST_GEOM,
  //geometry: fc,
  geometryType: 'polygon',
  crs: lsat8_crs,
  crsTransform: lsat8_crs_transform,
  eightConnected: false,
  maxPixels: 1e9,
  labelProperty: '1',
});
//Map.addLayer(Vectorized_MTR_1,{palette:['000000']}, 'vector');
var display = ee.Image(0).updateMask(0).paint(Vectorized_MTR_1, '000000', 2);
//Map.addLayer(display, {palette:['ff8700']}, 'vectorized_MTR_1');
//Map.addLayer(fc);
*/


// ERODE/DILATE MTR Sites to remove outliers
// ^^ Erosion still in progress

var buffer = MTR_1.distance(ee.Kernel.euclidean(30, "meters"));
Map.addLayer(buffer, {min:0, max:1}, 'buffer-MTR_1');
// ^^ Buffer works


/*
// Kroodsma Area Calculation Work:

// Get a pixel area image, which will apply to any scale you provide
var pixelArea = ee.Image.pixelArea();

// Function to reduce region to get statistics of area
function get_area(layerName, theLayer){
  var areaIAll = theLayer.multiply(pixelArea).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometryI,
    scale: 30,
    maxPixels: 1e9
   });
   var areaSqKm = ee.Number(areaIAll.get('constant')).divide(1000*1000);
  print(layerName, areaSqKm);
  return areaSqKm;
}
get_area("MTR_1 Area in Sq Km: ", MTR_1);

// Get a pixel area image, which will apply to any scale you provide
var PA = ee.Image.pixelArea();

function GA(layerName, theLayer){
  var areaIAll = theLayer.multiply(PA).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometryII,
    scale: 30,
    maxPixels: 1e9
   });
   var areaSqKm = ee.Number(areaIAll.get('constant')).divide(1000*1000);
  print(layerName, areaSqKm);
  return areaSqKm;
}
GA("MTR_1 Area2 in Sq Km: ", MTR_1);
*/
