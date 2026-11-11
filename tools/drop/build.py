"""One drop of rain: the data behind the web map.

  network  HydroRIVERS reaches draining at least MIN_UPLAND km2, joined into chains between
           confluences, each chain linked to the chain it flows into. Projected (Lambert azimuthal
           equal area, centre 20E 0N, km), simplified, with the country under every vertex.
  basins   HydroBASINS level 12 rasterised on a 2.5 km grid; each cell holds the chain its basin
           drains into, so a click is routed to the correct side of a watershed divide. Basins too
           small to hold a river point to the first basin downstream that does.
  names    the main rivers named from Natural Earth by matching their main stems.

Read in chunks: the laptop has little free memory.
Writes public/webmaps/drop/net.bin, basins.png, meta.json
    python build.py
"""
import json
import os
import struct
from collections import defaultdict

import geopandas as gpd
import numpy as np
import pyogrio
from PIL import Image
from pyproj import Transformer
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely import simplify
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
OUT = os.path.join(ROOT, "public", "webmaps", "drop")
RAWR = os.path.join(ROOT, "tools", "rivers", "raw")
RIV = "zip://" + os.path.join(RAWR, "hydrorivers_af.zip") + "!HydroRIVERS_v10_af_shp/HydroRIVERS_v10_af.shp"
BAS = "zip://" + os.path.join(HERE, "raw", "hybas_af_lev12.zip") + "!hybas_af_lev12_v1c.shp"
LAEA = "+proj=laea +lat_0=0 +lon_0=20 +datum=WGS84 +units=km"
TO = Transformer.from_crs("EPSG:4326", LAEA, always_xy=True)
MIN_UPLAND = 300
CELL = 2.5
TOL = 0.8
ALIAS = {"Rosetta Branch": "Nile", "Damietta Branch": "Nile"}


def sea_of(lon, lat, endo):
    if endo:
        return "an inland basin"
    if lat > 30 and -6 < lon < 37:
        return "the Mediterranean Sea"
    if 32 < lon < 44 and 12 < lat < 30:
        return "the Red Sea"
    if lon > 20 and lat < 12:
        return "the Indian Ocean"
    return "the Atlantic Ocean"


def main():
    os.makedirs(OUT, exist_ok=True)
    countries = gpd.read_file("zip://" + os.path.join(RAWR, "ne_countries.zip"))
    countries = countries[countries.CONTINENT == "Africa"][["NAME", "geometry"]].reset_index(drop=True).to_crs(LAEA)
    ctree = STRtree(list(countries.geometry))

    cols = ["HYRIV_ID", "NEXT_DOWN", "MAIN_RIV", "LENGTH_KM", "UPLAND_SKM", "ENDORHEIC", "HYBAS_L12", "DIST_DN_KM"]
    n_all = pyogrio.read_info(RIV)["features"]
    R = defaultdict(list)
    geoms = []
    for skip in range(0, n_all, 80000):
        df = pyogrio.read_dataframe(RIV, skip_features=skip, max_features=80000, columns=cols)
        df = df[df.UPLAND_SKM >= MIN_UPLAND]
        for c in cols:
            R[c] += list(df[c].values)
        for g in df.geometry.values:
            xy = np.asarray(g.coords)
            x, y = TO.transform(xy[:, 0], xy[:, 1])
            geoms.append((np.column_stack([x, y]), xy[-1]))
        print(f"  read {min(skip + 80000, n_all):,} of {n_all:,}, kept {len(geoms):,}", flush=True)
        del df
    R = {k: np.array(v) for k, v in R.items()}
    n = len(geoms)
    row = {h: i for i, h in enumerate(R["HYRIV_ID"])}
    nxt = np.array([row.get(h, -1) for h in R["NEXT_DOWN"]])
    up = np.bincount(nxt[nxt >= 0], minlength=n)

    # ---- chains between confluences
    chain_of = np.full(n, -1)
    chains = []
    for s in (i for i in range(n) if up[i] != 1):
        i, parts = s, []
        while i >= 0 and chain_of[i] < 0:
            chain_of[i] = len(chains); parts.append(i)
            j = nxt[i]
            if j < 0 or up[j] != 1:
                break
            i = j
        chains.append(parts)
    C = len(chains)
    c_next = np.array([chain_of[nxt[p[-1]]] if nxt[p[-1]] >= 0 else -1 for p in chains], np.int32)

    # ---- names for the big systems: vote with Natural Earth along the largest reaches
    ne = gpd.read_file("zip://" + os.path.join(RAWR, "ne_rivers.zip"))
    ne["label"] = ne["name_en"].where(ne["name_en"].notna(), ne["name"])
    ne = ne[ne.label.notna() & ne.featurecla.str.contains("River", na=False)].to_crs(LAEA)
    ntree = STRtree(list(ne.geometry))
    votes = defaultdict(lambda: defaultdict(float))
    for i in np.argsort(-R["UPLAND_SKM"])[:60000]:
        xy = geoms[i][0]; p = Point(xy[len(xy) // 2])
        k = ntree.nearest(p)
        if ne.geometry.iloc[k].distance(p) < 6:
            votes[int(R["MAIN_RIV"][i])][ALIAS.get(ne.label.iloc[k], ne.label.iloc[k])] += R["UPLAND_SKM"][i]
    # a chain is named after the Natural Earth river nearest to its middle, when close
    sysname = {m: max(v, key=v.get) for m, v in votes.items()}

    # ---- geometry, per vertex country, per chain data
    xs, ys, cc, vlen, clen, cname, cend = [], [], [], [], [], [], []
    names = []
    name_ix = {}
    for parts in chains:
        pts = [geoms[parts[0]][0]] + [geoms[i][0][1:] for i in parts[1:]]
        j = nxt[parts[-1]]
        if j >= 0:
            pts.append(geoms[j][0][:1])           # close the gap to the confluence
        xy = np.concatenate(pts)
        c2 = np.asarray(simplify(LineString(xy), TOL).coords)
        vc = []
        for x, y in c2:
            p = Point(x, y); k = ctree.query(p, predicate="within")
            vc.append(int(k[0]) if len(k) else 255)
        xs.append(c2[:, 0]); ys.append(c2[:, 1]); cc += vc; vlen.append(len(c2))
        clen.append(float(R["LENGTH_KM"][parts].sum()))
        # name: nearest Natural Earth river to the chain's middle
        mid = Point(c2[len(c2) // 2]); k = ntree.nearest(mid)
        nm = ALIAS.get(ne.label.iloc[k], ne.label.iloc[k]) if ne.geometry.iloc[k].distance(mid) < 4 else ""
        if nm not in name_ix:
            name_ix[nm] = len(names); names.append(nm)
        cname.append(name_ix[nm])
        last = parts[-1]
        cend.append(sea_of(*geoms[last][1], int(R["ENDORHEIC"][last])) if nxt[last] < 0 else "")
    ends = sorted(set(e for e in cend if e))
    X = np.concatenate(xs); Y = np.concatenate(ys)
    x0, y0, x1, y1 = X.min(), Y.min(), X.max(), Y.max()
    scale = 65000 / max(x1 - x0, y1 - y0)
    with open(os.path.join(OUT, "net.bin"), "wb") as f:
        f.write(struct.pack("<4I", C, len(X), 0, 0))
        f.write(np.array(vlen, np.uint16).tobytes())
        f.write(c_next.tobytes())
        f.write(np.clip(np.round(np.array(clen) * 10), 0, 65535).astype(np.uint16).tobytes())
        f.write(np.array(cname, np.uint16).tobytes())
        f.write(np.array([ends.index(e) + 1 if e else 0 for e in cend], np.uint8).tobytes())
        f.write(np.round((X - x0) * scale).astype(np.uint16).tobytes())
        f.write(np.round((Y - y0) * scale).astype(np.uint16).tobytes())
        f.write(np.array(cc, np.uint8).tobytes())
    print(f"network: {C:,} chains from {n:,} reaches, {len(X):,} vertices, {os.path.getsize(os.path.join(OUT, 'net.bin')) / 1e6:.1f} MB")

    # ---- basins grid
    by_basin = {}
    for i, b in enumerate(R["HYBAS_L12"]):
        b = int(b)
        if b not in by_basin or R["UPLAND_SKM"][i] > R["UPLAND_SKM"][by_basin[b]]:
            by_basin[b] = i
    W = int(np.ceil((x1 - x0) / CELL)) + 2; H = int(np.ceil((y1 - y0) / CELL)) + 2
    tr = from_origin(x0 - CELL, y1 + CELL, CELL, CELL)
    bn = pyogrio.read_info(BAS)["features"]
    bas_next, parts_saved = {}, []
    for skip in range(0, bn, 40000):
        bdf = pyogrio.read_dataframe(BAS, skip_features=skip, max_features=40000, columns=["HYBAS_ID", "NEXT_DOWN"]).to_crs(LAEA)
        bas_next.update({int(h): int(m) for h, m in zip(bdf.HYBAS_ID, bdf.NEXT_DOWN)})
        a = rasterize(((g, float(h)) for h, g in zip(bdf.HYBAS_ID, bdf.geometry)), out_shape=(H, W), transform=tr, fill=0, dtype="float64").astype(np.int64)
        p = os.path.join(HERE, "raw", f"bas_{skip}.npy"); np.save(p, a); parts_saved.append(p)
        print(f"  basins {min(skip + 40000, bn):,} of {bn:,}", flush=True)
        del bdf, a

    def chain_for(h):
        for _ in range(500):
            if not h:
                return -1
            if h in by_basin:
                return int(chain_of[by_basin[h]])
            h = bas_next.get(h, 0)
        return -1
    grid = np.zeros((H, W), np.uint32)
    memo = {}
    for p in parts_saved:
        a = np.load(p); m = a > 0
        uniq, inv = np.unique(a[m], return_inverse=True)
        vals = np.array([memo.setdefault(int(h), chain_for(int(h))) for h in uniq], np.int64) + 1
        grid[m] = vals[inv].astype(np.uint32)
        os.remove(p)
    rgb = np.dstack([(grid >> 16) & 255, (grid >> 8) & 255, grid & 255]).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(os.path.join(OUT, "basins.png"), optimize=True)
    print(f"basins grid {W} x {H}, {os.path.getsize(os.path.join(OUT, 'basins.png')) / 1e6:.1f} MB")

    json.dump({"bounds": [float(x0), float(y0), float(x1), float(y1)], "scale": scale,
               "grid": {"x0": float(x0 - CELL), "y1": float(y1 + CELL), "cell": CELL, "w": W, "h": H},
               "countries": list(countries.NAME), "names": names, "ends": ends},
              open(os.path.join(OUT, "meta.json"), "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
