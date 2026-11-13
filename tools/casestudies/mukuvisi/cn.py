"""Hydrologic soil groups and SCS curve numbers on the 30 m grid.
Soil: iSDAsoil 30 m sand and clay, depth-weighted mean over 0-30 cm (0-20 cm and the top 10 cm of 20-50 cm), USDA
texture class, then HSG. SoilGrids 2.0 (masked over built-up land) is kept as a check where it has values
(A sand, loamy sand, sandy loam; B loam, silt loam, silt; C sandy clay loam; D clay loam, silty clay loam, sandy clay, silty clay, clay).
Land cover: ESA WorldCover 2021. Curve numbers for average antecedent moisture (AMC II) from USDA TR-55 (1986) Table 2-2.
Output: data/cn.npz (hsg, cn, lc) and data/cn.json (shares and mean CN by sub-catchment)."""
import json, numpy as np, rasterio

def rd(n):
    with rasterio.open(f"raw/{n}.tif") as s: return s.read(1).astype("float32")

Z = np.load("data/grid.npz"); CM = Z["catch"]; lab = Z["lab"]
sand = (rd("isda_sand_0-20") * 20 + rd("isda_sand_20-50") * 10) / 30  # %
clay = (rd("isda_clay_0-20") * 20 + rd("isda_clay_20-50") * 10) / 30
sgs = (rd("sand_0-5cm") * 5 + rd("sand_5-15cm") * 10 + rd("sand_15-30cm") * 15) / 300
sgc = (rd("clay_0-5cm") * 5 + rd("clay_5-15cm") * 10 + rd("clay_15-30cm") * 15) / 300
ok = CM & (sgs > 0)
chk = {"sg_valid_share": float(ok.sum() / CM.sum()), "sand_isda": float(sand[ok].mean()), "sand_sg": float(sgs[ok].mean()),
       "clay_isda": float(clay[ok].mean()), "clay_sg": float(sgc[ok].mean()), "r_sand": float(np.corrcoef(sand[ok], sgs[ok])[0, 1]),
       "r_clay": float(np.corrcoef(clay[ok], sgc[ok])[0, 1])}
silt = 100 - sand - clay
lc = rd("lc").astype("uint8")


def texture(sa, si, cl):  # USDA texture triangle
    if si + 1.5 * cl < 15: return "sand"
    if si + 2 * cl < 30: return "loamy sand"
    if (7 <= cl < 20 and sa > 52 and si + 2 * cl >= 30) or (cl < 7 and si < 50 and si + 2 * cl >= 30): return "sandy loam"
    if 7 <= cl < 27 and 28 <= si < 50 and sa <= 52: return "loam"
    if (si >= 50 and 12 <= cl < 27) or (50 <= si < 80 and cl < 12): return "silt loam"
    if si >= 80 and cl < 12: return "silt"
    if 20 <= cl < 35 and si < 28 and sa > 45: return "sandy clay loam"
    if 27 <= cl < 40 and 20 < sa <= 45: return "clay loam"
    if 27 <= cl < 40 and sa <= 20: return "silty clay loam"
    if cl >= 35 and sa > 45: return "sandy clay"
    if cl >= 40 and si >= 40: return "silty clay"
    return "clay"


HSG = {"sand": 1, "loamy sand": 1, "sandy loam": 1, "loam": 2, "silt loam": 2, "silt": 2, "sandy clay loam": 3}
tex = np.full(sand.shape, "", object); hsg = np.zeros(sand.shape, "uint8")
for i, j in zip(*np.nonzero(CM)):
    t = texture(sand[i, j], silt[i, j], clay[i, j]); tex[i, j] = t; hsg[i, j] = HSG.get(t, 4)
# TR-55 Table 2-2 (A, B, C, D) joined to WorldCover classes
CNT = {10: (36, 60, 73, 79),   # tree cover: woods, fair condition
       20: (35, 56, 70, 77),   # shrubland: brush-weed-grass mixture, fair
       30: (49, 69, 79, 84),   # grassland: pasture, grassland or range, fair
       40: (67, 78, 85, 89),   # cropland: row crops, straight row, good
       50: (77, 85, 90, 92),   # built-up: residential 1/8 acre (65% impervious)
       60: (77, 86, 91, 94),   # bare: fallow, bare soil
       80: (98, 98, 98, 98),   # permanent water
       90: (85, 85, 85, 85)}   # herbaceous wetland
cn = np.zeros(sand.shape, "float32")
for k, v in CNT.items():
    for g in range(4): cn[CM & (lc == k) & (hsg == g + 1)] = v[g]
miss = CM & (cn == 0); print("cells without CN", int(miss.sum()), np.unique(lc[miss]))
cn[miss] = 79
np.savez_compressed("data/cn.npz", hsg=hsg, cn=cn, lc=lc, sand=sand, clay=clay)
LCN = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare", 80: "Water", 90: "Wetland"}
n = CM.sum()
J = {"lc_share": {LCN.get(int(k), str(k)): round(float((lc[CM] == k).sum() / n * 100), 2) for k in np.unique(lc[CM])},
     "hsg_share": {"ABCD"[g - 1]: round(float((hsg[CM] == g).sum() / n * 100), 2) for g in range(1, 5)},
     "texture_share": {t: round(float((tex[CM] == t).sum() / n * 100), 2) for t in set(tex[CM])},
     "check_soilgrids": chk, "sand_mean": float(sand[CM].mean()), "clay_mean": float(clay[CM].mean()), "cn_mean": float(cn[CM].mean()),
     "sub": {int(i): {"cn": round(float(cn[lab == i].mean()), 1), "built": round(float((lc[lab == i] == 50).mean() * 100), 1),
                      "hsg_d": round(float((hsg[lab == i] == 4).mean() * 100), 1)} for i in range(1, lab.max() + 1)}}
json.dump(J, open("data/cn.json", "w"), indent=1); print(json.dumps(J))
