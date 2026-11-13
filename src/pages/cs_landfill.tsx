import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/bulawayo-landfill/map1_study_area.webp";
import map2 from "../assets/casestudies/bulawayo-landfill/map2_factors.webp";
import map3 from "../assets/casestudies/bulawayo-landfill/map4_suitability.webp";
import map4 from "../assets/casestudies/bulawayo-landfill/map5_sites.webp";
import fig1 from "../assets/casestudies/bulawayo-landfill/fig2_weights.webp";
import fig2 from "../assets/casestudies/bulawayo-landfill/fig3_classes.webp";

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
  ["ESA WorldCover 10 m v200", "10 m", "2021", "Built-up land, water, wetland and land cover"],
  ["Google Open Buildings v3", "Building outlines", "2023", "Settlements"],
  ["iSDAsoil clay content, 0 to 20 cm", "30 m", "Modelled (2021)", "Soil clay"],
  ["Copernicus GLO-30 digital elevation model", "30 m", "2011 to 2015", "Slope"],
  ["Sentinel-2 surface reflectance", "20 m", "May to September 2024", "Background image on Map 4"],
  ["OpenStreetMap", "Lines and areas", "2026", "Rivers, water bodies, roads, airport runways, landfills"],
  ["OCHA administrative boundaries", "Areas", "2023", "City boundary"],
];

// Table 2: factor scores
const T2: string[][] = [
  ["Distance from settlements (m)", "Below 750", "750 to 1 000", "1 000 to 1 500", "1 500 to 2 000", "Above 2 000"],
  ["Distance from surface water (m)", "Below 500", "500 to 750", "750 to 1 000", "1 000 to 1 500", "Above 1 500"],
  ["Soil clay (%)", "Below 18", "18 to 21", "21 to 24", "24 to 27", "Above 27"],
  ["Slope (%)", "Above 15", "10 to 15", "5 to 10", "2 to 5", "Below 2"],
  ["Distance to roads (m)", "Above 3 000", "2 000 to 3 000", "1 000 to 2 000", "500 to 1 000", "Below 500"],
  ["Land cover", "Trees and other", "", "Cropland", "Shrubland", "Grassland and bare ground"],
];

// Table 3: pairwise comparison matrix and weights
const T3: string[][] = [
  ["Distance from settlements", "1", "1", "3", "3", "4", "5", "0.315"],
  ["Distance from surface water", "1", "1", "3", "3", "4", "5", "0.315"],
  ["Soil clay", "1/3", "1/3", "1", "1", "2", "3", "0.124"],
  ["Slope", "1/3", "1/3", "1", "1", "2", "3", "0.124"],
  ["Distance to roads", "1/4", "1/4", "1/2", "1/2", "1", "2", "0.074"],
  ["Land cover", "1/5", "1/5", "1/3", "1/3", "1/2", "1", "0.048"],
];

// Table 4: suitability classes
const T4: string[][] = [
  ["Very high (above 4.0)", "15.2", "2.8"],
  ["High (3.5 to 4.0)", "36.2", "6.6"],
  ["Moderate (3.0 to 3.5)", "136.7", "25.1"],
  ["Low (2.5 to 3.0)", "120.4", "22.1"],
  ["Very low (below 2.5)", "237.2", "43.5"],
  ["City", "545.7", "100"],
];

// Table 5: candidate sites
const T5: string[][] = [
  ["Site A (south)", "873", "4.08", "1.29", "1.73", "6.7"],
  ["Site B (north-west)", "432", "3.92", "2.05", "4.00", "17.5"],
  ["Site C (north-east)", "1 864", "3.85", "1.51", "3.58", "1.0"],
  ["Site D (north-east)", "154", "3.83", "1.06", "1.09", "1.5"],
];

// Table 6: existing landfills
const T6: string[][] = [
  ["Richmond landfill", "30", "1.90", "Very low", "163", "331"],
  ["Eastern dump site", "7", "2.28", "Very low", "143", "135"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function LandfillCaseStudy() {
  return (
    <>
      <CaseLayout slug="bulawayo-landfill">
        <h1>Landfill Site Selection for Bulawayo Using GIS-Based Multi-Criteria Analysis</h1>
        <p className="tc__by">Six weighted criteria used to find land fit for a new landfill.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (24 March 2026)</p>
        <Facts rows={[["Place", "Bulawayo"], ["Period", "2021 to 2024 data"], ["Data", "WorldCover, building outlines, soil clay, Copernicus DEM, OpenStreetMap"], ["Methods", "Multi-criteria decision analysis (MCDA), analytic hierarchy process (AHP), buffer analysis, weighted overlay"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Bulawayo is Zimbabwe's second city, with 665 952 people at the 2022 census (ZimStat, 2022). Most of its solid waste goes to the Richmond landfill, a 30 ha site run by the city council and worked by more than 240 waste pickers (UN-Habitat, 2022). The site is unlined, its disposal cells are almost full, and houses have grown up around it (UN-Habitat, 2022). The city will need a new site, and that site must keep waste away from homes, rivers and groundwater while staying close enough to roads for collection trucks.</p>
        <p>Choosing a landfill site is a long-standing use of geographic information systems. Several criteria are mapped and scored, and the scores are combined with weights to rank every part of the study area (Şener et al., 2006). The same approach was applied here to Bulawayo. Six siting factors were scored and weighted with the analytic hierarchy process (Saaty, 1980), suitability was mapped across the whole city, and the largest blocks of the best land were picked out as candidate sites.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To map and score six landfill siting factors for Bulawayo.</li>
          <li>To derive weights for the factors using the analytic hierarchy process.</li>
          <li>To map landfill suitability across the city.</li>
          <li>To identify and compare candidate landfill sites and assess the existing landfills against the same criteria.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Bulawayo lies in Matabeleland on the watershed between the Zambezi and Limpopo basins, at about 1 300 to 1 400 m above sea level (Map 1). The city covers 545.7 km². Its centre lies on a grid of streets, with suburbs spreading out on all sides and the high-density suburbs to the west and north-west. The Umguza, Khami and Umzingwane rivers and their tributaries drain the city to the north and south. Joshua Mqabuko Nkomo International Airport lies on the northern edge. Richmond landfill sits north-west of the centre between Cowdray Park and the northern suburbs, and a smaller dump site lies on the eastern edge of the city.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p className="tc__cap">Table 1. Data used in the study</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: Zanaga et al. (2022); Sirko et al. (2021); Hengl et al. (2021); ESA (2021); ESA (2024); OpenStreetMap contributors (2026); OCHA (2023). Raster data were processed in Google Earth Engine (Gorelick et al., 2017). All layers were placed on a 30 m grid in UTM zone 35S.</p>

        <h3>Siting factors</h3>
        <p>Six factors were used: distance from settlements, distance from surface water, soil clay, slope, distance to roads and land cover. Settlements were taken as built-up land in WorldCover, together with every 30 m cell at least one fifth covered by building outlines. Surface water was taken as the rivers, water bodies and wetlands in OpenStreetMap and WorldCover. Each factor was scored from 1 (very low suitability) to 5 (very high) (Table 2). Land far from homes and water scores high. Clay soils score high because they slow the movement of leachate into groundwater. Gentle slopes are easier to build on and shed less runoff, and land near roads is cheaper to serve. For land cover, grassland and bare ground score highest and trees lowest, so that woodland is not cleared.</p>
        <p className="tc__cap">Table 2. Factor scores</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Factor</th><th>1 Very low</th><th>2 Low</th><th>3 Moderate</th><th>4 High</th><th>5 Very high</th></tr></thead>
            <tbody><Rows rows={T2} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Distance from surface water is the distance to the nearest river, water body or wetland.</p>

        <h3>Factor weights</h3>
        <p>The factors were compared in pairs on Saaty's 1 to 9 scale, and the weights were taken from the principal eigenvector of the comparison matrix (Saaty, 1980). Distance from settlements and from surface water were rated most important, as in most landfill siting studies (Şener et al., 2006). The consistency ratio was checked against the limit of 0.10.</p>

        <h3>Suitability mapping</h3>
        <p>The suitability score of each cell was the weighted sum of its six factor scores, which gives a value between 1 and 5. The score was grouped into five classes across the whole city: very low (below 2.5), low (2.5 to 3.0), moderate (3.0 to 3.5), high (3.5 to 4.0) and very high (above 4.0).</p>

        <h3>Candidate sites and existing landfills</h3>
        <p>Cells in the high and very high classes were joined into blocks where they touch, including at corners. Blocks of at least 50 ha were kept and the four with the highest mean score were taken as candidate sites. For each site the mean distance to settlements and to main roads and the shortest distance to an airport runway were measured. The two existing landfills were scored in the same way. The Richmond landfill has no outline in OpenStreetMap, so it was drawn as a 30 ha circle around the location given by UN-Habitat (2022). The eastern dump site was taken from its OpenStreetMap outline.</p>

        <h2>5 Results</h2>
        <h3>Factor weights</h3>
        <p>Distance from settlements and distance from surface water carry the most weight, 0.315 each, which together is 63 % of the score (Table 3, Figure 1). Soil clay and slope follow at 0.124 each, then distance to roads (0.074) and land cover (0.048). The largest eigenvalue is 6.074. That gives a consistency index of 0.015 and a consistency ratio of 0.012, well under the limit of 0.10. Map 2 shows the six factor scores across the city. The settlement factor is very low over almost the whole built-up area, and the water factor follows the river network in narrow bands. Clay is highest in the east and south. Slope scores very high nearly everywhere, since the city is flat.</p>
        <p className="tc__cap">Table 3. Pairwise comparison matrix and weights</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Factor</th><th>SE</th><th>SW</th><th>CL</th><th>SL</th><th>RD</th><th>LC</th><th>Weight</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. SE settlements, SW surface water, CL soil clay, SL slope, RD roads, LC land cover. λmax 6.074, CI 0.015, CR 0.012.</p>
        <Fig src={fig1} cap="Figure 1. Weights of the six siting factors." />
        <Fig src={map2} cap="Map 2. Factor Suitability Maps." />

        <h3>Landfill suitability</h3>
        <p>Very low land is the largest class, at 237.2 km² or 43.5 % of the city, and it covers the built-up core and the river corridors (Table 4, Figure 2, Map 3). Low and moderate land together take up 257.1 km² (47.1 %) in a ring between the suburbs and the city edge. Only 51.4 km² (9.4 %) is highly or very highly suitable, and it lies in four places: the north-east around the airport, the southern tip of the city, the far north-west and a few patches on the western edge.</p>
        <p className="tc__cap">Table 4. Area of each suitability class</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class (score)</th><th>Area (km²)</th><th>Share of the city (%)</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study.</p>
        <Fig src={fig2} cap="Figure 2. Area of each suitability class." />
        <Fig src={map3} cap="Map 3. Landfill Suitability Map." />

        <h3>Candidate sites and existing landfills</h3>
        <p>The four best blocks of high and very high land range from 154 to 1 864 ha (Table 5, Map 4). Site A, at the southern tip of the city, ranks first with a mean score of 4.08. It covers 873 ha and lies on average 1.3 km from settlements, 1.7 km from a main road and 6.7 km from the airport. Site B in the north-west is farthest from settlements (2.1 km on average) but about 4 km from a main road. Sites C and D in the north-east are within 1.5 km of airport runways. Site C is the largest block, at 1 864 ha, and wraps around the end of the main runway. On the satellite image all four are open grassland or bush.</p>
        <p className="tc__cap">Table 5. Candidate sites</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Site</th><th>Area (ha)</th><th>Mean score</th><th>Distance to settlements (km)</th><th>Distance to main roads (km)</th><th>Distance to runway (km)</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Distances to settlements and roads are means over each site. Distance to runway is the shortest distance.</p>
        <p>Neither existing landfill does well; both fall in the very low class (Table 6). The Richmond site lies on average 163 m from homes and 331 m from water. The eastern dump site is 143 m from homes and 135 m from water.</p>
        <p className="tc__cap">Table 6. Existing landfills</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Landfill</th><th>Area (ha)</th><th>Mean score</th><th>Class</th><th>Distance to settlements (m)</th><th>Distance to surface water (m)</th></tr></thead>
            <tbody><Rows rows={T6} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Distances are means over each site.</p>
        <Fig src={map4} cap="Map 4. Candidate Landfill Sites Map." />

        <h2>6 Discussion</h2>
        <p>Inside its own boundary, Bulawayo has little good land for a landfill. Less than a tenth of the city is highly or very highly suitable, and nearly all of that lies at the edges, where the city is still growing. The best land will shrink as the suburbs spread, so a search that crosses into Umguza and Bulilima districts would offer more choice.</p>
        <p>For the north-eastern sites, the airport is the problem. Waste sites attract birds, and aviation guidance treats waste sites within about 3 km of a runway as a hazard to aircraft (FAA, 2007). Sites C and D lie inside that distance. They score well on the six factors but would be hard to get approved. Site A, far from the airport and close to a main road, is the stronger choice.</p>
        <p>Richmond landfill is an example of a city growing around its waste site. When it was chosen it lay well outside the built-up area. Houses now stand within 200 m of it, and it scores in the very low class. Any new site should be protected by a buffer written into the planning rules, so that housing cannot creep up to it.</p>
        <p>There are limits to the method. The weights come from judgement and would shift with the views of planners, engineers and residents. The clay layer is a continental model at 30 m and is no substitute for drilling. Groundwater depth and geology matter a great deal for leachate, but they were not mapped because no detailed data exist for the city. Settlements are taken from images of 2021 and 2023, so recent building may be missing, and the Richmond outline is an approximation. The candidate sites are places to survey, not final choices.</p>

        <h2>7 Recommendations</h2>
        <ol>
          <li>Survey Site A first, as the best scored site, far from the airport and with a short haul to a main road, and keep Site B as the second choice.</li>
          <li>Do not take Sites C and D forward without the agreement of the airport authority, because they lie within 1.5 km of runways.</li>
          <li>Drill test holes at the chosen site to measure groundwater depth and soil permeability before design.</li>
          <li>Protect a buffer of at least 500 m around the chosen site in the city plan, so that housing does not reach it as it reached Richmond.</li>
          <li>Repeat the analysis across the city boundary into Umguza and Bulilima districts, and ask planners and residents to review the weights.</li>
        </ol>

        <h2>8 Conclusion</h2>
        <p>Distance from settlements and distance from surface water carry 63 % of the weight, with a consistency ratio of 0.012. Only 51.4 km² (9.4 %) of Bulawayo is highly or very highly suitable for a landfill, against 43.5 % that is very low. Four candidate sites of 154 to 1 864 ha were found. The best is Site A at the southern edge of the city, with a mean score of 4.08. The existing Richmond landfill falls in the very low class, which confirms that a new site is needed.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>ESA (2024) Sentinel-2 MSI Level-2A surface reflectance. European Space Agency, Copernicus programme.</p>
          <p>FAA (2007) Hazardous wildlife attractants on or near airports. Advisory Circular 150/5200-33B. Federal Aviation Administration, Washington, DC.</p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Hengl, T., Miller, M.A.E., Križan, J., Shepherd, K.D. et al. (2021) African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Scientific Reports, 11, 6130. <A href="https://doi.org/10.1038/s41598-021-85639-y" /></p>
          <p>OCHA (2023) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>OpenStreetMap contributors (2026) OpenStreetMap. <A href="https://www.openstreetmap.org" /></p>
          <p>Saaty, T.L. (1980) The Analytic Hierarchy Process. McGraw-Hill, New York.</p>
          <p>Şener, B., Süzen, M.L. and Doyuran, V. (2006) Landfill site selection by using geographic information systems. Environmental Geology, 49, 376-388. <A href="https://doi.org/10.1007/s00254-005-0075-2" /></p>
          <p>Sirko, W., Kashubin, S., Ritter, M., Annkah, A. et al. (2021) Continental-scale building detection from high resolution satellite imagery. arXiv:2107.12283. <A href="https://arxiv.org/abs/2107.12283" /></p>
          <p>UN-Habitat (2022) Waste Wise Cities Tool: Bulawayo, Zimbabwe. United Nations Human Settlements Programme, Nairobi. <A href="https://unhabitat.org/sites/default/files/2022/07/bulawayo_en.pdf" /></p>
          <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
          <p>ZimStat (2022) 2022 Population and Housing Census: preliminary report. Zimbabwe National Statistics Agency, Harare.</p>
        </div>
      </CaseLayout>
    </>
  );
}
