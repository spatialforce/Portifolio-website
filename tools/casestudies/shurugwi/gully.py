# Gully susceptibility from terrain and cover (run after rusle.py).
# Stream power index SPI = As tan(beta) (Moore et al., 1991), As = specific catchment area (m2 per m of contour width).
# Candidate flow paths: drainage area 0.5 to 100 ha (overland and ephemeral flow lines, not permanent river channels).
# Gully-prone: SPI in the top 10 % of candidate cells in the district AND rainy-season cover is thin (C >= 0.10), not water or built-up.
# The result ranks where concentrated runoff is strongest on thinly covered ground. It is not a map of measured gullies.
import json, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
def rd(n): return rasterio.open(f"rast/{n}.tif").read(1).astype("float64")
src = rasterio.open("rast/A.tif"); PROF = dict(src.profile, dtype="uint8", nodata=None, compress="deflate")
acc, s, C, lc, A, dist = rd("acc"), rd("slope"), rd("C"), rd("lc"), rd("A"), rd("dist") == 1
land = dist & ~np.isin(lc, [50, 80])
As = acc * 30.0; ha = acc * 0.09; spi = As * s / 100
cand = land & (ha >= 0.5) & (ha <= 100)
thr = float(np.percentile(spi[cand], 90))
g = cand & (spi >= thr) & (C >= 0.10)
with rasterio.open("rast/gully.tif", "w", **PROF) as d: d.write(g.astype("uint8"), 1)
km = lambda m: float(m.sum() * 0.03)   # 30 m cell along a flow path = 0.03 km
w = gpd.read_file("out/wards.gpkg")
dens = []
for nm, geom in zip(w.ward, w.geometry):
    m = (rasterize([geom], out_shape=A.shape, transform=src.transform) == 1) & dist
    area = m.sum() * 0.0009
    dens.append(round(km(g & m) / area, 2))
w["gully"] = dens; w.to_file("out/wards.gpkg")
LC = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 60: "Bare or sparse"}
bylc = [dict(lc=n, km=round(km(g & (lc == k)), 1), share=round(100 * (g & (lc == k)).sum() / g.sum(), 1),
             dens=round(km(g & (lc == k)) / ((land & (lc == k)).sum() * 0.0009), 2)) for k, n in LC.items() if (land & (lc == k)).sum() > 1000]
out = dict(spi_thr=round(thr, 1), cand_km=round(km(cand), 0), gully_km=round(km(g), 0),
           gully_dens=round(km(g) / (dist.sum() * 0.0009), 2),
           in_high_rusle=round(float(100 * (g & (A >= 10)).sum() / g.sum()), 1),
           slope_med=round(float(np.median(s[g])), 1), ha_med=round(float(np.median(ha[g])), 1), C_med=round(float(np.median(C[g])), 3),
           landcover=bylc)
json.dump(out, open("out/gully.json", "w"), indent=1); print(json.dumps(out))
print(sorted(zip(w.gully, w.ward), reverse=True)[:6])
