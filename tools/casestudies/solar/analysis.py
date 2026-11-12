# Weighted AHP overlay: score criteria 1-5, combine with eigenvector weights,
# classify suitability, run one-at-a-time sensitivity, report district stats
# (equal-area EPSG:6933) and suitability at known solar project sites.
import json
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from ahp import A, CRITERIA, weights_cr

g = json.load(open("data/grid.json"))
minx, miny, maxx, maxy = g["bounds"]
W, H = (maxx - minx) // 250, (maxy - miny) // 250
TR = from_origin(minx, maxy, 250, 250)

def rd(name):
    with rasterio.open(f"rast/{name}.tif") as s:
        return s.read(1)

ghi, slope, d_grid, d_road, d_sett, wc = (rd(n) for n in
    ["ghi", "slope", "d_grid", "d_road", "d_sett", "worldcover"])
mask, prov = rd("mask").astype(bool), rd("prov").astype(bool)

def classify(v, breaks, scores):
    """breaks ascending; len(scores) = len(breaks)+1"""
    out = np.full(v.shape, scores[-1], dtype="float32")
    for b, s in zip(breaks[::-1], scores[-2::-1]):
        out[v <= b] = s
    return out

# --- criterion scores (1-5) -------------------------------------------------
S = {}
S["GHI"] = classify(ghi, GHI_BREAKS := [5.40, 5.60, 5.80, 6.00], [1, 2, 3, 4, 5])
S["Slope"] = classify(slope, [1, 2, 3, 5], [5, 4, 3, 2, 1])
S["Distance to grid"] = classify(d_grid, [5, 10, 20, 40], [5, 4, 3, 2, 1])
S["Distance to roads"] = classify(d_road, [2, 5, 10, 20], [5, 4, 3, 2, 1])
S["Distance to settlements"] = classify(d_sett, [10, 25, 50, 100], [5, 4, 3, 2, 1])
lc_score = {60: 5, 30: 4, 20: 3, 40: 2, 10: 1}
lc = np.ones(wc.shape, dtype="float32")
for k, v in lc_score.items():
    lc[wc == k] = v
S["Land cover"] = lc

# score rasters for the criteria small-multiples map (0 = outside mask)
SCORE_NAMES = {"GHI": "ghi_s", "Distance to grid": "d_grid_s", "Slope": "slope_s",
               "Distance to roads": "d_road_s", "Land cover": "lc_s",
               "Distance to settlements": "d_sett_s"}

w, lam, CI, CR = weights_cr(A)
WEIGHTS = dict(zip(CRITERIA, w))

def overlay(weights):
    s = np.zeros((H, W), dtype="float32")
    for c in CRITERIA:
        s += weights[c] * S[c]
    return s

suit = overlay(WEIGHTS)
suit[~mask] = np.nan

# classes: equal intervals on the 1-5 score
CLASS_BREAKS = [2.5, 3.0, 3.5, 4.0]
CLASS_NAMES = ["Unsuitable", "Low", "Moderate", "High", "Very high"]
cls = np.zeros((H, W), dtype="uint8")
valid = mask & np.isfinite(suit)
cls[valid] = np.digitize(suit[valid], CLASS_BREAKS) + 1  # 1..5

prof = dict(driver="GTiff", height=H, width=W, count=1, crs="EPSG:32735",
            transform=TR, compress="deflate")
with rasterio.open("rast/suit.tif", "w", **prof, dtype="float32", nodata=-9999) as d:
    d.write(np.where(np.isfinite(suit), suit, -9999).astype("float32"), 1)
with rasterio.open("rast/suit_class.tif", "w", **prof, dtype="uint8", nodata=0) as d:
    d.write(cls, 1)
for c, nm in SCORE_NAMES.items():
    sc = np.where(mask, S[c], 0).astype("uint8")
    with rasterio.open(f"rast/{nm}.tif", "w", **prof, dtype="uint8", nodata=0) as d:
        d.write(sc, 1)

# --- cell areas in equal-area CRS (EPSG:6933) -------------------------------
# 250 m cells in UTM are ~62 500 m2 but vary; compute true area per row via 6933
from pyproj import Transformer
tr6933 = Transformer.from_crs(32735, 6933, always_xy=True)
ys = maxy - (np.arange(H) + 0.5) * 250
xmid = (minx + maxx) / 2
x1, y1 = tr6933.transform(np.full(H, xmid - 125), ys)
x2, y2 = tr6933.transform(np.full(H, xmid + 125), ys)
_, yt = tr6933.transform(np.full(H, xmid), ys + 125)
_, yb = tr6933.transform(np.full(H, xmid), ys - 125)
cell_km2 = (np.abs(x2 - x1) * np.abs(yt - yb)) / 1e6  # per row
AREA = np.repeat(cell_km2[:, None], W, axis=1)

def area_of(m):
    return float(AREA[m].sum())

print(f"weights: " + ", ".join(f"{c}={WEIGHTS[c]:.3f}" for c in CRITERIA))
print(f"CR {CR:.4f}")
print(f"province area {area_of(prov):.0f} km2, analysable {area_of(valid):.0f} km2")
res = {"weights": {c: round(float(WEIGHTS[c]), 4) for c in CRITERIA},
       "CR": round(float(CR), 4), "lambda": round(float(lam), 4),
       "ghi_breaks": GHI_BREAKS,
       "province_km2": round(area_of(prov)), "analysable_km2": round(area_of(valid)),
       "classes": {}, "districts": {}, "sensitivity": {}, "sites": []}
for i, nm in enumerate(CLASS_NAMES, 1):
    a = area_of(valid & (cls == i))
    res["classes"][nm] = round(a)
    print(f"  {nm:10s} {a:8.0f} km2  {100*a/area_of(valid):5.1f}%")

# --- district breakdown -----------------------------------------------------
dist = gpd.read_file("data/districts_ms.gpkg").to_crs(32735)
dist_r = rasterize([(geom, i + 1) for i, geom in enumerate(dist.geometry)],
                   out_shape=(H, W), transform=TR, fill=0, dtype="uint16")
for i, row in dist.iterrows():
    m = (dist_r == i + 1)
    hv = valid & m & (cls >= 4)
    res["districts"][row["district"]] = {
        "area_km2": round(area_of(m & prov)),
        "high_plus_km2": round(area_of(hv)),
        "mean_score": round(float(np.nanmean(suit[m & valid])), 3) if (m & valid).any() else None,
        "mean_ghi": round(float(np.nanmean(ghi[m & prov])), 3)}
    print(f"  {row['district']:20s} high+ {res['districts'][row['district']]['high_plus_km2']:6d} km2")

# --- sensitivity: one-at-a-time +-20 % on each weight ------------------------
base_high = area_of(valid & (cls >= 4))
for c in CRITERIA:
    for d, tag in [(1.2, "+20%"), (0.8, "-20%")]:
        wmod = {k: (v * d if k == c else v) for k, v in WEIGHTS.items()}
        tot = sum(wmod.values())
        wmod = {k: v / tot for k, v in wmod.items()}
        s2 = overlay(wmod)
        c2 = np.zeros((H, W), dtype="uint8")
        c2[valid] = np.digitize(s2[valid], CLASS_BREAKS) + 1
        a = area_of(valid & (c2 >= 4))
        res["sensitivity"][f"{c} {tag}"] = {
            "high_plus_km2": round(a),
            "change_pct": round(100 * (a - base_high) / base_high, 2)}

# --- validation at known project sites ---------------------------------------
SITES = [
    ("Blanket Mine Solar Farm (12 MW, operating)", -20.8552, 28.9130),
    ("Gwanda Timber Farm / Matshela (100 MW, licensed)", -20.9426, 29.0016),
    ("ZPC-Intratrek Gwanda (100 MW, proposed)", -20.7365, 28.9396),
    ("Nottingham Estate (4.5 MW, operating)", -22.1124, 29.6454),
    ("Falcon College Esigodini (1 MW, operating)", -20.2172, 28.9684),
    ("Mashaba Solar Mini-Grid (99 kW)", -21.7342, 28.9758),
]
t35 = Transformer.from_crs(4326, 32735, always_xy=True)
for name, lat, lon in SITES:
    x, y = t35.transform(lon, lat)
    c0, r0 = int((x - minx) // 250), int((maxy - y) // 250)
    sc = suit[r0, c0]
    # a site may fall on an excluded cell (it is built now); check 3x3 window
    win = suit[max(0, r0-1):r0+2, max(0, c0-1):c0+2]
    wmax = float(np.nanmax(win)) if np.isfinite(win).any() else None
    k = int(cls[r0, c0])
    res["sites"].append({"name": name, "score": None if np.isnan(sc) else round(float(sc), 3),
                         "class": CLASS_NAMES[k - 1] if k else "excluded",
                         "window_max": None if wmax is None else round(wmax, 3),
                         "ghi": round(float(ghi[r0, c0]), 3),
                         "d_grid_km": round(float(d_grid[r0, c0]), 1)})
    print(f"  site {name[:44]:46s} score {res['sites'][-1]['score']} class {res['sites'][-1]['class']}")

json.dump(res, open("out/results.json", "w"), indent=1)
print("out/results.json written")
