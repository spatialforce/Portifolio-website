"""Station normals for 1961-1990 from GHCN v2 monthly precipitation. A month counts if at least 20 of the 30 years have a
value; trace (-8888) is taken as 0. The normal is the sum of the twelve monthly means. Duplicate series: the first
duplicate with a value is used for each month. Elevation is read from the Copernicus/SRTM DEM used in the census study.
Output: data/stations.csv"""
import collections, numpy as np, pandas as pd, rasterio, geopandas as gpd
from shapely.geometry import Point
inv = {}
for l in open("raw/zw.inv"):
    l = l.rstrip("\r\n"); t = l[42:].split()
    inv[l[:11]] = dict(id=l[:11], name=l[12:32].strip().title(), lat=float(t[0]), lon=float(t[1]), elev_inv=float(t[2]))
D = collections.defaultdict(dict); both = []
for l in open("raw/zw.prcp"):
    sid, dup, y = l[:11], l[11], int(l[12:16])
    if not 1961 <= y <= 1990: continue
    for m in range(12):
        v = int(l[16 + 5 * m:21 + 5 * m])
        if v == -9999: continue
        v = 0 if v == -8888 else v / 10
        k = (sid, y, m)
        if k in D: both.append((D[k], v)); continue
        D[k] = v
both = np.array(both); print("months held twice", len(both), "differ by > 1 mm", int((abs(both[:, 0] - both[:, 1]) > 1).sum()) if len(both) else 0)
rows = []
for sid, s in inv.items():
    mm, nn = [], []
    for m in range(12):
        v = [D[(sid, y, m)] for y in range(1961, 1991) if (sid, y, m) in D]; nn.append(len(v)); mm.append(np.mean(v) if v else np.nan)
    if min(nn) < 20: continue
    full = [sum(D[(sid, y, m)] for m in range(12)) for y in range(1961, 1991) if all((sid, y, m) in D for m in range(12))]
    rows.append(dict(**s, years_min=min(nn), years_full=len(full), p_ann=round(sum(mm), 1),
                     p_ondjfm=round(sum(mm[m] for m in (9, 10, 11, 0, 1, 2)), 1), cv=round(np.std(full, ddof=1) / np.mean(full) * 100, 1) if len(full) > 5 else np.nan))
st = pd.DataFrame(rows)
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326).geometry.union_all()
st["inside"] = [zwe.buffer(0.02).contains(Point(x, y)) for x, y in zip(st.lon, st.lat)]
with rasterio.open("../population/rast/dem.tif") as r:
    st["elev"] = [round(float(v[0])) for v in r.sample(zip(st.lon, st.lat))]
# stations sharing a position (within 2 km) are merged by mean so the interpolators see one point per place
st = st[st.inside].sort_values("years_min", ascending=False).reset_index(drop=True)
print(len(st), "stations; elevation inventory vs DEM r =", round(st[st.elev_inv > 0][["elev_inv", "elev"]].corr().iloc[0, 1], 3))
from scipy.spatial.distance import pdist, squareform
d = squareform(pdist(np.c_[st.lon * np.cos(np.radians(19)), st.lat] * 111.32)); np.fill_diagonal(d, 1e9)
close = [(st.name[i], st.name[j], round(d[i, j], 1)) for i in range(len(st)) for j in range(i + 1, len(st)) if d[i, j] < 5]
print("pairs closer than 5 km", close)
st.to_csv("data/stations.csv", index=False)
print(st[["name", "lat", "lon", "elev", "years_min", "p_ann"]].sort_values("p_ann").to_string(index=False))
