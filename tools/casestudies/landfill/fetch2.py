# Sentinel-2 dry-season true colour (May to September 2024, 20 m) and HOT basemap tiles for the map frame.
import json, urllib.request, numpy as np
g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]; R = 20
def s2():
    import ee; ee.Initialize(project="directed-sun-490915-m4")
    reg = ee.Geometry.Rectangle([x0, y0, x1, y1], "EPSG:32735", False)
    def cm(i):
        s = i.select("SCL"); return i.updateMask(s.neq(3).And(s.neq(8)).And(s.neq(9)).And(s.neq(10)))
    c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(reg).filterDate("2024-05-01", "2024-09-30") \
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)).map(cm)
    print("scenes", c.size().getInfo())
    img = c.median().select(["B4", "B3", "B2"]).visualize(min=0, max=2500)
    url = img.getDownloadURL({"crs": "EPSG:32735", "crs_transform": [R, 0, x0, 0, -R, y1],
                              "dimensions": f"{(x1-x0)//R}x{(y1-y0)//R}", "format": "GEO_TIFF"})
    d = urllib.request.urlopen(url, timeout=900).read(); open("rast/s2.tif", "wb").write(d); print("s2", len(d) // 1024, "KB")
def tiles():
    import contextily as ctx
    img, ext = ctx.bounds2img(28.25, -20.42, 28.85, -19.88, zoom=12, source=ctx.providers.OpenStreetMap.HOT, ll=True)
    img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:32735"); np.savez_compressed("rast/basemap_hot.npz", img=img, ext=np.array(ext)); print("tiles", img.shape)
import sys
for p in sys.argv[1:] or ["s2", "tiles"]: globals()[p]()
