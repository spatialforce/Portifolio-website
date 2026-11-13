"""MaxEnt (elapid) fit for the African baobab in Zimbabwe on three uncorrelated CHELSA predictors.
Spatial (geographic k-fold) cross-validation, permutation importance, response curve, MaxSSS threshold.
Writes data/suit.npy and data/model.json."""
import json
import numpy as np, pandas as pd, geopandas as gpd, elapid
from sklearn.metrics import roc_auc_score
P = ["bio11", "bio12", "bio15"]
Z = np.load("data/stack.npz"); M = Z["mask"]; T = Z["transform"]
X_all = np.column_stack([Z[v][M] for v in P])
rows, cols = np.nonzero(M)
xy = lambda r, c: (T[2] + (c + .5) * T[0], T[5] + (r + .5) * T[4])

pr = pd.read_csv("data/records.csv")
rng = np.random.default_rng(7); bi = rng.choice(len(X_all), 10000, replace=False)
X = np.vstack([pr[P].values, X_all[bi]]); y = np.r_[np.ones(len(pr)), np.zeros(len(bi))]
lon, lat = np.r_[pr.decimalLongitude.values, xy(rows[bi], cols[bi])[0]], np.r_[pr.decimalLatitude.values, xy(rows[bi], cols[bi])[1]]
pts = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326).to_crs(32735)
kw = dict(feature_types=["linear", "quadratic"], beta_multiplier=1.5, transform="cloglog", random_state=1)

# spatial cross-validation. Main: 50 km checkerboard blocks (each half trains the other), so test points are spread across the country.
# Also: 5 geographic folds (whole regions held out) and a random 5-fold split, for comparison.
from sklearn.model_selection import StratifiedKFold
def run(tr, te):
    m = elapid.MaxentModel(**kw).fit(X[tr], y[tr]); return round(roc_auc_score(y[te], m.predict(X[te])), 3)
G = gpd.GeoDataFrame({"i": np.arange(len(y))}, geometry=pts); A, B = elapid.checkerboard_split(G, grid_size=50000)
auc_cb = [run(A.i.values, B.i.values), run(B.i.values, A.i.values)]
auc_geo = [run(tr, te) for tr, te in elapid.GeographicKFold(n_splits=5, random_state=1).split(pts)]
auc_rnd = [run(tr, te) for tr, te in StratifiedKFold(5, shuffle=True, random_state=1).split(X, y)]
print("checkerboard", auc_cb, "geographic", auc_geo, "random", auc_rnd)
m = elapid.MaxentModel(**kw).fit(X, y); p = m.predict(X); auc = roc_auc_score(y, p)
# permutation importance: drop in training AUC when one predictor is shuffled (10 repeats)
imp = {}
for j, v in enumerate(P):
    d = []
    for k in range(10):
        Xs = X.copy(); Xs[:, j] = rng.permutation(Xs[:, j]); d.append(auc - roc_auc_score(y, m.predict(Xs)))
    imp[v] = max(float(np.mean(d)), 0)
tot = sum(imp.values()); imp = {v: round(100 * imp[v] / tot, 1) for v in P}; print("importance %", imp)
# MaxSSS threshold (max sensitivity + specificity, presences vs background)
ths = np.linspace(0.01, 0.99, 99); ss = [(p[y == 1] >= t).mean() + (p[y == 0] < t).mean() for t in ths]
thr = float(ths[int(np.argmax(ss))]); print("MaxSSS thr", round(thr, 2), "sens", round((p[y == 1] >= thr).mean(), 3))
# response curves: one predictor varies, the others held at their background median
med = np.median(X[y == 0], 0); resp = {}
for j, v in enumerate(P):
    g = np.linspace(*np.percentile(X_all[:, j], [0.5, 99.5]), 80); Xr = np.tile(med, (80, 1)); Xr[:, j] = g
    resp[v] = [g.round(2).tolist(), m.predict(Xr).round(4).tolist()]
S = np.full(M.shape, np.nan, "float32"); S[M] = m.predict(X_all)
np.save("data/suit.npy", S)
q = np.nanpercentile(S, [10, 25, 50, 75, 90, 99]); print("suit pct", q.round(2), "share>=thr", round(float((S[M] >= thr).mean()), 3))
json.dump(dict(P=P, n_pres=int(y.sum()), n_bg=int((y == 0).sum()), auc_train=round(auc, 3), auc_cb=auc_cb, auc_geo=auc_geo, auc_rnd=auc_rnd,
               cb_mean=round(float(np.mean(auc_cb)), 3), geo_mean=round(float(np.mean(auc_geo)), 3), rnd_mean=round(float(np.mean(auc_rnd)), 3), p10=round(float(np.percentile(p[y == 1], 10)), 3), importance=imp, thr=round(thr, 2), resp=resp),
          open("data/model.json", "w"), indent=1)
