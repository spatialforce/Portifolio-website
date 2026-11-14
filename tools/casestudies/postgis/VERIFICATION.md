# Verification: Walking Access to Health Facilities in Harare (PostGIS and pgRouting)

Page: src/pages/cs_postgis.tsx, slug harare-health-access. Run date 13 November 2026.

## Run order (from this folder, Git Bash)

1. `"/c/Program Files/PostgreSQL/16/bin/pg_ctl" -D pgdata -o "-p 5433 -c listen_addresses=localhost" -l pg.log start` (user gis, db harare)
2. `bash load.sh` (uses .projlib for ogr2ogr and raster2pgsql only)
3. `sql/01_network.sql` (about 44 s), `sql/02_cells.sql` (30 s), `sql/03_access.sql` (8 min), `sql/04_sites.sql` (3 min)
4. `bash export.sh` (writes exp/*.csv)
5. `unset PROJ_LIB PROJ_DATA; python -I analysis.py` (writes out/stats.json and prints the checks below)
6. `python -I maps.py; python -I graphs.py` (PROJ variables unset, or rasterio fails with "EPSG code is unknown")
7. Images: out/*.png (not _s_* previews) to lossless webp in clean/casestudies/harare-health-access, copy to src/assets, then
   `python -I tools/provenance/grain.py tools/casestudies/postgis/clean <files>`, `python -I tools/provenance/tag_images.py`, `npm run build`.

## Inputs

| Input | File |
|---|---|
| Province and wards | dl/gb/zwe_adm1.geojson (shapeName Harare), zwe_adm3.geojson (geoBoundaries) |
| Roads, health points and polygons, places | dl/osm/zimbabwe.osm.pbf (Geofabrik) |
| Public facility list | data/mfl_harare.csv, from dl/fac/ssa_mfl.xlsx (Maina et al. 2019) |
| Population | data/pop_harare.tif, clipped from WorldPop zwe_pop_2025_CN_100m.tif (R2025A, alpha) |

## Checks and the values on the page

| Check | Value |
|---|---|
| Province area (sum of 78 wards) | 940.2 km² |
| Populated cells, people | 101 890; 2 685 012 |
| Network segments, length | 256 500; 10 307.5 km (Table 2 from exp/netlen.csv; "Other" is 9 small classes, 3 610 segments) |
| Vertices; main component; components | 236 018; 234 838; 94 |
| Cell snap median, max | 50.5 m; 1 000 m |
| Facility snap median, max | B 38.7 m, 87.9 m; A 43.8 m, 185.9 m |
| Facilities A; B | 27 (24 clinics, 3 hospitals); 105 (84, 21) after the 50 m duplicate merge |
| Mean, median walk A; B | 4 964, 4 147 m; 2 185, 1 782 m |
| Bands A (%) | 5.4, 13.3, 15.3, 23.0, 43.0 |
| Bands B (%) | 20.8, 36.3, 20.9, 15.5, 6.5 |
| Within 2 km straight line A; B | 32.3 %; 77.1 % |
| Detour index A; B (population-weighted) | 1.39; 1.48; no ratio below 1.0 |
| Network nearest differs from straight-line nearest A; B | 9.5 %; 12.7 % |
| Catchment median, max A; B | 40 706, 462 857; 13 545, 159 382 |
| People beyond 2 km, B | 1 153 399 |
| Authorities (B > 2 km, A > 2 km, B mean) | Harare 35.7 %, 73.3 %, 1 853 m; Harare Rural 76.6, 98.7, 3 727; Chitungwiza 45.8, 86.1, 2 267; Epworth 31.8, 100, 1 765 |
| Candidates | 461 |
| Greedy 5 sites; 10 sites | 238 617 (20.7 % of far, within 2 km 57.0 to 65.9 %); 369 465 (32.0 %, to 70.8 %) |

Tables 5 and 6 on the page are copied from the analysis.py print (worst wards and the ten picks).

## Caveats stated on the page

OpenStreetMap under-maps clinics in Chitungwiza (5 clinics, 3 hospitals) and Epworth (3 clinics); candidate sites need ground checks;
5 km is a commonly quoted benchmark, not an official standard; WorldPop 2025 (2.69 million) is above the 2022 census (about 2.43 million)
and R2025A is an alpha release. No access tokens or personal data are stored in this folder's outputs.
