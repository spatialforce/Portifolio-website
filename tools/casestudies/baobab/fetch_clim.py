"""Clip CHELSA V2.1 bioclim (1981-2010, 30 arc-sec) to Zimbabwe's window. Writes raw/bioN.tif in real units."""
import rasterio, numpy as np, sys
from rasterio.windows import from_bounds
B = (25.0, -22.6, 33.2, -15.5)
U = "/vsicurl/https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_{v}_1981-2010_V.2.1.tif"
for v in sys.argv[1:]:
    with rasterio.open(U.format(v=v)) as s:
        w = from_bounds(*B, s.transform); a = s.read(1, window=w).astype("float32") * s.scales[0] + s.offsets[0]
        p = s.profile; p.update(driver="GTiff", dtype="float32", width=a.shape[1], height=a.shape[0], transform=s.window_transform(w), compress="deflate", tiled=False, blockxsize=None, blockysize=None)
        p.pop("blockxsize"); p.pop("blockysize")
    with rasterio.open(f"raw/{v}.tif", "w", **p) as d: d.write(a, 1)
    print(v, round(float(a.min()), 1), round(float(a.max()), 1))
