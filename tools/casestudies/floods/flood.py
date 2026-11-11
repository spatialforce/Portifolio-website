"""Sentinel-1 flood detection for the Muzarabani and lower Save study areas, wet seasons 2016/17 to 2025/26.

Per acquisition date (all scenes of one day and one orbit mosaicked):
  water now  = VV (30 m focal median) < -18 dB
  flood      = water now AND dry-season reference VV of the same orbit > -15 dB AND drop from reference > 3 dB
               AND MERIT Hydro height above nearest drainage < 15 m AND slope < 5 degrees
  normal water = dry-season reference VV < -18 dB (river channels, dams)
Outputs
  data/ts_<aoi>.csv            date, orbit, flooded km2, share of the study area imaged
  data/fl_<aoi>_<y>.tif        byte, number of acquisition dates flooded in season y (Nov y to Apr y+1), 30 m, EPSG:32736
  data/normal_<aoi>.tif        byte, 1 = normal water
Run: python -I flood.py ts | rast
"""
import sys, os, json, time, urllib.request, urllib.error, ee, geopandas as gpd, pandas as pd
ee.Initialize()
SEASONS = list(range(2016, 2026))          # season y = 1 Nov y to 30 Apr y+1
A = gpd.read_file("data/aoi.gpkg").set_index("aoi")
def geom(k): return ee.Geometry(json.loads(gpd.GeoSeries([A.geometry[k].simplify(0.002)]).to_json())["features"][0]["geometry"])

S1 = (ee.ImageCollection("COPERNICUS/S1_GRD").filter(ee.Filter.eq("instrumentMode", "IW"))
      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV")).select("VV"))
MERIT = ee.Image("MERIT/Hydro/v1_0_1")
HAND = MERIT.select("hnd"); SLOPE = ee.Terrain.slope(MERIT.select("elv"))
OK = HAND.lt(15).And(SLOPE.lt(5))

def smooth(i): return i.focalMedian(30, "circle", "meters")

def refs(g):
    c = S1.filterBounds(g).filter(ee.Filter.calendarRange(7, 10, "month")).filterDate("2017-01-01", "2026-01-01")
    orbits = c.aggregate_array("relativeOrbitNumber_start").distinct().getInfo()
    return {o: smooth(c.filter(ee.Filter.eq("relativeOrbitNumber_start", o)).median()) for o in orbits}

def flood_img(day, orbit, g, R):
    c = S1.filterBounds(g).filterDate(day, ee.Date(day).advance(1, "day")).filter(ee.Filter.eq("relativeOrbitNumber_start", orbit))
    vv = smooth(c.mosaic()); ref = R[orbit]
    return vv.lt(-18).And(ref.gt(-15)).And(ref.subtract(vv).gt(3)).And(OK).rename("f"), vv.mask().reduce(ee.Reducer.max()).rename("v")

def dates(g, a, b):
    c = S1.filterBounds(g).filterDate(a, b)
    return sorted(set(zip(c.aggregate_array("system:time_start").map(lambda t: ee.Date(t).format("YYYY-MM-dd")).getInfo(),
                          c.aggregate_array("relativeOrbitNumber_start").getInfo())))

def ts(k):
    g = geom(k); R = refs(g); out = f"data/ts_{k}.csv"
    done = pd.read_csv(out) if os.path.exists(out) else pd.DataFrame(columns=["date", "orbit", "flood_km2", "imaged"])
    have = set(zip(done.date, done.orbit)); rows = done.to_dict("records")
    for y in SEASONS:
        todo = [d for d in dates(g, f"{y}-11-01", f"{y + 1}-05-01") if d not in have and d[1] in R]
        for day, o in todo:
            f, v = flood_img(day, o, g, R)
            for t in range(4):
                try:
                    r = ee.Image.cat(f.multiply(ee.Image.pixelArea()), v.multiply(ee.Image.pixelArea())).reduceRegion(
                        ee.Reducer.sum(), g, 30, maxPixels=1e10, tileScale=4).getInfo(); break
                except Exception as e:
                    print("retry", day, e); time.sleep(10)
            rows.append(dict(date=day, orbit=o, flood_km2=round(r["f"] / 1e6, 3), imaged=round(r["v"] / g.area(1).getInfo(), 3)))
            print(k, day, o, rows[-1]["flood_km2"], rows[-1]["imaged"], flush=True)
        pd.DataFrame(rows).to_csv(out, index=False)

def dl(img, name, g):
    if os.path.exists(name): return
    try:
        urllib.request.urlretrieve(img.clip(g).getDownloadURL(dict(region=g.bounds(), scale=30, crs="EPSG:32736", format="GEO_TIFF")), name); print(name, flush=True)
    except urllib.error.HTTPError as e:
        print(name, e.read()[:400], flush=True)

def rast(k):
    g = geom(k); R = refs(g)
    for y in SEASONS:
        fs = [flood_img(d, o, g, R)[0] for d, o in dates(g, f"{y}-11-01", f"{y + 1}-05-01") if o in R]
        print(k, y, len(fs), flush=True)
        dl(ee.ImageCollection(fs).sum().unmask(0).toByte(), f"data/fl_{k}_{y}.tif", g)   # number of dates flooded in season y
    dl(ee.ImageCollection(list(R.values())).min().lt(-18).unmask(0).toByte(), f"data/normal_{k}.tif", g)

for k in ["muz", "save"]:
    (ts if sys.argv[1] == "ts" else rast)(k)
