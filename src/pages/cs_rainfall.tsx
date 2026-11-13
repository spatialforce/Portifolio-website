import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/rainfall-zimbabwe/map1_study_area.webp";
import map2 from "../assets/casestudies/rainfall-zimbabwe/map2_mean.webp";
import map3 from "../assets/casestudies/rainfall-zimbabwe/map3_variability.webp";
import map4 from "../assets/casestudies/rainfall-zimbabwe/map4_drought_seasons.webp";
import map5 from "../assets/casestudies/rainfall-zimbabwe/map6_driest_season.webp";
import map6 from "../assets/casestudies/rainfall-zimbabwe/map5_drought_frequency.webp";
import map7 from "../assets/casestudies/rainfall-zimbabwe/map7_trend_district.webp";
import fig1 from "../assets/casestudies/rainfall-zimbabwe/fig2_monthly.webp";
import fig2 from "../assets/casestudies/rainfall-zimbabwe/fig1_national_series.webp";

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

function Rows({ rows, num }: { rows: string[][]; num: number }) {
  return <>{rows.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}</tr>)}</>;
}

// Table 1: province, normal mm, standard deviation mm, CV %
const T1: string[][] = [
  ["Harare", "817", "181", "22.2"], ["Manicaland", "775", "196", "25.3"], ["Mashonaland East", "758", "170", "22.5"],
  ["Mashonaland Central", "738", "147", "19.9"], ["Mashonaland West", "726", "137", "18.9"], ["Midlands", "640", "146", "22.8"],
  ["Matabeleland North", "607", "144", "23.7"], ["Bulawayo", "525", "143", "27.2"], ["Masvingo", "523", "156", "29.9"],
  ["Matabeleland South", "450", "134", "29.7"],
];

// Table 2: driest and wettest national seasons
const DRY: string[][] = [
  ["1991/92", "359.8", "56.9"], ["2023/24", "435.9", "68.9"], ["1994/95", "437.1", "69.1"], ["2001/02", "464.7", "73.5"],
  ["2018/19", "473.4", "74.9"], ["2004/05", "477.8", "75.6"], ["2002/03", "501.8", "79.4"],
];
const WET: string[][] = [
  ["2016/17", "969.0", "153.3"], ["1999/00", "841.6", "133.1"], ["2007/08", "772.8", "122.2"], ["1996/97", "767.2", "121.3"],
];

// Table 3: national extent of the five drought seasons
const T3: string[][] = [
  ["1991/92", "56.9", "99.8", "90.4", "34.4"], ["1994/95", "69.1", "88.5", "67.5", "1.3"], ["2001/02", "73.5", "92.2", "64.9", "0.0"],
  ["2018/19", "74.9", "90.9", "57.0", "0.1"], ["2023/24", "68.9", "97.8", "72.1", "2.9"],
];

// Table 4: province rainfall as % of normal in each drought season, and the driest season of the province
const T4: string[][] = [
  ["Harare", "67", "61", "62", "84", "68", "1994/95"], ["Manicaland", "44", "70", "91", "92", "70", "1991/92"],
  ["Mashonaland East", "56", "65", "75", "87", "66", "1991/92"], ["Mashonaland Central", "58", "67", "70", "86", "68", "1991/92"],
  ["Mashonaland West", "67", "59", "71", "70", "75", "1994/95"], ["Midlands", "60", "68", "70", "69", "75", "1991/92"],
  ["Matabeleland North", "72", "63", "67", "65", "58", "2023/24"], ["Bulawayo", "58", "86", "73", "79", "64", "1991/92"],
  ["Masvingo", "33", "81", "79", "69", "77", "1991/92"], ["Matabeleland South", "50", "90", "69", "75", "65", "1991/92"],
];

// Table 5: drought seasons, Sen slope mm per decade, Mann-Kendall p
const T5: string[][] = [
  ["Harare", "4", "0.7", "0.97"], ["Manicaland", "5", "5.7", "0.87"], ["Mashonaland East", "5", "11.1", "0.76"],
  ["Mashonaland Central", "4", "2.2", "0.87"], ["Mashonaland West", "5", "−3.2", "0.89"], ["Midlands", "6", "19.7", "0.47"],
  ["Matabeleland North", "8", "−3.0", "0.94"], ["Bulawayo", "6", "2.5", "0.92"], ["Masvingo", "5", "1.3", "0.94"],
  ["Matabeleland South", "6", "9.5", "0.71"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;
const SRC = "Source: CHIRPS v2.0 (Funk et al., 2015), area-weighted means of the cells inside each province; normal 1991/92 to 2020/21.";

export default function RainfallCaseStudy() {
  return (
    <>
      <CaseLayout slug="rainfall-zimbabwe">
        <h1>Rainfall Variability and Drought Patterns in Zimbabwe from the 1991/92 to 2024/25 Agricultural Seasons</h1>
        <p className="tc__by">Seasonal rainfall, variability and drought frequency over 34 seasons.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (26 July 2025)</p>
        <Facts rows={[["Place", "Zimbabwe, by province"], ["Period", "1991/92 to 2024/25, 34 seasons"], ["Data", "CHIRPS v2.0 rainfall, 0.05° grid"], ["Methods", "Rainfall anomaly analysis, coefficient of variation, Mann-Kendall trend test"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Most farming in Zimbabwe depends on rain that falls between October and April. When the season fails, maize harvests, livestock, water supply and hydropower all suffer at once. The drought of 1991/92 was described as the worst in living memory in southern Africa (FAO, 1992), and in April 2024 the government declared a state of disaster after the El Niño season of 2023/24 left most of the country with well below normal rainfall (NBC News, 2024).</p>
        <p>Rain gauges in Zimbabwe are few and unevenly spread, which makes it difficult to say how often and where droughts occur. This case study analyses seasonal rainfall over the 34 seasons from 1991/92 to 2024/25, using a gridded record that combines satellite estimates with station data. It examines how much rain falls, how reliable it is and whether it has changed, and where drought has been most severe and most frequent.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To assess the monthly timing and spatial distribution of mean rainfall across Zimbabwe over the 1991/92 to 2020/21 normal period.</li>
          <li>To analyse the year-to-year variability of October to April rainfall nationally, by province and across the country.</li>
          <li>To evaluate the severity and spatial extent of the national drought seasons between 1991/92 and 2024/25, and which season was the driest at each location.</li>
          <li>To examine how often drought seasons occurred across the country over the 34 seasons.</li>
          <li>To assess whether October to April rainfall changed significantly over the 34 seasons nationally, by province and by district.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Zimbabwe is a landlocked country of about 390 757 km² in southern Africa, between the Zambezi and Limpopo rivers, and a member of the Southern African Development Community (Map 1). The highveld above 1 200 m runs from south-west to north-east across the centre of the country, the Eastern Highlands along the Mozambique border rise above 2 500 m, and the lowveld of the south and south-east and the Zambezi valley in the north lie mostly below 900 m. The country has ten provinces and 91 districts.</p>
        <p>Rain falls mainly from November to March, when the Inter-Tropical Convergence Zone moves south over the country. Farming land is classed into five natural regions on the basis of rainfall. Region I in the Eastern Highlands receives more than 1 000 mm a year, while Region V in the low-lying south and north-west receives less than 450 mm and is suited only to extensive livestock and wildlife (FAO, 2006).</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p>Rainfall was taken from the Climate Hazards Group InfraRed Precipitation with Station data, version 2.0 (CHIRPS), which blends satellite cold cloud duration estimates with gauge records on a 0.05° grid, about 5.5 km (Funk et al., 2015). Pentad (five-day) totals were summed for each season from 1 October to 30 April, giving 34 seasons from 1991/92 to 2024/25. The data were processed in Google Earth Engine and Python. Only grid cells whose centre falls inside the national boundary were used. Province and district values were the means of the cells inside each unit of the OCHA boundaries (OCHA, 2023), weighted by the cosine of latitude so that each cell counts in proportion to its area.</p>
        <p>The steps used to meet each objective are described below in the order of the objectives. Areas, percentages of land and national values were all area weighted. All maps after Map 1 are drawn over an OpenStreetMap basemap (Humanitarian style) for orientation only.</p>
        <h3>Mean rainfall and its distribution</h3>
        <p>Monthly totals for 1991 to 2020 were averaged for each calendar month and then over the country to give the mean monthly rainfall of Figure 1 and the share of the annual total that falls from October to April. The seasonal normal of each cell was the mean of its 30 October to April totals from 1991/92 to 2020/21, the standard reference period of the World Meteorological Organization. The normal was classed into 100 mm and 200 mm bands, and isohyets were drawn every 200 mm from a lightly smoothed copy of the grid (Gaussian filter of 1.2 cells) so that single-cell noise does not break the lines. Provincial normals were the area-weighted means of the cells in each province (Table 1).</p>
        <h3>Variability between seasons</h3>
        <p>The standard deviation of the seasonal totals and the coefficient of variation (CV), the standard deviation divided by the mean, were calculated for the national series, for each province and for every cell over the normal period. The national series of Figure 2 and the driest and wettest seasons of Table 2 come from the area-weighted national total of each season. The cell CV was drawn as a continuous surface clipped to the boundary, with lines every 5% drawn from a smoothed copy (Gaussian filter of 2.0 cells). The share of each province in each CV class was counted cell by cell rather than read from the map.</p>
        <h3>Severity and extent of droughts</h3>
        <p>Each season at each cell was expressed as a percentage of that cell's normal. A season below 75% of normal was taken as a drought season, and a national drought season as one whose national total fell below 75% of the national normal. For each national drought, the national percentage of normal and the share of land below 90%, 75% and 50% of normal were calculated (Table 3), and the percentage of normal of each province was calculated from its own total (Table 4). The five droughts were drawn on a common scale in Map 4. For Map 5 the season with the lowest October to April total over all 34 seasons was found at every cell, and the share of land in which each season was the driest was counted.</p>
        <h3>Frequency of droughts</h3>
        <p>The number of seasons below 75% of the cell normal was counted at every cell over all 34 seasons and grouped into classes of two seasons (Map 6). The share of land in each class and the provinces in which the highest classes fall were counted from the grid. The number of drought seasons in each provincial total was also counted (Table 5).</p>
        <h3>Trends</h3>
        <p>The trend over the 34 seasons was estimated with the Sen slope, the median of the slopes between all pairs of seasons, which is not affected by single extreme seasons, and expressed in millimetres per decade. Its significance was tested with the Mann-Kendall test at the 5% level. The test was applied to the national series, to each province, to the area-weighted series of each of the 91 districts (Map 7) and to every grid cell.</p>
        <h3>Reliability of the rainfall data</h3>
        <p>The rainfall data have been tested against gauges in Zimbabwe. A comparison with 30 years of daily station data found substantial agreement (Scientific African, 2023), while a study of a mountainous catchment in the east found weak agreement at the daily scale (Performance evaluation, 2024). Seasonal totals are less affected by these daily errors, but values in the Eastern Highlands should be treated with caution.</p>

        <h2>5 Results</h2>
        <h3>Spatial distribution of mean seasonal rainfall</h3>
        <p>Almost all rain falls between October and April (Figure 1). January is the wettest month with a national mean of 163.3 mm, followed by December with 149.5 mm and February with 127.1 mm, while May to September together receive 15.4 mm. The October to April season holds 630 mm of the 645 mm annual mean, or 98% of the yearly total.</p>
        <Fig src={fig1} cap="Figure 1. Mean monthly rainfall of Zimbabwe, July to June (1991 to 2020)." />
        <p>The national normal for October to April was 632 mm. The isohyets on Map 2 show rainfall decreasing from the north-east and east towards the south and west. The wettest areas are the Eastern Highlands, where cell values reach 2 456 mm, followed by the Harare plateau and northern Mashonaland at 700 mm to 900 mm. Rainfall falls below 600 mm over most of Matabeleland, Midlands south of Gweru and Masvingo, and below 400 mm in the southern lowveld, where the lowest cell received 197 mm. By province the normal ranged from 817 mm in Harare to 450 mm in Matabeleland South (Table 1).</p>
        <Fig src={map2} cap="Map 2. Mean Seasonal Rainfall Map (1991–2020), October to April totals with isohyets." />

        <h3>Interannual variability of seasonal rainfall</h3>
        <p>Nationally, the seasonal total had a standard deviation of 137 mm and a CV of 21.7%, and ranged from 359.8 mm in 1991/92 to 969.0 mm in 2016/17 (Figure 2, Table 2). By province the CV was lowest in Mashonaland West (18.9%) and Mashonaland Central (19.9%) and highest in Masvingo (29.9%) and Matabeleland South (29.7%) (Table 1).</p>
        <p>Map 3 shows that variability rises steadily from north to south. A CV below 21% covers 15% of the country, almost all of it in Mashonaland West, where it covers 67% of the province, and Mashonaland Central (47%). A CV of 30% or more covers 83% of Masvingo and 65% of Matabeleland South, and 4% of the country has a CV above 35%. The areas with the least rain therefore also have the least reliable rain.</p>
        <Fig src={map3} cap="Map 3. Rainfall Variability Map (1991–2020), coefficient of variation of October to April totals with lines every 5%." />
        <p className="tc__cap">Table 1. Mean seasonal rainfall and its variability by province (1991/92 to 2020/21)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Province</th><th className="n">Normal (mm)</th><th className="n">Standard deviation (mm)</th><th className="n">Coefficient of variation (%)</th></tr></thead>
            <tbody>
              <Rows rows={T1} num={1} />
              <tr className="t"><td>Zimbabwe</td><td className="n">632</td><td className="n">137</td><td className="n">21.7</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>
        <Fig src={fig2} cap="Figure 2. National October to April rainfall (1991/92 to 2024/25) with the 1991–2020 normal and 75% of normal." />
        <p className="tc__cap">Table 2. Driest and wettest seasons, national October to April rainfall (1991/92 to 2024/25)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Season</th><th className="n">Rainfall (mm)</th><th className="n">Percent of normal</th></tr></thead>
            <tbody>
              <tr><td colSpan={3}><i>Driest</i></td></tr>
              <Rows rows={DRY} num={1} />
              <tr><td colSpan={3}><i>Wettest</i></td></tr>
              <Rows rows={WET} num={1} />
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: CHIRPS v2.0 (Funk et al., 2015); normal 1991/92 to 2020/21 = 632.3 mm.</p>

        <h3>Severity and extent of the drought seasons</h3>
        <p>Five seasons fell below 75% of normal nationally: 1991/92, 1994/95, 2001/02, 2018/19 and 2023/24. The 1991/92 drought was the most severe by every measure. The country received 56.9% of normal, while 90% of the land was below 75% of normal and 34% was below half (Table 3). The 2023/24 season was the second driest at 68.9%, with 72% of the land below 75% of normal but only 3% below half. In 2001/02 and 2018/19 the national totals were just below the threshold and almost no land fell below half of normal.</p>
        <p className="tc__cap">Table 3. Severity and extent of the national drought seasons (1991/92 to 2024/25)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Season</th><th className="n">National rainfall (% of normal)</th><th className="n">Land below 90% of normal (%)</th><th className="n">Land below 75% of normal (%)</th><th className="n">Land below 50% of normal (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: CHIRPS v2.0 (Funk et al., 2015); land shares are area weighted; normal of each cell 1991/92 to 2020/21.</p>
        <p>The five droughts struck different parts of the country (Map 4, Table 4). In 1991/92 the deficit was deepest in the south and east: Masvingo received 33% of normal and 99% of the province was below half, Manicaland received 44% and Matabeleland South 50%, while Matabeleland North received 72%. In 1994/95 the pattern was reversed. The north was driest, with Mashonaland West at 59% and Harare at 61%, and the south was close to normal, with Matabeleland South at 90%. In 2001/02 the deficit was greatest in Harare (62%) and the west, while Manicaland received 91%. In 2018/19 the west and centre were driest, Matabeleland North at 65% and Masvingo and Midlands at 69%, while the north-east was close to normal. In 2023/24 Matabeleland North was the driest province at 58% of normal, and 15% of it received less than half.</p>
        <Fig src={map4} cap="Map 4. Drought Season Rainfall Anomaly Maps (1991–2024), October to April rainfall as a percentage of the 1991–2020 normal in the five national drought seasons." />
        <p className="tc__cap">Table 4. Seasonal rainfall as a percentage of normal by province in the five national drought seasons</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Province</th><th className="n">1991/92</th><th className="n">1994/95</th><th className="n">2001/02</th><th className="n">2018/19</th><th className="n">2023/24</th><th className="n">Driest season</th></tr></thead>
            <tbody>
              <Rows rows={T4} num={1} />
              <tr className="t"><td>Zimbabwe</td><td className="n">57</td><td className="n">69</td><td className="n">74</td><td className="n">75</td><td className="n">69</td><td className="n">1991/92</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>
        <p>Map 5 shows which season was the driest on record at each location. The 1991/92 drought was the driest over 59% of the land, covering most of the east and south. The 1994/95 season was the driest over 20%, mostly in the north, where it was the driest season for Harare and Mashonaland West, and the 2023/24 season over 13%, almost all of it in Matabeleland North. The most severe drought is therefore not the same everywhere.</p>
        <Fig src={map5} cap="Map 5. Driest Season Map (1991–2025), season with the lowest October to April total at each location." />

        <h3>Frequency of drought seasons</h3>
        <p>Every location had between two and twelve drought seasons in the 34 years (Map 6). Most of the land (77%) had between four and seven. Eight or more drought seasons occurred over 17% of the land, and 91% of that area lies in three provinces: Masvingo, Matabeleland South and Matabeleland North. Only 6% of the land had two or three drought seasons, mostly in Mashonaland West, where this applies to 28% of the province. By province, Matabeleland North had the most drought seasons in its provincial total, eight, and Harare and Mashonaland Central the fewest, four (Table 5).</p>
        <Fig src={map6} cap="Map 6. Drought Frequency Map (1991–2025), number of seasons below 75% of normal." />

        <h3>Trends in seasonal rainfall</h3>
        <p>No significant trend was found at any scale. The national Sen slope was +5.0 mm per decade with a Mann-Kendall p of 0.94. Provincial slopes ranged from −3.2 mm per decade in Mashonaland West to +19.7 mm in Midlands, and no province had a p below 0.47 (Table 5). Of the 91 districts 58 had a positive slope and 33 a negative one (Map 7). The largest decreases among rural districts were in Zaka, −17.5 mm per decade, Shamva, −16.3 mm, Kariba, −12.6 mm, Bikita and Lupane, and the largest increases in Chikomba, +25.7 mm, Mangwe, +23.1 mm, Hwedza and Bulilima. The lowest p of any district was 0.37, in Mangwe, and no grid cell had a significant trend at the 5% level. These slopes are small compared with the year-to-year range of several hundred millimetres and cannot be distinguished from chance.</p>
        <Fig src={map7} cap="Map 7. Seasonal Rainfall Trend By District Map (1991–2025), Sen slope of October to April totals." />
        <p className="tc__cap">Table 5. Drought seasons and trend in seasonal rainfall by province (1991/92 to 2024/25)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Province</th><th className="n">Seasons below 75% of normal</th><th className="n">Sen slope (mm per decade)</th><th className="n">Mann-Kendall p</th></tr></thead>
            <tbody>
              <Rows rows={T5} num={1} />
              <tr className="t"><td>Zimbabwe</td><td className="n">5</td><td className="n">5.0</td><td className="n">0.94</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>

        <h2>6 Discussion</h2>
        <p>The rainfall normal found here agrees with other sources. The 645 mm annual mean is close to the 658 mm given for 1961 to 2022 by The Global Economy (2024) and the roughly 670 mm of the World Bank Climate Change Knowledge Portal (World Bank, 2024). The 1 000 mm and 450 mm limits of Natural Regions I and V also match the isohyets of Map 2.</p>
        <p>The drought results agree with the historical record. The 1991/92 drought cut maize production by about three quarters and required large cereal imports across the region (FAO, 1992), and it was the most severe and most widespread event found here. Reports at the time of the 2024 disaster declaration stated that more than 80% of the country had received below normal rainfall (NBC News, 2024), which is consistent with the 98% of land found here below 90% of normal. Because each drought struck a different region, a response based on national totals or on the pattern of a previous drought would miss the areas hit hardest in a given year: in 2023/24 the worst affected province was Matabeleland North, which had come through 1991/92 better than any other.</p>
        <p>The south of the country combines low rainfall, high variability and frequent drought. In Masvingo and Matabeleland South a normal season is around 450 mm to 520 mm, and with a CV near 30% a season of 300 mm or less is not unusual. This supports the long-held view that these areas are unsuited to rain-fed maize and better suited to small grains, livestock and wildlife. Matabeleland North is drier than its mean suggests: its CV is moderate, but it had more drought seasons than any other province.</p>
        <p>The absence of a trend should not be read as an absence of climate change. Thirty-four seasons is a short record for a variable this noisy, and the district slopes form no coherent regional pattern, which is what random variation would produce. The study looked only at seasonal totals. Changes in the start of the season, the length of dry spells within the season or the intensity of rainfall, which matter greatly to farmers, were not tested here. The satellite estimates are also less accurate in mountainous areas such as the Eastern Highlands, where gauges are sparse.</p>

        <h2>7 Recommendations</h2>
        <p>Drought early warning and relief planning should use in-season maps of percent of normal rainfall like Map 4, not only national totals, so that the worst affected districts are identified early. The 2023/24 season shows that the hardest hit area can be one that escaped earlier droughts.</p>
        <p>In Masvingo and Matabeleland South, where the CV is near 30% and large areas had eight or more drought seasons, agricultural support should favour drought-tolerant small grains, short-season varieties, water harvesting and livestock, and should include crop and livestock insurance.</p>
        <p>In Matabeleland North, which had the most drought seasons of any province and the worst deficit of 2023/24, water supply for people, livestock and wildlife should be planned for repeated failed seasons, with boreholes and storage maintained in advance.</p>
        <p>The Meteorological Services Department should share its station records so that the satellite estimates can be validated and corrected locally, and the analysis should be extended to the onset of the season, dry spells and rainfall intensity, where change may be detectable even though seasonal totals show none.</p>

        <h2>8 Conclusion</h2>
        <p>The study met its five objectives. First, nearly all of the annual rain (98%) falls from October to April, peaking in January, and the mean seasonal total is 632 mm nationally and ranges from more than 1 000 mm in the Eastern Highlands to less than 400 mm in the southern lowveld, with provincial normals from 817 mm in Harare to 450 mm in Matabeleland South. Second, seasonal rainfall varies by about a fifth from year to year nationally and by close to 30% in Masvingo and Matabeleland South, so the driest areas are also the least reliable. Third, of the five national droughts 1991/92 was the most severe, with 90% of the land below 75% of normal, and 2023/24 the second, with 72%; each drought affected a different region, the south and east in 1991/92, the north in 1994/95 and the west in 2023/24. Fourth, most of the country had four to seven drought seasons in 34 years, and parts of Masvingo, Matabeleland South and Matabeleland North had eight or more. Fifth, no significant trend was found nationally, in any province, in any district or in any grid cell. The main problem for Zimbabwe is therefore the size and frequency of the swings between seasons, and drought planning should be directed first at the south and west of the country.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>FAO (1992) An update on the 1991/92 drought. In: The drought in southern Africa and how REWS enabled timely management. Food and Agriculture Organization, Rome. <A href="https://www.fao.org/4/x5558e/X5558e01.htm" /></p>
          <p>FAO (2006) Fertilizer use by crop in Zimbabwe. Food and Agriculture Organization, Rome. <A href="https://www.fao.org/4/a0395e/a0395e03.htm" /></p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D., Verdin, J., Shukla, S., Husak, G., Rowland, J., Harrison, L., Hoell, A. and Michaelsen, J. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>NBC News (2024) Zimbabwe declares drought a national disaster as El Niño hits southern Africa. 3 April 2024. <A href="https://www.nbcnews.com/news/world/zimbabwe-el-nino-africa-drought-disaster-humanitarian-aid-rcna146347" /></p>
          <p>OCHA (2023) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>Performance evaluation (2024) Performance evaluation of multiple satellite rainfall products in mountainous catchment of Eastern Zimbabwe. <A href="https://ouci.dntb.gov.ua/works/4YZ2w3Vl" /></p>
          <p>Scientific African (2023) Is climate really changing? Insights from analysis of 30-year daily CHIRPS and station rainfall data in Zimbabwe. Scientific African. <A href="https://doaj.org/article/7233224517104e9a8da0eec428f4057e" /></p>
          <p>The Global Economy (2024) Zimbabwe: precipitation. <A href="https://www.theglobaleconomy.com/Zimbabwe/precipitation/" /></p>
          <p>World Bank (2024) Zimbabwe: climatology. Climate Change Knowledge Portal. <A href="https://climateknowledgeportal.worldbank.org/node/4526" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
