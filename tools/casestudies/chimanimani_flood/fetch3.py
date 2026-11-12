"""Long-term mean annual rainfall (CHIRPS daily, 1991 to 2020) on the same 30 m UTM 36S grid as fetch.py."""
import os, io, zipfile, urllib.request, ee
from concurrent.futures import ThreadPoolExecutor
ee.Initialize(project="directed-sun-490915-m4")
X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834
TW, TH = W // 2, H // 2
c = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate("1991-01-01", "2021-01-01")
ann = c.sum().divide(30).setDefaultProjection(c.first().projection()).toFloat().resample("bilinear")

def job(a):
    i, j = a; f = f"rast/annrain_{i}{j}.tif"
    if os.path.exists(f): return
    tr = [RES, 0, X0 + i * TW * RES, 0, -RES, Y0 - j * TH * RES]
    for k in range(4):
        try:
            u = ann.getDownloadURL({"crs": "EPSG:32736", "crs_transform": tr, "dimensions": f"{TW}x{TH}", "format": "GEO_TIFF"})
            b = urllib.request.urlopen(u, timeout=600).read()
            if b[:2] == b"PK": z = zipfile.ZipFile(io.BytesIO(b)); b = z.read(z.namelist()[0])
            open(f, "wb").write(b); print("ok", f, flush=True); return
        except Exception as e: err = e
    print("FAILED", f, err, flush=True)
with ThreadPoolExecutor(2) as ex: list(ex.map(job, [(i, j) for i in range(2) for j in range(2)]))
