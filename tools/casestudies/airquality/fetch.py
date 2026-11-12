# Sentinel-5P OFFL L3 (GEE) NO2 and SO2 period means on a 0.01 deg grid over Hwange and Maamba, WorldPop constrained 2020,
# and monthly source vs background series (background ring 80-150 km from Hwange, excluding 60 km round Maamba).
import io, json, urllib.request, numpy as np, rasterio, ee
ee.Initialize(project="directed-sun-490915-m4")
HPS, MAA = [26.4706, -18.3833], [27.18594, -17.352722]
X0, Y0, X1, Y1, R = 25.4, -19.8, 28.6, -16.6, 0.01
W, H = round((X1 - X0) / R), round((Y1 - Y0) / R)
NO2 = ("COPERNICUS/S5P/OFFL/L3_NO2", "tropospheric_NO2_column_number_density")
SO2 = ("COPERNICUS/S5P/OFFL/L3_SO2", "SO2_column_number_density")
PER = {"pre": ("2019-01-01", "2023-01-01"), "post": ("2024-01-01", "2026-01-01")}

def dl(img, name):
    url = img.getDownloadURL({"crs": "EPSG:4326", "crs_transform": [R, 0, X0, 0, -R, Y1], "dimensions": f"{W}x{H}", "format": "GEO_TIFF"})
    d = urllib.request.urlopen(url, timeout=900).read()
    with rasterio.open(io.BytesIO(d)) as r, rasterio.open(f"rast/{name}.tif", "w", **(r.profile | {"compress": "deflate"})) as o: o.write(r.read())
    print(name, flush=True)

for g, (col, band) in (("no2", NO2), ("so2", SO2)):
    for p, (a, b) in PER.items():
        c = ee.ImageCollection(col).select(band).filterDate(a, b)
        dl(c.mean().multiply(1e6).toFloat(), f"{g}_{p}")          # umol/m2
        if g == "no2": dl(c.count().toFloat(), f"{g}_{p}_n")
wp = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").filter(ee.Filter.eq("country", "ZWE")).filter(ee.Filter.eq("year", 2020)).first().select("population")
# wpc2020 is built by fetch_pop.py (density x area method)

hp, mp = ee.Geometry.Point(HPS), ee.Geometry.Point(MAA)
geo = {"hwange": hp.buffer(15000), "maamba": mp.buffer(15000),
       "bg": hp.buffer(150000).difference(hp.buffer(80000)).difference(mp.buffer(60000))}
fire = ee.ImageCollection("FIRMS").select("T21")
months = ee.List([f"{y}-{m:02d}-01" for y in range(2019, 2026) for m in range(1, 13)])
def month(col, band):
    def f(d):
        d = ee.Date(d); im = ee.ImageCollection(col).select(band).filterDate(d, d.advance(1, "month")).mean()
        return ee.Feature(None, {k: im.reduceRegion(ee.Reducer.mean(), v, 1113.2).get(band) for k, v in geo.items()} | {"m": d.format("YYYY-MM")})
    return ee.FeatureCollection(months.map(f)).getInfo()["features"]
ser = {"no2": [f["properties"] for f in month(*NO2)], "so2": [f["properties"] for f in month(*SO2)]}
def fires(d):
    d = ee.Date(d); im = fire.filterDate(d, d.advance(1, "month")).max().gt(0)
    return ee.Feature(None, {"m": d.format("YYYY-MM"), "px": im.reduceRegion(ee.Reducer.sum(), hp.buffer(80000), 1000).get("T21")})
ser["fire80"] = [f["properties"] for f in ee.FeatureCollection(months.map(fires)).getInfo()["features"]]
json.dump(ser, open("data/monthly.json", "w")); print("monthly ok")
