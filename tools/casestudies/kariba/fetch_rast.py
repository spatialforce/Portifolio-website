"""Rasters and boundaries for the Kariba maps (GEE).
- JRC Global Surface Water 1.4 occurrence (1984 to 2021) and maximum extent, 60 m, UTM 35S
- Copernicus GLO-30 DEM, 150 m, for hillshade round the lake
- LSIB 2017 country outlines (Zambia, Zimbabwe and neighbours) as GeoJSON
"""
import ee, urllib.request, os, json
ee.Initialize(project="directed-sun-490915-m4")
os.makedirs("rast", exist_ok=True)
CRS = "EPSG:32735"
BB = [26.5, -18.3, 29.1, -16.3]
GSW = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
occ = GSW.select("occurrence").unmask(0).where(GSW.select("max_extent").unmask(0).eq(0), 255).toUint8()   # 255 = never water
dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").filterBounds(ee.Geometry.Rectangle(BB)).mosaic().toInt16()


def get(img, name, scale, bb):
    f = f"rast/{name}.tif"
    if os.path.exists(f): return
    u = img.getDownloadURL({"region": ee.Geometry.Rectangle(bb), "scale": scale, "crs": CRS, "format": "GEO_TIFF"})
    urllib.request.urlretrieve(u, f + ".part"); os.replace(f + ".part", f); print("saved", f, flush=True)


# occurrence in four tiles (download size limit)
xs = [26.5, 27.15, 27.8, 28.45, 29.1]
for i in range(4): get(occ, f"occ_{i}", 60, [xs[i], BB[1], xs[i + 1], BB[3]])
get(dem.reproject("EPSG:4326", None, 30), "dem", 150, [25.5, -19.3, 30.1, -15.3])
if not os.path.exists("data/countries.geojson"):
    lsib = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017").filter(ee.Filter.inList("country_na", ["Zambia", "Zimbabwe", "Botswana", "Mozambique", "Namibia", "Malawi", "Angola", "Tanzania", "Congo (Kinshasa)", "South Africa"]))
    json.dump(lsib.select(["country_na"]).getInfo(), open("data/countries.geojson", "w")); print("saved countries")
