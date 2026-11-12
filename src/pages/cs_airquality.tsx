import SiteNav, { SiteFooter } from "./SiteChrome";
import "./casestudy.css";
import map1 from "../assets/casestudies/hwange-air/map1_study_area.webp";
import map2 from "../assets/casestudies/hwange-air/map2_no2_post.webp";
import map3 from "../assets/casestudies/hwange-air/map3_no2_change.webp";
import map4 from "../assets/casestudies/hwange-air/map4_so2_post.webp";
import map5 from "../assets/casestudies/hwange-air/map5_exposure.webp";
import fig1 from "../assets/casestudies/hwange-air/fig1_monthly.webp";
import fig2 from "../assets/casestudies/hwange-air/fig2_annual.webp";
import fig3 from "../assets/casestudies/hwange-air/fig3_season.webp";
import fig4 from "../assets/casestudies/hwange-air/fig4_exposure.webp";

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

function Rows({ rows, num }: { rows: string[][]; num: number }) {
  return <>{rows.map((r) => <tr key={r.join("|")}>{r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}</tr>)}</>;
}

// Table 1: data
const T1: string[][] = [
  ["Sentinel-5P TROPOMI tropospheric NO₂ column (offline, Level 3)", "5.5 km by 3.5 km (7 km by 3.5 km before August 2019), gridded to 0.01°", "Daily, 2019 to 2025"],
  ["Sentinel-5P TROPOMI total SO₂ column (offline, Level 3)", "5.5 km by 3.5 km (7 km by 3.5 km before August 2019), gridded to 0.01°", "Daily, 2019 to 2025"],
  ["MODIS active fires (FIRMS)", "1 km", "Daily, 2019 to 2025"],
  ["WorldPop constrained population", "100 m, summed to 0.01°", "2020"],
  ["OpenStreetMap power station and settlement locations", "Points", "2026"],
];

// Table 2: before and after enhancement
const T2: string[][] = [
  ["NO₂", "Hwange", "8.3", "16.6", "+8.2", "+99", "< 0.001"],
  ["NO₂", "Maamba (control)", "0.6", "1.0", "+0.4", "—", "0.36"],
  ["SO₂", "Hwange", "48.6", "99.6", "+51.0", "+105", "< 0.001"],
  ["SO₂", "Maamba (control)", "−14.7", "−5.9", "+8.8", "—", "0.29"],
];

// Table 3: by fire season
const T3: string[][] = [
  ["NO₂", "December to May (few fires)", "7.5", "12.5", "+5.0", "< 0.001"],
  ["NO₂", "June to November (fire season)", "9.2", "20.6", "+11.4", "< 0.001"],
  ["SO₂", "December to May (few fires)", "44.6", "85.8", "+41.2", "0.002"],
  ["SO₂", "June to November (fire season)", "52.6", "113.4", "+60.8", "< 0.001"],
];

// Table 4: places
const T4: string[][] = [
  ["Hwange Power Station", "32.3", "48.0", "+49", "123.6", "203.6"],
  ["Hwange town", "24.1", "34.4", "+43", "74.1", "137.1"],
  ["Dete (about 50 km south-east)", "14.8", "17.1", "+16", "—", "—"],
  ["Victoria Falls (about 85 km north-west)", "16.8", "18.9", "+12", "—", "—"],
  ["Background ring (80 to 150 km)", "14.1", "15.2", "+8", "30.8", "25.8"],
];

// Table 5: exposure
const T5: string[][] = [
  ["Area above 1.5 × background (km²)", "790", "1 660"],
  ["People above 1.5 × background", "24 100", "38 400"],
  ["People above 2 × background", "8 200", "20 500"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function AirQualityCaseStudy() {
  return (
    <>
      <SiteNav />
      <article className="cs">
        <h1>Nitrogen Dioxide and Sulphur Dioxide Pollution from the Hwange Thermal Power Station Expansion Using Sentinel-5P (2019 to 2025)</h1>
        <p className="cs__by">Kudzanai Chakavarika. Case study 14. November 2026.</p>

        <h2>Introduction</h2>
        <p>Hwange Thermal Power Station in Matabeleland North is the largest coal-fired power station in Zimbabwe. Its six original units (four of 120 MW and two of 220 MW) were joined in 2023 by Units 7 and 8, two new units with a combined rating of about 600 MW, built at a cost of about US$1.4 billion. Unit 7 was synchronised to the grid on 20 March 2023 (Mining Index, 2023a) and Unit 8 first reached its full output of 355 MW on 14 June 2023 (Mining Index, 2023b). Burning coal releases nitrogen oxides and sulphur dioxide, both of which harm the lungs at high concentration and form fine particles and acid deposition downwind. No continuous public air quality record for Hwange could be found, so the people of Hwange town, Lukosi and the surrounding villages have no published measurement of what the expansion has done to the air they breathe.</p>
        <p>The TROPOMI instrument on the Sentinel-5P satellite has measured nitrogen dioxide (NO₂) and sulphur dioxide (SO₂) over the whole Earth every day since 2018, at a resolution of a few kilometres (Veefkind et al., 2012). It measures the amount of gas in the column of air above each point, not the concentration at street level, but it has been used widely to locate and track emissions from large power stations (Beirle et al., 2019; Fioletov et al., 2016). This case study uses seven years of TROPOMI measurements to compare the air over Hwange before and after Units 7 and 8, with the Maamba coal power station in Zambia, which did not change its capacity in the same period, as a control.</p>

        <h2>Objectives</h2>
        <ol>
          <li>To analyse the spatial distribution of NO₂ and SO₂ around Hwange Thermal Power Station after Units 7 and 8 came into service.</li>
          <li>To evaluate the change in NO₂ and SO₂ over Hwange between 2019 to 2022 and 2024 to 2025, against a background and a control power station.</li>
          <li>To examine how far the seasonal effect of bush fires accounts for the NO₂ signal at the power station.</li>
          <li>To assess the number of people living where NO₂ is well above the regional background.</li>
        </ol>

        <h2>Study area</h2>
        <p>Hwange Thermal Power Station (18.38° S, 26.47° E) lies on the edge of Hwange town, about 85 km south-east of Victoria Falls and on the northern side of Hwange National Park. The town grew around the colliery, and the area now holds several other coal users: coke batteries built from 2021 (The Herald, 2021) and a smaller power station mapped in OpenStreetMap as Zimbabwe ZhongXin, about 9 km north-west of the power station. The six original units were built between 1973 and 1987 without equipment to remove sulphur dioxide (Mining Index, 2024). Maamba Collieries power station in southern Zambia (17.35° S, 27.19° E), about 140 km north-east of Hwange, has run its 300 MW first phase since 2016; work on a second phase began in August 2024 and is not yet complete (Lusaka Times, 2024). Map 1 shows the study area.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>Data and methods</h2>
        <p className="cs__cap">Table 1. Data used in the study</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: Copernicus Sentinel-5P (van Geffen et al., 2022; Theys et al., 2017); FIRMS (Giglio et al., 2016); WorldPop (Bondarenko et al., 2020); OpenStreetMap contributors. All satellite data were processed in Google Earth Engine (Gorelick et al., 2017).</p>

        <h3>Spatial distribution of NO₂ and SO₂</h3>
        <p>Daily TROPOMI columns were averaged over each period on a 0.01° grid (about 1 km), giving one mean for 2019 to 2022 and one for 2024 to 2025. 2023 was left out of both periods because the two units were being commissioned through the year. Values are in micromoles per square metre (µmol/m²); one Dobson unit equals 446 µmol/m². The change map subtracts the drift of the background ring between the two periods, so that a change shown at Hwange is a change relative to the region, not a change in the whole atmosphere.</p>

        <h3>Change against a background and a control</h3>
        <p>For every month from January 2019 to December 2025 the mean column was taken inside a 15 km circle round each power station and inside a ring 80 to 150 km from Hwange, with 60 km round Maamba removed. The enhancement is the source zone minus the ring, which removes weather and regional changes that affect the whole area. The 48 months before and the 24 months after were compared with Welch's t-test. Maamba is a control: if the enhancement rose at both stations, the cause would more likely be in the method or the region than at Hwange. The difference between the change at Hwange and the change at Maamba (a difference in differences) is the part of the rise that the control does not explain.</p>

        <h3>Bush fires</h3>
        <p>Grass and woodland fires release NO₂ across the region from May to October. MODIS fire detections within 80 km of the power station were counted each month, the correlation of fire with the background and with the enhancement was measured (Spearman's rank), and the before and after comparison was repeated for the months with few fires (December to May) and the fire season (June to November).</p>

        <h3>Population exposure</h3>
        <p>Cells where the 2024 to 2025 mean NO₂ column was more than 1.5 times and 2 times the background mean were overlaid on the WorldPop 2020 constrained population, which places people only on mapped buildings. The same was done for 2019 to 2022 using that period's background. The population is held at 2020 in both periods, so any change in the count comes only from the change in the pollution footprint. WorldPop covers Zimbabwe only, so people in Zambia are not counted.</p>

        <h2>Results</h2>
        <h3>Distribution of NO₂ and SO₂</h3>
        <p>In 2024 to 2025 the highest NO₂ column in the study area was 74.3 µmol/m², about 5 km south-west of the power station, nearly five times the regional background of 15.2 µmol/m² (Map 2). The plume spreads to the south-west and west of the station, consistent with winds from the north-east, and does not centre on the ZhongXin plant to the north-west. Over the power station itself the mean was 48.0 µmol/m², and over Hwange town 34.4 µmol/m².</p>
        <Fig src={map2} cap="Map 2. Nitrogen Dioxide Column Map (2024 to 2025), mean tropospheric NO₂ from Sentinel-5P." />
        <p>SO₂ follows the same pattern but is noisier, because the SO₂ signal is closer to the detection limit of the instrument (Map 4). Over the power station the mean SO₂ column was 204 µmol/m² (about 0.46 Dobson units), and over Hwange town 137 µmol/m². The SO₂ plume looks wider than the NO₂ plume partly because the SO₂ map was smoothed more strongly to reduce noise, so its edges should be read as approximate.</p>
        <Fig src={map4} cap="Map 4. Sulphur Dioxide Column Map (2024 to 2025), mean total SO₂ from Sentinel-5P." />

        <h3>Change before and after Units 7 and 8</h3>
        <p>The NO₂ enhancement over Hwange roughly doubled, from 8.3 µmol/m² in 2019 to 2022 to 16.6 µmol/m² in 2024 to 2025 (Table 2). The SO₂ enhancement also doubled, from 48.6 to 99.6 µmol/m². Both rises are highly significant. At Maamba neither gas changed significantly. The rise at Hwange less the rise at Maamba is 7.8 µmol/m² for NO₂ and 42.2 µmol/m² for SO₂. The annual values (Figure 2) show no upward trend before 2023, a step in 2023 when the units were commissioned, and the highest values of the record in 2024. The monthly series (Figure 1) shows the step coming after Unit 8 reached full load in June 2023. The change map (Map 3) shows the rise concentrated in the same south-western plume, with little change across the rest of the region.</p>
        <p className="cs__cap">Table 2. Mean monthly enhancement above the background ring before and after Units 7 and 8 (µmol/m²)</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Gas</th><th>Zone</th><th className="n">2019 to 2022</th><th className="n">2024 to 2025</th><th className="n">Change</th><th className="n">Change (%)</th><th className="n">p</th></tr></thead>
            <tbody><Rows rows={T2} num={2} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study, from Sentinel-5P. Enhancement = mean of the 15 km zone minus mean of the background ring; 48 months before and 24 after; p from Welch's t-test. Percentages are not given for Maamba, where the enhancement is close to zero.</p>
        <Fig src={fig1} cap="Figure 1. Monthly NO₂ and SO₂ enhancement above the background ring at Hwange and Maamba (2019 to 2025)." />
        <Fig src={fig2} cap="Figure 2. Annual mean NO₂ and SO₂ enhancement at Hwange (2019 to 2025)." />
        <Fig src={map3} cap="Map 3. Change in Nitrogen Dioxide Map (2019–2022 to 2024–2025), change in mean NO₂ less the change in the background ring." />

        <h3>Bush fires and the seasonal cycle</h3>
        <p>Fires peak in September and October, and the background NO₂ follows them closely (Spearman's ρ = 0.57, p &lt; 0.001). The link between fire and the Hwange enhancement is weaker (ρ = 0.29, p = 0.008), which shows that subtracting the background removes most, but not all, of the fire signal. The rise at Hwange appears in both seasons (Table 3): in the months with few fires the NO₂ enhancement rose from 7.5 to 12.5 µmol/m² and the SO₂ enhancement from 44.6 to 85.8 µmol/m², both significant. Fires do not explain the rise. The enhancement is larger in the dry season in both periods (Figure 3), most likely because NO₂ lasts longer in the dry winter air and the plume is less often hidden by cloud.</p>
        <p className="cs__cap">Table 3. Mean Hwange enhancement by season before and after Units 7 and 8 (µmol/m²)</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Gas</th><th>Season</th><th className="n">2019 to 2022</th><th className="n">2024 to 2025</th><th className="n">Change</th><th className="n">p</th></tr></thead>
            <tbody><Rows rows={T3} num={2} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study, from Sentinel-5P and FIRMS. p from Welch's t-test on monthly values.</p>
        <Fig src={fig3} cap="Figure 3. Seasonal cycle of the Hwange NO₂ enhancement before and after Units 7 and 8, with fire detections within 80 km." />

        <h3>Population exposure</h3>
        <p>The area where NO₂ was more than 1.5 times the background doubled, from about 790 km² to about 1 660 km² (Table 5). About 38 400 people lived inside it in 2024 to 2025, up from about 24 100, and about 20 500 lived where NO₂ was more than twice the background, up from about 8 200 (Map 5, Figure 4). Almost all of those above twice the background (about 20 100) live within 10 km of the power station, most of them in Hwange town; Lukosi, 10 km to the east, lies just outside the 1.5 × zone. In Hwange town the NO₂ column rose by 43% and the SO₂ column nearly doubled (Table 4). Dete and Victoria Falls saw rises of 12 to 16%, close to the 8% rise of the background.</p>
        <p className="cs__cap">Table 4. Mean column at places in and around the study area</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Place</th><th className="n">NO₂ 2019 to 2022</th><th className="n">NO₂ 2024 to 2025</th><th className="n">NO₂ change (%)</th><th className="n">SO₂ 2019 to 2022</th><th className="n">SO₂ 2024 to 2025</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study, from Sentinel-5P. Values in µmol/m², mean of the nine 0.01° cells centred on each place. SO₂ is not given for Dete and Victoria Falls, where it is within the noise of the instrument.</p>
        <p className="cs__cap">Table 5. Area and population where mean NO₂ exceeded the background</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Measure</th><th className="n">2019 to 2022</th><th className="n">2024 to 2025</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study, from Sentinel-5P and WorldPop 2020 constrained population (Zimbabwe only), rounded to the nearest 100. Background means of 14.1 and 15.2 µmol/m².</p>
        <Fig src={map5} cap="Map 5. Population Exposure Map (2024 to 2025), people in each cell and the zones where NO₂ exceeded 1.5 and 2 times the background." />
        <Fig src={fig4} cap="Figure 4. People living where NO₂ exceeded 1.5 and 2 times the background, before and after Units 7 and 8." />

        <h2>Discussion</h2>
        <p>The satellite record shows that the air over Hwange carried about twice as much NO₂ and SO₂ above the regional background after 2023 as before, that the rise came in the year Units 7 and 8 were commissioned, that it is centred on the power station and its downwind plume, that it is present outside the fire season, and that it did not happen at the control station. This is strong evidence that pollution from Hwange rose after 2023. It is weaker evidence that Units 7 and 8 alone caused it, for four reasons.</p>
        <p>First, other coal users grew in the same area. Coke batteries were built in Hwange from 2021 (The Herald, 2021) and the ZhongXin power station lies about 9 km to the north-west. They lie within the 15 km zone and their emissions are included in the enhancement. The location of the peak, south-west of the power station rather than north-west towards ZhongXin, suggests the power station is the largest source, but the satellite cannot separate sources a few kilometres apart. Second, the six old units are unreliable and produce only about 300 MW of their 920 MW (Financial Gazette, 2026), and their output changed between years. Third, low water at Kariba after the 2023 to 2024 drought cut hydropower by about 800 MW (NewsDay, 2024), so the thermal station was run harder in 2024 than it might otherwise have been; this may explain why 2024 is higher than 2025. Fourth, Maamba is a good control for regional and method effects but it is a single station in another country, and its own output may have varied.</p>
        <p>The data also have limits. TROPOMI measures the gas in the whole column of air, not the concentration people breathe; a column cannot be converted into a ground concentration in µg/m³ without a model of how the gas is mixed through the lower atmosphere, so the results cannot be compared directly with the World Health Organization guidelines (WHO, 2021). TROPOMI tropospheric NO₂ is known to read low over polluted areas, by an amount that varies from place to place (Verhoelst et al., 2021), so the true enhancement is more likely to be larger than smaller. Each cell of the maps is a long-term mean of a sensor with a footprint of several kilometres, so the maps show the pattern of the plume, not conditions at a single house. The population figures use 2020 and only include Zimbabwe.</p>

        <h2>Recommendations</h2>
        <ol>
          <li>The Environmental Management Agency should install continuous ground monitors for NO₂, SO₂ and fine particles in Hwange town, inside the plume shown on Map 2, so that concentrations can be compared with national and WHO standards.</li>
          <li>The Zimbabwe Power Company should publish monthly generation and stack emissions by unit, which would allow the satellite signal to be divided between the new and old units.</li>
          <li>The coke batteries and ZhongXin should be included in any emissions inventory for Hwange, since they lie in the same airshed.</li>
          <li>Health surveillance for respiratory illness at clinics in Hwange town should be compared with the change shown here.</li>
          <li>The same method should be repeated each year with new TROPOMI data, and at Maamba once its second phase comes into service.</li>
        </ol>

        <h2>Conclusion</h2>
        <p>Seven years of Sentinel-5P measurements show that the NO₂ and SO₂ above Hwange, over and above the regional background, about doubled after Units 7 and 8 came into service in 2023, while the control station at Maamba showed no significant change. The rise is strongest in a plume to the south-west of the power station, holds outside the fire season, and more than doubled the number of people, to about 20 500, living where NO₂ is more than twice the background. The power station is the most likely main source, but coke batteries and other coal users in the same area contribute and cannot be separated from space. Ground monitors are needed to turn this evidence into a measure of the air people breathe.</p>

        <h2>References</h2>
        <div className="cs__ref">
          <p>Beirle, S., Borger, C., Dörner, S., Li, A. et al. (2019) Pinpointing nitrogen oxide emissions from space. Science Advances, 5(11), eaax9800. <A href="https://doi.org/10.1126/sciadv.aax9800" /></p>
          <p>Bondarenko, M., Kerr, D., Sorichetta, A. and Tatem, A.J. (2020) Census/projection-disaggregated gridded population datasets for 51 countries across sub-Saharan Africa in 2020 using building footprints. WorldPop, University of Southampton. <A href="https://doi.org/10.5258/SOTON/WP00682" /></p>
          <p>Financial Gazette (2026) Hwange Units 1-6 set for revival. 16 February. <A href="https://fingaz.co.zw/2026/02/16/hwange-units-1-6-set-for-revival/amp/" /></p>
          <p>Fioletov, V.E., McLinden, C.A., Krotkov, N., Li, C. et al. (2016) A global catalogue of large SO2 sources and emissions derived from the Ozone Monitoring Instrument. Atmospheric Chemistry and Physics, 16(18), 11497-11519. <A href="https://doi.org/10.5194/acp-16-11497-2016" /></p>
          <p>Giglio, L., Schroeder, W. and Justice, C.O. (2016) The collection 6 MODIS active fire detection algorithm and fire products. Remote Sensing of Environment, 178, 31-41. <A href="https://doi.org/10.1016/j.rse.2016.02.054" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Lusaka Times (2024) President Hichilema officially launches construction of 300MW Maamba power project. 14 August. <A href="https://www.lusakatimes.com/2024/08/14/president-hichilema-officially-launches-construction-of-300mw-maamba-power-project" /></p>
          <p>Mining Index (2023a) Hwange Unit 7 power generation set for gradual increase to 300MW capacity: ZESA. 22 March. <A href="https://www.miningindex.co.zw/2023/03/22/hwange-unit-7-power-generation-set-for-gradual-increase-to-300mw-capacity-zesa/" /></p>
          <p>Mining Index (2023b) Hwange Unit 8 output reaches 355 megawatts. 15 June. <A href="https://www.miningindex.co.zw/2023/06/15/hwange-unit-8-output-reaches-355-megawatts/" /></p>
          <p>Mining Index (2024) Chinese firm entangled in Hwange pollution crisis. 10 November. <A href="https://www.miningindex.co.zw/?p=109558" /></p>
          <p>NewsDay (2024) We've lost over 800MW at Kariba: Govt. 24 June. <A href="https://www.newsday.co.zw/amp/local-news/article/200028730/weve-lost-over-800mw-at-kariba-govt" /></p>
          <p>The Herald (2021) Tsingshan constructs second 150 000t coking plant in Hwange. 13 May. <A href="https://www.heraldonline.co.zw/tsingshan-constructs-second-150-000t-coking-plant-in-hwange/" /></p>
          <p>Theys, N., De Smedt, I., Yu, H., Danckaert, T. et al. (2017) Sulfur dioxide retrievals from TROPOMI onboard Sentinel-5 Precursor: algorithm theoretical basis. Atmospheric Measurement Techniques, 10(1), 119-153. <A href="https://doi.org/10.5194/amt-10-119-2017" /></p>
          <p>van Geffen, J., Eskes, H., Compernolle, S., Pinardi, G. et al. (2022) Sentinel-5P TROPOMI NO2 retrieval: impact of version v2.2 improvements and comparisons with OMI and ground-based data. Atmospheric Measurement Techniques, 15(7), 2037-2060. <A href="https://doi.org/10.5194/amt-15-2037-2022" /></p>
          <p>Veefkind, J.P., Aben, I., McMullan, K., Förster, H. et al. (2012) TROPOMI on the ESA Sentinel-5 Precursor: a GMES mission for global observations of the atmospheric composition for climate, air quality and ozone layer applications. Remote Sensing of Environment, 120, 70-83. <A href="https://doi.org/10.1016/j.rse.2011.09.027" /></p>
          <p>Verhoelst, T., Compernolle, S., Pinardi, G., Lambert, J.-C. et al. (2021) Ground-based validation of the Copernicus Sentinel-5P TROPOMI NO2 measurements with the NDACC ZSL-DOAS, MAX-DOAS and Pandonia global networks. Atmospheric Measurement Techniques, 14(1), 481-510. <A href="https://doi.org/10.5194/amt-14-481-2021" /></p>
          <p>WHO (2021) WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide. World Health Organization, Geneva. <A href="https://www.who.int/publications/i/item/9789240034228" /></p>
        </div>
      </article>
      <SiteFooter />
    </>
  );
}
