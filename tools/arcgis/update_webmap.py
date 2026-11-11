"""Write the access analysis into the Harare Health Facility Access web map on ArcGIS Online.

    python update_webmap.py           # builds cache/webmap_new.json and shows a summary
    python update_webmap.py --send    # also sends it to ArcGIS (needs tools/arcgis/.token)

The original web map is kept in harare_health_webmap_backup.json; send that back as the item's text to undo.
New layers are feature collections stored inside the web map itself (no hosted layers, no credits):
walking time bands, proposed clinic sites and facilities with weak mobile network. The old 2 km circles
layer is kept but hidden.
"""
import copy
import json
import os
import sys
import urllib.parse
import urllib.request

import shapely
from pyproj import Transformer
from shapely.geometry import shape
from shapely.geometry.polygon import orient

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM = "82868f52546a4e31bad6dae12c5dea96"
merc = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
SR = {"wkid": 102100, "latestWkid": 3857}
NB = " "


def fmt(n):
    return f"{round(n):,}".replace(",", NB)


def rings(geom):
    out = []
    for p in getattr(geom, "geoms", [geom]):
        p = orient(p, sign=-1.0)                     # Esri: outer rings clockwise, holes counter-clockwise
        for r in [p.exterior, *p.interiors]:
            out.append([[round(c, 1) for c in merc.transform(x, y)] for x, y in r.coords])
    return out


def point(lon, lat):
    x, y = merc.transform(lon, lat)
    return {"x": round(x, 1), "y": round(y, 1), "spatialReference": SR}


def fc(lid, title, gtype, fields, feats, renderer, popup, opacity=1, labels=None):
    ld = {"type": "Feature Layer", "name": title, "geometryType": gtype, "objectIdField": "OBJECTID", "spatialReference": SR,
          "fields": [{"name": "OBJECTID", "type": "esriFieldTypeOID", "alias": "OBJECTID"}] + fields,
          "drawingInfo": {"renderer": renderer}}
    if labels:
        ld["drawingInfo"]["labelingInfo"] = labels
    for i, f in enumerate(feats, 1):
        f["attributes"]["OBJECTID"] = i
    xs, ys = [], []
    for f in feats:
        g = f["geometry"]
        for r in g.get("rings", [[[g.get("x"), g.get("y")]]]):
            xs += [c[0] for c in r]; ys += [c[1] for c in r]
    ld["extent"] = {"xmin": min(xs), "ymin": min(ys), "xmax": max(xs), "ymax": max(ys), "spatialReference": SR}
    return {"id": lid, "title": title, "layerType": "ArcGISFeatureLayer", "opacity": opacity, "visibility": True,
            "featureCollection": {"layers": [{"layerDefinition": ld, "popupInfo": popup,
                                              "featureSet": {"geometryType": gtype, "features": feats}}],
                                  "showLegend": True}}


def sfs(color):
    return {"type": "esriSFS", "style": "esriSFSSolid", "color": color,
            "outline": {"type": "esriSLS", "style": "esriSLSSolid", "color": [255, 255, 255, 120], "width": 0.4}}


def main():
    r = json.load(open(os.path.join(HERE, "cache", "results.json"), encoding="utf-8"))
    web = json.load(open(os.path.join(HERE, "harare_health_webmap_backup.json"), encoding="utf-8"))
    new = copy.deepcopy(web)
    ops = new["operationalLayers"]
    for l in ops:
        if l["title"].startswith("2 km"):
            l["visibility"] = False

    # walking time bands
    colours = {1: [26, 120, 72, 255], 2: [120, 184, 96, 255], 3: [246, 196, 70, 255], 4: [232, 112, 45, 255], 5: [178, 34, 34, 255]}
    feats = [{"geometry": {"rings": rings(shape(z["geometry"])), "spatialReference": SR},
              "attributes": {"band": z["band"], "label": z["label"], "people": z["people"]}} for z in r["zones"]]
    zones = fc("walk_time", "Walking time to the nearest facility", "esriGeometryPolygon",
               [{"name": "band", "type": "esriFieldTypeInteger", "alias": "Band"},
                {"name": "label", "type": "esriFieldTypeString", "alias": "Walking time", "length": 32},
                {"name": "people", "type": "esriFieldTypeInteger", "alias": "People living here"}],
               feats,
               {"type": "uniqueValue", "field1": "band", "uniqueValueInfos": [
                   {"value": str(z["band"]), "label": z["label"], "symbol": sfs(colours[z["band"]])} for z in r["zones"]]},
               {"title": "{label} walk", "showAttachments": False, "fieldInfos": [
                   {"fieldName": "label", "label": "Walking time", "visible": True},
                   {"fieldName": "people", "label": "People living in this band", "visible": True,
                    "format": {"digitSeparator": True, "places": 0}}],
                "popupElements": [{"type": "text", "text":
                    "<p>About <b>{people}</b> people across Harare live <b>{label}</b> on foot from the nearest clinic or hospital, "
                    "walking at 4.5 km/h along the real roads and paths.</p>"}]},
               opacity=0.55)

    # proposed sites
    feats = [{"geometry": point(s["lon"], s["lat"]),
              "attributes": {"rank": i, "near": s["near"], "people": s["people"]}} for i, s in enumerate(r["sites"], 1)]
    sites = fc("new_sites", "Proposed new clinics", "esriGeometryPoint",
               [{"name": "rank", "type": "esriFieldTypeInteger", "alias": "Rank"},
                {"name": "near", "type": "esriFieldTypeString", "alias": "Near", "length": 64},
                {"name": "people", "type": "esriFieldTypeInteger", "alias": "People brought within 30 min"}],
               feats,
               {"type": "simple", "label": "Proposed new clinic", "symbol": {
                   "type": "esriSMS", "style": "esriSMSCircle", "color": [255, 255, 255, 255], "size": 18,
                   "outline": {"type": "esriSLS", "style": "esriSLSSolid", "color": [17, 17, 17, 255], "width": 2.5}}},
               {"title": "Proposed clinic {rank}, near {near}", "showAttachments": False, "fieldInfos": [
                   {"fieldName": "people", "label": "People brought within 30 min", "visible": True,
                    "format": {"digitSeparator": True, "places": 0}}],
                "popupElements": [{"type": "text", "text":
                    "<p>A clinic here would bring about <b>{people}</b> more people within a 30-minute walk of care. "
                    "Sites are picked one at a time: each is the spot that reaches the most people still left out.</p>"}]},
               labels=[{"labelExpressionInfo": {"expression": "$feature.rank"}, "labelPlacement": "esriServerPointLabelPlacementCenterCenter",
                        "symbol": {"type": "esriTS", "color": [17, 17, 17, 255], "font": {"family": "Arial", "size": 10, "weight": "bold"},
                                   "horizontalAlignment": "center", "verticalAlignment": "middle"}}])

    # weak network
    feats = [{"geometry": point(w["lon"], w["lat"]), "attributes": {"name": w["name"], "type": w["type"], "km": w["km"]}} for w in r["weak"]]
    weak = fc("weak_network", "Weak mobile network", "esriGeometryPoint",
              [{"name": "name", "type": "esriFieldTypeString", "alias": "Facility", "length": 128},
               {"name": "type", "type": "esriFieldTypeString", "alias": "Type", "length": 32},
               {"name": "km", "type": "esriFieldTypeDouble", "alias": "Km to nearest Econet site"}],
              feats,
              {"type": "simple", "label": "More than 2 km from an Econet site", "symbol": {
                  "type": "esriSMS", "style": "esriSMSCircle", "color": [0, 0, 0, 0], "size": 22,
                  "outline": {"type": "esriSLS", "style": "esriSLSSolid", "color": [230, 110, 20, 255], "width": 2.5}}},
              {"title": "{name}", "showAttachments": False, "fieldInfos": [
                  {"fieldName": "km", "label": "Km to nearest Econet site", "visible": True, "format": {"places": 1}}],
               "popupElements": [{"type": "text", "text":
                   "<p>This {type} is <b>{km} km</b> from the nearest Econet site, so calls and mobile data may be unreliable.</p>"}]})

    new["operationalLayers"] = [zones] + ops + [weak, sites]

    far = r["far"]; share = far / r["total"]
    snippet = (f"Walking access to Harare's {r['facilities']} clinics and hospitals: about {fmt(far)} people "
               f"({share:.0%}) live more than a 30-minute walk away, and five new sites would reach "
               f"{fmt(sum(s['people'] for s in r['sites']))} of them.")
    desc = ("<p>How far Harare's people have to walk to a clinic or hospital, measured along the real roads and paths "
            "at 4.5 km/h rather than in straight lines.</p>"
            f"<p><b>{fmt(far)}</b> of Harare Province's {fmt(r['total'])} people ({share:.0%}) live more than 30 minutes' walk "
            f"from the nearest of the {r['facilities']} facilities. The areas with the most people left out are "
            + ", ".join(s["name"] for s in r["suburbs"][:5]) + ".</p>"
            "<p>Five proposed sites, chosen one at a time to reach the most people still left out: "
            + "; ".join(f"near {s['near']} ({fmt(s['people'])})" for s in r["sites"]) + ".</p>"
            f"<p>Facilities more than 2 km from an Econet site are ringed in orange ({len(r['weak'])}).</p>"
            "<p>Data: health facilities from the web map's own layer; roads and suburb names from OpenStreetMap; "
            f"population from {r['popSource']}. Analysis in Python (SciPy shortest paths).</p>")

    text = json.dumps(new, separators=(",", ":"))
    open(os.path.join(HERE, "cache", "webmap_new.json"), "w", encoding="utf-8").write(text)
    print(f"web map JSON {len(text) / 1e6:.2f} MB, layers:", [l["title"] for l in new["operationalLayers"]])
    print(snippet)

    if "--send" not in sys.argv:
        return
    tok = json.load(open(os.path.join(HERE, ".token")))
    body = urllib.parse.urlencode({"text": text, "snippet": snippet, "description": desc,
                                   "f": "json", "token": tok["token"]}).encode()
    url = f"https://www.arcgis.com/sharing/rest/content/users/{tok['user']}/items/{ITEM}/update"
    res = json.load(urllib.request.urlopen(urllib.request.Request(url, body), timeout=120))
    print("ArcGIS:", res)


if __name__ == "__main__":
    main()
