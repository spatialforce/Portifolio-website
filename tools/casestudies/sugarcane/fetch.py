# Sentinel-2 L2A (harmonized) monthly median NDVI and NDMI at 20 m over the Hippo Valley and Triangle cane estates,
# Jan 2019 to Dec 2025, cloud and shadow masked with SCL. Stored as uint8 (value = index*100 + 100, 0 = no data).
import ee, urllib.request, os, sys
ee.Initialize(project="directed-sun-490915-m4")
R = ee.Geometry.Rectangle([31.33, -21.19, 31.80, -20.93])
CRS = "EPSG:32736"
def prep(i):
    t = i.get("system:time_start")
    s = i.select("SCL"); ok = s.eq(4).Or(s.eq(5)).Or(s.eq(6)).Or(s.eq(7)).Or(s.eq(11))
    i = i.updateMask(ok)
    return i.normalizedDifference(["B8", "B4"]).rename("ndvi").addBands(i.normalizedDifference(["B8A", "B11"]).rename("ndmi")).toFloat().set("system:time_start", t)
S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(R).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 70)).map(prep)
def month(y, m):
    d = ee.Date.fromYMD(y, m, 1)
    empty = ee.Image.constant([0, 0]).rename(["ndvi", "ndmi"]).toFloat().updateMask(0)
    ic = S2.filterDate(d, d.advance(1, "month"))
    return ee.Image(ee.Algorithms.If(ic.size().gt(0), ic.median(), empty))
TILES = [[31.33, -21.19, 31.565, -20.93], [31.565, -21.19, 31.80, -20.93]]
from concurrent.futures import ThreadPoolExecutor
def job(a):
    y, m, ix, t, bb = a; f = f"rast/{ix}_{y}{m:02d}_{t}.tif"
    if os.path.exists(f): return
    img = month(y, m).select(ix).multiply(100).add(100).clamp(1, 200).unmask(0).toUint8()
    for k in range(4):
        try:
            u = img.getDownloadURL({"region": ee.Geometry.Rectangle(bb), "scale": 20, "crs": CRS, "format": "GEO_TIFF"})
            urllib.request.urlretrieve(u, f + ".part"); os.replace(f + ".part", f); print(f, flush=True); return
        except Exception as e: err = e
    print("FAILED", f, err, flush=True)
jobs = [(y, m, ix, t, bb) for y in range(2019, 2026) for m in range(1, 13) for ix in ("ndvi", "ndmi") for t, bb in enumerate(TILES)]
with ThreadPoolExecutor(3) as ex: list(ex.map(job, jobs))
print("done")
