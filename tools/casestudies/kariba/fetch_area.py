"""Lake Kariba water area, dry-season low (Oct to Dec) and wet-season high (Apr to Jun), 2000 to 2025.

Landsat 5, 7, 8 and 9 surface reflectance, cloud masked, MNDWI > 0 is water. Clouds and the Landsat 7
stripes leave gaps, so the area is filled with JRC surface-water occurrence (Zhao and Gao 2018): the
occurrence level that best splits the observed water and land pixels is found, and the lake area is the
area of all pixels at or above that level. Output: data/area.csv
"""
import ee, csv, os, sys
ee.Initialize(project="directed-sun-490915-m4")
os.makedirs("data", exist_ok=True)
BOX = ee.Geometry.Rectangle([26.6, -18.2, 29.0, -16.35])
GSW = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
OCC = GSW.select("occurrence").unmask(0).updateMask(GSW.select("max_extent"))
SC = 90


def prep(img, sat):
    qa = img.select("QA_PIXEL")
    ok = qa.bitwiseAnd(0b11111).eq(0)   # fill, dilated cloud, cirrus, cloud, shadow
    if sat in ("L8", "L9"): g, s = "SR_B3", "SR_B6"
    else: g, s = "SR_B2", "SR_B5"
    b = img.select([g, s]).multiply(0.0000275).add(-0.2)
    return b.normalizedDifference([g, s]).rename("mndwi").updateMask(ok)


def coll(a, b):
    out = None
    for sat, cid in (("L5", "LANDSAT/LT05/C02/T1_L2"), ("L7", "LANDSAT/LE07/C02/T1_L2"),
                     ("L8", "LANDSAT/LC08/C02/T1_L2"), ("L9", "LANDSAT/LC09/C02/T1_L2")):
        c = ee.ImageCollection(cid).filterBounds(BOX).filterDate(a, b).map(lambda i, s=sat: prep(i, s))
        out = c if out is None else out.merge(c)
    return out


# area (km2) of each occurrence level 0..100 inside the maximum extent, done once
AREA_OCC = ee.Image.pixelArea().divide(1e6).addBands(OCC.int().rename("occ")).reduceRegion(
    ee.Reducer.sum().group(1, "occ"), BOX, SC, maxPixels=1e10).get("groups")


def window(a, b):
    m = coll(a, b).median()
    w = m.gt(0)
    h = OCC.int().addBands(w.rename("w")).updateMask(m.mask()).reduceRegion(
        ee.Reducer.frequencyHistogram().group(1, "w"), BOX, SC, maxPixels=1e10).get("groups")
    return h


if __name__ == "__main__":
    import json
    ao = {int(g["occ"]): g["sum"] for g in AREA_OCC.getInfo()}
    json.dump(ao, open("data/area_by_occ.json", "w"))
    years = range(int(sys.argv[1]), int(sys.argv[2]) + 1) if len(sys.argv) > 2 else range(2000, 2026)
    f = "data/area.csv"; new = not os.path.exists(f)
    with open(f, "a", newline="") as fh:
        wr = csv.writer(fh)
        if new: wr.writerow(["year", "season", "t", "area_km2", "observed_share", "error_share"])
        for y in years:
            for season, a, b in (("high", f"{y}-04-01", f"{y}-07-01"), ("low", f"{y}-10-01", f"{y + 1}-01-01")):
                hist = {int(g["w"]): {int(k): v for k, v in g["histogram"].items()} for g in window(a, b).getInfo()}
                land, wat = hist.get(0, {}), hist.get(1, {})
                nobs = sum(land.values()) + sum(wat.values()); ntot = sum(ao.values()) / (SC * SC / 1e6)
                best = min(range(1, 101), key=lambda t: sum(v for k, v in wat.items() if k < t) + sum(v for k, v in land.items() if k >= t))
                err = (sum(v for k, v in wat.items() if k < best) + sum(v for k, v in land.items() if k >= best)) / max(nobs, 1)
                area = sum(v for k, v in ao.items() if k >= best)
                wr.writerow([y, season, best, round(area, 1), round(nobs / ntot, 3), round(err, 4)]); fh.flush()
                print(y, season, best, round(area), round(nobs / ntot, 2), round(err, 3), flush=True)
