# Recompute CCI comparison numbers from saved outputs (CCI no-data is -inf), without retraining.
import json, numpy as np, geopandas as gpd, rasterio
from rasterio.features import geometry_mask
S = json.load(open("out/stats.json"))
pred = rasterio.open("out/agbd_pred.tif").read(1)
rd = lambda n: rasterio.open(f"rast/{n}.tif").read(1).astype("float32")
cci, wc, l4b = rd("cci_agb"), rd("worldcover"), rd("l4b_mu")
cci[~np.isfinite(cci) | (cci < 0)] = 0  # asset masks 0 Mg/ha; l4b[~np.isfinite(l4b) | (l4b < 0)] = np.nan
g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]
park = gpd.read_file("data/wdpa_hwange.geojson").to_crs(32735)
P = ~geometry_mask(park.geometry, pred.shape, rasterio.transform.from_origin(x0, y1, 100, 100)) & np.isfinite(pred)
b = P & np.isfinite(cci); b2 = P & np.isfinite(l4b)
t = S["totals"]
t.update(cci_mean=float(cci[b].mean()), cci_cover_pct=100 * b.sum() / P.sum(), r_cci=float(np.corrcoef(pred[b], cci[b])[0, 1]),
         pred_mean_on_cci=float(pred[b].mean()), cci_C_Mt=float(cci[b].sum() * 0.47 / 1e6),
         l4b_mean=float(l4b[b2].mean()), l4b_cover_pct=100 * b2.sum() / P.sum(), pred_mean_on_l4b=float(pred[b2].mean()))
for c in S["classes"]:
    s = P & (wc == c["code"]) & np.isfinite(cci); c["cci"] = float(cci[s].mean()) if s.any() else None
json.dump(S, open("out/stats.json", "w"), indent=1)
print({k: round(v, 3) for k, v in t.items()}); print([(c["name"], round(c["agbd"], 1), c["cci"] and round(c["cci"], 1)) for c in S["classes"]])
print(S["importance"])
