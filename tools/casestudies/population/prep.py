"""Dasymetric 2022 population grid: WorldPop 2020 constrained (100 m) pattern scaled to 2022 census district totals.
Writes rast/pop2022_300m.tif and rast/pop2022_1km.tif (on the MAP walking-time grid) and walking-time exposure tables."""
import numpy as np, rasterio, geopandas as gpd, pandas as pd, json
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
g = gpd.read_file("data/districts.gpkg")
with rasterio.open("raw/worldpop/pop.tif") as s:
    a = s.read(1, masked=True).filled(0).astype("float64"); T = s.transform
k = 3; h, w = a.shape[0] // k * k, a.shape[1] // k * k
p = a[:h, :w].reshape(h // k, k, w // k, k).sum(axis=(1, 3))
T3 = T * rasterio.Affine.scale(k)
idx = rasterize(((geom, i + 1) for i, geom in enumerate(g.geometry)), out_shape=p.shape, transform=T3, fill=0, dtype="int32")
wp = np.bincount(idx.ravel(), weights=p.ravel(), minlength=len(g) + 1)
ratio = np.zeros(len(g) + 1); ratio[1:] = g.pop2022.values / wp[1:]
print("WorldPop 2020 total", round(p.sum()), "inside districts", round(wp[1:].sum()))
print("scale ratio min/median/max", ratio[1:].min().round(3), np.median(ratio[1:]).round(3), ratio[1:].max().round(3))
p2 = p * ratio[idx]; p2[idx == 0] = 0
print("dasymetric total", round(p2.sum()))
prof = dict(driver="GTiff", height=p2.shape[0], width=p2.shape[1], count=1, dtype="float32", crs="EPSG:4326", transform=T3, compress="deflate")
with rasterio.open("rast/pop2022_300m.tif", "w", **prof) as o: o.write(p2.astype("float32"), 1)
with rasterio.open("raw/map/walk.tif") as s:
    wk = s.read(1).astype("float64"); WT = s.transform; wk[wk < 0] = np.nan
p1 = np.zeros(wk.shape)
reproject(p2, p1, src_transform=T3, src_crs="EPSG:4326", dst_transform=WT, dst_crs="EPSG:4326", resampling=Resampling.sum)
print("1 km total", round(p1.sum()))
with rasterio.open("rast/pop2022_1km.tif", "w", **{**prof, "height": wk.shape[0], "width": wk.shape[1], "transform": WT}) as o:
    o.write(p1.astype("float32"), 1)
# exposure
didx = rasterize(((geom, i + 1) for i, geom in enumerate(g.geometry)), out_shape=wk.shape, transform=WT, fill=0, dtype="int32")
bins = [0, 30, 60, 120, 180, 300, 1e9]; lab = ["Under 30", "30 to 60", "60 to 120", "120 to 180", "180 to 300", "Over 300"]
cls = np.digitize(np.nan_to_num(wk, nan=-1), bins) - 1
ok = (didx > 0) & ~np.isnan(wk)
print("people on cells without walk value", round(p1[(didx > 0) & np.isnan(wk)].sum()))
nat = [p1[ok & (cls == c)].sum() for c in range(6)]
tab = pd.DataFrame({"class": lab, "people": np.round(nat).astype(int)}); tab["share"] = 100 * tab.people / tab.people.sum()
print(tab.round(1).to_string())
prov = g.province.values
rows = []
for pv in sorted(set(prov)):
    m = ok & np.isin(didx, np.where(prov == pv)[0] + 1)
    tot = p1[m].sum(); over2 = p1[m & (wk > 120)].sum()
    med = np.average(wk[m], weights=p1[m])
    rows.append({"province": pv, "people": round(tot), "over2h": round(over2), "share_over2h": 100 * over2 / tot, "mean_min": med})
pt = pd.DataFrame(rows); print(pt.round(1).to_string())
d_over = []
for i in range(len(g)):
    m = ok & (didx == i + 1); t = p1[m].sum()
    d_over.append(100 * p1[m & (wk > 120)].sum() / t if t else np.nan)
g["over2h"] = d_over; g.to_file("data/districts.gpkg", driver="GPKG")
json.dump({"national": tab.to_dict("records"), "province": pt.to_dict("records")}, open("data/access.json", "w"), indent=1)
