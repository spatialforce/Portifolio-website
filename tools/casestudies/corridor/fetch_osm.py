"""OpenStreetMap roads (trunk to tertiary), settlements (place nodes) and rivers for the study box, via Overpass."""
import json, time, urllib.request, geopandas as gpd
from shapely.geometry import LineString, Point
BB = "-19.12,25.88,-17.28,29.22"
Q = {"roads": 'way["highway"~"^(motorway|trunk|primary|secondary|tertiary)(_link)?$"]({b});out geom tags;',
     "places": 'node["place"~"^(city|town|village|hamlet)$"]({b});out;',
     "rivers": 'way["waterway"="river"]({b});out geom tags;'}
import sys
for n, q in [(k, Q[k]) for k in (sys.argv[1:] or Q)]:
    for a in range(3):
        try:
            req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=("[out:json][timeout:240];" + q.format(b=BB)).encode(),
                                         headers={"User-Agent": "gis-case-study"})
            el = json.load(urllib.request.urlopen(req, timeout=300))["elements"]; break
        except Exception as e:
            print(n, "retry", e); time.sleep(30)
    if n == "places":
        g = gpd.GeoDataFrame([{"name": e["tags"].get("name", ""), "place": e["tags"]["place"]} for e in el],
                             geometry=[Point(e["lon"], e["lat"]) for e in el], crs=4326)
    else:
        rows = [e for e in el if len(e.get("geometry", [])) > 1]
        g = gpd.GeoDataFrame([{"name": e["tags"].get("name", ""), "kind": e["tags"].get("highway", e["tags"].get("waterway")), "ref": e["tags"].get("ref", "")} for e in rows],
                             geometry=[LineString([(p["lon"], p["lat"]) for p in e["geometry"]]) for e in rows], crs=4326)
    g.to_file(f"raw/osm_{n}.gpkg"); print(n, len(g))
