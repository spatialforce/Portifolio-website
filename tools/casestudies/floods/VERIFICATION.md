# Verification: Lower Save and Muzarabani floods case study (cs_floods.tsx)

## Study areas (exposure.py, data/aoi.gpkg)
- Muzarabani District: 4 267 km2, 29 wards, all in "Centenary/ Muzarabani" (OCHA COD-AB adm3), Mashonaland Central.
- Lower Save: land within 10 km of the Save and lower Runde south of Birchenough Bridge, 4 711 km2, 29 wards: Chiredzi 2 464, Chipinge 1 620, Bikita 536, Buhera 63, Chimanimani 24 km2.
- Elevation (GLO-30): Muzarabani <400 m 28.7 %, 400-600 22.8 %, 600-900 4.7 %, >900 43.6 %, median 517 m. Save <400 46.8 %, 400-600 50.2 %, 600-900 2.5 %, median 405 m.

## Method (flood2.py)
- Sentinel-1 GRD IW VV, 30 m focal median. Flooded: VV < -18 dB, dry-season reference (Jul-Oct 2017-2025, same orbit) > -15 dB, drop > 3 dB, MERIT HAND < 15 m, slope < 5 deg. Normal water: reference < -18 dB.
- Seasons Nov-Apr, 2016/17 to 2025/26.

## Own analysis
(filled from data/season.csv, data/ward.csv after analysis.py)

## External facts
- Chadereka at Musengezi-Hoya confluence; backflow from Cahora Bassa, Zambezi inflows and Kariba releases: Jamba journal (jamba.org.za article 138); Herald "Flood alert for Muzarabani"; NewsDay article 143856.
- 2017: Hoya River Bridge and Nzoumvunda Bridge swept away: The Standard, 6 Aug 2017, "Poverty stalks Muzarabani".
- Cyclone Idai, March 2019: at least 172 dead, ~327 missing, over 270 000 affected in 9 districts, ~122 000 Chipinge, ~115 000 Chimanimani: OCHA flash update 3 (ReliefWeb), ACAPS.
- Tongogara refugee camp flooded and cut off; ~1 060 houses damaged (UNHCR) vs ~1 100 shelters (UNDP); 49 households relocated (OCHA FU3). Copernicus EMSR349.
- January 2026: Manicaland worst affected, Chipinge and Chimanimani among worst hit; 250-300 mm in a week; warnings for Save, Runde, Manyame; at least 109 deaths by 24 Jan, ~1 000 homes destroyed: ReliefWeb FL-2026-000023-ZWE, IFRC MDRZW027.

## Not used
- Frontiers 2023 "17 000 displaced households": event unclear.
- Tiyabenzi dam and veld fire studies dropped.
