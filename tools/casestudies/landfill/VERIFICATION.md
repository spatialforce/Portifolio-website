# Verification: Landfill Site Selection for Bulawayo

Page: src/pages/cs_landfill.tsx, route /case-studies/bulawayo-landfill.

## Run order
1. fetch.py: DEM, WorldCover, iSDAsoil clay, Open Buildings (confidence 0.75 or more), OSM layers, city boundary.
2. fetch2.py: Sentinel-2 median for May to September 2024, plus basemap tiles.
3. prep.py: distance rasters (settlements, water, roads, runways) and the city mask.
4. ahp.py: weights and consistency ratio.
5. overlay.py: factor scores, suitability score and classes, candidate sites with distance to runway, landfill check, written to out/results.json.
6. maps.py, then graphs.py, then convert to webp, then grain.py, then tag_images.py.

## Checks done
- AHP: λmax 6.074, CI 0.0148, CR 0.0119 with RI 1.24 for n = 6. This is under 0.10.
- The factor breaks in Table 2 match cls() in overlay.py. The land-cover codes are WorldCover 60/30 → 5, 20 → 4, 40 → 3, 10 → 1, other → 1.
- No land is excluded or capped. The weighted score is classified as it is across the whole city: 237.2 + 120.4 + 136.7 + 36.2 + 15.2 = 545.7 km². High and very high together are 51.4 km² (9.4 %).
- Map 1: rivers and roads drawn at reduced opacity, Zimbabwe inset on top, legend below, airport symbol removed.
- The constraint map and the exclusions figure were dropped. Maps on the page are 1 study area, 2 factors, 3 suitability, 4 sites; figures are 1 weights, 2 classes.
- Sites C (1.0 km) and D (1.5 km) lie within the 3 km FAA bird-hazard distance of a runway (AC 150/5200-33B, 2007). The page says so in the results, discussion and recommendations.
- Site distances to settlements and roads are means over each site, not minimums. The page says so.
- Population of 665 952 is from the ZimStat 2022 census.
- Richmond facts (30 ha, cells almost full, about 242 waste pickers) are from the UN-Habitat 2022 Bulawayo PDF.
- The 3 km airport distance follows FAA AC 150/5200-33B (2007), which sets 10 000 ft for waste sites near airports.

## Open items
- Richmond has no outline in OSM. It is drawn as a 30 ha circle around the UN-Habitat coordinate (28°32′E, 20°05′S), so its scores are approximate. The OSM landfill polygon is a separate site on the eastern edge (6.9 ha).
- The exact title of the UN-Habitat report has not been confirmed. The reference uses "Waste Wise Cities Tool: Bulawayo, Zimbabwe" and the URL is correct.
- A long straight strip next to Site B looks like an airstrip that is not in OSM. If it is one, Site B would also be near a runway. Check this on high-resolution imagery.
- The data years are mixed (WorldCover 2021, Open Buildings 2023, Sentinel-2 2024, OSM 2026), so the map titles carry no year.
- Zimbabwe has no published landfill siting distances. The factor breaks follow common values from siting studies.
- Groundwater depth and geology were not mapped.
