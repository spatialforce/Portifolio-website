"""Rising sea in Portsmouth: data build.

    python fetch.py    # 1 m LiDAR tiles into cache/
    python buildings.py  # building blocks: OpenStreetMap outlines with LiDAR heights
    python build.py    # writes public/webmaps/flood/

Source: Environment Agency LIDAR Composite, 1 m ground model (DTM) and last return surface model (DSM),
Open Government Licence. Heights are metres above Ordnance Datum Newlyn.

Method: for every 1 m cell, the lowest sea level at which water reaches it from the open sea over ground
(the lowest "highest point on the way"), found by greyscale reconstruction of the ground model from the sea.
A cell is under water when the sea is at or above that level, so low ground behind a wall or a ridge stays
dry until the water gets over or round it. The rise is counted from mean high water springs at Portsmouth
(4.7 m above chart datum, chart datum 2.73 m below Ordnance Datum = 1.97 m).
No waves, no surge, no drains or pumps, and nothing narrower than 1 m.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import reconstruction

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "flood")
BOX = (462400, 97600, 468400, 104600)
MHWS = 1.97            # m above Ordnance Datum
SEA = 0.0              # border cells at or below this (or empty) are open sea
MAXRISE = 3.0
STEP = 0.02            # m per code in flood.png
TEX = 3                # m per pixel of shade.jpg and flood.png
MESH = 6               # m per vertex of height.png


def block(a, k, fn):
    h, w = a.shape
    return fn(a.reshape(h // k, k, w // k, k), axis=(1, 3))


def shade(z):
    """Soft hillshade of the surface model: light from the north west plus a little from straight above."""
    gy, gx = np.gradient(z)
    n = np.sqrt(gx * gx + gy * gy + 1)
    out = 0
    for az, w in ((315, 0.6), (270, 0.2), (0, 0.2)):
        a, alt = np.radians(az), np.radians(45)
        lx, ly, lz = np.sin(a) * np.cos(alt), np.cos(a) * np.cos(alt), np.sin(alt)
        out = out + w * np.clip((-gx * lx + gy * ly + lz) / n, 0, 1)      # rows run south, so +gy is northward slope
    return (0.75 * out + 0.25 / n).astype(np.float32)


def main():
    os.makedirs(OUT, exist_ok=True)
    dtm = np.load(os.path.join(CACHE, "dtm.npy"))
    dsm = np.load(os.path.join(CACHE, "dsm.npy"))
    cut = dtm.shape[0] % MESH                    # whole mesh cells only: drop the spare rows at the north edge
    dtm, dsm = dtm[cut:], dsm[cut:]
    empty = np.isnan(dtm)
    ground = np.where(empty, -5.0, dtm).astype(np.float32)

    # open sea: empty or low cells on the edge of the box
    edge = np.zeros(dtm.shape, bool)
    edge[0], edge[-1], edge[:, 0], edge[:, -1] = True, True, True, True
    seed = np.where(edge & (ground <= SEA), ground, np.float32(1e4)).astype(np.float32)
    level = reconstruction(seed, ground, method="erosion").astype(np.float32)
    np.save(os.path.join(CACHE, "level.npy"), level)

    rise = np.clip(level - MHWS, 0, None)
    land = level > MHWS
    steps = [round(i * 0.1, 1) for i in range(int(MAXRISE * 10) + 1)]
    ha = [round(float((land & (rise <= r + 1e-6)).sum()) / 1e4) for r in steps]
    print("land ha", round(land.sum() / 1e4), "sea ha", round((~land).sum() / 1e4))
    print(list(zip(steps, ha))[::5])

    # flood.png: red = rise code (0 sea today, 1 to 254 = rise in STEP m, 255 = stays dry)
    code = np.where(land, np.clip(np.ceil(rise / STEP), 1, 255), 0)
    code[rise > MAXRISE + 0.5] = 255
    code3 = block(code.astype(np.float32), TEX, np.median).astype(np.uint8)
    # buildings are drawn as their own blocks (buildings.py), so they are taken off the surface here; trees stay as shading
    surf = np.where(np.isnan(dsm), ground, dsm)
    surf = np.where(np.load(os.path.join(CACHE, "blocks_mask.npy")), ground, surf)
    rgb = np.zeros(code3.shape + (3,), np.uint8)
    rgb[..., 0] = code3
    Image.fromarray(rgb).save(os.path.join(OUT, "flood.png"), optimize=True)

    sh = block(shade(ndimage.gaussian_filter(surf, 0.7)), TEX, np.mean)
    Image.fromarray((np.clip(sh, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, "shade.jpg"), quality=80, optimize=True)

    # height.png: ground height in 0.1 m above -10 m, 16 bits in red (high) and green (low); blue = rise code at the vertex
    hm = np.clip((block(ground, MESH, np.mean) + 10) * 10, 0, 65535).astype(np.uint16)
    c6 = block(code.astype(np.float32), MESH, np.median).astype(np.uint8)
    out = np.dstack([(hm >> 8).astype(np.uint8), (hm & 255).astype(np.uint8), c6])
    Image.fromarray(out).save(os.path.join(OUT, "height.png"), optimize=True)

    json.dump({"box": BOX, "mhws": MHWS, "step": STEP, "tex": TEX, "mesh": MESH, "w": hm.shape[1], "h": hm.shape[0],
               "rise": steps, "ha": ha}, open(os.path.join(OUT, "flood.json"), "w"))
    for f in os.listdir(OUT):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
