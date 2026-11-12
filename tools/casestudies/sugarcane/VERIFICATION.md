# Verification: Sugarcane field monitoring, Triangle and Hippo Valley

Page: `src/pages/cs_sugarcane.tsx`, route `/case-studies/sugarcane-triangle`.

## Run order (from this folder, `python -I`, PROJ_LIB set to rasterio's proj_data)

1. `fetch.py`: Sentinel-2 L2A monthly median NDVI and NDMI at 20 m, Jan 2019 to Dec 2025, cloud and shadow masked with SCL (GEE)
2. `stack.py`: monthly tiles mosaicked to `rast/ndvi_stack.npz` and `rast/ndmi_stack.npz` (84 months)
3. `fetch_rain.py`: CHIRPS monthly rainfall over the estate box
4. `analysis.py`:
   - gap fill
   - cane mask
   - Felzenszwalb fields (5 ha or more)
   - within-field CV, dry-season NDMI, harvest month and weak fields
   - writes `out/fields.gpkg` and `out/stats.json`
5. `figures.py`:
   - three maps (fields, vigour, weak fields) and three charts in `out/`
   - rain correlations and class counts, written to `out/fig_stats.json`

`explore.py` is a quick look only and is not part of the results.

## Map layout

The title sits above the frame. The legend, scale bar, compass, source and author sit in a framed panel under the map, so nothing covers the fields. Legend labels use symbols, and units appear only in the legend title.

## Checked on 2026-11-12, page against `out/stats.json`, `out/fig_stats.json` and `out/fields.gpkg`

- **Fields:** there are 1 947 fields covering 16 272 ha. The median field is 7.0 ha, and the 10th to 90th percentile is 5.3 to 11.7 ha.
- **Clear months:** 99.6 % of the months over cane had a clear value.
- **Harvest:**
  - The peak is September, with 2 238 ha cut in an average year.
  - May to November holds 94.5 % of the harvested area.
- **Season rain (mm):** 384, 472, 759, 436, 403, 434 and 708 for 2019 to 2025, with a mean of 514.
- **Rain links:**
  - r is 0.12 for peak NDVI and −0.21 for dry-season NDMI.
  - The NDMI slope is −0.0055 per year.
- **Vigour:**
  - The median mean peak is 0.785, and the 5th to 95th percentile is 0.753 to 0.817.
  - Class counts are 184, 587, 777, 331 and 68.
- **Within field:**
  - The median CV is 3.1 % and the 90th percentile is 4.4 %.
  - Fields read as uniform at 20 m, so the zone map was dropped.
- **Weak fields (Table 3):**
  - The counts are 1 084, 756, 101 and 6 for 0, 1 to 2, 3 to 4 and 5 or more years.
  - The 6 weak fields cover 42.2 ha.
  - Their peaks are 0.726 to 0.740.
  - Four lie between 31.41 and 31.47° E.
