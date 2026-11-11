# Verification note: Population Distribution, Density and Growth in Zimbabwe

Case study 1. Built 2026-11-11. Every figure used in the case study is listed with its source and the check made against it.

## Census totals

| Figure | Value | Source | Checked against | Result |
|---|---|---|---|---|
| 2022 population | 15 178 979 | ZimStat 2022 PHC Preliminary Report (raw/prelim.pdf), sum of 91 parsed district totals | ZimStat preliminary headline figure; citypopulation.de final census 15 178 957 | Parsed sum equals the headline exactly. Final census is 22 lower; largest district gap 55 (Nyanga). Preliminary figures used throughout. |
| 2012 population | 13 061 239 | citypopulation.de district table (data/citypop_districts.csv) | ZimStat 2012 Census National Report | Sum of 91 districts equals the official total exactly. |
| 2002 population | 11 631 657 | citypopulation.de | Wikipedia Demographics of Zimbabwe, ZimStat 2012 report table | Agree. |
| 1992 population | 10 412 548 | citypopulation.de | Wikipedia, ZimStat 2012 report | Agree. |
| 1982 population | 7 608 432 | citypopulation.de, Wikipedia | One ZimStat table gives 7 546 041 | Disagree. Case study states both values. |
| Growth 2012 to 2022 | 1.51% per year | Computed, exponential rate | ZimStat preliminary report quotes about 1.5% | Agree. |
| Rural share 2022 | 61.4% | Preliminary report section 3.7 | Herald and The Zimbabwean: 67% rural in 2012, 65% in 2002 | Consistent trend direction is not assumed; stated as reported. |
| Sex ratio, households | 92 males per 100 females; 3 818 992 households; 4.0 persons per household | Preliminary report | Herald summary of the release | Agree. |

## Districts and areas

District names in the report were matched to the OCHA COD-AB admin2 layer (91 polygons) with an alias table in match.py and join.py; all 91 matched, no unmatched shapes. Province sums of the matched districts equal the preliminary province totals.

Areas were computed in Africa Albers Equal Area (ESRI:102022). National total 390 772 km², official figure 390 757 km² (difference 0.004%).

2012 figures are reported on 2012 district names. Where boundaries changed between censuses (notably around Harare: Harare Rural, Seke, Goromonzi, Ruwa, Epworth) growth rates include the effect of boundary changes. This is stated in the discussion.

## Dasymetric grid

WorldPop 2020 constrained 100 m (UN adjusted) total 14 862 927. Each district was rescaled to its 2022 census total: ratios 0.853 to 2.382, median 1.029. The highest ratio is Harare Rural, which WorldPop understates.

## Sex ratio

Male and female totals per district parsed from section 4 of the preliminary report text (sexsplit.py, data/sex2022.json). In each district block, male + female is the unique pair summing to the district total. Bubi needed a manual fix (39 063 male, 35 021 female).

Checks: 91 districts sum to 7 289 558 males and 7 889 421 females, which match the national totals in the report exactly; ratio 92.4 (report: 92). Province sums match the report province table. Masvingo 763 537 males and 875 002 females, a gap of 111 465, which matches TellZim News ("over 110k more women than men").

Range 82.3 (Gokwe Centre) to 111.5 (Bubi). 33 districts under 90, 10 at 100 or more; 12 of the 19 Masvingo and Matabeleland South districts under 90.

Migration context (press reports of the census emigration tables): 908 914 emigrants, 773 246 (85%) in South Africa (Sowetan, 7 Sep 2022); Masvingo 153 384 emigrants, 104 716 male (TellZim News); Matabeleland South about 33% of households with a member abroad (Victoria Falls Live). The mining explanation for high-ratio districts is stated in the text as likely, not tested.

## Elevation

Copernicus GLO-30 DEM resampled to 500 m in Earth Engine, used only for the study area map and hillshades.
