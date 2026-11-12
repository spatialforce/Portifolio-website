"""Stack all factors on the district grid, rasterise the district and the Cyclone Idai inventory -> rast/stack.npz."""
import numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.transform import from_origin

X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834
T = from_origin(X0, Y0, RES, RES); TW, TH = W // 2, H // 2


def tiles(n):
    a = np.zeros((H, W), np.float32)
    for i in range(2):
        for j in range(2):
            with rasterio.open(f"rast/{n}_{i}{j}.tif") as d: a[j * TH:(j + 1) * TH, i * TW:(i + 1) * TW] = d.read(1)
    return a


L = {k: rasterio.open(f"rast/t_{k}.tif").read(1) for k in
     ("elev", "slope", "hand", "twi", "dstream", "driver", "curv", "tpi", "upa", "streams")}
for n in ("rain", "chirps", "lulc", "clay", "sand"): L[n] = tiles(n)

d = gpd.read_file("data/dl/chimanimani-and-chipinge-district/Chimanimani and Chipinge District.shp").to_crs(32736)
dist = d[d.ADM2_EN == "Chimanimani"]
L["mask"] = rasterize(dist.geometry, (H, W), transform=T, fill=0, default_value=1).astype(np.uint8)
z = gpd.read_file("data/dl/idai-landslide-extent-maps_zones/Idai Landslide Extent Maps.shp").to_crs(32736)
code = {"Depletion zone": 1, "Run-out zone": 2, "Debris-rich Flow": 3}
# all_touched=False; debris-rich flow drawn last so it wins where zones touch
inv = np.zeros((H, W), np.uint8)
for k in ("Depletion zone", "Run-out zone", "Debris-rich Flow"):
    g = z[z.Zone == k].geometry
    inv = np.where(rasterize(g, (H, W), transform=T, fill=0, default_value=1) == 1, code[k], inv)
L["inv"] = inv
np.savez_compressed("rast/stack.npz", **L)
m = L["mask"] == 1
print("district km2", m.sum() * 0.0009)
for k, c in code.items(): print(k, "km2", round(((inv == c) & m).sum() * 0.0009, 2))
for k in ("elev", "slope", "hand", "rain", "chirps", "clay", "sand", "upa"):
    v = L[k][m]; print(k, np.round(np.percentile(v, [0, 1, 50, 99, 100]), 1))
print("lulc", dict(zip(*np.unique(L["lulc"][m], return_counts=True))))
