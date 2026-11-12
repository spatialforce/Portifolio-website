# Hwange National Park boundary from WDPA (Earth Engine copy), saved as GeoJSON.
import json, ee
ee.Initialize(project="directed-sun-490915-m4")
fc = ee.FeatureCollection("WCMC/WDPA/current/polygons").filter(ee.Filter.stringContains("NAME", "Hwange"))
info = fc.select(["NAME", "DESIG_ENG", "REP_AREA", "GIS_AREA", "STATUS_YR", "WDPAID"]).getInfo()
for f in info["features"]: print(f["properties"])
json.dump(info, open("data/wdpa_hwange.geojson", "w"))
