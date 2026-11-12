# Copernicus GLO-30 DEM resampled (mean) to 90 m on EPSG:32736 over Masvingo Province + 30 km, and WorldPop 2020
# unconstrained (wp2020) and constrained (wpc2020, used) 100 m regridded (sum) to the same 90 m grid. Tiled downloads from Earth Engine, stitched locally.
import os, io, json, urllib.request, numpy as np, rasterio, geopandas as gpd, ee
ee.Initialize(project="directed-sun-490915-m4")
B = "../population/raw/bnd/"
prov = gpd.read_file(B + "zwe_admin1.shp"); prov = prov[prov.adm1_name == "Masvingo"].to_crs(32736)
prov.to_file("data/masvingo.geojson")
R, PAD = 90, 30000
x0, y0, x1, y1 = prov.total_bounds
x0, y0 = int((x0 - PAD) // R) * R, int((y0 - PAD) // R) * R
x1, y1 = int((x1 + PAD) // R + 1) * R, int((y1 + PAD) // R + 1) * R
W, H = (x1 - x0) // R, (y1 - y0) // R
json.dump({"bounds": [x0, y0, x1, y1], "res": R, "crs": "EPSG:32736"}, open("data/grid.json", "w")); print("grid", W, H)

def dl(img, name, n=6):
    if os.path.exists(f"rast/{name}.tif"): return
    out = None; tw, th = -(-W // n), -(-H // n)
    for i in range(n):
        for j in range(n):
            cx, cy = i * tw, j * th; w, h = min(tw, W - cx), min(th, H - cy)
            url = img.getDownloadURL({"crs": "EPSG:32736", "crs_transform": [R, 0, x0 + cx * R, 0, -R, y1 - cy * R],
                                      "dimensions": f"{w}x{h}", "format": "GEO_TIFF"})
            d = urllib.request.urlopen(url, timeout=900).read()
            with rasterio.open(io.BytesIO(d)) as r:
                a = r.read(1)
                if out is None: out = np.full((H, W), np.nan, "float32")
                out[cy:cy + h, cx:cx + w] = a
    prof = dict(driver="GTiff", width=W, height=H, count=1, dtype="float32", crs="EPSG:32736", compress="deflate",
                transform=rasterio.transform.from_origin(x0, y1, R, R))
    with rasterio.open(f"rast/{name}.tif", "w", **prof) as r: r.write(out, 1)
    print(name, "ok", flush=True)

dem = ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1").select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30)
proj = ee.Projection("EPSG:32736").atScale(R)
dl(dem.reduceResolution(ee.Reducer.mean(), maxPixels=64).reproject(proj).toFloat(), "dem")
wp = ee.ImageCollection("WorldPop/GP/100m/pop").filter(ee.Filter.eq("country", "ZWE")).filter(ee.Filter.eq("year", 2020)).first()
# population density per m2 resampled, then x cell area: conserves totals to within resampling error
dens = wp.divide(ee.Image.pixelArea())
dl(dens.reproject(proj).multiply(R * R).unmask(0).toFloat(), "wp2020")
# Constrained 2020 (people only in mapped settlement footprints); replaces the unconstrained layer above in prep.py
wpc = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").filter(ee.Filter.eq("country", "ZWE")).filter(ee.Filter.eq("year", 2020)).first().select("population")
dl(wpc.divide(ee.Image.pixelArea()).unmask(0).reduceResolution(ee.Reducer.mean(), maxPixels=64).reproject(proj).multiply(R * R).unmask(0).toFloat(), "wpc2020")
