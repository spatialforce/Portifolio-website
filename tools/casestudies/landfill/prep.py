# Criteria and constraint rasters on the 30 m grid.
# Outputs rast/: city, slope, d_sett, d_river, d_water, d_road, excl_* layers, mask.
import json, numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
from scipy.ndimage import distance_transform_edt
from shapely.geometry import LineString, Polygon, Point

src = rasterio.open("rast/lc.tif"); TR, (H, W) = src.transform, src.shape
PROF = dict(src.profile, compress="deflate")
R = 30.0
def rd(n): return rasterio.open(f"rast/{n}.tif").read(1)
def save(n, a, dt="float32"):
    with rasterio.open(f"rast/{n}.tif", "w", **dict(PROF, dtype=dt, nodata=None)) as d: d.write(a.astype(dt), 1)
def burn(geoms): return rasterize([(g, 1) for g in geoms], out_shape=(H, W), transform=TR, fill=0, dtype="uint8", all_touched=True)
def dist(m): return (distance_transform_edt(m == 0) * R).astype("float32")

def geoms(name, poly=False):
    out = []
    for e in json.load(open(f"data/osm_{name}.json")):
        if e["type"] == "node": out.append(Point(e["lon"], e["lat"])); continue
        parts = [e["geometry"]] if e["type"] == "way" else [m["geometry"] for m in e.get("members", []) if "geometry" in m]
        for p in parts:
            c = [(q["lon"], q["lat"]) for q in p]
            if len(c) < 2: continue
            out.append(Polygon(c) if poly and len(c) > 3 and c[0] == c[-1] else LineString(c))
    return list(gpd.GeoSeries(out, crs=4326).to_crs(32735))

city = gpd.read_file("data/bulawayo.gpkg"); cm = rasterize(city.geometry, out_shape=(H, W), transform=TR, fill=0, dtype="uint8")
save("city", cm, "uint8")

dem = rd("dem"); gy, gx = np.gradient(dem, R); slope = (np.hypot(gx, gy) * 100).astype("float32")  # percent
save("slope", slope)
lc, bf = rd("lc"), rd("bfrac")
sett = ((lc == 50) | (bf >= 0.2)).astype("uint8"); save("sett", sett, "uint8")
d_sett = dist(sett); save("d_sett", d_sett)
d_river = dist(burn(geoms("rivers"))); save("d_river", d_river)
water = burn(geoms("water", True) + geoms("wetland", True)) | (lc == 80) | (lc == 90)
d_water = dist(water); save("d_water", d_water)
d_road = dist(burn(geoms("roads"))); save("d_road", d_road)
d_rail = dist(burn(geoms("rail")))

# open airports only (Induna is closed)
ae = json.load(open("data/osm_aero.json"))
ind = [g for e, g in zip(ae, geoms("aero", True)) if e.get("tags", {}).get("name", "").startswith("Induna")]
run = [g for e, g in zip(ae, geoms("aero", True)) if e.get("tags", {}).get("aeroway") == "runway" and not any(i.buffer(200).contains(g) for i in ind)]
d_air = dist(burn(run)); save("d_air", d_air)

EX = {"Settlements": d_sett <= 500, "Rivers": d_river <= 300, "Water bodies": d_water <= 500,
      "Main roads": d_road <= 100, "Railways": d_rail <= 100, "Airports": d_air <= 3000, "Steep slopes": slope > 20}
ex = np.zeros((H, W), bool)
for k, m in EX.items(): ex |= m
save("excl", ex, "uint8")
mask = (cm == 1) & ~ex; save("mask", mask, "uint8")
tot = cm.sum()
st = {k: float(round(100 * (m & (cm == 1)).sum() / tot, 1)) for k, m in EX.items()}
st["Settlements 1 km"] = float(round(100 * ((d_sett <= 1000) & (cm == 1)).sum() / tot, 1))
st["city_km2"] = float(round(tot * 0.0009, 1)); st["open_km2"] = float(round(mask.sum() * 0.0009, 1))
st["open_km2_sett1km"] = float(round(((cm == 1) & ~ex & (d_sett > 1000)).sum() * 0.0009, 1))
json.dump(st, open("out/constraints.json", "w"), indent=1); print(st)
