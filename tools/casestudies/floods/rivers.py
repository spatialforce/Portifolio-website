import ee, json, geopandas as gpd; ee.Initialize()
R = ee.FeatureCollection("WWF/HydroSHEDS/v1/FreeFlowingRivers")
out = []
for k, bb, up in [("muz", [30.6, -16.7, 32.0, -15.6], 500), ("save", [31.9, -21.5, 33.0, -19.6], 1000)]:
    f = R.filterBounds(ee.Geometry.Rectangle(bb)).filter(ee.Filter.gt("UPLAND_SKM", up)).select(["UPLAND_SKM", "DIS_AV_CMS", "RIV_ORD"])
    g = gpd.GeoDataFrame.from_features(f.getInfo()["features"], crs=4326); g["aoi"] = k; out.append(g)
    print(k, len(g), g.UPLAND_SKM.max())
import pandas as pd
gpd.GeoDataFrame(pd.concat(out), crs=4326).to_file("data/hydrorivers.gpkg")
