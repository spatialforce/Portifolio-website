"""Clip the Mazowe River (OSM relation 2638607) to Zimbabwe, orient it source to border,
cut it into 10 km reaches and build a 1 km corridor polygon for each reach (UTM 36S)."""
import geopandas as gpd
from shapely.ops import linemerge, substring
from shapely.geometry import LineString

UTM = "EPSG:32736"
d = gpd.read_file("../population/data/districts.gpkg")
zw = d.dissolve().to_crs(UTM).geometry.iloc[0]
r = gpd.read_file("data/mazowe_river.geojson").to_crs(UTM).geometry.iloc[0]
line = linemerge(r) if r.geom_type == "MultiLineString" else r
if line.geom_type == "MultiLineString":
    line = max(line.geoms, key=lambda g: g.length)
line = line.intersection(zw)
if line.geom_type == "MultiLineString":
    line = linemerge(line)
    if line.geom_type == "MultiLineString":
        line = max(line.geoms, key=lambda g: g.length)
# source is the western end (near Harare)
if line.coords[0][0] > line.coords[-1][0]:
    line = LineString(list(line.coords)[::-1])
L = line.length
print("main stem in Zimbabwe km", round(L / 1000, 1))
rows = []
k = 0
while k * 10000 < L:
    seg = substring(line, k * 10000, min((k + 1) * 10000, L))
    rows.append({"reach": k + 1, "km_from": k * 10, "km_to": round(min((k + 1) * 10000, L) / 1000, 1),
                 "geometry": seg})
    k += 1
seg = gpd.GeoDataFrame(rows, crs=UTM)
cor = seg.copy()
cor["geometry"] = seg.buffer(1000, cap_style=2).intersection(zw)
# remove overlaps: each later reach loses what earlier reaches already hold
taken = None
for i in cor.index:
    g = cor.at[i, "geometry"]
    if taken is not None:
        g = g.difference(taken)
    cor.at[i, "geometry"] = g
    taken = g if taken is None else taken.union(g)
cor["area_ha"] = cor.area / 1e4
# district of each reach (by majority length)
dd = d.to_crs(UTM)
def dist(g):
    best = max(dd.itertuples(), key=lambda t: g.intersection(t.geometry).length)
    return best.district
seg["district"] = seg.geometry.apply(dist)
cor["district"] = seg["district"]
seg.to_file("data/reaches_line.gpkg")
cor.to_file("data/reaches_corridor.gpkg")
gpd.GeoDataFrame(geometry=[line], crs=UTM).to_file("data/mainstem.gpkg")
print(len(seg), "reaches; corridor ha", round(cor.area_ha.sum(), 1))
print(seg[["reach", "km_from", "km_to", "district"]].to_string(index=False))
