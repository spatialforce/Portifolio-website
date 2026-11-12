import SiteNav, { SiteFooter } from "./SiteChrome";
import "./casestudy.css";
import map1 from "../assets/casestudies/chimanimani-flood/map1_study_area.webp";
import map2 from "../assets/casestudies/chimanimani-flood/map2_factors.webp";
import map3 from "../assets/casestudies/chimanimani-flood/map3_susceptibility.webp";
import fig1 from "../assets/casestudies/chimanimani-flood/fig1_weights.webp";
import fig2 from "../assets/casestudies/chimanimani-flood/fig2_classes.webp";

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
  ["Copernicus GLO-30 digital elevation model", "30 m", "2011 to 2015", "Elevation, slope, wetness index, rivers, drainage density"],
  ["CHIRPS daily rainfall", "0.05°", "1991 to 2020", "Mean annual rainfall"],
  ["Esri Sentinel-2 land use and land cover", "10 m", "2018", "Land use and land cover"],
  ["OpenLandMap clay content (surface)", "250 m", "Long-term", "Soil clay"],
  ["Google Open Buildings v3", "Polygons", "2023", "Buildings in each class"],
  ["WorldPop constrained population", "100 m", "2020", "People in each class"],
  ["District boundary (OCHA COD-AB)", "Polygon", "2023", "Study area"],
];

// Table 2: reclassification of the factors (score 5 = very high susceptibility)
const T2: string[][] = [
  ["Distance to river (m)", "> 2 000", "1 000 – 2 000", "500 – 1 000", "250 – 500", "< 250"],
  ["Slope (degrees)", "> 25", "15 – 25", "10 – 15", "5 – 10", "< 5"],
  ["Elevation (m)", "> 1 600", "1 300 – 1 600", "1 000 – 1 300", "700 – 1 000", "< 700"],
  ["Topographic wetness index", "< 6", "6 – 7", "7 – 8", "8 – 10", "> 10"],
  ["Mean annual rainfall (mm)", "< 800", "800 – 950", "950 – 1 100", "1 100 – 1 250", "> 1 250"],
  ["Drainage density (km/km²)", "< 0.3", "0.3 – 0.6", "0.6 – 0.9", "0.9 – 1.2", "> 1.2"],
  ["Land use and land cover", "Trees", "Rangeland", "Cropland", "Built area, bare ground", "Water, flooded vegetation"],
  ["Soil clay content (%)", "< 28", "28 – 30", "30 – 32", "32 – 34", "> 34"],
];

// Table 3: AHP pairwise comparison matrix and weights
const T3: string[][] = [
  ["Distance to river", "1", "2", "3", "3", "4", "5", "6", "7", "31.4"],
  ["Slope", "1/2", "1", "2", "2", "3", "4", "5", "6", "21.1"],
  ["Elevation", "1/3", "1/2", "1", "1", "2", "3", "4", "5", "13.4"],
  ["Wetness index", "1/3", "1/2", "1", "1", "2", "3", "4", "5", "13.4"],
  ["Annual rainfall", "1/4", "1/3", "1/2", "1/2", "1", "2", "3", "4", "8.5"],
  ["Drainage density", "1/5", "1/4", "1/3", "1/3", "1/2", "1", "2", "3", "5.6"],
  ["Land cover", "1/6", "1/5", "1/4", "1/4", "1/3", "1/2", "1", "2", "3.8"],
  ["Soil clay", "1/7", "1/6", "1/5", "1/5", "1/4", "1/3", "1/2", "1", "2.7"],
];

// Table 4: share of the district in each score, per factor (%)
const T4: string[][] = [
  ["Distance to river", "26", "32", "20", "11", "11"],
  ["Slope", "13", "24", "18", "21", "24"],
  ["Elevation", "13", "26", "33", "17", "11"],
  ["Wetness index", "29", "30", "20", "14", "7"],
  ["Annual rainfall", "32", "10", "11", "17", "31"],
  ["Drainage density", "30", "22", "22", "15", "10"],
  ["Land cover", "43", "52", "2", "2", "0.3"],
  ["Soil clay", "18", "12", "22", "24", "25"],
];

// Table 5: susceptibility classes, area, buildings and people
const T5: string[][] = [
  ["Very low", "1.08 – 1.99", "570", "17.0", "1 050", "1.6", "3 300", "2.2"],
  ["Low", "1.99 – 2.51", "836", "25.0", "6 614", "9.9", "16 000", "10.6"],
  ["Moderate", "2.51 – 3.04", "889", "26.6", "17 306", "25.8", "37 100", "24.5"],
  ["High", "3.04 – 3.65", "659", "19.7", "26 416", "39.4", "58 700", "38.7"],
  ["Very high", "3.65 – 4.95", "389", "11.6", "15 671", "23.4", "36 600", "24.1"],
  ["Total", "", "3 342", "100", "67 057", "100", "151 800", "100"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function ChimanimaniFloodCaseStudy() {
  return (
    <>
      <SiteNav />
      <article className="cs">
        <h1>Flood Susceptibility Mapping of Chimanimani District Using GIS-Based Multi-Criteria Analysis and the Analytic Hierarchy Process</h1>
        <p className="cs__by">Kudzanai Chakavarika. Case study 6. November 2026.</p>

        <h2>Introduction</h2>
        <p>Chimanimani District has steep highlands, heavy summer rain and narrow valleys where most people live. Water collects quickly in these valleys and rivers rise fast after storms. A flood susceptibility map shows which parts of the land are most likely to flood, based on the physical conditions of each place, so that planning and early warning can focus on the right areas.</p>
        <p>This study builds that map using GIS multi-criteria analysis. Eight flood conditioning factors are mapped on a 30 m grid. Each one is reclassified into five susceptibility scores. They are given weights with the analytic hierarchy process (AHP; Saaty, 1980) and combined into one flood susceptibility index by weighted overlay. The index is then split into five classes, and buildings and people are counted in each class.</p>

        <h2>Objectives</h2>
        <ol>
          <li>To identify and classify the physical and land-cover factors that control flooding in Chimanimani District.</li>
          <li>To derive factor weights with the analytic hierarchy process and evaluate the consistency of the judgements.</li>
          <li>To analyse the spatial pattern of flood susceptibility across the district in five classes.</li>
          <li>To assess the exposure of buildings and people in each susceptibility class.</li>
        </ol>

        <h2>Study area</h2>
        <p>Chimanimani District lies in the south-east of Manicaland Province in eastern Zimbabwe (Map 1). It covers 3 342 km². The land rises from about 300 m in the western lowlands to more than 2 000 m in the Chimanimani Mountains in the east. The eastern half is steep and deeply cut, and its southern part drains through the Rusitu River. The western half is drier and drains through the Nyanyadzi valley. Long-term rainfall ranges from about 480 mm a year in the west to more than 1 500 mm in the east (Funk et al., 2015). The district had 153 619 people at the 2022 census (City Population, 2023). Most live in Chimanimani town, around Cashel and Mutambara in the north, and along the Rusitu valley in the south.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>Data and methods</h2>
        <p className="cs__cap">Table 1. Data used in the study</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: ESA (2021); Funk et al. (2015); Karra et al. (2021); Hengl (2018); Sirko et al. (2021); Bondarenko et al. (2020); OCHA (2023). Rainfall, land cover, soil, buildings and population were processed in Google Earth Engine (Gorelick et al., 2017).</p>

        <h3>Flood conditioning factors</h3>
        <p>All layers were placed on one 30 m grid in UTM zone 36S. Eight factors were used:</p>
        <ul>
          <li><b>Distance to river.</b> Rivers were traced from the elevation model by flow accumulation, keeping channels that drain 10 km² or more. Land close to a river floods first.</li>
          <li><b>Slope.</b> Water collects and spreads on flat ground, but runs off steep slopes.</li>
          <li><b>Elevation.</b> Low ground receives water from the land above it.</li>
          <li><b>Topographic wetness index (TWI).</b> ln (upstream area ÷ tan slope) (Beven and Kirkby, 1979). High values mark hollows and valley floors where water gathers.</li>
          <li><b>Mean annual rainfall.</b> CHIRPS daily rainfall summed and averaged over 1991 to 2020.</li>
          <li><b>Drainage density.</b> Length of stream channel (1 km² or more upstream) per km², measured inside a 1 km circle around each cell.</li>
          <li><b>Land use and land cover.</b> Trees slow and absorb runoff. Bare ground and built-up surfaces do not.</li>
          <li><b>Soil clay content.</b> Clay soils let less water soak in, so more of it runs off.</li>
        </ul>

        <h3>Reclassification</h3>
        <p>Each factor was reclassified into five scores, from 1 (very low susceptibility) to 5 (very high), as Table 2 shows. The breaks follow the spread of each factor inside the district and the way it affects flooding. Map 2 shows all eight reclassified factors.</p>
        <p className="cs__cap">Table 2. Reclassification of the flood conditioning factors</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Factor</th><th>1 Very low</th><th>2 Low</th><th>3 Moderate</th><th>4 High</th><th>5 Very high</th></tr></thead>
            <tbody><Rows rows={T2} num={9} /></tbody>
          </table>
        </div>
        <Fig src={map2} cap="Map 2. Reclassified Flood Conditioning Factors, the eight factors scored from 1 (very low) to 5 (very high) with their AHP weights." />

        <h3>Weighting with the analytic hierarchy process</h3>
        <p>The factors were compared in pairs on Saaty's 1 to 9 scale (Saaty, 1980), where 1 means two factors are equally important and 9 means one is extremely more important than the other (Table 3). Distance to river was judged the most important factor, followed by slope, then elevation and wetness index (equal), then rainfall, drainage density, land cover and soil. The weights are the principal eigenvector of the matrix.</p>
        <p>The consistency of the judgements was checked with the consistency ratio, CR = CI ÷ RI, where CI = (λmax − n) ÷ (n − 1). For this matrix λmax = 8.207 and n = 8, so CI = 0.030. The random index RI for eight factors is 1.41, which gives CR = 0.021. This is well below the 0.10 limit, so the judgements are consistent (Saaty, 1980).</p>
        <p className="cs__cap">Table 3. Pairwise comparison matrix and factor weights</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Factor</th><th>DR</th><th>SL</th><th>EL</th><th>TWI</th><th>RF</th><th>DD</th><th>LC</th><th>SC</th><th>Weight (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">DR distance to river, SL slope, EL elevation, TWI topographic wetness index, RF annual rainfall, DD drainage density, LC land cover, SC soil clay. λmax = 8.207, CI = 0.030, RI = 1.41, CR = 0.021.</p>
        <Fig src={fig1} cap="Figure 1. AHP weights of the eight flood conditioning factors." />

        <h3>Weighted overlay and classification</h3>
        <p>The flood susceptibility index (FSI) of each cell is the weighted sum of its eight scores:</p>
        <p>FSI = 0.314 DR + 0.211 SL + 0.134 EL + 0.134 TWI + 0.085 RF + 0.056 DD + 0.038 LC + 0.027 SC</p>
        <p>The index can run from 1 to 5. In the district it ranges from 1.08 to 4.95. It was split into five classes (very low, low, moderate, high and very high) with natural breaks (Jenks, 1967). Buildings and people were then counted in each class.</p>

        <h2>Results</h2>
        <h3>Reclassified factors</h3>
        <p>The factors split the district in different ways (Map 2, Table 4). Distance to river and drainage density pick out the valley network. About a fifth of the district lies within 500 m of a river. Slope and elevation separate the flat, low western plains from the steep eastern highlands: a quarter of the district has slopes under 5°, and 11 % lies below 700 m, almost all of it in the west. Rainfall works the other way: the east gets the most, and 31 % of the district receives more than 1 250 mm a year. Land cover is mostly rangeland and trees, which both score low. Clay content is highest in the east, where 68 % of the land scores 4 or 5, against 25 % in the west.</p>
        <p className="cs__cap">Table 4. Share of the district in each score, by factor (%)</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Factor</th><th>1 Very low</th><th>2 Low</th><th>3 Moderate</th><th>4 High</th><th>5 Very high</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>

        <h3>Flood susceptibility</h3>
        <p>Map 3 shows the final flood susceptibility map. The high and very high classes cover 1 048 km², or 31.3 % of the district. They follow two settings. The first is the flat western lowlands along the lower Nyanyadzi, around Nyanyadzi and Hot Springs. Here low ground, gentle slopes and nearby rivers all score high. 37 % of the western half of the district is in the high or very high class. The second is the valley floors that cut through the highlands, such as the Rusitu valley around Machongwe and the valleys around Cashel and Mutambara in the north. In these valleys, closeness to the river and high rainfall make up for the higher ground. The ridges, steep slopes and plateaus, including the ground around Chimanimani town itself, fall mostly in the very low and low classes, which together cover 42 % of the district.</p>
        <Fig src={map3} cap="Map 3. Flood Susceptibility Map, five classes of the weighted overlay of eight reclassified factors." />
        <p className="cs__cap">Table 5. Area, buildings and people in each flood susceptibility class</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Class</th><th>FSI range</th><th>Area (km²)</th><th>Area (%)</th><th>Buildings</th><th>Buildings (%)</th><th>People</th><th>People (%)</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="cs__src">Source: this study; Sirko et al. (2021); Bondarenko et al. (2020). People are rounded to the nearest hundred.</p>

        <h3>Buildings and people</h3>
        <p>Settlements in Chimanimani sit in the valleys, close to water and flat land. This puts many of them on the most flood-prone ground (Figure 2). The high and very high classes cover 31 % of the district, but they hold 42 087 buildings (63 % of the total) and about 95 300 people (63 %). The very high class alone covers 11.6 % of the land, but has 23 % of the buildings and 24 % of the people. Only 1.6 % of buildings stand in the very low class.</p>
        <Fig src={fig2} cap="Figure 2. Share of district area, buildings and people in each flood susceptibility class." />

        <h3>Check against mapped flood areas</h3>
        <p>As an independent check, the map was compared with the flood areas mapped across the district by the Royal Museum for Central Africa after the floods of March 2019 (RMCA, 2025). These were not used to build the map. 85.7 % of the mapped flood cells fall in the very high class and 11.2 % in the high class. The area under the ROC curve is 0.95, which means the index separates flooded from unflooded ground well.</p>

        <h2>Discussion</h2>
        <p>The map shows that flood susceptibility in Chimanimani is controlled mainly by where the valleys are. Distance to river and slope together carry more than half of the weight, so the high classes trace the river network and the flat ground beside it. The two halves of the district are prone for different reasons. The western lowlands are low, flat and close to large rivers, but they get less rain. The eastern valleys are higher, but they are narrow and get the heaviest rain. Both end up in the high and very high classes.</p>
        <p>The weights come from expert judgement, so a different analyst could rank the factors differently. The consistency ratio shows that the judgements agree with each other, but not that they are correct. The close match with the mapped flood areas gives some confidence in the result. Several limits remain. The 30 m elevation model smooths narrow channels. Rainfall and soil data are coarse (about 5 km and 250 m). The land cover is from a single year. The map shows where flooding is likely, not how deep or how often it will be.</p>

        <h2>Recommendations</h2>
        <ol>
          <li>Use the high and very high classes to guide where new homes, schools and clinics are built, and keep valley floors such as the Rusitu and Nyanyadzi free of new building.</li>
          <li>Give priority for early warning and evacuation planning to the settlements in the very high class, starting with the valley villages and the Nyanyadzi lowlands.</li>
          <li>Keep forest cover on the steep eastern slopes, since trees slow the runoff that feeds the valleys below.</li>
          <li>Refine the map with a finer elevation model and local rain gauge records, and test the weights with the people who know the district.</li>
        </ol>

        <h2>Conclusion</h2>
        <p>Eight factors were reclassified, weighted with AHP (CR = 0.021) and combined by weighted overlay into a flood susceptibility map of Chimanimani District. 31 % of the district is in the high or very high class, mostly the western lowlands and the valley floors of the highlands. These classes hold about 63 % of the district's buildings and people, so flood risk here comes as much from where people live as from the land itself.</p>

        <h2>References</h2>
        <div className="cs__ref">
          <p>Beven, K.J. and Kirkby, M.J. (1979) A physically based, variable contributing area model of basin hydrology. Hydrological Sciences Bulletin, 24(1), 43-69. <A href="https://doi.org/10.1080/02626667909491834" /></p>
          <p>Bondarenko, M., Kerr, D., Sorichetta, A. and Tatem, A.J. (2020) Census/projection-disaggregated gridded population datasets for 51 countries across sub-Saharan Africa in 2020 using building footprints. WorldPop, University of Southampton. <A href="https://doi.org/10.5258/SOTON/WP00682" /></p>
          <p>City Population (2023) Chimanimani (District, Zimbabwe): population statistics from the Zimbabwe National Statistics Agency census. <A href="https://www.citypopulation.de/en/zimbabwe/admin/manicaland/102__chimanimani/" /></p>
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Hengl, T. (2018) Clay content in % (kg / kg) at 6 standard depths (0, 10, 30, 60, 100 and 200 cm) at 250 m resolution. Zenodo. <A href="https://doi.org/10.5281/zenodo.2525663" /></p>
          <p>Jenks, G.F. (1967) The data model concept in statistical mapping. International Yearbook of Cartography, 7, 186-190.</p>
          <p>Karra, K., Kontgis, C., Statman-Weil, Z., Mazzariello, J.C., Mathis, M. and Brumby, S.P. (2021) Global land use/land cover with Sentinel 2 and deep learning. IEEE International Geoscience and Remote Sensing Symposium (IGARSS), 4704-4707. <A href="https://doi.org/10.1109/IGARSS47720.2021.9553499" /></p>
          <p>OCHA (2023) Zimbabwe subnational administrative boundaries (COD-AB). United Nations Office for the Coordination of Humanitarian Affairs, Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>RMCA (2025) Landslide susceptibility and exposure assessment: Chimanimani and Chipinge districts, Zimbabwe. Royal Museum for Central Africa, on the UNESCO IHP Water Information Network System. <A href="https://doi.org/10.63253/nii4g2ac" /></p>
          <p>Saaty, T.L. (1980) The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation. McGraw-Hill, New York.</p>
          <p>Sirko, W., Kashubin, S., Ritter, M., Annkah, A. et al. (2021) Continental-scale building detection from high resolution satellite imagery. arXiv:2107.12283. <A href="https://doi.org/10.48550/arXiv.2107.12283" /></p>
        </div>
      </article>
      <SiteFooter />
    </>
  );
}
