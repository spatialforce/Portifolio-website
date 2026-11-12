# Enhancement statistics for the Hwange Units 7 and 8 air quality case study. Writes out/stats.json.
# Enhancement = zone mean minus background ring mean (same month). Pre = 2019-2022, post = 2024-2025 (2023 = commissioning year).
import json, numpy as np, rasterio
from scipy import stats
D = json.load(open("data/monthly.json")); S = {}
def ser(g, z): return np.array([np.nan if r[z] is None else r[z] * 1e6 for r in D[g]])
M = [r["m"] for r in D["no2"]]; yr = np.array([int(m[:4]) for m in M]); mo = np.array([int(m[5:]) for m in M])
pre, post = yr <= 2022, yr >= 2024
for g in ("no2", "so2"):
    o = {}
    for z in ("hwange", "maamba"):
        e = ser(g, z) - ser(g, "bg"); a, b = e[pre & ~np.isnan(e)], e[post & ~np.isnan(e)]
        t = stats.ttest_ind(b, a, equal_var=False)
        o[z] = {"pre": a.mean(), "post": b.mean(), "chg": b.mean() - a.mean(), "pct": 100 * (b.mean() / a.mean() - 1), "p": t.pvalue,
                "n_pre": len(a), "n_post": len(b), "annual": {int(y): np.nanmean(e[yr == y]) for y in range(2019, 2026)},
                "clim": [np.nanmean(e[mo == m]) for m in range(1, 13)]}
        o[z + "_raw"] = {"pre": np.nanmean(ser(g, z)[pre]), "post": np.nanmean(ser(g, z)[post])}
    o["bg"] = {"pre": np.nanmean(ser(g, "bg")[pre]), "post": np.nanmean(ser(g, "bg")[post]), "clim": [np.nanmean(ser(g, "bg")[mo == m]) for m in range(1, 13)]}
    o["did"] = o["hwange"]["chg"] - o["maamba"]["chg"]
    o["monthly"] = {"m": M, "hwange": list(ser(g, "hwange") - ser(g, "bg")), "maamba": list(ser(g, "maamba") - ser(g, "bg"))}
    S[g] = o
fire = np.array([r["px"] for r in D["fire80"]]); S["fire_clim"] = [float(fire[mo == m].mean()) for m in range(1, 13)]
r = stats.spearmanr(fire, ser("no2", "bg"), nan_policy="omit"); S["fire_bg_rho"] = [r.statistic, r.pvalue]
r = stats.spearmanr(fire, ser("no2", "hwange") - ser("no2", "bg"), nan_policy="omit"); S["fire_enh_rho"] = [r.statistic, r.pvalue]
# Exposure: people in cells where the period-mean NO2 exceeds the background-ring period mean by more than 50 % and 100 %
rd = lambda n: rasterio.open(f"rast/{n}.tif").read(1)
pop = rd("wpc2020"); ex = {}
for p in ("pre", "post"):
    a, bg = rd(f"no2_{p}"), S["no2"]["bg"][p]
    ex[p] = {k: float(pop[a > bg * f].sum()) for k, f in (("x1.5", 1.5), ("x2", 2.0))} | {"area_x1.5": int((a > bg * 1.5).sum())}
S["exposure"] = ex
# Towns (values from the 3x3 cell window)
with rasterio.open("rast/no2_post.tif") as R0: tr = R0
T = {"Hwange town": (26.4918, -18.3646), "Dete": (26.8630, -18.6207), "Victoria Falls": (25.8390, -17.9325), "Hwange Power Station": (26.4706, -18.3833)}
S["towns"] = {}
for n, (x, y) in T.items():
    i, j = tr.index(x, y); w = lambda z: float(np.nanmean(z[i - 1:i + 2, j - 1:j + 2]))
    S["towns"][n] = {k: w(rd(k)) for k in ("no2_pre", "no2_post", "so2_pre", "so2_post")}
a = rd("no2_post"); i, j = np.unravel_index(np.nanargmax(a), a.shape); S["no2_post_max"] = [float(a[i, j]), *map(float, tr.xy(i, j))]
json.dump(S, open("out/stats.json", "w"), indent=1, default=float)
for g in ("no2", "so2"):
    o = S[g]; print(g, {z: {k: round(o[z][k], 2) for k in ("pre", "post", "chg", "pct", "p")} for z in ("hwange", "maamba")}, "DiD", round(o["did"], 2),
                   "bg", round(o["bg"]["pre"], 1), round(o["bg"]["post"], 1))
    print("  annual", {y: round(v, 1) for y, v in o["hwange"]["annual"].items()})
print("fire rho bg", S["fire_bg_rho"], "enh", S["fire_enh_rho"]); print("exposure", ex); print("towns", {k: {a: round(b, 1) for a, b in v.items()} for k, v in S["towns"].items()}); print("max", S["no2_post_max"])
