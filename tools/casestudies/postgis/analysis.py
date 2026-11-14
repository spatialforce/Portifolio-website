"""Summaries from the PostGIS exports (exp/*.csv) and the greedy choice of new clinic sites. Writes out/stats.json.
Run from this folder with python -I after load.sh, sql/01 to 04 and export.sh."""
import json, os
import numpy as np, pandas as pd

os.makedirs("out", exist_ok=True)
C = pd.read_csv("exp/cell.csv"); F = pd.read_csv("exp/fac.csv"); W = pd.read_csv("exp/ward.csv")
K = pd.read_csv("exp/cand.csv"); V = pd.read_csv("exp/cover.csv"); P = pd.read_csv("exp/place.csv")
NS = pd.read_csv("exp/netstat.csv").iloc[0].to_dict(); NL = pd.read_csv("exp/netlen.csv")
TOT = C["pop"].sum()
BANDS = [(0, 1000, "< 1 km"), (1000, 2000, "1 – 2 km"), (2000, 3000, "2 – 3 km"), (3000, 5000, "3 – 5 km"), (5000, 1e9, "> 5 km")]


def wmed(d, w):
    o = np.argsort(d); cw = np.cumsum(w[o]); return float(d[o][np.searchsorted(cw, cw[-1] / 2)])


S = {"pop_total": TOT, "cells": len(C), "net": NS, "netlen": NL.to_dict("records"), "scen": {}}
for sc in "AB":
    d = C[f"dist{sc.lower()}"].to_numpy(); w = C["pop"].to_numpy()
    bands = [{"band": b, "pop": float(w[(d >= lo) & (d < hi)].sum()), "pct": float(w[(d >= lo) & (d < hi)].sum() / TOT * 100)}
             for lo, hi, b in BANDS]
    cum = [{"km": k, "pct": float(w[d <= k * 1000].sum() / TOT * 100)} for k in np.arange(0, 20.01, 0.1).round(1)]
    f = F[F.scen == sc]
    load = C.groupby(f"fid{sc.lower()}")["pop"].sum().reindex(f.fid, fill_value=0)
    S["scen"][sc] = {"n_fac": len(f), "n_clinic": int((f.kind == "Clinic").sum()), "n_hosp": int((f.kind == "Hospital").sum()),
                     "mean_m": float((d * w).sum() / TOT), "median_m": wmed(d, w), "max_m": float(d.max()), "bands": bands, "cum": cum,
                     "load_median": float(load.median()), "load_max": float(load.max()), "load_min": float(load.min()),
                     "load": [{"fid": int(i), "name": str(F.set_index("fid").loc[i, "name"]), "kind": F.set_index("fid").loc[i, "kind"],
                               "pop": float(p)} for i, p in load.sort_values(ascending=False).items()]}

# Wards: population, population-weighted mean walk and share beyond 2 km, both scenarios
g = C.assign(wa=C.dista * C["pop"], wb=C.distb * C["pop"], fa=C["pop"] * (C.dista > 2000), fb=C["pop"] * (C.distb > 2000)) \
     .groupby("wid")[["pop", "wa", "wb", "fa", "fb"]].sum()
W = W.set_index("wid").join(g)
W["mean_a"] = W.wa / W["pop"]; W["mean_b"] = W.wb / W["pop"]; W["far_a"] = W.fa / W["pop"] * 100; W["far_b"] = W.fb / W["pop"] * 100
W["auth"] = W.name.str.replace(r" \d+$", "", regex=True)
fb = F[F.scen == "B"]
S["wards"] = [{"wid": int(i), "name": r["name"], "auth": r.auth, "km2": r.km2, "pop": r["pop"], "mean_a": r.mean_a, "mean_b": r.mean_b,
               "far_a": r.far_a, "far_b": r.far_b} for i, r in W.iterrows()]
S["auth"] = [{"auth": a, "wards": int(len(x)), "pop": float(x["pop"].sum()),
              "far_b": float(x.fb.sum() / x["pop"].sum() * 100), "far_a": float(x.fa.sum() / x["pop"].sum() * 100),
              "mean_b": float(x.wb.sum() / x["pop"].sum())} for a, x in W.groupby("auth")]

# Greedy maximal coverage: five new clinics, each chosen to bring the most uncovered people (> 2 km in scenario B)
# within a 2 km walk, after removing the people already brought in by earlier picks.
popc = C.set_index("cid")["pop"]; cov = V.groupby("kid")["cid"].apply(set).to_dict(); done = set(); picks = []
for step in range(10):
    gain = {k: popc.loc[list(c - done)].sum() if c - done else 0 for k, c in cov.items()}
    k = max(gain, key=gain.get); done |= cov[k]
    row = K.set_index("kid").loc[k]
    near = P.assign(d=np.hypot(P.x - row.x, P.y - row.y)).nsmallest(1, "d").iloc[0]
    cx = C[C.cid.isin(cov[k])]
    picks.append({"step": step + 1, "kid": int(k), "x": float(row.x), "y": float(row.y), "gain": float(gain[k]),
                  "cum": float(popc.loc[list(done)].sum()), "near": near["name"], "near_m": float(near.d),
                  "ward": W.loc[int(cx.wid.mode().iloc[0]), "name"]})
far_b = float(C.loc[C.distb > 2000, "pop"].sum())
S["sites"] = {"far_b": far_b, "n_cand": len(K), "picks": picks}
json.dump(S, open("out/stats.json", "w"), indent=1, default=float)

# Short print for checking
for sc in "AB":
    s = S["scen"][sc]
    print(sc, s["n_fac"], s["n_clinic"], s["n_hosp"], round(s["mean_m"]), round(s["median_m"]), [round(b["pct"], 1) for b in s["bands"]],
          "load med/max", round(s["load_median"]), round(s["load_max"]))
for a in S["auth"]: print(a)
print("far_b", round(far_b))
for p in picks: print(p["step"], round(p["gain"]), round(p["cum"]), p["near"], round(p["near_m"]), p["ward"])
w = sorted(S["wards"], key=lambda r: -r["far_b"])[:10]
for r in w: print(r["name"], round(r["pop"]), round(r["far_b"], 1), round(r["mean_b"]), round(r["far_a"], 1))
