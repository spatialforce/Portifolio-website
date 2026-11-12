# Export analysis rasters for Matabeleland South at 250 m (EPSG:32735) from
# Earth Engine: slope (Copernicus GLO-30), ESA WorldCover 2021, JRC surface
# water, GHS-SMOD settlement classes, and WDPA protected areas as GeoJSON.
import json, urllib.request, zipfile, io, os
import ee
import geopandas as gpd

ee.Initialize(project="directed-sun-490915-m4")

prov = gpd.read_file("data/province.gpkg").to_crs(32735)
minx, miny, maxx, maxy = prov.total_bounds
PAD = 15000
minx, miny = (int((minx - PAD) // 250) * 250, int((miny - PAD) // 250) * 250)
maxx, maxy = (int((maxx + PAD) // 250 + 1) * 250, int((maxy + PAD) // 250 + 1) * 250)
print("grid", minx, miny, maxx, maxy, (maxx - minx) // 250, (maxy - miny) // 250)
json.dump({"bounds": [minx, miny, maxx, maxy], "res": 250, "crs": "EPSG:32735"},
          open("data/grid.json", "w"))

W, H = (maxx - minx) // 250, (maxy - miny) // 250

def dl(img, name, scale=250):
    url = img.getDownloadURL({"crs": "EPSG:32735",
                              "crs_transform": [250, 0, minx, 0, -250, maxy],
                              "dimensions": f"{W}x{H}", "format": "GEO_TIFF"})
    with urllib.request.urlopen(url, timeout=600) as r:
        data = r.read()
    open(f"rast/{name}.tif", "wb").write(data)
    print(name, len(data) // 1024, "KB")

# Slope from GLO-30, mean-aggregated to 250 m
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic() \
    .setDefaultProjection("EPSG:4326", None, 30)
slope = ee.Terrain.slope(dem).reduceResolution(ee.Reducer.mean(), maxPixels=1024) \
    .toFloat()
dl(slope, "slope")

# Elevation itself (for the study area map hillshade)
elev = dem.reduceResolution(ee.Reducer.mean(), maxPixels=1024) \
    .toFloat()
dl(elev, "elev")

# ESA WorldCover 2021, mode at 250 m
wc = ee.ImageCollection("ESA/WorldCover/v200").first() \
    .reduceResolution(ee.Reducer.mode(), maxPixels=1024) \
    .toByte()
dl(wc, "worldcover")

# Built-up presence at 250 m (any 10 m built pixel)
built = ee.ImageCollection("ESA/WorldCover/v200").first().eq(50) \
    .reduceResolution(ee.Reducer.max(), maxPixels=1024) \
    .toByte()
dl(built, "builtup")

# JRC permanent/seasonal water (occurrence > 50 %)
water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").gt(50) \
    .unmask(0).reduceResolution(ee.Reducer.max(), maxPixels=1024) \
    .toByte()
dl(water, "water")

# GHS-SMOD 2020 settlement model (towns and cities >= 21)
smod = ee.Image("JRC/GHSL/P2023A/GHS_SMOD_V2-0/2020").select("smod_code") \
    .toByte()
dl(smod, "smod")

# WDPA protected areas intersecting the region -> GeoJSON
wgs = gpd.read_file("data/province.gpkg").to_crs(4326)
w, s, e, n = wgs.total_bounds
bbox = ee.Geometry.Rectangle([w - 0.15, s - 0.15, e + 0.15, n + 0.15])
pa = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
    .filterBounds(bbox).select(["NAME", "DESIG_ENG", "IUCN_CAT", "GIS_AREA"])
gj = pa.getInfo()
json.dump(gj, open("data/wdpa.geojson", "w"))
print("wdpa", len(gj["features"]))
