"""Interpolation of the 1961-1990 mean annual rainfall normal: inverse distance weighting (IDW), ordinary kriging (OK)
and thin-plate spline (TPS). Distances in km on a Lambert azimuthal equal-area projection centred on Zimbabwe.
Each method's parameter is chosen by leave-one-out cross-validation (LOOCV). Surfaces are evaluated at 0.025 degree
cell centres inside Zimbabwe. Output: data/interp.json, data/loocv.csv, data/points.csv, data/surfaces.npz, data/vario.csv"""
import json, numpy as np, pandas as pd, geopandas as gpd
from pyproj import Transformer
from scipy.optimize import curve_fit
from scipy.interpolate import RBFInterpolator
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr
from rasterio.features import geometry_mask
from rasterio.transform import from_origin

LAEA = "+proj=laea +lat_0=-19 +lon_0=29.8 +datum=WGS84 +units=km"
T = Transformer.from_crs(4326, LAEA, always_xy=True)
st = pd.read_csv("data/stations.csv")
st["elev"] = np.where(st.elev_inv > 0, st.elev_inv, st.elev)
st["key"] = st.lat.round(2).astype(str) + "_" + st.lon.round(2).astype(str)
merged = [g for _, g in st.groupby("key") if len(g) > 1]
print("merged", [(g.name.tolist(), g.p_ann.tolist()) for g in merged])
S = st.groupby("key").agg(name=("name", "first"), lat=("lat", "first"), lon=("lon", "first"), elev=("elev", "first"), p=("p_ann", "mean"),
                          n=("p_ann", "size"), years=("years_min", "min"), cv=("cv", "mean")).reset_index(drop=True)
S["x"], S["y"] = T.transform(S.lon.values, S.lat.values)
X = S[["x", "y"]].values; z = S.p.values; N = len(S)
D = cdist(X, X); nn = np.where(np.eye(N, dtype=bool), np.inf, D).min(1); S["nn_km"] = nn.round(1)
print("points", N)


def idw(Xs, zs, Xq, p):
    d = np.maximum(cdist(Xq, Xs), 1e-6); w = d ** -p
    return (w @ zs) / w.sum(1)


MODELS = {"Spherical": lambda h, c0, c, a: np.where(h < a, c0 + c * (1.5 * h / a - 0.5 * (h / a) ** 3), c0 + c),
          "Exponential": lambda h, c0, c, a: c0 + c * (1 - np.exp(-3 * h / a)),
          "Gaussian": lambda h, c0, c, a: c0 + c * (1 - np.exp(-3 * (h / a) ** 2))}
iu = np.triu_indices(N, 1); h = D[iu]
F_ = np.c_[np.ones(N), X]; beta = np.linalg.lstsq(F_, z, rcond=None)[0]; res = z - F_ @ beta
LAG = 25; edges = np.arange(0, 400 + LAG, LAG); V = {}
FIT = {}
for tag, v in (("ok", z), ("uk", res)):
    g = 0.5 * (v[:, None] - v[None, :])[iu] ** 2; rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (h >= a) & (h < b)
        if m.sum(): rows.append(dict(lag_km=round(h[m].mean(), 1), gamma=round(g[m].mean(), 1), pairs=int(m.sum())))
    V[tag] = pd.DataFrame(rows); FIT[tag] = {}
    for k, f in MODELS.items():  # weighted by number of pairs; range limited to about half the largest station distance
        p, _ = curve_fit(f, V[tag].lag_km, V[tag].gamma, p0=[2000, v.var(), 150], sigma=1 / np.sqrt(V[tag].pairs),
                         bounds=([0, 1, 20], [v.var(), v.var() * 3, 400]), maxfev=20000)
        FIT[tag][k] = dict(nugget=round(p[0], 1), psill=round(p[1], 1), range_km=round(p[2], 1))
pd.concat([V["ok"].add_prefix("ok_"), V["uk"].add_prefix("uk_")], axis=1).to_csv("data/vario.csv", index=False)
TREND = dict(b0=round(beta[0], 2), bx=round(beta[1], 4), by=round(beta[2], 4), r2=round(1 - (res ** 2).sum() / ((z - z.mean()) ** 2).sum(), 3),
             var_raw=round(z.var(), 1), var_res=round(res.var(), 1))


def krige(Xs, zs, Xq, k, drift, ret_var=False):
    f = MODELS[k]; q = FIT["uk" if drift else "ok"][k]; c0, c, a = q["nugget"], q["psill"], q["range_km"]
    gam = lambda hh: np.where(hh > 0, f(hh, c0, c, a), 0.0)
    n = len(Xs); Fs = np.c_[np.ones(n), Xs] if drift else np.ones((n, 1)); Fq = np.c_[np.ones(len(Xq)), Xq] if drift else np.ones((len(Xq), 1))
    m = Fs.shape[1]; A = np.zeros((n + m, n + m)); A[:n, :n] = gam(cdist(Xs, Xs)); A[:n, n:] = Fs; A[n:, :n] = Fs.T
    b = np.c_[gam(cdist(Xq, Xs)), Fq]
    W = np.linalg.solve(A, b.T).T
    est = W[:, :n] @ zs
    if ret_var: return est, (W * b).sum(1)
    return est


ok = lambda Xs, zs, Xq, k, rv=False: krige(Xs, zs, Xq, k, False, rv)
uk = lambda Xs, zs, Xq, k, rv=False: krige(Xs, zs, Xq, k, True, rv)


def tps(Xs, zs, Xq, s):
    return RBFInterpolator(Xs, zs, kernel="thin_plate_spline", smoothing=s)(Xq)


def loo(fn, par):
    out = np.empty(N)
    for i in range(N):
        m = np.arange(N) != i; out[i] = fn(X[m], z[m], X[i:i + 1], par)[0]
    return out


def stats(pr, mask=slice(None)):
    e = pr[mask] - z[mask]; o = z[mask]
    return dict(me=round(e.mean(), 1), mae=round(np.abs(e).mean(), 1), rmse=round(np.sqrt((e ** 2).mean()), 1),
                rmse_pct=round(100 * np.sqrt((e ** 2).mean()) / o.mean(), 1),
                r2=round(1 - (e ** 2).sum() / ((o - o.mean()) ** 2).sum(), 3), r=round(np.corrcoef(pr[mask], o)[0, 1], 3))


R = {"n": N, "vario": FIT, "trend": TREND}
idw_t = {p: stats(loo(idw, p))["rmse"] for p in (1, 1.5, 2, 2.5, 3, 4)}
ok_t = {k: stats(loo(ok, k))["rmse"] for k in MODELS}
uk_t = {k: stats(loo(uk, k))["rmse"] for k in MODELS}
tps_t = {s: stats(loo(tps, s))["rmse"] for s in (0, 1, 3, 10, 30, 100, 300, 1000)}
P_IDW = min(idw_t, key=idw_t.get); K_OK = min(ok_t, key=ok_t.get); K_UK = min(uk_t, key=uk_t.get); S_TPS = min(tps_t, key=tps_t.get)
R["tuning"] = dict(idw=idw_t, ok=ok_t, uk=uk_t, tps=tps_t, best=dict(idw=P_IDW, ok=K_OK, uk=K_UK, tps=S_TPS))
print("tuning", R["tuning"])
L = pd.DataFrame(dict(name=S.name, lat=S.lat, lon=S.lon, elev=S.elev, obs=z.round(1), nn_km=S.nn_km, years=S.years))
for c, fn, par in (("idw", idw, P_IDW), ("ok", ok, K_OK), ("uk", uk, K_UK), ("tps", tps, S_TPS)):
    L[c] = loo(fn, par).round(1)
L["idw2"] = loo(idw, 2).round(1)
L.to_csv("data/loocv.csv", index=False)
out = int(L.obs.idxmax()); keep = np.arange(N) != out
R["cv"] = {c: stats(L[c].values) for c in ("idw", "ok", "uk", "tps", "idw2")}
R["cv_no_outlier"] = {c: stats(L[c].values, keep) for c in ("idw", "ok", "uk", "tps")}
R["outlier"] = dict(name=L.name[out], obs=float(L.obs[out]), **{c: float(L[c][out]) for c in ("idw", "ok", "uk", "tps")})
sparse = (L.nn_km > np.median(L.nn_km)).values
R["cv_sparse"] = {c: dict(dense=stats(L[c].values, ~sparse)["mae"], sparse=stats(L[c].values, sparse)["mae"]) for c in ("idw", "ok", "uk", "tps")}
R["nn_km"] = dict(median=float(np.median(nn)), mean=round(nn.mean(), 1), max=float(nn.max()), max_name=S.name[nn.argmax()])
err = np.abs(L[["idw", "ok", "uk", "tps"]].values - L.obs.values[:, None])
R["closest_method_count"] = pd.Series(np.array(["idw", "ok", "uk", "tps"])[err.argmin(1)]).value_counts().to_dict()
R["stations"] = dict(min=float(z.min()), min_name=S.name[z.argmin()], max=float(z.max()), max_name=S.name[z.argmax()], mean=round(z.mean(), 1),
                     median=round(float(np.median(z)), 1), sd=round(z.std(ddof=1), 1), cv_pct=round(100 * z.std(ddof=1) / z.mean(), 1),
                     years_min=int(S.years.min()), r_elev=round(pearsonr(S.elev, z)[0], 3), p_elev=float(pearsonr(S.elev, z)[1]),
                     r_lon=round(pearsonr(S.lon, z)[0], 3), r_lat=round(pearsonr(S.lat, z)[0], 3),
                     elev_min=float(S.elev.min()), elev_max=float(S.elev.max()), interannual_cv_median=round(float(S.cv.median()), 1))
Wm = np.where(D > 0, 1 / np.maximum(D, 1e-6), 0); Wm = Wm / Wm.sum(1, keepdims=True)


def moran(v):
    d = v - v.mean(); return N / Wm.sum() * (d @ Wm @ d) / (d @ d)


I0 = moran(z); rng = np.random.default_rng(1); perm = np.array([moran(rng.permutation(z)) for _ in range(9999)])
R["moran"] = dict(I=round(I0, 3), E=round(-1 / (N - 1), 3), p=round((1 + (perm >= I0).sum()) / 10000, 4))
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326)
b = zwe.total_bounds; RES = 0.025
x0, y1 = np.floor(b[0] / RES) * RES, np.ceil(b[3] / RES) * RES
W_, H_ = int(np.ceil((b[2] - x0) / RES)), int(np.ceil((y1 - b[1]) / RES))
TR = from_origin(x0, y1, RES, RES); M = geometry_mask(zwe.geometry, (H_, W_), TR, invert=True)
lon = x0 + (np.arange(W_) + 0.5) * RES; lat = y1 - (np.arange(H_) + 0.5) * RES; LO, LA = np.meshgrid(lon, lat)
qx, qy = T.transform(LO[M], LA[M]); Q = np.c_[qx, qy]
area = (np.cos(np.radians(LA)) * (RES * 111.32) ** 2)[M]
G = {}
for c, fn, par in (("idw", idw, P_IDW), ("ok", ok, K_OK), ("uk", uk, K_UK), ("tps", tps, S_TPS)):
    a = np.full((H_, W_), np.nan, "float32"); a[M] = fn(X, z, Q, par); G[c] = a
for c, fn, k in (("ok", ok, K_OK), ("uk", uk, K_UK)):
    _, var = fn(X, z, Q, k, True); se = np.full((H_, W_), np.nan, "float32"); se[M] = np.sqrt(np.maximum(var, 0)); G[c + "_se"] = se
se = G["uk_se"]
stack = np.stack([G[c][M] for c in ("idw", "ok", "uk", "tps")]); spread = stack.max(0) - stack.min(0)
G["spread"] = np.full((H_, W_), np.nan, "float32"); G["spread"][M] = spread
np.savez_compressed("data/surfaces.npz", **G, mask=M, x0=x0, y1=y1, res=RES)
CL = [0, 450, 650, 800, 1000, 9999]
R["surface"] = {}
for c in ("idw", "ok", "uk", "tps"):
    v = G[c][M]
    R["surface"][c] = dict(mean=round(float((v * area).sum() / area.sum()), 1), min=round(float(v.min()), 1), max=round(float(v.max()), 1),
                           classes_pct=[round(float(100 * area[(v >= a) & (v < bb)].sum() / area.sum()), 1) for a, bb in zip(CL[:-1], CL[1:])])
R["spread"] = dict(mean=round(float((spread * area).sum() / area.sum()), 1), p50=round(float(np.median(spread)), 1), max=round(float(spread.max()), 1),
                   pct_lt50=round(float(100 * area[spread < 50].sum() / area.sum()), 1),
                   pct_50_100=round(float(100 * area[(spread >= 50) & (spread < 100)].sum() / area.sum()), 1),
                   pct_gt100=round(float(100 * area[spread >= 100].sum() / area.sum()), 1))
R["spread_pairs"] = {f"{a}-{bb}": round(float((np.abs(G[a][M] - G[bb][M]) * area).sum() / area.sum()), 1)
                     for a, bb in (("idw", "ok"), ("idw", "uk"), ("idw", "tps"), ("ok", "uk"), ("ok", "tps"), ("uk", "tps"))}
sev = se[M]
R["ok_se"] = dict(min=round(float(sev.min()), 1), max=round(float(sev.max()), 1), mean=round(float((sev * area).sum() / area.sum()), 1),
                  nugget_sd=round(float(np.sqrt(FIT["uk"][K_UK]["nugget"])), 1),
                  ok_mean=round(float((G["ok_se"][M] * area).sum() / area.sum()), 1))
R["area_km2"] = round(float(area.sum()))
json.dump(R, open("data/interp.json", "w"), indent=1, default=float)
S.to_csv("data/points.csv", index=False)
print(json.dumps({k: R[k] for k in ("vario", "trend", "cv", "cv_no_outlier", "outlier", "cv_sparse", "nn_km", "closest_method_count", "stations",
                                    "moran", "surface", "spread", "spread_pairs", "ok_se", "area_km2")}, default=float))
