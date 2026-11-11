"""Cities in 3D: building heights in the dense cores of African cities, every year from 2016 to 2023.

    python build.py            # every city
    python build.py nairobi    # one city

Source, through Earth Engine project directed-sun-490915-m4: Google Open Buildings 2.5D Temporal
(GOOGLE/Research/open-buildings-temporal/v1), yearly layers of building presence and height at 0.5 m,
inferred from Sentinel-2. Ground picture from Sentinel-2 surface reflectance, 2023 to 2025.

Each city gets a window on its own equal area grid (Lambert azimuthal, centred on the window), 8 m cells.
A cell holds a building in a year where the mean building presence is at least PRESENT; its height is the
mean height of the building pixels in it.

public/webmaps/city3d/<slug>_a.png, _b.png, _c.png: three years each in R, G and B (2016 to 2018, 2019 to 2021,
    2022 and 2023): height in metres (0 = no building, capped at 254).
public/webmaps/city3d/<slug>.jpg: the ground picture, 2 x the cell grid.
city3d.json: per city the window, cell size and, for every year, the number of building cells, the built
    volume (km3) and the count of cells taller than 40 m.
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
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "city3d")
CACHE = os.path.join(HERE, "cache")
PROJECT = "directed-sun-490915-m4"
RES = 8
YEARS = list(range(2016, 2024))
PRESENT = 0.35
TALL = 40

# slug, name, country, centre lat, lon, window width and height in km
CITIES = [
    ("nairobi", "Nairobi", "Kenya", -1.278, 36.808, 10, 7),
    ("lagos", "Lagos", "Nigeria", 6.445, 3.425, 12, 8),
    ("johannesburg", "Johannesburg", "South Africa", -26.155, 28.050, 9, 13),
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


def wkt(lat, lon):
    return (f'PROJCS["laea",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],'
            f'UNIT["degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["latitude_of_center",{lat}],'
            f'PARAMETER["longitude_of_center",{lon}],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1]]')


def pixels(img, lat, lon, wkm, hkm, res, bands, tile=256):
    """Read the window in tiles; a tile that runs out of memory is split in four and read again."""
    W, H = int(wkm * 1000 // res), int(hkm * 1000 // res)
    x0, y1 = -wkm * 500, hkm * 500
    out = {}

    def read(x, y, w, h):
        grid = {"dimensions": {"width": w, "height": h},
                "affineTransform": {"scaleX": res, "shearX": 0, "translateX": x0 + x * res, "shearY": 0, "scaleY": -res, "translateY": y1 - y * res},
                "crsWkt": wkt(lat, lon)}
        try:
            raw = call(lambda: ee.data.computePixels({"expression": img, "fileFormat": "NPY", "grid": grid}))
        except Exception as e:
            if "memory limit" in str(e) and min(w, h) > 32:
                hw, hh = w // 2, h // 2
                for u, v, ww, wh in [(x, y, hw, hh), (x + hw, y, w - hw, hh), (x, y + hh, hw, h - hh), (x + hw, y + hh, w - hw, h - hh)]:
                    read(u, v, ww, wh)
                return
            raise
        a = np.load(io.BytesIO(raw))
        for b in bands:
            if b not in out:
                out[b] = np.zeros((H, W), a[b].dtype)
            out[b][y:y + h, x:x + w] = a[b]

    n, total = 0, -(-W // tile) * -(-H // tile)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            read(x, y, min(tile, W - x), min(tile, H - y))
            n += 1
            print(f"   tile {n}/{total}  {time.strftime('%H:%M:%S')}", flush=True)
    return out


def year_image(y, region):
    col = (ee.ImageCollection("GOOGLE/Research/open-buildings-temporal/v1").filterBounds(region)
           .filter(ee.Filter.calendarRange(y, y, "year")))
    m = col.mosaic()
    pres = m.select("building_presence")
    h = m.select("building_height").updateMask(pres.gte(0.5))
    # 0.5 m to 8 m: the mean presence and the mean height of the building pixels in each cell
    return pres.unmask(0).rename(f"p{y}").addBands(h.rename(f"h{y}"))


def fetch(slug, lat, lon, wkm, hkm):
    path = os.path.join(CACHE, f"{slug}.npz")
    if os.path.exists(path):
        return dict(np.load(path))
    region = ee.Geometry.Point([lon, lat]).buffer(max(wkm, hkm) * 800)
    img = ee.Image.cat([year_image(y, region) for y in YEARS]).unmask(0).toFloat()
    a = pixels(img, lat, lon, wkm, hkm, RES, [f"{k}{y}" for y in YEARS for k in "ph"])
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(path, **a)
    return a


def picture(slug, lat, lon, wkm, hkm):
    path = os.path.join(OUT, f"{slug}.jpg")
    if os.path.exists(path):
        return
    region = ee.Geometry.Point([lon, lat]).buffer(max(wkm, hkm) * 800)
    col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(region).filterDate("2023-01-01", "2026-01-01")
           .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10)))

    def clear(im):
        scl = im.select("SCL")
        return im.updateMask(scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10)))
    rgb = col.map(clear).select(["B4", "B3", "B2"]).median().unmask(0)
    vis = rgb.divide(2800).clamp(0, 1).pow(1 / 1.3).multiply(255).toUint8()
    a = pixels(vis, lat, lon, wkm, hkm, RES // 2, ["B4", "B3", "B2"])
    Image.fromarray(np.dstack([a["B4"], a["B3"], a["B2"]]), "RGB").save(path, quality=84, optimize=True, progressive=True)


def main():
    ee.Initialize(project=PROJECT)
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    path = os.path.join(OUT, "city3d.json")
    doc = json.load(open(path)) if os.path.exists(path) else {"res": RES, "years": YEARS, "cities": []}
    for slug, name, country, lat, lon, wkm, hkm in CITIES:
        if only and slug not in only:
            continue
        print(f"{name}: {wkm} x {hkm} km at {RES} m", flush=True)
        a = fetch(slug, lat, lon, wkm, hkm)
        picture(slug, lat, lon, wkm, hkm)
    # one stable city per window from the cached years (see blocks.py)
    import blocks
    blocks.main()

if __name__ == "__main__":
    main()
