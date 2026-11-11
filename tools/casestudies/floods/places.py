"""Named places (OSM place nodes: town, village, hamlet) and refugee camp in both study bboxes -> data/places.csv
Run: python -I places.py"""
import json, urllib.request, urllib.parse, pandas as pd
BB = {"muz": (-16.7, 30.6, -15.6, 32.0), "save": (-21.5, 31.9, -19.6, 33.0)}
rows = []
for k, (s, w, n, e) in BB.items():
    q = f'[out:json][timeout:60];(node["place"~"town|village|city"]({s},{w},{n},{e});nwr["amenity"="refugee_site"]({s},{w},{n},{e});nwr["name"~"Tongogara"]({s},{w},{n},{e}););out center;'
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "casestudy-maps/1.0"})
    for el in json.load(urllib.request.urlopen(req, timeout=90))["elements"]:
        t = el.get("tags", {}); c = el.get("center", el)
        if "name" in t: rows.append(dict(aoi=k, name=t["name"], kind=t.get("place", t.get("amenity", t.get("landuse", ""))), lon=c["lon"], lat=c["lat"]))
d = pd.DataFrame(rows).drop_duplicates(["aoi", "name"]); d.to_csv("data/places.csv", index=False)
print(d.groupby(["aoi", "kind"]).size().to_string())
