# Quick look: Sentinel-2 true colour and NDVI over the Hippo Valley / Triangle estates (dry season 2024)
import ee, urllib.request
ee.Initialize(project="directed-sun-490915-m4")
R = ee.Geometry.Rectangle([31.30, -21.20, 31.85, -20.80])
def mask(i):
    s = i.select("SCL"); return i.updateMask(s.neq(3).And(s.neq(8)).And(s.neq(9)).And(s.neq(10))).divide(10000)
c = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(R).filterDate("2024-08-01","2024-10-01").filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",20)).map(mask)
print("images", c.size().getInfo())
m = c.median()
u = m.select(["B4","B3","B2"]).getThumbURL({"region":R,"dimensions":1400,"min":0.02,"max":0.25,"format":"jpg"})
urllib.request.urlretrieve(u, "data/look_rgb.jpg")
nd = m.normalizedDifference(["B8","B4"])
u = nd.getThumbURL({"region":R,"dimensions":1400,"min":0,"max":0.9,"palette":["ffffff","ccbb88","77aa44","115511"],"format":"jpg"})
urllib.request.urlretrieve(u, "data/look_ndvi.jpg"); print("ok")
