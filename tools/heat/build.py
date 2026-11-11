"""Urban heat islands: land surface temperature in and around twelve African cities.

    python build.py            # every city
    python build.py harare     # one city

Source, through Earth Engine project directed-sun-490915-m4:
  Landsat 8 and 9 Collection 2 Level 2 surface temperature (ST_B10, 100 m sensor, delivered at 30 m),
  every pass from 2021 to 2025 with under 25% cloud. Clouds, shadows and cirrus are masked with QA_PIXEL
  and the median of what is left is taken, so the picture is a typical clear mid-morning (about 10:00).
  The delivered product has holes where the ASTER emissivity map is empty. Those are filled from the
  top-of-atmosphere thermal band (NDVI emissivity), fitted to the delivered temperature in the same window.
  Built-up share from GHSL 2020 (JRC/GHSL/P2023A/GHS_BUILT_S). Water from JRC Global Surface Water and
  the Landsat water flag. True colour picture from Sentinel-2, 2024 to 2025.

Every city gets the same 64 x 40 km window on its own equal area grid (Lambert azimuthal, centred on the
city), 50 m cells for temperature and 25 m for the picture.

public/webmaps/heat/<slug>.png (grey, 1280 x 800): 1 to 254 = temperature, t0 + (v - 1) * 0.2 degrees C;
    0 = no clear view; 255 = water.
public/webmaps/heat/<slug>.jpg: Sentinel-2 true colour, 2560 x 1600.
heat.json: per city t0, the mean temperature of built-up land (at least 20% built) and of open land
    (under 2% built, not water) and the difference between them.
"""
import io
import json
import os
import sys
import time

import ee
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "heat")
CACHE = os.path.join(HERE, "cache")
PROJECT = "directed-sun-490915-m4"
WKM, HKM, RES = 64, 40, 50
NX, NY = WKM * 1000 // RES, HKM * 1000 // RES
STEP = 0.2
URBAN, OPEN = 0.20, 0.02

CITIES = [
    ("harare", "Harare", "Zimbabwe", -17.829, 31.053),
    ("bulawayo", "Bulawayo", "Zimbabwe", -20.15, 28.58),
    ("johannesburg", "Johannesburg", "South Africa", -26.2, 28.05),
    ("lusaka", "Lusaka", "Zambia", -15.417, 28.283),
    ("nairobi", "Nairobi", "Kenya", -1.286, 36.817),
    ("kampala", "Kampala", "Uganda", 0.33, 32.58),
    ("addis-ababa", "Addis Ababa", "Ethiopia", 9.01, 38.76),
    ("dar-es-salaam", "Dar es Salaam", "Tanzania", -6.82, 39.24),
    ("kinshasa", "Kinshasa", "DR Congo", -4.38, 15.33),
    ("luanda", "Luanda", "Angola", -8.92, 13.27),
    ("lagos", "Lagos", "Nigeria", 6.55, 3.38),
    ("accra", "Accra", "Ghana", 5.62, -0.2),
]


def call(f):
    for k in range(8):
        try:
            return f()
        except Exception as e:                       # quota, concurrency and dropped connections
            if k == 7 or "memory limit" in str(e):
                raise
            print("   retry:", str(e)[:90], flush=True)
            time.sleep(15 * (k + 1))


def window(slug, lat, lon):
    """The area read for a city, in metres on its own equal area grid: the default 64 x 40 km round the city
    point, or, where the official boundary does not fit in that, a box round the whole boundary with a margin.
    Larger boxes get larger cells so every city has about the same number of cells."""
    from admin import outline                         # official boundary, projected
    dflt = {"x0": -WKM * 500, "y1": HKM * 500, "wm": WKM * 1000, "hm": HKM * 1000, "res": RES}
    g = outline(slug, lat, lon)
    if g is None:
        return dflt
    x0, y0, x1, y1 = g.bounds
    pad = 0
    if x0 - pad >= -WKM * 500 and x1 + pad <= WKM * 500 and y0 - pad >= -HKM * 500 and y1 + pad <= HKM * 500:
        return dflt
    m = 0.06 * max(x1 - x0, y1 - y0) + 2000
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    res = max(RES, int(np.ceil(np.sqrt((x1 - x0) * (y1 - y0) / (NX * NY)) / 10) * 10))
    W, H = int(np.ceil((x1 - x0) / res / 8) * 8), int(np.ceil((y1 - y0) / res / 8) * 8)   # whole tiles, also at half the cell size
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return {"x0": round(cx - W * res / 2), "y1": round(cy + H * res / 2), "wm": W * res, "hm": H * res, "res": res}


def grid(lat, lon, res, tile=None, win=None):
    wkt = (f'PROJCS["laea",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],'
           f'UNIT["degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["latitude_of_center",{lat}],'
           f'PARAMETER["longitude_of_center",{lon}],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1]]')
    win = win or {"x0": -WKM * 500, "y1": HKM * 500, "wm": WKM * 1000, "hm": HKM * 1000}
    x, y, w, h = tile or (0, 0, win["wm"] // res, win["hm"] // res)          # tile in cells from the top left
    return {"dimensions": {"width": w, "height": h},
            "affineTransform": {"scaleX": res, "shearX": 0, "translateX": win["x0"] + x * res, "shearY": 0, "scaleY": -res, "translateY": win["y1"] - y * res},
            "crsWkt": wkt}


def pixels(img, lat, lon, res, bands, win=None, tile=256):
    """Read the window in tiles of at most tile x tile cells. The median of a few hundred Landsat passes is too
    heavy in one request; a tile that still runs out of memory is split in four and read again."""
    win = win or {"wm": WKM * 1000, "hm": HKM * 1000}
    W, H = win["wm"] // res, win["hm"] // res
    out = {}
    done = [0]
    total = -(-W // tile) * -(-H // tile)

    def read(x, y, w, h):
        try:
            raw = call(lambda: ee.data.computePixels({"expression": img, "fileFormat": "NPY", "grid": grid(lat, lon, res, (x, y, w, h), win)}))
        except Exception as e:
            if "memory limit" in str(e) and min(w, h) > 32:
                hw, hh = w // 2, h // 2
                for (u, v, ww, wh) in [(x, y, hw, hh), (x + hw, y, w - hw, hh), (x, y + hh, hw, h - hh), (x + hw, y + hh, w - hw, h - hh)]:
                    read(u, v, ww, wh)
                return
            raise
        a = np.load(io.BytesIO(raw))
        for b in bands:
            if b not in out:
                out[b] = np.zeros((H, W), a[b].dtype)
            out[b][y:y + h, x:x + w] = a[b]

    for y in range(0, H, tile):
        for x in range(0, W, tile):
            read(x, y, min(tile, W - x), min(tile, H - y))
            done[0] += 1
            print(f"   tile {done[0]}/{total}  {time.strftime('%H:%M:%S')}", flush=True)
    return out


CLEAR = 0b11110                                      # QA_PIXEL: dilated cloud, cirrus, cloud, shadow
YEARS = ("2021-01-01", "2026-01-01")


def passes(kind):
    col = (ee.ImageCollection(f"LANDSAT/LC08/C02/{kind}").merge(ee.ImageCollection(f"LANDSAT/LC09/C02/{kind}"))
           .filterDate(*YEARS).filter(ee.Filter.lt("CLOUD_COVER", 25)))
    return col


def level2():
    """Surface temperature as delivered (degrees C) and the water flag."""
    def prep(im):
        qa = im.select("QA_PIXEL")
        clear = qa.bitwiseAnd(CLEAR).eq(0)
        st = im.select("ST_B10").multiply(0.00341802).add(149.0 - 273.15).rename("t")
        water = qa.bitwiseAnd(1 << 7).neq(0).rename("w")
        return st.updateMask(clear).addBands(water.updateMask(clear)).toFloat()
    return passes("T1_L2").map(prep)


def brightness():
    """Temperature from the top-of-atmosphere thermal band with an NDVI emissivity (Sobrino et al. 2004).
    Not corrected for the atmosphere, so it reads low, but it has no holes: the delivered product is
    empty wherever the ASTER emissivity map it depends on is empty."""
    def prep(im):
        clear = im.select("QA_PIXEL").bitwiseAnd(CLEAR).eq(0)
        ndvi = im.normalizedDifference(["B5", "B4"])
        pv = ndvi.subtract(0.2).divide(0.3).clamp(0, 1).pow(2)
        eps = pv.multiply(0.004).add(0.986)
        bt = im.select("B10")
        lst = bt.divide(bt.multiply(10.895e-6 / 1.4388e-2).multiply(eps.log()).add(1)).subtract(273.15)
        return lst.rename("b").updateMask(clear).toFloat()
    return passes("T1_TOA").map(prep)


def tag(win):
    return "" if win["wm"] == WKM * 1000 and win["hm"] == HKM * 1000 and win["x0"] == -WKM * 500 else "_wide"


def reach(lat, lon, win):
    """A point and radius that cover the whole window, for filtering the image collections."""
    return ee.Geometry.Point([lon, lat]).buffer(float(np.hypot(max(abs(win["x0"]), abs(win["x0"] + win["wm"])),
                                                          max(abs(win["y1"]), abs(win["y1"] - win["hm"])))) + 5000)


def fetch(slug, lat, lon, win):
    path = os.path.join(CACHE, f"{slug}{tag(win)}.npz")
    if os.path.exists(path):
        z = np.load(path)
        return z["t"], z["built"], z["water"], int(z["n"])
    pt = reach(lat, lon, win)
    l2, toa = level2().filterBounds(pt), brightness().filterBounds(pt)
    n = call(lambda: l2.size().getInfo())
    wet = l2.select("w").mean().unmask(0)
    gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").unmask(0)
    water = wet.gt(0.5).Or(gsw.gte(50))
    built = (ee.ImageCollection("JRC/GHSL/P2023A/GHS_BUILT_S").filter(ee.Filter.eq("system:index", "2020"))
             .first().select("built_surface").unmask(0).divide(10000))
    img = (l2.select("t").median().unmask(-99).rename("t").addBands(l2.select("t").count().unmask(0).rename("n"))
           .addBands(toa.median().unmask(-99).rename("b"))
           .addBands(built.rename("built")).addBands(water.rename("water")).toFloat())
    a = pixels(img, lat, lon, win["res"], ["t", "n", "b", "built", "water"], win)
    t, b, cnt = a["t"], a["b"], a["n"]
    # trust the delivered temperature only where it was seen about as often as its neighbours
    good = (t > -50) & (cnt >= 0.5 * np.median(cnt[cnt > 0]))
    both = good & (b > -50) & (a["water"] < 0.5)
    k, c = np.polyfit(b[both], t[both], 1)                     # delivered = k * brightness + c
    r = np.corrcoef(b[both], t[both])[0, 1]
    hole = ~good & (b > -50)
    t = np.where(good, t, np.where(hole, k * b + c, -99)).astype(np.float32)
    print(f"   {n} passes; holes filled on {hole.mean():.1%} of the window (fit {k:.2f} x + {c:.1f}, r {r:.2f})", flush=True)
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(path, t=t, built=a["built"], water=a["water"], n=n)
    return t, a["built"], a["water"], n


def picture(slug, lat, lon, win):
    path = os.path.join(OUT, f"{slug}.jpg")
    mark = os.path.join(CACHE, f"{slug}{tag(win)}.jpgdone")
    if os.path.exists(path) and os.path.exists(mark):
        return
    pt = reach(lat, lon, win)
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(pt).filterDate("2024-01-01", "2026-01-01")
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 8)))

    def clear(im):
        scl = im.select("SCL")
        return im.updateMask(scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)))
    rgb = col.map(clear).select(["B4", "B3", "B2"]).median().unmask(0)
    vis = rgb.divide(3000).clamp(0, 1).pow(1 / 1.35).multiply(255).toUint8()
    a = pixels(vis, lat, lon, win["res"] // 2, ["B4", "B3", "B2"], win)
    Image.fromarray(np.dstack([a["B4"], a["B3"], a["B2"]]), "RGB").save(path, quality=82, optimize=True, progressive=True)
    open(mark, "w").close()


def main():
    ee.Initialize(project=PROJECT)
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    meta = []
    for slug, name, country, lat, lon in CITIES:
        if only and slug not in only:
            continue
        win = window(slug, lat, lon)
        print(f"{name}: window {win['wm'] / 1000:.0f} x {win['hm'] / 1000:.0f} km at {win['res']} m", flush=True)
        t, built, water, n = fetch(slug, lat, lon, win)
        wet = water > 0.5
        ok = (t > -50) & ~wet
        urban, open_ = ok & (built >= URBAN), ok & (built < OPEN)
        tu, to = float(t[urban].mean()), float(t[open_].mean())
        t0 = float(np.floor(np.percentile(t[ok], 0.5)))
        code = np.clip(np.round((t - t0) / STEP) + 1, 1, 254)
        code = np.where(ok, code, 0)
        code = np.where(wet, 255, code).astype(np.uint8)
        Image.fromarray(code, "L").save(os.path.join(OUT, f"{slug}.png"), optimize=True)
        meta.append({"slug": slug, "name": name, "country": country, "t0": t0, "urban": round(tu, 1), "open": round(to, 1),
                     "diff": round(tu - to, 1), "passes": n, "builtKm2": round(float(urban.sum()) * win["res"] ** 2 / 1e6),
                     "km": [win["wm"] / 1000, win["hm"] / 1000], "w": t.shape[1], "h": t.shape[0]})
        print(f"{name:14s} {n:4d} passes  built-up {tu:5.1f} C  open land {to:5.1f} C  difference {tu - to:+.1f} C"
              f"   clear {ok.mean():.0%}  water {wet.mean():.0%}  range {np.percentile(t[ok], 1):.0f} to {np.percentile(t[ok], 99):.0f}", flush=True)
        publish(meta[-1], lat, lon, win)
    # satellite photos last: they are slow and the temperature map does not need them
    for slug, name, country, lat, lon in CITIES:
        if not only or slug in only:
            picture(slug, lat, lon, window(slug, lat, lon))
            print(f"   {name} satellite image done", flush=True)


def publish(entry, lat, lon, win):
    """Put one finished city on the map at once: its boundary and its row in heat.json."""
    import admin
    from rasterio import features
    from rasterio.transform import Affine
    g = admin.outline(entry["slug"], lat, lon)
    if g is not None:
        r = win["res"]
        m = features.rasterize([(g, 255)], out_shape=(win["hm"] // r, win["wm"] // r),
                               transform=Affine(r, 0, win["x0"], 0, -r, win["y1"]), fill=0, dtype="uint8")
        Image.fromarray(m, "L").save(os.path.join(OUT, f"{entry['slug']}_city.png"), optimize=True)
    path = os.path.join(OUT, "heat.json")
    doc = json.load(open(path)) if os.path.exists(path) else {"km": [WKM, HKM], "w": NX, "h": NY, "step": STEP, "cities": []}
    rows = [c for c in doc["cities"] if c["slug"] != entry["slug"]] + [entry]
    order = [c[0] for c in CITIES]
    doc["cities"] = sorted(rows, key=lambda c: order.index(c["slug"]))
    json.dump(doc, open(path, "w"), indent=1)
    print(f"   {entry['name']} is on the map", flush=True)


if __name__ == "__main__":
    main()
