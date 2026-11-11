"""Statistics for the rainfall case study. Seasons are October to April totals (mm)."""
import numpy as np, rasterio, geopandas as gpd, pandas as pd
from rasterio.features import rasterize
from scipy import stats
B = "../population/raw/bnd/"
r = rasterio.open("rast/seasons.tif"); S = r.read().astype(float); T = r.transform; H, W = S.shape[1:]
Y = np.arange(1991, 2025)                       # season start year
zwe = gpd.read_file(B + "zwe_admin0.shp"); prov = gpd.read_file(B + "zwe_admin1.shp")
m0 = rasterize([(g, 1) for g in zwe.geometry], (H, W), transform=T, all_touched=False).astype(bool)
pid = rasterize([(g, i + 1) for i, g in enumerate(prov.geometry)], (H, W), transform=T)
lat = T.f + T.e * (np.arange(H) + 0.5); wgt = np.cos(np.radians(lat))[:, None] * np.ones((1, W))   # area weights
S[:, ~m0] = np.nan
base = (Y >= 1991) & (Y <= 2020)
mean = S[base].mean(0); sd = S[base].std(0, ddof=1); cv = 100 * sd / mean
pct = 100 * S / mean                            # percent of normal per season
drought = (pct < 75).sum(0).astype(float); drought[~m0] = np.nan   # seasons below 75 % of normal, all 34 seasons
# Sen's slope and Mann-Kendall (scipy kendalltau) per cell, 34 seasons
slope = np.full((H, W), np.nan); pval = np.full((H, W), np.nan)
ii, jj = np.where(m0)
for i, j in zip(ii, jj):
    v = S[:, i, j]; slope[i, j] = stats.theilslopes(v, Y)[0] * 10; pval[i, j] = stats.kendalltau(Y, v).pvalue
np.savez("data/grids.npz", mean=mean, cv=cv, pct2023=pct[Y == 2023][0], drought=drought, slope=slope, pval=pval, m0=m0)
def wmean(a, msk): return np.nansum(a[msk] * wgt[msk]) / np.sum(wgt[msk] * ~np.isnan(a[msk]))
nat = np.array([wmean(S[k], m0) for k in range(len(Y))])
nm = nat[base].mean()
ser = pd.DataFrame({"season": [f"{y}/{str(y+1)[2:]}" for y in Y], "mm": nat.round(1), "pct": (100 * nat / nm).round(1)})
ser.to_csv("data/national_series.csv", index=False)
print("national normal 1991-2020 mm", round(nm, 1), "sd", round(nat[base].std(ddof=1), 1), "cv", round(100 * nat[base].std(ddof=1) / nm, 1))
print("grid mean range", np.nanmin(mean).round(0), np.nanmax(mean).round(0), "cv range", np.nanmin(cv).round(1), np.nanmax(cv).round(1))
print(ser.sort_values("mm").head(7).to_string(index=False)); print(ser.sort_values("mm").tail(4).to_string(index=False))
tn = stats.theilslopes(nat, Y); print("national Sen slope mm/decade", round(tn[0] * 10, 1), "MK p", round(stats.kendalltau(Y, nat).pvalue, 3))
sig = (pval < 0.05) & m0; print("share of land with significant trend %", round(100 * wgt[sig].sum() / wgt[m0].sum(), 1),
      "of which positive", round(100 * wgt[sig & (slope > 0)].sum() / max(wgt[sig].sum(), 1e-9), 1))
rows = []
for i, n in enumerate(prov.ADM1_EN if "ADM1_EN" in prov else prov.iloc[:, 0]):
    k = (pid == i + 1) & m0
    if k.sum() == 0: continue
    pn = np.array([wmean(S[s], k) for s in range(len(Y))]); pm = pn[base].mean()
    rows.append(dict(province=n, cells=int(k.sum()), normal=round(pm), cv=round(100 * pn[base].std(ddof=1) / pm, 1),
                     pct2023=round(100 * pn[Y == 2023][0] / pm), pct1991=round(100 * pn[Y == 1991][0] / pm), pct2015=round(100 * pn[Y == 2015][0] / pm),
                     droughts=int((100 * pn / pm < 75).sum()), slope=round(stats.theilslopes(pn, Y)[0] * 10, 1), p=round(stats.kendalltau(Y, pn).pvalue, 3)))
pt = pd.DataFrame(rows).sort_values("normal", ascending=False); pt.to_csv("data/provinces.csv", index=False); print(pt.to_string(index=False))
pc = pct[Y == 2023][0]; print("2023/24 land below 75% of normal %", round(100 * wgt[m0 & (pc < 75)].sum() / wgt[m0].sum(), 1), "below 50%", round(100 * wgt[m0 & (pc < 50)].sum() / wgt[m0].sum(), 1))
print("drought count range", np.nanmin(drought), np.nanmax(drought))
c = rasterio.open("rast/monthly_clim.tif").read().astype(float); c[:, ~m0] = np.nan
print("monthly national mean mm", [round(wmean(c[k], m0), 1) for k in range(12)])
