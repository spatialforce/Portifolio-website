# Build the 250 m criteria stack and constraint mask for the AHP overlay.
# Inputs: rast/*.tif from fetch_ee2.py, GHI from Global Solar Atlas zip,
# OSM vectors in data/. Outputs rast/ghi.tif, rast/d_grid.tif, rast/d_road.tif,
# rast/d_sett.tif, rast/mask.tif (1 = analysable), rast/prov.tif.
import json, zipfile, os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from scipy.ndimage import distance_transform_edt
from shapely.geometry import shape

GSA_ZIP = r"C:\Users\user\AppData\Local\Temp\claude\0c15e2d236ef5d5b\7fd6ca56-b6ac-4fbc-a9a3-e199ecbb2edb\scratchpad\dl\gsa.zip"

g = json.load(open("data/grid.json"))
minx, miny, maxx, maxy = g["bounds"]
W, H = (maxx - minx) // 250, (maxy - miny) // 250
TR = from_origin(minx, maxy, 250, 250)
PROF = dict(driver="GTiff", height=H, width=W, count=1, crs="EPSG:32735",
            transform=TR, compress="deflate")

def save(name, arr, dtype, nodata=None):
    p = dict(PROF, dtype=dtype)
    if nodata is not None:
        p["nodata"] = nodata
    with rasterio.open(f"rast/{name}.tif", "w", **p) as d:
        d.write(arr.astype(dtype), 1)
    print(name, "saved")

# ---- province mask -------------------------------------------------------
prov = gpd.read_file("data/province.gpkg").to_crs(32735)
prov_r = rasterize([(geom, 1) for geom in prov.geometry], out_shape=(H, W),
                   transform=TR, fill=0, dtype="uint8")
save("prov", prov_r, "uint8")

# ---- GHI: extract from GSA zip, warp to grid (bilinear) ------------------
if not os.path.exists("rast/ghi.tif"):
    zf = zipfile.ZipFile(GSA_ZIP)
    ghi_name = [n for n in zf.namelist() if n.upper().endswith(".TIF")
                and "GHI" in n.upper()][0]
    print("GHI source:", ghi_name)
    tmp = "rast/_ghi_src.tif"
    open(tmp, "wb").write(zf.read(ghi_name))
    dst = np.full((H, W), np.nan, dtype="float32")
    with rasterio.open(tmp) as src:
        reproject(rasterio.band(src, 1), dst, dst_transform=TR,
                  dst_crs="EPSG:32735", src_transform=src.transform,
                  src_crs=src.crs, resampling=Resampling.bilinear,
                  dst_nodata=np.nan)
    os.remove(tmp)
    save("ghi", dst, "float32", nodata=-9999)
    v = dst[prov_r == 1]
    print("GHI range in province:", np.nanmin(v), np.nanmax(v), np.nanmean(v))

# ---- distance rasters from OSM vectors -----------------------------------
def dist_from(geoms, name):
    src = rasterize([(s, 1) for s in geoms], out_shape=(H, W), transform=TR,
                    fill=0, dtype="uint8")
    d = distance_transform_edt(src == 0) * 250.0 / 1000.0  # km
    save(name, d, "float32")
    return d

def load_lines(path, keep=None):
    gj = json.load(open(path))
    out = []
    for f in gj["features"]:
        if keep and not keep(f["properties"]):
            continue
        out.append(shape(f["geometry"]))
    s = gpd.GeoSeries(out, crs=4326).to_crs(32735)
    return list(s.geometry)

# transmission lines (power=line, 66-400 kV)
dist_from(load_lines("data/power_lines.geojson"), "d_grid")
# major roads
dist_from(load_lines("data/roads.geojson"), "d_road")

# settlements: GHS-SMOD urban centres/dense clusters (>= 21)
with rasterio.open("rast/smod.tif") as s:
    smod = s.read(1)
sett = (smod >= 21).astype("uint8")
d = distance_transform_edt(sett == 0) * 250.0 / 1000.0
save("d_sett", d, "float32")

# ---- constraint mask ------------------------------------------------------
with rasterio.open("rast/slope.tif") as s:
    slope = s.read(1)
with rasterio.open("rast/worldcover.tif") as s:
    wc = s.read(1)
with rasterio.open("rast/water.tif") as s:
    water = s.read(1)
# dominant built-up cells (WorldCover mode); the max-reducer builtup.tif flags
# any cell containing a single 10 m built pixel and would exclude a third of
# the province through scattered homesteads
built = (wc == 50).astype("uint8")

# protected areas (+500 m)
pa = gpd.read_file("data/wdpa.geojson").set_crs(4326).to_crs(32735)
pa_r = rasterize([(geom.buffer(500), 1) for geom in pa.geometry],
                 out_shape=(H, W), transform=TR, fill=0, dtype="uint8")
save("protected", pa_r, "uint8")

# built-up + 500 m buffer (2 cells)
db = distance_transform_edt(built == 0) * 250.0
built_buf = (db <= 500).astype("uint8")

excl = ((slope > 5) | (water == 1) | (wc == 80) | (wc == 90) | (wc == 95) |
        (wc == 50) | (built_buf == 1) | (pa_r == 1))
mask = ((prov_r == 1) & ~excl).astype("uint8")
save("mask", mask, "uint8")

tot = (prov_r == 1).sum()
print(f"province cells {tot}, analysable {mask.sum()} ({100*mask.sum()/tot:.1f}%)")
for lbl, m in [("slope>5", slope > 5), ("water", (water == 1) | (wc == 80)),
               ("wetland", (wc == 90) | (wc == 95)), ("built+500m", built_buf == 1),
               ("protected+500m", pa_r == 1)]:
    print(f"  excluded by {lbl}: {100*((m)&(prov_r==1)).sum()/tot:.2f}%")
