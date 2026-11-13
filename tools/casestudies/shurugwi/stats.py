# Soil loss classes, means by land cover and by ward. Writes rast/cls.tif and out/stats.json, out/wards.gpkg.
import json, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
def rd(n): return rasterio.open(f"rast/{n}.tif").read(1).astype("float64")
src = rasterio.open("rast/A.tif"); PROF = dict(src.profile, dtype="uint8", nodata=None, compress="deflate")
A, lc, dist = rd("A"), rd("lc"), rd("dist") == 1
land = dist & (lc != 80)
BR = [2, 5, 10, 20]; cls = np.where(land, np.digitize(A, BR) + 1, 0)
with rasterio.open("rast/cls.tif", "w", **PROF) as d: d.write(cls.astype("uint8"), 1)
ha = 0.09; tot = land.sum()
classes = [dict(c=c, km2=round(float((cls == c).sum() * ha / 100), 1), pct=round(float(100 * (cls == c).sum() / tot), 1)) for c in range(1, 6)]
LC = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare or sparse"}
lcs = []
for k, nm in LC.items():
    m = land & (lc == k)
    if m.sum() < 100: continue
    lcs.append(dict(lc=nm, km2=round(float(m.sum() * ha / 100), 1), mean=round(float(A[m].mean()), 2), median=round(float(np.median(A[m])), 2),
                    hi_pct=round(float(100 * (A[m] >= 10).mean()), 1), C=round(float(rd("C")[m].mean()), 3),
                    loss_kt=round(float(A[m].sum() * ha / 1000), 1)))
w = gpd.read_file("data/wards.gpkg").to_crs(32736)
w["ward"] = np.where(w.shapeName.str.contains("Town"), "Town", w.shapeName.str.replace("Shurugwi ", ""))
w = w.dissolve("ward", as_index=False)[["ward", "geometry"]]
rows = []
for i, g in zip(w.ward, w.geometry):
    m = (rasterize([g], out_shape=A.shape, transform=src.transform) == 1) & land
    rows.append(dict(ward=str(i), km2=round(float(m.sum() * ha / 100), 1), mean=round(float(A[m].mean()), 2), median=round(float(np.median(A[m])), 2),
                     hi_pct=round(float(100 * (A[m] >= 10).mean()), 1), slope=round(float(np.median(rd("slope")[m])), 1),
                     crop_pct=round(float(100 * (lc[m] == 40).mean()), 1)))
for k in ("km2", "mean", "median", "hi_pct", "slope", "crop_pct"): w[k] = [r[k] for r in rows]
w.to_file("out/wards.gpkg")
rows.sort(key=lambda r: -r["mean"])
out = dict(land_km2=round(float(tot * ha / 100), 1), mean=round(float(A[land].mean()), 2), median=round(float(np.median(A[land])), 2),
           total_Mt=round(float(A[land].sum() * ha / 1e6), 2), above_T11=round(float(100 * (A[land] > 11.2).mean()), 1),
           top10_share=round(float(100 * np.sort(A[land])[::-1][: tot // 10].sum() / A[land].sum()), 1),
           classes=classes, landcover=lcs, wards=rows)
json.dump(out, open("out/stats.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "wards"})); print(rows[:5], rows[-3:])
