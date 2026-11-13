# RUSLE A = R K LS C P on the 30 m grid (t/ha/yr).
# R: Renard and Freimund (1994), R = 0.0483 P^1.61 for P < 850 mm (MJ mm/ha/h/yr), P = CHIRPS 1991-2020 mean.
# K: Williams (1995) EPIC equation from iSDAsoil sand, silt, clay and organic carbon (0-20 cm), x 0.1317 to SI.
# LS: Moore and Burch (1986) from flow accumulation (pysheds) and slope, slope length capped at 300 m.
# C: van der Knijff et al. (2000), C = exp(-2 NDVI / (1 - NDVI)), Sentinel-2 NDVI median of Dec to Mar, 2019/20 to 2023/24.
# P: Wischmeier and Smith (1978) contouring values on cropland by slope, 1 elsewhere.
import json, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
np.in1d = np.isin
from pysheds.grid import Grid

def rd(n): return rasterio.open(f"rast/{n}.tif").read(1).astype("float64")
src = rasterio.open("rast/dem.tif"); PROF = dict(src.profile, dtype="float32", nodata=None, compress="deflate")
def save(n, a):
    with rasterio.open(f"rast/{n}.tif", "w", **PROF) as d: d.write(a.astype("float32"), 1)

P = rd("rain"); R = 0.0483 * P ** 1.61
from scipy.ndimage import distance_transform_edt
def fill(a):   # iSDAsoil masks rock and water cells (-inf): take the nearest valid cell
    bad = ~np.isfinite(a); i = distance_transform_edt(bad, return_distances=False, return_indices=True); return a[tuple(i)]
san, sil, cla = fill(rd("sand")), fill(rd("silt")), fill(rd("clay")); oc = (np.exp(fill(rd("oc_raw")) / 10) - 1) / 10   # g/kg -> %
NOSOIL = int((~np.isfinite(rd("sand"))).sum())
sn1 = 1 - san / 100
K = ((0.2 + 0.3 * np.exp(-0.256 * san * (1 - sil / 100))) * (sil / np.maximum(cla + sil, 1)) ** 0.3
     * (1 - 0.25 * oc / (oc + np.exp(3.72 - 2.95 * oc))) * (1 - 0.7 * sn1 / (sn1 + np.exp(-5.51 + 22.9 * sn1)))) * 0.1317

g = Grid.from_raster("rast/dem.tif"); r = g.read_raster("rast/dem.tif")
f = g.resolve_flats(g.fill_depressions(g.fill_pits(r)))
acc = np.asarray(g.accumulation(g.flowdir(f)), "float64")
dem = rd("dem"); gy, gx = np.gradient(dem, 30); beta = np.arctan(np.hypot(gx, gy))
LS = (np.minimum(acc * 30, 300) / 22.13) ** 0.4 * (np.sin(beta) / 0.0896) ** 1.3

nd = np.clip(rd("ndvi_wet"), -1, 0.95)   # rainy-season cover (Dec to Mar), when erosive rain falls
C = np.clip(np.exp(-2 * nd / (1 - nd)), 0, 1)
lc = rd("lc"); C[np.isin(lc, [50, 80])] = 0          # built-up and open water: no soil loss
s = np.tan(beta) * 100
Pf = np.where(lc == 40, np.select([s < 2, s < 8, s < 12, s < 16, s < 20], [0.6, 0.5, 0.6, 0.7, 0.8], 0.9), 1.0)

A = R * K * LS * C * Pf
for n, a in dict(R=R, K=K, LS=LS, C=C, P=Pf, A=A, slope=s, acc=acc).items(): save(n, a)

b = gpd.read_file("data/chivi.gpkg")
dist = rasterize(b.geometry, out_shape=A.shape, transform=src.transform) == 1
land = dist & ~np.isin(lc, [80])
save("dist", dist)
q = lambda a: [float(round(v, 3)) for v in np.percentile(a[land], [1, 25, 50, 75, 99])]
out = dict(R=q(R), K=q(K), LS=q(LS), C=q(C), P=q(Pf), A=q(A), A_mean=float(round(A[land].mean(), 2)),
           rain=q(P), nosoil_cells=NOSOIL, oc_pct=q(oc), slope=q(s))
json.dump(out, open("out/factors.json", "w"), indent=1); print(json.dumps(out))
