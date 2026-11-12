# 1) OpenCelliD cells (MCC 648) near Masvingo -> estimated tower sites (cells merged by complete linkage, no two cells of a site more than 500 m apart).
# 2) WorldPop 2020 constrained on the 90 m grid rescaled to ZimStat 2022 census district totals (dasymetric), Masvingo districts.
import json, numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.features import rasterize
from sklearn.cluster import AgglomerativeClustering
g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]; R = g["res"]; W, H = (x1 - x0) // R, (y1 - y0) // R
tr = rasterio.transform.from_origin(x0, y1, R, R)
prov = gpd.read_file("data/masvingo.geojson")
c = pd.read_csv("data/648.csv.gz", header=None, names=["radio", "mcc", "net", "area", "cell", "unit", "lon", "lat", "range",
                                                    "samples", "changeable", "created", "updated", "avgSignal"])
c = gpd.GeoDataFrame(c, geometry=gpd.points_from_xy(c.lon, c.lat), crs=4326).to_crs(32736)
c["x"], c["y"] = c.geometry.x, c.geometry.y
c = c[(c.x > x0) & (c.x < x1) & (c.y > y0) & (c.y < y1)].copy()
c["inprov"] = c.within(prov.union_all())
c["site"] = AgglomerativeClustering(n_clusters=None, linkage="complete", distance_threshold=500).fit_predict(c[["x", "y"]].values)
c["w"] = c.samples.clip(lower=1)
s = c.groupby("site").apply(lambda d: pd.Series(dict(
    x=np.average(d.x, weights=d.w), y=np.average(d.y, weights=d.w), cells=len(d), samples=int(d.samples.sum()),
    gsm=int((d.radio == "GSM").any()), umts=int((d.radio == "UMTS").any()), lte=int((d.radio == "LTE").any()),
    nets="".join(sorted(set(d.net.astype(str)))))), include_groups=False).reset_index()
s = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s.x, s.y), crs=32736)
s["inprov"] = s.within(prov.union_all())
r = rasterio.open("rast/dem.tif"); dem = r.read(1)
s["elev"] = [dem[int((y1 - yy) // R), int((xx - x0) // R)] for xx, yy in zip(s.x, s.y)]
s.to_file("data/sites.gpkg"); c.drop(columns="geometry").to_csv("data/cells_masvingo.csv", index=False)
print("cells in grid", len(c), "in province", int(c.inprov.sum()), "| sites", len(s), "in province", int(s.inprov.sum()))
print(c[c.inprov].radio.value_counts().to_dict(), c[c.inprov].net.value_counts().to_dict())
print("sites in prov by tech", s[s.inprov][["gsm", "umts", "lte"]].sum().to_dict())

# population
d = gpd.read_file("../population/data/districts.gpkg"); d = d[d.province == "Masvingo"].to_crs(32736).reset_index(drop=True)
d[["district", "pop2022", "area_km2", "geometry"]].to_file("data/districts.gpkg")
lab = rasterize([(geom, i + 1) for i, geom in enumerate(d.geometry)], (H, W), transform=tr, dtype="int16")
wp = rasterio.open("rast/wpc2020.tif").read(1); wp[~np.isfinite(wp) | (wp < 0)] = 0
pop = np.zeros_like(wp)
for i, row in d.iterrows():
    m = lab == i + 1; k = row.pop2022 / wp[m].sum(); pop[m] = wp[m] * k
    print(f"{row.district:16s} census {row.pop2022:>8} worldpop {wp[m].sum():>10.0f} ratio {k:.3f}")
prof = dict(driver="GTiff", width=W, height=H, count=1, crs="EPSG:32736", transform=tr, compress="deflate")
with rasterio.open("rast/pop2022.tif", "w", dtype="float32", **prof) as o: o.write(pop.astype("float32"), 1)
with rasterio.open("rast/district.tif", "w", dtype="int16", **prof) as o: o.write(lab, 1)
print("pop total", round(pop.sum()), "dem", np.nanmin(dem), np.nanmax(dem))
