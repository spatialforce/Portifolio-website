# Feasibility probe: annual mean S5P NO2 and SO2 at Hwange power station vs a background ring.
import ee; ee.Initialize(project="directed-sun-490915-m4")
hps = ee.Geometry.Point([26.468, -18.383])
near = hps.buffer(15000); ring = hps.buffer(150000).difference(hps.buffer(80000))
def m(col, band, y):
    im = ee.ImageCollection(col).select(band).filterDate(f"{y}-01-01", f"{y+1}-01-01").mean()
    r = lambda g: im.reduceRegion(ee.Reducer.mean(), g, 1113.2).get(band)
    return ee.Dictionary({"near": r(near), "bg": r(ring)})
for y in range(2019, 2026):
    n = m("COPERNICUS/S5P/OFFL/L3_NO2", "tropospheric_NO2_column_number_density", y).getInfo()
    s = m("COPERNICUS/S5P/OFFL/L3_SO2", "SO2_column_number_density", y).getInfo()
    print(y, "NO2 umol/m2 near %.1f bg %.1f" % (n["near"]*1e6, n["bg"]*1e6), "| SO2 near %.1f bg %.1f" % (s["near"]*1e6, s["bg"]*1e6))
