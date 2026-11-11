"""Extra statistics for the redesigned case study 2: drought seasons by province and the trend by district.
Run with PROJ_LIB set (see .projlib). Output: data/drought_seasons.csv, data/prov_droughts.csv, data/district_trend.csv"""
import numpy as np, rasterio, geopandas as gpd, pandas as pd
from rasterio.features import rasterize
from scipy import stats

with rasterio.open("rast/seasons.tif") as r:
    S = r.read().astype(float); T = r.transform; shp = (r.height, r.width); b = r.bounds
G = np.load("data/grids.npz"); M0 = G["m0"]; N = G["mean"]; S[:, ~M0] = np.nan
Y = np.arange(1991, 2025); DRY = [1991, 1994, 2001, 2018, 2023]
lat = b.top - (np.arange(shp[0]) + 0.5) * (b.top - b.bottom) / shp[0]
W = np.cos(np.radians(lat))[:, None] * np.ones((1, shp[1])) * M0
P = 100 * S / N                                   # percent of the cell's own 1991-2020 normal


def share(m): return round(100 * W[m & M0].sum() / W[M0].sum(), 1)
def series(m): return np.array([np.nansum(S[k][m] * W[m]) / W[m].sum() for k in range(len(Y))])


rows = []
for y in DRY:
    k = y - 1991; p = P[k]
    rows.append(dict(season=f"{y}/{str(y + 1)[2:]}", below90=share(p < 90), below75=share(p < 75), below50=share(p < 50)))
pd.DataFrame(rows).to_csv("data/drought_seasons.csv", index=False); print(pd.DataFrame(rows))

prov = gpd.read_file("../population/raw/bnd/zwe_admin1.shp")
pr = rasterize(((g, i + 1) for i, g in enumerate(prov.geometry)), out_shape=shp, transform=T)
out = []
for i, n in enumerate(prov.adm1_name):
    m = (pr == i + 1) & M0; s = series(m); nm = s[:30].mean()
    out.append(dict(province=n, normal=round(nm), sd=round(s[:30].std(ddof=1)), driest=f"{Y[s.argmin()]}/{str(Y[s.argmin()] + 1)[2:]}",
                    **{f"p{y}": round(100 * s[y - 1991] / nm) for y in DRY}))
pd.DataFrame(out).to_csv("data/prov_droughts.csv", index=False); print(pd.DataFrame(out))

dist = gpd.read_file("../population/raw/bnd/zwe_admin2.shp")
dr = rasterize(((g, i + 1) for i, g in enumerate(dist.geometry)), out_shape=shp, transform=T)
out = []
for i, (n, pn) in enumerate(zip(dist.adm2_name, dist.adm2_pcode)):
    m = (dr == i + 1) & M0
    if m.sum() == 0:                                 # very small urban districts: take the cell under the centroid
        c = dist.geometry.iloc[i].centroid; r_, c_ = rasterio.transform.rowcol(T, c.x, c.y); m = np.zeros(shp, bool); m[r_, c_] = True
    s = series(m)
    out.append(dict(district=n, pcode=pn, cells=int(m.sum()), slope=round(stats.theilslopes(s, Y)[0] * 10, 1), p=round(stats.kendalltau(Y, s).pvalue, 3)))
d = pd.DataFrame(out); d.to_csv("data/district_trend.csv", index=False)
print(d.slope.describe()); print("min p", d.p.min(), "districts p<0.1", (d.p < 0.1).sum(), "p<0.05", (d.p < 0.05).sum())
print("negative", (d.slope < 0).sum(), "positive", (d.slope > 0).sum())
