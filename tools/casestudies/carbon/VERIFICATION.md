# Verification: Above-Ground Carbon Stock of Hwange National Park (case study 16)

All model figures come from out/stats.json, out/cv.csv and the rasters written by analysis.py / fix_cci.py.

| Page figure | Value | Source in this build | Cross-checked against |
|---|---|---|---|
| Park area | 14 699 km² (equal-area, EPSG:6933); 14 689 km² as 1 468 858 one-ha UTM cells | data/wdpa_hwange.geojson | WDPA REP_AREA 14 651 km² (0.3% difference) |
| Elevation 828–1 148 m, median 1 017 m; mean slope 0.7° | rast/elev.tif, rast/slope.tif inside park | GLO-30 | Childes & Walker 1987 describe the park as flat Kalahari sand plateau |
| Footprints 721 540, kept 721 522 (18 outside 0–200 Mg/ha) | stats.json n_all, n_keep | GEDI L4A v2.1 | 2023 has only 6 245 shots, consistent with GEDI storage from March 2023 |
| About 49 footprints per km² | 721 521 inside polygon / 14 689 km² | computed | — |
| Footprint median 4.7, mean 10.8 Mg/ha; 51.5% < 5; 68.7% < 10; 5.2% > 40 | footprints inside park | computed | GEDI L4B park mean 10.47 Mg/ha |
| Training cells 211 509 | stats.json n_cells | — | — |
| CV R² 0.575, RMSE 8.04 (73.5%), MAE 5.14, bias +0.16, mean obs 10.94 | stats.json cv | 5-fold GroupKFold, 10 km blocks | Li et al. 2024: L4A product R² 0.42, RMSE 12 Mg/ha (79.5%); local RF R² 0.71, 53.3% |
| Cells obs > 40: 4.1%, obs mean 49.9, pred 29.1; obs < 5: obs 2.7, pred 5.5 | out/cv.csv | computed | regression to mean, expected for RF |
| Importance radar 53.0% (VV 30.7%), optical 37.7%, terrain 9.3% | stats.json importance (summed) | — | — |
| AGB 16.73 Mt; C 7.87 Mt; CO2e 28.84 Mt; mean 11.39 Mg/ha (5.35 Mg C/ha), median 7.63 | stats.json totals | C = 0.47 × AGB (IPCC 2006); CO2e = C × 44/12 | — |
| Classes: tree 1 818 km² (12.4%), 29.1 Mg/ha, 13.7 Mg C/ha, 2.49 Mt C (31.6%) | stats.json classes | WorldCover 2021 | GIZ 2015 Baikiaea woodland 29.44 t/ha |
| Shrubland 11 408 km² (77.7%), 9.5, 4.5, 5.09 Mt C (64.7%) | stats.json classes | — | — |
| Grassland 1 355 km² (9.2%), 4.3, 2.0, 0.27 Mt C (3.5%); cropland 90 km², 3.1; other 17 km², 4.8 | stats.json classes (other = bare + water + wetland) | — | class sums = 14 688 km², 7.865 Mt C |
| Tree spread mean 5.25 Mg/ha (2.5 Mg C/ha); mean per-cell ratio 54% | stats.json sd_mean, cv_cell_pct | 50 of 200 trees | spread by class: tree 10.2, shrub 5.8, grass 3.6 Mg/ha; r(pred, sd) 0.84 |
| Footprint mean in park 10.81; map 5.4% higher | stats.json gedi_park_mean | — | — |
| L4B 10.47 vs 11.17 on same cells (6.6%), cover 90.5%, r 0.66 | stats.json | GEDI L4B v2.1 | — |
| CCI 3.50 Mg/ha, 2.41 Mt C, r 0.79; class shrub 2.2, grass 0.1, tree 14.3 | stats.json (masked cells read as 0) | ESA CCI Biomass v5 2020 | GIZ 2015 tree value is 2.06 × CCI tree class |
| FREL 5 187 697.6 t CO2e/yr (modified; submitted 4 255 249.2) | — | UNFCCC FCCC/TAR/2024/ZWE | — |
| GEDI L4A ~2.1 × field in Sudanian woodland | — | Hasoba & Czimber 2026, Remote Sensing 18(16) 2751 | — |
| Elephant damage 23% (high use) vs 11% (low use) at artificial points | — | Mukwashi, Gandiwa & Kativu 2012, IJES 2(3) 1355–1368 | — |

Disagreements stated on the page: CCI is less than a third of this study; published L4A error direction differs (−37% South Africa, ×2.1 Sudan).

Map 2 (revised 2026-11-12): mean of footprints per 1 km cell (grid_gedi.py). 14 203 cells hold footprints; of the 14 691
1 km cells with centres inside the park, 95.1% hold at least one footprint. Figure 1 (revised): plain scatter of a random
5 000 cells plus mean prediction per 5 Mg/ha observed class; 0.07% of cells lie above 80 Mg/ha and fall outside the axes.
