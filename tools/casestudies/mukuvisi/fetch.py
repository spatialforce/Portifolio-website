"""Rasters and vectors for the Mukuvisi catchment study on one 30 m grid in UTM zone 36S (EPSG:32736).
Copernicus GLO-30 DEM and ESA WorldCover 2021 v200 from AWS open data, SoilGrids 2.0 sand and clay (0-5, 5-15, 15-30 cm)
from the ISRIC WCS (masked over built-up land), iSDAsoil 30 m sand and clay (0-20, 20-50 cm) from AWS, OpenStreetMap rivers, roads and suburbs from an Overpass mirror."""
import sys, json, time, urllib.request, numpy as np, rasterio, geopandas as gpd
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from pyproj import Transformer
from shapely.geometry import LineString, Point

LL = (30.80, -18.08, 31.33, -17.66); R = 30
t = Transformer.from_crs(4326, 32736, always_xy=True)
xs, ys = zip(*[t.transform(x, y) for x in (LL[0], LL[2]) for y in (LL[1], LL[3])])
X0, X1 = (min(xs) // R) * R, (max(xs) // R + 1) * R
Y0, Y1 = (min(ys) // R) * R, (max(ys) // R + 1) * R
W, H = int((X1 - X0) / R), int((Y1 - Y0) / R); TR = from_origin(X0, Y1, R, R)
json.dump({"x0": X0, "y1": Y1, "res": R, "w": W, "h": H, "crs": "EPSG:32736"}, open("raw/grid.json", "w")); print("grid", W, H)
PROF = dict(driver="GTiff", width=W, height=H, count=1, crs="EPSG:32736", transform=TR, compress="deflate")


def warp(srcs, name, rs, dtype, nodata=None):
    out = np.zeros((H, W), dtype)
    for u in srcs:
        with rasterio.open(u) as s:
            tmp = np.zeros_like(out)
            reproject(rasterio.band(s, 1), tmp, dst_transform=TR, dst_crs="EPSG:32736", resampling=rs, src_nodata=nodata, dst_nodata=0)
            out = np.where(tmp != 0, tmp, out)
        print(" read", u.split("/")[-1], flush=True)
    with rasterio.open(f"raw/{name}.tif", "w", **PROF, dtype=dtype) as o: o.write(out, 1)
    print("saved", name, out.min(), out.max(), flush=True)


def warpb(u, b, name):  # one band of a large COG, nodata 255
    out = np.full((H, W), 255, "uint8")
    with rasterio.open(u) as s:
        reproject(rasterio.band(s, b), out, dst_transform=TR, dst_crs="EPSG:32736", resampling=Resampling.nearest, src_nodata=255, dst_nodata=255)
    with rasterio.open(f"raw/{name}.tif", "w", **PROF, dtype="uint8", nodata=255) as o: o.write(out, 1)
    print("saved", name, (out == 255).mean().round(3), flush=True)


want = sys.argv[1:] or ["dem", "lc", "soil", "isda", "osm"]
if "dem" in want:
    DEM = [f"/vsicurl/https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_S{la:02d}_00_E{lo:03d}_00_DEM/Copernicus_DSM_COG_10_S{la:02d}_00_E{lo:03d}_00_DEM.tif"
           for la in (19, 18) for lo in (30, 31)]
    warp(DEM, "dem", Resampling.bilinear, "float32")
if "lc" in want:
    WC = [f"/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{k}_Map.tif" for k in ("S21E030", "S18E030")]
    warp(WC, "lc", Resampling.mode, "uint8")
if "soil" in want:  # g/kg, 250 m Homolosine; fetched in WGS 84 then warped
    for v in ("sand", "clay"):
        for d in ("0-5cm", "5-15cm", "15-30cm"):
            u = (f"https://maps.isric.org/mapserv?map=/map/{v}.map&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID={v}_{d}_mean"
                 f"&FORMAT=image/tiff&SUBSET=long({LL[0] - 0.02},{LL[2] + 0.02})&SUBSET=lat({LL[1] - 0.02},{LL[3] + 0.02})"
                 "&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/4326&OUTPUTCRS=http://www.opengis.net/def/crs/EPSG/0/4326"
                 "&RESOLUTION=long(0.0025)&RESOLUTION=lat(0.0025)")
            f = f"raw/sg_{v}_{d}.tif"
            for a in range(4):
                try:
                    import ssl; c = ssl.create_default_context(); open(f, "wb").write(urllib.request.urlopen(u, timeout=300, context=c).read()); break
                except Exception as e: print("retry", e); time.sleep(10)
            warp([f], f"{v}_{d}", Resampling.bilinear, "float32", nodata=0); print(v, d, flush=True)
if "isda" in want:  # iSDAsoil 30 m, % by weight; band 1 = 0-20 cm, band 2 = 20-50 cm
    for v in ("sand", "clay"):
        for b, d in ((1, "0-20"), (2, "20-50")):
            warpb(f"/vsicurl/https://isdasoil.s3.amazonaws.com/soil_data/{v}_content/{v}_content.tif", b, f"isda_{v}_{d}")
if "osm" in want:
    BB = f"{LL[1]},{LL[0]},{LL[3]},{LL[2]}"
    Q = {"rivers": 'way["waterway"~"^(river|stream)$"]({b});out geom tags;',
         "roads": 'way["highway"~"^(motorway|trunk|primary|secondary)(_link)?$"]({b});out geom tags;',
         "places": 'node["place"~"^(city|town|suburb|neighbourhood)$"]({b});out;',
         "dams": 'way["natural"="water"]({b});out geom tags;'}
    for n, q in [(k, Q[k]) for k in (want[want.index("osm") + 1:] or Q)]:
        for a in range(3):
            try:
                req = urllib.request.Request("https://maps.mail.ru/osm/tools/overpass/api/interpreter",
                                             data=("[out:json][timeout:240];" + q.format(b=BB)).encode(), headers={"User-Agent": "gis-case-study"})
                el = json.load(urllib.request.urlopen(req, timeout=300))["elements"]; break
            except Exception as e: print(n, "retry", e); time.sleep(20)
        el = [e for e in el if "tags" in e or n != "places"]
        if n == "places":
            g = gpd.GeoDataFrame([{"name": e["tags"].get("name", ""), "place": e["tags"]["place"]} for e in el],
                                 geometry=[Point(e["lon"], e["lat"]) for e in el], crs=4326)
        else:
            rows = [e for e in el if len(e.get("geometry", [])) > 1]
            geo = [LineString([(p["lon"], p["lat"]) for p in e["geometry"]]) for e in rows]
            if n == "dams":
                from shapely.geometry import Polygon
                geo = [Polygon(l.coords) if len(l.coords) > 3 and l.is_ring else l for l in geo]
            g = gpd.GeoDataFrame([{"name": e["tags"].get("name", ""), "kind": e["tags"].get("highway", e["tags"].get("waterway", "water")),
                                   "ref": e["tags"].get("ref", "")} for e in rows], geometry=geo, crs=4326)
        g.to_file(f"raw/osm_{n}.gpkg"); print(n, len(g), flush=True)
