"""Flood susceptibility by factor reclassification and AHP weighted overlay (Chimanimani District, 30 m).
Eight factors are each reclassified to a 1 to 5 score (5 = most prone to flooding), weighted by the analytic
hierarchy process (Saaty 1980) and summed. The sum is split into five classes by natural breaks (Jenks).
Writes rast/scores.npz, rast/fsi.npy, rast/fcls.npy and out/overlay.json."""
import json, numpy as np, rasterio
from scipy import ndimage as nd
H, W, RES = 2834, 2600, 30; TW, TH = W // 2, H // 2
S = dict(np.load("rast/stack.npz")); M = S["mask"] == 1

def tiles(n):
    a = np.zeros((H, W), np.float32)
    for i in range(2):
        for j in range(2):
            with rasterio.open(f"rast/{n}_{i}{j}.tif") as d: a[j*TH:(j+1)*TH, i*TW:(i+1)*TW] = d.read(1)
    return a

rain = tiles("annrain")                                   # CHIRPS mean annual rainfall 1991 to 2020 (mm)
# drainage density: length of streams (>= 1 km2 upstream) per km2 inside a 1 km radius circle
r = int(1000 / RES); yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; disk = (xx**2 + yy**2 <= r * r).astype(np.float32)
dd = nd.convolve(S["streams"].astype(np.float32), disk, mode="nearest") * RES / 1000 / (disk.sum() * RES * RES / 1e6)
riv = S["upa"] >= 10                                       # rivers: >= 10 km2 upstream area
dr = (nd.distance_transform_edt(~riv) * RES).astype(np.float32)
F = {"driver": dr, "slope": S["slope"], "elev": S["elev"], "twi": S["twi"], "rain": rain, "dd": dd,
     "lulc": S["lulc"], "clay": S["clay"]}

# Class breaks (score 5 = highest susceptibility). Continuous factors: lower bounds of each score band.
BR = {"driver": ([2000, 1000, 500, 250], "lt"),          # m from a river (>= 10 km2 upstream)
      "slope": ([25, 15, 10, 5], "lt"),                  # degrees
      "elev": ([1600, 1300, 1000, 700], "lt"),           # m above sea level
      "twi": ([6, 7, 8, 10], "gt"),
      "rain": ([800, 950, 1100, 1250], "gt"),            # mm per year
      "dd": ([0.3, 0.6, 0.9, 1.2], "gt"),                # km per km2
      "clay": ([28, 30, 32, 34], "gt")}                  # % clay, topsoil
LU = {1: 5, 4: 5, 7: 4, 8: 4, 5: 3, 11: 2, 2: 1}          # Esri LULC: water, flooded veg, built, bare, crops, rangeland, trees

def score(k):
    a = F[k]
    if k == "lulc":
        s = np.zeros(a.shape, np.uint8)
        for c, v in LU.items(): s[a == c] = v
        s[(s == 0) & M] = 2; return s
    b, d = BR[k]
    return (np.digitize(a, b) + 1).astype(np.uint8) if d == "gt" else (5 - np.digitize(a, sorted(b))).astype(np.uint8)
R = {k: score(k) for k in F}

# AHP pairwise comparison (row factor vs column factor, Saaty 1 to 9 scale)
NAMES = ["driver", "slope", "elev", "twi", "rain", "dd", "lulc", "clay"]
A = np.array([[1,   2,   3,   3,   4,   5,   6,   7],
              [1/2, 1,   2,   2,   3,   4,   5,   6],
              [1/3, 1/2, 1,   1,   2,   3,   4,   5],
              [1/3, 1/2, 1,   1,   2,   3,   4,   5],
              [1/4, 1/3, 1/2, 1/2, 1,   2,   3,   4],
              [1/5, 1/4, 1/3, 1/3, 1/2, 1,   2,   3],
              [1/6, 1/5, 1/4, 1/4, 1/3, 1/2, 1,   2],
              [1/7, 1/6, 1/5, 1/5, 1/4, 1/3, 1/2, 1]])
ev, vec = np.linalg.eig(A); i = np.argmax(ev.real); w = np.abs(vec[:, i].real); w /= w.sum()
lmax = ev[i].real; n = len(A); CI = (lmax - n) / (n - 1); CR = CI / 1.41    # random index for n = 8
WT = dict(zip(NAMES, w))

fsi = sum(WT[k] * R[k].astype(np.float32) for k in NAMES); fsi[~M] = np.nan

def jenks(v, k=5, bins=400):
    """Fisher-Jenks natural breaks on a fine histogram of the values (exact DP over bins)."""
    h, e = np.histogram(v, bins); c = (e[:-1] + e[1:]) / 2
    W1 = np.concatenate([[0], np.cumsum(h)]); S1 = np.concatenate([[0], np.cumsum(h * c)]); S2 = np.concatenate([[0], np.cumsum(h * c * c)])
    def ssd(a, b):
        nn = W1[b] - W1[a]; return 0 if nn == 0 else S2[b] - S2[a] - (S1[b] - S1[a]) ** 2 / nn
    B = len(c); D = np.full((k + 1, B + 1), np.inf); P = np.zeros((k + 1, B + 1), int); D[0, 0] = 0
    for j in range(1, k + 1):
        for b in range(j, B + 1):
            best = [(D[j - 1, a] + ssd(a, b), a) for a in range(j - 1, b)]; D[j, b], P[j, b] = min(best)
    cut, b = [], B
    for j in range(k, 0, -1): a = P[j, b]; cut.append(a); b = a
    return [float(e[a]) for a in sorted(cut)[1:]]
brk = jenks(fsi[M])
cls = np.zeros((H, W), np.uint8); cls[M] = np.digitize(fsi[M], brk) + 1

bld, pop = np.load("rast/bld.npy"), np.load("rast/pop.npy")
ha = RES * RES / 1e4; tot = M.sum()
out = {"weights": {k: round(float(v), 4) for k, v in WT.items()}, "lambda_max": float(lmax), "CI": float(CI), "CR": float(CR),
       "breaks": brk, "fsi_range": [float(np.nanmin(fsi)), float(np.nanmax(fsi))], "area_km2": float(tot * ha / 100),
       "classes": [{"km2": float((cls == c).sum() * ha / 100), "pct": float((cls == c).sum() / tot * 100),
                    "bld": int(bld[cls == c].sum()), "pop": float(pop[cls == c].sum())} for c in range(1, 6)],
       "bld_total": int(bld[M].sum()), "pop_total": float(pop[M].sum()),
       "factor_pct": {k: [float((R[k][M] == s).mean() * 100) for s in range(1, 6)] for k in NAMES},
       "rain_range": [float(np.percentile(rain[M], 1)), float(np.percentile(rain[M], 99))],
       "dd_pct": [float(x) for x in np.percentile(dd[M], [1, 25, 50, 75, 99])]}
np.savez_compressed("rast/scores.npz", **R); np.save("rast/fsi.npy", fsi.astype(np.float32)); np.save("rast/fcls.npy", cls)
np.save("rast/annrain.npy", rain); np.save("rast/driver10.npy", dr); np.save("rast/dd.npy", dd.astype(np.float32))
json.dump(out, open("out/overlay.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("weights", "CR", "breaks", "dd_pct")}))
for c in out["classes"]: print({k: round(v, 1) for k, v in c.items()})
for k, v in out["factor_pct"].items(): print(k, [round(x) for x in v])
