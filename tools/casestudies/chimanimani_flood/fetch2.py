"""Exposure layers on the district grid: Google Open Buildings v3 count per 30 m cell (confidence >= 0.75, centroids)
and constrained WorldPop 2020 people per 30 m cell."""
import os, io, zipfile, urllib.request, ee
from concurrent.futures import ThreadPoolExecutor
ee.Initialize(project="directed-sun-490915-m4")
X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834
TW, TH = W // 2, H // 2
box = ee.Geometry.Rectangle([32.33, -20.13, 33.08, -19.35])
b = ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons").filterBounds(box) \
    .filter(ee.Filter.gte("confidence", 0.75)).map(lambda f: ee.Feature(f.geometry().centroid(1), {"n": 1}))
bld = b.reduceToImage(["n"], ee.Reducer.sum()).unmask(0).toFloat()
wp = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").filter(ee.Filter.eq("country", "ZWE")) \
    .filter(ee.Filter.eq("year", 2020)).first().select("population")
pop = wp.unmask(0).divide(ee.Image.pixelArea()).multiply(RES * RES).setDefaultProjection(wp.projection()).toFloat()
LAY = {"bld": bld, "pop": pop}


def job(a):
    name, i, j = a
    f = f"rast/{name}_{i}{j}.tif"
    if os.path.exists(f): return
    tr = [RES, 0, X0 + i * TW * RES, 0, -RES, Y0 - j * TH * RES]
    for k in range(4):
        try:
            u = LAY[name].getDownloadURL({"crs": "EPSG:32736", "crs_transform": tr, "dimensions": f"{TW}x{TH}",
                                          "format": "GEO_TIFF"})
            r = urllib.request.urlopen(u, timeout=600).read()
            if r[:2] == b"PK": r = zipfile.ZipFile(io.BytesIO(r)).read(zipfile.ZipFile(io.BytesIO(r)).namelist()[0])
            open(f + ".part", "wb").write(r); os.replace(f + ".part", f); print("ok", f, flush=True); return
        except Exception as e:
            err = e
    print("FAILED", f, err, flush=True)


with ThreadPoolExecutor(2) as ex: list(ex.map(job, [(n, i, j) for n in LAY for i in range(2) for j in range(2)]))
print("done")
