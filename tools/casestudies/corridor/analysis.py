"""Least-cost corridor analysis for elephants between Hwange and Chizarira National Parks.
Factors are reclassified to resistance (1 to 100), combined by an AHP weighted overlay, then cost-weighted distance
from each park, the least-cost path and a corridor zone (cost-distance sum within 5, 10 and 20 % of the minimum).
All on the 100 m UTM 35S grid from fetch_open.py. Writes data/*.npy, data/*.gpkg and data/summary.json."""
import json, numpy as np, pandas as pd, rasterio, geopandas as gpd
from rasterio.features import rasterize
from scipy import ndimage as ndi
from scipy.stats import mannwhitneyu
from skimage.graph import MCP_Geometric
from shapely.geometry import LineString, Point

G = json.load(open("raw/grid.json")); R = G["res"]; H, W = G["h"], G["w"]
TR = rasterio.transform.from_origin(G["x0"], G["y1"], R, R); CRS = "EPSG:32735"
rd = lambda f: rasterio.open(f"raw/{f}.tif").read(1)
lc, dem, slope, pop = rd("lc"), rd("dem"), rd("slope"), rd("pop").astype("float64")
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(CRS)
lakes = gpd.read_file("zip://../../corridors/raw/ne_10m_lakes.zip").to_crs(CRS).cx[G["x0"]:G["x0"] + W * R, G["y1"] - H * R:G["y1"]]
pa = gpd.read_file("../baobab/raw/wdpa.geojson").to_crs(CRS)
roads = gpd.read_file("raw/osm_roads.gpkg").to_crs(CRS); rivers = gpd.read_file("raw/osm_rivers.gpkg").to_crs(CRS)
ras = lambda geoms: rasterize(geoms, (H, W), transform=TR, fill=0, default_value=1, all_touched=True).astype(bool)
inside = rasterize(zwe.geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool)
lake = ras(lakes.geometry) if len(lakes) else np.zeros((H, W), bool)
M = inside & ~lake                                    # land in Zimbabwe; everything else is a barrier
hw = rasterize(pa[pa.NAME.eq("Hwange") & pa.DESIG_ENG.eq("National Park")].geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool) & M
cz = rasterize(pa[pa.NAME.eq("Chizarira") & pa.DESIG_ENG.eq("National Park")].geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool) & M
prot = pa[pa.DESIG_ENG.isin(["National Park", "Safari Area", "State Forest", "Recreation Park"])]
PROT = rasterize(prot.geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool) & M
WMA = rasterize(pa[pa.DESIG_ENG.eq("Wildlife Management Area")].geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool) & M & ~PROT

# ---- factors, each reclassified to resistance 1 (easy) to 100 (hard)
def classify(x, breaks, vals):
    return np.asarray(vals, "float32")[np.digitize(x, breaks)]

LC_R = {10: 1, 20: 5, 30: 10, 90: 20, 60: 50, 40: 80, 50: 100, 80: 100, 70: 100, 95: 20, 100: 10}
f_lc = np.vectorize(lambda v: LC_R.get(int(v), 50), otypes=["float32"])(lc)
dens = ndi.uniform_filter(pop, size=21, mode="constant") * 100      # people per km², 2.1 km moving window
f_pop = classify(dens, [2, 5, 11, 25], [1, 10, 40, 80, 100])
road_m = ras(roads.geometry); d_road = ndi.distance_transform_edt(~road_m) * R
f_road = classify(d_road, [500, 1000, 2000, 5000], [100, 70, 40, 15, 1])
riv_m = ras(rivers.geometry) | (lc == 80) & ~lake; d_riv = ndi.distance_transform_edt(~riv_m) * R
f_wat = classify(d_riv, [1000, 3000, 5000, 10000], [1, 10, 30, 60, 100])
f_slp = classify(slope, [5, 10, 20, 30], [1, 10, 40, 70, 100])
FAC = {"pop": f_pop, "lc": f_lc, "road": f_road, "wat": f_wat, "slp": f_slp}

# ---- AHP weights (Saaty scale): people > land cover > roads > water > slope
A = np.array([[1, 2, 3, 4, 5], [1 / 2, 1, 2, 3, 4], [1 / 3, 1 / 2, 1, 2, 3], [1 / 4, 1 / 3, 1 / 2, 1, 2], [1 / 5, 1 / 4, 1 / 3, 1 / 2, 1]])
ev, evec = np.linalg.eig(A); k = np.argmax(ev.real); w = np.abs(evec[:, k].real); w /= w.sum()
lmax = ev.real[k]; CI = (lmax - 5) / 4; CR = CI / 1.12
WTS = dict(zip(FAC, w))


def cost_of(wts):
    c = sum(wts[n] * FAC[n] for n in FAC); c = np.where(M, c, np.inf); return c.astype("float64")


def run(wts):
    c = cost_of(wts)
    mh = MCP_Geometric(c, sampling=(R / 1000, R / 1000)); ch, _ = mh.find_costs(list(zip(*np.nonzero(hw))))
    mc = MCP_Geometric(c, sampling=(R / 1000, R / 1000)); cc, _ = mc.find_costs(list(zip(*np.nonzero(cz))))
    s = ch + cc; mn = np.nanmin(s[np.isfinite(s)])
    end = np.unravel_index(np.argmin(np.where(cz, ch, np.inf)), ch.shape)
    path = np.array(mh.traceback(end))
    return c, ch, cc, s, mn, path


cost, ch, cc, S, MN, path = run(WTS)
rel = (S - MN) / MN * 100                                  # % above the least cost
cls = np.zeros((H, W), "uint8")                            # 3 high (<=5 %), 2 moderate (5-10 %), 1 low (10-20 %)
for v, t in [(1, 20), (2, 10), (3, 5)]: cls[(rel <= t) & M] = v
cls[hw | cz] = 0

# ---- least-cost path: keep the part between the two parks
pr, pc = path[:, 0], path[:, 1]
out_p = ~(hw[pr, pc] | cz[pr, pc]); i0 = np.argmax(out_p); i1 = len(out_p) - np.argmax(out_p[::-1])
seg = path[max(i0 - 1, 0):i1 + 1]
xy = np.c_[G["x0"] + (seg[:, 1] + 0.5) * R, G["y1"] - (seg[:, 0] + 0.5) * R]
step = np.r_[0, np.hypot(*np.diff(xy, axis=0).T)]; dist = np.cumsum(step) / 1000
lcp = gpd.GeoDataFrame({"name": ["Least-cost path"]}, geometry=[LineString(xy)], crs=CRS)
lcp.to_file("data/lcp.gpkg")
full_xy = np.c_[G["x0"] + (pc + 0.5) * R, G["y1"] - (pr + 0.5) * R]
gpd.GeoDataFrame(geometry=[LineString(full_xy)], crs=CRS).to_file("data/lcp_full.gpkg")
L = float(dist[-1])
sr, sc = seg[:, 0], seg[:, 1]
NAMES = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare", 80: "Water", 90: "Wetland"}
lc_path = {NAMES.get(int(v), str(v)): round(float(step[lc[sr, sc] == v].sum() / 1000), 1) for v in np.unique(lc[sr, sc])}
road_x = int(lcp.geometry[0].intersection(roads.unary_union).geoms.__len__()) if lcp.geometry[0].intersects(roads.unary_union) else 0
try: road_x = len(lcp.geometry[0].intersection(roads.unary_union).geoms)
except AttributeError: road_x = 1 if not lcp.geometry[0].intersection(roads.unary_union).is_empty else 0
prot_km = float(step[PROT[sr, sc] & ~(hw | cz)[sr, sc]].sum() / 1000); wma_km = float(step[WMA[sr, sc]].sum() / 1000)
profile = pd.DataFrame({"km": dist.round(2), "elev": dem[sr, sc].round(0), "cost": cost[sr, sc].round(2), "lc": lc[sr, sc],
                        "dens": dens[sr, sc].round(1)})
profile.to_csv("data/profile.csv", index=False)

# ---- corridor zone (<= 10 %) outside the two parks: composition, people, roads, width
CZ = (cls >= 2); a_km = lambda m: float(m.sum() * R * R / 1e6)
corr = {"area_km2": {c: round(a_km(cls == v), 0) for c, v in [("high", 3), ("moderate", 2), ("low", 1)]}}
corr["lc_pct"] = {NAMES.get(int(v), str(v)): round(float((lc[CZ] == v).mean() * 100), 1) for v in np.unique(lc[CZ])}
corr["people"] = int(round(pop[CZ].sum())); corr["people_high"] = int(round(pop[cls == 3].sum()))
corr["prot_pct"] = round(float(PROT[CZ].mean() * 100), 1); corr["wma_pct"] = round(float(WMA[CZ].mean() * 100), 1)
corr["dens_mean"] = round(float(pop[CZ].sum() / a_km(CZ)), 1)
# width of the corridor (<= 10 %) along the path: twice the distance from the path to the corridor edge
edt = ndi.distance_transform_edt(CZ | hw | cz) * R / 1000
width = 2 * edt[sr, sc]; profile["width"] = width.round(2); profile.to_csv("data/profile.csv", index=False)
mid = (~hw[sr, sc]) & (~cz[sr, sc])
iw = np.argmin(np.where(mid, width, np.inf)); pinch = xy[iw]
gpd.GeoDataFrame({"width_km": [round(float(width[iw]), 1)]}, geometry=[Point(pinch)], crs=CRS).to_file("data/pinch.gpkg")

# ---- elephant records (GBIF): resistance at records against all land cells
g = pd.read_csv("raw/gbif.csv"); g = g[(g.coordinateUncertaintyInMeters.fillna(0) <= 5000)]
gg = gpd.GeoDataFrame(g, geometry=gpd.points_from_xy(g.decimalLongitude, g.decimalLatitude), crs=4326).to_crs(CRS)
rc = ((G["y1"] - gg.geometry.y) / R).astype(int).values; cc_ = ((gg.geometry.x - G["x0"]) / R).astype(int).values
ok = (rc >= 0) & (rc < H) & (cc_ >= 0) & (cc_ < W); rc, cc_ = rc[ok], cc_[ok]; ok2 = M[rc, cc_]; rc, cc_ = rc[ok2], cc_[ok2]
gg = gg[ok][ok2]; gg.to_file("data/gbif.gpkg")
rng = np.random.default_rng(1); bg = np.flatnonzero(M.ravel()); bg = rng.choice(bg, 10000, replace=False)
c_rec, c_bg = cost[rc, cc_], cost.ravel()[bg]
u, pval = mannwhitneyu(c_rec, c_bg, alternative="less")
inpark = (hw | cz | PROT)[rc, cc_]

# ---- sensitivity: other weight sets
SETS = {"AHP weights (base)": WTS, "Equal weights": {n: 0.2 for n in FAC},
        "Land cover first": dict(zip(FAC, [w[1], w[0], w[2], w[3], w[4]])),
        "People only doubled": {n: (2 * WTS[n] if n == "pop" else WTS[n]) / (1 + WTS["pop"]) for n in FAC},
        "Without water": {n: (0 if n == "wat" else WTS[n] / (1 - WTS["wat"])) for n in FAC}}
sens = {}
for nm, wt in SETS.items():
    if nm.startswith("AHP"): p2 = path
    else: _, _, _, _, _, p2 = run(wt)
    r2, c2 = p2[:, 0], p2[:, 1]; o2 = ~(hw[r2, c2] | cz[r2, c2])
    near = ndi.distance_transform_edt(~ras(lcp.geometry))[r2[o2], c2[o2]] * R
    xy2 = np.c_[G["x0"] + (c2 + 0.5) * R, G["y1"] - (r2 + 0.5) * R]
    gap = float(np.hypot(*np.diff(xy2, axis=0).T)[o2[1:]].sum() / 1000)
    sens[nm] = {"weights": {k: round(float(v), 3) for k, v in wt.items()}, "len_km": round(gap, 1),
                "in_corr_pct": round(float(CZ[r2[o2], c2[o2]].mean() * 100), 1), "within2km_pct": round(float((near <= 2000).mean() * 100), 1)}
    if not nm.startswith("AHP"): gpd.GeoDataFrame({"set": [nm]}, geometry=[LineString(xy2)], crs=CRS).to_file(f"data/sens_{len(sens)}.gpkg")

# ---- straight-line gap between the parks
from shapely.ops import nearest_points
hwp = pa[pa.NAME.eq("Hwange") & pa.DESIG_ENG.eq("National Park")].unary_union; czp = pa[pa.NAME.eq("Chizarira") & pa.DESIG_ENG.eq("National Park")].unary_union
gap_km = hwp.distance(czp) / 1000
mean_cost = {n: round(float(FAC[n][M].mean()), 1) for n in FAC}
SM = {"grid": [W, H, R], "land_km2": round(a_km(M)), "hw_km2": round(a_km(hw)), "cz_km2": round(a_km(cz)), "gap_km": round(gap_km, 1),
      "ahp": {"weights": {k: round(float(v), 3) for k, v in WTS.items()}, "lmax": round(float(lmax), 3), "CI": round(float(CI), 4), "CR": round(float(CR), 4)},
      "cost": {"mean": round(float(cost[M].mean()), 1), "median": round(float(np.median(cost[M])), 1),
               "share": {f"{a}-{b}": round(float(((cost >= a) & (cost < b) & M).sum() / M.sum() * 100), 1) for a, b in [(1, 10), (10, 25), (25, 50), (50, 101)]}},
      "factor_mean": mean_cost,
      "lcp": {"length_km": round(L, 1), "cost": round(float(MN), 1), "ratio": round(L / gap_km, 2), "lc_km": lc_path, "road_crossings": road_x,
              "prot_km": round(prot_km, 1), "wma_km": round(wma_km, 1), "elev_min": int(dem[sr, sc].min()), "elev_max": int(dem[sr, sc].max()),
              "mean_cost": round(float(cost[sr, sc].mean()), 1), "max_dens": round(float(dens[sr, sc].max()), 1),
              "start_xy": xy[0].round(0).tolist(), "end_xy": xy[-1].round(0).tolist()},
      "corridor": corr, "pinch": {"width_km": round(float(width[iw]), 1), "km_along": round(float(dist[iw]), 1), "xy": pinch.round(0).tolist(),
                                  "lc": NAMES.get(int(lc[sr[iw], sc[iw]])), "dens": round(float(dens[sr[iw], sc[iw]]), 1),
                                  "d_road_m": round(float(d_road[sr[iw], sc[iw]]))},
      "width": {"median": round(float(np.median(width[mid])), 1), "lt2_km": round(float(step[mid & (width < 2)].sum() / 1000), 1)},
      "gbif": {"n": int(len(c_rec)), "in_protected": int(inpark.sum()), "median_rec": round(float(np.median(c_rec)), 1),
               "median_bg": round(float(np.median(c_bg)), 1), "U": float(u), "p": float(pval), "years": [int(gg.year.min()), int(gg.year.max())]},
      "sens": sens}
json.dump(SM, open("data/summary.json", "w"), indent=1)
np.savez_compressed("data/rasters.npz", cost=cost.astype("float32"), cls=cls, M=M, hw=hw, cz=cz, PROT=PROT, WMA=WMA, dens=dens.astype("float32"),
                    **{f"f_{n}": FAC[n].astype("uint8") for n in FAC}, transform=np.array(TR)[:6])
print(json.dumps({k: SM[k] for k in ("gap_km", "ahp", "cost", "lcp", "corridor", "pinch", "width", "gbif")}, indent=0)[:3000])
for k, v in sens.items(): print(k, v["len_km"], v["in_corr_pct"], v["within2km_pct"])
