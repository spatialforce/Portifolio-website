# Case study 2: verification of figures

Source data: CHIRPS v2.0 pentad, 0.05°, October to April, 34 seasons 1991/92 to 2024/25, normal 1991/92 to 2020/21.
All page numbers were checked against data/national_series.csv, data/provinces.csv and data/grids.npz on 2026-11-11.

| Figure in the text | Our value | Cross-check | Agreement |
|---|---|---|---|
| Annual mean rainfall | 645 mm (Jul to Jun climatology) | The Global Economy 658 mm (1961 to 2022); World Bank CCKP about 670 mm | Within 2 to 4% |
| Season share of annual rain | 98% Oct to Apr | Standard description of a single summer rainy season | Consistent |
| Eastern Highlands above 1 000 mm | Up to 2 456 mm per cell | FAO a0395e: Natural Region I above 1 000 mm | Consistent; CHIRPS weak over mountains, so magnitude uncertain |
| South and far west below 450 mm | Matabeleland South 450 mm, minimum cell 197 mm | FAO: Region V below 450 mm | Consistent |
| 1991/92 the driest season | 359.8 mm, 56.9% of normal; driest over 59% of land, mostly south and east | FAO SADC REWS update: worst drought in living memory, deepest in southern Zimbabwe; World Bank 1992: most severe this century | Consistent |
| 2023/24 drought | 435.9 mm, 68.9%; 72% of land below 75% of normal, 98% below 90% | NBC 3 April 2024: state of disaster, more than 80% of country below normal rain | Consistent |
| No significant trend | Sen +5.0 mm per decade, p = 0.94; 0% of land significant | Scientific African 2023 (30-year CHIRPS and station study, Zimbabwe) | Consistent with no clear seasonal-total change |
| CHIRPS accuracy | n/a | Dinku et al. 2018 good skill in eastern Africa, weaker over mountains; eastern Zimbabwe 2024 r = 0.34; Scientific African 2023 kappa 0.74 to 0.81 | Stated as a limitation |

Notes
- Natural region rainfall bounds differ between FAO documents; only Region I (above 1 000 mm) and Region V (below 450 mm) are quoted.
- Harare (30 cells) and Bulawayo (19 cells) are small; their provincial values rest on few cells.
- Drought season = below 75% of the cell's own 1991 to 2020 normal.

## Redesign checks (2026-11-11)
Extra figures from droughts.py (data/drought_seasons.csv, prov_droughts.csv, district_trend.csv) and a grid check by province.

| Figure in the text | Value | Checked against |
|---|---|---|
| Land below 75% / 50% of normal | 1991/92 90.4 / 34.4%; 2023/24 72.1 / 2.9% | drought_seasons.csv |
| Masvingo 1991/92 | 33% of normal, 99% of province below half | prov_droughts.csv, grid check |
| Matabeleland North 2023/24 | 58% of normal, 15% of province below half | prov_droughts.csv, grid check |
| CV below 21% | 15% of land; 67% of Mash West, 47% of Mash Central | Map 3 legend shares, grid check |
| CV 30% or more | 83% of Masvingo, 65% of Mat South | grid check |
| Drought frequency | 2 to 12 seasons; 77% of land 4 to 7; 17% 8 or more, 91% of it in Masvingo, Mat South, Mat North | Map 6 legend shares, grid check |
| District trends | 58 positive, 33 negative; Zaka −17.5, Chikomba +25.7; minimum p 0.366 (Mangwe) | district_trend.csv |
