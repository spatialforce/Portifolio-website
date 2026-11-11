"""Growing cities: built-up surface 1975 to 2020 for ten African cities, from the GHSL
(JRC/GHSL/P2023A/GHS_BUILT_S, 100 m) through Google Earth Engine.

Every city gets the same 80 x 80 km window on its own equal area grid (Lambert azimuthal,
centred on the city), so the maps share one scale. 2025 and 2030 are left out: in this
release they are modelled projections, not observations.

Per city, written to public/webmaps/cities/<slug>.png (800 x 800):
  R  epoch in which the cell first had at least 5% of its area built (1 = 1975 ... 10 = 2020), 0 never
  G  share of the cell built in 2020, 0 to 255
and cities.json with the built-up area (cells at least 5% built) and the built surface, km2, for every epoch.
    python build.py
"""
import io
import json
import os

import ee
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "cities")
EPOCHS = list(range(1975, 2021, 5))
HALF, RES = 40000, 100              # metres
N = 2 * HALF // RES
MIN_BUILT = 500                     # m2 of a 10 000 m2 cell, 5%

CITIES = [
    ("harare", "Harare", "Zimbabwe", -17.829, 31.053),
    ("lusaka", "Lusaka", "Zambia", -15.417, 28.283),
    ("nairobi", "Nairobi", "Kenya", -1.286, 36.817),
    ("dar-es-salaam", "Dar es Salaam", "Tanzania", -6.82, 39.24),
    ("addis-ababa", "Addis Ababa", "Ethiopia", 9.01, 38.76),
    ("kinshasa", "Kinshasa", "DR Congo", -4.38, 15.33),
    ("luanda", "Luanda", "Angola", -8.92, 13.27),
    ("lagos", "Lagos", "Nigeria", 6.55, 3.38),
    ("cairo", "Cairo", "Egypt", 30.05, 31.24),
    ("johannesburg", "Johannesburg", "South Africa", -26.15, 28.05),
]


def window(lat, lon):
    wkt = (f'PROJCS["laea",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],'
           f'UNIT["degree",0.0174532925199433]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["latitude_of_center",{lat}],'
           f'PARAMETER["longitude_of_center",{lon}],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1]]')
    ic = ee.ImageCollection("JRC/GHSL/P2023A/GHS_BUILT_S").select("built_surface")
    img = ee.ImageCollection([ic.filter(ee.Filter.eq("system:index", str(y))).first().rename(f"b{y}") for y in EPOCHS]).toBands()
    img = img.rename([f"b{y}" for y in EPOCHS]).unmask(0)
    raw = ee.data.computePixels({
        "expression": img, "fileFormat": "NPY",
        "grid": {"dimensions": {"width": N, "height": N},
                 "affineTransform": {"scaleX": RES, "shearX": 0, "translateX": -HALF, "shearY": 0, "scaleY": -RES, "translateY": HALF},
                 "crsWkt": wkt},
    })
    arr = np.load(io.BytesIO(raw))
    return np.stack([arr[f"b{y}"].astype(np.float32) for y in EPOCHS])   # epochs x N x N, m2 built per cell


def main():
    ee.Initialize(project="directed-sun-490915-m4")
    os.makedirs(OUT, exist_ok=True)
    meta = []
    for slug, name, country, lat, lon in CITIES:
        s = window(lat, lon)
        built = s >= MIN_BUILT
        first = np.where(built.any(0), built.argmax(0) + 1, 0).astype(np.uint8)
        dens = np.clip(s[-1] / 10000 * 255, 0, 255).astype(np.uint8)
        Image.fromarray(np.dstack([first, dens, np.zeros_like(first)]), "RGB").save(os.path.join(OUT, f"{slug}.png"), optimize=True)
        surface = [round(float(v) / 1e6, 1) for v in s.sum((1, 2))]
        # built-up area: land in cells that are at least 5% built (each cell is 0.01 km2)
        area = [round(float((built[k]).sum()) * RES * RES / 1e6) for k in range(len(EPOCHS))]
        meta.append({"slug": slug, "name": name, "country": country, "area": area, "surface": surface})
        print(f"{name:14s} built-up area {area[0]:5d} km2 in 1975 -> {area[-1]:5d} in 2020  (x{area[-1] / max(area[0], 1):.1f})")
    json.dump({"epochs": EPOCHS, "window_km": 2 * HALF // 1000, "cities": meta},
              open(os.path.join(OUT, "cities.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
