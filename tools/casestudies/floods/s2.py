"""Sentinel-2 L2A true-colour image (least-cloudy median) of a small window, for map backdrops.
Run: python -I s2.py <name> <lon0> <lon1> <lat0> <lat1> <date0> <date1> [scale]
Output: data/s2_<name>.tif  (bytes RGB, EPSG:32736)"""
import sys, urllib.request, ee
ee.Initialize(project="directed-sun-490915-m4")
n, x0, x1, y0, y1, d0, d1 = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6], sys.argv[7]
sc = float(sys.argv[8]) if len(sys.argv) > 8 else 20
g = ee.Geometry.Rectangle([x0, y0, x1, y1])
c = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(g).filterDate(d0, d1)
     .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30)))
def mask(i):
    s = i.select("SCL"); return i.updateMask(s.neq(8).And(s.neq(9)).And(s.neq(10)).And(s.neq(3)))
print("scenes", c.size().getInfo())
img = c.map(mask).median().select(["B4", "B3", "B2"]).divide(2800).pow(0.8).multiply(255).clamp(0, 255).toByte()
urllib.request.urlretrieve(img.getDownloadURL(dict(region=g, scale=sc, crs="EPSG:32736", format="GEO_TIFF")), f"data/s2_{n}.tif"); print("saved", n)
