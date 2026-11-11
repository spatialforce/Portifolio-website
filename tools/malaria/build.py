"""Malaria prevalence in Africa: the share of children aged 2 to 10 carrying Plasmodium falciparum
(PfPR 2-10), every year from 2000 to 2025.

    python build.py    # writes public/webmaps/malaria/<year>.png, borders.json and malaria.json

Source: Malaria Atlas Project, coverage Malaria__202608_Global_Pf_Parasite_Rate (2.5 arc minutes, about 5 km),
read from the MAP GeoServer over WCS. The server cuts replies off at 16 MB, so each year is fetched in
latitude strips. Band 1 is the rate (0 to 1); -9999 is no data (no transmission, or not modelled).

Each year is averaged 2 x 2 to 5 arc minutes (about 10 km) and written as a grey PNG:
    0 to 200 = rate in steps of 0.5 percentage points (200 = 100%), 255 = no data.
malaria.json: box, size, years, and for every year the mean rate over the mapped land and the share of
that land where more than one child in five is infected. Both are shares of land, not of people.
borders.json: country outlines (Natural Earth) as rings of [lon, lat].
"""
import io
import json
import os
import time
import zipfile

import geopandas as gpd
import numpy as np
import rasterio
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "malaria")
CACHE = os.path.join(HERE, "cache")
NE = os.path.join(HERE, "..", "corridors", "raw", "ne_10m_admin_0_countries.zip")
URL = "https://data.malariaatlas.org/geoserver/Malaria/ows"
COVER = "Malaria__202608_Global_Pf_Parasite_Rate"
BOX = [-18.0, -35.0, 52.0, 38.0]                 # west, south, east, north
STRIPS = [(-35, -20), (-20, -5), (-5, 10), (10, 25), (25, 38)]
YEARS = range(2000, 2026)
PX = 24                                          # cells per degree in the source


def strip(year, lat0, lat1):
    params = [("service", "WCS"), ("version", "2.0.1"), ("request", "GetCoverage"), ("coverageId", COVER),
              ("format", "image/tiff"), ("subset", f"Long({BOX[0]},{BOX[2]})"), ("subset", f"Lat({lat0},{lat1})"),
              ("subset", f'time("{year}-01-01T00:00:00.000Z")')]
    want = (int(round((lat1 - lat0) * PX)), int(round((BOX[2] - BOX[0]) * PX)))
    for k in range(6):
        try:
            r = requests.get(URL, params=params, timeout=300)
            r.raise_for_status()
            with rasterio.open(io.BytesIO(r.content)) as src:
                a = src.read(1)
            if a.shape != want:
                raise ValueError(f"got {a.shape}, wanted {want}")
            return a
        except Exception as e:                    # dropped or cut-off replies
            if k == 5:
                raise
            print("   retry:", str(e)[:80], flush=True)
            time.sleep(10 * (k + 1))


def fetch(year):
    path = os.path.join(CACHE, f"{year}.npy")
    if os.path.exists(path):
        return np.load(path)
    rows = [strip(year, a, b) for a, b in reversed(STRIPS)]      # north to south
    arr = np.vstack(rows).astype(np.float32)
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, arr)
    return arr


def half(a):
    """2 x 2 mean of the valid cells; -1 where all four are empty."""
    h, w = a.shape
    b = a.reshape(h // 2, 2, w // 2, 2)
    ok = b > -1
    n = ok.sum((1, 3))
    s = np.where(ok, b, 0).sum((1, 3))
    return np.where(n > 0, s / np.maximum(n, 1), -1).astype(np.float32)


def borders():
    g = gpd.read_file("zip://" + NE).cx[BOX[0]:BOX[2], BOX[1]:BOX[3]]
    rings = []
    for geom in g.geometry.simplify(0.03):
        for poly in getattr(geom, "geoms", [geom]):
            if poly.area < 0.02:
                continue
            rings.append([[round(x, 2), round(y, 2)] for x, y in poly.exterior.coords])
    json.dump(rings, open(os.path.join(OUT, "borders.json"), "w"), separators=(",", ":"))


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = []
    for y in YEARS:
        a = half(fetch(y))
        ok = a >= 0
        code = np.where(ok, np.clip(np.round(a * 200), 0, 200), 255).astype(np.uint8)
        Image.fromarray(code, "L").save(os.path.join(OUT, f"{y}.png"), optimize=True)
        # weight every cell by its true area (cells shrink away from the equator)
        lat = BOX[3] - (np.arange(a.shape[0]) + 0.5) / (PX / 2)
        wgt = np.cos(np.radians(lat))[:, None] * ok
        mean = float((np.where(ok, a, 0) * wgt).sum() / wgt.sum())
        high = float(((a > 0.2) * wgt).sum() / wgt.sum())
        meta.append({"year": y, "mean": round(mean, 4), "high": round(high, 4)})
        print(f"{y}: mean {mean:.1%}   land over 20%: {high:.1%}", flush=True)
    h, w = a.shape
    json.dump({"box": BOX, "w": w, "h": h, "step": 0.005, "years": meta},
              open(os.path.join(OUT, "malaria.json"), "w"), indent=1)
    borders()


if __name__ == "__main__":
    main()
