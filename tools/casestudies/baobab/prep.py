"""Clean and thin the baobab records, put every predictor on the CHELSA 30 arc-sec grid inside Zimbabwe.
Writes data/records.csv, data/stack.npz (layers + mask + transform) and prints the cleaning counts and correlations."""
import os, json
import numpy as np, pandas as pd, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
os.makedirs("data", exist_ok=True)
V = ["bio1", "bio4", "bio5", "bio6", "bio9", "bio11", "bio12", "bio15", "bio17"]

with rasterio.open("raw/bio1.tif") as s: T, H, W, CRS = s.transform, s.height, s.width, s.crs
L = {}
for v in V:
    with rasterio.open(f"raw/{v}.tif") as s: L[v] = s.read(1)
dem = np.zeros((H, W), "float32")
with rasterio.open("raw/dem500.tif") as s:
    reproject(rasterio.band(s, 1), dem, dst_transform=T, dst_crs=CRS, resampling=Resampling.average)
L["elev"] = dem
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326)
M = rasterize(zwe.geometry, (H, W), transform=T, fill=0, default_value=1).astype(bool)
lakes = gpd.read_file("zip://../../corridors/raw/ne_10m_lakes.zip").to_crs(4326).cx[25:33.2, -22.6:-15.5]
print("lakes", lakes.name.tolist())
M &= ~rasterize(lakes.geometry, (H, W), transform=T, fill=0, default_value=1).astype(bool)
for v in L: M &= np.isfinite(L[v])

# records
d = pd.read_csv("raw/gbif_ZW.csv"); n0 = len(d); log = {"gbif": n0}
d = d[~d.issues.fillna("").str.contains("ZERO_COORDINATE|COUNTRY_COORDINATE_MISMATCH|COORDINATE_INVALID")]
d = d[d.coordinateUncertaintyInMeters.isna() | (d.coordinateUncertaintyInMeters <= 5000)]; log["uncert_le_5km"] = len(d)
d = d.drop_duplicates(["decimalLongitude", "decimalLatitude"]); log["unique_xy"] = len(d)
r, c = rasterio.transform.rowcol(T, d.decimalLongitude.values, d.decimalLatitude.values); r, c = np.array(r), np.array(c)
ok = (r >= 0) & (r < H) & (c >= 0) & (c < W); ok[ok] = M[r[ok], c[ok]]; d = d[ok]; r, c = r[ok], c[ok]; log["inside"] = len(d)
d = d.assign(r=r, c=c).drop_duplicates(["r", "c"]); log["one_per_1km"] = len(d)
# spatial thinning to one record per 10 km cell (12 x 12 grid cells) to reduce clustering around visited sites
g = (d.r // 12) * 10000 + d.c // 12; d = d.loc[~g.duplicated()]; log["one_per_10km"] = len(d)
for v in L: d[v] = L[v][d.r, d.c]
d.to_csv("data/records.csv", index=False)
np.savez_compressed("data/stack.npz", mask=M, transform=np.array(T)[:6], **{v: L[v] for v in L})
json.dump(log, open("data/cleaning.json", "w"), indent=1); print(log)
# correlation of predictors at 20 000 random land cells
rng = np.random.default_rng(1); idx = rng.choice(M.sum(), 20000, replace=False)
X = pd.DataFrame({v: L[v][M][idx] for v in L}); print(X.corr().round(2).to_string())
print(d[["elev", "bio6", "bio12"]].describe().round(1).to_string())
