"""Wet-season true-colour Landsat composites (same scenes and cloud mask as the bare-ground windows) for the Shamva hotspot."""
import urllib.request, ee
import sys; sys.path.insert(0, ".")
from analysis import AOI
R = ee.Geometry.Rectangle([337290, 8085930, 371640, 8101740], "EPSG:32736", False)
def rgb(year):
    cols = [("LANDSAT/LC08/C02/T1_L2", ["SR_B4", "SR_B3", "SR_B2"]), ("LANDSAT/LC09/C02/T1_L2", ["SR_B4", "SR_B3", "SR_B2"])] if year >= 2014 else \
           [("LANDSAT/LT05/C02/T1_L2", ["SR_B3", "SR_B2", "SR_B1"]), ("LANDSAT/LE07/C02/T1_L2", ["SR_B3", "SR_B2", "SR_B1"])]
    out = None
    for cid, bs in cols:
        c = ee.ImageCollection(cid).filterBounds(AOI).filterDate(f"{year - 2}-11-01", f"{year + 1}-04-30") \
              .filter(ee.Filter.calendarRange(5, 10, "month").Not()) \
              .map(lambda i, bs=bs: i.select(bs, ["r", "g", "b"]).multiply(0.0000275).add(-0.2).updateMask(i.select("QA_PIXEL").bitwiseAnd(0b11010).eq(0)))
        out = c if out is None else out.merge(c)
    return out.median()
for y in [2000, 2009, 2017, 2025]:
    u = rgb(y).unitScale(0, 0.2).clamp(0, 1).pow(1 / 1.4).multiply(255).toByte().getDownloadURL({"region": R, "scale": 30, "crs": "EPSG:32736", "format": "GEO_TIFF"})
    urllib.request.urlretrieve(u, f"data/hot_l_rgb_{y}.tif"); print(y, flush=True)
