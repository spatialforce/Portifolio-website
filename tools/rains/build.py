"""When the rains come: the start of the rainy season across Southern Africa, every season since 1981/82.

    python build.py    # writes public/webmaps/rains/<season>.png and rains.json

Source: CHIRPS v2.0 pentad rainfall (UCSB-CHG/CHIRPS/PENTAD, 0.05 degrees) through Earth Engine project
directed-sun-490915-m4. Pentads are the six 5-day periods of each month (the last runs to month end).

Onset: the first pentad from 1 September with at least START mm that is not followed, within the next
six pentads (30 days), by two pentads in a row under DRY mm (a dry spell of about ten days). A false start
followed by a dry spell does not count. Searched to the end of February.

<season>.png (grey): onset pentad, 1 = 1 to 5 September ... 36 = 26 to 28/29 February;
    0 = the rains never started this way; 255 = sea or no data.
rains.json: seasons, box, size, and for every season the share of the land where the rains started by
1 December.
"""
import io
import json
import os
import time

import ee
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "rains")
CACHE = os.path.join(HERE, "cache")
PROJECT = "directed-sun-490915-m4"
BOX = [11.5, -35.0, 41.0, -8.0]
RES = 0.05
SEASONS = range(1981, 2026)           # 1981 = the 1981/82 season
START, DRY = 25, 5
SEARCH = 36                           # September to February
LOOK = 6                              # pentads checked after the start
N = SEARCH + LOOK                     # September to March


def call(f):
    for k in range(8):
        try:
            return f()
        except Exception as e:                       # quota, concurrency and dropped connections
            if k == 7:
                raise
            print("   retry:", str(e)[:80], flush=True)
            time.sleep(15 * (k + 1))


def pentads(y):
    col = (ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
           .filterDate(f"{y}-09-01", f"{y + 1}-04-01").sort("system:time_start"))
    img = col.toBands().rename([f"p{i}" for i in range(N)])
    return img.min(254).unmask(255).toUint8()


def fetch(y):
    path = os.path.join(CACHE, f"{y}.npy")
    if os.path.exists(path):
        return np.load(path)
    w0, s0, e0, n0 = BOX
    nx, ny = int(round((e0 - w0) / RES)), int(round((n0 - s0) / RES))
    raw = call(lambda: ee.data.computePixels({
        "expression": pentads(y), "fileFormat": "NPY",
        "grid": {"dimensions": {"width": nx, "height": ny},
                 "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": w0, "shearY": 0, "scaleY": -RES, "translateY": n0},
                 "crsCode": "EPSG:4326"}}))
    a = np.load(io.BytesIO(raw))
    arr = np.stack([a[f"p{i}"] for i in range(N)]).astype(np.uint8)
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, arr)
    return arr


def onset(p):
    """p: pentads x rows x cols of mm (255 = sea). Returns the onset pentad, 1-based, 0 none, 255 sea."""
    sea = (p == 255).all(0)
    mm = np.where(p == 255, 0, p).astype(np.int16)
    dry = mm < DRY
    spell = dry[:-1] & dry[1:]                         # spell[i]: pentads i and i+1 both dry
    out = np.zeros(p.shape[1:], np.uint8)
    for i in range(SEARCH):
        ok = mm[i] >= START
        for j in range(i + 1, min(i + LOOK, N - 1)):
            ok &= ~spell[j]
        out[(out == 0) & ok] = i + 1
    out[sea] = 255
    return out


def main():
    ee.Initialize(project=PROJECT)
    os.makedirs(OUT, exist_ok=True)
    meta = []
    by_dec = 18                                        # pentad 18 ends 30 November
    for y in SEASONS:
        o = onset(fetch(y))
        Image.fromarray(o, "L").save(os.path.join(OUT, f"{y}.png"), optimize=True)
        land = o != 255
        share = float(((o >= 1) & (o <= by_dec) & land).sum() / land.sum())
        meta.append({"season": y, "byDec": round(share, 3)})
        print(f"{y}/{(y + 1) % 100:02d}: rains started by 1 December on {share:.0%} of the land", flush=True)
    h, w = o.shape
    json.dump({"box": BOX, "w": w, "h": h, "start": START, "dry": DRY, "seasons": meta},
              open(os.path.join(OUT, "rains.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
