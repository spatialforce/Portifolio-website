"""Download MODIS MCD64A1 v6.1 burn date (day of year, 0 = not burned) for each calendar year, the MCD12Q1 land cover
and a protected-area mask for Zimbabwe, all on the native MODIS sinusoidal grid (equal area, 463.3127 m pixels)."""
import os, sys, urllib.request, ee
ee.Initialize()
R = ee.Geometry.Rectangle([25.1, -22.5, 33.2, -15.5], None, False)
C = ee.ImageCollection("MODIS/061/MCD64A1")
print("last image", ee.Date(C.aggregate_max("system:time_start")).format("YYYY-MM-dd").getInfo(), flush=True)
P = dict(region=R, scale=463.3127165, crs="SR-ORG:6974", format="GEO_TIFF")
def get(img, name):
    if os.path.exists(name): return
    urllib.request.urlretrieve(img.getDownloadURL(P), name); print(name, flush=True)
for y in range(2001, 2026):
    get(C.filterDate(f"{y}-01-01", f"{y + 1}-01-01").select("BurnDate").max().unmask(0).toInt16(), f"data/burn_{y}.tif")
get(ee.ImageCollection("MODIS/061/MCD12Q1").filterDate("2022-01-01", "2023-01-01").first().select("LC_Type1").toByte(), "data/lc_2022.tif")
wd = ee.FeatureCollection("WCMC/WDPA/current/polygons").filterBounds(R)
get(ee.Image(0).byte().paint(wd, 1), "data/protected.tif")
print("WDPA names", wd.filter(ee.Filter.eq("ISO3", "ZWE")).aggregate_array("DESIG_ENG").distinct().getInfo())
