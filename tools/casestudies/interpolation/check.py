"""Independent checks of the interpolated surfaces.
1. CHIRPS v2.0 monthly climatology from the rainfall study (rainfall/rast/monthly_clim.tif, sum of 12 months; a later period,
   so only the pattern and rough level are compared), sampled at every 0.025 degree cell and at the stations.
2. FAO AQUASTAT long-term mean for Zimbabwe (657 mm/yr).
Output: data/check.json"""
import json, numpy as np, pandas as pd, rasterio
from rasterio.transform import rowcol
G = np.load("data/surfaces.npz"); M = G["mask"]; x0, y1, res = float(G["x0"]), float(G["y1"]), float(G["res"])
H, W = M.shape
lon = x0 + (np.arange(W) + 0.5) * res; lat = y1 - (np.arange(H) + 0.5) * res; LO, LA = np.meshgrid(lon, lat)
with rasterio.open("../rainfall/rast/monthly_clim.tif") as s:
    A = s.read().astype(float); A[A < 0] = np.nan; ann = A.sum(0); tr = s.transform
r, c = rowcol(tr, LO[M], LA[M]); ch = ann[np.clip(r, 0, ann.shape[0] - 1), np.clip(c, 0, ann.shape[1] - 1)]
area = np.cos(np.radians(LA[M])); ok = np.isfinite(ch)
out = {"chirps_mean": round(float((ch[ok] * area[ok]).sum() / area[ok].sum()), 1), "aquastat": 657}
for k in ("idw", "ok", "uk", "tps"):
    v = G[k][M]
    out[k] = dict(r=round(float(np.corrcoef(v[ok], ch[ok])[0, 1]), 3), mean_diff=round(float(((v - ch)[ok] * area[ok]).sum() / area[ok].sum()), 1),
                  mad=round(float((np.abs(v - ch)[ok] * area[ok]).sum() / area[ok].sum()), 1))
P = pd.read_csv("data/points.csv")
r, c = rowcol(tr, P.lon.values, P.lat.values); cs = ann[r, c]
out["stations_vs_chirps"] = dict(r=round(float(np.corrcoef(P.p, cs)[0, 1]), 3), mean_diff=round(float((cs - P.p).mean()), 1))
json.dump(out, open("data/check.json", "w"), indent=1); print(out)
