import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/solar-site-suitability/map1_study_area.webp";
import map2 from "../assets/casestudies/solar-site-suitability/map2_ghi.webp";
import map3 from "../assets/casestudies/solar-site-suitability/map3_criteria.webp";
import map4 from "../assets/casestudies/solar-site-suitability/map4_constraints.webp";
import map5 from "../assets/casestudies/solar-site-suitability/map5_suitability.webp";
import fig1 from "../assets/casestudies/solar-site-suitability/fig1_weights.webp";
import fig2 from "../assets/casestudies/solar-site-suitability/fig2_classes.webp";
import fig3 from "../assets/casestudies/solar-site-suitability/fig3_sensitivity.webp";
import fig4 from "../assets/casestudies/solar-site-suitability/fig4_districts.webp";

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

// Table 1: pairwise comparison matrix and weights
const T1: string[][] = [
  ["Solar resource (GHI)", "1", "3", "4", "5", "5", "7", "0.444"],
  ["Distance to grid", "1/3", "1", "2", "3", "3", "5", "0.215"],
  ["Slope", "1/4", "1/2", "1", "2", "2", "4", "0.137"],
  ["Distance to roads", "1/5", "1/3", "1/2", "1", "1", "3", "0.083"],
  ["Land cover", "1/5", "1/3", "1/2", "1", "1", "3", "0.083"],
  ["Distance to settlements", "1/7", "1/5", "1/4", "1/3", "1/3", "1", "0.038"],
];

// Table 2: scoring scheme
const T2: string[][] = [
  ["GHI (kWh/m²/day)", "over 6.00", "5.80 to 6.00", "5.60 to 5.80", "5.40 to 5.60", "5.40 or less"],
  ["Distance to grid (km)", "5 or less", "5 to 10", "10 to 20", "20 to 40", "over 40"],
  ["Slope (degrees)", "1 or less", "1 to 2", "2 to 3", "3 to 5", "over 5 (excluded)"],
  ["Distance to roads (km)", "2 or less", "2 to 5", "5 to 10", "10 to 20", "over 20"],
  ["Land cover", "Bare or sparse", "Grassland", "Shrubland", "Cropland", "Trees"],
  ["Distance to settlements (km)", "10 or less", "10 to 25", "25 to 50", "50 to 100", "over 100"],
];

// Table 3: exclusion constraints
const T3: string[][] = [
  ["Slope over 5°", "Copernicus GLO-30 DEM", "10.2"],
  ["Permanent water", "JRC Global Surface Water; ESA WorldCover", "0.6"],
  ["Wetland and mangrove", "ESA WorldCover", "0.0"],
  ["Built-up land plus 500 m", "ESA WorldCover (dominant class)", "0.2"],
  ["Protected areas plus 500 m", "World Database on Protected Areas", "23.4"],
];

// Table 4: districts — area, mean GHI, mean score, High+ km²
const T4: string[][] = [
  ["Bulilima", "6 432", "6.05", "3.62", "2 669"],
  ["Mangwe", "5 718", "5.85", "3.50", "2 631"],
  ["Matobo", "7 241", "5.75", "3.06", "1 266"],
  ["Insiza", "8 224", "5.70", "2.98", "981"],
  ["Umzingwane", "2 780", "5.73", "3.17", "444"],
  ["Gwanda", "10 714", "5.56", "2.71", "322"],
  ["Plumtree", "174", "5.96", "3.56", "105"],
  ["Beitbridge", "12 737", "5.42", "2.34", "28"],
];

// Table 5: validation sites
const T5: string[][] = [
  ["Blanket Mine Solar Farm", "12", "Operating", "Moderate", "3.30", "3.4"],
  ["ZPC-Intratrek Gwanda", "100", "Proposed", "Moderate", "3.39", "5.8"],
  ["Gwanda Timber Farm (Matshela)", "100", "Licensed", "Excluded (built-up)", "—", "0.9"],
  ["Nottingham Estate", "4.5", "Operating", "Low", "2.56", "13.1"],
  ["Falcon College, Esigodini", "1", "Operating", "Low", "2.83", "15.7"],
  ["Mashaba Solar Mini-Grid", "0.1", "Operating", "Excluded (protected)", "—", "61.0"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function SolarCaseStudy() {
  return (
    <>
      <CaseLayout slug="solar-site-suitability">
        <h1>Site Suitability Analysis for Utility-Scale Solar Farms in Matabeleland South Province of Zimbabwe Using the Analytic Hierarchy Process</h1>
        <p className="tc__by">AHP weighted overlay of six siting criteria on a 250 m grid.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (11 August 2025)</p>
        <Facts rows={[["Place", "Matabeleland South, 54 133 km²"], ["Data", "Global Solar Atlas, Copernicus DEM, WorldCover, OpenStreetMap"], ["Method", "AHP weighted overlay of six criteria, 250 m grid"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Zimbabwe does not generate enough electricity. Installed capacity of about 2 400 MW rests mainly on the Kariba hydropower station, whose output falls in drought years, and the ageing coal units at Hwange, and in recent years load shedding has at times exceeded twelve hours a day. The National Renewable Energy Policy set targets of 1 100 MW of renewable capacity by 2025 and 2 100 MW by 2030 (Government of Zimbabwe, 2019), and the Zimbabwe Energy Regulatory Authority has licensed dozens of independent solar producers, yet few plants have been built and fewer than 50 MW of utility-scale solar were operating by 2024.</p>
        <p>Where a solar farm is placed decides much of its cost: the strength of the resource, the length of the transmission connection, the earthworks, the access roads and the land that must be taken. A geographic information system can weigh all of these at once. This case study applies the analytic hierarchy process (AHP), a structured method for deriving weights from pairwise comparisons (Saaty, 1980), to six siting criteria across Matabeleland South, the province with the strongest solar resource in the country, and maps the suitability of every 250 m cell of land. The method follows published GIS-AHP siting studies in Saudi Arabia (Al Garni and Awasthi, 2017), Mauritius (Doorga et al., 2019), Iran (Noorollahi et al., 2016), Spain (Sánchez-Lozano et al., 2013), Turkey (Uyan, 2013) and Zimbabwe itself (Mutume, 2023), and the result is checked against the solar plants that exist in the province today.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To derive weights for six solar farm siting criteria by pairwise comparison using the analytic hierarchy process and to test their consistency.</li>
          <li>To exclude land where a solar farm cannot reasonably be built using hard constraints for slope, water, built-up land and protected areas.</li>
          <li>To map the suitability of the remaining land on a 250 m grid by a weighted overlay of the scored criteria.</li>
          <li>To test the sensitivity of the suitable area to each criterion weight.</li>
          <li>To compare the mapped suitability against the locations of existing, licensed and proposed solar plants in the province.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Matabeleland South lies in the south-west of Zimbabwe, between Bulawayo and the South African border at Beitbridge, and borders Botswana in the west (Map 1). It covers 54 133 km² in this analysis, within 0.1% of the official 54 172 km², across the districts of Beitbridge, Bulilima, Gwanda, Insiza, Mangwe, Matobo and Umzingwane. The land is mostly flat to gently undulating savanna between 500 m and 1 500 m, broken by the granite hills of the Matobo range south of Bulawayo. Gwanda is the provincial capital; the main towns of Plumtree, Beitbridge, Esigodini and Filabusi are small, and the province held about 760 000 people in 2022, the second lowest provincial population in the country.</p>
        <p>The province is the driest in Zimbabwe. The rainfall analysis in case study 2 of this series gave it the lowest seasonal normal of any province, 450 mm, and one of the highest coefficients of variation, near 30%. The same low cloud cover that limits its farming gives it the country's best solar resource. Two regional transmission corridors cross the province, from Insukamini near Bulawayo west towards Plumtree and the Botswana border, and south through Gwanda to Beitbridge, and these lines set how far any new plant must build to connect.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p>Six criteria and five constraints were assembled on a common 250 m grid in the UTM zone 35S projection, about 866 000 cells over the province. The solar resource was the long-term average daily global horizontal irradiation (GHI) of the Global Solar Atlas version 2 (Solargis, 2019), resampled bilinearly from its 250 m native grid. Slope was derived from the Copernicus GLO-30 digital elevation model (ESA, 2021) and averaged to the grid. Land cover came from ESA WorldCover 2021 at 10 m, taking the dominant class of each cell (Zanaga et al., 2022). Permanent water was taken from the JRC Global Surface Water dataset (Pekel et al., 2016), settlements from the GHS-SMOD 2020 settlement model (Schiavina et al., 2023), and protected areas from the World Database on Protected Areas (UNEP-WCMC and IUCN, 2025). Transmission lines of 66 kV to 400 kV and major roads were extracted from OpenStreetMap (OpenStreetMap contributors, 2025), and straight-line distances to the nearest line, road and settlement were computed for every cell. Areas were computed in an equal-area projection (EPSG:6933).</p>
        <h3>Criteria and weights</h3>
        <p>The six criteria were compared in pairs on Saaty's one-to-nine scale, informed by the weights of six published solar siting studies. The solar resource was judged the dominant criterion, as in every published study consulted; distance to the grid second, because transmission construction is the largest location-dependent cost; then slope, distance to roads, land cover and distance to settlements (Table 1). The weights are the principal eigenvector of the matrix. The consistency ratio was 0.023, well below the 0.10 limit of Saaty (1980), so the judgements are internally consistent.</p>
        <p className="tc__cap">Table 1. Pairwise comparison matrix and the resulting weights</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Criterion</th><th className="n">GHI</th><th className="n">Grid</th><th className="n">Slope</th><th className="n">Roads</th><th className="n">Land cover</th><th className="n">Settlements</th><th className="n">Weight</th></tr></thead>
            <tbody><Rows rows={T1} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Consistency ratio 0.023 (λmax = 6.145, n = 6, random index 1.24).</p>
        <p>Each criterion was scored from 1 to 5 on each cell (Table 2). The GHI classes follow the range found in the province, 5.0 to 6.1 kWh/m²/day; the slope, grid, road and land cover classes follow the published studies. Bare and sparsely vegetated ground scores highest for land cover and tree cover lowest, since clearing woodland raises cost and loses carbon. Distance to settlements was scored in favour of nearer cells, since the plants serve load and their construction uses local labour, but it carries the smallest weight.</p>
        <p className="tc__cap">Table 2. Criterion classes and scores</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Criterion</th><th className="n">5</th><th className="n">4</th><th className="n">3</th><th className="n">2</th><th className="n">1</th></tr></thead>
            <tbody><Rows rows={T2} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: class limits set from Al Garni and Awasthi (2017), Doorga et al. (2019), Noorollahi et al. (2016) and the GHI range of the province.</p>
        <h3>Constraints</h3>
        <p>Cells failing any hard constraint were removed before the overlay: slope over 5°, permanent water, wetland, dominantly built-up cells with a 500 m buffer, and protected areas with a 500 m buffer (Table 3). Built-up land was taken as the cells whose dominant 10 m class is built; flagging any cell containing a single built pixel would have excluded 30% of the province through scattered homesteads, against 0.2% under the dominant rule, and the looser rule was judged unrealistic for a rural province.</p>
        <h3>Overlay, sensitivity and validation</h3>
        <p>The suitability of each remaining cell was the weighted sum of its six scores, a value between 1 and 5, classified into five classes at equal breaks of 0.5 from 2.5 to 4.0. The sensitivity of the result was tested by raising and lowering each weight by 20%, renormalising the weights and recomputing the High and Very high area. Finally the suitability was read at the locations of six solar plants in the province, operating, licensed or proposed, compiled from regulator licences, company announcements and news reports.</p>

        <h2>5 Results</h2>
        <h3>Criterion weights</h3>
        <p>The weights were 0.444 for GHI, 0.215 for distance to grid, 0.137 for slope, 0.083 each for distance to roads and land cover, and 0.038 for distance to settlements. Figure 1 places them against the published studies: the GHI weight sits between the 0.401 of Doorga et al. (2019) and the 0.555 of Mutume (2023), with Al Garni and Awasthi (2017) at 0.322; the grid weight lies between the 0.112 of Noorollahi et al. (2016) and the 0.415 of Sánchez-Lozano et al. (2013); and the slope weight is close to the 0.163 of Al Garni and Awasthi. The consistency ratio of 0.023 is lower than the 0.041 to 0.071 reported by those studies.</p>
        <Fig src={fig1} cap="Figure 1. Criterion weights of this study (bars) against the weight five published solar siting studies gave the same criterion (diamonds)." />

        <h3>The solar resource</h3>
        <p>The long-term GHI of the province runs from 5.0 to 6.1 kWh/m²/day and rises steadily from south-east to north-west (Map 2). The median cell receives 5.66 kWh/m²/day, close to the national average of about 5.7 reported by Mutume (2023). The far west is the richest: Bulilima district averages 6.05 and Mangwe 5.85, while Beitbridge, lower and cloudier in summer, averages 5.42. For comparison, these western values exceed the resource of most operating solar farms in Germany or the United Kingdom by half or more.</p>
        <Fig src={map2} cap="Map 2. Global Horizontal Irradiance Map, long-term average daily GHI from the Global Solar Atlas." />

        <h3>Criterion scores</h3>
        <p>Map 3 shows the six scored criteria with their weights. The GHI score follows the north-west gradient. The grid score forms corridors along the Insukamini to Plumtree and Gwanda to Beitbridge lines, and most of the far south and the Botswana border strip lie more than 40 km from a line. Slope scores are high nearly everywhere except the Matobo hills. The road network is dense in the centre and sparse in the west and south. Land cover is mostly shrubland and grassland with cropland concentrated in the communal lands, and almost the whole province lies within 25 km of a settlement cluster.</p>
        <Fig src={map3} cap="Map 3. Criteria Score Maps, the six scored criteria with their AHP weights, and the excluded areas." />

        <h3>Excluded land</h3>
        <p>The constraints removed 32.0% of the province (Map 4, Table 3). Protected areas with their buffer account for 23.4%, mainly the Tuli and Maleme blocks in the south and west, the Matobo National Park and the forest and safari areas along the Botswana border. Slope over 5° removed 10.2%, almost all of it in the Matobo range and along the Insiza and Umzingwane valleys. Water, wetland and built-up land together removed less than 1%. The remaining analysable land covers 36 824 km², 68.0% of the province.</p>
        <p className="tc__cap">Table 3. Exclusion constraints and the share of the province excluded</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Constraint</th><th>Source</th><th className="n">Share of province (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={2} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Shares overlap where a cell fails more than one constraint; together the constraints exclude 32.0%.</p>
        <Fig src={map4} cap="Map 4. Exclusion Constraints Map, land removed before the weighted overlay, by cause." />

        <h3>Suitability</h3>
        <p>Of the analysable land, 1 483 km² (4.0%) is Very high, 6 968 km² (18.9%) High, 8 827 km² (24.0%) Moderate, 11 420 km² (31.0%) Low and 8 126 km² (22.1%) Unsuitable (Map 5, Figure 2). The suitable land is strongly concentrated: Bulilima holds 2 669 km² of High or better and Mangwe 2 631 km², together 63% of the provincial total, where high irradiation, flat ground and the Plumtree transmission corridor coincide (Table 4, Figure 4). Matobo (1 266 km²) and Insiza (981 km²) follow. Beitbridge, the largest district, holds just 28 km², because its resource is the weakest and most of it lies far from both lines, and much of Gwanda district scores Low for the same reason once outside the corridor through Gwanda town.</p>
        <Fig src={map5} cap="Map 5. Solar Farm Suitability Map, weighted overlay of the six criteria with existing and planned plants." />
        <Fig src={fig2} cap="Figure 2. Area of each suitability class." />
        <p className="tc__cap">Table 4. Suitability by district</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>District</th><th className="n">Area (km²)</th><th className="n">Mean GHI (kWh/m²/day)</th><th className="n">Mean score</th><th className="n">High and Very high (km²)</th></tr></thead>
            <tbody>
              <Rows rows={T4} num={1} />
              <tr className="t"><td>Matabeleland South</td><td className="n">54 133</td><td className="n">5.66</td><td className="n">2.95</td><td className="n">8 451</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Plumtree town is listed separately in the boundary data; the small Beitbridge and Gwanda urban districts (112 km² together) are included in the provincial total. Provincial mean GHI is the median cell; mean score is over analysable cells.</p>
        <Fig src={fig4} cap="Figure 4. High and Very high area by district." />

        <h3>Sensitivity</h3>
        <p>The ranking is stable under reweighting (Figure 3). A 20% change in the GHI weight changes the High and Very high area by −7.2% to +4.4%, the largest response of any criterion; every other weight changes it by less than 4%, and the western concentration of suitable land does not move. The result depends more on the class limits chosen for GHI than on the exact weights, which is the common finding of the published studies.</p>
        <Fig src={fig3} cap="Figure 3. Change in High and Very high area when each weight is raised or lowered by 20%." />

        <h3>Validation against existing plants</h3>
        <p>The six known solar plants of the province behave consistently with the map (Table 5). The two utility-scale projects near Gwanda, the operating 12 MW plant at Blanket Mine and the proposed 100 MW ZPC-Intratrek site, both score Moderate, 3.30 and 3.39, above the analysable mean of 2.95: they sit on good but not exceptional resource, chosen for the mine load and the substation rather than for irradiation. The licensed 100 MW Gwanda Timber Farm site falls on cells the model excludes as built-up, its own cleared footprint 0.9 km from the grid. The two small plants at Nottingham Estate and Falcon College score Low; both are behind-the-meter plants built at their load, 13 km and 16 km from the transmission grid. The Mashaba mini-grid falls inside a protected-area buffer 61 km from the grid, which is exactly why it was built as an off-grid system. No plant has yet been built in the Bulilima-Mangwe zone the model ranks highest.</p>
        <p className="tc__cap">Table 5. Solar plants of the province against the suitability map</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Plant</th><th className="n">Capacity (MW)</th><th className="n">Status</th><th className="n">Model class</th><th className="n">Score</th><th className="n">Distance to grid (km)</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: plant locations from ZERA licence records, company announcements and news reports; class and score from this study.</p>

        <h2>6 Discussion</h2>
        <p>The weights, the consistency ratio and the shares found here all sit inside the range of the published literature. The 4.0% of analysable land in the top class compares with the 3.8% of Mauritius found by Doorga et al. (2019) and the 8.8% of the Karapinar region found by Uyan (2013). The area figures are internally checked: the rasterised province measures 54 133 km² against the official 54 172 km², a difference of 0.1%, and the provincial GHI median of 5.66 kWh/m²/day agrees with the national average of about 5.7 reported by Mutume (2023) from the same Solargis data.</p>
        <p>The validation is honest rather than flattering. The plants that exist score Moderate or Low, not High, because none of them was sited for resource: the mine plant serves a mine, the estate plants serve estates, and the mini-grid serves a clinic and shops where the grid will not reach. This is the expected relationship between a resource-led map and load-led projects, and it is the gap the map exposes: the best 8 451 km² of the province, overwhelmingly in Bulilima and Mangwe along the Plumtree corridor, holds no plant at all. At a conservative 30 MW per km² of panels on even 1% of that land, the zone could host more than the country's entire present generation capacity.</p>
        <p>The analysis has limits. OpenStreetMap transmission lines are incomplete in rural Zimbabwe, and distance to a line says nothing about the spare capacity of that line or its substations, which only the utility knows. GHI is the right resource measure for photovoltaics but not for concentrated solar power, which depends on direct irradiation and which Mutume (2023) found viable further north at Hwange and Lupane. Land tenure, which decides whether a site can actually be leased, is not mapped: most of Bulilima and Mangwe is communal land, where assembly of a 200-hectare site needs negotiation that freehold land near Gwanda does not. The 250 m grid also smooths away small terrain breaks, and WorldCover maps some fallow fields as grassland. The map is therefore a screening tool for where detailed work should start, not a substitute for it.</p>

        <h2>7 Recommendations</h2>
        <p>Prefeasibility work for utility-scale solar in Matabeleland South should start in the Bulilima-Mangwe corridor within 10 km of the Insukamini to Plumtree 132 kV line, where the model places the largest contiguous High and Very high zone in the province. The Zimbabwe Electricity Transmission and Distribution Company should publish the hosting capacity of this line and of the Gwanda to Beitbridge corridor, since grid capacity, not land or resource, is the binding constraint the map cannot see.</p>
        <p>Licensing should weigh resource as well as connection. The plants licensed so far sit on Moderate ground near substations; a tender zoned on this map, as South Africa's renewable energy zones were, would steer the next 100 MW onto land a full suitability class higher at similar connection cost.</p>
        <p>For the south and east of the province, Beitbridge above all, the map argues against utility-scale solar and for the mini-grid model already proven at Mashaba: the resource is weaker, the grid is distant, and settlement is sparse. The same analysis should be repeated with direct normal irradiation and relaxed grid limits if concentrated solar or storage-backed plants are considered.</p>
        <p>The exclusion of 23.4% of the province for protected areas should be kept under review, since several of the western blocks are safari and forest areas rather than national parks, and policy may in future allow solar development on degraded parts of them. Any site advanced from this screening needs ground verification of slope, land cover and tenure before design.</p>

        <h2>8 Conclusion</h2>
        <p>The study met its five objectives. First, the pairwise comparison gave weights of 0.444 for solar resource, 0.215 for grid distance, 0.137 for slope, 0.083 for roads and land cover and 0.038 for settlements, with a consistency ratio of 0.023, and each weight sits inside the range of six published studies. Second, hard constraints removed 32.0% of the province, mostly protected areas (23.4%) and steep ground (10.2%), leaving 36 824 km² analysable. Third, the weighted overlay placed 1 483 km² in the Very high class and 6 968 km² in the High class, 22.9% of the analysable land, concentrated in Bulilima and Mangwe districts where high irradiation, flat ground and the Plumtree transmission corridor meet. Fourth, the result is stable: no 20% change in any weight moves the High and Very high area by more than 7.2% or shifts its western concentration. Fifth, the six existing and planned plants of the province score Moderate or Low or fall on excluded cells, consistent with their siting at mines, estates and off-grid settlements rather than on the best resource, which remains unused. The province could host utility-scale solar far beyond the national renewable energy targets, and the place to begin is the west.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Al Garni, H.Z. and Awasthi, A. (2017) Solar PV power plant site selection using a GIS-AHP based approach with application in Saudi Arabia. Applied Energy, 206, 1225-1240. <A href="https://doi.org/10.1016/j.apenergy.2017.10.024" /></p>
          <p>Doorga, J.R.S., Rughooputh, S.D.D.V. and Boojhawon, R. (2019) Multi-criteria GIS-based modelling technique for identifying potential solar farm sites: A case study in Mauritius. Renewable Energy, 133, 1201-1219. <A href="https://doi.org/10.1016/j.renene.2018.08.105" /></p>
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>Government of Zimbabwe (2019) National Renewable Energy Policy. Ministry of Energy and Power Development, Harare. <A href="https://www.zera.co.zw/National_Renewable_Energy_Policy_Final.pdf" /></p>
          <p>Mutume, B. (2023) A feasibility assessment of utilizing concentrated solar power (CSP) in the Zimbabwean regions of Hwange and Lupane. Heliyon, 9(7), e18210. <A href="https://doi.org/10.1016/j.heliyon.2023.e18210" /></p>
          <p>Noorollahi, E., Fadai, D., Akbarpour Shirazi, M. and Ghodsipour, S.H. (2016) Land suitability analysis for solar farms exploitation using GIS and fuzzy analytic hierarchy process (FAHP) - a case study of Iran. Energies, 9(8), 643. <A href="https://doi.org/10.3390/en9080643" /></p>
          <p>OpenStreetMap contributors (2025) Power lines and roads of Zimbabwe. <A href="https://www.openstreetmap.org" /></p>
          <p>Pekel, J.F., Cottam, A., Gorelick, N. and Belward, A.S. (2016) High-resolution mapping of global surface water and its long-term changes. Nature, 540, 418-422. <A href="https://doi.org/10.1038/nature20584" /></p>
          <p>Saaty, T.L. (1980) The Analytic Hierarchy Process. McGraw-Hill, New York.</p>
          <p>Sánchez-Lozano, J.M., Teruel-Solano, J., Soto-Elvira, P.L. and García-Cascales, M.S. (2013) Geographical Information Systems (GIS) and Multi-Criteria Decision Making (MCDM) methods for the evaluation of solar farms locations: Case study in south-eastern Spain. Renewable and Sustainable Energy Reviews, 24, 544-556. <A href="https://doi.org/10.1016/j.rser.2013.03.019" /></p>
          <p>Schiavina, M., Melchiorri, M. and Pesaresi, M. (2023) GHS-SMOD R2023A - GHS settlement layers. Joint Research Centre, European Commission. <A href="https://doi.org/10.2905/A0DF7A6F-49DE-46EA-9BDE-563437A6E2BA" /></p>
          <p>Solargis (2019) Global Solar Atlas 2.0. World Bank Group, ESMAP. <A href="https://globalsolaratlas.info" /></p>
          <p>UNEP-WCMC and IUCN (2025) World Database on Protected Areas. Protected Planet. <A href="https://www.protectedplanet.net" /></p>
          <p>Uyan, M. (2013) GIS-based solar farms site selection using analytic hierarchy process (AHP) in Karapinar region, Konya/Turkey. Renewable and Sustainable Energy Reviews, 28, 11-17. <A href="https://doi.org/10.1016/j.rser.2013.07.042" /></p>
          <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
