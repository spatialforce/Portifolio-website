"""Download monthly occurrence counts from GBIF on a 256 x 128 global grid (1.40625 degree cells).

Uses the GBIF ad hoc map API (EPSG:4326, zoom 1 = 4 x 2 tiles of 90 degrees), binned into
squares of 64 tile units, so each tile holds 64 x 64 cells. Every tile is cached on disk.

    python fetch.py            # fetch everything listed in species.py
"""
import concurrent.futures as cf
import os
import time
import urllib.error
import urllib.request

import numpy as np

import mvt
from species import EFFORT, SPECIES, YEARS

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
GRID = os.path.join(HERE, "grids")
W, H, N = 256, 128, 64  # grid size, cells per tile edge

URL = ("https://api.gbif.org/v2/map/occurrence/adhoc/1/{x}/{y}.mvt?srs=EPSG:4326"
       "&taxonKey={key}&month={m}&year={years}&bin=square&squareSize=64"
       "&occurrenceStatus=PRESENT&hasGeospatialIssue=false")


def tile(key, m, x, y):
    path = os.path.join(CACHE, str(key), f"{m:02d}_{x}_{y}.mvt")
    if os.path.exists(path):
        return open(path, "rb").read()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = URL.format(key=key, m=m, x=x, y=y, years=YEARS)
    for attempt in range(12):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "migration-atlas-build/1.0"})
            data = urllib.request.urlopen(req, timeout=120).read()
            open(path, "wb").write(data)
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            if e.code == 400 and "missing the expected layer" in body:
                open(path, "wb").write(b"")  # no records in this tile
                return b""
            wait = min(60, 3 * (attempt + 1) ** 2)
            print(f"  retry {key} m{m} {x},{y} in {wait}s ({e})")
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001 - retry anything network related
            wait = min(60, 3 * (attempt + 1) ** 2)
            print(f"  retry {key} m{m} {x},{y} in {wait}s ({e})")
            time.sleep(wait)
    raise RuntimeError(f"failed {url}")


def grid_for(key):
    out_path = os.path.join(GRID, f"{key}.npy")
    if os.path.exists(out_path):
        return
    g = np.zeros((12, H, W), np.float64)
    jobs = [(m, x, y) for m in range(1, 13) for x in range(4) for y in range(2)]
    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda j: (j, tile(key, *j)), jobs))
    for (m, x, y), data in res:
        for layer in mvt.decode(data):
            ext = layer["extent"]
            for props, bb in layer["features"]:
                if bb is None:
                    continue
                cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
                if not (0 <= cx < ext and 0 <= cy < ext):
                    continue  # tile buffer
                gx = x * N + int(cx * N / ext)
                gy = y * N + int(cy * N / ext)
                g[m - 1, gy, gx] += props.get("total", 0)
    os.makedirs(GRID, exist_ok=True)
    np.save(out_path, g)
    print(f"{key}: {int(g.sum()):,} records")


if __name__ == "__main__":
    keys = [s["key"] for s in SPECIES] + list(EFFORT.values())
    for k in keys:
        t = time.time()
        grid_for(k)
        print(f"  done {k} in {time.time() - t:.0f}s")
