"""Turn the yearly building heights cached by build.py into one stable 3D city per window.

    python blocks.py            # every city that has been fetched
    python blocks.py nairobi

Why: the source is modelled from 10 m satellite imagery. Single years flicker (a cell is built one year and
empty the next) and heights jitter, so the year to year change is mostly noise. This keeps only what holds up:
  - a cell is a building if it is one in at least two of 2021, 2022 and 2023; its height is the middle of the three
  - heights are smoothed over the 3 x 3 neighbourhood of building cells and rounded to whole storeys of 3 m
  - neighbouring cells with the same storey count are merged into rectangular blocks

public/webmaps/city3d/<slug>.bin: uint16 records of x, y, width, depth (cells, from the top left) and height
    in tenths of a metre.
city3d.json: per city the window, cell size, block count, land under buildings, building volume and the
    tallest block.
"""
import json
import os
import sys

import numpy as np
from scipy import ndimage

from build import CACHE, CITIES, OUT, RES

LAST = (2021, 2022, 2023)
PRESENT = 0.35
STOREY = 3.0
MIN_H = 2.5


def stable(z):
    P = np.stack([z[f"p{y}"] >= PRESENT for y in LAST])
    H = np.stack([np.where(P[i], z[f"h{y}"], np.nan) for i, y in enumerate(LAST)])
    built = P.sum(0) >= 2
    h = np.where(built, np.nanmedian(H, 0), 0)
    built &= h >= MIN_H
    h = np.where(built, h, 0)
    # smooth over neighbouring building cells only, so edges are not pulled down to the ground
    s = ndimage.uniform_filter(h, 3)
    n = ndimage.uniform_filter(built.astype(float), 3)
    h = np.where(built, s / np.maximum(n, 1e-6), 0)
    q = np.where(built, np.maximum(1, np.round(h / STOREY)), 0).astype(np.int32)
    return q


def rectangles(q):
    """Greedy merge of equal-storey cells into rectangles."""
    H, W = q.shape
    used = np.zeros_like(q, bool)
    out = []
    for y in range(H):
        row = q[y]
        x = 0
        while x < W:
            v = row[x]
            if v == 0 or used[y, x]:
                x += 1
                continue
            w = 1
            while x + w < W and row[x + w] == v and not used[y, x + w]:
                w += 1
            d = 1
            while y + d < H and (q[y + d, x:x + w] == v).all() and not used[y + d, x:x + w].any():
                d += 1
            used[y:y + d, x:x + w] = True
            out.append((x, y, w, d, int(round(v * STOREY * 10))))
            x += w
    return np.array(out, np.uint16).reshape(-1, 5)


def main():
    only = sys.argv[1:]
    path = os.path.join(OUT, "city3d.json")
    doc = json.load(open(path)) if os.path.exists(path) else {"res": RES, "cities": []}
    doc = {"res": RES, "cities": [c for c in doc.get("cities", [])]}
    for slug, name, country, lat, lon, wkm, hkm in CITIES:
        npz = os.path.join(CACHE, f"{slug}.npz")
        if (only and slug not in only) or not os.path.exists(npz):
            continue
        q = stable(np.load(npz))
        r = rectangles(q)
        r.tofile(os.path.join(OUT, f"{slug}.bin"))
        cell = RES * RES
        hm = q * STOREY
        entry = {"slug": slug, "name": name, "country": country, "km": [wkm, hkm], "w": q.shape[1], "h": q.shape[0],
                 "blocks": len(r), "landKm2": round(float((q > 0).sum() * cell / 1e6), 2),
                 "volume": round(float(hm.sum() * cell / 1e6), 1), "top": int(hm.max())}
        doc["cities"] = [c for c in doc["cities"] if c["slug"] != slug] + [entry]
        for old in ("a", "b", "c"):                      # the per-year images are no longer used
            p = os.path.join(OUT, f"{slug}_{old}.png")
            if os.path.exists(p):
                os.remove(p)
        print(f"{name:13s} {len(r):7d} blocks from {int((q > 0).sum()):7d} cells   land {entry['landKm2']} km2"
              f"   volume {entry['volume']} million m3   tallest {entry['top']} m", flush=True)
    order = [c[0] for c in CITIES]
    doc["cities"].sort(key=lambda c: order.index(c["slug"]))
    json.dump(doc, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
