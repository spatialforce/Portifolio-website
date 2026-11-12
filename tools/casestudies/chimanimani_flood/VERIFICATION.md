# Verification: Chimanimani flood susceptibility (case study 6)

Page: `src/pages/cs_chimflood.tsx`, route `/case-studies/chimanimani-flood`.
Method: eight factors reclassified 1 to 5, AHP weights, weighted overlay, natural breaks.

## Run order (from this folder, `python -I`, PROJ_LIB set to rasterio's proj_data)

1. `fetch.py`: Esri LULC 2018 and OpenLandMap clay from GEE, on the 30 m UTM 36S grid. The IMERG and sand layers it also fetches are no longer used.
2. `fetch2.py`: Open Buildings v3 count (confidence 0.75 or more) and WorldPop 2020 constrained people per cell.
3. `fetch3.py`: CHIRPS daily rainfall from 1991 to 2020, summed and divided by 30, giving `rast/annrain_*.tif`.
4. `terrain.py`: GLO-30 with a 15 km buffer, run through pysheds to get slope, TWI, upstream area and `dem_buf.tif`.
5. `prep.py`: district mask (OCHA COD-AB) and the RMCA zones, stacked in `rast/stack.npz`.
6. `exposure.py`: building and people rasters (`rast/bld.npy`, `rast/pop.npy`).
7. `overlay.py`: reclassification, AHP, FSI, Jenks classes and exposure, written to `out/overlay.json`.
8. `check.py`: AUC and class shares against the RMCA debris-rich flow zones, written to `out/check.json`. These zones are not used to build the map.
9. `maps.py` and `graphs.py`: the images in `out/`.

The grid is EPSG:32736 at 30 m, with X0 430000, Y0 7860000 and 2600 × 2834 cells.

## Checked on 2026-11-12

- **AHP:**
  - λmax is 8.207, CI 0.030, RI 1.41 (Saaty, for n = 8) and CR 0.021.
  - The weights in Table 3 sum to 99.9 % after rounding.
- **FSI:**
  - The range is 1.08 to 4.95.
  - The breaks are 1.99, 2.51, 3.04 and 3.65, from a Fisher-Jenks DP on a 400-bin histogram.
- **Areas:**
  - Class areas and shares in Table 5 match `overlay.json`.
  - High plus very high is 658.7 + 388.8 = 1 047.5 km², which is 31.3 % of 3 342 km².
- **Buildings and people:**
  - 42 087 of the 67 057 buildings (62.8 %) are in the high and very high classes.
  - About 95 300 of 151 816 people (62.8 %) are in those classes.
  - People are rounded to the nearest 100, so the table total shows 151 800.
- **Factor shares:** Table 4 matches `factor_pct` in `overlay.json`. Land cover score 5 is 0.3 %.
- **Rainfall:** the in-district range is 443 to 1 564 mm, and the 1st to 99th percentile is 483 to 1 516 mm. The page says "about 480" and "more than 1 500".
- **Check:**
  - AUC is 0.946, shown as 0.95.
  - Shares of the flood cells by class are 0.1, 0.7, 2.3, 11.2 and 85.7 %.
  - The flood zones cover 47.2 km².
- **Census:** 153 619 people at the 2022 census (City Population, 2023).
- **DOIs:**
  - ESA, Karra, Gorelick, Sirko, Bondarenko, Hengl (clay) and RMCA were checked in an earlier session.
  - Funk 2015 (10.1038/sdata.2015.66) and Beven and Kirkby 1979 (10.1080/02626667909491834) are standard references.
  - Saaty (1980) and Jenks (1967) are books with no DOI.

## Limits stated on the page

- The AHP weights are expert judgement.
- The DEM is 30 m, CHIRPS is about 5 km and clay is 250 m.
- The land cover is a single year (2018).
- The map shows relative likelihood, not depth or return period.
