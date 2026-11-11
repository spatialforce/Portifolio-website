import ee; ee.Initialize()
AOI = {"muz": ee.Geometry.Rectangle([30.85, -16.55, 31.75, -16.0]), "save": ee.Geometry.Rectangle([32.25, -21.35, 32.75, -19.9])}
for k, g in AOI.items():
    c = ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(g).filter(ee.Filter.eq("instrumentMode", "IW")).filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
    ys = c.aggregate_histogram("system:index").size()
    d = c.map(lambda i: i.set("y", i.date().format("YYYY"), "o", ee.Number(i.get("relativeOrbitNumber_start")).format("%d")))
    print(k, d.aggregate_histogram("y").getInfo(), d.aggregate_histogram("o").getInfo())
