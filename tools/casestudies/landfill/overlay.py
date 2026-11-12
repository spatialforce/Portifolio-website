# Factor scores (1 to 5), AHP weighted overlay inside the open land, suitability classes, candidate sites.
import json
from shapely.geometry import Polygon
import numpy as np, rasterio, geopandas as gpd
from scipy.ndimage import label
from shapely.geometry import shape
from rasterio.features import shapes, rasterize
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ahp import A, CRITERIA, weights_cr

def rd(n): return rasterio.open(f"rast/{n}.tif").read(1)
src = rasterio.open("rast/lc.tif"); PROF = dict(src.profile, compress="deflate", nodata=None)
def save(n, a, dt): 
    with rasterio.open(f"rast/{n}.tif", "w", **dict(PROF, dtype=dt)) as d: d.write(a.astype(dt), 1)
def cls(a, br, rev=False):  # breaks ascending -> 1..5 (rev: low values score high)
    c = np.digitize(a, br) + 1; return (6 - c) if rev else c

city, mask = rd("city") == 1, rd("mask") == 1
dw = np.minimum(rd("d_river"), rd("d_water"))
lc = rd("lc")
F = {"Distance from settlements": cls(rd("d_sett"), [750, 1000, 1500, 2000]),
     "Distance from surface water": cls(dw, [500, 750, 1000, 1500]),
     "Soil clay": cls(rd("clay"), [18, 21, 24, 27]),
     "Slope": cls(rd("slope"), [2, 5, 10, 15], rev=True),
     "Distance to roads": cls(rd("d_road"), [500, 1000, 2000, 3000], rev=True),
     "Land cover": np.select([np.isin(lc, [60, 30]), lc == 20, lc == 40, lc == 10], [5, 4, 3, 1], 1)}
for i, k in enumerate(F): save(f"f{i}", F[k], "uint8")
w, lam, CI, CR = weights_cr(A)
S = sum(wi * F[k] for wi, k in zip(w, CRITERIA)).astype("float32")
save("score", np.where(city, S, 0), "float32")
cl = cls(S, [2.5, 3.0, 3.5, 4.0])  # 1 very low .. 5 very high
cl = np.where(city, cl, 0)
save("suit", cl, "uint8")

# candidate sites: connected patches of high and very high land >= 50 ha
lab, n = label(cl >= 4, structure=np.ones((3, 3)))
ha = np.bincount(lab.ravel()) * 0.09
keep = [i for i in range(1, n + 1) if ha[i] >= 50]
rows = []
for i in keep:
    m = lab == i; rows.append(dict(id=i, ha=float(round(ha[i], 1)), score=float(round(S[m].mean(), 2)),
         sett_km=float(round(rd("d_sett")[m].mean() / 1000, 2)), road_km=float(round(rd("d_road")[m].mean() / 1000, 2)), air_km=float(round(rd("d_air")[m].min() / 1000, 2)),
         geometry=Polygon(max((shape(g) for g, v in shapes(m.astype("uint8"), mask=m, transform=src.transform) if v == 1), key=lambda p: p.area).exterior).buffer(30).buffer(-30)))
sites = gpd.GeoDataFrame(rows, crs=32735).sort_values("score", ascending=False).head(4).reset_index(drop=True)
sites["site"] = [chr(65 + i) for i in range(len(sites))]
sites.to_file("out/sites.gpkg")

# validation at the existing landfills: Richmond (UN-Habitat 2022 coordinate, 30 ha reported size) and the unnamed OSM landfill in the east
lf = json.load(open("data/osm_landfill.json"))[0]["geometry"]
from shapely.geometry import Polygon, Point
from pyproj import Transformer
rx, ry = Transformer.from_crs(4326, 32735, always_xy=True).transform(28 + 32 / 60, -(20 + 5 / 60))
lfp = gpd.GeoDataFrame(dict(name=["Richmond", "Eastern"]), crs=32735, geometry=[Point(rx, ry).buffer((300000 / np.pi) ** 0.5),
      gpd.GeoSeries([Polygon([(q["lon"], q["lat"]) for q in lf])], crs=4326).to_crs(32735).iloc[0]])
lfp.to_file("out/landfill.gpkg")
LFS = []
for nm, g in zip(lfp.name, lfp.geometry):
    lfm = rasterize([g], out_shape=S.shape, transform=src.transform) == 1
    LFS.append(dict(name=nm, ha=float(round(lfm.sum() * 0.09, 1)), score=float(round(S[lfm].mean(), 2)), excluded_pct=float(round(100 * (~mask[lfm]).mean(), 1)),
                    d_sett=float(round(rd("d_sett")[lfm].mean())), d_water=float(round(dw[lfm].mean()))))
area = {c: float(round(((cl == c) & city).sum() * 0.0009, 1)) for c in range(1, 6)}
open_area = {c: float(round(((cl == c) & mask).sum() * 0.0009, 1)) for c in range(1, 6)}
out = dict(weights={k: float(round(x, 3)) for k, x in zip(CRITERIA, w)}, lam=float(round(lam, 3)), CI=float(round(CI, 4)), CR=float(round(CR, 4)),
           class_km2=area, open_class_km2=open_area, excluded_km2=float(round((city & ~mask).sum() * 0.0009, 1)),
           landfills=LFS,
           sites=sites.drop(columns="geometry").to_dict("records"))
out = json.loads(json.dumps(out), parse_float=lambda s: round(float(s), 3))
json.dump(out, open("out/results.json", "w"), indent=1); print(json.dumps(out))
