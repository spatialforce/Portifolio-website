"""GLO-30 DEM -> 30 m UTM 36S terrain and hydrology factors (pysheds), cropped to the district grid.
Hydrology runs on a 15 km buffer so streams entering the district carry upstream area."""
import glob, numpy as np, rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from scipy import ndimage as nd
np.in1d = np.isin   # pysheds 0.5 still calls the removed numpy alias
from pysheds.grid import Grid

RES = 30
XB, YB, WB, HB = 415000, 7875000, 3600, 3834      # buffered grid
X0, Y0, W, H = 430000, 7860000, 2600, 2834        # district grid (same as fetch.py)
c0, r0 = (X0 - XB) // RES, (YB - Y0) // RES
tb = from_origin(XB, YB, RES, RES)
src = [rasterio.open(f) for f in sorted(glob.glob("data/dem/*.tif"))]
mos, mt = merge(src)
dem = np.zeros((HB, WB), np.float32)
reproject(mos[0], dem, src_transform=mt, src_crs="EPSG:4326", dst_transform=tb, dst_crs="EPSG:32736",
          resampling=Resampling.bilinear)
prof = dict(driver="GTiff", height=HB, width=WB, count=1, dtype="float32", crs="EPSG:32736", transform=tb, nodata=-9999)
with rasterio.open("rast/dem_buf.tif", "w", **prof) as d: d.write(dem, 1)

g = Grid.from_raster("rast/dem_buf.tif"); r = g.read_raster("rast/dem_buf.tif")
f = g.resolve_flats(g.fill_depressions(g.fill_pits(r)))
fdir = g.flowdir(f)
acc = g.accumulation(fdir)
streams = acc > 1111                                 # >= 1 km2 upstream area
hand = g.compute_hand(fdir, f, streams)
acc, hand, streams = np.asarray(acc, np.float32), np.asarray(hand, np.float32), np.asarray(streams)

gy, gx = np.gradient(dem.astype(np.float64), RES)
slope = np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)
twi = np.log((acc + 1) * RES / np.maximum(np.tan(np.radians(slope)), 0.001)).astype(np.float32)
dist = (nd.distance_transform_edt(~streams) * RES).astype(np.float32)
big = acc > 111111                                   # >= 100 km2: main rivers
dbig = (nd.distance_transform_edt(~big) * RES).astype(np.float32)
lap = nd.laplace(nd.gaussian_filter(dem.astype(np.float64), 1)) / RES ** 2
curv = (-lap * 100).astype(np.float32)               # + convex, - concave (1/100 m)
tpi = (dem - nd.uniform_filter(dem, 33)).astype(np.float32)   # relative to a ~1 km window
upa = (acc + 1) * RES * RES / 1e6                    # km2

out = {"elev": dem, "slope": slope, "hand": hand, "twi": twi, "dstream": dist, "driver": dbig, "curv": curv,
       "tpi": tpi, "upa": upa.astype(np.float32), "streams": streams.astype(np.float32)}
t0 = from_origin(X0, Y0, RES, RES)
p0 = dict(prof, height=H, width=W, transform=t0)
for k, v in out.items():
    with rasterio.open(f"rast/t_{k}.tif", "w", **p0) as d: d.write(v[r0:r0 + H, c0:c0 + W], 1)
print("terrain ok", {k: (float(np.nanmin(v)), float(np.nanmax(v))) for k, v in out.items() if k != "streams"})
