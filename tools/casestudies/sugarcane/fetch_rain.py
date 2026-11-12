# CHIRPS monthly rainfall over the estates (mean of the box), Jan 2019 to Dec 2025
import ee, json
ee.Initialize(project="directed-sun-490915-m4")
R = ee.Geometry.Rectangle([31.33, -21.19, 31.80, -20.93])
c = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD").filterDate("2018-07-01", "2026-01-01")
out = {}
for y in range(2018, 2026):
    for m in range(1, 13):
        if y == 2018 and m < 7: continue
        d = ee.Date.fromYMD(y, m, 1)
        out[f"{y}-{m:02d}"] = c.filterDate(d, d.advance(1, "month")).sum()
fc = ee.FeatureCollection([ee.Feature(None, {"m": k, "mm": v.reduceRegion(ee.Reducer.mean(), R, 5566).get("precipitation")}) for k, v in out.items()])
res = {f["properties"]["m"]: round(f["properties"]["mm"], 1) for f in fc.getInfo()["features"]}
json.dump(res, open("data/rain_monthly.json", "w"), indent=0); print(len(res), list(res.items())[-14:])
