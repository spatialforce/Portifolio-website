"""Named rivers (OSM waterway=river) in both study bboxes -> data/osm_rivers.gpkg (aoi, name). Run: python -I osmrivers.py"""
import json, time, urllib.request, urllib.parse, geopandas as gpd
from shapely.geometry import LineString
BB = {"muz": (-16.9, 30.7, -15.8, 31.7), "save": (-21.6, 31.7, -19.8, 32.6)}
rows = []
for k, (s, w, n, e) in BB.items():
    q = f'[out:json][timeout:120];way["waterway"="river"]["name"]({s},{w},{n},{e});out geom;'
    for u in ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass-api.de/api/interpreter"]:
        try:
            req = urllib.request.Request(u, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "casestudy-maps/1.0"})
            E = json.load(urllib.request.urlopen(req, timeout=180))["elements"]; break
        except Exception as ex: print("retry", u, ex); time.sleep(10)
    for el in E:
        if len(el.get("geometry", [])) > 1:
            rows.append(dict(aoi=k, name=el["tags"]["name"], geometry=LineString([(p["lon"], p["lat"]) for p in el["geometry"]])))
g = gpd.GeoDataFrame(rows, crs=4326); g.to_file("data/osm_rivers.gpkg")
L = g.to_crs(32736).assign(km=lambda d: d.length / 1000).groupby(["aoi", "name"]).km.sum().round(0)
print(L[L > 15].to_string())
