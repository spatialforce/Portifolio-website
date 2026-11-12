# GEDI L4A footprints -> 100 m cells -> Random Forest on S2/S1/terrain -> wall-to-wall AGBD and carbon for Hwange NP.
# Spatial block cross-validation (10 km blocks, 5 folds). Carbon fraction 0.47 (IPCC 2006), CO2e = C x 44/12.
import glob, json, numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.features import geometry_mask
from pyproj import Transformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold

g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]; R = g["res"]
W, H = (x1 - x0) // R, (y1 - y0) // R
PRED = [f"dry_{b}" for b in ["B2", "B3", "B4", "B5", "B8", "B11", "B12", "NDVI"]] + \
       [f"wet_{b}" for b in ["B4", "B8", "B11", "NDVI"]] + ["s1_VV", "s1_VH", "elev", "slope"]
rd = lambda n: rasterio.open(f"rast/{n}.tif").read(1).astype("float32")
X = np.stack([rd(n) for n in PRED], -1)
park = gpd.read_file("data/wdpa_hwange.geojson").to_crs(32735)
tr = rasterio.transform.from_origin(x0, y1, R, R)
inpark = ~geometry_mask(park.geometry, (H, W), tr)

# footprints
df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/gedi_*.csv"))], ignore_index=True)
n_all = len(df)
df = df[(df.agbd >= 0) & (df.agbd <= 200)]          # remove physically implausible values for this savanna
n_keep = len(df)
ex, ny = Transformer.from_crs(4326, 32735, always_xy=True).transform(df.longitude.values, df.latitude.values)
df["c"] = ((ex - x0) // R).astype(int)
df["r"] = ((y1 - ny) // R).astype(int)
df = df[(df.c >= 0) & (df.c < W) & (df.r >= 0) & (df.r < H)]
df["inpark"] = inpark[df.r, df.c]
cell = df.groupby(["r", "c"]).agg(agbd=("agbd", "mean"), n=("agbd", "size")).reset_index()
cell = cell[cell.n >= 2]                              # at least two shots per hectare
Xc = X[cell.r, cell.c]; ok = np.isfinite(Xc).all(1); cell, Xc = cell[ok], Xc[ok]
y = cell.agbd.values
blocks = (cell.r.values // 100) * 1000 + cell.c.values // 100   # 10 km blocks
print("footprints", n_all, "kept", n_keep, "cells", len(cell))

# spatial block CV
oof = np.zeros_like(y)
rf_kw = dict(n_estimators=200, min_samples_leaf=5, max_features=0.4, n_jobs=-1, random_state=1)
for k, (a, b) in enumerate(GroupKFold(5).split(Xc, y, blocks)):
    m = RandomForestRegressor(**rf_kw).fit(Xc[a], y[a]); oof[b] = m.predict(Xc[b])
res = oof - y
cv = dict(r2=float(1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()), rmse=float(np.sqrt((res ** 2).mean())),
          bias=float(res.mean()), mae=float(np.abs(res).mean()), mean_obs=float(y.mean()))
cv["rmse_pct"] = 100 * cv["rmse"] / cv["mean_obs"]
print("CV", cv)
pd.DataFrame({"obs": y, "pred": oof}).to_csv("out/cv.csv", index=False)

# final model and wall-to-wall prediction
m = RandomForestRegressor(**rf_kw).fit(Xc, y)
imp = dict(sorted(zip(PRED, m.feature_importances_.round(4).tolist()), key=lambda t: -t[1]))
flat = X.reshape(-1, len(PRED)); valid = np.isfinite(flat).all(1)
pred = np.full(H * W, np.nan, "float32"); sd = np.full(H * W, np.nan, "float32")
idx = np.where(valid)[0]
for s in range(0, len(idx), 200000):
    ii = idx[s:s + 200000]
    t = np.stack([e.predict(flat[ii]) for e in m.estimators_[::4]])   # 50 trees for spread
    pred[ii] = m.predict(flat[ii]); sd[ii] = t.std(0)
pred, sd = pred.reshape(H, W), sd.reshape(H, W)
prof = dict(driver="GTiff", width=W, height=H, count=1, dtype="float32", crs="EPSG:32735", transform=tr, compress="deflate")
for n, a in [("agbd_pred", pred), ("agbd_sd", sd)]:
    with rasterio.open(f"out/{n}.tif", "w", **prof) as r: r.write(a, 1)

# totals inside park (each cell = 1 ha)
P = inpark & np.isfinite(pred)
agb_t = float(pred[P].sum()); C = agb_t * 0.47
cci, l4b, wc = rd("cci_agb"), rd("l4b_mu"), rd("worldcover")
l4b[~np.isfinite(l4b) | (l4b < 0)] = np.nan; cci[~np.isfinite(cci) | (cci < 0)] = 0  # asset masks 0 Mg/ha
tot = dict(cells=int(P.sum()), area_km2=P.sum() / 100, agbd_mean=float(pred[P].mean()), agbd_median=float(np.median(pred[P])),
           agb_Mt=agb_t / 1e6, C_Mt=C / 1e6, CO2e_Mt=C * 44 / 12 / 1e6, C_mean=float(pred[P].mean() * 0.47),
           sd_mean=float(np.nanmean(sd[P])), cv_cell_pct=float(np.nanmean(sd[P] / np.maximum(pred[P], 1)) * 100),
           cci_mean=float(np.nanmean(cci[P])), l4b_mean=float(np.nanmean(l4b[P])),
           gedi_park_mean=float(df[df.inpark].agbd.mean()), gedi_park_n=int(df.inpark.sum()))
both = P & np.isfinite(cci)
tot["r_cci"] = float(np.corrcoef(pred[both], cci[both])[0, 1])
b2 = P & np.isfinite(l4b); tot["r_l4b"] = float(np.corrcoef(pred[b2], l4b[b2])[0, 1])
names = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare / sparse",
         80: "Open water", 90: "Herbaceous wetland"}
cls = []
for v, nm in names.items():
    s = P & (wc == v)
    if s.sum() < 100: continue
    cls.append(dict(code=v, name=nm, area_km2=s.sum() / 100, share=100 * s.sum() / P.sum(), agbd=float(pred[s].mean()),
                    C_Mt=float(pred[s].sum() * 0.47 / 1e6), cci=float(np.nanmean(cci[s]))))
json.dump(dict(n_all=n_all, n_keep=n_keep, n_cells=len(cell), cv=cv, importance=imp, totals=tot, classes=cls),
          open("out/stats.json", "w"), indent=1)
print(json.dumps(tot, indent=1)); print(pd.DataFrame(cls).round(2).to_string())
