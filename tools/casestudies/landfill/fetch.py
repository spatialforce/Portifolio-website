# Bulawayo boundary, 30 m grid (EPSG:32735, 6 km pad), Earth Engine rasters and OSM vectors.
import json, urllib.request, time, sys
import geopandas as gpd

d = gpd.read_file("../population/data/districts.gpkg")
b = d[d.district == "Bulawayo"][["district", "geometry"]].to_crs(32735)
b.to_file("data/bulawayo.gpkg")
R, PAD = 30, 6000
x0, y0, x1, y1 = b.total_bounds
x0, y0 = int((x0 - PAD) // R) * R, int((y0 - PAD) // R) * R
x1, y1 = int((x1 + PAD) // R + 1) * R, int((y1 + PAD) // R + 1) * R
W, H = (x1 - x0) // R, (y1 - y0) // R
json.dump({"bounds": [x0, y0, x1, y1], "res": R, "crs": "EPSG:32735"}, open("data/grid.json", "w"))
print("grid", W, H)
ll = b.to_crs(4326).buffer(0).total_bounds

def ee_part():
    import ee
    ee.Initialize(project="directed-sun-490915-m4")
    reg = ee.Geometry.Rectangle([x0, y0, x1, y1], "EPSG:32735", False)
    def dl(img, name):
        url = img.getDownloadURL({"crs": "EPSG:32735", "crs_transform": [R, 0, x0, 0, -R, y1],
                                  "dimensions": f"{W}x{H}", "format": "GEO_TIFF"})
        data = urllib.request.urlopen(url, timeout=900).read(); open(f"rast/{name}.tif", "wb").write(data)
        print(name, len(data) // 1024, "KB")
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").filterBounds(reg).select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30)
    dl(dem.float(), "dem")
    dl(ee.ImageCollection("ESA/WorldCover/v200").first().select("Map"), "lc")
    dl(ee.Image("ISDASOIL/Africa/v1/clay_content").select("mean_0_20").float(), "clay")
    fc = ee.FeatureCollection("GOOGLE/Research/open-buildings/v3/polygons").filterBounds(reg).filter("confidence >= 0.75")
    print("buildings", fc.size().getInfo())
    bl = ee.Image(0).byte().paint(fc, 1).reproject("EPSG:32735", None, 10)
    dl(bl.reduceResolution(ee.Reducer.mean(), maxPixels=16).reproject("EPSG:32735", [R, 0, x0, 0, -R, y1]).float(), "bfrac")

Q = {"rivers": 'way["waterway"~"^(river|stream)$"]({b});out geom;',
     "water": 'nwr["natural"="water"]({b});out geom;',
     "wetland": 'nwr["natural"="wetland"]({b});out geom;',
     "roads": 'way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]({b});out geom;',
     "rail": 'way["railway"="rail"]({b});out geom;',
     "aero": 'nwr["aeroway"~"^(aerodrome|runway)$"]({b});out geom;',
     "landfill": 'nwr["landuse"="landfill"]({b});out geom tags;'}

def osm_part():
    bb = f"{ll[1]-0.07},{ll[0]-0.07},{ll[3]+0.07},{ll[2]+0.07}"
    for n, q in Q.items():
        for a in range(3):
            try:
                req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                        data=("[out:json][timeout:240];" + q.format(b=bb)).encode(), headers={"User-Agent": "gis-case-study"})
                el = json.load(urllib.request.urlopen(req, timeout=300))["elements"]
                json.dump(el, open(f"data/osm_{n}.json", "w")); print(n, len(el)); break
            except Exception as e:
                print(n, "retry", e); time.sleep(20)

if __name__ == "__main__":
    for p in sys.argv[1:] or ["ee", "osm"]: globals()[p + "_part"]()
