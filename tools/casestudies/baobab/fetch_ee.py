"""Elevation (SRTM, 30 arc-sec mean and 15 arc-sec for hillshade) and WDPA protected areas for Zimbabwe from Earth Engine."""
import ee, json, urllib.request, zipfile, io
ee.Initialize(project="directed-sun-490915-m4")
reg = ee.Geometry.Rectangle([25.0, -22.6, 33.2, -15.5], None, False)
dem = ee.Image("USGS/SRTMGL1_003")
import sys
if "dem500" in sys.argv[1:]:  # SRTM at 15 arc-sec; prep.py averages it to the 30 arc-sec CHELSA grid
    u = dem.toInt16().getDownloadURL({"region": reg, "crs": "EPSG:4326", "dimensions": "1968x1704", "format": "GEO_TIFF"})
    open("raw/dem500.tif", "wb").write(urllib.request.urlopen(u).read()); print("dem500")
pa = ee.FeatureCollection("WCMC/WDPA/current/polygons").filter(ee.Filter.eq("ISO3", "ZWE")).filter(ee.Filter.neq("STATUS", "Proposed"))
if "wdpa" not in sys.argv: raise SystemExit
pa = pa.map(lambda f: f.simplify(200).select(["NAME", "DESIG_ENG", "IUCN_CAT", "REP_AREA", "STATUS_YR"]))
d = pa.getInfo(); json.dump(d, open("raw/wdpa.geojson", "w")); print("wdpa", len(d["features"]))
