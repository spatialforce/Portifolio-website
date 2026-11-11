"""Build the data for the "Where to open next" map for one province.

What goes in, and how far each part can be trusted:
  People   WorldPop 2020, 100 m grid. Checked against the 2022 census: Harare Province
           2,401,567 against 2,427,209 (1.1% low), Bulawayo 664,462 against 665,952.
  Wards    ZimStat ward boundaries via geoBoundaries (2020 delimitation).
  Outlets  OpenStreetMap and Overture Maps Places merged, duplicates within 60 m removed.
           Neither list is complete, so the map calls them "listed" outlets and never
           turns them into gap figures.

    python extract.py harare      # OpenStreetMap outlets (once)
    python analyse.py harare
Writes public/webmaps/sites/<city>.json
"""
import json
import math
import os
import sys

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import duckdb  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "sites")
PROVINCE = {"harare": ("Harare", 2427209)}   # boundary name, 2022 census population

CATS = {
    "pharmacy": {"label": "Pharmacies", "osm": ["pharmacy"], "ovt": ["pharmacy"]},
    "supermarket": {"label": "Supermarkets and grocers", "osm": ["supermarket"], "ovt": ["grocery_store", "organic_grocery_store"]},
    "bank": {"label": "Banks", "osm": ["bank"], "ovt": ["bank", "bank_or_credit_union"]},
    "fuel": {"label": "Fuel stations", "osm": ["fuel"], "ovt": ["gas_station"]},
}
MIN_CONF = 0.5   # Overture confidence below this is mostly stale or wrong listings
SAME_M = 60      # two listings of the same kind closer than this are one outlet


def main(city):
    name, census = PROVINCE[city]
    prov = gpd.read_file(os.path.join(HERE, "raw", "zwe_ADM1.geojson"))
    prov = prov[prov.shapeName == name].geometry.iloc[0]
    wards = gpd.read_file(os.path.join(HERE, "raw", "zwe_ADM3.geojson"))
    wards = wards[wards.representative_point().within(prov)].reset_index(drop=True)
    w, s, e, n = prov.bounds
    lat0 = (s + n) / 2
    kx, ky = 111320 * math.cos(math.radians(lat0)), 110540

    # ---- people, clipped to the province ----
    with rasterio.open(os.path.join(HERE, "raw", "zwe_pop_2020.tif")) as src:
        pop, tr = mask(src, [prov], crop=True, nodata=0)
    pop = np.where(pop[0] > 0, pop[0], 0).astype(np.float64)
    ward_id = rasterize(((g, i + 1) for i, g in enumerate(wards.geometry)), out_shape=pop.shape, transform=tr, fill=0, dtype="int32")
    total = pop.sum()
    print(f"people: WorldPop {total:,.0f} against census {census:,} ({(total - census) / census * 100:+.1f}%)")

    # ---- outlets ----
    osm = json.load(open(os.path.join(HERE, "cache", city, "pois.json")))
    con = duckdb.connect()
    ovt = con.execute(f"SELECT name, cat, confidence, lon, lat FROM read_parquet('{os.path.join(HERE, 'cache', city, 'overture_all.parquet').replace(os.sep, '/')}')").fetchall()
    from shapely.geometry import Point
    from shapely.prepared import prep
    pp = prep(prov)
    cats_out, counts = {}, {}
    for c, spec in CATS.items():
        pts = [(p["lon"], p["lat"], p["name"] or p["brand"], "OpenStreetMap") for p in osm if p["cat"] == c]
        pts += [(lon, lat, nm or "", "Overture") for nm, cat, conf, lon, lat in ovt if cat in spec["ovt"] and (conf or 0) >= MIN_CONF]
        pts = [p for p in pts if pp.contains(Point(p[0], p[1]))]
        # merge duplicates: keep the first of any group within SAME_M
        xy = np.array([[p[0] * kx, p[1] * ky] for p in pts]) if pts else np.zeros((0, 2))
        keep, used = [], np.zeros(len(pts), bool)
        tree = cKDTree(xy) if len(pts) else None
        for i in range(len(pts)):
            if used[i]:
                continue
            group = tree.query_ball_point(xy[i], SAME_M)
            used[group] = True
            srcs = sorted({pts[j][3] for j in group})
            nm = next((pts[j][2] for j in group if pts[j][2]), "")
            keep.append([round(pts[i][0], 5), round(pts[i][1], 5), nm, " and ".join(srcs)])
        counts[c] = {"osm": sum(1 for p in pts if p[3] == "OpenStreetMap"), "ovt": sum(1 for p in pts if p[3] == "Overture"), "merged": len(keep)}
        cats_out[c] = {"label": spec["label"], "pois": keep, "sources": counts[c]}
        print(f"  {c:12s} OpenStreetMap {counts[c]['osm']:4d}, Overture {counts[c]['ovt']:4d}, merged {len(keep):4d}")

    # ---- wards: people, area, density, listed outlets ----
    wards_m = wards.to_crs(32736)
    ward_out = []
    for i, row in wards.iterrows():
        p = float(pop[ward_id == i + 1].sum())
        area = wards_m.geometry.iloc[i].area / 1e6
        g = row.geometry.simplify(0.0004, preserve_topology=True)
        polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
        rings = [[[round(x, 5), round(y, 5)] for x, y in poly.exterior.coords] for poly in polys]
        ward_out.append({"name": row.shapeName, "people": round(p), "km2": round(area, 2), "rings": rings})

    # ---- people grid for the catchment counts: populated cells only ----
    rows, cols = np.nonzero(pop > 0)
    data = {
        "city": "Harare Province", "census": census, "worldpop": round(total),
        "grid": {"lon0": tr.c, "lat0": tr.f, "dlon": tr.a, "dlat": tr.e},
        "cells": np.column_stack([rows, cols, np.round(pop[rows, cols] * 10).astype(int)]).ravel().tolist(),
        "wards": ward_out, "cats": cats_out,
        "bounds": [w, s, e, n],
    }
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{city}.json")
    json.dump(data, open(path, "w"), separators=(",", ":"))
    print(f"wrote {path} ({os.path.getsize(path) / 1e6:.1f} MB), {len(ward_out)} wards")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "harare")
