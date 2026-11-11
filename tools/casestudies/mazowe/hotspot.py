"""Download 30 m bare-ground masks (all four windows) and a 2025 dry-season true-colour composite
for the Shamva hotspot (reaches 14 to 17)."""
import urllib.request, ee, geopandas as gpd
from analysis import bare, landsat, scale_l, AOI
c = gpd.read_file("data/reaches_corridor.gpkg").to_crs(4326)
h = c[c.reach.between(14, 17)]
x0, y0, x1, y1 = h.total_bounds; p = 0.02
R = ee.Geometry.Rectangle([x0 - p, y0 - p, x1 + p, y1 + p])
print("bbox", [round(v, 3) for v in (x0 - p, y0 - p, x1 + p, y1 + p)])
for y in [2000, 2009, 2017, 2025]:
    b, _ = bare(y)
    u = b.unmask(0).toByte().getDownloadURL({"region": R, "scale": 30, "crs": "EPSG:32736", "format": "GEO_TIFF"})
    urllib.request.urlretrieve(u, f"data/hot_bare_{y}.tif"); print(y, flush=True)
