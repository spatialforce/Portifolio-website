# Mean GEDI L4A AGBD of the footprints in each 1 km cell (EPSG:32735), for Map 2. Empty cells stay NaN.
import glob, numpy as np, pandas as pd, rasterio
from pyproj import Transformer
df = pd.concat([pd.read_csv(f, usecols=["agbd", "longitude", "latitude"]) for f in sorted(glob.glob("data/gedi_*.csv"))])
df = df[(df.agbd >= 0) & (df.agbd <= 200)]
x, y = Transformer.from_crs(4326, 32735, always_xy=True).transform(df.longitude.values, df.latitude.values)
R = 1000; X0, Y1 = np.floor(x.min() / R) * R, np.ceil(y.max() / R) * R
c, r = ((x - X0) // R).astype(int), ((Y1 - y) // R).astype(int); W, H = c.max() + 1, r.max() + 1
sm = np.bincount(r * W + c, df.agbd.values, W * H); n = np.bincount(r * W + c, minlength=W * H)
a = np.where(n > 0, sm / np.maximum(n, 1), np.nan).reshape(H, W).astype("float32")
with rasterio.open("out/gedi_1km.tif", "w", driver="GTiff", width=W, height=H, count=1, dtype="float32", crs="EPSG:32735",
                   transform=rasterio.transform.from_origin(X0, Y1, R, R)) as o: o.write(a, 1)
print("cells with footprints", int((n > 0).sum()))
