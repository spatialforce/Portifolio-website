"""Turn the cached GBIF grids into the files the web map loads.

For every species and month:
  reporting rate = species records / all records of its group (birds, insects or mammals)
computed on lightly smoothed grids, and only where the group has enough records to trust.

Writes to public/webmaps/migration/:
  <slug>.png   1024 x 512 atlas, 4 x 4 slots of 256 x 128 (months 1 to 12 in reading order)
               red = (rate / vmax) ** GAMMA scaled to 0..255, green = 255 where the data is trustworthy
  atlas.json   species metadata, colour scale, latitude wave and flyway centres
"""
import json
import os

import numpy as np
from PIL import Image

from species import EFFORT, SPECIES, YEARS

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "grids")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "migration")
W, H = 256, 128
CELL = 180 / H
LAT = 90 - (np.arange(H) + 0.5) * CELL           # cell centre latitudes, north to south
LON = -180 + (np.arange(W) + 0.5) * CELL
AREA = np.cos(np.radians(LAT))[:, None]          # relative cell area
MIN_FLYWAY = 0.08  # a flyway needs this share of the population to get a trail
GAMMA = 0.7  # colour curve: stored value = (rate / vmax) ** GAMMA
# rate = species / (group + DAMP): places with few records still show but faintly.
# Cells with fewer than MIN_EFFORT group records are marked as unknown.
DAMP = {"Aves": 40, "Insecta": 10, "Cetacea": 5}
MIN_EFFORT = {"Aves": 4, "Insecta": 2, "Cetacea": 1}

# flyways for the population centre trails: lon ranges
FLYWAYS = [
    ("Americas", -170, -25),
    ("Africa and Eurasia", -25, 65),
    ("Asia and Australasia", 65, 180),
]

K = np.array([1, 4, 6, 4, 1], float); K /= K.sum()


def blur(g, passes=2):
    """Separable blur of a (12, H, W) stack: wraps in longitude, clamps in latitude, light in time.
    Two spatial passes give a smooth surface (about 2 cells, 300 km)."""
    out = g
    for _ in range(passes):
        out = sum(K[i] * np.roll(out, i - 2, axis=2) for i in range(5))
        pad = np.pad(out, ((0, 0), (2, 2), (0, 0)), mode="edge")
        out = sum(K[i] * pad[:, i:i + H, :] for i in range(5))
    return 0.2 * np.roll(out, 1, axis=0) + 0.6 * out + 0.2 * np.roll(out, -1, axis=0)


def main():
    credits = json.load(open(os.path.join(OUT, "photos", "credits.json")))
    effort = {g: blur(np.load(os.path.join(GRID, f"{k}.npy"))) for g, k in EFFORT.items()
              if os.path.exists(os.path.join(GRID, f"{k}.npy"))}
    meta = []
    for s in SPECIES:
        if s["effort"] not in effort or not os.path.exists(os.path.join(GRID, f"{s['key']}.npy")):
            print(f"skipping {s['slug']}: grids not downloaded yet")
            continue
        raw = np.load(os.path.join(GRID, f"{s['key']}.npy"))
        sp = blur(raw)
        ef = effort[s["effort"]]
        valid = ef >= MIN_EFFORT[s["effort"]]
        rate = np.where(valid & (sp >= 1.0), sp / (ef + DAMP[s["effort"]]), 0.0)  # ignore spots from one or two records
        rate = np.clip(rate, 0, 1)
        # set the top of the scale from well recorded places only
        pos = rate[(rate > 0) & (ef >= 4 * DAMP[s["effort"]])]
        vmax = float(np.percentile(pos, 99.5)) if pos.size else 1.0
        q = np.clip(rate / vmax, 0, 1) ** GAMMA

        atlas = np.zeros((512, 1024, 3), np.uint8)
        for m in range(12):
            r, c = divmod(m, 4)
            atlas[r * H:(r + 1) * H, c * W:(c + 1) * W, 0] = np.round(q[m] * 255)
            atlas[r * H:(r + 1) * H, c * W:(c + 1) * W, 1] = valid[m] * 255
        Image.fromarray(atlas, "RGB").save(os.path.join(OUT, f"{s['slug']}.png"), optimize=True)

        # latitude wave: share of each month's population by latitude band (2 cells = 2.8 deg)
        lin = np.clip(rate / vmax, 0, 1) * AREA
        prof = lin.sum(axis=2).reshape(12, H // 2, 2).sum(axis=2)
        # each month on its own scale, so the strip shows where the population is
        # rather than how busy observers were that month
        prof = prof / np.maximum(prof.max(axis=1, keepdims=True), 1e-12)

        # population centre per flyway, only in months where that flyway holds a real share
        trails = []
        for name, lo, hi in FLYWAYS:
            cols = (LON >= lo) & (LON < hi)
            wgt = lin[:, :, cols] ** 1.5
            tot = wgt.sum(axis=(1, 2))
            share = tot.sum() / max((lin ** 1.5).sum(), 1e-12)
            if "flyways" in s and name not in s["flyways"]:
                continue
            if tot.max() <= 0 or share < MIN_FLYWAY:
                continue
            pts = []
            for m in range(12):
                if tot[m] < 0.12 * tot.max():
                    pts.append(None); continue
                la = float((wgt[m].sum(axis=1) * LAT).sum() / tot[m])
                lo_ = float((wgt[m].sum(axis=0) * LON[cols]).sum() / tot[m])
                pts.append([round(lo_, 2), round(la, 2)])
            if sum(p is not None for p in pts) >= 6:
                trails.append({"name": name, "points": pts})

        records = int(raw.sum())
        meta.append({
            **{k: s[k] for k in ("slug", "name", "sci", "journey", "effort")},
            "vmax": vmax,
            "records": records,
            "monthly": [int(v) for v in raw.sum(axis=(1, 2))],
            "wave": [[int(round(v * 100)) for v in row] for row in prof],
            "trails": trails,
            "credit": credits.get(s["slug"]),
        })
        print(f"{s['slug']:26s} vmax {vmax * 100:6.2f}%  records {records:>10,}  trails {[t['name'] for t in trails]}")
    json.dump({"years": YEARS.replace(",", " to "), "grid": [W, H], "gamma": GAMMA, "species": meta},
              open(os.path.join(OUT, "atlas.json"), "w"), separators=(",", ":"))


if __name__ == "__main__":
    main()
