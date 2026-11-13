# Esri World Imagery tiles over the 6 x 4.5 km window with the densest gully-prone flow paths (for Map 5 and a visual check).
import numpy as np, rasterio, contextily as ctx, json
from scipy import ndimage as nd
from pyproj import Transformer
g = rasterio.open("rast/gully.tif"); T = g.transform; a = g.read(1).astype(float); d = rasterio.open("rast/dist.tif").read(1) == 1
s = nd.uniform_filter(a, 160); s[~nd.binary_erosion(d, iterations=120)] = 0
r, c = np.unravel_index(np.argmax(s), s.shape); x, y = T.c + c * 30, T.f - r * 30
ext = (x - 3000, x + 3000, y - 2250, y + 2250)
F = Transformer.from_crs(32736, 4326, always_xy=True); w, so = F.transform(ext[0], ext[2]); e, n = F.transform(ext[1], ext[3])
img, bb = ctx.bounds2img(w, so, e, n, zoom=16, source=ctx.providers.Esri.WorldImagery, ll=True)
img, bb = ctx.warp_tiles(img, bb, t_crs="EPSG:32736")
np.savez_compressed("rast/esri.npz", img=img, ext=np.array(bb), win=np.array(ext)); print("centre", F.transform(x, y), img.shape)
