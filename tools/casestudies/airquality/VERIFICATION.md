# Verification: Hwange air quality (case study 14)

Run order: fetch.py, fetch_pop.py, analysis.py, maps.py, graphs.py (PROJ_LIB/PROJ_DATA set to rasterio's proj_data).

## Checked
- HPS location: OSM "Hwange Thermal Power Station" -18.3844, 26.4700, about 120 m from the script's point.
- WorldPop grid total 775 456 vs native-projection sum 775 455.
- All page numbers come from out/stats.json (enhancement, p, DiD, annual, seasonal, towns, exposure, NO2 maximum).
- Area above 1.5 ×: 668 and 1 409 cells × 1.176 km² (0.01° at 18.4° S) = about 790 and 1 660 km².
- 2 × zone: 20 142 of 20 453 people within 10 km of HPS. Lukosi NO2 22.4 is below the 1.5 × threshold of 22.8, so it is outside the zone.
- Distances from HPS: Dete about 49 km, Victoria Falls about 83 km, Maamba about 137 km.
- Unit 7 synchronised on 20 Mar 2023; Unit 8 reached 355 MW on 14 Jun 2023 (Mining Index articles).
- Herald article dated 13 May 2021: first coke battery done April 2021, second started May 2021.
- Mining Index ?p=109558 (10 Nov 2024): units 1 to 6 built 1973 to 1987 without SO2 control. It does NOT describe ZhongXin; the ZhongXin location comes only from OSM.
- NewsDay, 24 Jun 2024: 800 MW lost at Kariba ("hydrological challenges").
- FinGaz, 16 Feb 2026: units 1 to 6 produce about 300 MW.
- Engineering News (Jindal) returned 403 and was dropped.

## Not verifiable here
- No ground monitor data. Columns are not surface concentrations.
- No unit-level generation data to split the new and old units or the coke batteries.
