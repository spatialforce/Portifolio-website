import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/hwange-chizarira-corridor/map1_study_area.webp";
import map2 from "../assets/casestudies/hwange-chizarira-corridor/map2_land_cover.webp";
import map3 from "../assets/casestudies/hwange-chizarira-corridor/map3_factors.webp";
import map4 from "../assets/casestudies/hwange-chizarira-corridor/map4_resistance.webp";
import map5 from "../assets/casestudies/hwange-chizarira-corridor/map5_corridor.webp";
import map6 from "../assets/casestudies/hwange-chizarira-corridor/map6_pressures.webp";
import fig1 from "../assets/casestudies/hwange-chizarira-corridor/fig1_path_cover.webp";
import fig2 from "../assets/casestudies/hwange-chizarira-corridor/fig2_path_profile.webp";
import fig3 from "../assets/casestudies/hwange-chizarira-corridor/fig3_sensitivity.webp";

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

function Table({ cap, head, rows, num, src }: { cap: string; head: string[]; rows: string[][]; num: number; src: string }) {
  return (
    <>
      <p className="tc__cap">{cap}</p>
      <div className="tc__tw">
        <table>
          <thead><tr>{head.map((h, i) => <th key={h} className={i >= num ? "n" : undefined}>{h}</th>)}</tr></thead>
          <tbody>{rows.map((r) => <tr key={r.join("|")}>{r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}</tr>)}</tbody>
        </table>
      </div>
      <p className="tc__src">{src}</p>
    </>
  );
}

const T1 = [
  ["ESA WorldCover v200", "10 m, resampled to 100 m (majority)", "2021", "Land cover factor"],
  ["Copernicus DEM GLO-30", "30 m, slope at about 60 m, averaged to 100 m", "2011 to 2015", "Slope factor and elevation"],
  ["WorldPop constrained population (UN adjusted)", "3 arc-seconds (about 100 m)", "2020", "Population density factor"],
  ["OpenStreetMap roads and rivers", "Lines (725 roads, 602 rivers)", "2026", "Road and water factors"],
  ["World Database on Protected Areas", "Areas", "2026", "Parks, safari areas, forests and wildlife management areas"],
  ["OCHA administrative boundaries and Natural Earth lakes", "Areas", "2020", "Land mask"],
];

const T2: [string, string, [string, string][]][] = [
  ["Population density (people per km²)", "0.419", [["< 2", "1"], ["2 – 5", "10"], ["5 – 11", "40"], ["11 – 25", "80"], ["> 25", "100"]]],
  ["Land cover", "0.263", [["Tree cover", "1"], ["Shrubland", "5"], ["Grassland", "10"], ["Wetland", "20"], ["Bare ground", "50"], ["Cropland", "80"], ["Built-up and water", "100"]]],
  ["Distance to a main road (m)", "0.160", [["< 500", "100"], ["500 – 1 000", "70"], ["1 000 – 2 000", "40"], ["2 000 – 5 000", "15"], ["> 5 000", "1"]]],
  ["Distance to a river or water (m)", "0.097", [["< 1 000", "1"], ["1 000 – 3 000", "10"], ["3 000 – 5 000", "30"], ["5 000 – 10 000", "60"], ["> 10 000", "100"]]],
  ["Slope (degrees)", "0.062", [["< 5", "1"], ["5 – 10", "10"], ["10 – 20", "40"], ["20 – 30", "70"], ["> 30", "100"]]],
];

function FactorTable() {
  return (
    <>
      <p className="tc__cap">Table 2. Factors, classes, resistance values and AHP weights</p>
      <div className="tc__tw">
        <table>
          <thead><tr><th>Factor</th><th>Class</th><th className="n">Resistance</th><th className="n">Weight</th></tr></thead>
          <tbody>
            {T2.map(([f, w, cls]) => cls.map(([c, r], i) => (
              <tr key={f + c}>
                {i === 0 && <td rowSpan={cls.length}>{f}</td>}
                <td>{c}</td>
                <td className="n">{r}</td>
                {i === 0 && <td rowSpan={cls.length} className="n">{w}</td>}
              </tr>
            )))}
          </tbody>
        </table>
      </div>
      <p className="tc__src">Source: this study. Consistency ratio 0.015.</p>
    </>
  );
}

const T3 = [
  ["Low (1 to 10)", "31.3"],
  ["Moderate (10 to 25)", "22.2"],
  ["High (25 to 50)", "25.7"],
  ["Very high (50 to 100)", "20.9"],
];

const T4 = [
  ["High (within 5 % of the least cost)", "1 443", "619"],
  ["Moderate (5 to 10 %)", "699", "1 781"],
  ["Low (10 to 20 %)", "1 415", "—"],
];

const T5 = [
  ["Deka Safari Area", "Safari area", "1.7"],
  ["Lubu", "Wildlife management area", "10.2"],
  ["Nekatambe", "Wildlife management area", "23.3"],
  ["Saba-Lubanda", "Wildlife management area", "29.6"],
  ["Sikalenge", "Wildlife management area", "21.4"],
  ["Communal land outside these areas", "—", "66.5"],
];

const T6 = [
  ["Base (AHP weights)", "152.5", "100", "100"],
  ["Equal weights (0.2 each)", "159.9", "67.7", "50.6"],
  ["Land cover first (people and land cover swapped)", "153.1", "100", "100"],
  ["People doubled", "150.6", "100", "100"],
  ["Without water", "150.3", "100", "69.2"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function CorridorCaseStudy() {
  return (
    <CaseLayout slug="hwange-chizarira-corridor">
      <h1>Least-Cost Corridor Analysis for Elephant Movement Between Hwange and Chizarira National Parks, Zimbabwe</h1>
      <p className="tc__by">Five weighted resistance factors used to trace the cheapest route and corridor between the two parks.</p>
      <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (11 November 2026)</p>
      <Facts rows={[["Place", "Hwange and Binga districts, Matabeleland North"], ["Period", "2020 to 2021"], ["Data", "ESA WorldCover, Copernicus DEM, WorldPop, OpenStreetMap, WDPA"], ["Methods", "AHP cost surface, least-cost path, least-cost corridor analysis"], ["Tools", "Python (scikit-image, rasterio, GeoPandas)"]]} />

      <h2>1 Introduction</h2>
      <p>Hwange National Park in the west of Zimbabwe holds one of the largest elephant populations in Africa, while Chizarira National Park, about 115 km to the north-east, lies in the Sebungwe region, where elephant numbers fell by about three quarters between 2001 and 2014 (Chase et al., 2016). Both parks are part of the Kavango–Zambezi Transfrontier Conservation Area, which aims to keep wildlife able to move between protected areas. The land between them is not a park. It is communal land in Hwange and Binga districts, where villages, fields and roads sit beside wildlife management areas run by rural district councils.</p>
      <p>Elephants range over hundreds of kilometres, but they avoid people, roads and steep ground (Hoare and du Toit, 1999; Wall et al. 2006; Roever et al., 2013). If the land between Hwange and Chizarira fills with settlement, the two populations will be cut off from each other. Least-cost modelling is a common way of finding where animals can most easily cross such land (Adriaensen et al. 2003; Beier et al., 2008). Every cell of a resistance surface carries a cost of crossing and the route with the lowest total cost is the most likely line of movement. Such a surface was built here for elephants and used to find the path and the wider corridor between the two parks, the places where the corridor is narrowest and the pressures along it.</p>

      <h2>2 Objectives</h2>
      <ol>
        <li>To model the resistance of the landscape between Hwange and Chizarira National Parks to elephant movement from five weighted factors.</li>
        <li>To delineate the least-cost path and the least-cost corridor between the two parks.</li>
        <li>To examine the land cover, people, roads and protection along the corridor and identify its narrowest point.</li>
        <li>To evaluate how sensitive the path and the corridor are to the factor weights.</li>
      </ol>

      <h2>3 Study area</h2>
      <p>The study area is a box from 25.95° E to 29.15° E and from 19.05° S to 17.35° S in Matabeleland North, holding 55 788 km² of land in Zimbabwe (Map 1). Zambia and Lake Kariba to the north were treated as closed to movement, because the study is concerned with the route inside Zimbabwe. The box holds the northern half of Hwange National Park (7 343 km² of its 14 651 km²), the whole of Chizarira National Park (1 947 km²), the Matetsi, Deka, Sijarira, Chete and Chirisa safari areas, several state forests and a ring of wildlife management areas. The shortest straight line between the two parks is 115.3 km. The land rises from about 500 m in the Zambezi valley to over 1 300 m in the Chizarira hills and it is covered mainly by mopane and miombo woodland and shrubland. People live in scattered villages, densest along the Bulawayo to Victoria Falls highway and the road to Binga.</p>
      <Fig src={map1} cap="Map 1. Study Area Map, showing Hwange and Chizarira National Parks and the safari areas and forests around them." />

      <h2>4 Data and methods</h2>
      <p>All data were projected to UTM zone 35S and placed on one grid of 100 m cells (Table 1). Areas and distances were measured on this grid.</p>
      <Table cap="Table 1. Data used in the study" head={["Dataset", "Resolution", "Date", "Use"]} rows={T1} num={9}
        src="Source: Zanaga et al. (2022); European Space Agency (2021); Bondarenko et al. (2020); OpenStreetMap contributors (2026); UNEP-WCMC and IUCN (2026); OCHA (2020)." />

      <h3>Resistance surface</h3>
      <p>Five factors known to slow or turn back elephants were taken from the literature (Table 2). Population density was measured as the number of people within a moving window of 2.1 km, so that a single village counts across the land around it. Its breaks make resistance rise steeply above about 11 people per km², close to the densities at which elephants disappeared from the Sebungwe (Hoare and du Toit, 1999). Woodland and shrubland got the lowest resistance and cropland, built-up land and open water the highest. Resistance falls away from main roads and rises away from rivers, because elephants must drink every day or two. Slope was included because climbing steep ground costs elephants a lot of energy (Wall et al. 2006). Each factor was reclassified to a scale from 1 (easy to cross) to 100 (hard to cross).</p>
      <p>The weights were set by the Analytic Hierarchy Process (Saaty, 1977). The five factors were compared in pairs, with population ranked above land cover, land cover above roads, roads above water and water above slope and the weights were taken from the principal eigenvector of the comparison matrix. The consistency ratio was 0.015 (λmax 5.068), well below the limit of 0.10, so the comparisons were consistent. The resistance surface was the weighted sum of the five factors.</p>
      <FactorTable />

      <h3>Least-cost path and corridor</h3>
      <p>The cost of reaching every cell from Hwange National Park and from Chizarira, was found with a cost-distance algorithm that moves in eight directions and allows for the longer diagonal steps (van der Walt et al., 2014). The least-cost path was traced back from the cell of Chizarira that was cheapest to reach from Hwange and only the stretch between the two parks was kept. Adding the two cost surfaces together gives, in every cell, the cost of the cheapest route between the parks that passes through it, with the path itself at the lowest value. Cells within 5 % of that value were classed as high corridor, cells within 5 to 10 % as moderate and cells within 10 to 20 % as low. Here, the corridor means the high and moderate classes together, the land within 10 % of the least cost.</p>

      <h3>Conditions along the corridor</h3>
      <p>Land cover, people, protected areas and wildlife management areas were summarised for the path and for the corridor. Road crossings were found where the path cut an OpenStreetMap road. The width of the corridor was measured at every cell of the path as twice the distance from the path to the edge of the corridor and the narrowest point outside the parks was found from these widths.</p>

      <h3>Sensitivity to the weights</h3>
      <p>The path was traced again with four other sets of weights: equal weights, land cover and population swapped, the population weight doubled and the water factor removed. Each new path was compared with the base path by its length, the share of it inside the base corridor and the share of it within 2 km of the base path.</p>

      <h2>5 Results</h2>
      <h3>Resistance to elephant movement</h3>
      <p>Most of the land between the parks is woodland or shrubland, which elephants cross easily (Map 2). Cropland and settlement are found mainly along the main roads and around Hwange town, Dete, Lupane and Binga. Of the five factors, population density and distance to water had the highest mean resistance (42.4 and 39.8 out of 100), while slope had the lowest (3.8), because steep ground is found only on the escarpments (Map 3).</p>
      <Fig src={map2} cap="Map 2. Land Cover Map (2021)." />
      <Fig src={map3} cap="Map 3. Resistance Factors Map, each factor reclassified from 1 (easy to cross) to 100 (hard to cross)." />
      <p>The combined resistance had a mean of 28.5 and a median of 20.7 (Map 4). Close to a third of the land (31.3 %) fell in the low class and about a fifth (20.9 %) in the very high class (Table 3). Low resistance covers the woodland of the parks, the safari areas and much of the communal land in the north of Hwange District and in Binga. The highest values follow the roads and the villages around them and form a belt along the Bulawayo to Victoria Falls highway on the northern edge of Hwange National Park.</p>
      <Table cap="Table 3. Share of the land in each resistance class" head={["Resistance class", "Share of land (%)"]} rows={T3} num={1}
        src="Source: this study. Land in Zimbabwe inside the study area, 55 788 km²." />
      <Fig src={map4} cap="Map 4. Resistance Surface Map, the weighted sum of the five factors." />

      <h3>Least-cost path and corridor</h3>
      <p>The least-cost path leaves Hwange National Park at its north-eastern corner, near the Deka Safari Area and heads north-east to enter Chizarira National Park on its western side (Map 5). At 152.6 km it is about one third longer (ratio 1.32) than the straight line between the parks, because it bends round the villages along the roads. Its accumulated cost was 717.0 and its mean cost per cell 4.6, less than a quarter of the median for the whole area. The path starts at about 990 m, drops into the lowlands south of the Zambezi valley to a lowest point of 544 m and climbs to 1 096 m before it reaches Chizarira.</p>
      <p>The corridor within 10 % of the least cost covers 2 142 km², of which 1 443 km² is high corridor and 699 km² moderate (Table 4). A further 1 415 km² falls in the low class. The corridor is widest in its first 50 km north-east of Hwange, where it is about 10 km across and narrowest where it crosses the Binga road.</p>
      <Table cap="Table 4. Area and population of the corridor classes" head={["Corridor class", "Area (km²)", "People"]} rows={T4} num={1}
        src="Source: this study, from WorldPop 2020. People are rounded to the nearest whole number and are not given for the low class, which lies outside the corridor used in this study." />
      <Fig src={map5} cap="Map 5. Least-Cost Corridor Map, the corridor classes and the least-cost path between Hwange and Chizarira National Parks." />

      <h3>Conditions along the corridor</h3>
      <p>Woodland made up more than half of the path (88.0 km) and shrubland most of the rest (63.1 km), with only 1.5 km of grassland and no cropland (Figure 1). In the corridor as a whole shrubland was the main cover (60.5 %), followed by tree cover (35.4 %), with small areas of grassland (2.4 %) and cropland (1.6 %). About 2 400 people live in the corridor, 619 of them in the high class, at a mean density of 1.1 people per km². The highest density on the path itself was 6.0 people per km².</p>
      <Fig src={fig1} cap="Figure 1. Land cover along the least-cost path." />
      <p>The path crosses three main roads: the Bulawayo to Victoria Falls highway at km 18.9, the Binga road at km 69.7 and a smaller road at km 133.8. Each crossing appears as a peak in the resistance along the path (Figure 2). Only 1.7 km of the path lies in a protected area, in the Deka Safari Area. Most of it (84.4 km, or 55 %) runs through four wildlife management areas, Lubu, Nekatambe, Saba-Lubanda and Sikalenge and the remaining 66.5 km crosses communal land (Table 5). Of the corridor as a whole, 4.9 % is protected land and 47.5 % is in wildlife management areas.</p>
      <Table cap="Table 5. Length of the least-cost path in each type of land" head={["Area", "Type", "Length (km)"]} rows={T5} num={2}
        src="Source: this study, from the World Database on Protected Areas. Total 152.6 km." />
      <Fig src={fig2} cap="Figure 2. Resistance along the least-cost path from Hwange to Chizarira National Park, with the narrowest point of the corridor." />
      <p>The median width of the corridor along the path was 5.9 km and no part of it was narrower than 2 km. The narrowest point (2.2 km) lies at km 68.7, about 1 km before the path crosses the Binga road (Map 6). The land there is woodland, but it lies 860 m from the road and has 4.2 people per km² and settlement lines the road on both sides. Map 6 shows the corridor passing between areas of higher population density along the roads.</p>
      <Fig src={map6} cap="Map 6. Corridor Pressures Map, population density, main roads and the narrowest point of the corridor." />

      <h3>Sensitivity to the weights</h3>
      <p>The path was stable under three of the four other weight sets (Table 6, Figure 3). When land cover and population were swapped, or the population weight doubled, the new path lay wholly inside the base corridor and within 2 km of the base path. When the water factor was removed, the path stayed inside the corridor but only 69.2 % of it lay within 2 km of the base path, because it no longer followed the rivers. Equal weights gave the greatest change: the path was 7.4 km longer and only about two thirds of it (67.7 %) lay inside the base corridor.</p>
      <Table cap="Table 6. Least-cost paths under other weight sets" head={["Weight set", "Length (km)", "Inside base corridor (%)", "Within 2 km of base path (%)"]} rows={T6} num={1}
        src="Source: this study. The base length differs from 152.6 km by 0.1 km because lengths in this table were measured between cell centres." />
      <Fig src={fig3} cap="Figure 3. Share of each alternative path inside the base corridor and within 2 km of the base path." />

      <h2>6 Discussion</h2>
      <p>An easy route for elephants still exists between Hwange and Chizarira. It runs through woodland and shrubland, carries few people and is nowhere narrower than about 2 km. That fits studies showing that elephants in the region favour woodland near water and avoid settled land (Hoare and du Toit, 1999; Roever et al. 2013). The route leans heavily on the wildlife management areas, which hold more than half of the path and almost half of the corridor. These areas have no legal protection as parks and are open to settlement and cultivation. The link is most likely to break at the two road crossings and above all at the Binga road, where the corridor is narrowest and settlement is growing.</p>
      <p>The sensitivity test shows that population and land cover set the position of the path. As long as these two factors carry most of the weight, the path stays where it is. It moved away from the base corridor only when all five factors were weighted equally, so that slope and water counted as much as people. The location of the corridor therefore holds up under reasonable changes in the weights, even if its exact edges are less certain.</p>
      <p>The model has limits. The resistance values and weights come from the literature and expert judgement, not from tracked elephants and they have not been tested against movement data. An attempt was made to test the model with GBIF records of elephants, but only four usable records fell in the study area, because the locations of elephant sightings on iNaturalist are blurred by about 30 km to protect the animals, so no test was possible. Studies elsewhere have shown that corridors from resistance models can differ from those used by collared elephants, especially between seasons (Osipova et al., 2019). The population data are for 2020 and the land cover for 2021, so newer settlement is not included. OpenStreetMap roads may be incomplete in remote areas. The corridor ends at the border, although elephants also move through Zambia and along the Lake Kariba shore, which were closed in the model.</p>

      <h2>7 Recommendations</h2>
      <p>The Hwange and Binga rural district councils should keep the wildlife management areas of Lubu, Nekatambe, Saba-Lubanda and Sikalenge free of new fields and settlement, since together they carry more than half of the path. Land use plans for these wards should mark the corridor shown on Map 5.</p>
      <p>The crossing of the Binga road near km 69, where the corridor narrows to about 2 km, should be treated as a priority. New homesteads there should be discouraged and warning signs and lower speed limits should be placed where the path crosses the Binga road and the Bulawayo to Victoria Falls highway.</p>
      <p>The Zimbabwe Parks and Wildlife Management Authority should collar elephants in the north-east of Hwange and in Chizarira, so that the corridor can be tested against real movements and the resistance values fitted from data. The analysis should be repeated when newer population and land cover data become available, so that the narrowing of the corridor can be tracked.</p>

      <h2>8 Conclusion</h2>
      <p>A resistance surface built from population, land cover, roads, water and slope gives a 152.6 km least-cost path for elephants between Hwange and Chizarira National Parks and a corridor of 2 142 km² within 10 % of the least cost. The path runs mainly through woodland and shrubland, crosses three main roads and spends more than half of its length in four wildlife management areas. It is narrowest, at 2.2 km, beside the Binga road. Under most other weight sets the path stayed in the same place, so the corridor looks like a stable feature of the landscape, but one that rests on land without formal protection.</p>

      <h2>References</h2>
      <div className="tc__ref">
        <p>Adriaensen, F., Chardon, J.P., De Blust, G., Swinnen, E. et al. (2003) The application of 'least-cost' modelling as a functional landscape model. Landscape and Urban Planning, 64(4), 233-247. <A href="https://doi.org/10.1016/S0169-2046(02)00242-6" /></p>
        <p>Beier, P., Majka, D.R. and Spencer, W.D. (2008) Forks in the road: choices in procedures for designing wildland linkages. Conservation Biology, 22(4), 836-851. <A href="https://doi.org/10.1111/j.1523-1739.2008.00942.x" /></p>
        <p>Bondarenko, M., Kerr, D., Sorichetta, A. and Tatem, A.J. (2020) Census/projection-disaggregated gridded population datasets for 51 countries across sub-Saharan Africa in 2020 using building footprints. WorldPop, University of Southampton. <A href="https://doi.org/10.5258/SOTON/WP00682" /></p>
        <p>Chase, M.J., Schlossberg, S., Griffin, C.R., Bouché, P.J.C. et al. (2016) Continent-wide survey reveals massive decline in African savannah elephants. PeerJ, 4, e2354. <A href="https://doi.org/10.7717/peerj.2354" /></p>
        <p>European Space Agency (2021) Copernicus Global Digital Elevation Model (GLO-30). <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
        <p>Hoare, R.E. and du Toit, J.T. (1999) Coexistence between people and elephants in African savannas. Conservation Biology, 13(3), 633-639. <A href="https://doi.org/10.1046/j.1523-1739.1999.98035.x" /></p>
        <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
        <p>OpenStreetMap contributors (2026) OpenStreetMap data for Zimbabwe, retrieved through the Overpass API. <A href="https://www.openstreetmap.org" /></p>
        <p>Osipova, L., Okello, M.M., Njumbi, S.J., Ngene, S. et al. (2019) Validating movement corridors for African elephants predicted from resistance-based landscape connectivity models. Landscape Ecology, 34, 865-878. <A href="https://doi.org/10.1007/s10980-019-00811-0" /></p>
        <p>Roever, C.L., van Aarde, R.J. and Leggett, K. (2013) Functional connectivity within conservation networks: delineating corridors for African elephants. Biological Conservation, 157, 128-135. <A href="https://doi.org/10.1016/j.biocon.2012.06.025" /></p>
        <p>Saaty, T.L. (1977) A scaling method for priorities in hierarchical structures. Journal of Mathematical Psychology, 15(3), 234-281. <A href="https://doi.org/10.1016/0022-2496(77)90033-5" /></p>
        <p>UNEP-WCMC and IUCN (2026) Protected Planet: The World Database on Protected Areas (WDPA). Cambridge, UK. <A href="https://www.protectedplanet.net" /></p>
        <p>van der Walt, S., Schönberger, J.L., Nunez-Iglesias, J., Boulogne, F. et al. (2014) scikit-image: image processing in Python. PeerJ, 2, e453. <A href="https://doi.org/10.7717/peerj.453" /></p>
        <p>Wall, J., Douglas-Hamilton, I. and Vollrath, F. (2006) Elephants avoid costly mountaineering. Current Biology, 16(14), R527-R529. <A href="https://doi.org/10.1016/j.cub.2006.06.049" /></p>
        <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
      </div>
    </CaseLayout>
  );
}
