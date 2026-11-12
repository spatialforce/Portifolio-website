# Field-level sugarcane monitoring from the monthly Sentinel-2 NDVI and NDMI stacks (20 m, 2019 to 2025).
# 1 cane mask and field segmentation, 2 within-field vigour zones, 3 dry-season water stress,
# 4 harvest month per field and year, 5 consistently weak fields. Writes out/fields.gpkg, out/*.npy, out/stats.json.
import json, numpy as np, rasterio.features, geopandas as gpd
from affine import Affine
from scipy import ndimage as ndi
from skimage.segmentation import felzenszwalb
from shapely.geometry import shape
YEARS = list(range(2019, 2026)); NY = len(YEARS)
def stack(ix):
    z = np.load(f"rast/{ix}_stack.npz"); return z["a"].astype("float32"), Affine(*z["transform"]), str(z["crs"])
V, TR, CRS = stack("ndvi"); M, _, _ = stack("ndmi")
T, H, W = V.shape; PX = 0.04  # ha per 20 m pixel

def fill(a, chunk=200000):
    """Linear gap fill along time for every pixel (edges held), in pixel chunks to keep memory low."""
    T0 = a.shape[0]; a = a.reshape(T0, -1); out = np.empty_like(a); t = np.arange(T0, dtype="int16")[:, None]
    for s0 in range(0, a.shape[1], chunk):
        b = a[:, s0:s0 + chunk]; ok = np.isfinite(b); col = np.arange(b.shape[1])
        i1 = np.where(ok, t, 0).astype("int16"); np.maximum.accumulate(i1, axis=0, out=i1)
        i2 = np.where(ok, t, T0 - 1).astype("int16"); i2 = np.minimum.accumulate(i2[::-1], axis=0)[::-1]
        p, q = b[i1, col], b[i2, col]; w = np.where(i2 > i1, (t - i1) / np.maximum(i2 - i1, 1), 0).astype("float32")
        out[:, s0:s0 + chunk] = np.where(ok, b, np.where(np.isfinite(p) & np.isfinite(q), p + (q - p) * w, np.where(np.isfinite(p), p, q)))
    return out.reshape((T0, H, W))
clear = np.isfinite(V).mean(0)
Vf = fill(V); del V
Mf = fill(M); del M
print('filled', flush=True)

# 1 Cane mask: high dry-season vigour (max NDVI Jun to Oct > 0.6) in at least 5 of 7 years AND at least 3 harvest-like
# drops (NDVI below 0.35 after being above 0.6 within the previous 3 months). Natural bush is brown in the dry season;
# riparian evergreen never drops.
Y = Vf.reshape(NY, 12, H, W)
dry_hi = (np.nanmax(Y[:, 5:10], axis=1) > 0.6).sum(0)
drop = np.zeros((H, W), "int16")
for k in range(3, T):
    hit = (Vf[k] < 0.35) & (np.nanmax(Vf[k - 3:k], axis=0) > 0.6); drop += hit & ~(Vf[k - 1] < 0.35)
cane = (dry_hi >= 5) & (drop >= 3) & (clear > 0.4)
cane = ndi.binary_opening(cane, iterations=1)

# Field segmentation: Felzenszwalb on three NDVI summaries of the full time series (fields share planting and harvest dates).
f1 = np.nanmean(Vf, 0); f2 = np.nanstd(Vf, 0); f3 = np.nanmean(Vf[-24:], 0) - np.nanmean(Vf[:24], 0)
img = np.dstack([(f - np.nanpercentile(f[cane], 2)) / (np.nanpercentile(f[cane], 98) - np.nanpercentile(f[cane], 2)) for f in (f1, f2, f3)])
img = np.clip(np.nan_to_num(img), 0, 1); img[~cane] = 0
seg = felzenszwalb(img, scale=60, sigma=0.6, min_size=60) + 1
seg[~cane] = 0
ids, cnt = np.unique(seg, return_counts=True)
small = ids[(cnt * PX < 5) & (ids > 0)]; seg[np.isin(seg, small)] = 0  # fields under 5 ha dropped
lab, n = ndi.label(seg > 0)  # keep segments; relabel compactly
_, seg = np.unique(seg, return_inverse=True); seg = seg.reshape(H, W).astype("int32")
nf = seg.max(); print("fields", nf)

def fstat(a, fn=None):
    """Per-field mean (or sd) of a 2D array, NaN ignored (field ids 1..nf)."""
    ok = np.isfinite(a) & (seg > 0); l = seg[ok]; v = a[ok].astype("float64")
    n = np.bincount(l, minlength=nf + 1)[1:]; s1 = np.bincount(l, v, nf + 1)[1:]
    mu = np.where(n > 0, s1 / np.maximum(n, 1), np.nan)
    if fn is np.nanstd:
        s2 = np.bincount(l, v * v, nf + 1)[1:]; return np.sqrt(np.maximum(s2 / np.maximum(n, 1) - mu ** 2, 0))
    return mu

# 2 Vigour: per-pixel peak NDVI per season (Jul to Jun cane year is awkward; use calendar-year max), multi-year mean.
peak = np.nanmax(Y, axis=1)                      # (NY, H, W)
pk_mean = np.nanmean(peak, 0)
fmean = fstat(pk_mean); fsd = fstat(pk_mean, np.nanstd)
rel = np.zeros((H, W), "float32"); rel[seg > 0] = pk_mean[seg > 0] / fmean[seg[seg > 0] - 1] - 1
zone = np.zeros((H, W), "uint8"); m = seg > 0
zone[m & (rel < -0.05)] = 1; zone[m & (rel >= -0.05) & (rel <= 0.05)] = 2; zone[m & (rel > 0.05)] = 3

# 3 Water stress: NDMI in the dry months (Aug to Oct) on standing cane only (NDVI > 0.5 that month), per year.
dry = {}
for i, y in enumerate(YEARS):
    sl = slice(i * 12 + 7, i * 12 + 10); nd = np.where(Vf[sl] > 0.5, Mf[sl], np.nan)
    dry[y] = np.nanmean(nd, 0)
dry_mean = np.nanmean(np.stack(list(dry.values())), 0)

# 4 Harvest month per field and year: first month the field mean NDVI falls below 0.35 after a field mean above 0.6.
fv = np.stack([fstat(Vf[k]) for k in range(T)])  # (T, nf)
fm = np.stack([fstat(Mf[k]) for k in range(T)])
harv = np.zeros((NY, nf), "int8")  # 0 = no harvest detected that year, else month 1..12
for j in range(nf):
    for k in range(3, T):
        if fv[k, j] < 0.35 and np.nanmax(fv[k - 3:k, j]) > 0.6 and not fv[k - 1, j] < 0.35:
            yi, mo = divmod(k, 12)
            if harv[yi, j] == 0: harv[yi, j] = mo + 1

# 5 Weak fields: field mean peak NDVI in the bottom 10 % of all fields in at least 5 of 7 years.
fpk = np.stack([fstat(peak[i]) for i in range(NY)])  # (NY, nf)
q10 = np.nanpercentile(fpk, 10, axis=1)[:, None]
weak_n = (fpk < q10).sum(0)

# Polygons
area = np.bincount(seg.ravel(), minlength=nf + 1)[1:] * PX
geoms = [(shape(g), int(v)) for g, v in rasterio.features.shapes(seg, mask=seg > 0, transform=TR)]
gdf = gpd.GeoDataFrame({"fid": [v for _, v in geoms]}, geometry=[g for g, _ in geoms], crs=CRS).dissolve("fid").reset_index()
j = gdf.fid.values - 1
gdf["area_ha"] = area[j]; gdf["pk_mean"] = fmean[j]; gdf["pk_sd"] = fsd[j]; gdf["cv"] = fsd[j] / fmean[j]
gdf["weak_n"] = weak_n[j]
for i, y in enumerate(YEARS):
    gdf[f"h{y}"] = harv[i, j]; gdf[f"pk{y}"] = fpk[i, j]; gdf[f"dm{y}"] = fstat(dry[y])[j]
gdf.to_file("out/fields.gpkg", driver="GPKG")
np.save("out/seg.npy", seg); np.save("out/zone.npy", zone); np.save("out/rel.npy", rel)
np.save("out/dry.npy", np.stack([dry[y] for y in YEARS]).astype("float32")); np.save("out/fv.npy", fv); np.save("out/fm.npy", fm)

# Stats
S = {"fields": int(nf), "cane_ha": float(area.sum()), "area_med": float(np.median(area)), "area_p10_p90": [float(x) for x in np.percentile(area, [10, 90])],
     "clear_share_cane": float(clear[cane].mean()),
     "cv_median": float(np.nanmedian(fsd / fmean)), "cv_p90": float(np.nanpercentile(fsd / fmean, 90)),
     "zone_share": {k: float((zone == v).sum() / m.sum()) for k, v in (("low", 1), ("mid", 2), ("high", 3))},
     "fields_lowzone_over_20pct": int((np.bincount(seg[zone == 1], minlength=nf + 1)[1:] > 0.2 * np.bincount(seg.ravel(), minlength=nf + 1)[1:]).sum()),
     "annual": {}, "weak_fields": int((weak_n >= 5).sum()), "weak_ha": float(area[weak_n >= 5].sum())}
w = area / area.sum()
for i, y in enumerate(YEARS):
    h = harv[i]; ok = h > 0
    S["annual"][y] = {"peak_ndvi": float(np.nansum(fpk[i] * w) / np.sum(w[np.isfinite(fpk[i])])),
                      "dry_ndmi": float(np.nanmean(dry[y][cane])), "harvest_share": float(w[ok].sum()),
                      "harvest_month_hist_ha": [float(area[h == mo].sum()) for mo in range(1, 13)],
                      "estate_ndvi": [float(np.nansum(fv[i * 12 + k] * w)) for k in range(12)],
                      "estate_ndmi": [float(np.nansum(fm[i * 12 + k] * w)) for k in range(12)]}
json.dump(S, open("out/stats.json", "w"), indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "annual"}, indent=0))
for y in YEARS: a = S["annual"][y]; print(y, round(a["peak_ndvi"], 3), round(a["dry_ndmi"], 3), round(a["harvest_share"], 2))
