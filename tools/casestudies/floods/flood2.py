"""Batch version of flood.py (interactive downloads hit "User memory limit exceeded").
Same rule as flood.py. Starts Earth Engine export tasks to project assets:
  fl_<aoi>     image, bands s2016..s2025 = number of acquisition dates flooded in season y (Nov y to Apr y+1), band normal = 1 normal water; 30 m EPSG:32736
  ts_<aoi>     table, one row per acquisition date: date, orbit, flood_km2, imaged_km2
Run: python -I flood2.py start | status | get
"""
import sys, os, json, urllib.request, ee, geopandas as gpd, pandas as pd
ee.Initialize(project="directed-sun-490915-m4")
ROOT = "projects/directed-sun-490915-m4/assets/"
SEASONS = list(range(2016, 2026))
A = gpd.read_file("data/aoi.gpkg").set_index("aoi")
def geom(k): return ee.Geometry(json.loads(gpd.GeoSeries([A.geometry[k].simplify(0.002)]).to_json())["features"][0]["geometry"])

S1 = (ee.ImageCollection("COPERNICUS/S1_GRD").filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV")).select("VV"))
MERIT = ee.Image("MERIT/Hydro/v1_0_1")
OK = MERIT.select("hnd").lt(15).And(ee.Terrain.slope(MERIT.select("elv")).lt(5))
def smooth(i): return i.focalMedian(30, "circle", "meters")

def refs(g):
    c = S1.filterBounds(g).filter(ee.Filter.calendarRange(7, 10, "month")).filterDate("2017-01-01", "2026-01-01")
    return {o: smooth(c.filter(ee.Filter.eq("relativeOrbitNumber_start", o)).median()) for o in c.aggregate_array("relativeOrbitNumber_start").distinct().getInfo()}

def dates(g, a, b):
    c = S1.filterBounds(g).filterDate(a, b)
    return sorted(set(zip(c.aggregate_array("system:time_start").map(lambda t: ee.Date(t).format("YYYY-MM-dd")).getInfo(),
                          c.aggregate_array("relativeOrbitNumber_start").getInfo())))

def flood_img(day, o, g, R):
    vv = smooth(S1.filterBounds(g).filterDate(day, ee.Date(day).advance(1, "day")).filter(ee.Filter.eq("relativeOrbitNumber_start", o)).mosaic())
    return vv.lt(-18).And(R[o].gt(-15)).And(R[o].subtract(vv).gt(3)).And(OK).unmask(0).rename("f"), vv.mask().reduce(ee.Reducer.max()).unmask(0).rename("v")

def start(k):
    g = geom(k); R = refs(g); bands, feats = [], []
    for y in SEASONS:
        ds = [d for d in dates(g, f"{y}-11-01", f"{y + 1}-05-01") if d[1] in R]; print(k, y, len(ds), flush=True)
        fs = []
        for day, o in ds:
            f, v = flood_img(day, o, g, R); fs.append(f)
            r = ee.Image.cat(f, v).multiply(ee.Image.pixelArea()).reduceRegion(ee.Reducer.sum(), g, 30, maxPixels=1e10, tileScale=8)
            feats.append(ee.Feature(None, dict(date=day, orbit=o, flood_km2=ee.Number(r.get("f")).divide(1e6), imaged_km2=ee.Number(r.get("v")).divide(1e6))))
        bands.append(ee.ImageCollection(fs).sum().toByte().rename(f"s{y}"))
    bands.append(ee.ImageCollection(list(R.values())).min().lt(-18).unmask(0).toByte().rename("normal"))
    img = ee.Image.cat(bands).clip(g)
    ee.batch.Export.image.toAsset(img, f"fl_{k}", ROOT + f"fl_{k}", region=g.bounds(), scale=30, crs="EPSG:32736", maxPixels=1e10).start()
    ee.batch.Export.table.toAsset(ee.FeatureCollection(feats), f"ts_{k}", ROOT + f"ts_{k}").start()
    print("started", k, flush=True)

def get(k):
    g = geom(k); im = ee.Image(ROOT + f"fl_{k}")
    for b in im.bandNames().getInfo():
        n = f"data/fl_{k}_{b[1:]}.tif" if b != "normal" else f"data/normal_{k}.tif"
        if not os.path.exists(n):
            urllib.request.urlretrieve(im.select(b).getDownloadURL(dict(region=g.bounds(), scale=30, crs="EPSG:32736", format="GEO_TIFF")), n); print(n)
    fc = ee.FeatureCollection(ROOT + f"ts_{k}").getInfo()["features"]
    pd.DataFrame([f["properties"] for f in fc]).sort_values("date").to_csv(f"data/ts_{k}.csv", index=False); print("ts", k, len(fc))

if sys.argv[1] == "status":
    for t in ee.batch.Task.list()[:6]: print(t.config.get("description"), t.state, t.status().get("error_message", ""))
else:
    for k in ["muz", "save"]: (start if sys.argv[1] == "start" else get)(k)
