# Verification: Mazowe Valley case study (cs_mazowe.tsx)

## Own analysis (recomputed from data/ on 2026-11-11)
- Main stem in Zimbabwe 358.6 km, 36 reaches (reaches.py). Corridor 64 683 ha; background band 1-5 km 226 053 ha.
- Corridor bare ha 2000/2009/2017/2025: 1524.5 / 2087.7 / 1628.9 / 2189.8 (bare_by_reach.csv); 2.36 / 3.23 / 2.52 / 3.39 %.
- Background %: 0.64 / 1.08 / 0.25 / 0.58 (bare_background.csv).
- Table 1 districts: recomputed from reaches_corridor.gpkg + bare_by_reach.csv; matches page.
- Table 2 sections: data/section_table.csv (graphs.py).
- Shamva hotspot reaches 14-17: 34.9 -> 143.1 ha; change classes approx. (reprojected pixels): stable 5, new 134, lost 29 ha.
- NDTI per reach (median of yearly medians 2021-2025, >=20 water px): reaches 18-27 all 0.111-0.189; reach 13 0.185; Mudzi 32-36 0.056-0.115; >0.15: 8 reaches; 0.10-0.15: 8.
- Table 3: section medians from ndti_by_reach.csv.
- CHIRPS Nov-Apr corridor mean, 3-season windows: 1026 / 876 / 740 / 664 mm (chirps_corridor.csv).
- Town distances along stem (places.json): Mazowe 26 km (1.2 km off), Bindura 91 km (5.6 km off), Shamva 161 km (8.8 km off).

## External facts
- Catchment ~39 000 km2; Mazowe Dam 1920, ~35 million m3: Wikipedia, Mazowe River.
- ~130 km length in some sources: not reconciled, own 358.6 km used.
- Fidelity 2024 36.5 t, 65% small-scale/artisanal: businesstimes.co.zw/gold-deliveries-to-fidelity-surge/
- 2025 46.7 t, ASM 34.9 t: 360mozambique.com (see reference).
- UZ thesis (handle 10646/3460): artisanal mining overtook agriculture as main livelihood.
- Herald 19 Feb 2018 (EMA): panning rampant in Mazowe, Bindura, Mt Darwin; rivers silted.
- Standard 27 Sep 2020 (ban), 27 Dec 2020 (defiance, heavy equipment). NewsDay 21 Oct 2013 (Chinese miners ordered off).
- SI 188 of 2024 alluvial ban; SI 91 of 2026 state of disaster on 17 rivers incl. Mazowe, extended (NewsDay, Herald). Gazette date differs between sources, so no date given in text.
- CNRG warning on mineral recovery by rehabilitation contractors.
- Charema (2024) Wits: 5 points, Mazowe Dam to ~25 km downstream, metals attributed to informal mining, small sample. Title paraphrased in reference.

## Removed during checking
- Invented second Business Times URL, citrus estate claim, Mazowe Dam Wikipedia page, plateau elevations, Map 4 bridge/longitude locations, "dam water" explanation for low NDTI, claim of greatest turbidity after wetter seasons.

## Caveats stated in text
- 2009 window inflated (Landsat 5/7, background also rises).
- Lower river rise confounded by falling rainfall.
- NDTI relative, uncalibrated, mixed pixels in narrow channels.
