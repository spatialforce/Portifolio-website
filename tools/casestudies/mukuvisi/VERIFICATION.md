# Verification: Mukuvisi catchment runoff (SCS curve number)

Every figure on the page comes from `data/delin.json`, `data/cn.json`, `data/runoff.json`, `data/qmap.npz` and the gpkg
files. Rerun order: `fetch.py` → `fetch_rain.py` → `delineate.py` → `cn.py` → `runoff.py` → `maps.py`
(set PROJ_LIB/PROJ_DATA from `.projlib`). Grid: 30 m, EPSG:32736. Images: `out/*.png` → webp (max 2 000 px, q 92)
in `clean/` → `tools/provenance/grain.py` → `src/assets/casestudies/mukuvisi-runoff/` → `tag_images.py`.

## Data
| Item | Source | Checked |
|---|---|---|
| Elevation | Copernicus DEM GLO-30 (AWS COG, bilinear to 30 m) | `raw/dem.tif` |
| Land cover | ESA WorldCover v200 2021 (AWS COG, mode to 30 m) | `raw/lc.tif` |
| Soil | iSDAsoil sand and clay, 0–20 and 20–50 cm, weighted to 0–30 cm (AWS) | `raw/isda_*.tif` |
| Soil check | SoilGrids 2.0 0–30 cm (ISRIC WCS); only 40 % of cells have values; r = 0.22 sand, 0.26 clay | `cn.py` |
| Rainfall | CHIRPS v2.0 daily p05, 1 Oct–30 Apr, 1981/82–2024/25, 19 cells (area weighted) | `raw/chirps.npz` |
| Rivers, roads, dams, places | OpenStreetMap via Overpass mirror | `raw/osm_*.gpkg` |
| Admin | OCHA COD-AB Zimbabwe | `maps.py` |

## Figures on the page
| Page item | Value | Where |
|---|---|---|
| Area, main stem | 224.2 km², 46.5 km (OSM line 44.1 km) | `delin.json` |
| Check with OSM | 90.9 % of OSM points within 100 m; mean 99 m | `osm_within_100m`, `osm_dist_mean_m` |
| Streams | ≥ 1 km² drainage, 149.3 km, max Strahler order 3 | `stream_km`, `max_order` |
| Elevation | 1 368–1 601 m, mean 1 476 m | `z_*` |
| Bounds | 30.90–31.19° E, 17.79–17.95° S | `catchment.gpkg` |
| Sub-catchments | 8 (tributaries ≥ 8 km²), 11.2–67.0 km² | `subcatch.gpkg` |
| Land cover | built-up 39.9, tree 25.5, crop 16.7, grass 14.5, shrub 2.7, bare 0.6, water 0.1 % | `cn.json` |
| Soil | sand 56.4, clay 26.4 %; group C 90.6, D 6.4, A 3.0 %; D = 41 % of Eastlea–Highlands, 16 % of Greendale | `cn.npz` |
| Mean CN | 82.4; sub-catchments 78.1–87.0 | `cn.json`, `runoff.json` |
| Annual maxima | mean 44.1, SD 12.1, max 68.6 (8 Mar 2003), min 26.2 mm; season mean 780 mm | `runoff.json` |
| Design P (Gumbel, moments) | 42.1, 52.8, 59.9, 68.8, 75.5, 82.1 mm (2–100 yr) | `runoff.json` |
| Single wettest cell | 10 yr 86.2, 100 yr 119.3 mm | `runoff.json` |
| Timing | L 46.6 km, S 0.0049, Kirpich tc 9.9 h, lag 6.07 h | `runoff.json` |
| Table 3 | Q 13.2–42.0 mm, C 0.31–0.51, V 2.95–9.43 Mm³, qp 73.9–246.1 m³/s, peak ~19 h | `runoff.json` |
| Map 6 classes (Q10) | Low < 20 mm 44.4 % (99.7 km²), Moderate 16.1 %, High ≥ 30 mm 39.5 % (88.6 km²) | `qmap.npz` |
| Q10 by cover | built-up 35.2, crop 26.5, grass 18.3, tree 13.3 mm | `qmap.npz` |
| Table 4 | per sub-catchment, each routed alone (not summed) | `runoff.json` |
| Table 5 (AMC) | I 10.3 mm / 54.6 m³/s; II 25.1 / 144.5; III 39.1 / 231.3 | `runoff.json` |

## Published comparison
Gumindoga et al. (2014, Remote Sensing 6, 12544, doi:10.3390/rs61212544): Mukuvisi 223.1 km², flow path 44.7 km;
urban land 21.43 → 56.31 km² (1986–2008). Matches this study within 0.5 % (area) and 4 % (length).

## Not used / caveats
- No measured streamflow; results are not calibrated.
- CHIRPS smooths daily extremes; design storms are catchment means and should be read as lower values.
- WorldCover built-up is one class; all given the 65 % impervious CN (TR-55 1/8 acre).
- Dams and city drains not modelled; sub-catchment peaks not routed to the outlet.
- SoilGrids kept as a check only (masked over built-up land).
