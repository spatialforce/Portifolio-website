"""Kariba level, area and storage analysis. Writes out/stats.json, rast/occ.npz, rast/bed.npz.
Level: DAHITI multi-mission altimetry (data/kariba_dahiti.csv). Area: data/area.csv (fetch_area.py).
"""
import numpy as np, pandas as pd, json, os, glob, rasterio
from rasterio.merge import merge
os.makedirs("out", exist_ok=True)
MOL, MRL = 475.5, 488.5           # ZRA operating range (lake-levels page); technical page gives 474.8 / 487.8

# ---- levels ----
L = pd.read_csv("data/kariba_dahiti.csv", sep=";", parse_dates=["datetime"]).rename(columns={"datetime": "t", "wse": "h", "wse_u": "u"})
L = L.set_index("t").sort_index()
# datum: DAHITI normal heights sit below the ZRA gauge; shift by the mean offset on matched dates
GAUGE = [("2024-11-27", 475.99), ("2024-11-01", 476.14), ("2025-11-10", 476.67), ("2026-11-01", 480.19)]
def near(d):
    t = pd.Timestamp(d); w = L.loc[t - pd.Timedelta(days=12): t + pd.Timedelta(days=12)].h
    if not len(w): return None
    i = abs((w.index - t).days).argmin(); return float(w.iloc[i]), str(w.index[i].date())
gchk = [dict(date=d, gauge=g, dahiti=round(n[0], 3), dahiti_date=n[1], diff=round(g - n[0], 3)) for d, g in GAUGE if (n := near(d))]
OFF = float(np.mean([x["diff"] for x in gchk])); L["h"] = L.h + OFF
Lp = L.loc["2000":"2025"]
yr = Lp.h.groupby(Lp.index.year).agg(["min", "max", "count"])
yr["amp"] = yr["max"] - yr["min"]
dmin = Lp.h.groupby(Lp.index.year).idxmin(); dmax = Lp.h.groupby(Lp.index.year).idxmax()
mon = Lp.h.resample("MS").mean().interpolate(limit=2)
# share of time within 1 m and 2 m of the minimum operating level, by year
near1 = (mon < MOL + 1).groupby(mon.index.year).mean(); near2 = (mon < MOL + 2).groupby(mon.index.year).mean()
# linear trend in annual mean level
am = Lp.h.groupby(Lp.index.year).mean(); tr = np.polyfit(am.index, am.values, 1)[0]

# ---- pair with area ----
# ---- occurrence mosaic and lake-bed elevation of the drawdown zone ----
srcs = [rasterio.open(f) for f in sorted(glob.glob("rast/occ_*.tif"))]
occ, tf = merge(srcs, nodata=None); occ = occ[0]
np.savez_compressed("rast/occ.npz", occ=occ, tf=np.array(tf)[:6], crs=str(srcs[0].crs))
from scipy import ndimage as nd
lab, _ = nd.label((occ >= 3) & (occ <= 100)); sz = np.bincount(lab.ravel()); sz[0] = 0; LAKE = lab == sz.argmax()
np.save("rast/lake.npy", LAKE)
# share of the thresholded water that belongs to the lake itself (the box also holds small dams and river reaches)
LSH = {t: float((LAKE & (occ >= t) & (occ <= 100)).sum() / max(((occ >= t) & (occ <= 100)).sum(), 1)) for t in range(1, 101)}
A = pd.read_csv("data/area.csv")
A["area_box"] = A.area_km2; A["area_km2"] = [round(v * LSH[int(t)], 1) for v, t in zip(A.area_box, A.t)]
def win(y, s):
    a, b = (f"{y}-04-01", f"{y}-06-30") if s == "high" else (f"{y}-10-01", f"{y}-12-31")
    v = L.loc[a:b].h; return v.median() if len(v) else np.nan
A["h"] = [win(y, s) for y, s in zip(A.year, A.season)]
P = A[(A.error_share < 0.05) & A.h.notna()].copy()
c1 = np.polyfit(P.h, P.area_km2, 1); c2 = np.polyfit(P.h, P.area_km2, 2)
for k, c in (("lin", c1), ("quad", c2)):
    r = P.area_km2 - np.polyval(c, P.h); P[f"res_{k}"] = r
rmse1 = float(np.sqrt((P.res_lin ** 2).mean())); rmse2 = float(np.sqrt((P.res_quad ** 2).mean()))
r2 = float(np.corrcoef(P.h, P.area_km2)[0, 1] ** 2)
C = c2 if rmse2 < rmse1 * 0.95 else c1
Af = lambda h: np.polyval(C, h)
# storage above MOL, km3 (area km2 x m / 1000)
hh = np.arange(470, 489.01, 0.01)
V = np.concatenate([[0], np.cumsum((Af(hh[1:]) + Af(hh[:-1])) / 2 * 0.01 / 1000)]); V -= np.interp(MOL, hh, V)
Vf = lambda h: np.interp(h, hh, V)
live = float(Vf(MRL))
# ZRA checks (kariba-reservoir-data page): level, live storage x10^9 m3 or percent full
ZRA = [("2026-11-01", 480.19, 21.53, 33.22), ("2026-11-10", 479.98, None, 31.67), ("2025-11-10", 476.67, None, 8.09)]
chk = []
for d, h, v, p in ZRA:
    chk.append(dict(date=d, level=h, zra_live=v, zra_pct=p, our_live=round(float(Vf(h)), 2), our_pct=round(float(Vf(h)) / live * 100, 2)))
ao = {int(k): v for k, v in json.load(open("data/area_by_occ.json")).items()}
At = {t: sum(v for k, v in ao.items() if t <= k <= 100) * LSH[max(t, 1)] for t in range(0, 101)}
hgrid = np.arange(465, 490, 0.01); agrid = Af(hgrid)
hoft = {t: float(np.interp(At[t], agrid, hgrid)) for t in range(1, 101)}   # level at which the lake reaches area A(t)
bed = np.full(occ.shape, np.nan, np.float32)
for t in range(1, 101): bed[occ == t] = hoft[t]
np.savez_compressed("rast/bed.npz", bed=bed)
# extents for the maps: wettest and driest seasons
hi = A.loc[A.area_km2.idxmax()]; lo = A.loc[A.area_km2.idxmin()]

st = dict(
    n_all=int(len(L)), n_period=int(len(Lp)), first=str(L.index[0].date()), last=str(L.index[-1].date()),
    u_median=float(Lp.u.median()),
    hmax=float(Lp.h.max()), hmax_date=str(Lp.h.idxmax().date()), hmin=float(Lp.h.min()), hmin_date=str(Lp.h.idxmin().date()),
    annual={int(y): dict(min=round(r["min"], 2), max=round(r["max"], 2), amp=round(r.amp, 2), n=int(r["count"]),
                         dmin=str(dmin[y].date()), dmax=str(dmax[y].date()), near1=round(float(near1.get(y, 0)), 2), near2=round(float(near2.get(y, 0)), 2))
            for y, r in yr.iterrows()},
    trend_m_per_yr=round(float(tr), 3), mean_2000_09=round(float(Lp.loc["2000":"2009"].h.mean()), 2), mean_2016_25=round(float(Lp.loc["2016":"2025"].h.mean()), 2),
    amp_median=round(float(yr.amp.median()), 2),
    pairs=int(len(P)), dropped=[(int(y), s) for y, s in A[(A.error_share >= 0.05) | A.h.isna()][["year", "season"]].values],
    fit="quad" if C is c2 else "lin", coef=[float(x) for x in C], lin=[float(x) for x in c1], r2_lin=round(r2, 3),
    rmse_lin=round(rmse1, 1), rmse_quad=round(rmse2, 1),
    slope_km2_per_m=round(float(np.polyval(np.polyder(C), 480)), 1),
    area_mol=round(float(Af(MOL)), 0), area_mrl=round(float(Af(MRL)), 0), area_max_extent=round(sum(ao.values()), 0), area_lake_t1=round(At[1], 0), lsh3=round(LSH[3], 4), lsh96=round(LSH[96], 4),
    live_km3=round(live, 2), checks=chk, gauge=gchk, offset=round(OFF, 3),
    hoft={t: round(hoft[t], 2) for t in (1, 5, 10, 25, 50, 75, 90, 95, 100)},
    hi=dict(year=int(hi.year), season=hi.season, t=int(hi.t), area=float(hi.area_km2)),
    lo=dict(year=int(lo.year), season=lo.season, t=int(lo.t), area=float(lo.area_km2)),
    table=[dict(h=h, area=round(float(Af(h)), 0), live=round(float(Vf(h)), 2), pct=round(float(Vf(h)) / live * 100, 1)) for h in (475.5, 477, 479, 481, 483, 485, 487, 488.5)],
)
P.to_csv("out/pairs.csv", index=False); mon.to_csv("out/monthly.csv")
json.dump(st, open("out/stats.json", "w"), indent=1)
print(json.dumps({k: st[k] for k in ("hmax", "hmax_date", "hmin", "hmin_date", "trend_m_per_yr", "mean_2000_09", "mean_2016_25", "amp_median", "pairs", "dropped", "fit", "r2_lin", "rmse_lin", "rmse_quad", "slope_km2_per_m", "area_mol", "area_mrl", "area_max_extent", "live_km3", "checks", "gauge", "hoft", "hi", "lo")}, indent=0))
