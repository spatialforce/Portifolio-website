"""Harare health facility access: walking time to the nearest facility along real roads, the people
beyond reach, and where five new clinics would reach the most of them.

    python harare_access.py     # reads cache/, writes cache/results.json

Inputs (fetched into cache/ once):
    facilities.geojson  the 151 Harare facilities from the web map's own layer (Province = 'Harare')
    boundary.json       Harare Province, OpenStreetMap relation 318467
    roads.json          every OpenStreetMap highway that can be walked (no motorways, no private roads)
    places.json         OpenStreetMap suburb and neighbourhood names
    pop.npy / pop.json  WorldPop R2025A, 2025 population per 3 arc-second cell (about 90 m)

Walking: WALK m per minute (4.5 km/h) along the road network, plus a straight walk from each cell to its
nearest road point. All distances in UTM zone 36S.
New sites: greedy maximal coverage. Candidates are road points among the people beyond REACH minutes;
each pick is the one that brings the most of those people within REACH minutes, then those people are
counted as served and the next pick is made.
"""
import json
import os

import numpy as np
import rasterio.features
import shapely
from affine import Affine
from pyproj import Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "cache")
WALK = 75.0
REACH = 30
BANDS = [15, 30, 45, 60]
NEW = 5
utm = Transformer.from_crs("EPSG:4326", "EPSG:32736", always_xy=True)


def load(name):
    return json.load(open(os.path.join(C, name), encoding="utf-8"))


def boundary():
    rel = load("boundary.json")["elements"][0]
    lines = [shapely.LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
             for m in rel["members"] if m["type"] == "way" and m.get("role", "outer") in ("outer", "")]
    return unary_union(list(polygonize(unary_union(lines))))


def graph():
    ids, xy, rows, cols, w = {}, [], [], [], []
    for way in load("roads.json")["elements"]:
        pts = way["geometry"]
        idx = []
        for nid, p in zip(way["nodes"], pts):
            if nid not in ids:
                ids[nid] = len(xy)
                xy.append(utm.transform(p["lon"], p["lat"]))
            idx.append(ids[nid])
        for a, b in zip(idx[:-1], idx[1:]):
            d = float(np.hypot(xy[a][0] - xy[b][0], xy[a][1] - xy[b][1]))
            rows += [a, b]; cols += [b, a]; w += [d, d]
    n = len(xy)
    return np.array(xy), coo_matrix((w, (rows, cols)), shape=(n, n)).tocsr()


def main():
    area = boundary()
    xy, G = graph()
    tree = cKDTree(xy)
    print("road points", len(xy))

    fac = load("facilities.geojson")["features"]
    fxy = np.array([utm.transform(*f["geometry"]["coordinates"]) for f in fac])
    fsnap, fnode = tree.query(fxy)
    dist = dijkstra(G, indices=np.unique(fnode), min_only=True)
    dist = np.asarray(dist, dtype=float)

    meta = load("pop.json")
    pop = np.load(os.path.join(C, "pop.npy"))
    h, w = pop.shape
    lon = meta["x0"] + (np.arange(w) + 0.5) * meta["res"]
    lat = meta["y0"] - (np.arange(h) + 0.5) * meta["res"]
    LON, LAT = np.meshgrid(lon, lat)
    inside = shapely.contains_xy(area, LON, LAT)
    cx, cy = utm.transform(LON[inside], LAT[inside])
    csnap, cnode = tree.query(np.c_[cx, cy])
    minutes = (dist[cnode] + csnap) / WALK
    people = pop[inside].astype(float)
    total = people.sum()

    by_band = {}
    lo = 0
    for b in BANDS + [10 ** 6]:
        by_band[f"{lo}-{b}"] = round(float(people[(minutes > lo) & (minutes <= b)].sum()))
        lo = b
    far = minutes > REACH
    print(f"people {total:,.0f}; beyond {REACH} min walk {people[far].sum():,.0f} ({people[far].sum() / total:.0%})")

    # suburbs: each far cell goes to its nearest named place
    places = [e for e in load("places.json")["elements"] if "name" in e.get("tags", {})]
    pxy = np.array([utm.transform(p["lon"], p["lat"]) for p in places])
    _, pi = cKDTree(pxy).query(np.c_[cx, cy][far])
    sub = {}
    for k, v in zip(pi, people[far]):
        n = places[k]["tags"]["name"]
        sub[n] = sub.get(n, 0) + v
    suburbs = [{"name": n, "people": round(v)} for n, v in sorted(sub.items(), key=lambda q: -q[1])[:8]]

    # new sites: greedy maximal coverage over the far cells
    far_idx = np.nonzero(far & (people > 0))[0]
    cand = np.unique(cnode[far_idx])
    weight = np.bincount(cnode[far_idx], weights=people[far_idx], minlength=len(xy))
    cand = cand[np.argsort(-weight[cand])][:2500]
    lim = REACH * WALK
    cover = []
    for s in range(0, len(cand), 100):
        d = dijkstra(G, indices=cand[s:s + 100], limit=lim)
        for row in d:
            t = row[cnode[far_idx]] + csnap[far_idx]
            cover.append(far_idx[t <= lim])
    served = np.zeros(len(people), bool)
    picks = []
    for _ in range(NEW):
        gain = [people[c[~served[c]]].sum() for c in cover]
        k = int(np.argmax(gain))
        served[cover[k]] = True
        lon_k, lat_k = Transformer.from_crs("EPSG:32736", "EPSG:4326", always_xy=True).transform(*xy[cand[k]])
        _, near = cKDTree(pxy).query(xy[cand[k]])
        picks.append({"lon": round(lon_k, 5), "lat": round(lat_k, 5), "people": round(float(gain[k])),
                      "near": places[near]["tags"]["name"]})
        print(f"  site {len(picks)} near {picks[-1]['near']}: {gain[k]:,.0f} people brought within {REACH} min")

    # walking time bands as polygons
    grid = np.zeros((h, w), np.uint8)
    band = np.digitize(minutes, BANDS, right=True) + 1          # 1 = up to 15 min ... 5 = over 60
    grid[inside] = band
    tf = Affine(meta["res"], 0, meta["x0"], 0, -meta["res"], meta["y0"])
    zones = {}
    for geom, v in rasterio.features.shapes(grid, mask=grid > 0, transform=tf):
        zones.setdefault(int(v), []).append(shapely.geometry.shape(geom))
    labels = ["Up to 15 min", "15 to 30 min", "30 to 45 min", "45 to 60 min", "Over 60 min"]
    keys = list(by_band)
    zone_feats = []
    for v in sorted(zones):
        g = unary_union(zones[v]).simplify(0.0004, preserve_topology=True)
        zone_feats.append({"band": v, "label": labels[v - 1], "people": by_band[keys[v - 1]], "geometry": shapely.geometry.mapping(g)})

    weak = [{"name": f["properties"]["Site_Name"], "type": f["properties"]["Type"], "km": f["properties"]["Distance_km_"],
             "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
            for f in fac if (f["properties"]["Distance_km_"] or 0) > 2]
    print("weak network facilities:", len(weak))

    out = {"total": round(total), "far": round(float(people[far].sum())), "reach": REACH, "bands": by_band,
           "suburbs": suburbs, "sites": picks, "zones": zone_feats, "weak": weak, "facilities": len(fac),
           "popSource": meta.get("source")}
    json.dump(out, open(os.path.join(C, "results.json"), "w", encoding="utf-8"))
    print("bands", by_band)
    print("suburbs", suburbs[:5])


if __name__ == "__main__":
    main()
