# Chivi district, 30 m grid (EPSG:32736, 3 km pad). Earth Engine rasters in 2x2 tiles, OSM vectors, ward boundaries.
import json, urllib.request, time, sys, io
import numpy as np, geopandas as gpd, rasterio
from rasterio.transform import from_origin

d = gpd.read_file("../population/data/districts.gpkg")
b = d[d.district == "Chivi"][["district", "geometry"]].to_crs(32736)
import os
if not os.path.exists("data/chivi.gpkg"): b.to_file("data/chivi.gpkg")
R, PAD = 30, 3000
x0, y0, x1, y1 = b.total_bounds
x0, y0 = int((x0 - PAD) // R) * R, int((y0 - PAD) // R) * R
x1, y1 = int((x1 + PAD) // R + 1) * R, int((y1 + PAD) // R + 1) * R
W, H = (x1 - x0) // R, (y1 - y0) // R
json.dump({"bounds": [x0, y0, x1, y1], "res": R, "crs": "EPSG:32736"}, open("data/grid.json", "w"))
print("grid", W, H)
ll = b.to_crs(4326).total_bounds
PROF = dict(driver="GTiff", width=W, height=H, count=1, crs="EPSG:32736", transform=from_origin(x0, y1, R, R), compress="deflate")

def ee_part(only=None):
    import ee
    ee.Initialize(project="directed-sun-490915-m4")
    reg = ee.Geometry.Rectangle([x0, y0, x1, y1], "EPSG:32736", False)
    def dl(img, name, dt="float32", bands=1, n=2):
        out = np.zeros((bands, H, W), dt)
        cs = [W * i // n for i in range(n + 1)]; rs = [H * i // n for i in range(n + 1)]
        for c0, cw in [(cs[i], cs[i + 1] - cs[i]) for i in range(n)]:
            for r0, rh in [(rs[i], rs[i + 1] - rs[i]) for i in range(n)]:
                url = img.getDownloadURL({"crs": "EPSG:32736", "crs_transform": [R, 0, x0 + c0 * R, 0, -R, y1 - r0 * R],
                                          "dimensions": f"{cw}x{rh}", "format": "GEO_TIFF"})
                for a in range(3):
                    try: data = urllib.request.urlopen(url, timeout=900).read(); break
                    except Exception as e: print("retry", str(e)[:200], flush=True); time.sleep(10)
                with rasterio.open(io.BytesIO(data)) as s: out[:, r0:r0 + rh, c0:c0 + cw] = s.read()
                print(name, "tile", c0, r0, "ok", flush=True)
        with rasterio.open(f"rast/{name}.tif", "w", **dict(PROF, dtype=dt, count=bands)) as o: o.write(out)
        print(name, out.min(), out.max())
    J = {}
    J["dem"] = lambda: dl(ee.ImageCollection("COPERNICUS/DEM/GLO30").filterBounds(reg).select("DEM").mosaic()
                          .setDefaultProjection("EPSG:4326", None, 30).float(), "dem")
    J["lc"] = lambda: dl(ee.ImageCollection("ESA/WorldCover/v200").first().select("Map"), "lc", "uint8")
    def soil():
        for v in ["sand_content", "silt_content", "clay_content", "carbon_organic"]:
            dl(ee.Image(f"ISDASOIL/Africa/v1/{v}").select("mean_0_20").float(), v.split("_")[0] if v != "carbon_organic" else "oc_raw")
    J["soil"] = soil
    # mean annual rainfall 1991-2020 (a climate normal, used only as the R-factor input)
    J["rain"] = lambda: dl(ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD").filterDate("1991-01-01", "2021-01-01").sum()
                           .divide(30).resample("bilinear").float(), "rain")
    def s2():
        def m(i):
            q = i.select("SCL"); ok = q.neq(3).And(q.neq(8)).And(q.neq(9)).And(q.neq(10))
            return i.updateMask(ok)
        c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(reg).filterDate("2023-10-01", "2024-10-01") \
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)).map(m)
        md = c.median()
        dl(md.normalizedDifference(["B8", "B4"]).float(), "ndvi", n=4)
        dl(md.select(["B4", "B3", "B2"]).divide(3000).multiply(255).clamp(0, 255).uint8(), "rgb", "uint8", 3, n=4)
    J["s2"] = s2
    # rainy-season cover for C: NDVI per scene, median over December to March of five seasons (2019/20 to 2023/24)
    def wet():
        def m(i):
            q = i.select("SCL"); ok = q.neq(3).And(q.neq(8)).And(q.neq(9)).And(q.neq(10))
            return i.updateMask(ok).normalizedDifference(["B8", "B4"])
        c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(reg).filterDate("2019-12-01", "2024-04-01")               .filter(ee.Filter.calendarRange(12, 3, "month")).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30)).map(m)
        print("wet scenes", c.size().getInfo(), flush=True)
        dl(c.median().float(), "ndvi_wet", n=4)
    J["wet"] = wet
    for k in (only or J): J[k]()

Q = {"rivers": 'way["waterway"="river"]({b});out geom tags;',
     "streams": 'way["waterway"="stream"]({b});out geom;',
     "water": 'nwr["natural"="water"]({b});out geom;',
     "roads": 'way["highway"~"^(trunk|primary|secondary)$"]({b});out geom;',
     "places": 'node["place"~"^(town|village)$"]({b});out;'}

def osm_part(only=None):
    bb = f"{ll[1]-0.05},{ll[0]-0.05},{ll[3]+0.05},{ll[2]+0.05}"
    for n, q in Q.items():
        for a in range(3):
            try:
                req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                        data=("[out:json][timeout:240];" + q.format(b=bb)).encode(), headers={"User-Agent": "gis-case-study"})
                el = json.load(urllib.request.urlopen(req, timeout=300))["elements"]
                json.dump(el, open(f"data/osm_{n}.json", "w")); print(n, len(el)); break
            except Exception as e: print(n, "retry", e); time.sleep(20)

def wards_part(only=None):
    meta = json.load(urllib.request.urlopen("https://www.geoboundaries.org/api/current/gbOpen/ZWE/ADM3/"))
    print(meta.get("boundarySource"), meta.get("boundaryYearRepresented"))
    w = gpd.read_file(meta["gjDownloadURL"]).to_crs(32736)
    c = b.geometry.iloc[0]
    w = w[w.representative_point().within(c)]
    w.to_file("data/wards.gpkg"); json.dump({k: meta.get(k) for k in ("boundarySource", "boundaryYearRepresented", "boundaryLicense")}, open("data/wards_meta.json", "w"))
    print("wards", len(w), w.columns.tolist()[:6])

if __name__ == "__main__":
    a = sys.argv[1:] or ["ee", "osm", "wards"]
    globals()[a[0] + "_part"](a[1:] or None)
