"""Suitability classes, area by class, by province and inside protected areas, and conditions at the records.
Cell areas use the exact area of each 30 arc-sec cell on a sphere of the authalic radius (6371.007 km). Writes data/summary.json."""
import json
import numpy as np, pandas as pd, geopandas as gpd
from rasterio.features import rasterize
from affine import Affine
Z = np.load("data/stack.npz"); M = Z["mask"]; T = Affine(*Z["transform"]); S = np.load("data/suit.npy"); H, W = M.shape
BR = [0.2, 0.4, 0.6]; NAMES = ["Not suitable", "Low", "Moderate", "High"]
C = np.full(M.shape, -1, "int8"); C[M] = np.digitize(S[M], BR)
R = 6371.007; lat_top = T.f + np.arange(H) * T.e
A = (np.radians(T.a) * R * R * np.abs(np.sin(np.radians(lat_top)) - np.sin(np.radians(lat_top + T.e))))[:, None] * np.ones((1, W))
np.save("data/classes.npy", C)
tot = A[M].sum(); out = {"land_km2": round(float(tot))}
out["classes"] = {NAMES[k]: [round(float(A[C == k].sum())), round(100 * float(A[C == k].sum()) / tot, 1)] for k in range(4)}
suit = C >= 2  # moderate or high = suitable habitat
out["suitable_km2"] = round(float(A[suit].sum())); out["suitable_pct"] = round(100 * float(A[suit].sum()) / tot, 1)

pv = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(4326); prov = {}
for _, r in pv.iterrows():
    m = rasterize([r.geometry], (H, W), transform=T, fill=0, default_value=1).astype(bool) & M
    a = A[m].sum(); prov[r.adm1_name] = dict(land=round(float(a)), high=round(float(A[m & (C == 3)].sum())), mod=round(float(A[m & (C == 2)].sum())),
                                            suit=round(float(A[m & suit].sum())), pct=round(100 * float(A[m & suit].sum()) / a, 1),
                                            mean=round(float(np.nanmean(S[m])), 3))
out["prov"] = dict(sorted(prov.items(), key=lambda x: -x[1]["suit"]))

pa = gpd.read_file("raw/wdpa.geojson")
KEEP = ["National Park", "Safari Area", "Recreation Park", "Sanctuary", "Botanical Reserve", "State Forest"]
pa = pa[pa.DESIG_ENG.isin(KEEP)]; pa.to_file("data/pa.gpkg")
PM = rasterize(pa.geometry, (H, W), transform=T, fill=0, default_value=1).astype(bool) & M
out["pa_n"] = len(pa); out["pa_km2"] = round(float(A[PM].sum())); out["pa_land_pct"] = round(100 * float(A[PM].sum()) / tot, 1)
out["suit_in_pa_km2"] = round(float(A[suit & PM].sum())); out["suit_in_pa_pct"] = round(100 * float(A[suit & PM].sum()) / float(A[suit].sum()), 1)
out["high_in_pa_pct"] = round(100 * float(A[(C == 3) & PM].sum()) / float(A[C == 3].sum()), 1)
out["pa_suit_pct"] = round(100 * float(A[suit & PM].sum()) / float(A[PM].sum()), 1)
by = {}
for dsg in KEEP:
    mm = rasterize(pa[pa.DESIG_ENG == dsg].geometry, (H, W), transform=T, fill=0, default_value=1).astype(bool) & M
    by[dsg] = dict(n=int((pa.DESIG_ENG == dsg).sum()), area=round(float(A[mm].sum())), suit=round(float(A[mm & suit].sum())))
out["pa_by"] = by
top = []
for _, r in pa.iterrows():
    mm = rasterize([r.geometry], (H, W), transform=T, fill=0, default_value=1).astype(bool) & M
    top.append((r.NAME, r.DESIG_ENG, round(float(A[mm & suit].sum())), round(float(A[mm].sum()))))
out["pa_top"] = sorted(top, key=lambda x: -x[2])[:8]

pr = pd.read_csv("data/records.csv"); q = lambda v: [round(float(x), 1) for x in np.percentile(pr[v], [5, 50, 95])]
out["rec"] = {v: q(v) for v in ["elev", "bio6", "bio11", "bio12", "bio15", "bio17", "bio1"]}
out["land"] = {v: [round(float(x), 1) for x in np.percentile(Z[v][M], [5, 50, 95])] for v in ["elev", "bio6", "bio11", "bio12", "bio15", "bio17", "bio1"]}
out["rec_class"] = {NAMES[k]: int((C[pr.r, pr.c] == k).sum()) for k in range(4)}
e = Z["elev"]; out["elev_band"] = {f"{a}-{b}": [round(100 * float(A[M & (e >= a) & (e < b) & suit].sum()) / max(float(A[M & (e >= a) & (e < b)].sum()), 1), 1),
                                              int(((pr.elev >= a) & (pr.elev < b)).sum())] for a, b in [(0, 600), (600, 900), (900, 1200), (1200, 1500), (1500, 3000)]}
json.dump(out, open("data/summary.json", "w"), indent=1); print(json.dumps(out, indent=0)[:3000])
