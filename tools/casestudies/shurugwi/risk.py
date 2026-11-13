"""Gully erosion risk: length of gully-prone path within ~1 km of each cell (km/km2), in three plain classes."""
import json, numpy as np, rasterio, scipy.ndimage as nd
s = rasterio.open("rast/gully.tif"); g = s.read(1).astype("f4"); dm = rasterio.open("rast/dist.tif").read(1) == 1
lc = rasterio.open("rast/lc.tif").read(1); land = dm & (lc != 80)
r = 17; y, x = np.ogrid[-r:r + 1, -r:r + 1]; k = ((x * x + y * y) <= r * r).astype("f4")
num = nd.convolve(g * land, k, mode="constant"); den = nd.convolve(land.astype("f4"), k, mode="constant")
d = np.where(den > 0, num * 0.03 / (np.maximum(den, 1) * 0.0009), 0)
v = d[land]; print("pct", [round(float(np.percentile(v, p)), 2) for p in (25, 50, 75, 90, 95)])
br = [0.3, 0.6]
c = np.zeros(g.shape, "u1"); c[land] = 1; c[land & (d >= br[0])] = 2; c[land & (d >= br[1])] = 3
p = s.profile; p.update(dtype="uint8", nodata=0, compress="lzw")
with rasterio.open("rast/grisk.tif", "w", **p) as o: o.write(c, 1)
cnt = {n: round(float((c == i).sum() * 0.0009), 1) for i, n in ((1, "Low"), (2, "Moderate"), (3, "High"))}
tot = sum(cnt.values()); out = {"breaks": [round(b, 2) for b in br], "km2": cnt, "pct": {k_: round(v_ / tot * 100, 1) for k_, v_ in cnt.items()}}
cl = rasterio.open("rast/cls.tif").read(1); hi = c == 3
out["high_on_high_soil_loss_pct"] = round(float((hi & (cl >= 4)).sum() / hi.sum() * 100), 1)
json.dump(out, open("out/grisk.json", "w"), indent=1); print(out)

import geopandas as gpd
from rasterio.features import rasterize
w = gpd.read_file("out/wards.gpkg").to_crs(s.crs)
z = rasterize([(geom, i + 1) for i, geom in enumerate(w.geometry)], out_shape=g.shape, transform=s.transform)
w["ghi"] = [round(float((c[z == i + 1] == 3).sum() / max((c[z == i + 1] > 0).sum(), 1) * 100), 1) for i in range(len(w))]
w.to_file("out/wards.gpkg"); print(w[["ward", "gully", "ghi", "mean"]].sort_values("ghi", ascending=False).to_string(index=False))
import numpy as np2
print("r ghi-mean rural", round(float(np2.corrcoef(w[w.ward != "Town"].ghi, w[w.ward != "Town"]["mean"])[0, 1]), 2))

# soil erosion risk for the map: soil loss averaged over ~250 m, three plain classes
A = rasterio.open("rast/A.tif").read(1).astype("f4"); A = np.where(land & np.isfinite(A), A, 0)
r2 = 8; y2, x2 = np.ogrid[-r2:r2 + 1, -r2:r2 + 1]; k2 = ((x2 * x2 + y2 * y2) <= r2 * r2).astype("f4")
m = nd.convolve(A, k2, mode="constant") / np.maximum(nd.convolve(land.astype("f4"), k2, mode="constant"), 1)
e = np.zeros(g.shape, "u1"); e[land] = 1; e[land & (m >= 5)] = 2; e[land & (m >= 10)] = 3
with rasterio.open("rast/erisk.tif", "w", **p) as o: o.write(e, 1)
n = {i: float((e == i).sum()) for i in (1, 2, 3)}; t = sum(n.values())
print("soil risk km2", {i: round(v * 0.0009, 1) for i, v in n.items()}, "pct", {i: round(v / t * 100, 1) for i, v in n.items()})
