import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/chimanimani-landslide/map1_study_area.webp";
import map2 from "../assets/casestudies/chimanimani-landslide/map2_factors.webp";
import map3 from "../assets/casestudies/chimanimani-landslide/map3_susceptibility.webp";
import map4 from "../assets/casestudies/chimanimani-landslide/map4_landslides.webp";
import fig1 from "../assets/casestudies/chimanimani-landslide/fig1_weights.webp";
import fig2 from "../assets/casestudies/chimanimani-landslide/fig2_landslides.webp";
import fig3 from "../assets/casestudies/chimanimani-landslide/fig3_exposure.webp";

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
  ["Copernicus GLO-30 digital elevation model", "30 m", "2011 to 2015", "Slope, elevation, curvature, aspect, streams"],
  ["CHIRPS daily rainfall", "0.05°", "1991 to 2020", "Mean annual rainfall"],
  ["Esri Sentinel-2 land use and land cover", "10 m", "2018", "Land cover"],
  ["OpenLandMap clay content (surface)", "250 m", "Long-term", "Soil clay"],
  ["Google Open Buildings v3", "Polygons", "2023", "Buildings in each class"],
  ["WorldPop constrained population", "100 m", "2020", "People in each class"],
  ["RMCA landslide source points", "Points", "2019", "Check of the map only"],
  ["District boundary (OCHA COD-AB)", "Polygon", "2023", "Study area"],
];

// Table 2: reclassification of the factors (score 5 = very high susceptibility)
const T2: string[][] = [
  ["Slope (°)", "< 5", "5 – 15", "15 – 25", "25 – 35", "> 35"],
  ["Mean annual rainfall (mm)", "< 800", "800 – 1 000", "1 000 – 1 200", "1 200 – 1 400", "> 1 400"],
  ["Land use and land cover", "Water, flooded vegetation", "Trees", "Rangeland, built area", "Cropland", "Bare ground"],
  ["Soil clay content (%)", "< 26", "26 – 30", "30 – 33", "33 – 36", "> 36"],
  ["Curvature (1/100 m)", "", "−0.2 – 0.2", "> 0.2", "−0.5 – −0.2", "< −0.5"],
  ["Distance to streams (m)", "> 800", "400 – 800", "200 – 400", "100 – 200", "< 100"],
  ["Elevation (m)", "< 700", "700 – 1 000", "1 000 – 1 300", "1 300 – 1 600", "> 1 600"],
  ["Aspect", "N (315° – 45°), flat", "W, NW (225° – 315°)", "SW (180° – 225°)", "NE (45° – 90°)", "E to S (90° – 180°)"],
];

// Table 3: AHP pairwise comparison matrix and weights
const T3: string[][] = [
  ["Slope", "1", "2", "3", "4", "4", "5", "6", "7", "32.4"],
  ["Annual rainfall", "1/2", "1", "2", "3", "3", "4", "5", "6", "22.2"],
  ["Land cover", "1/3", "1/2", "1", "2", "2", "3", "4", "5", "14.6"],
  ["Soil clay", "1/4", "1/3", "1/2", "1", "1", "2", "3", "4", "9.2"],
  ["Curvature", "1/4", "1/3", "1/2", "1", "1", "2", "3", "4", "9.2"],
  ["Distance to streams", "1/5", "1/4", "1/3", "1/2", "1/2", "1", "2", "3", "5.8"],
  ["Elevation", "1/6", "1/5", "1/4", "1/3", "1/3", "1/2", "1", "2", "3.9"],
  ["Aspect", "1/7", "1/6", "1/5", "1/4", "1/4", "1/3", "1/2", "1", "2.7"],
];

// Table 4: share of the district in each score, per factor (%)
const T4: string[][] = [
  ["Slope", "24", "39", "24", "10", "3"],
  ["Annual rainfall", "32", "13", "18", "24", "13"],
  ["Land cover", "0.2", "43", "53", "2", "0.6"],
  ["Soil clay", "11", "19", "34", "27", "9"],
  ["Curvature", "0", "60", "20", "14", "7"],
  ["Distance to streams", "19", "34", "22", "12", "14"],
  ["Elevation", "11", "17", "33", "26", "13"],
  ["Aspect", "30", "25", "12", "8", "25"],
];

// Table 5: susceptibility classes, area and mapped landslides
const T5: string[][] = [
  ["Very low", "1.15 – 1.91", "644.2", "19.3", "0.0", "0.00"],
  ["Low", "1.91 – 2.41", "542.6", "16.2", "0.1", "0.01"],
  ["Moderate", "2.41 – 2.87", "844.2", "25.3", "4.5", "0.18"],
  ["High", "2.87 – 3.32", "918.9", "27.5", "38.2", "1.39"],
  ["Very high", "3.32 – 4.84", "392.2", "11.7", "57.2", "4.88"],
  ["Total", "", "3 342", "100", "100", ""],
];

// Table 6: buildings and people in each class
const T6: string[][] = [
  ["Very low", "26 364", "39.3", "61 200", "40.3"],
  ["Low", "9 056", "13.5", "21 000", "13.8"],
  ["Moderate", "13 292", "19.8", "25 600", "16.9"],
  ["High", "14 874", "22.2", "33 600", "22.1"],
  ["Very high", "3 471", "5.2", "10 400", "6.8"],
  ["Total", "67 057", "100", "151 800", "100"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function ChimanimaniLandslideCaseStudy() {
  return (
    <>
      <CaseLayout slug="chimanimani-landslide">
        <h1>Landslide Susceptibility Mapping of Chimanimani District Using GIS-Based Multi-Criteria Analysis and the Analytic Hierarchy Process</h1>
        <p className="tc__by">Eight terrain, rainfall, soil and land-cover factors reclassified, weighted with AHP and combined by weighted overlay.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (13 November 2026)</p>
        <Facts rows={[["Place", "Chimanimani District"], ["Period", "1991 to 2020 rainfall"], ["Data", "Copernicus DEM, CHIRPS, land cover, soil, buildings, mapped landslides"], ["Methods", "Multi-criteria decision analysis (MCDA), analytic hierarchy process (AHP), weighted overlay"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Chimanimani District is one of the most landslide-prone parts of Zimbabwe. Its eastern highlands are steep, deeply weathered and wet and heavy rain can loosen thousands of slopes at once. A landslide susceptibility map shows which ground is most likely to fail, judged from the physical conditions of each place, so that building, roads and warning can be planned around it.</p>
        <p>The map was built with GIS multi-criteria analysis, a method widely used for landslide studies (Pourghasemi, Pradhan and Gokceoglu, 2012; Kayastha, Dhital and De Smedt, 2013). Eight conditioning factors were mapped on a 30 m grid and each was reclassified into five susceptibility scores. The factors were weighted with the analytic hierarchy process (AHP; Saaty, 1980) and combined by weighted overlay into one landslide susceptibility index. The index was split into five classes and the result was checked against landslides mapped in the district, which played no part in building it.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To identify and classify the terrain, rainfall, soil and land-cover factors that control landslides in Chimanimani District.</li>
          <li>To derive factor weights with the analytic hierarchy process and evaluate the consistency of the judgements.</li>
          <li>To analyse the spatial pattern of landslide susceptibility across the district in five classes.</li>
          <li>To assess the agreement between the susceptibility classes and the mapped landslides.</li>
          <li>To assess the exposure of buildings and people in each susceptibility class.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Chimanimani District lies in the south-east of Manicaland Province in eastern Zimbabwe (Map 1). It covers 3 342 km². The land rises from about 300 m in the western lowlands to more than 2 000 m in the Chimanimani Mountains on the border with Mozambique. The eastern half is a high, broken plateau cut by steep valleys such as the Rusitu, while the western half is lower, flatter and drier. Long-term rainfall ranges from about 480 mm a year in the west to more than 1 500 mm in the east (Funk et al., 2015). The district had 153 619 people at the 2022 census (City Population, 2023). Many live in Chimanimani town, around Cashel and Chikukwa and along the Rusitu valley, all on or below steep slopes.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p className="tc__cap">Table 1. Data used in the study</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: ESA (2021); Funk et al. (2015); Karra et al. (2021); Hengl (2018); Sirko et al. (2021); Bondarenko et al. (2020); RMCA (2025); OCHA (2023). Rainfall, land cover, soil, buildings and population were processed in Google Earth Engine (Gorelick et al., 2017).</p>

        <h3>Landslide conditioning factors</h3>
        <p>All layers were placed on one 30 m grid in UTM zone 36S and eight factors were used. Slope is the main control, since steeper ground carries more shear stress. Mean annual rainfall is the CHIRPS daily rainfall summed and averaged over 1991 to 2020 and it stands for how wet the soil usually is. Land use and land cover matters because roots bind the soil, so bare ground and cropland fail more readily than forest. Soil clay content affects how water moves through the soil and how weak it becomes when wet.</p>
        <p>Curvature is the general curvature of the ground surface, taken from the lightly smoothed elevation model. Concave hollows gather water and soil and are where many slides begin. Distance to streams was measured from channels that drain 1 km² or more, because stream banks are undercut and wet. Elevation stands for the wetter, more deeply weathered uplands and aspect for the slopes that face the moist east and south-east winds.</p>

        <h3>Reclassification</h3>
        <p>Each factor was reclassified into five scores, from 1 (very low susceptibility) to 5 (very high), as Table 2 shows. The breaks follow the spread of each factor inside the district and the way it affects slope failure. Curvature has no score of 1, since no shape of ground is free of landslides, and ground flatter than 2° scores 1 for aspect. Map 2 shows all eight reclassified factors.</p>
        <p className="tc__cap">Table 2. Reclassification of the landslide conditioning factors</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Factor</th><th>1 Very low</th><th>2 Low</th><th>3 Moderate</th><th>4 High</th><th>5 Very high</th></tr></thead>
            <tbody><Rows rows={T2} num={9} /></tbody>
          </table>
        </div>
        <Fig src={map2} cap="Map 2. Reclassified Landslide Conditioning Factors, the eight factors scored from 1 (very low) to 5 (very high)." />

        <h3>Weighting with the analytic hierarchy process</h3>
        <p>The factors were compared in pairs on Saaty's 1 to 9 scale (Saaty, 1980), where 1 means two factors are equally important and 9 means one is extremely more important than the other (Table 3). Slope was judged the most important factor, followed by rainfall and land cover, then soil clay and curvature (equal), then distance to streams, elevation and aspect. The weights are the principal eigenvector of the matrix.</p>
        <p>The consistency of the judgements was checked with the consistency ratio, CR = CI ÷ RI, where CI = (λmax − n) ÷ (n − 1). For this matrix λmax = 8.208 and n = 8, so CI = 0.030. With a random index RI of 1.41 for eight factors, CR = 0.021. That is well below the 0.10 limit, so the judgements are consistent (Saaty, 1980).</p>
        <p className="tc__cap">Table 3. Pairwise comparison matrix and factor weights</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Factor</th><th>SL</th><th>RF</th><th>LC</th><th>SC</th><th>CU</th><th>DS</th><th>EL</th><th>AS</th><th>Weight (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">SL slope, RF annual rainfall, LC land cover, SC soil clay, CU curvature, DS distance to streams, EL elevation, AS aspect. λmax = 8.208, CI = 0.030, RI = 1.41, CR = 0.021.</p>
        <Fig src={fig1} cap="Figure 1. AHP weights of the eight landslide conditioning factors." />

        <h3>Weighted overlay and classification</h3>
        <p>The landslide susceptibility index (LSI) of each cell is the weighted sum of its eight scores:</p>
        <p>LSI = 0.324 SL + 0.222 RF + 0.146 LC + 0.092 SC + 0.092 CU + 0.058 DS + 0.039 EL + 0.027 AS</p>
        <p>The index can run from 1 to 5. In the district it ranges from 1.15 to 4.84. It was split into five classes (very low, low, moderate, high and very high) with natural breaks (Jenks, 1967). The share of the district in each class and in each factor score was then measured.</p>

        <h3>Check against mapped landslides</h3>
        <p>The landslide source points mapped across the district after the March 2019 storm (RMCA, 2025; Dille et al., 2026) were used as an independent check. They were not used to set any break or weight. The points were placed on the same grid, giving 10 213 landslide cells. For each class the share of landslide cells was compared with the share of area as a frequency ratio (FR), where a value above 1 means the class holds more landslides than its size alone would give. The area under the ROC curve (AUC) measures how well the index separates landslide cells from the rest of the district, where 0.5 is no better than chance and 1 is perfect. The same AUC was worked out for each factor on its own.</p>

        <h3>Exposure of buildings and people</h3>
        <p>Building footprints (Sirko et al., 2021) and gridded population for 2020 (Bondarenko et al., 2020) were placed on the 30 m grid and summed in each susceptibility class.</p>

        <h2>5 Results</h2>
        <h3>Reclassified factors</h3>
        <p>Each factor divides the district in its own way (Map 2, Table 4). Most of the district is gently to moderately sloping. Slopes steeper than 25° cover 13 % of it and three quarters of that steep ground lies east of 32.65° E. Rainfall rises from west to east and 37 % of the district receives more than 1 200 mm a year. Land cover is mostly rangeland and trees, so 96 % of the district scores 2 or 3 and bare ground and cropland are rare. Clay scores 4 or 5 on 36 % of the district, rising to 48 % in the east against 13 % in the west. Concave hollows (scores 4 and 5) make up 21 % of the ground and a quarter of the district faces east to south.</p>
        <p className="tc__cap">Table 4. Share of the district in each score, by factor (%)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Factor</th><th>1 Very low</th><th>2 Low</th><th>3 Moderate</th><th>4 High</th><th>5 Very high</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>

        <h3>Factor weights and consistency</h3>
        <p>Slope and rainfall together carry 54.6 % of the weight and land cover adds another 14.6 % (Figure 1, Table 3). Soil clay and curvature carry 9.2 % each, while distance to streams, elevation and aspect together carry 12.4 %. The consistency ratio of 0.021 shows that the pairwise judgements agree with each other well within Saaty's limit.</p>

        <h3>Landslide susceptibility</h3>
        <p>Map 3 shows the final landslide susceptibility map. The high and very high classes cover 1 311 km², or 39.2 % of the district (Table 5) and they lie almost all in the east. East of 32.65° E, 54.8 % of the land is in the high or very high class, against 9.5 % in the west. The very high class follows the steep, wet slopes of the Chimanimani Mountains, the Chikukwa hills and the sides of the Rusitu valley, where steep ground, heavy rain and clay soils come together. The western lowlands around Nyanyadzi, Hot Springs, Chakohwa and Mutambara are almost wholly very low and low. The very low and low classes together cover 35.5 % of the district.</p>
        <Fig src={map3} cap="Map 3. Landslide Susceptibility Map, five classes of the weighted overlay of eight reclassified factors." />
        <p className="tc__cap">Table 5. Area and mapped landslides in each landslide susceptibility class</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>LSI range</th><th>Area (km²)</th><th>Area (%)</th><th>Landslides (%)</th><th>FR</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; RMCA (2025). Landslides (%) is the share of the 10 213 landslide cells; FR is that share divided by the share of area.</p>

        <h3>Agreement with the mapped landslides</h3>
        <p>The map agrees closely with where landslides happened (Map 4, Figure 2). The high and very high classes hold 95.4 % of the landslide cells and the very high class alone holds 57.2 % on 11.7 % of the land, a frequency ratio of 4.88. The very low and low classes hold only 0.1 %. The AUC of the index is 0.867, which means that a landslide cell scores higher than a randomly chosen other cell 87 times in 100. West of 32.65° E, where a third of the district lies, there are only 4.1 % of the landslide cells.</p>
        <p>Of the single factors, slope agrees best with the landslides (AUC 0.83), followed by rainfall (0.73), soil clay (0.67), elevation (0.66), curvature (0.63) and aspect (0.57). Land cover (0.41) and distance to streams (0.42) fall below 0.5. Their scores run against the mapped landslides, which happened mostly on tree-covered slopes and on ground well away from streams.</p>
        <Fig src={map4} cap="Map 4. Mapped Landslides Over Landslide Susceptibility." />
        <Fig src={fig2} cap="Figure 2. Share of district area and of mapped landslides in each landslide susceptibility class." />

        <h3>Buildings and people</h3>
        <p>Most buildings and people are on safe ground, because the largest settlements lie in the western lowlands and on the gentler plateau (Figure 3, Table 6). The very low class alone holds 39.3 % of the buildings and 40.3 % of the people. Even so the high and very high classes hold 18 345 buildings (27.4 %) and about 44 000 people (28.9 %). The very high class has 3 471 buildings and about 10 400 people. Within 3 km of Rusitu, 87 % of the land is in the high or very high class, as is 77 % around Chikukwa, 63 % around Machongwe and 51 % around Chimanimani town.</p>
        <p className="tc__cap">Table 6. Buildings and people in each landslide susceptibility class</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>Buildings</th><th>Buildings (%)</th><th>People</th><th>People (%)</th></tr></thead>
            <tbody><Rows rows={T6} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; Sirko et al. (2021); Bondarenko et al. (2020). People are rounded to the nearest hundred.</p>
        <Fig src={fig3} cap="Figure 3. Share of buildings and people in each landslide susceptibility class." />

        <h2>6 Discussion</h2>
        <p>Landslide susceptibility in Chimanimani is controlled mainly by steep ground in the wettest part of the district. Slope and rainfall carry more than half of the weight and both are highest in the east, so the high classes gather in the highlands and the western lowlands are almost free of them. The mapped landslides follow the same pattern, which is why the index agrees with them well (AUC 0.867) even though they played no part in building it.</p>
        <p>Two factors did not behave as expected. Land cover and distance to streams scored the landslide ground lower than the rest of the district. Trees cover 60.3 % of the landslide cells against 43.4 % of the district and the median landslide cell lies 560 m from a stream against 424 m for the district as a whole. In this district trees did not stop failure under extreme rain and stream undercutting was not the main trigger. Their weights are small, so they change the final map little, but a revised version could lower them further.</p>
        <p>Because the weights come from expert judgement, another analyst could rank the factors differently. The consistency ratio shows that the judgements agree with each other, not that they are right. The rainfall factor is long-term mean rainfall, not the rain of a single storm, so the map shows where slopes are prone in general rather than where one storm will strike. The 30 m elevation model smooths out small hollows and stream banks, the rainfall and soil data are coarse (about 5 km and 250 m) and the land cover is from a single year. The map shows where landslides are likely, not how large they will be or how far they will run out.</p>

        <h2>7 Recommendations</h2>
        <ol>
          <li>Use the high and very high classes to guide where new homes, schools, clinics and roads are built, and keep new building off the very high ground around Rusitu, Chikukwa and the slopes above Chimanimani town.</li>
          <li>Give priority for early warning and evacuation planning to the settlements in and below the very high class when heavy rain is forecast.</li>
          <li>Inspect the slopes above roads and homes in the high and very high classes and improve drainage on them.</li>
          <li>Refine the map with a finer elevation model, geology and local rain gauge records, and review the land-cover and stream weights against the mapped landslides.</li>
        </ol>

        <h2>8 Conclusion</h2>
        <p>Eight factors were reclassified and weighted with AHP (CR = 0.021), with slope and rainfall carrying more than half of the weight. Their weighted overlay places 39.2 % of Chimanimani District in the high or very high class, almost all of it on the steep, wet eastern highlands, while the western lowlands are mostly very low and low. The map agrees closely with the mapped landslides, with 95.4 % of them in the two highest classes and an AUC of 0.867. Those classes hold 27.4 % of the district's buildings and 28.9 % of its people, most of them around Rusitu, Chikukwa, Machongwe and Chimanimani town.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Bondarenko, M., Kerr, D., Sorichetta, A. and Tatem, A.J. (2020) Census/projection-disaggregated gridded population datasets for 51 countries across sub-Saharan Africa in 2020 using building footprints. WorldPop, University of Southampton. <A href="https://doi.org/10.5258/SOTON/WP00682" /></p>
          <p>City Population (2023) Chimanimani (District, Zimbabwe): population statistics from the Zimbabwe National Statistics Agency census. <A href="https://www.citypopulation.de/en/zimbabwe/admin/manicaland/102__chimanimani/" /></p>
          <p>Dille, A. et al. (2026) Capturing the complete landslide–debris-rich flood continuum for accurate inventory, susceptibility and exposure mapping: lessons from Cyclone Idai. Natural Hazards and Earth System Sciences, 26, 2561-2577. <A href="https://doi.org/10.5194/nhess-26-2561-2026" /></p>
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Hengl, T. (2018) Clay content in % (kg / kg) at 6 standard depths (0, 10, 30, 60, 100 and 200 cm) at 250 m resolution. Zenodo. <A href="https://doi.org/10.5281/zenodo.2525663" /></p>
          <p>Jenks, G.F. (1967) The data model concept in statistical mapping. International Yearbook of Cartography, 7, 186-190.</p>
          <p>Karra, K., Kontgis, C., Statman-Weil, Z., Mazzariello, J.C., Mathis, M. and Brumby, S.P. (2021) Global land use/land cover with Sentinel 2 and deep learning. IEEE International Geoscience and Remote Sensing Symposium (IGARSS), 4704-4707. <A href="https://doi.org/10.1109/IGARSS47720.2021.9553499" /></p>
          <p>Kayastha, P., Dhital, M.R. and De Smedt, F. (2013) Application of the analytical hierarchy process (AHP) for landslide susceptibility mapping: a case study from the Tinau watershed, west Nepal. Computers and Geosciences, 52, 398-408. <A href="https://doi.org/10.1016/j.cageo.2012.11.003" /></p>
          <p>OCHA (2023) Zimbabwe subnational administrative boundaries (COD-AB). United Nations Office for the Coordination of Humanitarian Affairs, Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>Pourghasemi, H.R., Pradhan, B. and Gokceoglu, C. (2012) Application of fuzzy logic and analytical hierarchy process (AHP) to landslide susceptibility mapping at Haraz watershed, Iran. Natural Hazards, 63(2), 965-996. <A href="https://doi.org/10.1007/s11069-012-0217-2" /></p>
          <p>RMCA (2025) Landslide susceptibility and exposure assessment: Chimanimani and Chipinge districts, Zimbabwe. Royal Museum for Central Africa, on the UNESCO IHP Water Information Network System. <A href="https://doi.org/10.63253/nii4g2ac" /></p>
          <p>Saaty, T.L. (1980) The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation. McGraw-Hill, New York.</p>
          <p>Sirko, W., Kashubin, S., Ritter, M., Annkah, A. et al. (2021) Continental-scale building detection from high resolution satellite imagery. arXiv:2107.12283. <A href="https://doi.org/10.48550/arXiv.2107.12283" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
