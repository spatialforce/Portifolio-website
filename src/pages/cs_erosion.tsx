import SiteNav, { SiteFooter } from "./SiteChrome";
import "./casestudy.css";
import map1 from "../assets/casestudies/chivi-soil-erosion/map1_study_area.webp";
import map2 from "../assets/casestudies/chivi-soil-erosion/map2_factors.webp";
import map3 from "../assets/casestudies/chivi-soil-erosion/map3_classes.webp";
import map4 from "../assets/casestudies/chivi-soil-erosion/map4_wards.webp";
import map5 from "../assets/casestudies/chivi-soil-erosion/map5_hotspot.webp";
import fig1 from "../assets/casestudies/chivi-soil-erosion/fig1_classes.webp";
import fig2 from "../assets/casestudies/chivi-soil-erosion/fig2_landcover.webp";

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
  ["CHIRPS v2.0 rainfall", "5.5 km", "1991 to 2020", "Rainfall erosivity (R)"],
  ["iSDAsoil sand, silt, clay and organic carbon, 0 to 20 cm", "30 m", "Modelled (2021)", "Soil erodibility (K)"],
  ["Copernicus GLO-30 digital elevation model", "30 m", "2011 to 2015", "Slope length and steepness (LS), hillshade"],
  ["Sentinel-2 surface reflectance (366 scenes)", "10 m", "December to March, 2019/20 to 2023/24", "Cover management (C), image on Map 5"],
  ["ESA WorldCover 10 m v200", "10 m", "2021", "Land cover, support practice (P)"],
  ["Ward boundaries (ZimStat and OCHA)", "Areas", "2020", "District and ward boundaries"],
  ["OpenStreetMap", "Lines and points", "2026", "Rivers, roads and place names"],
];

// Table 2: RUSLE factors
const T2: string[][] = [
  ["R, rainfall erosivity (MJ mm ha⁻¹ h⁻¹ yr⁻¹)", "R = 0.0483 P^1.61, P = mean annual rainfall (mm)", "Renard and Freimund (1994)", "1 082 to 1 518"],
  ["K, soil erodibility (t ha h ha⁻¹ MJ⁻¹ mm⁻¹)", "EPIC equation from sand, silt, clay and organic carbon", "Williams (1995)", "0.017 to 0.020"],
  ["LS, slope length and steepness", "LS = (λ / 22.13)^0.4 (sin β / 0.0896)^1.3, λ ≤ 300 m", "Moore and Burch (1986)", "0.04 to 19.4"],
  ["C, cover management", "C = exp(−2 NDVI / (1 − NDVI)), rainy-season NDVI", "van der Knijff et al. (2000)", "0 to 0.61"],
  ["P, support practice", "Contouring values by slope on cropland, 1 elsewhere", "Wischmeier and Smith (1978)", "0.5 to 1"],
];

// Table 3: soil loss classes
const T3: string[][] = [
  ["Very low (below 2)", "1 872.4", "53.6"],
  ["Low (2 to 5)", "842.9", "24.2"],
  ["Moderate (5 to 10)", "421.8", "12.1"],
  ["High (10 to 20)", "193.7", "5.6"],
  ["Very high (above 20)", "159.6", "4.6"],
  ["District land", "3 490.4", "100"],
];

// Table 4: soil loss by land cover
const T4: string[][] = [
  ["Tree cover", "863.4", "0.032", "1.67", "3.2", "144"],
  ["Shrubland", "1 214.9", "0.182", "4.81", "10.5", "584"],
  ["Grassland", "844.3", "0.264", "10.88", "21.0", "918"],
  ["Cropland", "533.4", "0.305", "1.92", "0.9", "103"],
  ["Bare or sparse", "26.1", "0.705", "24.23", "59.7", "63"],
];

// Table 5: wards
const T5: string[][] = [
  ["Ward 14", "219.5", "12.47", "27.9", "7.5", "12.2"],
  ["Ward 15", "131.6", "12.28", "28.1", "9.2", "9.5"],
  ["Ward 16", "164.3", "9.51", "19.2", "4.9", "13.6"],
  ["Ward 18", "98.9", "7.97", "15.0", "5.7", "11.0"],
  ["Ward 22", "93.0", "6.71", "10.2", "4.0", "20.0"],
  ["Ward 31", "31.9", "2.59", "5.0", "9.1", "3.5"],
  ["Ward 29", "204.4", "2.23", "3.9", "5.5", "14.2"],
  ["Ward 24", "75.0", "2.22", "3.9", "6.1", "7.2"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function ErosionCaseStudy() {
  return (
    <>
      <SiteNav />
      <article className="cs">
        <h1>Soil Loss Estimation in Chivi District Using the Revised Universal Soil Loss Equation</h1>
        <p className="cs__by">Kudzanai Chakavarika. November 2026.</p>

        <h2>Introduction</h2>
        <p>Soil erosion is one of the main causes of land degradation in the communal areas of southern Zimbabwe. Thin sandy soils on granite, low and erratic rainfall, heavy grazing and the clearing of woodland for fields leave much of the ground bare when the first storms of the rainy season arrive. The soil that is washed off lowers crop yields where it leaves and fills dams and rivers where it settles. In the Upper Runde catchment, which drains Chivi, reservoir sedimentation has been linked to changes in land use and land cover (Kusena et al., 2022).</p>
        <p>The Revised Universal Soil Loss Equation (RUSLE) estimates the mean annual loss of soil by sheet and rill erosion as the product of five factors: rainfall erosivity, soil erodibility, slope length and steepness, cover management and support practice (Renard et al., 1997). Each factor can be mapped from open data, so the equation can be applied cell by cell across a whole district. This study applies RUSLE to Chivi District on a 30 m grid for a single recent period. It maps where soil loss is highest, measures how much of the district loses soil faster than it forms, and ranks wards so that soil conservation work can be targeted.</p>

        <h2>Objectives</h2>
        <ol>
          <li>To map the five RUSLE factors for Chivi District at 30 m resolution.</li>
          <li>To estimate the mean annual soil loss and map it in five classes.</li>
          <li>To compare soil loss between land cover types and between wards.</li>
          <li>To identify the main hot spot of soil loss and recommend where conservation should start.</li>
        </ol>

        <h2>Study area</h2>
        <p>Chivi District lies in Masvingo Province in south-central Zimbabwe, between about 30.0°E and 31.1°E and 19.9°S and 21.0°S (Map 1). The district covers 3 546 km², of which 3 490 km² is land and the rest is open water, mostly part of Tugwi-Mukosi Dam on the eastern edge. It is divided into 32 wards. The land rises from about 490 m in the south-east to about 1 040 m in the north-west, and granite hills stand above gently rolling plains. Mean annual rainfall from 1991 to 2020 was 504 to 621 mm (Funk et al., 2015), falling mostly between November and March. Most of the district is communal land where people grow maize and small grains on small fields and graze cattle and goats on the land in between.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>Data and methods</h2>
        <p className="cs__cap">Table 1. Data used in the study</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: Funk et al. (2015); Hengl et al. (2021); ESA (2021); ESA (2024); Zanaga et al. (2022); OCHA (2020); OpenStreetMap contributors (2026). Raster data were processed in Google Earth Engine (Gorelick et al., 2017). All layers were placed on a 30 m grid in UTM zone 36S.</p>

        <h3>The RUSLE model</h3>
        <p>Mean annual soil loss A, in tonnes per hectare per year, was calculated for every cell as A = R × K × LS × C × P (Renard et al., 1997). Table 2 gives the equation used for each factor and the range of its values across the district, from the 1st to the 99th percentile.</p>
        <p className="cs__cap">Table 2. RUSLE factors</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Factor</th><th>Method</th><th>Source</th><th>Range in the district</th></tr></thead>
            <tbody><Rows rows={T2} num={3} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study. Ranges are the 1st to 99th percentile over district land. λ is the slope length from flow accumulation and β the slope angle.</p>
        <p>R was calculated from the CHIRPS 1991 to 2020 mean annual rainfall with the equation of Renard and Freimund (1994) for rainfall below 850 mm. K was calculated from iSDAsoil topsoil texture and organic carbon with the EPIC equation (Williams, 1995) and converted to SI units. Rock outcrops and water have no soil values in iSDAsoil, so these cells (72 810, about 6 % of the grid) took the value of the nearest cell with soil. LS was calculated from the 30 m elevation model after filling pits and depressions, with slope length taken from flow accumulation and capped at 300 m (Moore and Burch, 1986).</p>
        <p>C was calculated from the normalised difference vegetation index (NDVI) of Sentinel-2 (van der Knijff et al., 2000). Because almost all erosive rain falls between December and March, the NDVI is the median of all cloud-masked scenes from December to March over five rainy seasons, 2019/20 to 2023/24, which gives the ground cover at the time when soil is most at risk. C was set to 0 on built-up land and water. P was set from slope on cropland, using the contouring values of Wischmeier and Smith (1978), and to 1 on all other land.</p>

        <h3>Classes and comparison</h3>
        <p>Soil loss was grouped into five classes: very low (below 2 t/ha/yr), low (2 to 5), moderate (5 to 10), high (10 to 20) and very high (above 20). The share of land above the upper soil loss tolerance of 11.2 t/ha/yr (Wischmeier and Smith, 1978) was also measured. Mean soil loss, the share of high and very high land, the median slope and the share of cropland were then calculated for each land cover type and each ward. All statistics exclude open water.</p>

        <h2>Results</h2>
        <h3>RUSLE factors</h3>
        <p>Map 2 shows the five factors and land cover. R rises from about 1 080 MJ mm ha⁻¹ h⁻¹ yr⁻¹ in the south to about 1 520 in the north, following rainfall. K varies little, from 0.017 to 0.020, because the topsoils are sandy loams across most of the district. LS has the strongest pattern: it is below 1 on the plains and rises above 10 on the granite hills and along valley sides. C is lowest under the woodland of the hills and the north and highest on open grazing land, fields and bare ground.</p>
        <Fig src={map2} cap="Map 2. RUSLE Factor Maps." />

        <h3>Soil loss</h3>
        <p>The mean soil loss over the district is 5.19 t/ha/yr and the median is 1.75 t/ha/yr, which gives a total of about 1.81 million tonnes a year. More than half the land (53.6 %) is in the very low class and a further 24.2 % in the low class (Table 3, Figure 1, Map 3). High and very high loss covers 353.3 km², 10.1 % of the land, and 8.8 % of the land loses soil faster than 11.2 t/ha/yr. The loss is very uneven: the 10 % of cells with the highest loss produce 61.0 % of all the soil lost.</p>
        <p className="cs__cap">Table 3. Area of each soil loss class</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Class (t/ha/yr)</th><th>Area (km²)</th><th>Share of the land (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study.</p>
        <Fig src={fig1} cap="Figure 1. Area of each soil loss class." />
        <Fig src={map3} cap="Map 3. Soil Loss Classes Map." />

        <h3>Land cover</h3>
        <p>Grassland loses the most soil of the large land cover types, 10.88 t/ha/yr on average, and 21.0 % of it is in the high or very high class (Table 4, Figure 2). It produces about 918 000 tonnes a year, half of the district total. Bare and sparse land has the highest rate, 24.23 t/ha/yr, but covers only 26.1 km². Shrubland follows with 4.81 t/ha/yr. Tree cover (1.67 t/ha/yr) and cropland (1.92 t/ha/yr) lose the least. Cropland has the second highest C value after bare land, but it lies mostly on flat ground and has a support practice factor below 1, so its modelled loss is low.</p>
        <p className="cs__cap">Table 4. Soil loss by land cover</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Land cover</th><th>Area (km²)</th><th>Mean C</th><th>Mean soil loss (t/ha/yr)</th><th>High and very high (%)</th><th>Soil loss (thousand t/yr)</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study. Built-up land (8.0 km²) has no modelled loss and is not shown.</p>
        <Fig src={fig2} cap="Figure 2. Mean soil loss by land cover." />

        <h3>Wards</h3>
        <p>Mean soil loss ranges from 2.22 t/ha/yr in ward 24 to 12.47 t/ha/yr in ward 14 (Table 5, Map 4). Wards 14 and 15 in the centre-west of the district are the only wards with a mean above the tolerance limit, and in each more than a quarter of the land is in the high or very high class. Ward 16, just to the east, follows with 9.51 t/ha/yr. Seven of the 32 wards have a mean above the district mean. Slope alone does not explain the ranking: ward 31 is as steep as ward 15 but loses only 2.59 t/ha/yr, because its hills are wooded (mean C 0.037, against 0.158 in ward 15).</p>
        <p className="cs__cap">Table 5. Wards with the highest and lowest mean soil loss</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Ward</th><th>Area (km²)</th><th>Mean soil loss (t/ha/yr)</th><th>High and very high (%)</th><th>Median slope (%)</th><th>Cropland (%)</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study. The top five and bottom three of 32 wards.</p>
        <Fig src={map4} cap="Map 4. Mean Soil Loss by Ward Map." />

        <h3>Hot spot</h3>
        <p>The largest block of high and very high loss lies across wards 14 and 15, centred at about 30.44°E, 20.41°S. On the satellite image this is an area of rocky granite hills and pale, thinly covered ground between them (Map 5). The very high cells follow the hill slopes and the open ground at their feet, while the darker wooded patches and the valley floors stay in the lower classes.</p>
        <Fig src={map5} cap="Map 5. Soil Loss Hot Spot in Wards 14 and 15." />

        <h2>Discussion</h2>
        <p>The results show that soil loss in Chivi is concentrated rather than widespread. Most of the district loses less than 5 t/ha/yr, but a tenth of the land loses more than 10 t/ha/yr and produces most of the sediment. This is useful for planning, because conservation work on a small part of the district would deal with most of the problem. The hot spot in wards 14 and 15 combines steep granite slopes with open grazing land, the two conditions that RUSLE treats as most severe.</p>
        <p>The choice of vegetation period has a large effect on the result. A first run with the NDVI of the whole year gave a mean of 12.6 t/ha/yr, because the dry season leaves the ground bare for months when little rain falls. Using rainy-season NDVI lowered the mean to 5.19 t/ha/yr. The rainy-season value is the better estimate, since cover matters most when the erosive storms fall. Kusena et al. (2022) reported lower rates, 1.2 to 1.7 t/ha/yr, for the Upper Runde catchment. Part of the difference is likely to come from the finer 30 m grid used here, which resolves the steep slopes of the granite hills that a coarser grid smooths out.</p>
        <p>The low loss on cropland should be read with care. RUSLE estimates sheet and rill erosion only. It does not model gullies, which in Chivi often start in fields and along paths and cattle tracks, and it does not capture the bare soil of fields after ploughing early in the season. The R equation was developed in the United States and has not been calibrated for Zimbabwe. The K values come from a modelled soil map, and rock outcrops were filled from the nearest soil. Tolerance limits of 4.5 to 11.2 t/ha/yr were set for deep soils (Wischmeier and Smith, 1978), and the shallow sandy soils of Chivi may tolerate much less. The values should therefore be treated as a relative ranking of risk, not as measured losses.</p>

        <h2>Recommendations</h2>
        <ol>
          <li>Start soil conservation in wards 14 and 15, where mean loss is above 12 t/ha/yr, with grazing control, the restoration of grass cover and stone lines on hill slopes.</li>
          <li>Protect the woodland on the hills, which keeps loss low in wards such as 31 despite steep slopes.</li>
          <li>Map gullies in the high and very high areas from high-resolution imagery and field surveys, since RUSLE does not include them.</li>
          <li>Measure sediment at small dams below the hot spot to check the modelled rates and calibrate the R and C factors for local conditions.</li>
          <li>Repeat the analysis for the neighbouring districts that drain to Tugwi-Mukosi Dam to estimate the sediment reaching it.</li>
        </ol>

        <h2>Conclusion</h2>
        <p>The mean soil loss in Chivi District is 5.19 t/ha/yr, about 1.81 million tonnes a year. High and very high loss covers 10.1 % of the land, and the top tenth of the land produces 61.0 % of the soil lost. Grassland and bare ground lose the most soil, while woodland and cropland lose the least. Wards 14 and 15 are the only wards with a mean above the tolerance limit of 11.2 t/ha/yr and should be the first targets for soil conservation.</p>

        <h2>References</h2>
        <div className="cs__ref">
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>ESA (2024) Sentinel-2 MSI Level-2A surface reflectance. European Space Agency, Copernicus programme.</p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Hengl, T., Miller, M.A.E., Križan, J., Shepherd, K.D. et al. (2021) African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Scientific Reports, 11, 6130. <A href="https://doi.org/10.1038/s41598-021-85639-y" /></p>
          <p>Kusena, W., Chemura, A., Dube, T., Nicolau, M. and Marambanyika, T. (2022) Landuse and landcover change assessment in the Upper Runde sub-catchment, Zimbabwe and possible impacts on reservoir sedimentation. Physics and Chemistry of the Earth, 126, 103105. <A href="https://doi.org/10.1016/j.pce.2021.103105" /></p>
          <p>Moore, I.D. and Burch, G.J. (1986) Physical basis of the length-slope factor in the Universal Soil Loss Equation. Soil Science Society of America Journal, 50, 1294-1298. <A href="https://doi.org/10.2136/sssaj1986.03615995005000050042x" /></p>
          <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB), with ZimStat ward boundaries. Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>OpenStreetMap contributors (2026) OpenStreetMap. <A href="https://www.openstreetmap.org" /></p>
          <p>Renard, K.G. and Freimund, J.R. (1994) Using monthly precipitation data to estimate the R-factor in the revised USLE. Journal of Hydrology, 157, 287-306. <A href="https://doi.org/10.1016/0022-1694(94)90110-4" /></p>
          <p>Renard, K.G., Foster, G.R., Weesies, G.A., McCool, D.K. and Yoder, D.C. (1997) Predicting Soil Erosion by Water: A Guide to Conservation Planning with the Revised Universal Soil Loss Equation (RUSLE). Agriculture Handbook 703. US Department of Agriculture, Washington, DC.</p>
          <p>van der Knijff, J.M., Jones, R.J.A. and Montanarella, L. (2000) Soil Erosion Risk Assessment in Europe. EUR 19044 EN. European Soil Bureau, Joint Research Centre, Ispra.</p>
          <p>Williams, J.R. (1995) The EPIC model. In: Singh, V.P. (ed.) Computer Models of Watershed Hydrology. Water Resources Publications, Highlands Ranch, 909-1000.</p>
          <p>Wischmeier, W.H. and Smith, D.D. (1978) Predicting Rainfall Erosion Losses: A Guide to Conservation Planning. Agriculture Handbook 537. US Department of Agriculture, Washington, DC.</p>
          <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
        </div>
      </article>
      <SiteFooter />
    </>
  );
}
