"""Cyclone tracks: every tropical storm in the south-west Indian Ocean since 1980.

    python build.py    # writes public/webmaps/cyclones.json

Source: IBTrACS v04r01, South Indian basin (raw/ibtracs_SI.csv, from NOAA NCEI). Main and provisional
tracks (the latest seasons are provisional); spur tracks dropped. A storm renamed on crossing from the
Australian region ("Eline:Leone") keeps its first, south-west Indian Ocean name.
Wind is the JTWC one-minute wind (USA_WIND, knots), else the WMO agency wind. A storm is kept if it
reached 34 kt (tropical storm) inside BOX. Land from Natural Earth 10 m.

Each storm: name, season, start date, peak wind (km/h), countries it crossed, and its points as
[lon, lat, wind km/h, hours since the first point].
"""
import csv
import json
import os
from datetime import datetime

import geopandas as gpd
import numpy as np
import shapely

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw", "ibtracs_SI.csv")
NE = os.path.join(HERE, "..", "corridors", "raw", "ne_10m_admin_0_countries.zip")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "cyclones.json")
BOX = (20, -37, 72, -6)
FIRST = 1980
KT = 1.852
NAMES = {"MOZ": "Mozambique", "MDG": "Madagascar", "MWI": "Malawi", "ZWE": "Zimbabwe", "ZAF": "South Africa",
         "SWZ": "Eswatini", "MUS": "Mauritius", "COM": "Comoros", "TZA": "Tanzania", "FRA": "Réunion"}


def num(v):
    v = v.strip()
    return float(v) if v else None


def main():
    world = gpd.read_file(f"zip://{NE}")
    world["geometry"] = world.geometry.intersection(shapely.box(BOX[0] - 15, BOX[1] - 10, BOX[2] + 10, BOX[3] + 10))
    world = world[~world.geometry.is_empty]
    land = world[world.ADM0_A3.isin(NAMES)]

    storms = {}
    with open(RAW, newline="", encoding="utf-8") as f:
        rows = csv.reader(f)
        head = next(rows)
        next(rows)                                   # units row
        ix = {k: head.index(k) for k in ["SID", "SEASON", "NAME", "ISO_TIME", "LAT", "LON", "USA_WIND", "WMO_WIND", "TRACK_TYPE"]}
        for r in rows:
            if r[ix["TRACK_TYPE"]].startswith("spur") or int(r[ix["SEASON"]]) < FIRST:
                continue
            w = num(r[ix["USA_WIND"]])
            if w is None:
                w = num(r[ix["WMO_WIND"]])
            t = datetime.strptime(r[ix["ISO_TIME"]], "%Y-%m-%d %H:%M:%S")
            s = storms.setdefault(r[ix["SID"]], {"name": r[ix["NAME"]].title(), "season": int(r[ix["SEASON"]]), "pts": []})
            s["pts"].append((float(r[ix["LON"]]), float(r[ix["LAT"]]), w, t))

    out = []
    for sid, s in storms.items():
        p = s["pts"]
        lon = np.array([q[0] for q in p]); lat = np.array([q[1] for q in p])
        wind = np.array([q[2] if q[2] is not None else np.nan for q in p])
        inbox = (lon >= BOX[0]) & (lon <= BOX[2]) & (lat >= BOX[1]) & (lat <= BOX[3])
        if not inbox.any() or not np.nanmax(np.where(inbox, wind, np.nan), initial=0) >= 34:
            continue
        wind = np.nan_to_num(wind, nan=0)
        hit = []
        for code, geom in zip(land.ADM0_A3, land.geometry):
            if shapely.contains_xy(geom, lon, lat).any():
                hit.append(NAMES[code])
        t0 = p[0][3]
        name = s["name"].split(":")[0]
        name = name if name not in ("Unnamed", "Not_Named") else "Unnamed"
        out.append({"id": sid, "name": name, "season": s["season"], "start": t0.strftime("%Y-%m-%d"),
                    "days": round((p[-1][3] - t0).total_seconds() / 86400, 1),
                    "peak": round(float(wind.max()) * KT), "hit": hit,
                    "pts": [[round(q[0], 2), round(q[1], 2), round((q[2] or 0) * KT), round((q[3] - t0).total_seconds() / 3600)]
                            for i, q in enumerate(p) if i % 2 == 0 or i == len(p) - 1]})
    out.sort(key=lambda s: s["start"])

    rings = []
    for g in world.geometry.simplify(0.03):
        for poly in getattr(g, "geoms", [g]):
            if poly.area > 0.002:
                rings.append([[round(x, 2), round(y, 2)] for x, y in poly.exterior.coords])

    json.dump({"box": BOX, "first": FIRST, "land": rings, "storms": out}, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    hits = [s for s in out if s["hit"]]
    print(len(out), "storms,", len(hits), "crossed land;", os.path.getsize(OUT) // 1024, "KB")
    for s in sorted(out, key=lambda s: -s["peak"])[:5]:
        print(" ", s["name"], s["season"], s["peak"], "km/h", s["days"], "days", s["hit"])
    for n in ("Freddy", "Idai", "Eline", "Kenneth", "Gombe", "Chido", "Dineo"):
        for s in out:
            if s["name"] == n:
                print(" ", n, s["season"], s["peak"], s["days"], s["hit"])


if __name__ == "__main__":
    main()
