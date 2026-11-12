# Line-of-sight coverage per estimated site (GDAL viewshed, observer 30 m mast, 1.5 m handset, curvature with 4/3-earth radio refraction (coefficient 0.75)).
# One viewshed per site to 20 km, then cut to each assumed range. Distance-only buffers kept for comparison.
import json, numpy as np, geopandas as gpd, rasterio
from osgeo import gdal
g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]; R = g["res"]; W, H = (x1 - x0) // R, (y1 - y0) // R
dem = rasterio.open("rast/dem.tif").read(1).astype("float32")
s = gpd.read_file("data/sites.gpkg")
RANGES = {"gsm": [10, 15, 20], "umts": [5, 10, 15]}
los = {f"{t}{r}": np.zeros((H, W), "uint8") for t, rs in RANGES.items() for r in rs}
buf = {k: np.zeros((H, W), "uint8") for k in los}
P = int(20000 / R) + 1; drv = gdal.GetDriverByName("MEM")
for i, st in s.iterrows():
    c, r = int((st.x - x0) // R), int((y1 - st.y) // R)
    ra, rb, ca, cb = max(r - P, 0), min(r + P + 1, H), max(c - P, 0), min(c + P + 1, W)
    win = dem[ra:rb, ca:cb]
    ds = drv.Create("", win.shape[1], win.shape[0], 1, gdal.GDT_Float32)
    ds.SetGeoTransform((x0 + ca * R, R, 0, y1 - ra * R, 0, -R)); ds.GetRasterBand(1).WriteRaster(0, 0, win.shape[1], win.shape[0], np.ascontiguousarray(win).tobytes())
    v = gdal.ViewshedGenerate(ds.GetRasterBand(1), "MEM", "", None, float(st.x), float(st.y), 30.0, 1.5,
                              1, 0, 0, -1, 0.75, gdal.GVM_Edge, 20000.0)
    b = v.GetRasterBand(1); vis = np.frombuffer(b.ReadRaster(0, 0, v.RasterXSize, v.RasterYSize, buf_type=gdal.GDT_Byte), 'uint8').reshape(v.RasterYSize, v.RasterXSize) == 1
    yy, xx = np.mgrid[ra:rb, ca:cb]
    d = np.hypot((xx + 0.5) * R + x0 - st.x, y1 - (yy + 0.5) * R - st.y) / 1000
    for t, rs in RANGES.items():
        if not st[t]: continue
        for rr in rs:
            inr = d <= rr
            los[f"{t}{rr}"][ra:rb, ca:cb] += (vis & inr).astype("uint8")
            buf[f"{t}{rr}"][ra:rb, ca:cb] += inr.astype("uint8")
    if i % 200 == 0: print(i, flush=True)
prof = dict(driver="GTiff", width=W, height=H, count=1, crs="EPSG:32736", dtype="uint8",
            transform=rasterio.transform.from_origin(x0, y1, R, R), compress="deflate")
for k in los:
    with rasterio.open(f"rast/los_{k}.tif", "w", **prof) as o: o.write(np.minimum(los[k], 255), 1)
    with rasterio.open(f"rast/buf_{k}.tif", "w", **prof) as o: o.write(np.minimum(buf[k], 255), 1)
print("done")
