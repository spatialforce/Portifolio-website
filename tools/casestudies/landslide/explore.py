"""Quick look: factor percentiles over the district and at Idai landslide source points (not used to set weights)."""
import numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
F = "../chimanimani_flood/"
H, W, RES = 2834, 2600, 30; X0, Y0 = 430000, 7860000
S = dict(np.load(F + "rast/stack.npz")); M = S["mask"] == 1
T = rasterio.transform.from_origin(X0, Y0, RES, RES)
p = gpd.read_file(F + "data/dl/idai-landslide-source-points").to_crs(32736)
pts = rasterize([(g, 1) for g in p.geometry], (H, W), transform=T, fill=0).astype(bool) & M
print("points", len(p), "cells in district", pts.sum())
e = S["elev"]; gy, gx = np.gradient(e, RES); asp = (np.degrees(np.arctan2(-gx, gy)) + 360) % 360
S["aspect"] = asp
for k in ["slope", "elev", "curv", "dstream", "twi", "chirps", "clay", "sand", "aspect", "tpi"]:
    a = S[k]; q = [1, 10, 25, 50, 75, 90, 99]
    print(k.ljust(8), "all", np.round(np.percentile(a[M], q), 2), " pts", np.round(np.percentile(a[pts], q), 2))
lu = S["lulc"]
for c in np.unique(lu[M]): print("lulc", int(c), round((lu[M] == c).mean() * 100, 1), round((lu[pts] == c).mean() * 100, 1))
np.save("pts.npy", pts)
