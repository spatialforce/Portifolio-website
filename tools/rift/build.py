"""East African Rift in 3D: terrain, rift lakes, Holocene volcanoes and GPS motion relative to Nubia.

    python build.py

Sources (raw files in tools/rift/raw, tiles cached in tools/rift/cache):
- Terrain: Terrain Tiles (Terrarium, AWS open data: SRTM, GMTED2010, ETOPO1), zoom 8.
- Water: Natural Earth 10m land and lakes.
- Volcanoes: Smithsonian Global Volcanism Program, Volcanoes of the World, Holocene list (WFS).
- GPS: Nevada Geodetic Laboratory MIDAS velocities in IGS20 (gps_timeseries/IGS20/midas/midas.IGS.txt).
  Velocities are made relative to the Nubian plate with an Euler vector fitted here to stations on stable Nubia.
- Plate boundaries: Bird (2003) PB2002.

public/webmaps/rift/height.png  terrain height on a lat/lon grid, metres + 1000 in R (high byte) and G (low byte).
public/webmaps/rift/ground.jpg  hypsometric tint with hillshade and water, 2 x the height grid.
public/webmaps/rift/rift.json   extent, grid, volcanoes, GPS vectors, plate boundary, lake labels, Euler vector.
"""
import io
import json
import math
import os
import urllib.request

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "rift")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

W0, E0, S0, N0 = 27.0, 45.0, -16.0, 15.0  # extent
STEP = 0.025                               # height grid, about 2.8 km
TSTEP = STEP / 2                           # ground picture
VOLCANIC = {"CURG", "CNHG", "DA60", "DABT"}
Z = 8                                      # terrain tile zoom (about 0.6 km a pixel)

# rift lakes to label: Natural Earth name, label
LAKES = [("Lake Tanganyika", "Tanganyika"), ("Lake Malawi", "Malawi"), ("Lake Turkana", "Turkana"),
         ("Lake Albert", "Albert"), ("Lake Edward", "Edward"), ("Lake Kivu", "Kivu"), ("Lake Rukwa", "Rukwa"),
         ("Lake Abaya", "Abaya"), ("Lake Natron", "Natron"), ("Lake Chamo", "Chamo"), ("Lake Ziway", "Ziway"),
         ("Lake Baringo", "Baringo"), ("Lake Eyasi", "Eyasi"), ("Lake Manyara", "Manyara"), ("Lake Abbe", "Abbe")]


# ---------- terrain ----------
def tile(x, y):
    p = os.path.join(CACHE, f"{Z}_{x}_{y}.png")
    if not os.path.exists(p):
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png"
        with urllib.request.urlopen(url, timeout=60) as r, open(p, "wb") as f:
            f.write(r.read())
    a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
    return a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def merc(lon, lat):
    n = 2 ** Z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def terrain(step):
    x0, y0 = merc(W0, N0)
    x1, y1 = merc(E0, S0)
    tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1), int(y1)
    mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256))
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = tile(tx, ty)
    lons = W0 + step / 2 + np.arange(round((E0 - W0) / step)) * step
    lats = N0 - step / 2 - np.arange(round((N0 - S0) / step)) * step
    LO, LA = np.meshgrid(lons, lats)
    n = 2 ** Z
    px = ((LO + 180) / 360 * n - tx0) * 256 - 0.5
    py = ((1 - np.log(np.tan(np.radians(LA)) + 1 / np.cos(np.radians(LA))) / np.pi) / 2 * n - ty0) * 256 - 0.5
    return map_coordinates(mosaic, [py, px], order=1, mode="nearest")


def rasterize(path, w, h, step, keep=None):
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        if keep and not keep(f["properties"]):
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            for k, ring in enumerate(poly):
                pts = [((lo - W0) / step, (N0 - la) / step) for lo, la in ring]
                if len(pts) > 2:
                    d.polygon(pts, fill=0 if k else 1)
    return np.asarray(img) > 0


def hillshade(z, step, az=315, alt=45, exag=6):
    dy = step * 111320
    gy, gx = np.gradient(z * exag, dy, dy)  # rows run south, so gy is the southward slope
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gy, gx)  # angle of the downhill direction from east, counter clockwise
    a, h = math.radians(90 - az), math.radians(alt)
    s = np.sin(h) * np.cos(slope) + np.cos(h) * np.sin(slope) * np.cos(a - aspect + math.pi)
    return np.clip(s, 0, 1)


# Wikipedia topographic map convention, land tints
TINT = [(0, "ACD0A5"), (50, "94BF8B"), (200, "A8C68F"), (500, "BDCC96"), (800, "D1D7AB"), (1200, "E1E4B5"),
        (1600, "EFEBC0"), (2000, "E8E1B6"), (2500, "DED6A3"), (3000, "D3CA9D"), (3500, "CAB982"),
        (4000, "C3A76B"), (4500, "B9985A"), (5000, "AA8753"), (5600, "BAAE9A")]
SEA, LAKE = (0x9F, 0xC6, 0xE2), (0x6E, 0xA6, 0xD3)


def tint(z):
    xs = [t for t, _ in TINT]
    cs = np.array([[int(c[i:i + 2], 16) for i in (0, 2, 4)] for _, c in TINT], dtype=np.float64)
    return np.stack([np.interp(z, xs, cs[:, i]) for i in range(3)], -1)


def build_ground():
    z = terrain(TSTEP)
    h, w = z.shape
    land = rasterize(os.path.join(RAW, "ne_10m_land.geojson"), w, h, TSTEP)
    lake = rasterize(os.path.join(RAW, "ne_10m_lakes.geojson"), w, h, TSTEP)
    sea = ~land
    shade = hillshade(np.where(sea, 0, z), TSTEP)
    col = tint(np.clip(z, -200, 6000)) * (0.45 + 0.75 * shade[..., None])
    col = np.clip(col, 0, 255)
    col[lake] = LAKE
    col[sea] = SEA
    Image.fromarray(col.astype(np.uint8)).save(os.path.join(OUT, "ground.jpg"), quality=88, optimize=True)
    return z, land, lake


def build_height(z2, land2, lake2):
    # height grid = 2 x 2 means of the picture grid, so mesh and picture line up
    h, w = z2.shape[0] // 2, z2.shape[1] // 2
    blk = lambda a: a[:h * 2, :w * 2].reshape(h, 2, w, 2).mean((1, 3))
    z = blk(z2)
    sea = blk((~land2).astype(float)) > 0.5
    z[sea] = 0
    z = np.maximum(z, -160)  # lowest dry land is Lake Assal at -155 m; deeper values are sea floor in the gulf
    # lakes flat at their surface: median height inside each connected lake
    from scipy.ndimage import label
    lk = blk(lake2.astype(float)) > 0.5
    lab, n = label(lk)
    for i in range(1, n + 1):
        m = lab == i
        z[m] = np.median(z[m])
    v = np.clip(np.round(z) + 1000, 0, 65535).astype(np.uint16)
    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[..., 0], rgb[..., 1] = v >> 8, v & 255
    Image.fromarray(rgb).save(os.path.join(OUT, "height.png"), optimize=True)
    return z, w, h


# ---------- volcanoes ----------
def volcanoes():
    out = []
    for f in json.load(open(os.path.join(RAW, "gvp.json"), encoding="utf-8"))["features"]:
        p = f["properties"]
        lo, la = f["geometry"]["coordinates"][:2]
        if not (W0 <= lo <= E0 and S0 <= la <= N0):
            continue
        out.append({"name": p["Volcano_Name"], "lon": round(lo, 3), "lat": round(la, 3), "type": p.get("Primary_Volcano_Type"),
                    "elev": p.get("Elevation"), "last": p.get("Last_Eruption_Year"), "country": p.get("Country")})
    return sorted(out, key=lambda v: -(v["elev"] or 0))


# ---------- GPS ----------
R = 6371000.0
MAS = math.radians(1 / 3.6e6)  # milliarcseconds to radians


def enu_basis(lon, lat):
    lo, la = math.radians(lon), math.radians(lat)
    e = np.array([-math.sin(lo), math.cos(lo), 0])
    n = np.array([-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)])
    r = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)]) * R
    return e, n, r


def gps():
    rows = []
    for line in open(os.path.join(RAW, "midas.txt")):
        s = line.split()
        if len(s) < 27:
            continue
        dur = float(s[4])
        ve, vn = float(s[8]) * 1000, float(s[9]) * 1000  # mm/yr
        se, sn = float(s[11]) * 1000, float(s[12]) * 1000
        lat, lon = float(s[24]), (float(s[25]) + 180) % 360 - 180
        if dur >= 2.5 and se < 1.5 and sn < 1.5:
            rows.append((s[0], lon, lat, ve, vn, se, sn, dur))

    # stable Nubia: west and south of the rift, away from plate edges
    def stable(lon, lat):
        return (-18 <= lon <= 26 and -35 <= lat <= 14) and not (lon > 24 and lat > -12)
    use = [r for r in rows if stable(r[1], r[2])]
    while True:  # fit, drop the worst station while any residual is over 1.5 mm/yr, refit
        A, b = [], []
        for _, lon, lat, ve, vn, *_ in use:
            e, n, r = enu_basis(lon, lat)
            # v = w x r ; v_e = e . (w x r) = w . (r x e)
            A += [np.cross(r, e) * MAS * 1000, np.cross(r, n) * MAS * 1000]  # mas/yr to mm/yr
            b += [ve, vn]
        A, b = np.array(A), np.array(b)
        w = np.linalg.lstsq(A, b, rcond=None)[0]
        res = (b - A @ w).reshape(-1, 2)
        r2 = np.hypot(res[:, 0], res[:, 1])
        if r2.max() < 1.5:
            break
        use.pop(int(r2.argmax()))
    rms = float(np.sqrt(((b - A @ w) ** 2).mean()))

    out = []
    for name, lon, lat, ve, vn, se, sn, dur in rows:
        if not (W0 <= lon <= E0 and S0 <= lat <= N0):
            continue
        e, n, r = enu_basis(lon, lat)
        pe, pn = w @ (np.cross(r, e) * MAS * 1000), w @ (np.cross(r, n) * MAS * 1000)
        out.append({"id": name, "lon": round(lon, 3), "lat": round(lat, 3), "ve": round(ve - pe, 2), "vn": round(vn - pn, 2),
                    "se": round(se, 2), "sn": round(sn, 2), "yrs": round(dur, 1)})
    return out, {"wx": round(float(w[0]), 4), "wy": round(float(w[1]), 4), "wz": round(float(w[2]), 4), "stations": len(use), "rms": round(rms, 2)}


def boundaries():
    lines = []
    for f in json.load(open(os.path.join(RAW, "pb.json"), encoding="utf-8"))["features"]:
        g = f["geometry"]
        parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for p in parts:
            seg, cur = [], []
            for lo, la in p:
                if W0 - 1 <= lo <= E0 + 1 and S0 - 1 <= la <= N0 + 1:
                    cur.append([round(lo, 3), round(la, 3)])
                elif cur:
                    seg.append(cur); cur = []
            if cur:
                seg.append(cur)
            lines += [s for s in seg if len(s) > 1]
    return lines


def lake_labels():
    want = {a: b for a, b in LAKES}
    out = []
    for f in json.load(open(os.path.join(RAW, "ne_10m_lakes.geojson"), encoding="utf-8"))["features"]:
        nm = f["properties"].get("name") or ""
        if nm not in want:
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        ring = max((p[0] for p in polys), key=len)
        a = np.array(ring)
        out.append({"name": want.pop(nm), "lon": round(float(a[:, 0].mean()), 3), "lat": round(float(a[:, 1].mean()), 3)})
    if want:
        print("lakes not found:", ", ".join(want))
    return out


if __name__ == "__main__":
    z2, land2, lake2 = build_ground()
    z, w, h = build_height(z2, land2, lake2)
    v = volcanoes()
    g, euler = gps()
    # stations that record magma moving, not plate motion: Corbetti caldera uplift (CURG, CNHG) and the
    # Dabbahu-Manda Hararo dyke intrusions of 2005 to 2010 (DA60, DABT)
    for st in g:
        st["volcanic"] = st["id"] in VOLCANIC
    print("volcanic:", [s["id"] for s in g if s["volcanic"]])
    meta = {"extent": [W0, S0, E0, N0], "w": w, "h": h, "step": STEP, "maxElev": int(z.max()), "minElev": int(z.min()),
            "volcanoes": v, "gps": g, "euler": euler, "boundary": boundaries(), "lakes": lake_labels()}
    json.dump(meta, open(os.path.join(OUT, "rift.json"), "w"), separators=(",", ":"))
    print(f"grid {w}x{h}, elev {z.min():.0f} to {z.max():.0f} m, volcanoes {len(v)}, gps {len(g)}, euler {euler}")
