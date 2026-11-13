# 90 m GLO-30 DEM over a wider box, used only for the hillshade outside the district on the maps.
import io, urllib.request, ee, numpy as np, rasterio
from rasterio.transform import from_origin
ee.Initialize(project="directed-sun-490915-m4")
x0, y0, x1, y1 = 178000, 7660000, 312000, 7812000; R = 90
W, H = (x1 - x0) // R, (y1 - y0) // R
img = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30).float()
url = img.getDownloadURL({"crs": "EPSG:32736", "crs_transform": [R, 0, x0, 0, -R, y1], "dimensions": f"{W}x{H}", "format": "GEO_TIFF"})
with rasterio.open(io.BytesIO(urllib.request.urlopen(url, timeout=600).read())) as s: a = s.read(1)
with rasterio.open("rast/dem_wide.tif", "w", driver="GTiff", height=H, width=W, count=1, dtype="float32", crs="EPSG:32736",
                   transform=from_origin(x0, y1, R, R), compress="deflate") as d: d.write(a, 1)
print("wide", a.shape, a.min(), a.max())
