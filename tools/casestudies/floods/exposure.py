"""Exposure layers for both study areas, on the same 30 m EPSG:32736 grid as the flood rasters where possible.
  data/pop_<aoi>.tif     GHS-POP R2023A 2025 epoch, people per 100 m cell (EPSG:32736, 100 m)
  data/lc_<aoi>.tif      ESA WorldCover 2021 class, 30 m (mode)
  data/bld_<aoi>.csv     Google Open Buildings v3 centroids, confidence >= 0.70
  data/dem_<aoi>.tif     Copernicus GLO-30 elevation, 30 m
Run: python -I exposure.py
"""
import os, json, urllib.request, ee, geopandas as gpd
ee.Initialize()
A = gpd.read_file("data/aoi.gpkg").set_index("aoi")
def geom(k): return ee.Geometry(json.loads(gpd.GeoSeries([A.geometry[k].simplify(0.002)]).to_json())["features"][0]["geometry"])
def get(img, name, g, scale):
    if os.path.exists(name): return
    urllib.request.urlretrieve(img.clip(g).getDownloadURL(dict(region=g.bounds(), scale=scale, crs="EPSG:32736", format="GEO_TIFF")), name); print(name, flush=True)
for k in ["muz", "save"]:
    g = geom(k)
    get(ee.Image("JRC/GHSL/P2023A/GHS_POP/2025").select(0).unmask(0).toFloat(), f"data/pop_{k}.tif", g, 100)
    get(ee.ImageCollection("ESA/WorldCover/v200").first().toByte(), f"data/lc_{k}.tif", g, 30)
    get(ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").filterBounds(g).mosaic().toInt16(), f"data/dem_{k}.tif", g, 30)
    name = f"data/bld_{k}.csv"
    if not os.path.exists(name):
        b = (ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons").filterBounds(g).filter(ee.Filter.gte("confidence", 0.70))
             .map(lambda f: ee.Feature(None, dict(lon=f.geometry().centroid(1).coordinates().get(0), lat=f.geometry().centroid(1).coordinates().get(1), m2=f.get("area_in_meters")))))
        urllib.request.urlretrieve(b.getDownloadURL("CSV", ["lon", "lat", "m2"]), name); print(name, flush=True)
