"""Lagos built from the sea: data build.

    python build.py    # writes public/webmaps/lagos/<year>.jpg, land.png and lagos.json

Sources, through Earth Engine project directed-sun-490915-m4:
    Landsat 7 and 8 Collection 2 top of atmosphere, sharpened to 15 m with the panchromatic band
    Copernicus Sentinel-2 L1C with Cloud Score+, 10 m
The Landsat frames are the single clearest pass (23 January 2001 and 18 December 2013). The Sentinel-2 frames
are the median of the cloud-free passes of the two dry seasons (November to March) before the year shown.
Water in the first frame is MNDWI above WATER, land in later frames is MNDWI below LAND. New land is water in the first frame that is land in a later frame and
in every frame after it, in patches of at least MIN_PX. land.png holds the index of the frame in
which each new cell first appears (0 = not new land).
"""
import io
import json
import math
import os

import ee
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.restoration import denoise_tv_chambolle

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "lagos")
PROJECT = "directed-sun-490915-m4"
BOX = [3.385, 6.385, 3.56, 6.475]
RES = 0.00009          # about 10 m
WATER = 0.05          # water in the first frame: open water and flooded swamp (0.15 would keep open water only)
LAND = 0.0            # land in later frames
MIN_PX = 100           # 1 ha
# year shown, sensor, first and last date of the passes used
FRAMES = [(2001, "l7", "1999-07-01", "2002-12-31"),
          (2013, "l8", "2013-04-01", "2015-12-31"), (2018, "s2", "2016-11-01", "2018-04-01"),
          (2022, "s2", "2020-11-01", "2022-04-01"), (2026, "s2", "2024-11-01", "2026-04-01")]
SRC = {"l7": "Landsat 7", "l8": "Landsat 8", "s2": "Sentinel-2"}


def landsat(kind, a, b, box):
    cid, r, g, bl, sw, pan = (("LANDSAT/LE07/C02/T1_TOA", "B3", "B2", "B1", "B5", "B8") if kind == "l7"
                              else ("LANDSAT/LC08/C02/T1_TOA", "B4", "B3", "B2", "B6", "B8"))

    def m(i):
        q = i.select("QA_PIXEL")
        ok = q.bitwiseAnd(1 << 1).eq(0).And(q.bitwiseAnd(1 << 3).eq(0)).And(q.bitwiseAnd(1 << 4).eq(0))
        clear = ok.unmask(0).reduceRegion(ee.Reducer.mean(), box, 90).get("QA_PIXEL")
        return (i.resample("bicubic").select([r, g, bl, sw, pan], ["r", "g", "b", "sw", "pan"])
                .set("clear", clear, "day", i.date().format("YYYY-MM-dd")))
    # the single clearest pass over the window
    col = ee.ImageCollection(cid).filterBounds(box).filterDate(a, b).map(m).sort("clear", False).limit(1)
    print("  ", col.aggregate_array("day").getInfo(), [round(x, 3) for x in col.aggregate_array("clear").getInfo()])
    med = col.sort("clear").mosaic()
    hsv = med.select(["r", "g", "b"]).rgbToHsv()
    rgb = ee.Image.cat([hsv.select("hue"), hsv.select("saturation"), med.select("pan")]).hsvToRgb()
    mnd = med.normalizedDifference(["g", "sw"])
    return rgb.rename(["r", "g", "b"]).addBands(mnd.rename("mnd")), col.size()


def sentinel(a, b, box):
    cs = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
    col = (ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterBounds(box).filterDate(a, b)
           .filter(ee.Filter.calendarRange(11, 3, "month")).linkCollection(cs, ["cs"])
           .map(lambda i: i.updateMask(i.select("cs").gte(0.65)).select(["B4", "B3", "B2", "B11"], ["r", "g", "b", "sw"]).divide(10000)))
    med = col.median()
    return med.select(["r", "g", "b"]).addBands(med.normalizedDifference(["g", "sw"]).rename("mnd")), col.size()


def fetch(img):
    w0, s0, e0, n0 = BOX
    nx, ny = int(round((e0 - w0) / RES)), int(round((n0 - s0) / RES))
    bands = ["r", "g", "b", "mnd"]
    out = np.zeros((ny, nx, 4), np.float32)
    t = 1024
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
                out[ty:ty + h, tx:tx + w, k] = a[n]
    return out


def raw(year, kind, a, b):
    path = os.path.join(CACHE, f"{year}.npz")
    if os.path.exists(path):
        return np.load(path)["a"]
    box = ee.Geometry.Rectangle(BOX)
    img, n = sentinel(a, b, box) if kind == "s2" else landsat(kind, a, b, box)
    print(" ", year, "passes", n.getInfo())
    arr = fetch(img)
    np.savez_compressed(path, a=arr)
    return arr


def picture(a, kind):
    """Natural colour land with the water drawn in one blue for every year, so sensors of different age read alike.

    Land: haze taken off each band, then one stretch over the land's own range, more saturation, sharpened.
    Landsat frames are first smoothed with an edge keeping filter to take out sensor noise.
    Water: where MNDWI says water, a blue that follows the brightness of the water (sediment stays visible).
    """
    rgb = np.nan_to_num(a[..., :3], nan=0.0)
    mnd = np.nan_to_num(a[..., 3], nan=1.0)
    dry = mnd < -0.05
    lo = np.minimum(np.percentile(rgb[dry], 0.5, axis=0), np.percentile(rgb, 0.1, axis=(0, 1)))
    hi = np.percentile((rgb - lo)[dry], 99.0)
    v = np.clip((rgb - lo) / hi, 0, 1)
    if kind != "s2":
        v = denoise_tv_chambolle(v, weight=0.035, channel_axis=-1)
    v = v ** (1 / 1.9)
    lum = v.mean(axis=2, keepdims=True)
    v = lum + (v - lum) * 1.3
    v = v + 0.7 * (v - ndimage.gaussian_filter(v, (1.5, 1.5, 0)))
    m = np.clip((ndimage.gaussian_filter(mnd, 0.8) + 0.02) / 0.14, 0, 1)
    m = (m * m * (3 - 2 * m))[..., None]
    wl = ndimage.gaussian_filter(rgb.mean(axis=2), 1.5)
    w0, w1 = np.percentile(wl[mnd > 0.1], [2, 98])
    t = (np.clip((wl - w0) / (w1 - w0), 0, 1) ** 0.8)[..., None]
    blue = np.array([20, 66, 118]) / 255 * (1 - t) + np.array([70, 146, 196]) / 255 * t
    v = np.clip(v * (1 - m) + blue * m, 0, 1)
    return Image.fromarray((v * 255).astype(np.uint8))


def clean(m):
    m = ndimage.binary_opening(m, iterations=1)
    lab, n = ndimage.label(m)
    if n == 0:
        return m
    size = ndimage.sum(m, lab, range(1, n + 1))
    return np.isin(lab, np.nonzero(size >= MIN_PX)[0] + 1)


def main():
    ee.Initialize(project=PROJECT)
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    data = [raw(*f) for f in FRAMES]
    water = [np.nan_to_num(a[..., 3], nan=1) > (WATER if i == 0 else LAND) for i, a in enumerate(data)]
    for (year, kind, *_), a in zip(FRAMES, data):
        picture(a, kind).save(os.path.join(OUT, f"{year}.jpg"), quality=86, optimize=True, progressive=True)
        print(year, "empty", round(float((~np.isfinite(a[..., 0])).mean()) * 100, 2), "%")
    # land from frame k onward, on water in the first frame
    first = np.zeros(water[0].shape, np.uint8)
    land_after = ~water[-1]
    stay = [None] * len(water)
    for k in range(len(water) - 1, 0, -1):
        land_after = land_after & ~water[k]
        stay[k] = land_after.copy()
    final = clean(water[0] & stay[-1])
    for k in range(len(water) - 1, 0, -1):
        first[final & stay[k]] = k
    lat = math.radians((BOX[1] + BOX[3]) / 2)
    ha = (RES * 111320 * math.cos(lat)) * (RES * 110574) / 1e4
    Image.fromarray(first).save(os.path.join(OUT, "land.png"), optimize=True)
    frames = [{"year": y, "src": SRC[k], "ha": round(float(((first > 0) & (first <= i)).sum()) * ha)}
              for i, (y, k, *_) in enumerate(FRAMES)]
    json.dump({"box": BOX, "w": first.shape[1], "h": first.shape[0], "frames": frames},
              open(os.path.join(OUT, "lagos.json"), "w"), indent=1)
    print([(f["year"], f["ha"]) for f in frames])


if __name__ == "__main__":
    main()
