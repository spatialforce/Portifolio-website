"""Download flood conditioning factors for Chimanimani District on one 30 m UTM 36S grid (2 x 2 tiles per layer)."""
import os, io, zipfile, urllib.request, ee
from concurrent.futures import ThreadPoolExecutor
ee.Initialize(project="directed-sun-490915-m4")
os.makedirs("rast", exist_ok=True)

# grid: EPSG:32736, 30 m, covering the district box (lon 32.34 to 33.07, lat -20.12 to -19.36)
X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834   # x 430 to 508 km, y 7775 to 7860 km
print("grid", X0, X0 + W * RES, Y0 - H * RES, Y0)

dem = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM").mosaic().setDefaultProjection("EPSG:4326", None, 30)
merit = ee.Image("MERIT/Hydro/v1_0_1")
gpm = ee.ImageCollection("NASA/GPM_L3/IMERG_V07").filterDate("2019-03-14", "2019-03-20").select("precipitation")
rain = gpm.sum().multiply(0.5).setDefaultProjection(gpm.first().projection())                       # mm/hr half-hourly -> mm (14 to 19 March 2019)
chd = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate("2019-03-14", "2019-03-20")
chirps = chd.sum().setDefaultProjection(chd.first().projection())   # keep native grids or bilinear runs on 1 degree
lulc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS") \
    .filterDate("2018-01-01", "2018-12-31").mosaic()  # pre-cyclone land cover (2018)
clay = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select("b0")
sand = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select("b0")
LAY = {"rain": rain.toFloat(), "chirps": chirps.toFloat(), "lulc": lulc.toFloat(), "clay": clay.toFloat(),
       "sand": sand.toFloat()}
NN = {"lulc"}   # categorical: nearest neighbour (default); others bilinear
TW, TH = W // 2, H // 2


def job(a):
    name, i, j = a
    f = f"rast/{name}_{i}{j}.tif"
    if os.path.exists(f): return
    img = LAY[name] if name in NN else LAY[name].resample("bilinear")
    tr = [RES, 0, X0 + i * TW * RES, 0, -RES, Y0 - j * TH * RES]
    for k in range(4):
        try:
            u = img.getDownloadURL({"crs": "EPSG:32736", "crs_transform": tr, "dimensions": f"{TW}x{TH}",
                                    "format": "GEO_TIFF"})
            b = urllib.request.urlopen(u, timeout=600).read()
            if b[:2] == b"PK": b = zipfile.ZipFile(io.BytesIO(b)).read(zipfile.ZipFile(io.BytesIO(b)).namelist()[0])
            open(f + ".part", "wb").write(b); os.replace(f + ".part", f); print("ok", f, flush=True); return
        except Exception as e:
            err = e
    print("FAILED", f, err, flush=True)


jobs = [(n, i, j) for n in LAY for i in range(2) for j in range(2)]
with ThreadPoolExecutor(3) as ex: list(ex.map(job, jobs))
print("done")
