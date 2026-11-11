"""Official city boundaries for the heat map, from OpenStreetMap (Nominatim, administrative polygons).

    python admin.py

Each city's boundary is drawn onto the same equal area grid as its temperature (see build.window) and written
as public/webmaps/heat/<slug>_city.png (255 inside, 0 outside). The raw polygons are kept in cache/admin/.
"""
import json
import os
import time

import requests
from PIL import Image
from pyproj import Transformer
from rasterio import features
from rasterio.transform import Affine
from shapely.geometry import mapping, shape
from shapely.ops import transform as reproject, unary_union

UA = {"User-Agent": "portfolio-heat-map/1.0 (city boundary lookup)"}
HERE = os.path.dirname(os.path.abspath(__file__))
ADMIN = os.path.join(HERE, "cache", "admin")
# what to search for where the plain city name finds the wrong area; R<n> is an OpenStreetMap relation
QUERY = {
    "johannesburg": "City of Johannesburg Metropolitan Municipality",
    "lusaka": "Lusaka District",
    "kinshasa": "Kinshasa",
    "lagos": "Lagos",
    "dar-es-salaam": "Dar es Salaam",
    "addis-ababa": "Addis Ababa",
    # Luanda municipality, the city before the 2024 reorganisation of the province
    "luanda": "R11704226",
    # the old Accra Metropolitan Assembly, before the 2018 split: today's Accra Metropolitan District and the
    # eight districts carved out of it
    "accra": "R1991850,R12759091,R12759092,R12759083,R12759087,R12759089,R12759086,R12759085,R12759088",
}


def lookup(slug, name, country):
    q = QUERY.get(slug, name)
    path = os.path.join(ADMIN, f"{slug}.json")
    if os.path.exists(path):
        hit = json.load(open(path, encoding="utf-8"))
        if hit and hit.get("query", q) == q:              # older cache files have no query field
            return hit
    if all(p[:1] == "R" and p[1:].isdigit() for p in q.split(",")):
        r = requests.get("https://nominatim.openstreetmap.org/lookup", headers=UA, timeout=60,
                         params={"osm_ids": q, "format": "jsonv2", "polygon_geojson": 1, "polygon_threshold": 0.0005})
    else:
        r = requests.get("https://nominatim.openstreetmap.org/search", headers=UA, timeout=60,
                         params={"q": f"{q}, {country}", "format": "jsonv2", "polygon_geojson": 1, "limit": 8, "polygon_threshold": 0.0005})
    r.raise_for_status()
    time.sleep(1.2)                                       # Nominatim allows one request a second
    hits = [h for h in r.json() if h.get("geojson", {}).get("type") in ("Polygon", "MultiPolygon")]
    if "," in q:                                          # several districts make one city
        hit = {"display_name": f"{name}: {len(hits)} districts joined",
               "geojson": mapping(unary_union([shape(h["geojson"]) for h in hits]).buffer(0))} if hits else None
    else:
        adm = [h for h in hits if h.get("category") == "boundary" and h.get("type") in ("administrative", "historic")]
        hit = (adm or hits or [None])[0]
    if hit:
        hit = {"query": q, "display_name": hit["display_name"], "geojson": hit["geojson"]}
    os.makedirs(ADMIN, exist_ok=True)
    json.dump(hit, open(path, "w", encoding="utf-8"))
    return hit


def outline(slug, lat, lon):
    """The city's boundary on its own equal area grid (metres), or None."""
    from build import CITIES
    name, country = next((c[1], c[2]) for c in CITIES if c[0] == slug)
    hit = lookup(slug, name, country)
    if not hit:
        return None
    to = Transformer.from_crs("EPSG:4326", f"+proj=laea +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m",
                              always_xy=True).transform
    return reproject(to, shape(hit["geojson"]))


def main():
    from build import CITIES, OUT, window
    for slug, name, country, lat, lon in CITIES:
        g = outline(slug, lat, lon)
        if g is None:
            print(f"{name:14s} no boundary found")
            continue
        win = window(slug, lat, lon)
        res = win["res"]
        aff = Affine(res, 0, win["x0"], 0, -res, win["y1"])
        mask = features.rasterize([(g, 255)], out_shape=(win["hm"] // res, win["wm"] // res), transform=aff, fill=0, dtype="uint8")
        Image.fromarray(mask, "L").save(os.path.join(OUT, f"{slug}_city.png"), optimize=True)
        whole, shown = g.area / 1e6, (mask > 0).sum() * res * res / 1e6
        cut = "" if shown > whole * 0.98 else f"  (only {shown / whole:.0%} inside the window)"
        hit = lookup(slug, name, country)
        print(f"{name:14s} {hit['display_name'][:55]:55s} {whole:7.0f} km2  window {win['wm'] / 1000:.0f} x {win['hm'] / 1000:.0f} km at {res} m{cut}")


if __name__ == "__main__":
    main()
