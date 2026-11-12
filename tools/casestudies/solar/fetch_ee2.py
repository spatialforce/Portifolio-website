# Tiled EE exports (full-grid requests hit "Reprojection output too large").
# Downloads each raster in 500x500-cell tiles and mosaics locally.
import json, urllib.request, os
import numpy as np
import ee, rasterio
from rasterio.transform import from_origin

ee.Initialize(project="directed-sun-490915-m4")

g = json.load(open("data/grid.json"))
minx, miny, maxx, maxy = g["bounds"]
W, H = (maxx - minx) // 250, (maxy - miny) // 250
TILE = 500

def dl(img, name, dtype, nodata=None, tile=TILE):
    if os.path.exists(f"rast/{name}.tif"):
        print(name, "exists"); return
    full = np.zeros((H, W), dtype=dtype)
    for r0 in range(0, H, tile):
        for c0 in range(0, W, tile):
            w, h = min(tile, W - c0), min(tile, H - r0)
            ox, oy = minx + c0 * 250, maxy - r0 * 250
            url = img.getDownloadURL({"crs": "EPSG:32735",
                                      "crs_transform": [250, 0, ox, 0, -250, oy],
                                      "dimensions": f"{w}x{h}", "format": "GEO_TIFF"})
            with urllib.request.urlopen(url, timeout=600) as resp:
                data = resp.read()
            tmp = f"rast/_t.tif"
            open(tmp, "wb").write(data)
            with rasterio.open(tmp) as src:
                full[r0:r0+h, c0:c0+w] = src.read(1)
    os.remove("rast/_t.tif")
    tr = from_origin(minx, maxy, 250, 250)
    prof = dict(driver="GTiff", height=H, width=W, count=1, dtype=dtype,
                crs="EPSG:32735", transform=tr, compress="deflate")
    if nodata is not None:
        prof["nodata"] = nodata
    with rasterio.open(f"rast/{name}.tif", "w", **prof) as dst:
        dst.write(full, 1)
    print(name, "done")

dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic() \
    .setDefaultProjection("EPSG:4326", None, 30)
dl(ee.Terrain.slope(dem).reduceResolution(ee.Reducer.mean(), maxPixels=1024).toFloat(),
   "slope", "float32")
dl(dem.reduceResolution(ee.Reducer.mean(), maxPixels=1024).toFloat(),
   "elev", "float32")
wc = ee.ImageCollection("ESA/WorldCover/v200").first()
dl(wc.reduceResolution(ee.Reducer.mode(), maxPixels=1024).toByte(), "worldcover", "uint8",
   tile=250)
dl(wc.eq(50).reduceResolution(ee.Reducer.max(), maxPixels=1024).toByte(), "builtup", "uint8",
   tile=250)
dl(ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence").gt(50)
   .unmask(0).reduceResolution(ee.Reducer.max(), maxPixels=1024).toByte(), "water", "uint8")
dl(ee.Image("JRC/GHSL/P2023A/GHS_SMOD_V2-0/2020").select("smod_code").toByte(),
   "smod", "uint8")

if not os.path.exists("data/wdpa.geojson"):
    import geopandas as gpd
    wgs = gpd.read_file("data/province.gpkg").to_crs(4326)
    w, s, e, n = wgs.total_bounds
    bbox = ee.Geometry.Rectangle([w - 0.15, s - 0.15, e + 0.15, n + 0.15])
    pa = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(bbox).select(["NAME", "DESIG_ENG", "IUCN_CAT", "GIS_AREA"])
    gj = pa.getInfo()
    json.dump(gj, open("data/wdpa.geojson", "w"))
    print("wdpa", len(gj["features"]))
