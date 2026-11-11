"""Elephant tracks in Etosha and Kruger: data build.

    cache/   files from fetch.py (Movebank Data Repository)
             Etosha: Tsalyuk et al. 2018, CC BY-NC 4.0
             Kruger: Thaker et al. 2019, CC0
    Earth Engine (project directed-sun-490915-m4): Sentinel-2 dry season 2022 backdrop, WDPA boundary for Kruger

Each park is resampled to one position every STEP hours. Positions are written as
uint16 pairs on the park's UTM grid (65535 = no fix), one row per elephant.

    python build.py    # writes public/webmaps/elephants/{etosha,kruger}.{bin,jpg} and parks.json
"""
import io
import json
import os
import zipfile

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
from PIL import Image
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "elephants")
PROJECT = "directed-sun-490915-m4"
STEP = 2            # hours between positions
MAXSPEED = 8        # km/h; faster jumps are GPS errors
IMG = 2000          # backdrop width in pixels

PARKS = {
    "etosha": dict(name="Etosha", country="Namibia", epsg=32733, box=(14.25, -19.55, 17.25, -18.25),
                   rain=(11, 4), csv="etosha.csv.zip", ref="etosha_ref.csv",
                   credit="Tsalyuk, Kilian, Reineking and Getz (2018), Movebank Data Repository, CC BY-NC 4.0"),
    "kruger": dict(name="Kruger", country="South Africa", epsg=32736, box=(30.95, -25.45, 32.1, -23.85),
                   rain=(10, 3), csv="kruger.csv", ref="kruger_ref.csv",
                   credit="Thaker, Gupte, Prins, Slotow and Vanak (2019), Movebank Data Repository, CC0"),
}


def tracks(p):
    path = os.path.join(CACHE, p["csv"])
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        d = pd.read_csv(z.open([n for n in z.namelist() if not n.startswith("__MACOSX")][0]), low_memory=False)
    else:
        d = pd.read_csv(path, low_memory=False)
    d = d[d["visible"].astype(str).str.lower() != "false"]
    if "manually-marked-outlier" in d:
        d = d[d["manually-marked-outlier"].astype(str).str.lower() != "true"]
    b = p["box"]
    d = d[d["location-long"].between(b[0], b[2]) & d["location-lat"].between(b[1], b[3])].copy()
    d["t"] = pd.to_datetime(d["timestamp"])
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{p['epsg']}", always_xy=True)
    d["x"], d["y"] = tr.transform(d["location-long"].values, d["location-lat"].values)
    return d.sort_values(["individual-local-identifier", "t"])


def clean(g):
    """Drop fixes that would need an impossible speed to reach."""
    keep = np.ones(len(g), bool)
    x, y, t = g.x.values, g.y.values, g.t.values.astype("datetime64[s]").astype(np.int64)
    last = 0
    for i in range(1, len(g)):
        dt = max(60, t[i] - t[last]) / 3600
        if np.hypot(x[i] - x[last], y[i] - y[last]) / 1000 / dt > MAXSPEED:
            keep[i] = False
        else:
            last = i
    return g[keep]


def backdrop(p, x0, y0, x1, y1, name):
    dest = os.path.join(OUT, f"{name}.jpg")
    if os.path.exists(dest):
        return
    w = IMG; h = int(round(IMG * (y1 - y0) / (x1 - x0)))
    s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
          .filterBounds(ee.Geometry.Rectangle(list(p["box"])))
          .filterDate("2022-06-01", "2022-10-15")                  # dry season, few clouds
          .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 15))
          .select(["B4", "B3", "B2"]).median())
    vis = s2.visualize(min=200, max=2600, gamma=1.15)
    # fetched in strips to stay inside Earth Engine's memory limit
    out = Image.new("RGB", (w, h))
    n = 4; sh = -(-h // n)
    for i in range(n):
        top = y1 - (y1 - y0) * i * sh / h
        hh = min(sh, h - i * sh)
        raw = ee.data.computePixels({
            "expression": vis, "fileFormat": "PNG",
            "grid": {"dimensions": {"width": w, "height": hh},
                     "affineTransform": {"scaleX": (x1 - x0) / w, "shearX": 0, "translateX": x0,
                                         "shearY": 0, "scaleY": -(y1 - y0) / h, "translateY": top},
                     "crsCode": f"EPSG:{p['epsg']}"},
        })
        out.paste(Image.open(io.BytesIO(raw)).convert("RGB"), (0, i * sh))
    out.save(dest, quality=82, optimize=True, progressive=True)


def boundary(name, p):
    if name == "etosha":
        g = gpd.read_file(f"zip://{os.path.join(CACHE, 'etosha_fence.zip')}")
        g = g.set_crs(4326, allow_override=True) if g.crs is None else g
        geom = g.to_crs(p["epsg"]).union_all()
    else:
        fc = ee.FeatureCollection("WCMC/WDPA/current/polygons").filter(ee.Filter.eq("NAME", "Kruger National Park"))
        gj = fc.geometry().simplify(100).getInfo()
        geom = gpd.GeoDataFrame.from_features([{"type": "Feature", "geometry": gj, "properties": {}}], crs=4326).to_crs(p["epsg"]).union_all()
    geom = geom.simplify(150)
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return [list(map(list, np.round(np.array(pp.exterior.coords), 0).astype(int).tolist())) for pp in polys if pp.area > 1e7]


def main():
    os.makedirs(OUT, exist_ok=True)
    ee.Initialize(project=PROJECT)
    meta = {}
    for name, p in PARKS.items():
        d = tracks(p)
        ref = pd.read_csv(os.path.join(CACHE, p["ref"]))
        sex = dict(zip(ref["animal-id"], ref["animal-sex"]))
        note = dict(zip(ref["animal-id"], ref.get("deployment-end-comments", pd.Series(dtype=str)).fillna(""))) if "deployment-end-comments" in ref else {}
        d = pd.concat([clean(g) for _, g in d.groupby("individual-local-identifier")])

        t0 = d.t.min().floor("D"); t1 = d.t.max().ceil("D")
        slots = int((t1 - t0) / pd.Timedelta(hours=STEP)) + 1
        pad = 3000
        x0, y0 = d.x.min() - pad, d.y.min() - pad
        x1, y1 = d.x.max() + pad, d.y.max() + pad
        # keep the backdrop at a 16:10-ish ratio around the tracks
        span = max(x1 - x0, (y1 - y0) * 1.5)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, x1 = cx - span / 2, cx + span / 2
        y0, y1 = cy - span / 3, cy + span / 3
        sc = 65534 / max(x1 - x0, y1 - y0)

        ids = sorted(d["individual-local-identifier"].unique(), key=lambda s: int("".join(c for c in s if c.isdigit()) or 0))
        arr = np.full((len(ids), slots, 2), 65535, np.uint16)
        animals = []
        for i, a in enumerate(ids):
            g = d[d["individual-local-identifier"] == a]
            k = ((g.t - t0) / pd.Timedelta(hours=STEP)).round().astype(int).values
            gx = np.clip((g.x.values - x0) * sc, 0, 65534); gy = np.clip((y1 - g.y.values) * sc, 0, 65534)
            # one fix per slot: the last one that falls in it
            arr[i, k, 0] = gx.astype(np.uint16); arr[i, k, 1] = gy.astype(np.uint16)
            # distance from the full-rate track, km
            km = float(np.hypot(np.diff(g.x.values), np.diff(g.y.values)).sum() / 1000)
            days = (g.t.max() - g.t.min()).total_seconds() / 86400
            cells = len(set(zip((g.x.values // 1000).astype(int), (g.y.values // 1000).astype(int))))
            animals.append(dict(id=a, sex={"m": "Bull", "f": "Cow"}.get(str(sex.get(a, "")), ""),
                                start=str(g.t.min().date()), end=str(g.t.max().date()),
                                km=round(km), perday=round(km / max(days, 1), 1), range=cells,
                                note=str(note.get(a, ""))))
            print(f"{name} {a:6} {animals[-1]['sex']:4} {len(g):7} fixes {km:7.0f} km  {km / max(days, 1):4.1f} km/day  {cells} km²")
        arr.tofile(os.path.join(OUT, f"{name}.bin"))
        backdrop(p, x0, y0, x1, y1, name)
        edge = [[[round((px - x0) * sc), round((y1 - py) * sc)] for px, py in r] for r in boundary(name, p)]
        meta[name] = dict(name=p["name"], country=p["country"], start=str(t0), step=STEP, slots=slots,
                          w=round((x1 - x0) * sc), h=round((y1 - y0) * sc), km=round((x1 - x0) / 1000),
                          rain=p["rain"], credit=p["credit"], animals=animals, edge=edge)
        print(name, slots, "slots,", os.path.getsize(os.path.join(OUT, f"{name}.bin")) // 1024, "KB")
    json.dump(meta, open(os.path.join(OUT, "parks.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
