"""Five-class versions of the soil erosion and gully risk maps (for display). Writes rast/erisk5.tif, rast/grisk5.tif, out/risk5.json."""
import json, numpy as np, rasterio, scipy.ndimage as nd
s = rasterio.open("rast/gully.tif"); p = s.profile; p.update(dtype="uint8", nodata=0, compress="lzw")
dm = rasterio.open("rast/dist.tif").read(1) == 1; lc = rasterio.open("rast/lc.tif").read(1); land = dm & (lc != 80)
def disk(r): y, x = np.ogrid[-r:r + 1, -r:r + 1]; return ((x * x + y * y) <= r * r).astype("f4")
den = lambda k: np.maximum(nd.convolve(land.astype("f4"), k, mode="constant"), 1)
g = s.read(1).astype("f4"); k = disk(17); d = nd.convolve(g * land, k, mode="constant") * 0.03 / (den(k) * 0.0009)
A = rasterio.open("rast/A.tif").read(1).astype("f4"); A = np.where(land & np.isfinite(A), A, 0); k2 = disk(8); m = nd.convolve(A, k2, mode="constant") / den(k2)
out = {}
for name, v, br in (("erisk5", m, [2, 5, 10, 20]), ("grisk5", d, [0.15, 0.3, 0.6, 1.0])):
    c = np.zeros(g.shape, "u1"); c[land] = 1
    for i, b in enumerate(br): c[land & (v >= b)] = i + 2
    with rasterio.open(f"rast/{name}.tif", "w", **p) as o: o.write(c, 1)
    n = np.array([(c == i).sum() for i in range(1, 6)]) * 0.0009
    out[name] = {"breaks": br, "km2": [round(float(x), 1) for x in n], "pct": [round(float(x / n.sum() * 100), 1) for x in n]}
json.dump(out, open("out/risk5.json", "w"), indent=1); print(out)
