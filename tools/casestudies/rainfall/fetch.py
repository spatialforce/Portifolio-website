"""CHIRPS rainy-season totals (Oct-Apr) for Zimbabwe from Earth Engine, 0.05 degree."""
import ee, requests, os
ee.Initialize(project="directed-sun-490915-m4")
box = ee.Geometry.Rectangle([25.0, -22.6, 33.2, -15.4])
ch = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD").select("precipitation")
T = [0.05, 0, 25.0, 0, -0.05, -15.4]
def get(img, out):
    if os.path.exists(out): return
    url = img.reproject(crs="EPSG:4326", crsTransform=T).getDownloadURL({"region": box, "crs": "EPSG:4326", "crsTransform": T, "dimensions": "164x144", "format": "GEO_TIFF"})
    r = requests.get(url, timeout=600); assert r.status_code == 200, r.text[:300]
    open(out, "wb").write(r.content); print(out, len(r.content))
# seasons 1991/92 .. 2024/25, band i = season starting October of 1991+i
seasons = ee.ImageCollection([ch.filterDate(f"{y}-10-01", f"{y+1}-05-01").sum().rename(f"s{y}") for y in range(1991, 2025)])
get(seasons.toBands().toFloat(), "rast/seasons.tif")
# monthly mean 1991-2020, Jan..Dec
mon = ee.ImageCollection([ch.filterDate("1991-01-01", "2021-01-01").filter(ee.Filter.calendarRange(m, m, "month")).sum().divide(30).rename(f"m{m}") for m in range(1, 13)])
get(mon.toBands().toFloat(), "rast/monthly_clim.tif")
