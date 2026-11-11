"""Rising water in 3D: download the 1 m LiDAR tiles.

    python fetch.py    # writes cache/dtm.npy and cache/dsm.npy (float32, 1 m, British National Grid)

Source: Environment Agency LIDAR Composite 1 m (Open Government Licence), over WCS.
    DTM  bare ground, used for the flood calculation
    DSM  last return surface with buildings, used for the 3D view
"""
import io
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
BOX = (462400, 97600, 468400, 104600)      # Portsea Island: west, south, east, north (metres)
T = 1000
BASE = "https://environment.data.gov.uk/spatialdata/"
SRC = {
    "dtm": ("lidar-composite-digital-terrain-model-dtm-1m", "13787b9a-26a4-4775-8523-806d13af58fc__Lidar_Composite_Elevation_DTM_1m"),
    "dsm": ("lidar-composite-digital-surface-model-last-return-dsm-1m", "9ba4d5ac-d596-445a-9056-dae3ddec0178__Lidar_Composite_Elevation_LZ_DSM_1m"),
}
Image.MAX_IMAGE_PIXELS = None


def tile(kind, x, y):
    path = os.path.join(CACHE, f"{kind}_{x}_{y}.npy")
    if os.path.exists(path):
        return np.load(path)
    name, cov = SRC[kind]
    url = (f"{BASE}{name}/wcs?service=WCS&version=2.0.1&request=GetCoverage&CoverageId={cov}"
           f"&format=image/tiff&subset=E({x},{x + T})&subset=N({y},{y + T})")
    for k in range(12):
        try:
            r = requests.get(url, timeout=300)
            a = np.array(Image.open(io.BytesIO(r.content)), np.float32)
            if a.shape == (T, T):
                break
        except Exception as e:
            print("  retry", kind, x, y, str(e)[:60], flush=True); __import__("time").sleep(15)
    else:
        raise SystemExit(f"could not fetch {kind} {x} {y}")
    a[a < -1000] = np.nan
    np.save(path, a)
    return a


def main():
    w, s, e, n = BOX
    for kind in SRC:
        jobs = [(kind, x, y) for y in range(s, n, T) for x in range(w, e, T)]
        with ThreadPoolExecutor(2) as ex:
            tiles = list(ex.map(lambda j: tile(*j), jobs))
        out = np.full((n - s, e - w), np.nan, np.float32)
        for (_, x, y), a in zip(jobs, tiles):
            out[n - y - T:n - y, x - w:x - w + a.shape[1]] = a      # row 0 is north
        np.save(os.path.join(CACHE, f"{kind}.npy"), out)
        print(kind, out.shape, "empty", round(float(np.isnan(out).mean()) * 100, 1), "%", np.nanmin(out), np.nanmax(out))


if __name__ == "__main__":
    main()
