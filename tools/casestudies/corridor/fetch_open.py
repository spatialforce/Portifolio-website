"""Rasters for the Hwange-Chizarira corridor study on one 100 m grid in UTM zone 35S (EPSG:32735).
ESA WorldCover 2021 v200 (AWS open data, 40 m overview, mode to 100 m), Copernicus GLO-30 DEM (AWS open data,
about 60 m overview; slope computed at that resolution, then mean to 100 m) and constrained WorldPop 2020 (people per cell)."""
import sys, json, numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
EXT = (25.95, 29.15, -19.05, -17.35); R = 100
t = Transformer.from_crs(4326, 32735, always_xy=True)
xs, ys = zip(*[t.transform(x, y) for x in (EXT[0], EXT[1]) for y in (EXT[2], EXT[3])])
X0, X1 = (min(xs) // R) * R - 2000, (max(xs) // R + 1) * R + 2000
Y0, Y1 = (min(ys) // R) * R - 2000, (max(ys) // R + 1) * R + 2000
W, H = int((X1 - X0) / R), int((Y1 - Y0) / R); TR = from_origin(X0, Y1, R, R)
json.dump({"x0": X0, "y1": Y1, "res": R, "w": W, "h": H}, open("raw/grid.json", "w")); print("grid", W, H)
PROF = dict(driver="GTiff", width=W, height=H, count=1, crs="EPSG:32735", transform=TR, compress="deflate")


def warp(srcs, name, rs, dtype, ovr=None, nodata=None, fn=None):
    out = np.zeros((H, W), "float32") if dtype != "uint8" else np.zeros((H, W), "uint8")
    for u in srcs:
        kw = {"OVERVIEW_LEVEL": ovr} if ovr is not None else {}
        with rasterio.open(u, **kw) as s:
            a = s.read(1); a = fn(a, s) if fn else a
            tmp = np.zeros_like(out)
            reproject(a.astype(out.dtype), tmp, src_transform=s.transform, src_crs=s.crs, dst_transform=TR, dst_crs="EPSG:32735",
                      resampling=rs, src_nodata=nodata, dst_nodata=0)
            out = np.where(tmp != 0, tmp, out)
        print(" read", u.split("/")[-1])
    with rasterio.open(f"raw/{name}.tif", "w", **PROF, dtype=out.dtype) as o: o.write(out, 1)
    print("saved", name)


def slope(z, s):
    dy = abs(s.transform.e) * 111320; lat = s.transform.f + np.arange(z.shape[0])[:, None] * s.transform.e
    dx = s.transform.a * 111320 * np.cos(np.radians(lat))
    gy, gx = np.gradient(z.astype("float64")); return np.degrees(np.arctan(np.hypot(gx / dx, gy / dy))).astype("float32") + 1e-3


want = sys.argv[1:] or ["lc", "dem", "slope", "pop"]
WC = [f"/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{t}_Map.tif"
      for t in ("S21E024", "S21E027", "S18E024", "S18E027")]
DEM = [f"/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_S{la:02d}_00_E{lo:03d}_00_DEM/Copernicus_DSM_COG_10_S{la:02d}_00_E{lo:03d}_00_DEM.tif"
       for la in (20, 19, 18) for lo in (25, 26, 27, 28, 29)]
if "lc" in want: warp(WC, "lc", Resampling.mode, "uint8", ovr=1)
if "dem" in want: warp(DEM, "dem", Resampling.average, "float32", ovr=0)
if "slope" in want: warp(DEM, "slope", Resampling.average, "float32", ovr=0, fn=slope)
if "pop" in want:  # people per 100 m cell; WorldPop cells are 3 arc-seconds, so warp density then multiply by cell area
    with rasterio.open("../population/raw/worldpop/pop.tif") as s:
        a = s.read(1).astype("float32"); a[a < 0] = 0
        lat = s.transform.f + (np.arange(a.shape[0])[:, None] + 0.5) * s.transform.e
        area = (s.transform.a * 111320 * np.cos(np.radians(lat))) * (abs(s.transform.e) * 110574)
        d = a / area; out = np.zeros((H, W), "float32")
        reproject(d, out, src_transform=s.transform, src_crs=s.crs, dst_transform=TR, dst_crs="EPSG:32735", resampling=Resampling.average)
    out *= R * R
    with rasterio.open("raw/pop.tif", "w", **PROF, dtype="float32") as o: o.write(out, 1)
    print("saved pop", round(float(out.sum())))
