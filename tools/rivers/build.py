"""Rivers of Africa: HydroRIVERS (HydroSHEDS) prepared for a WebGL map.

  rivers     every reach draining at least MIN_UPLAND km2, joined into continuous lines between
             confluences, simplified, projected (Lambert azimuthal equal area, centre 20E 0N)
  systems    each river system (all reaches sharing one outlet): name from Natural Earth where it
             matches, main stem length, basin area, flow at the mouth, countries, where it ends
  land       African countries and large lakes from Natural Earth, for the background

Writes public/webmaps/rivers/rivers.bin, systems.json, land.json
    python build.py
"""
import json
import os
import struct
from collections import defaultdict

import geopandas as gpd
import numpy as np
import pyogrio
from pyproj import Transformer
from shapely.geometry import LineString
from shapely.strtree import STRtree

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "rivers")
RIV = "zip://" + os.path.join(HERE, "raw", "hydrorivers_af.zip") + "!HydroRIVERS_v10_af_shp/HydroRIVERS_v10_af.shp"
MIN_UPLAND = 1000
TOL_KM = 1.2
LAEA = "+proj=laea +lat_0=0 +lon_0=20 +datum=WGS84 +units=km"
TO = Transformer.from_crs("EPSG:4326", LAEA, always_xy=True)
ALIAS = {"Rosetta Branch": "Nile", "Damietta Branch": "Nile"}   # Natural Earth names the Nile's delta arms


def sea_of(lon, lat, endo):
    if endo:
        return "an inland basin"
    if lat > 30 and -6 < lon < 37:
        return "the Mediterranean"
    if 32 < lon < 44 and 12 < lat < 30:
        return "the Red Sea"
    if lon > 20 and lat < 12:
        return "the Indian Ocean"
    return "the Atlantic"


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pyogrio.read_dataframe(RIV, where=f"UPLAND_SKM >= {MIN_UPLAND}",
                                columns=["HYRIV_ID", "NEXT_DOWN", "MAIN_RIV", "LENGTH_KM", "DIST_DN_KM", "DIST_UP_KM", "UPLAND_SKM", "ENDORHEIC", "DIS_AV_CMS"])
    print(len(df), "reaches")
    ids = df.HYRIV_ID.values
    row = {h: i for i, h in enumerate(ids)}
    nxt = np.array([row.get(n, -1) for n in df.NEXT_DOWN.values])
    up = np.bincount(nxt[nxt >= 0], minlength=len(df))

    # ---- join reaches into chains: a chain carries on downstream while the next reach has a single upstream reach
    starts = [i for i in range(len(df)) if up[i] != 1]
    seen = np.zeros(len(df), bool)
    geoms = df.geometry.values
    chains = []
    for s in starts:
        i, parts = s, []
        while i >= 0 and not seen[i]:
            seen[i] = True
            parts.append(i)
            j = nxt[i]
            if j < 0 or up[j] != 1:
                if j >= 0:
                    parts.append(-j - 1)      # remember the confluence it joins, to close the gap
                break
            i = j
        chains.append(parts)

    # ---- system ids, dense
    sys_ids = df.MAIN_RIV.values
    sys_index = {m: k for k, m in enumerate(sorted(set(sys_ids)))}

    # ---- geometry: project, simplify, quantise
    xs_all, ys_all, d_all, q_all, line_len, line_sys = [], [], [], [], [], []
    for parts in chains:
        join = None
        if parts and parts[-1] < 0:
            join = -parts.pop() - 1
        coords, dist, flow = [], [], []
        for i in parts:
            c = list(geoms[i].coords)
            if coords:
                c = c[1:]
            n = len(c)
            # distance to the outlet along this reach, from its upstream end to its downstream end
            d0 = df.DIST_DN_KM.values[i] + df.LENGTH_KM.values[i]
            d1 = df.DIST_DN_KM.values[i]
            dist += list(np.linspace(d0, d1, n + (0 if coords else 0))) if n else []
            flow += [df.DIS_AV_CMS.values[i]] * n
            coords += c
        if join is not None:
            jc = geoms[join].coords[0]
            coords.append(jc); dist.append(df.DIST_DN_KM.values[join] + df.LENGTH_KM.values[join]); flow.append(df.DIS_AV_CMS.values[join])
        if len(coords) < 2:
            continue
        x, y = TO.transform(*np.array(coords).T)
        ls = LineString(np.column_stack([x, y])).simplify(TOL_KM, preserve_topology=False)
        sx, sy = np.array(ls.coords).T
        # carry distance and flow over to the simplified vertices by nearest original vertex
        tree_idx = [int(np.argmin((x - a) ** 2 + (y - b) ** 2)) for a, b in zip(sx, sy)]
        xs_all.append(sx); ys_all.append(sy)
        d_all.append(np.array(dist)[tree_idx]); q_all.append(np.array(flow)[tree_idx])
        line_len.append(len(sx)); line_sys.append(sys_index[sys_ids[parts[0]]])
    X = np.concatenate(xs_all); Y = np.concatenate(ys_all); D = np.concatenate(d_all); Q = np.concatenate(q_all)
    x0, x1, y0, y1 = X.min(), X.max(), Y.min(), Y.max()
    scale = 65000 / max(x1 - x0, y1 - y0)
    qx = np.round((X - x0) * scale).astype(np.uint16); qy = np.round((Y - y0) * scale).astype(np.uint16)
    qd = np.clip(np.round(D), 0, 65535).astype(np.uint16)
    qf = np.clip(np.round(np.log10(np.maximum(Q, 0.01)) * 40 + 80), 0, 255).astype(np.uint8)   # log flow, 0.01 to about 10^4 m3/s
    with open(os.path.join(OUT, "rivers.bin"), "wb") as f:
        f.write(struct.pack("<4I", len(line_len), len(X), 0, 0))
        f.write(np.array(line_len, np.uint32).tobytes()); f.write(np.array(line_sys, np.uint32).tobytes())
        f.write(qx.tobytes()); f.write(qy.tobytes()); f.write(qd.tobytes()); f.write(qf.tobytes())
    print(f"{len(line_len):,} lines, {len(X):,} vertices, {os.path.getsize(os.path.join(OUT, 'rivers.bin')) / 1e6:.1f} MB")

    # ---- systems
    outlets = df[df.NEXT_DOWN == 0].set_index("MAIN_RIV")
    ne = gpd.read_file("zip://" + os.path.join(HERE, "raw", "ne_rivers.zip"))
    ne["label"] = ne["name_en"].where(ne["name_en"].notna(), ne["name"]) if "name_en" in ne else ne["name"]
    ne = ne[ne.label.notna() & (ne.featurecla.str.contains("River", na=False))].to_crs(LAEA)
    ne_tree = STRtree(list(ne.geometry))
    countries = gpd.read_file("zip://" + os.path.join(HERE, "raw", "ne_countries.zip"))
    africa = countries[countries.CONTINENT == "Africa"].to_crs(LAEA)
    big = outlets.sort_values("UPLAND_SKM", ascending=False)
    systems = {}
    mids = df.geometry.interpolate(0.5, normalized=True)
    mx, my = TO.transform(mids.x.values, mids.y.values)
    pts = gpd.GeoDataFrame({"sys": sys_ids, "up": df.UPLAND_SKM.values}, geometry=gpd.points_from_xy(mx, my), crs=LAEA)
    hit = gpd.sjoin(pts, africa[["NAME", "geometry"]], predicate="within", how="left")
    by_sys_country = hit.groupby("sys").NAME.agg(lambda v: sorted(set(x for x in v if isinstance(x, str))))
    for rank, (m, o) in enumerate(big.iterrows()):
        if rank >= 400:
            break
        # name: the Natural Earth river nearest to the main stem (the reaches carrying the most water)
        stem = pts[(pts.sys == m)].nlargest(40, "up")
        votes = defaultdict(float)
        for g, u in zip(stem.geometry, stem.up):
            k = ne_tree.nearest(g)
            if ne.geometry.iloc[k].distance(g) < 8:
                votes[ALIAS.get(ne.label.iloc[k], ne.label.iloc[k])] += u
        name = max(votes, key=votes.get) if votes else None
        ox, oy = o.geometry.coords[-1]
        systems[str(sys_index[m])] = {
            "name": name, "km": round(float(o.DIST_UP_KM + o.LENGTH_KM)), "basin": round(float(o.UPLAND_SKM)),
            "flow": round(float(o.DIS_AV_CMS), 1), "ends": sea_of(ox, oy, int(o.ENDORHEIC)),
            "countries": by_sys_country.get(m, []),
        }
    named = {k: v for k, v in systems.items() if v["name"]}
    print(f"{len(systems)} systems described, {len(named)} named; largest:",
          [(v["name"], v["basin"]) for v in list(systems.values())[:8]])
    json.dump({"bounds": [float(x0), float(y0), float(x1), float(y1)], "scale": scale, "systems": systems},
              open(os.path.join(OUT, "systems.json"), "w"), separators=(",", ":"))

    # ---- land and lakes
    def rings(gdf, tol):
        out = []
        for g in gdf.geometry.simplify(tol):
            for p in getattr(g, "geoms", [g]):
                c = np.array(p.exterior.coords)
                if len(c) >= 4:
                    out.append([[round(float(a), 1), round(float(b), 1)] for a, b in c])
        return out
    lakes = gpd.read_file("zip://" + os.path.join(HERE, "raw", "ne_lakes.zip")).to_crs(LAEA)
    lakes = lakes[lakes.intersects(africa.union_all().buffer(50))]
    lakes = lakes[lakes.area > 300]
    json.dump({"land": rings(africa, 3), "lakes": rings(lakes, 1.5)}, open(os.path.join(OUT, "land.json"), "w"), separators=(",", ":"))
    print("land and", len(lakes), "lakes written")


if __name__ == "__main__":
    main()
