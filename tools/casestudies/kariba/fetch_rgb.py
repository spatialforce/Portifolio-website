"""Landsat 8 and 9 true-colour median of the 2024 low season (October to December), 30 m, UTM 35S,
for the three shore windows with the most lake bed exposed between the 2000 high and the 2024 low."""
import ee, urllib.request, os
ee.Initialize(project="directed-sun-490915-m4")
CRS = "EPSG:32735"
SITES = {"a": (707940, 8157120), "b": (608280, 8118720), "c": (546720, 8071200)}
HW, HH = 14000, 9000     # half width and half height (28 x 18 km windows)


def prep(i):
    ok = i.select("QA_PIXEL").bitwiseAnd(0b11111).eq(0)
    return i.select(["SR_B4", "SR_B3", "SR_B2"]).multiply(0.0000275).add(-0.2).updateMask(ok)


col = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")) \
    .filterBounds(ee.Geometry.Rectangle([26.5, -18.3, 29.1, -16.3])).filterDate("2024-10-01", "2025-01-01").map(prep)
img = col.median().visualize(min=0.0, max=0.24, gamma=1.15)
for k, (x, y) in SITES.items():
    f = f"rast/rgb_{k}.tif"
    if os.path.exists(f): continue
    reg = ee.Geometry.Rectangle([x - HW, y - HH, x + HW, y + HH], ee.Projection(CRS), False)
    u = img.getDownloadURL({"region": reg, "scale": 30, "crs": CRS, "format": "GEO_TIFF"})
    urllib.request.urlretrieve(u, f); print("saved", f, flush=True)
