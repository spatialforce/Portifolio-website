# Fetch OSM power lines, substations, major roads and solar plants around
# Matabeleland South from Overpass. Saves GeoJSON into data/.
import json, time, urllib.request

BBOX = (-23.4, 25.7, -18.5, 32.1)  # s, w, n, e  (province + ~1 deg margin)
URL = "https://overpass-api.de/api/interpreter"

QUERIES = {
    "power_lines": '[out:json][timeout:180];way["power"="line"]({b});out geom;',
    "power_minor": '[out:json][timeout:180];way["power"="minor_line"]({b});out geom;',
    "substations": '[out:json][timeout:180];nwr["power"="substation"]({b});out center tags;',
    "roads": '[out:json][timeout:300];way["highway"~"^(motorway|trunk|primary|secondary)$"]({b});out geom;',
    "solar_plants": '[out:json][timeout:120];nwr["plant:source"="solar"]({b});out center tags;',
}

def run(name, q):
    q = q.format(b=",".join(str(x) for x in BBOX))
    req = urllib.request.Request(URL, data=q.encode(), headers={"User-Agent": "gis-case-study"})
    with urllib.request.urlopen(req, timeout=360) as r:
        d = json.load(r)
    feats = []
    for el in d["elements"]:
        t = el.get("tags", {})
        if el["type"] == "way" and "geometry" in el:
            coords = [[p["lon"], p["lat"]] for p in el["geometry"]]
            geom = {"type": "LineString", "coordinates": coords}
        elif "center" in el:
            geom = {"type": "Point", "coordinates": [el["center"]["lon"], el["center"]["lat"]]}
        elif el["type"] == "node":
            geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
        else:
            continue
        feats.append({"type": "Feature", "geometry": geom, "properties": {
            "id": el["id"], "voltage": t.get("voltage"), "name": t.get("name"),
            "highway": t.get("highway"), "operator": t.get("operator"),
            "plant_output": t.get("plant:output:electricity")}})
    out = {"type": "FeatureCollection", "features": feats}
    json.dump(out, open(f"data/{name}.geojson", "w"))
    print(name, len(feats))

for name, q in QUERIES.items():
    for attempt in range(3):
        try:
            run(name, q)
            break
        except Exception as e:
            print(name, "retry", attempt, e)
            time.sleep(30)
