# Shurugwi soil loss and gully study: verification

Page: src/pages/cs_shurugwi.tsx (layout: src/pages/casestudy_wide.css, `.rw` prefix). Slug: shurugwi-soil-erosion. Replaces the Chivi study.

Run order: fetch.py (ee, wards, osm) -> wide.py -> rusle.py -> stats.py -> gully.py -> img.py -> maps.py -> graphs.py.

Checked against outputs:
- out/stats.json: land 3 595.3 km2, mean 4.36, median 2.33, 1.57 Mt/yr, 7.9 % above 11.2, top 10 % of cells = 44.2 % of loss. Classes sum to land area; high + very high = 347.3 km2 (9.7 %).
- out/factors.json: 1st-99th percentile ranges in Table 2.
- out/gully.json: SPI threshold 201.6, 1 138 of 32 385 km flagged, 0.32 km/km2, 25.9 % on A >= 10.
- out/wards.gpkg: Table 5 (all 25 ward units). r = 0.23 all, 0.46 rural (graphs.py).
- Direction claims (halves of the grid): elevation N 1 310 / S 1 081 m; R higher N and E; loss N 4.63 / S 4.10, W 4.52 / E 4.21; gully density S 0.36 / N 0.28, E 0.34 / W 0.29.
- Elevation bands: <1 200 m 2 277 km2 (63 %), loss 4.17, gully 0.36, C 0.162; >1 350 m loss 5.04, gully 0.21, C 0.095.
- Map 5 close-up window centre 29.982E 19.903S lies in ward 20 (point-in-polygon).

Limits stated on the page: SPI threshold is relative (top 10 %), not tested against mapped gullies; Esri check is visual only; R equation not calibrated for Zimbabwe.

## Revision 2026-11-13: plain risk maps

Map 4 and the ward map now show **gully risk** instead of flow-path pixels (risk.py, out/grisk.json):
- Length of likely gully paths within 500 m (radius 17 cells) per km² of land; Low < 0.3, Moderate 0.3–0.6, High > 0.6 km/km².
- Low 2 175.5 km² (60.5 %), Moderate 890.5 km² (24.8 %), High 529.4 km² (14.7 %).
- High risk share: below 1 200 m 18.0 %, 1 200–1 350 m 9.5 %, above 1 350 m 8.1 %; south 18.6 / north 10.7; east 16.5 / west 12.8.
- By land cover: bare 43.0, grassland 17.9, shrubland 16.2, cropland 12.5, tree cover 8.4 %.
- 15.1 % of high gully risk area has high or very high soil loss (cls ≥ 4).
- Ward share at high risk: 11 35.8, 7 26.1, 10 24.6, 6 23.2, 20 and 5 21.3; Town 5.5, 18 4.9. r with mean soil loss: 0.48 rural, 0.30 all.

Map 3 shows **soil erosion risk**: soil loss averaged over a 250 m radius, Low < 5, Moderate 5–10, High > 10 t/ha/yr: 73.7 / 22.5 / 3.8 % of land. Table 3 still reports the five unsmoothed classes.
