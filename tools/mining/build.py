"""Mining footprint, before and after: data build.

    python build.py    # writes public/webmaps/mining/<site>_before.png, <site>_after.png, sites.json

Sources, through Earth Engine project directed-sun-490915-m4:
    Copernicus Sentinel-2 L2A (COPERNICUS/S2_SR_HARMONIZED), 10 m
    Landsat 5 and 7 Collection 2 L2 for Marange before the 2006 diamond rush, 30 m
    JRC Global Surface Water v1.4 (water 1984 to 2021)

For each year the raw layers are cached in cache/<site>_<year>.npz:
    p90  90th percentile NDVI over the hydrological year (October to September)
    dry  median NDVI in the dry season (May to September)
    mnd  median MNDWI in the dry season
Classes are then made here, so thresholds can be tuned without going back to Earth Engine.

Classes (PNG red channel; green channel is mining intensity 0..255):
    1 water   2 woodland   3 fields and grass   4 sparse   5 bare   6 mining
Bare all year = p90 below BARE. New ground = bare all year after, not before, not old water.
The mining zone is new ground grown by ZONE pixels; inside it, bare ground and new water count as
mining in both years (old pits next to new ones). Intensity is how far below BARE the greenest
time of year stays: fully stripped ground and pit lakes score highest.
"""
import io
import json
import math
import os
from concurrent.futures import ThreadPoolExecutor

import ee
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "mining")
PROJECT = "directed-sun-490915-m4"
RES = 0.00009          # about 10 m
BARE = 0.22
MIN_PX = 30            # 0.3 ha
WATER = 10             # percent of months with water, JRC 1984 to 2021
ZONE = 40              # 400 m

SITES = [
    {"id": "bikita", "name": "Bikita", "what": "Lithium", "box": [31.385, -19.995, 31.49, -19.925],
     "before": ("s2", 2019), "after": ("s2", 2026)},
    {"id": "marange", "name": "Marange", "what": "Diamonds", "box": [32.30, -19.72, 32.46, -19.53],
     "before": ("ls", 2005), "after": ("s2", 2026), "nomine": True},
    {"id": "arcadia", "name": "Arcadia", "what": "Lithium", "box": [31.375, -17.805, 31.455, -17.74],
     "before": ("s2", 2019), "after": ("s2", 2026), "nomine": True},
    {"id": "sabistar", "name": "Sabi Star", "what": "Lithium", "box": [31.93, -19.225, 31.995, -19.17],
     "before": ("s2", 2019), "after": ("s2", 2026), "nomine": True},
    {"id": "kamativi", "name": "Kamativi", "what": "Lithium", "box": [27.01, -18.355, 27.095, -18.29],
     "before": ("s2", 2019), "after": ("s2", 2026)},
    {"id": "manhize", "name": "Manhize", "what": "Iron and steel", "box": [30.57, -18.97, 30.65, -18.91],
     "before": ("s2", 2019), "after": ("s2", 2026), "nomine": True},
    {"id": "hwange", "name": "Hwange", "what": "Coal", "box": [26.36, -18.48, 26.56, -18.33],
     "before": ("s2", 2016), "after": ("s2", 2026)},
]
# nomine: no mine there in the before year, so nothing is drawn as mining in it.


def square(box):
    """Grow a box to a square of ground around its centre, so every site fills the frames the same way."""
    w, s_, e, n = box
    cx, cy = (w + e) / 2, (s_ + n) / 2
    k = math.cos(math.radians(cy))
    half = max((e - w) * k, n - s_) / 2
    return [round(cx - half / k, 5), round(cy - half, 5), round(cx + half / k, 5), round(cy + half, 5)]


for _s in SITES:
    _s["box"] = square(_s["box"])


def s2_col(box, a, b):
    def m(i):
        q = i.select("SCL")
        ok = q.neq(3).And(q.neq(8)).And(q.neq(9)).And(q.neq(10))
        i = i.updateMask(ok)
        return i.normalizedDifference(["B8", "B4"]).rename("ndvi").addBands(
            i.normalizedDifference(["B3", "B11"]).rename("mnd")).copyProperties(i, ["system:time_start"])
    return (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(box).filterDate(a, b)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)).map(m))


def ls_col(box, a, b):
    def m(i):
        q = i.select("QA_PIXEL")
        ok = q.bitwiseAnd(1 << 3).eq(0).And(q.bitwiseAnd(1 << 4).eq(0)).And(q.bitwiseAnd(1 << 5).eq(0))
        s = i.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5"]).multiply(0.0000275).add(-0.2).updateMask(ok)
        return s.normalizedDifference(["SR_B4", "SR_B3"]).rename("ndvi").addBands(
            s.normalizedDifference(["SR_B2", "SR_B5"]).rename("mnd")).copyProperties(i, ["system:time_start"])
    # Landsat 5 only: Landsat 7 after May 2003 has scan line gaps (SLC off) that show as stripes.
    return ee.ImageCollection("LANDSAT/LT05/C02/T1_L2").filterBounds(box).filterDate(a, b).map(m)


def layers(src, year, box):
    col = s2_col if src == "s2" else ls_col
    span = 1 if src == "s2" else 2          # Landsat 5 passes are sparse: use two hydrological years
    dry = ee.ImageCollection(col(box, f"{year - span + 1}-05-01", f"{year}-10-01")).filter(ee.Filter.calendarRange(5, 9, "month")).median()
    p90 = col(box, f"{year - span}-10-01", f"{year}-10-01").select("ndvi").reduce(ee.Reducer.percentile([90]))
    jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").unmask(0)
    return p90.rename("p90").addBands(dry.select("ndvi").rename("dry")).addBands(dry.select("mnd")).addBands(jrc.rename("jrc"))


def fetch(img, box, bands):
    w0, s0, e0, n0 = box
    nx, ny = int(round((e0 - w0) / RES)), int(round((n0 - s0) / RES))
    out = np.zeros((ny, nx, len(bands)), np.float32)
    t = 512
    for ty in range(0, ny, t):
        for tx in range(0, nx, t):
            w, h = min(t, nx - tx), min(t, ny - ty)
            raw = ee.data.computePixels({
                "expression": img.select(bands).toFloat(), "fileFormat": "NPY",
                "grid": {"dimensions": {"width": w, "height": h},
                         "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": w0 + tx * RES,
                                             "shearY": 0, "scaleY": -RES, "translateY": n0 - ty * RES},
                         "crsCode": "EPSG:4326"}})
            a = np.load(io.BytesIO(raw))
            for k, n in enumerate(bands):
                out[ty:ty + h, tx:tx + w, k] = np.nan_to_num(a[n], nan=0)
    return out


def raw(s, which):
    src, year = s[which]
    path = os.path.join(CACHE, f"{s['id']}_{year}.npz")
    if os.path.exists(path):
        return np.load(path)["a"]
    print(" ", s["name"], year, "fetching")
    a = fetch(layers(src, year, ee.Geometry.Rectangle(s["box"])), s["box"], ["p90", "dry", "mnd", "jrc"])
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(path, a=a)
    return a


def clean(m):
    m = ndimage.median_filter(m.astype(np.uint8), 3).astype(bool)
    lab, n = ndimage.label(m)
    if n == 0:
        return m
    size = ndimage.sum(m, lab, range(1, n + 1))
    return np.isin(lab, np.nonzero(size >= MIN_PX)[0] + 1)


def classify(a, zone, mining):
    p90, dry, mnd, jrc = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    old_water = jrc >= WATER
    water_now = mnd > 0.15
    bare = p90 < BARE
    c = np.full(p90.shape, 4, np.uint8)                 # sparse
    c[p90 >= 0.40] = 3                                  # fields and grass: green in the rains
    c[dry >= 0.32] = 2                                  # woodland: still green in the dry season
    c[bare] = 5
    c[old_water | water_now] = 1
    mine = np.zeros(p90.shape, bool)
    if mining:
        mine = clean(zone & (bare | water_now) & ~old_water)
        c[mine] = 6
    inten = np.where(mine, np.clip((BARE + 0.05 - p90) / (BARE + 0.15), 0.15, 1), 0)
    return c, (inten * 255).astype(np.uint8), mine


def save(c, inten, path):
    img = np.zeros(c.shape + (3,), np.uint8)
    img[..., 0] = c
    img[..., 1] = inten
    Image.fromarray(img).save(path, optimize=True)


def area_px(box):
    lat = math.radians((box[1] + box[3]) / 2)
    return (RES * 111320 * math.cos(lat)) * (RES * 110574)


def build(s):
    print(s["name"])
    b, a = raw(s, "before"), raw(s, "after")
    old_water = a[..., 3] >= WATER
    new = clean((a[..., 0] < BARE) & ~(b[..., 0] < BARE) & ~old_water)
    zone = ndimage.binary_dilation(new, iterations=ZONE)
    cb, ib, mb = classify(b, zone, not s.get("nomine"))
    ca, ia, ma = classify(a, zone, True)
    save(cb, ib, os.path.join(OUT, f"{s['id']}_before.png"))
    save(ca, ia, os.path.join(OUT, f"{s['id']}_after.png"))
    px = area_px(s["box"]) / 1e4
    meta = {"id": s["id"], "name": s["name"], "what": s["what"], "box": s["box"],
            "before": s["before"][1], "after": s["after"][1],
            "beforeSrc": "Landsat" if s["before"][0] == "ls" else "Sentinel-2", "afterSrc": "Sentinel-2",
            "haBefore": round(float(mb.sum()) * px), "haAfter": round(float(ma.sum()) * px),
            "ha": round(float(new.sum()) * px)}
    print(" ", s["name"], meta["haBefore"], "->", meta["haAfter"], "ha mined,", meta["ha"], "ha new")
    return meta


def main():
    ee.Initialize(project=PROJECT)
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(1) as ex:
        meta = list(ex.map(build, SITES))
    json.dump(meta, open(os.path.join(OUT, "sites.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
