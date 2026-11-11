"""Saharan dust web map build.

MERRA-2 hourly aerosol (NASA/GSFC/MERRA/aer/2) from Earth Engine, every 3 hours:
  DUEXTTAU  dust optical depth at 550 nm (whole air column)
  DUFLUXU/V dust mass flux (kg m-1 s-1); divided by DUCMASS (kg m-2) it gives the
            speed and direction the dust itself is carried (m/s)
Writes public/webmaps/dust/<event>.png (frame atlas, R = optical depth, G/B = transport
velocity) and public/webmaps/dust/dust.json.
"""
import json, math, os, sys, datetime as dt
import numpy as np
import ee
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(HERE, "cache"); os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(ROOT, "public", "webmaps", "dust"); os.makedirs(OUT, exist_ok=True)

# MERRA-2 grid: lon centres -180 + i*0.625, lat centres -90 + j*0.5
LON0, LON1, LAT0, LAT1 = -100.0, 60.0, -5.0, 60.0
DX, DY = 0.625, 0.5
W = int(round((LON1 - LON0) / DX)) + 1
H = int(round((LAT1 - LAT0) / DY)) + 1
HOURS = list(range(0, 24, 3))
AOD_MAX = 4.0     # optical depth stored 0..4 on a square root scale
VMAX = 30.0       # transport speed stored -30..30 m/s

EVENTS = [
    ("jul2026", "2026-06-29", "2026-07-15"),
    ("mar2026", "2026-02-28", "2026-03-11"),
    # id, start (UTC), end (UTC, exclusive)
    ("jun2020", "2020-06-12", "2020-06-29"),
    ("mar2022", "2022-03-12", "2022-03-21"),
    ("feb2021", "2021-02-02", "2021-02-11"),
]


def day_stack(day):
    path = os.path.join(CACHE, day + ".npy")
    if os.path.exists(path):
        return np.load(path)
    t0 = ee.Date(day)
    col = ee.ImageCollection("NASA/GSFC/MERRA/aer/2").filterDate(t0, t0.advance(1, "day"))
    bands = []
    for h in HOURS:
        im = col.filterDate(t0.advance(h, "hour"), t0.advance(h + 1, "hour")).first()
        bands.append(im.select(["DUEXTTAU", "DUFLUXU", "DUFLUXV", "DUCMASS"],
                               [f"a{h}", f"u{h}", f"v{h}", f"m{h}"]))
    img = ee.Image.cat(bands).toFloat()
    arr = ee.data.computePixels({
        "expression": img, "fileFormat": "NUMPY_NDARRAY",
        "grid": {"dimensions": {"width": W, "height": H}, "crsCode": "EPSG:4326",
                 "affineTransform": {"scaleX": DX, "shearX": 0, "translateX": LON0 - DX / 2,
                                     "shearY": 0, "scaleY": -DY, "translateY": LAT1 + DY / 2}}})
    out = np.stack([np.stack([arr[f"{k}{h}"] for k in "auvm"]) for h in HOURS]).astype(np.float32)
    np.save(path, out)   # (8 frames, 4 vars, H, W), row 0 = north
    return out


def land():
    from shapely.geometry import shape, box, mapping
    from shapely.ops import unary_union
    g = json.load(open(os.path.join(ROOT, "tools", "rift", "raw", "ne_10m_land.geojson"), encoding="utf-8"))
    clip = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
    geoms = [shape(f["geometry"]).intersection(clip) for f in g["features"]]
    u = unary_union([x for x in geoms if not x.is_empty]).simplify(0.06)
    rings = []
    for p in getattr(u, "geoms", [u]):
        if p.area < 0.15:
            continue
        rings.append([[round(x, 2), round(y, 2)] for x, y in p.exterior.coords])
    return rings


def main():
    ee.Initialize(project="directed-sun-490915-m4")
    meta = {"box": [LON0, LAT0, LON1, LAT1], "w": W, "h": H, "dx": DX, "dy": DY,
            "aodMax": AOD_MAX, "vmax": VMAX, "hours": HOURS, "events": []}
    for eid, a, b in EVENTS:
        d0, d1 = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
        days = [(d0 + dt.timedelta(n)).isoformat() for n in range((d1 - d0).days)]
        frames = []
        for d in days:
            print(eid, d, flush=True)
            frames.append(day_stack(d))
        F = np.concatenate(frames)               # (n, 4, H, W)
        aod, fu, fv, cm = F[:, 0], F[:, 1], F[:, 2], F[:, 3]
        safe = np.maximum(cm, 1e-7)
        u = np.clip(np.where(cm > 1e-6, fu / safe, 0), -VMAX, VMAX)
        v = np.clip(np.where(cm > 1e-6, fv / safe, 0), -VMAX, VMAX)
        n = F.shape[0]
        cols = 8
        rows = math.ceil(n / cols)
        A = np.zeros((rows * H, cols * W), np.uint8)
        hw, hh = (W + 1) // 2, (H + 1) // 2
        V = np.zeros((rows * hh, cols * hw, 3), np.uint8)
        R = np.round(np.sqrt(np.clip(aod, 0, AOD_MAX) / AOD_MAX) * 255)
        for i in range(n):
            r, c = divmod(i, cols)
            A[r * H:(r + 1) * H, c * W:(c + 1) * W] = R[i]
            # velocity on every second cell, whole m/s, 128 = still
            V[r * hh:(r + 1) * hh, c * hw:(c + 1) * hw, 0] = np.round(u[i, ::2, ::2]) + 128
            V[r * hh:(r + 1) * hh, c * hw:(c + 1) * hw, 1] = np.round(v[i, ::2, ::2]) + 128
        Image.fromarray(A, "L").save(os.path.join(OUT, eid + "_a.png"), optimize=True)
        Image.fromarray(V).save(os.path.join(OUT, eid + "_v.png"), optimize=True)
        meta["events"].append({"id": eid, "start": a, "frames": n, "cols": cols, "peak": round(float(aod.max()), 2)})
        # checks: daily max optical depth in a few boxes
        def boxmax(lo0, lo1, la0, la1):
            i0, i1 = int((lo0 - LON0) / DX), int((lo1 - LON0) / DX)
            j0, j1 = int((LAT1 - la1) / DY), int((LAT1 - la0) / DY)
            return aod[:, j0:j1, i0:i1].reshape(len(days), 8, -1).max(axis=(1, 2))
        for nm, bx in [("Caribbean", (-90, -58, 10, 25)), ("Iberia", (-10, 4, 36, 44)), ("Alps", (5, 15, 44, 48)), ("UK", (-6, 2, 50, 56))]:
            print(" ", nm, " ".join(f"{x:.1f}" for x in boxmax(*bx)))
    meta["land"] = land()
    json.dump(meta, open(os.path.join(OUT, "dust.json"), "w"), separators=(",", ":"))
    print("done", W, H)


if __name__ == "__main__":
    main()
