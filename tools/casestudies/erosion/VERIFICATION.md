# Verification: Soil Loss Estimation in Chivi District (RUSLE)

Page: src/pages/cs_erosion.tsx, route /case-studies/chivi-soil-erosion.

## Run order
1. fetch.py: DEM, WorldCover, iSDAsoil texture and organic carbon, CHIRPS mean, ward boundaries, OSM; `fetch.py ee wet` for the Dec to Mar Sentinel-2 NDVI median (366 scenes, 2019/20 to 2023/24, cloud < 30 %, SCL mask).
2. rusle.py: R, K, LS, C, P and A on the 30 m grid, out/factors.json.
3. stats.py: classes, land cover and ward stats, out/stats.json and out/wards.gpkg.
4. wide.py: 90 m GLO-30 DEM around the district, used only for the hillshade outside the district.
5. maps.py, graphs.py, then webp into clean/, grain.py, tag_images.py.
Run with the PROJ_LIB/PROJ_DATA prefix pointing at rasterio's proj_data (PostGIS proj.db clash).

## Checks done
- Mean 5.19 t/ha/yr, median 1.75, total 1.81 Mt/yr over 3 490.4 km² of land (open water 55.5 km² excluded).
- Class areas sum to 3 490.4 km². High + very high 353.3 km² (10.1 %). 8.8 % above 11.2 t/ha/yr. Top 10 % of cells give 61.0 % of loss.
- Factor ranges in Table 2 are p1 to p99 from factors.json.
- Directions in the text checked: DEM mean 925 m in the NW third vs 632 m in the SE; R 1 419 in the north third vs 1 136 in the south.
- Ward 16 centroid lies east of wards 14 and 15. Ward 31 mean C 0.037 vs 0.158 in ward 15 (wooded hills).
- Annual NDVI gave a mean of 12.6 t/ha/yr; rainy-season NDVI is used and the page explains why.

## Open items
- RUSLE does not model gullies; the original idea title said "gully erosion", so the title was changed to soil loss.
- R equation is from the US and uncalibrated for Zimbabwe. K is modelled; 72 810 no-soil cells (rock, water) filled from the nearest cell.
- No field or sediment data to validate. Kusena et al. (2022) give 1.2 to 1.7 t/ha/yr for Upper Runde, lower than here.
- OSM streams download failed, so only main rivers are drawn.
