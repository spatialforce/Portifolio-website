"""Design storms, SCS-CN runoff and peak discharge for the Mukuvisi catchment and its sub-catchments.
Rain: CHIRPS v2.0 daily, catchment-mean (cells weighted by the share of the catchment they cover), annual maximum per
rainy season 1981/82-2024/25, Gumbel (method of moments) depths for 2-100 year return periods.
Runoff: Q = (P - 0.2S)^2 / (P + 0.8S), S = 25400/CN - 254 (mm), applied cell by cell (grouped by CN value).
Timing: longest D8 flow path and Kirpich (1940) time of concentration, lag = 0.6 tc. Hydrograph: 24 h SCS Type II storm
in 15 min steps, excess by CN, convolved with the SCS dimensionless unit hydrograph (NRCS NEH 630 ch. 16).
Output: data/runoff.json, data/qmap.npz (10-year runoff depth per cell)."""
import json, numpy as np
from pyproj import Transformer

Z = np.load("data/grid.npz"); C = np.load("data/cn.npz"); G = json.load(open("raw/grid.json"))
CM, lab, A, F, dem = Z["catch"], Z["lab"], Z["acc"], Z["fdir"], Z["fill"]; cn = C["cn"]; R = G["res"]; CA = R * R / 1e6
HH, WW = CM.shape; NS = int(lab.max())
NAMES = {1: "Greendale", 2: "Upper Mukuvisi", 3: "Eastlea–Highlands", 4: "Hatfield", 5: "City Centre", 6: "Glen Norah",
         7: "Waterfalls–Mbare", 8: "Glen View"}
RP = [2, 5, 10, 25, 50, 100]

# ---- rainfall: catchment-mean annual maxima
W = np.load("raw/chirps.npz"); dates, px, py, P = W["dates"], W["x"], W["y"], W["p"]
P = np.where(P < 0, np.nan, P)
rr, cc = np.nonzero(CM); rr, cc = rr[::7], cc[::7]
lon, lat = Transformer.from_crs(32736, 4326, always_xy=True).transform(G["x0"] + (cc + 0.5) * R, G["y1"] - (rr + 0.5) * R)
ix = np.round((lon - px[0]) / (px[1] - px[0])).astype(int); iy = np.round((lat - py[0]) / (py[1] - py[0])).astype(int)
wt = np.zeros(P.shape[1:]); np.add.at(wt, (iy, ix), 1); wt /= wt.sum()
pm = np.nansum(P * wt, axis=(1, 2)); pmax = np.nanmax(np.where(wt > 0, P, np.nan), axis=(1, 2))
season = np.array([int(d[:4]) - (int(d[5:7]) < 7) for d in dates])
yrs = sorted(set(season)); am = np.array([pm[season == s].max() for s in yrs]); amp = np.array([pmax[season == s].max() for s in yrs])
tot = np.array([pm[season == s].sum() for s in yrs])
amd = [str(dates[season == s][np.argmax(pm[season == s])]) for s in yrs]


def gumbel(x, T):
    K = -np.sqrt(6) / np.pi * (0.5772 + np.log(np.log(T / (T - 1)))); return x.mean() + K * x.std(ddof=1)


PT = {T: float(gumbel(am, T)) for T in RP}; PTc = {T: float(gumbel(amp, T)) for T in RP}
# Gringorten plotting positions for the figure
srt = np.sort(am)[::-1]; Temp = (len(am) + 0.12) / (np.arange(1, len(am) + 1) - 0.44)
print("cells", int((wt > 0).sum()), "seasons", len(yrs), "mean season total", tot.mean().round(0), "AM mean/sd", am.mean().round(1), am.std(ddof=1).round(1))
print("design P", {T: round(v, 1) for T, v in PT.items()}, "single-cell", {T: round(v, 1) for T, v in PTc.items()})


def Q(p, c):
    s = 25400 / c - 254; ia = 0.2 * s
    return np.where(p > ia, (p - ia) ** 2 / (p - ia + s), 0.0)


def amc(c, k):  # Chow et al. (1988) conversion from AMC II
    return {1: 4.2 * c / (10 - 0.058 * c), 2: c, 3: 23 * c / (10 + 0.13 * c)}[k]


# ---- flow length to the outlet (downstream distance) for every catchment cell
OFF = {64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)}
D = np.full(CM.shape, np.nan); r0, c0 = np.unravel_index(np.argmax(np.where(CM, A, 0)), A.shape); D[r0, c0] = 0
sr, sc = np.nonzero(CM); idx = np.argsort(-A[sr, sc])
for r, c in zip(sr[idx], sc[idx]):
    if r == r0 and c == c0: continue
    a, b = OFF[int(F[r, c])]; D[r, c] = D[r + a, c + b] + R * (1.4142 if a and b else 1)

# ---- hydrograph tools
TT = np.array([0, 2, 4, 6, 7, 8, 8.5, 9, 9.5, 9.75, 10, 10.5, 11, 11.5, 11.75, 12, 12.5, 13, 13.5, 14, 16, 20, 24])
FF = np.array([0, .022, .048, .080, .098, .120, .133, .147, .163, .172, .181, .204, .235, .283, .357, .663, .735, .772, .799, .820, .880, .952, 1])
dt = 0.25; t = np.arange(0, 24 + dt, dt); frac = np.interp(t, TT, FF)
UT = np.array([0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.8, 4, 4.5, 5])
UQ = np.array([0, .03, .1, .19, .31, .47, .66, .82, .93, .99, 1, .99, .93, .86, .78, .68, .56, .46, .39, .33, .28, .207, .147, .107, .077, .055, .04, .029, .021, .015, .011, .005, 0])


def hydro(mask, p24, k=2):
    """Outflow hydrograph (m3/s, 15 min steps) of the cells in mask for a 24 h Type II storm of depth p24."""
    vals, cnt = np.unique(cn[mask], return_counts=True); area = mask.sum() * CA
    cum = sum(Q(p24 * frac, amc(v, k)) * n for v, n in zip(vals, cnt)) / cnt.sum()  # mm, area-weighted
    ex = np.diff(cum)
    out = np.unravel_index(np.nanargmin(np.where(mask, D, np.nan)), D.shape)
    far = np.unravel_index(np.nanargmax(np.where(mask, D, np.nan)), D.shape)
    L = D[far] - D[out]; S = max((dem[far] - dem[out]) / L, 1e-3)
    tc = 0.0195 * L ** 0.77 * S ** -0.385 / 60  # h
    tp = dt / 2 + 0.6 * tc
    u = np.interp(np.arange(0, 5 * tp + dt, dt) / tp, UT, UQ); u = u / (u.sum() * dt * 3600) * area * 1e6 / 1000  # m3/s per mm
    q = np.convolve(ex, u)
    return dict(area=area, L=L, S=S, tc=tc, tp=tp, q=q, Q=cum[-1])


res = {"rain": {"seasons": [int(s) for s in yrs], "am": am.round(2).tolist(), "am_cell": amp.round(2).tolist(), "am_date": amd,
                "season_total": tot.round(1).tolist(), "n_cells": int((wt > 0).sum()), "PT": PT, "PT_cell": PTc,
                "emp_T": Temp.round(3).tolist(), "emp_P": srt.round(2).tolist()}}
whole = {T: hydro(CM, PT[T]) for T in RP}
res["outlet"] = {T: {"P": PT[T], "Q": float(h["Q"]), "C": float(h["Q"] / PT[T]), "V_Mm3": float(h["Q"] * h["area"] / 1000),
                     "qp": float(h["q"].max()), "t_peak_h": float(np.argmax(h["q"]) * dt + dt)} for T, h in whole.items()}
h10 = whole[10]; res["timing"] = {"L_km": h10["L"] / 1000, "S": h10["S"], "tc_h": h10["tc"], "tp_h": h10["tp"]}
res["hydro10"] = h10["q"].round(2).tolist(); res["hydro100"] = whole[100]["q"].round(2).tolist(); res["hydro2"] = whole[2]["q"].round(2).tolist()
res["amc10"] = {k: {"Q": float(hydro(CM, PT[10], k)["Q"]), "qp": float(hydro(CM, PT[10], k)["q"].max())} for k in (1, 2, 3)}
res["sub"] = {}
for i in range(1, NS + 1):
    m = lab == i; h = hydro(m, PT[10]); h100 = hydro(m, PT[100])
    res["sub"][i] = {"name": NAMES[i], "area": float(h["area"]), "cn": float(cn[m].mean()), "built": float((C["lc"][m] == 50).mean() * 100),
                     "L_km": h["L"] / 1000, "tc_h": h["tc"], "Q10": float(h["Q"]), "C10": float(h["Q"] / PT[10]), "qp10": float(h["q"].max()),
                     "qs10": float(h["q"].max() / h["area"]), "Q100": float(h100["Q"]), "qp100": float(h100["q"].max())}
qmap = np.where(CM, Q(PT[10], cn), np.nan).astype("float32"); np.savez_compressed("data/qmap.npz", q10=qmap)
res["qmap10"] = {"p10": float(np.nanpercentile(qmap, 10)), "p50": float(np.nanpercentile(qmap, 50)), "p90": float(np.nanpercentile(qmap, 90))}
json.dump(res, open("data/runoff.json", "w"), indent=1)
print("timing", {k: round(v, 3) for k, v in res["timing"].items()})
for T, o in res["outlet"].items(): print(T, {k: round(v, 2) for k, v in o.items()})
print("AMC", res["amc10"]); print("qmap", res["qmap10"])
for i, s in res["sub"].items(): print(i, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()})
