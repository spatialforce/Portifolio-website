"""Landslide susceptibility by factor reclassification and AHP weighted overlay (Chimanimani District, 30 m).
Eight factors are reclassified to 1 to 5 (5 = most prone), weighted by AHP (Saaty 1980) and summed; the index is
split into five classes by natural breaks. The mapped landslide source points are used ONLY to check the result.
Inputs come from ../chimanimani_flood/rast (same 30 m UTM 36S grid). Writes rast/*.npy and out/overlay.json."""
import json, os, numpy as np
from scipy import ndimage as nd
F = "../chimanimani_flood/"; os.makedirs("rast", exist_ok=True); os.makedirs("out", exist_ok=True)
H, W, RES = 2834, 2600, 30
S = dict(np.load(F + "rast/stack.npz")); M = S["mask"] == 1
rain = np.load(F + "rast/annrain.npy")                     # CHIRPS mean annual rainfall 1991 to 2020 (mm)
e = S["elev"]; gy, gx = np.gradient(e, RES)
asp = ((np.degrees(np.arctan2(-gx, gy)) + 360) % 360).astype(np.float32)   # 0 = north, clockwise
FA = {"slope": S["slope"], "rain": rain, "lulc": S["lulc"], "clay": S["clay"], "curv": S["curv"],
      "dstream": S["dstream"], "elev": e, "aspect": asp}

def digit(a, b, up=True):
    s = np.digitize(a, b) + 1
    return (s if up else 6 - s).astype(np.uint8)
LU = {8: 5, 5: 4, 11: 3, 7: 3, 2: 2, 1: 1, 4: 1}         # Esri LULC: bare, crops, rangeland, built, trees, water, flooded veg
def score(k):
    a = FA[k]
    if k == "slope": return digit(a, [5, 15, 25, 35])                 # degrees
    if k == "rain": return digit(a, [800, 1000, 1200, 1400])          # mm per year
    if k == "clay": return digit(a, [26, 30, 33, 36])                 # % clay, topsoil
    if k == "elev": return digit(a, [700, 1000, 1300, 1600])          # m: wetter, steeper uplands
    if k == "dstream": return digit(a, [100, 200, 400, 800], up=False)  # m from a stream
    if k == "curv":                                                    # 1/100 m, - concave (hollows)
        s = np.full(a.shape, 2, np.uint8); s[a < -0.2] = 4; s[a < -0.5] = 5; s[a > 0.2] = 3; return s
    if k == "aspect":                                                  # windward E to S slopes wettest
        s = np.full(a.shape, 2, np.uint8)
        s[(a >= 45) & (a < 90)] = 4; s[(a >= 90) & (a < 180)] = 5; s[(a >= 180) & (a < 225)] = 3; s[(a >= 315) | (a < 45)] = 1
        s[S["slope"] < 2] = 1; return s
    s = np.zeros(a.shape, np.uint8)
    for c, v in LU.items(): s[a == c] = v
    s[(s == 0) & M] = 2; return s
NAMES = ["slope", "rain", "lulc", "clay", "curv", "dstream", "elev", "aspect"]
R = {k: score(k) for k in NAMES}

A = np.array([[1,   2,   3,   4,   4,   5,   6,   7],
              [1/2, 1,   2,   3,   3,   4,   5,   6],
              [1/3, 1/2, 1,   2,   2,   3,   4,   5],
              [1/4, 1/3, 1/2, 1,   1,   2,   3,   4],
              [1/4, 1/3, 1/2, 1,   1,   2,   3,   4],
              [1/5, 1/4, 1/3, 1/2, 1/2, 1,   2,   3],
              [1/6, 1/5, 1/4, 1/3, 1/3, 1/2, 1,   2],
              [1/7, 1/6, 1/5, 1/4, 1/4, 1/3, 1/2, 1]])
ev, vec = np.linalg.eig(A); i = np.argmax(ev.real); w = np.abs(vec[:, i].real); w /= w.sum()
lmax = ev[i].real; n = len(A); CI = (lmax - n) / (n - 1); CR = CI / 1.41
WT = dict(zip(NAMES, w))
lsi = sum(WT[k] * R[k].astype(np.float32) for k in NAMES); lsi[~M] = np.nan

def jenks(v, k=5, bins=400):
    h, ed = np.histogram(v, bins); c = (ed[:-1] + ed[1:]) / 2
    W1 = np.concatenate([[0], np.cumsum(h)]); S1 = np.concatenate([[0], np.cumsum(h * c)]); S2 = np.concatenate([[0], np.cumsum(h * c * c)])
    def ssd(a, b):
        nn = W1[b] - W1[a]; return 0 if nn == 0 else S2[b] - S2[a] - (S1[b] - S1[a]) ** 2 / nn
    B = len(c); D = np.full((k + 1, B + 1), np.inf); P = np.zeros((k + 1, B + 1), int); D[0, 0] = 0
    for j in range(1, k + 1):
        for b in range(j, B + 1):
            D[j, b], P[j, b] = min((D[j - 1, a] + ssd(a, b), a) for a in range(j - 1, b))
    cut, b = [], B
    for j in range(k, 0, -1): a = P[j, b]; cut.append(a); b = a
    return [float(ed[a]) for a in sorted(cut)[1:]]
brk = jenks(lsi[M])
cls = np.zeros((H, W), np.uint8); cls[M] = np.digitize(lsi[M], brk) + 1

def auc(score_, pts):                      # Mann-Whitney AUC: landslide cells vs all district cells
    from scipy.stats import rankdata
    a, b = score_[pts], score_[M & ~pts]
    r = rankdata(np.concatenate([a, b])); return float((r[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b)))
pts = np.load("pts.npy")
bld, pop = np.load(F + "rast/bld.npy"), np.load(F + "rast/pop.npy")
km2 = RES * RES / 1e6; tot = M.sum()
out = {"weights": {k: round(float(v), 4) for k, v in WT.items()}, "lambda_max": float(lmax), "CI": float(CI), "CR": float(CR),
       "breaks": brk, "lsi_range": [float(np.nanmin(lsi)), float(np.nanmax(lsi))], "area_km2": float(tot * km2),
       "classes": [{"km2": float((cls == c).sum() * km2), "pct": float((cls == c).sum() / tot * 100),
                    "pts_pct": float((cls[pts] == c).mean() * 100),
                    "bld": int(bld[cls == c].sum()), "pop": float(pop[cls == c].sum())} for c in range(1, 6)],
       "bld_total": int(bld[M].sum()), "pop_total": float(pop[M].sum()), "pts_cells": int(pts.sum()),
       "auc": auc(lsi, pts), "auc_factor": {k: auc(R[k].astype(np.float32), pts) for k in NAMES},
       "factor_pct": {k: [float((R[k][M] == s).mean() * 100) for s in range(1, 6)] for k in NAMES},
       "rain_range": [float(np.percentile(rain[M], 1)), float(np.percentile(rain[M], 99))]}
for c in out["classes"]: c["fr"] = c["pts_pct"] / c["pct"]
np.save("rast/lsi.npy", lsi.astype(np.float32)); np.save("rast/lcls.npy", cls); np.savez_compressed("rast/scores.npz", **R)
json.dump(out, open("out/overlay.json", "w"), indent=1)
print({k: round(v, 3) for k, v in WT.items()}, "CR", round(CR, 3), "AUC", round(out["auc"], 3))
print("breaks", [round(b, 2) for b in brk]); print({k: round(v, 2) for k, v in out["auc_factor"].items()})
for c in out["classes"]: print({k: round(v, 1) for k, v in c.items()})
