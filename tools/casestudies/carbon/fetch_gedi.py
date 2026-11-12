# GEDI L4A footprint AGBD (v2.1, monthly rasterised footprints in Earth Engine) inside Hwange NP.
# Kept: l4_quality_flag = 1, degrade_flag = 0, sensitivity >= 0.95 (ORNL DAAC user guide advice).
import sys, json, urllib.request, ee
ee.Initialize(project="directed-sun-490915-m4")
park = ee.FeatureCollection("WCMC/WDPA/current/polygons").filter(ee.Filter.eq("NAME", "Hwange")).geometry()
B = ["agbd", "agbd_se", "pft_class", "sensitivity", "beam", "leaf_off_flag", "solar_elevation"]
def one(im):
    q = im.select("l4_quality_flag").eq(1).And(im.select("degrade_flag").eq(0)).And(im.select("sensitivity").gte(0.95))
    s = im.select(B).updateMask(q).addBands(ee.Image.pixelLonLat())
    return s.sample(region=park, scale=25, projection="EPSG:4326", geometries=False, tileScale=8, dropNulls=True) \
            .map(lambda f: f.set("month", im.date().format("YYYY-MM")))
for yr in sys.argv[1:]:
    col = ee.ImageCollection("LARSE/GEDI/GEDI04_A_002_MONTHLY").filterBounds(park).filterDate(f"{yr}-01-01", f"{int(yr)+1}-01-01")
    fc = col.map(one).flatten()
    url = fc.getDownloadURL(filetype="csv", selectors=B + ["longitude", "latitude", "month"])
    data = urllib.request.urlopen(url, timeout=900).read()
    open(f"data/gedi_{yr}.csv", "wb").write(data)
    print(yr, data.count(b"\n") - 1, "footprints")
