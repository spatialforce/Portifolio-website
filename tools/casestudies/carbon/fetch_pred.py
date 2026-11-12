# Predictor stack and comparison layers on a 100 m grid (EPSG:32735) over Hwange NP + 5 km.
# Sentinel-2 SR (Cloud Score+ >= 0.6) dry season Jun-Oct and wet season Dec-Mar medians 2020-2023,
# Sentinel-1 GRD IW dry season median, Copernicus GLO-30 elevation and slope.
# Comparison only (not predictors): ESA CCI Biomass v5 2020, GEDI L4B v2.1 1 km, ESA WorldCover 2021.
import sys, os, json, urllib.request, ee
import geopandas as gpd
ee.Initialize(project="directed-sun-490915-m4")
park = gpd.read_file("data/wdpa_hwange.geojson").to_crs(32735)
R = 100; PAD = 5000
x0, y0, x1, y1 = park.total_bounds
x0, y0 = int((x0 - PAD) // R) * R, int((y0 - PAD) // R) * R
x1, y1 = int((x1 + PAD) // R + 1) * R, int((y1 + PAD) // R + 1) * R
W, H = (x1 - x0) // R, (y1 - y0) // R
json.dump({"bounds": [x0, y0, x1, y1], "res": R, "crs": "EPSG:32735"}, open("data/grid.json", "w"))
print("grid", W, H)
reg = ee.Geometry.Rectangle([x0, y0, x1, y1], "EPSG:32735", False)

def dl(img, name, n=4):
    """Download in n x n tiles (restricted-mode memory limit), stitch into rast/<name>.tif."""
    import io, numpy as np, rasterio
    if os.path.exists(f"rast/{name}.tif"): return
    out = None; tw, th = -(-W // n), -(-H // n)
    for i in range(n):
        for j in range(n):
            cx, cy = i * tw, j * th; w, h = min(tw, W - cx), min(th, H - cy)
            url = img.getDownloadURL({"crs": "EPSG:32735", "crs_transform": [R, 0, x0 + cx * R, 0, -R, y1 - cy * R],
                                      "dimensions": f"{w}x{h}", "format": "GEO_TIFF"})
            for k in range(3):
                try: d = urllib.request.urlopen(url, timeout=900).read(); break
                except urllib.error.HTTPError as e: print(name, i, j, e.read()[:200]); d = None
            if d is None: return
            with rasterio.open(io.BytesIO(d)) as r:
                a = r.read(1)
                if out is None: out = np.full((H, W), np.nan if a.dtype.kind == "f" else 0, a.dtype)
                out[cy:cy + h, cx:cx + w] = a
    prof = dict(driver="GTiff", width=W, height=H, count=1, dtype=out.dtype, crs="EPSG:32735", compress="deflate",
                transform=rasterio.transform.from_origin(x0, y1, R, R))
    with rasterio.open(f"rast/{name}.tif", "w", **prof) as r: r.write(out, 1)
    print(name, "ok", flush=True)

cs = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
def s2(months_filter):
    c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(reg).filterDate("2020-01-01", "2024-01-01") \
        .filter(months_filter).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)) \
        .map(lambda i: i.updateMask(i.select("SCL").remap([3, 8, 9, 10], [0, 0, 0, 0], 1).eq(1)).select(["B2", "B3", "B4", "B5", "B8", "B11", "B12"]).divide(10000))
    m = c.median()
    return m.addBands(m.normalizedDifference(["B8", "B4"]).rename("NDVI"))
dry = s2(ee.Filter.calendarRange(6, 10, "month"))
wet = s2(ee.Filter.Or(ee.Filter.calendarRange(12, 12, "month"), ee.Filter.calendarRange(1, 3, "month")))
s1 = ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(reg).filterDate("2020-01-01", "2024-01-01") \
    .filter(ee.Filter.calendarRange(6, 10, "month")).filter(ee.Filter.eq("instrumentMode", "IW")) \
    .select(["VV", "VH"]).median()
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30_2024_1").select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30)

L = {f"dry_{b}": dry.select(b) for b in ["B2", "B3", "B4", "B5", "B8", "B11", "B12", "NDVI"]}
L.update({f"wet_{b}": wet.select(b) for b in ["B4", "B8", "B11", "NDVI"]})
L.update({"s1_VV": s1.select("VV"), "s1_VH": s1.select("VH"),
          "elev": dem, "slope": ee.Terrain.slope(dem)})
L["cci_agb"] = ee.ImageCollection("projects/sat-io/open-datasets/ESA/ESA_CCI_AGB").filterDate("2020-01-01", "2021-01-01").first().select(0)
L["l4b_mu"] = ee.Image("LARSE/GEDI/GEDI04_B_002").select("MU")
L["worldcover"] = ee.ImageCollection("ESA/WorldCover/v200").first().select("Map")
for n in (sys.argv[1:] or L):
    dl(L[n].toFloat() if n != "worldcover" else L[n].toByte(), n)
