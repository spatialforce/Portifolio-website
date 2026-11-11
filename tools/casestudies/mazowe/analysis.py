"""Bare ground and river turbidity along the Mazowe River corridor (Earth Engine).
Bare ground: median wet-season (Nov-Apr) NDVI < 0.3 over three rainy seasons (bare at the height of the rains), not water
(annual median MNDWI > 0) and not built up (ESA WorldCover 2021 class 50).
Turbidity: NDTI = (red - green) / (red + green) on Sentinel-2 water pixels, April to July."""
import json, sys
import ee, geopandas as gpd, pandas as pd
ee.Initialize()

cor = gpd.read_file("data/reaches_corridor.gpkg").to_crs(4326)
lines = gpd.read_file("data/reaches_line.gpkg").to_crs(4326)
def fc(g):
    return ee.FeatureCollection([ee.Feature(ee.Geometry(json.loads(gpd.GeoSeries([r.geometry]).to_json())["features"][0]["geometry"]),
                                            {"reach": int(r.reach)}) for r in g.itertuples()])
COR = fc(cor)
BG = fc(gpd.read_file("data/reaches_background.gpkg").to_crs(4326))
AOI = COR.geometry().bounds()
built = ee.Image("ESA/WorldCover/v200/2021").select("Map").eq(50)

def scale_l(i, sensor):
    qa = i.select("QA_PIXEL")
    m = qa.bitwiseAnd(0b11010).eq(0)          # fill, dilated cloud, cloud, shadow
    if sensor == "oli":
        b = i.select(["SR_B3", "SR_B4", "SR_B5", "SR_B6"], ["g", "r", "n", "s"])
    else:
        b = i.select(["SR_B2", "SR_B3", "SR_B4", "SR_B5"], ["g", "r", "n", "s"])
    b = b.multiply(0.0000275).add(-0.2)
    return b.addBands(b.normalizedDifference(["n", "r"]).rename("ndvi")) \
            .addBands(b.normalizedDifference(["g", "s"]).rename("mndwi")).updateMask(m)

def landsat(year, seasons=3):
    """Wet-season (November to April) scenes of the `seasons` rainy seasons centred on `year`
    (season named by the year it ends in)."""
    cols = []
    if year >= 2014:
        cols += [("LANDSAT/LC08/C02/T1_L2", "oli"), ("LANDSAT/LC09/C02/T1_L2", "oli")]
    else:
        cols += [("LANDSAT/LT05/C02/T1_L2", "tm"), ("LANDSAT/LE07/C02/T1_L2", "tm")]
    h = seasons // 2
    d0, d1 = f"{year - h - 1}-11-01", f"{year + h}-04-30"
    out = None
    for cid, s in cols:
        c = ee.ImageCollection(cid).filterBounds(AOI).filterDate(d0, d1)               .filter(ee.Filter.calendarRange(5, 10, "month").Not()).map(lambda i, s=s: scale_l(i, s))
        out = c if out is None else out.merge(c)
    return out

def bare(year, seasons=3):
    c = landsat(year, seasons)
    md = c.select("ndvi").median()
    wet = c.select("mndwi").median().gt(0)
    b = md.lt(0.3).And(wet.Not()).And(built.Not())
    return b.rename("bare").selfMask(), c.size()

def stats(year, seasons=3, zone=None):
    b, n = bare(year, seasons)
    r = b.multiply(ee.Image.pixelArea()).divide(1e4).reduceRegions(zone or COR, ee.Reducer.sum(), 30)
    return {f["properties"]["reach"]: f["properties"].get("sum", 0) for f in r.getInfo()["features"]}, n.getInfo()

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "reaches":
        out = {}
        for y in [2000, 2009, 2017, 2025]:
            s, n = stats(y); out[y] = s; print(y, "scenes", n, "bare ha", round(sum(s.values()), 1), flush=True)
        df = pd.DataFrame(out); df.index.name = "reach"; df.to_csv("data/bare_by_reach.csv")
    elif what == "background":
        out = {}
        for y in [2000, 2009, 2017, 2025]:
            s, n = stats(y, zone=BG); out[y] = s; print(y, round(sum(s.values()), 1), flush=True)
        df = pd.DataFrame(out); df.index.name = "reach"; df.to_csv("data/bare_background.csv")
    elif what == "annual":
        rows = []
        for y in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
            s, n = stats(y, 1); rows.append({"year": y, "scenes": n, "bare_ha": sum(s.values())}); print(rows[-1], flush=True)
        pd.DataFrame(rows).to_csv(f"data/bare_annual_{sys.argv[2]}_{sys.argv[3]}.csv", index=False)
