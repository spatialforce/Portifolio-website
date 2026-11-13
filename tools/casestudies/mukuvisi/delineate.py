"""Catchment, drainage network and sub-catchments of the Mukuvisi River from the 30 m Copernicus DEM (pysheds, D8).
Steps: fill pits and depressions, resolve flats, D8 flow direction, flow accumulation, snap the outlet just above the
Manyame confluence, delineate the catchment, extract streams (>= 1 km2), Strahler order, then split the catchment into
sub-catchments at every junction where a tributary of >= MIN_TRIB km2 joins the main stem.
Output: data/catchment.gpkg, data/subcatch.gpkg, data/streams.gpkg, data/mainstem.gpkg, data/grid.npz, data/delin.json"""
import json, numpy as np, rasterio, geopandas as gpd, shapely
from rasterio.features import shapes, rasterize
if not hasattr(np, "in1d"): np.in1d = np.isin  # pysheds 0.5 on numpy 2
from pysheds.grid import Grid
from shapely.geometry import shape, LineString, Point

MIN_TRIB = 8.0  # km2
G = json.load(open("raw/grid.json")); R = G["res"]; CA = R * R / 1e6
grid = Grid.from_raster("raw/dem.tif"); dem = grid.read_raster("raw/dem.tif")
TR = grid.affine; CRS = "EPSG:32736"
fl = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
DIRS = (64, 128, 1, 2, 4, 8, 16, 32)  # N NE E SE S SW W NW
fdir = grid.flowdir(fl, dirmap=DIRS)
acc = grid.accumulation(fdir, dirmap=DIRS)

# outlet: a point on the OSM Mukuvisi line 600 m above its end at the Manyame, snapped to the largest accumulation within 120 m
riv = gpd.read_file("raw/osm_rivers.gpkg").to_crs(CRS)
mk = riv[riv.name.str.contains("Mukuvisi", na=False) & ~riv.name.str.contains("stream", na=False)]
line = shapely.ops.linemerge(mk.geometry.union_all())
parts = sorted(getattr(line, "geoms", [line]), key=lambda l: l.coords[-1][0])
low = parts[0]; end = Point(low.coords[-1]); p = low.interpolate(low.length - 600)
inv = ~TR; c, r = [int(v) for v in inv * (p.x, p.y)]
win = np.asarray(acc)[r - 4:r + 5, c - 4:c + 5]; dr, dc = np.unravel_index(np.argmax(win), win.shape)
r, c = r - 4 + dr, c - 4 + dc; ox, oy = TR * (c + 0.5, r + 0.5)
A = np.asarray(acc); F = np.asarray(fdir); HH, WW = A.shape
OFF = {64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)}


def upmask(rr, cc, within=None):
    """All cells that drain to (rr, cc): breadth-first search up the D8 directions."""
    m = np.zeros(A.shape, bool); m[rr, cc] = True; fr = (np.array([rr]), np.array([cc]))
    while fr[0].size:
        nr, nc = [], []
        for d, (a, b) in OFF.items():
            r2, c2 = fr[0] - a, fr[1] - b
            ok = (r2 >= 0) & (r2 < HH) & (c2 >= 0) & (c2 < WW)
            r2, c2 = r2[ok], c2[ok]; ok = (F[r2, c2] == d) & ~m[r2, c2]
            if within is not None: ok &= within[r2, c2]
            r2, c2 = r2[ok], c2[ok]; m[r2, c2] = True; nr.append(r2); nc.append(c2)
        fr = (np.concatenate(nr), np.concatenate(nc))
    return m


CM = upmask(r, c)
print("outlet", round(ox), round(oy), "area km2", round(CM.sum() * CA, 2), "acc", round(A[r, c] * CA, 2))

# streams (>= 1 km2) and Strahler order, cells processed from upstream (small accumulation) to downstream
ST = (A * CA >= 1.0) & CM
order = np.zeros(A.shape, "int8")
sr, sc = np.nonzero(ST); idx = np.argsort(A[sr, sc])
for rr, cc in zip(sr[idx], sc[idx]):
    o = [order[rr - a, cc - b] for d, (a, b) in OFF.items() if 0 <= rr - a < HH and 0 <= cc - b < WW and ST[rr - a, cc - b] and F[rr - a, cc - b] == d]
    if not o: order[rr, cc] = 1
    else:
        mx = max(o); order[rr, cc] = mx + 1 if o.count(mx) > 1 else mx

# main stem: walk upstream from the outlet along the largest upstream accumulation
def ups(rr, cc):
    out = []
    for d, (a, b) in OFF.items():
        r2, c2 = rr - a, cc - b
        if 0 <= r2 < HH and 0 <= c2 < WW and F[r2, c2] == d and CM[r2, c2]: out.append((r2, c2))
    return out

main = [(r, c)]; juncs = []
while True:
    u = ups(*main[-1])
    if not u: break
    u.sort(key=lambda q: A[q], reverse=True)
    for q in u[1:]:
        if A[q] * CA >= MIN_TRIB: juncs.append((len(main) - 1, q))
    main.append(u[0])
main_len = sum(np.hypot(main[i][0] - main[i + 1][0], main[i][1] - main[i + 1][1]) for i in range(len(main) - 1)) * R
print("main stem km", round(main_len / 1000, 2), "tributary junctions", len(juncs), [round(A[q] * CA, 1) for _, q in juncs])

# sub-catchments: each large tributary is one; the main-stem land between successive junctions is another
lab = np.zeros(A.shape, "int16"); k = 0; info = []
for mi, q in juncs:
    k += 1; cm = upmask(*q) & (lab == 0); lab[cm] = k
    info.append({"id": k, "kind": "tributary", "row": int(q[0]), "col": int(q[1]), "main_i": int(mi)})
for b in sorted(set([mi for mi, _ in juncs] + [0]), reverse=True):
    q = main[b]; cm = upmask(*q) & (lab == 0) & CM
    if cm.sum() * CA < 0.5: continue
    k += 1; lab[cm] = k; info.append({"id": k, "kind": "main stem", "row": int(q[0]), "col": int(q[1]), "main_i": int(b)})
# a main-stem sliver under 5 km2 joins the main-stem piece below it; then ids run upstream to downstream along the main stem
ms_ids = [d for d in info if d["kind"] == "main stem"]
for i, d in enumerate(ms_ids[:-1]):
    if (lab == d["id"]).sum() * CA < 5: lab[lab == d["id"]] = ms_ids[i + 1]["id"]; d["drop"] = True
info = [d for d in info if not d.get("drop")]
info.sort(key=lambda d: (-d["main_i"], d["kind"] != "tributary"))
new_lab = np.zeros_like(lab)
for i, d in enumerate(info, 1): new_lab[lab == d["id"]] = i; d["id"] = i
lab = new_lab; k = len(info)
print("sub-catchments", k, "unlabelled cells", int((CM & (lab == 0)).sum()))


def poly(mask, attrs):
    g = [shape(s) for s, v in shapes(mask.astype("uint8"), mask=mask, transform=TR) if v == 1]
    return gpd.GeoDataFrame([attrs], geometry=[shapely.unary_union(g)], crs=CRS)


gpd.GeoDataFrame(geometry=[shapely.unary_union([shape(s) for s, v in shapes(CM.astype("uint8"), mask=CM, transform=TR)])], crs=CRS).to_file("data/catchment.gpkg")
sub = gpd.pd.concat([poly(lab == d["id"], d) for d in info], ignore_index=True)
sub["area_km2"] = sub.area / 1e6; sub.to_file("data/subcatch.gpkg")
# stream lines: one segment per cell to its downstream cell, merged by order
segs = []
for rr, cc in zip(*np.nonzero(ST)):
    a, b = OFF.get(int(F[rr, cc]), (0, 0)); r2, c2 = rr + a, cc + b
    if (a, b) != (0, 0) and 0 <= r2 < A.shape[0] and 0 <= c2 < A.shape[1] and ST[r2, c2]:
        segs.append((int(order[rr, cc]), LineString([TR * (cc + 0.5, rr + 0.5), TR * (c2 + 0.5, r2 + 0.5)])))
sg = gpd.GeoDataFrame({"order": [s[0] for s in segs]}, geometry=[s[1] for s in segs], crs=CRS).dissolve("order").reset_index()
sg["geometry"] = sg.geometry.apply(shapely.ops.linemerge); sg.to_file("data/streams.gpkg")
ms = LineString([TR * (q[1] + 0.5, q[0] + 0.5) for q in main]); gpd.GeoDataFrame(geometry=[ms], crs=CRS).to_file("data/mainstem.gpkg")
np.savez_compressed("data/grid.npz", dem=np.asarray(dem), fill=np.asarray(fl), acc=A, fdir=F, catch=CM, lab=lab, order=order)
# check against the mapped river: mean distance from the OSM Mukuvisi line to the derived main stem
osm = line.intersection(gpd.GeoSeries([shape(s) for s, v in shapes(CM.astype("uint8"), mask=CM, transform=TR)], crs=CRS).union_all().buffer(30))
pts = [osm.interpolate(d) for d in np.arange(0, osm.length, 100)]
dd = np.array([ms.distance(q) for q in pts])
J = {"outlet_xy": [ox, oy], "osm_end_xy": [end.x, end.y], "area_km2": float(CM.sum() * CA), "main_km": main_len / 1000,
     "osm_main_km": float(line.length / 1000), "osm_dist_mean_m": float(dd.mean()), "osm_dist_p90_m": float(np.percentile(dd, 90)),
     "osm_within_100m": float((dd <= 100).mean()), "max_order": int(order.max()), "stream_km": float(sg.length.sum() / 1000),
     "n_sub": int(k), "z_min": float(np.asarray(dem)[CM].min()), "z_max": float(np.asarray(dem)[CM].max()), "z_mean": float(np.asarray(dem)[CM].mean())}
json.dump(J, open("data/delin.json", "w"), indent=1); print({a: round(b, 2) if isinstance(b, float) else b for a, b in J.items()})
print(sub[["id", "kind", "area_km2"]].round(2).to_string())
