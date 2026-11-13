# Verification: Baobab habitat suitability (MaxEnt), Zimbabwe

Every figure on the page comes from the files in `data/` that these scripts write. To rerun, use the order
`fetch_ee.py dem500` → `prep.py` → `model.py` → `summary.py` → `maps.py` (set PROJ_LIB to rasterio's proj_data).

## Data
| Item | Source | Checked |
|---|---|---|
| Records | GBIF occurrence search, *Adansonia digitata* L. (taxonKey 5406695), country ZW, with coordinates. 535 records: 513 human observations and 22 preserved specimens, from 1886 to 2026 | `raw/gbif_ZW.csv` |
| Climate | CHELSA V2.1 bio11, bio12 and bio15, 1981–2010, 30 arc-sec (Karger et al. 2017), read in a window over Zimbabwe | `raw/bio*.tif` |
| Elevation | SRTM via Earth Engine at 15 arc-sec, averaged to the 30 arc-sec grid. Used for maps and summaries only, not as a predictor | `raw/dem500.tif` |
| Protected areas | WDPA (UNEP-WCMC & IUCN). 93 areas kept: National Park, Safari Area, Recreation Park, Sanctuary, Botanical Reserve, State Forest | `data/pa.gpkg` |
| Boundaries | OCHA COD-AB admin 0 and 1; Natural Earth lakes removed from the land mask (Kariba, Cahora Bassa) | prep.py |

## Record cleaning (data/cleaning.json)
535 → 461 (bad coordinate flags removed, uncertainty ≤ 5 km) → 421 (unique coordinates) → 410 (on land in Zimbabwe)
→ 269 (one per 1 km cell) → **145** (one per 10 km block).

## Model (data/model.json)
- Predictors: bio11, bio12, bio15. Pairwise |r| at 20 000 random cells is 0.43 or less (bio11–bio15 0.43, bio12–bio15 0.33, bio11–bio12 −0.24).
  Elevation was left out because r(bio11, elevation) = −0.85.
- elapid 1.0.4 MaxentModel, linear and quadratic features, beta multiplier 1.5, cloglog output, 10 000 background points.
- AUC: training 0.774. Main check, 50 km checkerboard: 0.736 and 0.794 (mean 0.765). Random 5-fold mean 0.773.
  Geographic 5-fold mean 0.652 (0.863, 0.723, 0.536, 0.517, 0.623), reported as a limitation.
- Permutation importance: bio11 73.2 %, bio15 22.2 %, bio12 4.6 %.
- Response (other predictors held at their background median): bio11 0.02 at 11.75 °C to 1.0 at 21.95 °C;
  bio12 0.18 at 335 mm to 0.71 at 1 463 mm; bio15 0.67 at 85 to 0.05 at 129.
- 10th percentile training presence threshold 0.214.
- Response to bio11 crosses 0.2 at about 16.3 °C and 0.6 at about 18.6 °C (quoted on the page).

## Summary (data/summary.json), exact spherical cell areas
- Land 389 459 km². Not suitable (< 0.2) 126 783 (32.6 %); Low (0.2–0.4) 140 820 (36.2 %); Moderate (0.4–0.6) 48 686 (12.5 %); High (≥ 0.6) 73 171 (18.8 %).
- Suitable (moderate + high) 121 857 km² (31.3 %).
- Protected areas 62 594 km² (16.1 % of land). Suitable inside them 26 309 km² = 21.6 % of suitable habitat; 26.9 % of high; 42.0 % of protected land is suitable.
- Records by class: 14, 24, 19, 88 (High). So 107 of 145 (73.8 %) fall in moderate or high.
- Suitable share by elevation band: 0–600 m 100 % (80 records); 600–900 66.2 % (29); 900–1200 6.7 % (25); 1200–1500 0.4 % (9); > 1500 0 % (2).
- Provinces: see summary.json `prov`. Masvingo 40 737 km² suitable (72.0 %), of which 32 532 high.

## Literature checks
- Moyo et al. 2019 (Trans. R. Soc. S. Afr. 74(3): 213–218, doi 10.1080/0035919X.2019.1650309): MaxEnt for baobab in Zimbabwe;
  altitude and the mean temperatures of the driest and coldest quarters were key. Agrees with bio11 leading here.
- Sanchez et al. 2011: African baobab distribution limited by cold and by rainfall extremes.
- Wickens and Lowe 2008: baobab grows mostly below about 1 500 m in hot, seasonally dry savanna. Agrees with the elevation bands.

## Visual checks
Maps viewed at preview size: no false suitability on the Eastern Highlands, Lake Kariba masked, labels clear.
