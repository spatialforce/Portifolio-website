# Verification: Hwange–Chizarira elephant corridor (least-cost path)

Every figure on the page comes from `data/summary.json`, `data/profile.csv` and the gpkg files written by
`analysis.py`. Rerun order: `fetch_open.py` → `fetch_osm.py` → (`fetch_gbif.py`) → `analysis.py` → `maps.py`
(set PROJ_LIB/PROJ_DATA from `../population/.projlib`). Grid: 100 m, EPSG:32735, 3 441 × 1 933 cells.

## Data
| Item | Source | Checked |
|---|---|---|
| Land cover | ESA WorldCover v200 2021 (AWS COG, 40 m overview, mode to 100 m) | `raw/lc.tif` |
| Elevation, slope | Copernicus DEM GLO-30 (AWS COG, ~60 m overview; slope there, mean to 100 m) | `raw/dem.tif`, `raw/slope.tif` |
| Population | WorldPop 2020 constrained, UN adjusted, people per cell | `raw/pop.tif` |
| Roads, rivers, places | OpenStreetMap via Overpass: 725 roads (motorway–tertiary), 602 rivers, 77 places | `raw/osm_*.gpkg` |
| Parks, WMAs | WDPA (`../baobab/raw/wdpa.geojson`) | analysis.py |
| Land mask | OCHA COD-AB admin 0; Natural Earth lakes removed; Zambia and Kariba closed | analysis.py |

## Figures on the page
| Page item | Value | Where |
|---|---|---|
| Land in box | 55 788 km² | `land_km2` |
| Hwange in box / Chizarira | 7 343 / 1 947 km² (Hwange full 14 651 km²) | `hw_km2`, `cz_km2` |
| Straight gap | 115.3 km | `gap_km` |
| AHP weights | pop 0.419, lc 0.263, road 0.160, wat 0.097, slp 0.062; λmax 5.068, CR 0.0152 | `ahp` |
| Factor mean resistance | pop 42.4, lc 14.5, road 17.9, wat 39.8, slp 3.8 | `factor_mean` |
| Cost mean / median, Table 3 | 28.5 / 20.7; 31.3, 22.2, 25.7, 20.9 % | `cost` |
| Path | 152.6 km, cost 717.0, ratio 1.32, mean cost 4.6, max density 6.0 | `lcp` |
| Path elevation | 544–1 096 m; starts ~990 m, ends ~860 m | `profile.csv` |
| Path land cover (Fig 1) | tree 88.0, shrub 63.1, grass 1.5 km | `lcp.lc_km` |
| Road crossings | 3: Bulawayo–Victoria Falls highway km 18.9, Binga Road km 69.7, unnamed km 133.8 | line ∩ `osm_roads` |
| Table 5 | Deka SA 1.7; Lubu 10.2, Nekatambe 23.3, Saba-Lubanda 29.6, Sikalenge 21.4 (WMA total 84.4); rest 66.5 km | line ∩ WDPA |
| Table 4 | high 1 443, moderate 699, low 1 415 km²; people 619 high, 1 781 moderate (2 400 total ≤10 %) | `corridor` |
| Corridor cover | shrub 60.5, tree 35.4, grass 2.4, crop 1.6 % | `corridor.lc_pct` |
| Corridor protection | protected 4.9 %, WMA 47.5 %; density 1.1 per km² | `corridor` |
| Width | median 5.9 km, none < 2 km; ~10 km in first 50 km | `width`, `profile.csv` |
| Pinch point | 2.2 km at km 68.7, tree cover, 4.2 per km², 860 m to road | `pinch` |
| Table 6 / Fig 3 | base 152.5; equal 159.9/67.7/50.6; lc first 153.1/100/100; people ×2 150.6/100/100; no water 150.3/100/69.2 | `sens` |

Base length in Table 6 (152.5) is measured between cell centres of the raw path; 152.6 is the clipped line.

## Not used
GBIF *Loxodonta africana*: only 4 usable records (≤5 km uncertainty) in the box; iNaturalist obscures elephant
locations to ~30 km. Mann-Whitney p = 0.88, meaningless with n = 4, so it is reported only as a limitation.

## Maps and figures
map1_study_area, map2_land_cover, map3_factors, map4_resistance, map5_corridor, map6_pressures,
fig1_path_cover, fig2_path_profile, fig3_sensitivity → `out/*.png` → webp in `clean/` → grain.py → tag_images.py.
