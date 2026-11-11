"""Pull the drivable road network and business locations for one city out of the
Geofabrik Zimbabwe extract, and save them as compact files for analyse.py.

    python extract.py harare
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))  # osmium lives here, not in the system Python
import osmium  # noqa: E402

from config import CATEGORIES, CITIES, SPEED  # noqa: E402

PBF = os.path.join(HERE, "raw", "zimbabwe.osm.pbf")


def main(city):
    w, s, e, n = CITIES[city]["bbox"]
    inside = lambda lon, lat: w <= lon <= e and s <= lat <= n  # noqa: E731
    want = {(k, v): c for c, spec in CATEGORIES.items() for k, v in spec["tags"]}

    coords = {}   # node id -> (lon, lat) for road nodes
    ways = []     # (highway, oneway, [node ids])
    pois = []     # category, name, brand, lon, lat
    seen = 0
    fp = osmium.FileProcessor(PBF).with_locations().with_filter(osmium.filter.KeyFilter("highway", "shop", "amenity"))
    for obj in fp:
        seen += 1
        tags = obj.tags
        cat = next((want[(k, tags.get(k))] for k in ("shop", "amenity") if (k, tags.get(k)) in want), None)
        if obj.is_node():
            if cat and obj.location.valid() and inside(obj.location.lon, obj.location.lat):
                pois.append({"cat": cat, "name": tags.get("name", ""), "brand": tags.get("brand", ""),
                             "lon": round(obj.location.lon, 6), "lat": round(obj.location.lat, 6)})
            continue
        if not obj.is_way():
            continue
        pts = [(nd.ref, nd.lon, nd.lat) for nd in obj.nodes if nd.location.valid()]
        if not pts:
            continue
        if cat:  # a business mapped as a building outline: use its middle
            lon = sum(p[1] for p in pts) / len(pts)
            lat = sum(p[2] for p in pts) / len(pts)
            if inside(lon, lat):
                pois.append({"cat": cat, "name": tags.get("name", ""), "brand": tags.get("brand", ""),
                             "lon": round(lon, 6), "lat": round(lat, 6)})
        hw = tags.get("highway")
        if hw in SPEED and tags.get("access") not in ("private", "no") and any(inside(p[1], p[2]) for p in pts):
            for ref, lon, lat in pts:
                coords[ref] = (round(lon, 6), round(lat, 6))
            ways.append([hw, tags.get("oneway", "no"), [p[0] for p in pts]])
    out = os.path.join(HERE, "cache", city)
    os.makedirs(out, exist_ok=True)
    json.dump({"coords": {str(k): v for k, v in coords.items()}, "ways": ways}, open(os.path.join(out, "roads.json"), "w"))
    json.dump(pois, open(os.path.join(out, "pois.json"), "w"), indent=0)
    print(f"read {seen:,} tagged objects; {len(ways):,} road ways, {len(coords):,} road nodes")
    for c in CATEGORIES:
        print(f"  {c:12s} {sum(p['cat'] == c for p in pois):5d}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "harare")
