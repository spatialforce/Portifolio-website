"""Download rasters for the population case study from Earth Engine (one at a time; project is in Restricted Mode)."""
import ee, requests, os, sys
ee.Initialize(project="directed-sun-490915-m4")
box = ee.Geometry.Rectangle([25.0, -22.6, 33.2, -15.4])
zwe = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq("ADM0_NAME", "Zimbabwe"))
J = {
 "dem": (ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic(), 500),
 "pop": (ee.ImageCollection("WorldPop/GP/100m/pop").filter(ee.Filter.eq("country", "ZWE"))
         .filter(ee.Filter.eq("year", 2020)).first().select("population"), 100),
 "walk": (ee.Image("Oxford/MAP/accessibility_to_healthcare_2019").select("accessibility_walking_only"), 1000),
}
for k in sys.argv[1:]:
    img, sc = J[k]; out = f"rast/{k}.tif"
    if os.path.exists(out): continue
    if k == "pop":  # sum to 250 m so people are preserved
        img = img.unmask(0).reduceResolution(ee.Reducer.sum().unweighted(), maxPixels=64).reproject("EPSG:4326", None, 0.0025)
        sc = None
    url = img.clip(box).getDownloadURL({"region": box, "scale": sc, "crs": "EPSG:4326", "format": "GEO_TIFF",
                                        **({"crsTransform": [0.0025, 0, 25.0, 0, -0.0025, -15.4]} if sc is None else {})})
    if sc is None: url = img.getDownloadURL({"region": box, "crs": "EPSG:4326", "crsTransform": [0.0025, 0, 25.0, 0, -0.0025, -15.4], "format": "GEO_TIFF"})
    r = requests.get(url, timeout=600)
    if r.status_code != 200: print(k, r.text[:300]); continue
    open(out + ".part", "wb").write(r.content); os.replace(out + ".part", out); print(k, len(r.content))
