# Verification: Chimanimani landslide susceptibility

Page: `src/pages/cs_landslide.tsx`, route `/case-studies/chimanimani-landslide`.
Method: eight factors reclassified 1 to 5, AHP weights, weighted overlay, natural breaks.
The Idai landslide source points (RMCA, 2025) are used ONLY to check the map, never to set breaks or weights.

## Run order (from this folder, `python -I`, PROJ_LIB/PROJ_DATA from `.projlib`)

Inputs are reused from `../chimanimani_flood` (same 30 m UTM 36S grid, X0 430000, Y0 7860000, 2600 × 2834 cells):
`rast/stack.npz` (elevation, slope, curvature, distance to streams, land cover, clay, mask), `rast/annrain.npy`
(CHIRPS mean annual rainfall 1991 to 2020), `rast/bld.npy`, `rast/pop.npy`.

1. `explore.py`: rasterises the source points to `pts.npy` (10 213 district cells). Prints factor percentiles only.
2. `overlay.py`: reclassification, AHP, LSI, Jenks classes, AUC, exposure, written to `out/overlay.json`.
3. `maps.py` and `graphs.py`: the images in `out/` (the `_s_*.png` files are small previews, not for the site).

## Checked on 2026-11-13

- AHP: λmax 8.208, CI 0.030, RI 1.41, CR 0.021 (< 0.10). Weights (%): slope 32.4, rainfall 22.2, land cover 14.6,
  clay 9.2, curvature 9.2, distance to streams 5.8, elevation 3.9, aspect 2.7; they sum to 100.0.
- LSI range 1.15 to 4.84. Jenks breaks 1.91, 2.41, 2.87, 3.32 (Fisher-Jenks DP on a 400-bin histogram).
- District area 3 342 km². Class areas 644.2, 542.6, 844.2, 918.9, 392.2 km² (sum 3 342.1).
  High plus very high = 1 311.1 km² (39.2 %).
- Landslide cells by class: 0.0, 0.1, 4.5, 38.2, 57.2 %. High plus very high = 95.4 %. Frequency ratios 0.00, 0.01,
  0.18, 1.39, 4.88. AUC of the LSI 0.867 (Mann-Whitney, landslide cells against all other district cells).
- Factor AUCs: slope 0.83, rainfall 0.73, clay 0.67, elevation 0.66, curvature 0.63, aspect 0.57, land cover 0.41,
  distance to streams 0.42. The last two fall below 0.5, so their scores run against the inventory. Reported as is.
- West of 32.65° E (34.3 % of the district): 9.5 % high or very high, 4.1 % of landslide cells.
  East: 54.8 % high or very high, 95.9 % of landslide cells.
- Within 3 km of villages, high plus very high: Rusitu 87 %, Chikukwa 77 %, Machongwe 63 %, Chimanimani 51 %,
  Cashel 27 %, Nhedziwa 1 %, Mutambara, Nyanyadzi, Chakohwa and Hot Springs 0 %.
- Exposure (totals 67 057 buildings, 151 816 people): high plus very high hold 18 345 buildings (27.4 %) and
  about 44 000 people (28.9 %). People are rounded to the nearest hundred on the page.
- Rainfall 1st to 99th percentile 483 to 1 516 mm. This is long-term mean rainfall, not the March 2019 storm total.
- Curvature from terrain.py is −Laplacian × 100 of the lightly smoothed DEM (general curvature, 1/100 m), so the page
  calls it "Curvature", not plan or profile curvature.

## References checked

- RMCA (2025) source points and extent maps on UNESCO IHP-WINS, doi 10.63253/nii4g2ac.
- Dille et al. (2026) NHESS 26, 2561–2577, doi 10.5194/nhess-26-2561-2026.
- Kayastha, Dhital and De Smedt (2013) Computers & Geosciences 52, 398–408, doi 10.1016/j.cageo.2012.11.003.
- Pourghasemi, Pradhan and Gokceoglu (2012) Natural Hazards 63(2), 965–996, doi 10.1007/s11069-012-0217-2.
- Others as on the flood page (Saaty, Jenks, Funk, ESA, Karra, Hengl, Gorelick, Sirko, Bondarenko, OCHA, City Population).

## Text checks (2026-11-13, scratchpad counts)

- Slopes > 25°: 74.1 % of that ground lies east of 32.65° E. Clay score 4 or 5: east 48 %, west 13 %.
- Land cover at landslide cells: trees 60.3 % (district 43.4 %), rangeland 38.7 % (52.4 %).
- Median distance to streams: landslide cells 560 m, district 424 m.
- Within 3 km of Mutambara, Nyanyadzi, Chakohwa and Hot Springs, very low plus low is 95 to 100 %.
