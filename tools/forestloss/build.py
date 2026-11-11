"""Tree cover loss in Zimbabwe, 2001 to 2025: data build.

    Hansen et al. Global Forest Change v1.13 (UMD/hansen/global_forest_change_2025_v1_13)
    FAO GAUL 2025 provinces
    both through Earth Engine project directed-sun-490915-m4

Raster (lossyear.png, RGBA, EPSG:4326 at RES degrees):
    R = year of loss most common in the cell (1 = 2001 ... 25 = 2025), 0 = none
    G = share of the cell lost, 0..255
    B = tree cover in 2000, percent
    A = 255 inside Zimbabwe
Stats (forest.json): loss in hectares per year for the country and each province,
measured at the full 30 m, counting land with 10% canopy cover or more in 2000.

    python build.py
"""
import io
import json
import os

import ee
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "forestloss")
PROJECT = "directed-sun-490915-m4"
HANSEN = "UMD/hansen/global_forest_change_2025_v1_13"
YEARS = list(range(2001, 2026))
RES = 0.0027                    # about 300 m
W0, N0, E0, S0 = 25.2, -15.55, 33.1, -22.45
CANOPY = 10                     # percent; 10 keeps the open miombo and mopane woodland that covers most of Zimbabwe


def provinces():
    fc = ee.FeatureCollection("FAO/GAUL/2025/level1").filter(ee.Filter.eq("GAUL0_NAME", "Zimbabwe"))
    return fc


def raster(zw):
    path = os.path.join(CACHE, "grid.npz")
    if os.path.exists(path):
        return np.load(path)["a"]
    h = ee.Image(HANSEN)
    tree = h.select("treecover2000").gte(CANOPY)
    loss = h.select("loss").And(tree)
    proj = ee.Projection("EPSG:4326").scale(RES, RES)
    frac = loss.unmask(0).reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj).rename("frac")
    year = h.select("lossyear").updateMask(loss).reduceResolution(ee.Reducer.mode(), maxPixels=1024).reproject(proj).unmask(0).rename("year")
    tc = h.select("treecover2000").reduceResolution(ee.Reducer.mean(), maxPixels=1024).reproject(proj).rename("tc")
    inside = ee.Image(0).byte().paint(zw, 1).rename("in")
    img = year.addBands(frac).addBands(tc).addBands(inside).toFloat()

    nx, ny = int(round((E0 - W0) / RES)), int(round((N0 - S0) / RES))
    out = np.zeros((ny, nx, 4), np.float32)
    tile = 256
    for ty in range(0, ny, tile):
        for tx in range(0, nx, tile):
            w, hh = min(tile, nx - tx), min(tile, ny - ty)
            raw = ee.data.computePixels({
                "expression": img, "fileFormat": "NPY",
                "grid": {"dimensions": {"width": w, "height": hh},
                         "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": W0 + tx * RES,
                                             "shearY": 0, "scaleY": -RES, "translateY": N0 - ty * RES},
                         "crsCode": "EPSG:4326"}})
            a = np.load(io.BytesIO(raw))
            for k, n in enumerate(("year", "frac", "tc", "in")):
                out[ty:ty + hh, tx:tx + w, k] = a[n]
            print("tile", ty, tx)
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(path, a=out)
    return out


def stats(zw):
    path = os.path.join(CACHE, "stats.json")
    if os.path.exists(path):
        return json.load(open(path))
    h = ee.Image(HANSEN)
    tree = h.select("treecover2000").gte(CANOPY)
    ha = ee.Image.pixelArea().divide(1e4)
    img = ha.updateMask(h.select("loss").And(tree)).addBands(h.select("lossyear"))
    # one request per province, in parallel: a single request for the whole country runs out of time
    from concurrent.futures import ThreadPoolExecutor
    names = zw.aggregate_array("GAUL1_NAME").getInfo()

    def one(name):
        geom = zw.filter(ee.Filter.eq("GAUL1_NAME", name)).geometry()
        g = img.reduceRegion(ee.Reducer.sum().group(groupField=1, groupName="y"), geom, 30, maxPixels=1e11, tileScale=8)
        c = ha.updateMask(tree).reduceRegion(ee.Reducer.sum(), geom, 30, maxPixels=1e11, tileScale=8)
        r = ee.Dictionary({"g": g.get("groups"), "c": c.get("area")}).getInfo()
        print("  stats:", name, flush=True)
        return name, {"loss": {str(x["y"]): x["sum"] for x in r["g"]}, "cover2000": r["c"]}

    with ThreadPoolExecutor(10) as ex:
        out = dict(ex.map(one, names))
    json.dump(out, open(path, "w"))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    ee.Initialize(project=PROJECT)
    zw = provinces()

    a = raster(zw)
    rgba = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgba[..., 0] = np.clip(np.round(a[..., 0]), 0, 25)
    rgba[..., 1] = np.clip(np.round(a[..., 1] * 255), 0, 255)
    rgba[..., 2] = np.clip(np.round(a[..., 2]), 0, 100)
    rgba[..., 3] = np.where(a[..., 3] > 0.5, 255, 0)
    rgba[rgba[..., 3] == 0, :3] = 0
    Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, "lossyear.png"), optimize=True)

    st = stats(zw)
    geo = zw.map(lambda f: f.simplify(400)).getInfo()
    shapes = {}
    for f in geo["features"]:
        g = f["geometry"]
        parts = g["geometries"] if g["type"] == "GeometryCollection" else [g]
        polys = []
        for q in parts:
            if q["type"] == "Polygon":
                polys.append(q["coordinates"])
            elif q["type"] == "MultiPolygon":
                polys += q["coordinates"]
        shapes[f["properties"]["GAUL1_NAME"]] = [[[round(x, 3), round(y, 3)] for x, y in poly[0]] for poly in polys]

    prov = []
    for name, s in st.items():
        loss = [round(s["loss"].get(str(y - 2000), 0)) for y in YEARS]
        prov.append(dict(name=name.replace("Matebeleland", "Matabeleland"), cover2000=round(s["cover2000"]), loss=loss, shape=shapes.get(name, [])))
    prov.sort(key=lambda p: -sum(p["loss"]))
    total = [sum(p["loss"][i] for p in prov) for i in range(len(YEARS))]
    json.dump(dict(years=YEARS, canopy=CANOPY, cover2000=sum(p["cover2000"] for p in prov), loss=total, provinces=prov,
                   grid=dict(w=rgba.shape[1], h=rgba.shape[0], west=W0, north=N0, res=RES)),
              open(os.path.join(OUT, "forest.json"), "w", encoding="utf-8"), separators=(",", ":"))
    print("total loss 2001-2025:", round(sum(total) / 100), "km² of", round(sum(p["cover2000"] for p in prov) / 100), "km² tree cover")
    for p in prov:
        print(f'{p["name"]:22} {sum(p["loss"]) / 100:8.0f} km²  of {p["cover2000"] / 100:7.0f}')
    print("by year (km²):", [round(v / 100) for v in total])


if __name__ == "__main__":
    main()
