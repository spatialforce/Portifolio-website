# Case study 7: verification of figures

AHP site suitability for utility-scale solar farms, Matabeleland South. 250 m grid (EPSG:32735),
areas in EPSG:6933 equal area. All page numbers come from out/results.json, written by
analysis.py on 2026-11-12, and were checked against the sources below.

| Figure in the text | Our value | Cross-check | Agreement |
|---|---|---|---|
| Province area | 54 133 km² (rasterised, equal area) | ZimStat / commonly cited 54 172 km² | Within 0.07% |
| Mean daily GHI in the province | 5.42 to 6.05 kWh/m²/day by district; median 5.66 | Global Solar Atlas country factsheet: Zimbabwe average ~5.7; Mutume et al. 2023 national GHI ~5.7 kWh/m²/day | Consistent |
| Highest GHI in the far west | Bulilima district mean 6.05 | GSA GHI layer itself (same source, read off map) and GeoSUN Africa maps showing SW Zimbabwe/ NE Botswana > 6.0 | Consistent |
| Consistency ratio | CR = 0.023 (λmax 6.145, n = 6, RI 1.24) | Published solar AHP studies report CR 0.041 (Al Garni & Awasthi 2017), 0.019–0.08 (Doorga et al. 2019), 0.071 (Mutume et al. 2023); Saaty threshold 0.10 | Inside the published envelope |
| GHI weight 0.444 | Largest criterion weight | Al Garni & Awasthi 0.322; Doorga et al. 0.401; Mutume et al. 0.555 (solar resource criterion) | Brackets our value |
| Grid distance weight 0.215 | Second largest | Noorollahi et al. 2016: 0.112; Sánchez-Lozano et al. 2013: 0.415 | Between published values |
| Slope weight 0.137 | Third | Al Garni & Awasthi 0.163 | Close |
| Analysable share | 68.0% of the province after constraints | — (depends on constraint set; stated as a result of this analysis) | n/a |
| Protected areas exclude 23.4% | WDPA May 2025 + 500 m | Matobo NP, Tuli, Maleme and safari/recreational parks are in WDPA; ~27% of Zimbabwe has protected status nationally (UNEP-WCMC country profile) | Plausible for this province |
| Built-up exclusion only 0.2% | Dominant built-up cells (WorldCover mode = 50) | Max-reducer version (any 10 m built pixel in a cell) would exclude 30.5% — scattered homesteads; documented as a method choice in the text | Method note |
| Suitability classes | Unsuitable 22.1%, Low 31.0%, Moderate 24.0%, High 18.9%, Very high 4.0% of analysable area | Comparable AHP studies place 2–10% in the top class (Doorga et al. 3.8% of Mauritius; Uyan 2013 8.8% "best") | Consistent order of magnitude |
| High + Very high area | 8 451 km², concentrated in Bulilima (2 669) and Mangwe (2 631) | Flat terrain, GHI > 5.8 and the Bulawayo–Plumtree (Insukamini–Marula) 132 kV line explain the pattern; checked against OSM power lines used in the model | Internally consistent |
| Sensitivity | High+ area changes −7.2% to +4.4% for ±20% on the GHI weight; all other criteria within ±4% | One-at-a-time reweighting, recomputed overlay | Ranking stable |
| Blanket Mine solar (12 MW, operating) | Score 3.30, Moderate; 3.4 km from grid | Caledonia Mining 12.2 MW plant commissioned 2023 at Blanket Mine, Gwanda | Site exists; model rates it above the analysable median (2.95) |
| ZPC–Intratrek Gwanda (100 MW) | Score 3.39, Moderate; 5.8 km from grid | ZPC Gwanda 100 MW project site near Gwanda town | Consistent: sited for grid and town, not raw resource |
| Gwanda Timber Farm / Matshela (100 MW, licensed) | Excluded cell | Its own footprint is mapped built-up in WorldCover 2021 and parts of the 3×3 window exceed 5° slope; 0.9 km from the grid | Expected artefact; reported honestly in the text |
| Nottingham Estate (4.5 MW) | Score 2.56, Low; 13.1 km from grid | Behind-the-meter plant for a citrus estate on the Limpopo | Consistent: sited at the load, not for grid access |
| Mashaba mini-grid (99 kW) | Excluded (inside WDPA + 500 m); 61 km from grid | Built as an off-grid mini-grid precisely because the grid is far | Consistent with its off-grid design |

Notes
- Weights are principal-eigenvector weights of the 6×6 pairwise matrix in ahp.py; RI = 1.24 (Saaty, n = 6).
- Constraints: slope > 5°, permanent water (JRC GSW occurrence > 50% or WorldCover 80), wetland (90/95),
  dominant built-up + 500 m, WDPA + 500 m. Cells failing any constraint are removed before the overlay.
- GHI from Global Solar Atlas v2 (Solargis) long-term daily totals, warped bilinear to the 250 m grid.
- District areas sum to 54 132 km² against the 54 133 km² province raster (rounding).
- Class breaks are equal 0.5 intervals on the 1–5 weighted score: [2.5, 3.0, 3.5, 4.0].
