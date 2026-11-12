# Verification: Lake Kariba area–elevation–storage and level decline

Page: `src/pages/cs_kariba.tsx`, route `/case-studies/lake-kariba`.

## Run order (from this folder, `python -I`, PROJ_LIB set to rasterio's proj_data)

1. `fetch_rast.py`: JRC GSW 1.4 occurrence tiles (`rast/occ_*.tif`) and GLO-30 relief for the lake box (GEE)
2. `fetch_area.py`: Landsat 5, 7, 8 and 9 C2 L2 lake area at 90 m, high (Apr to Jun) and low (Oct to Dec) seasons 2000 to 2025
   - QA cloud mask, MNDWI > 0
   - gaps filled from JRC occurrence (Zhao and Gao, 2018): best-splitting threshold t, area = pixels with occurrence ≥ t
   - writes `data/area.csv` and `data/area_by_occ.json`
3. `analysis.py`:
   - DAHITI levels (`data/kariba_dahiti.csv`, downloaded by hand from DAHITI) shifted to the ZRA gauge datum
   - area paired with the seasonal median level, linear and quadratic fits, storage curve, ZRA checks
   - bed elevation of the drawdown zone (`rast/bed.npz`)
   - writes `out/stats.json`, `out/pairs.csv`, `out/monthly.csv`
4. `fetch_rgb.py`: Landsat 8 and 9 true-colour median, Oct to Dec 2024, for the three Map 3 windows
5. `maps.py`: Maps 1 to 5 and `out/mapstats.json`
6. `graphs.py`: Figures 1 to 4

Then `tools/provenance/grain.py` on the webps (once only) and `tools/provenance/tag_images.py` (entry "kariba").

## Map layout

Title inside the frame at the top, legend at lower right, brackets for years. Map 3 is a 2 × 2 grid with the spare cell holding the legend, north arrow and 10 km scale. Map 5 uses the dark basemap.

## Checked on 2026-11-12, page against `out/stats.json` and `out/mapstats.json`

- **Levels:**
  - There are 2 080 DAHITI readings from 1992-11-22 to 2026-10-09, with 1 827 in 2000 to 2025.
  - The datum offset is +0.409 m, and gauge matches differ by 0.35 to 0.47 m.
  - The highest level is 487.60 m (21 May 2000) and the lowest 475.53 m (26 Dec 2022).
  - The trend is −0.275 m a year, and the median annual amplitude 4.01 m.
  - The means are 483.17 m (2000 to 2009) and 479.39 m (2016 to 2025).
  - Months less than 1 m above the MOL: 2, 1, 3 and 2 for 2022 to 2025 (`near1` × 12).
- **Area curve:**
  - There are 51 pairs, and 2025 low was dropped (error share ≥ 5 %).
  - A = 79.0496 h − 33 153.15, with R² 0.976 and RMSE 40.6 km². The quadratic RMSE of 38.8 is not 5 % better, so the line is kept.
  - The area is 4 435 km² at the MOL and 5 463 km² at the MRL (ZRA gives 5 580, 2.1 % higher).
- **Storage:**
  - Live storage is 64.33 km³ (ZRA implied 21.53 ÷ 0.3322 = 64.8).
  - Table 3 rows match `stats.json` `table`.
  - Period values (36.3 / 17.8 km³, 56.5 / 27.7 %, minimum 28.0 / 6.4 km³) come from the curve at the Table 2 levels.
  - At 475.53 m storage is 0.13 km³, and at 475.68 m it is 0.80 km³ (1.2 %).
- **ZRA checks:** 480.19 m gives 21.67 km³ and 33.68 % (ZRA 21.53, 33.22). 479.98 m gives 32.12 % (ZRA 31.67). 476.67 m gives 8.15 % (ZRA 8.09).
- **Exposed bed:**
  - 850.4 km² was exposed (Zambia 389.1, Zimbabwe 461.3).
  - The water area was 5 356.8 km² at the 2000 high and 4 506.3 km² at the 2024 low.
  - The Map 3 windows (28 × 18 km) held 83.0, 82.1 and 63.7 km².
- **Retreat:**
  - The median is 300 m, p90 1 697 m and the maximum 8 408 m, at UTM 35S 616 410, 8 103 570 (28.09° E, 17.15° S, Binga District south shore).
  - The class shares are 47.0, 17.4, 15.7, 12.2 and 7.7 %.
  - The medians are 247 m in Zambia and 339 m in Zimbabwe.
- **Occurrence:** 84.8 % of the lake has occurrence ≥ 95.
- **Hydropower:** the 2024 allocation is 16 BCM, against 30 BCM for 2023, with 8 BCM each for ZESCO and ZPC (ZRA press statement, 28 Dec 2023).
