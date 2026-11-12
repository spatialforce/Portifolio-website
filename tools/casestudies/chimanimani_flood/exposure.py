"""Buildings (Google Open Buildings v3, confidence 0.75 or more) and people (WorldPop 2020 constrained) per 30 m cell
-> rast/bld.npy, rast/pop.npy. overlay.py counts them in each susceptibility class."""
import numpy as np, rasterio
from pyproj import Transformer
H, W = 2834, 2600; TW, TH = W // 2, H // 2
def tiles(n):
    a = np.zeros((H, W), np.float32)
    for i in range(2):
        for j in range(2):
            with rasterio.open(f"rast/{n}_{i}{j}.tif") as d: a[j*TH:(j+1)*TH, i*TW:(i+1)*TW] = d.read(1)
    a[~np.isfinite(a)] = 0; return a.astype(np.float64)
bld, pop = tiles("bld"), tiles("pop")
# fetch2 sampled the 100 m WorldPop count into every 30 m cell, so rescale by 900 m2 / native 3 arc-second pixel area
yy = 7860000 - 15 - 30 * np.arange(H); lat = Transformer.from_crs(32736, 4326, always_xy=True).transform(np.full(H, 470000), yy)[1]
a3 = (6371008.8 * np.radians(3 / 3600)) ** 2 * np.cos(np.radians(lat))
pop *= (900 / a3)[:, None]
np.save("rast/bld.npy", bld); np.save("rast/pop.npy", pop)
