# Rebuild wpc2020: constrained WorldPop 2020 (Zimbabwe only) as density, mean-aggregated to the 0.01 deg grid, times cell area.
# (A direct sum reduceResolution into 0.01 deg cells lost most people; this method conserves totals.)
import io, urllib.request, rasterio, ee
ee.Initialize(project="directed-sun-490915-m4")
X0, Y1, R, W, H = 25.4, -16.6, 0.01, 320, 320
wp = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").filter(ee.Filter.eq("country", "ZWE")).filter(ee.Filter.eq("year", 2020)).first().select("population")
proj = ee.Projection("EPSG:4326", [R, 0, X0, 0, -R, Y1])
img = wp.divide(ee.Image.pixelArea()).unmask(0).reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj).multiply(ee.Image.pixelArea()).toFloat()
url = img.getDownloadURL({"crs": "EPSG:4326", "crs_transform": [R, 0, X0, 0, -R, Y1], "dimensions": f"{W}x{H}", "format": "GEO_TIFF"})
d = urllib.request.urlopen(url, timeout=900).read()
with rasterio.open(io.BytesIO(d)) as r, rasterio.open("rast/wpc2020.tif", "w", **(r.profile | {"compress": "deflate"})) as o: o.write(r.read())
# check: Hwange district total from the native layer
b = ee.Geometry.Rectangle([X0, -19.8, 28.6, Y1])
print("native box total", wp.reduceRegion(ee.Reducer.sum(), b, 100, maxPixels=1e10).getInfo())
