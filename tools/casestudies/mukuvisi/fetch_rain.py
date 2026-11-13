"""CHIRPS v2.0 daily rainfall (0.05 degrees) for a small window over Harare, rainy-season days only
(1 October to 30 April, seasons 1981/82 to 2024/25). Each daily COG is read by HTTP range request.
Output: raw/chirps.npz (dates, cell centres, mm per day)."""
import os, sys, datetime as dt, numpy as np, rasterio
from rasterio.windows import from_bounds
from concurrent.futures import ThreadPoolExecutor
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".cog", GDAL_HTTP_MAX_RETRY="4",
                  GDAL_HTTP_RETRY_DELAY="5", VSI_CACHE="FALSE")
B = (30.80, -18.10, 31.35, -17.65)
URL = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v2.0/global_daily/cogs/p05/{y}/chirps-v2.0.{y}.{m:02d}.{d:02d}.cog"
days = []
for s in range(1981, 2025):
    d = dt.date(s, 10, 1)
    while d <= dt.date(s + 1, 4, 30): days.append(d); d += dt.timedelta(days=1)
out = "raw/chirps_parts"; os.makedirs(out, exist_ok=True)


def one(d):
    f = f"{out}/{d.isoformat()}.npy"
    if os.path.exists(f): return
    for a in range(4):
        try:
            with rasterio.open(URL.format(y=d.year, m=d.month, d=d.day)) as s:
                w = from_bounds(*B, s.transform); np.save(f, s.read(1, window=w).astype("float32")); return
        except Exception as e:
            err = e; import time; time.sleep(5 * (a + 1))
    print("fail", d, str(err)[:100], flush=True)


with ThreadPoolExecutor(4) as ex:
    for i, _ in enumerate(ex.map(one, days)):
        if i % 500 == 0: print(i, len(days), flush=True)
import time
for a in range(10):
    try:
        with rasterio.open(URL.format(y=2020, m=1, d=1)) as s:
            w = from_bounds(*B, s.transform); T = s.window_transform(w)
        break
    except Exception: time.sleep(30)
got = [d for d in days if os.path.exists(f"{out}/{d.isoformat()}.npy")]
A = np.stack([np.load(f"{out}/{d.isoformat()}.npy") for d in got])
xs = T.c + (np.arange(A.shape[2]) + 0.5) * T.a; ys = T.f + (np.arange(A.shape[1]) + 0.5) * T.e
np.savez_compressed("raw/chirps.npz", dates=np.array([d.isoformat() for d in got]), x=xs, y=ys, p=A)
print("saved", A.shape, "missing", len(days) - len(got))
