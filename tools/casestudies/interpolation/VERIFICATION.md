# Verification: rainfall interpolation (IDW, kriging, thin-plate spline)

Every figure on the page comes from `data/interp.json`, `data/check.json`, `data/map5.json`, `data/fig4.json`,
`data/loocv.csv`, `data/points.csv` and `data/surfaces.npz`. Rerun order: `fetch.py` → `stations.py` → `interp.py` →
`check.py` → `maps.py` (set PROJ_LIB/PROJ_DATA from `.projlib`). Distances in LAEA (lat_0 −19, lon_0 29.8, km); grid
0.025°. Images: `out/*.png` → webp (max 2 000 px, q 92) in scratchpad `clean/` → `tools/provenance/grain.py` →
`src/assets/casestudies/rainfall-interpolation/` → `tag_images.py`.

## Data
| Item | Source | Checked |
|---|---|---|
| Rain gauges | GHCN-Monthly v2 precipitation (NOAA NCEI), Zimbabwe lines; 1961–1990 normals, ≥ 20 years per month | `raw/zw.*`, `stations.csv` (68) |
| Merged gauges | same location to 2 dp: Harare 809.8/818.7, Mutare 761.1/796.5, Mvuma 686.6/691.2 → 65 points | `points.csv` |
| Elevation | inventory value, else Copernicus DEM GLO-30 (500 m) | `points.csv` |
| Check surface | CHIRPS v2.0 monthly climatology, 12 bands summed (`../rainfall/rast/monthly_clim.tif`; later period) | `check.py` |
| National mean | FAO AQUASTAT 657 mm/yr | `check.json` |
| Admin | OCHA COD-AB Zimbabwe; Natural Earth | `maps.py` |

## Figures on the page
| Page item | Value | Where |
|---|---|---|
| Gauges | 65; 20–30 years (median 28); 421–1 830 m | `points.csv` |
| Rainfall | 333.2 (Beitbridge) – 1 631.4 (Inyanga Downs); mean 725.8, median 739.3, SD 194.0, CV 26.7 % | `stations` |
| Spacing | nearest neighbour median 33.2, mean 41.7, max 128.1 km (Gwaai) | `nn_km` |
| Correlations | elevation 0.59, longitude 0.597, latitude 0.555; slope 36.7 mm/100 m | `stations`, `fig4.json` |
| Moran's I | 0.235 (E −0.016, p 0.0001, 9 999 perms) | `moran` |
| Trend | 692.94 + 0.5795x + 0.5879y, R² 0.567; variance 37 074 → 16 045 | `trend` |
| Variograms | OK exponential nugget 0, sill 35 315, range 400 (at bound); UK spherical 471.3 / 14 684.7 / 123.3 km | `vario` |
| Tuning (Table 2) | IDW p 2.5 (RMSE 123.0); OK exp 116.9; UK sph 116.2; TPS smoothing 30 | `tuning` |
| Table 4 (LOOCV) | ME / MAE / RMSE / R²: IDW 10.6/71.4/123.0/0.592; OK 4.4/64.7/116.9/0.631; UK 4.8/68.9/116.2/0.636; TPS 4.9/67.6/116.6/0.633 | `cv` |
| Without Inyanga Downs | RMSE IDW 95.2, OK 85.3, UK 89.0, TPS 94.5 | `cv_no_outlier` |
| Dense / sparse MAE | split at median spacing; IDW 70.7/72.1, OK 65.4/63.9, UK 66.7/71.1, TPS 64.2/71.2 | `cv_sparse` |
| Closest method | IDW 19, OK 19, UK 14, TPS 13 | `closest_method_count` |
| Table 3 (surfaces) | means 697.2 / 688.9 / 688.9 / 683.3; TPS max 1 824.5 | `surface` |
| Map 4 | spread mean 57.2, median 36.4; < 50 mm 60.0 %, 50–100 23.0 %, ≥ 100 17.0 % | `spread` |
| Map 5 | UK SE 36.4–135.4, mean 97.7 (OK 109.5); Low 16.1, Moderate 38.3, High 45.6 % | `map5.json` |
| Table 5 (checks) | CHIRPS mean 645.6; r 0.824/0.835/0.781/0.796; mean diff +51.7/+43.3/+43.4/+37.7 | `check.json` |
| Gauges vs CHIRPS | r 0.97, CHIRPS 22.1 mm lower | `check.json` |

## Published comparison
FAO AQUASTAT long-term mean 657 mm; surfaces give 683–697 mm (4–6 % higher). Gauge networks sit mostly on the wetter
plateau, which fits the positive bias against CHIRPS.

## Not used / caveats
- Normals are 1961–1990 (the last period with dense GHCN v2 cover); CHIRPS covers 1981 onwards, so only pattern and level are compared.
- Raw-value variogram has no clear sill (range at the 400 km bound) because of the regional trend; UK handles this.
- UK linear drift extrapolates below 450 mm in a strip along the western border.
- No gauges in the far north-west, the Zambezi valley floor or most border strips; errors there are untested.
- pykrige not installed; kriging solved directly in `interp.py`.
