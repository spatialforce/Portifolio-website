# Case study 14 verification (Masvingo mobile network coverage)

All figures come from out/stats.json (stats.py) and were checked against the page text and tables.

## Data
- OpenCelliD MCC 648 export (data/648.csv.gz): 11 637 cells nationally (UMTS 6 674, GSM 4 393, LTE 570).
- Province plus 30 km margin: 2 891 cells; inside the province 1 325 (UMTS 932, GSM 393, LTE 0). NetOne (MNC 1) 5 cells inside, the rest Econet (MNC 4).
- Sites: complete-linkage clustering at 500 m, sample-weighted centre (prep.py). 1 448 in the grid, 706 in the province (2G only 211, 3G only 392, both 103).
- Viewshed: gdal.ViewshedGenerate, 30 m observer, 1.5 m target, curvature coefficient 0.75, 20 km max (viewshed.py).
- Population: WorldPop/GP/100m/pop_age_sex_cons_unadj (constrained, ZWE 2020), unmask(0) before reduceResolution, scaled to ZIMSTAT 2022 district totals (ratios 0.909 to 1.216). Total 1 638 539.
- Note: WorldPop/GP/100m/pop is the UNCONSTRAINED product (first fetch used it by mistake; replaced).
- Province area 56 456 km² (published about 56 566 km²). Elevation 155 to 1 546 m, median 584 m.

## Results
- Line of sight: 2G 15 km 35.9%, 3G 10 km 28.7%, either 38.0%. Buffers: 2G 62.1%, 3G 35.9%.
- Area in line of sight: 2G 20.9%, 3G 15.9%, either 22.8%. Two or more 2G sites: 29.3%.
- Uncovered 1 015 194 (62.0%), all rural; rural coverage 32.7% of 1 507 796.
- Terrain share hidden: (62.1 - 35.9) / 62.1 = 42%.
- Uncovered by distance: <10 km 21.3%, 10-15 18.4%, 15-20 17.3%, 20-30 19.3%, >30 23.6%; median 17.7 km.
- Sensitivity (LOS / buffer): 2G 10 km 31.9/48.3, 15 km 35.9/62.1, 20 km 38.9/73.0; 3G 5 km 23.2/26.1, 10 km 28.7/35.9, 15 km 32.0/44.5.
- District table: see Table 3 on the page (identical to stats.json districts).

## Sources checked
- POTRAZ Q1 2024 Abridged Sector Performance Report: 2G 4 956, 3G 3 544, LTE 2 341, 5G 27 base stations (total 10 868).
  https://techzim.co.zw/wp-content/uploads/2024/06/First-Quarter-2024-Abridged-Sector-Performance-Report-12-June-2024.pdf
- Bondarenko et al. (2020) doi:10.5258/SOTON/WP00682 (51-country constrained set).
- Wang, Robinson and White (2000) PE&RS 66(1) 87-90.
- ESA (2021) GLO-30 doi:10.5270/ESA-c5d3d65.

## Limits (stated on the page)
Crowd-sourced, incomplete site record (no LTE, Econet only, road bias), so coverage is a lower bound. Surface model includes canopy; no diffraction; assumed ranges (tested); estimated positions; uniform 30 m mast.
