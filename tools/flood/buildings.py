"""Rising sea in Portsmouth: buildings.

    python buildings.py    # after fetch.py; writes public/webmaps/flood/blocks.png

Outlines: OpenStreetMap buildings (Overpass), ODbL. Heights: Environment Agency 1 m LiDAR.
Each building is a flat topped block. Top = 80th percentile of the surface model inside the outline,
foot = 10th percentile of the ground model inside it. Outlines under MIN_H tall in the LiDAR are left out.

blocks.png is a stream of 16 bit numbers packed in the red green blue bytes:
    n, foot, top, x0, y0, dx1, dy1, ...   (heights in 0.1 m above -10 m, x east and y south in UNIT m from the
    north west corner of the model, later corners as differences) and a single 0 at the end.
"""
import json
import os
import sys

import numpy as np
import requests
from PIL import Image
from pyproj import Transformer
from shapely.geometry import Polygon
from skimage.draw import polygon as fill

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "flood")
BOX = (462400, 97600, 468400, 104600)
MESH = 6
UNIT = 0.2
MIN_H = 2.0


def osm():
    path = os.path.join(CACHE, "osm.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    t = Transformer.from_crs(27700, 4326, always_xy=True)
    w, s = t.transform(BOX[0], BOX[1])
    e, n = t.transform(BOX[2], BOX[3])
    q = f'[out:json][timeout:180];(way["building"]({s - .002},{w - .003},{n + .002},{e + .003});relation["building"]({s - .002},{w - .003},{n + .002},{e + .003}););out geom;'
    for url in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        r = requests.post(url, data={"data": q}, headers={"User-Agent": "portfolio-map-build"}, timeout=240)
        if r.ok:
            open(path, "wb").write(r.content)
            return r.json()
        print(url, r.status_code)
    sys.exit("Overpass did not answer")


def main():
    dtm = np.load(os.path.join(CACHE, "dtm.npy"))
    dsm = np.load(os.path.join(CACHE, "dsm.npy"))
    cut = dtm.shape[0] % MESH
    dtm, dsm = dtm[cut:], dsm[cut:]
    dsm = np.where(np.isnan(dsm), dtm, dsm)
    H, W = dtm.shape
    north = BOX[1] + H
    t = Transformer.from_crs(4326, 27700, always_xy=True)

    rings = []
    for el in osm()["elements"]:
        if el["type"] == "way" and "geometry" in el:
            rings.append(el["geometry"])
        elif el["type"] == "relation":
            rings += [m["geometry"] for m in el.get("members", []) if m.get("role") == "outer" and "geometry" in m]
    print("outlines", len(rings))

    out, kept, seen = [], 0, np.zeros(dtm.shape, bool)
    for g in rings:
        if len(g) < 4:
            continue
        x, y = t.transform([p["lon"] for p in g], [p["lat"] for p in g])
        x, y = np.array(x) - BOX[0], north - np.array(y)
        if x.max() < 0 or y.max() < 0 or x.min() > W or y.min() > H:
            continue
        p = Polygon(np.c_[x, y])
        if not p.is_valid:
            p = p.buffer(0)
        p = p.simplify(0.4)
        if p.is_empty or p.geom_type != "Polygon" or p.area < 12:
            continue
        c = np.array(p.exterior.coords)[:-1]
        if len(c) > 250 or c.min() < 0 or c[:, 0].max() >= W or c[:, 1].max() >= H:
            continue
        rr, cc = fill(c[:, 1], c[:, 0], dtm.shape)
        if len(rr) < 8:
            continue
        foot = float(np.percentile(dtm[rr, cc], 10))
        top = float(np.percentile(dsm[rr, cc], 80))
        if top - foot < MIN_H:
            continue
        seen[rr, cc] = True
        q = np.round(c / UNIT).astype(np.int64)
        d = np.diff(q, axis=0)
        out += [len(q), int(round((foot + 10) * 10)), int(round((top + 10) * 10)), q[0, 0], q[0, 1]] + list(d.ravel() & 0xFFFF)
        kept += 1
    tall = (dsm - dtm) > 3.0
    print("blocks", kept, "share of tall LiDAR cells inside an outline", round(float((tall & seen).sum() / tall.sum()), 2),
          "share of outline cells that are tall", round(float((tall & seen).sum() / seen.sum()), 2))
    np.save(os.path.join(CACHE, "blocks_mask.npy"), seen)

    a = np.array(out + [0], np.uint16)
    b = np.zeros(-(-len(a) * 2 // (3 * 2048)) * 3 * 2048, np.uint8)
    b[0:len(a) * 2:2], b[1:len(a) * 2:2] = a >> 8, a & 255
    Image.fromarray(b.reshape(-1, 2048, 3)).save(os.path.join(OUT, "blocks.png"), optimize=True)
    print("blocks.png", os.path.getsize(os.path.join(OUT, "blocks.png")) // 1024, "KB")


if __name__ == "__main__":
    main()
