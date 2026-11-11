"""Sentinel-2 NDTI on water pixels per reach (April to July) and CHIRPS wet-season rainfall per window."""
import sys, ee, pandas as pd
from analysis import COR, AOI
def s2(i):
    scl = i.select("SCL")
    w = scl.eq(6)
    g, r = i.select("B3").divide(1e4), i.select("B4").divide(1e4)
    return r.subtract(g).divide(r.add(g)).rename("ndti").updateMask(w)
if sys.argv[1] == "ndti":
    rows = []
    for y in range(2019, 2026):
        c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(AOI).filterDate(f"{y}-04-01", f"{y}-07-31") \
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)).map(s2)
        im = c.median().addBands(c.count().rename("n"))
        red = ee.Reducer.median().combine(ee.Reducer.count(), sharedInputs=True)
        f = im.select("ndti").reduceRegions(COR, red, 20).getInfo()["features"]
        for x in f:
            p = x["properties"]; rows.append({"year": y, "reach": p["reach"], "ndti": p.get("median"), "px": p.get("count", 0)})
        print(y, c.size().getInfo(), flush=True)
    pd.DataFrame(rows).to_csv("data/ndti_by_reach.csv", index=False)
else:
    ch = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
    out = []
    for yr in range(1999, 2027):   # season ending in yr
        t = ch.filterDate(f"{yr-1}-11-01", f"{yr}-04-30").sum()
        v = t.reduceRegion(ee.Reducer.mean(), COR.geometry(), 5000).getInfo()["precipitation"]
        out.append({"season_end": yr, "nov_apr_mm": round(v, 1)})
    pd.DataFrame(out).to_csv("data/chirps_corridor.csv", index=False); print(pd.DataFrame(out).to_string(index=False))
