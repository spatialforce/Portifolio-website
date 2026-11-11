import SiteNav, { SiteFooter } from "./SiteChrome";
import "./casestudy.css";
import gwStudyArea from "../assets/Gweru_Study_Area.webp";
import factorsA from "../assets/Chimanimani_Factors_A.webp";
import factorsB from "../assets/Chimanimani_Factors_B.webp";
import floodRisk from "../assets/Chimanimani_Flood_Risk.webp";
import gwMaps from "../assets/Gweru_Flood_Susceptibility_Maps.webp";

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

function A({ href }: { href: string }) {
  return <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;
}

// Table 1: Chimanimani factors, weight %, very high risk range
const T1: string[][] = [
  ["Slope", "25", "0 to 6.85°"],
  ["Distance to river", "20", "0 to 250 m"],
  ["Topographic Wetness Index (TWI)", "20", "9.68 to 20.82"],
  ["Drainage density", "15", "0.25 to 0.37 km/km²"],
  ["NDVI", "10", "−0.14 to 0.14"],
  ["Flow length", "10", "0 to 10 213 m"],
];

// Table 2: Chimanimani class, area ha, % area, buildings, % buildings
const T2: string[][] = [
  ["Very low", "49 108.3", "14.7", "1 617", "2.7"],
  ["Low", "109 474.3", "32.8", "12 571", "21.1"],
  ["Moderate", "94 152.6", "28.2", "18 892", "31.7"],
  ["High", "55 824.5", "16.7", "17 684", "29.7"],
  ["Very high", "24 900.3", "7.5", "8 853", "14.8"],
];

// Table 3: Gweru class, area ha, %
const T3: string[][] = [
  ["Very low", "1 280.1", "7.8"],
  ["Low", "2 333.4", "14.2"],
  ["Moderate", "5 410.1", "32.9"],
  ["High", "4 340.5", "26.4"],
  ["Very high", "3 073.9", "18.7"],
];

export default function FloodSusceptibilityMapping() {
  return (
    <>
      <SiteNav />
      <article className="cs">
        <h1>Flood Susceptibility Mapping of Chimanimani District and Gweru Urban Using Weighted Overlay Analysis</h1>
        <p className="cs__by">Kudzanai Chakavarika. November 2026.</p>

        <h2>Introduction</h2>
        <p>Floods are among the most frequent natural hazards in Zimbabwe, and their effects are felt both in mountain districts and in towns. In March 2019 Cyclone Idai brought heavy rain, floods and landslides to the eastern highlands. In Chimanimani District it claimed about 300 lives, more than 325 people were reported missing and about 4 000 people were displaced (Matsvange et al., 2020, cited in Munsaka et al., 2021). The disaster exposed gaps in disaster planning and early warning in the district (Munsaka et al., 2021).</p>
        <p>Flooding is also a problem in cities that are not usually thought of as flood prone. Gweru, on the central plateau, flooded in the 2020/21 rainy season, when low-lying suburbs such as Mkoba, Riverside, Athlone and Nashville were affected (Matsa and Mupepi, 2022; Nehanda Radio, 2021). Matsa and Mupepi (2022) linked the damage to building on former wetlands. In both places a map of land that is naturally prone to flooding is a practical first step for planning. This study produces such maps for Chimanimani District and Gweru Urban with two weighted overlay models.</p>

        <h2>Objectives</h2>
        <p>The aim of the study is to map flood susceptibility in a mountain district and in an urban area of Zimbabwe. The specific objectives are:</p>
        <ol>
          <li>To analyse the terrain and land cover factors that control flood susceptibility in Chimanimani District.</li>
          <li>To map flood susceptibility zones in Chimanimani District and assess the buildings exposed in each zone.</li>
          <li>To map flood susceptibility in Gweru Urban from Sentinel-1 surface moisture and terrain.</li>
        </ol>

        <h2>Study area</h2>
        <p>Chimanimani District lies in Manicaland Province on the border with Mozambique. Its eastern part is high and rugged mountain land, while the west falls towards the Save valley around Birchenough Bridge and the Nyanyadzi River. The district covers about 333 460 ha in the analysis.</p>
        <p>Gweru Urban is the capital of the Midlands Province and lies on the central plateau between Harare and Bulawayo. The study area is the urban boundary of 16 438 ha, divided into 18 wards (Map 1). The Gweru River runs through the city.</p>
        <Fig src={gwStudyArea} cap="Map 1. Study Area Map of Gweru Urban, with its 18 wards, Gweru District and Zimbabwe." />

        <h2>Data and methods</h2>
        <p>Both models used a weighted overlay. Each factor was reclassified into five classes from very low (1) to very high (5) susceptibility, each class was multiplied by the weight of its factor, and the weighted classes were added. The result was divided into five susceptibility zones from very low to very high.</p>
        <p>The steps used for each objective are described below in the order of the objectives.</p>
        <h3>Flood factors in Chimanimani District</h3>
        <p>Six factor layers were made for the district: slope, distance to river, Topographic Wetness Index (TWI), drainage density, NDVI and flow length. Slope, TWI, drainage density and flow length were derived from a digital elevation model. The river network for the distance and drainage density layers was extracted from flow accumulation with a threshold of more than 35 000 cells. NDVI was calculated from satellite imagery. Each layer was split into five classes, and the weights were set according to the importance of each factor for flooding, with slope given the largest weight (Table 1). Gentle slopes, short distance to rivers, high TWI, high drainage density, low NDVI and short flow length were scored as high susceptibility.</p>
        <p className="cs__cap">Table 1. Factors and weights used for Chimanimani District</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Factor</th><th className="n">Weight (%)</th><th className="n">Very high class</th></tr></thead>
            <tbody>
              <Rows rows={T1} num={1} />
              <tr className="t"><td>Total</td><td className="n">100</td><td className="n"></td></tr>
            </tbody>
          </table>
        </div>
        <p className="cs__src">Source: own analysis.</p>
        <h3>Flood susceptibility zones and buildings in Chimanimani District</h3>
        <p>The six weighted layers were combined into the final susceptibility map, and the area of each zone was calculated. To assess exposure, OpenStreetMap building footprints (59 617 buildings) were overlaid on the map and the buildings in each zone were counted.</p>
        <h3>Flood susceptibility in Gweru Urban</h3>
        <p>Sentinel-1 scenes of the 2024 dry season were processed in SNAP with orbit correction, thermal noise removal, radiometric calibration, speckle filtering and terrain correction. A surface moisture index was calculated as the difference between the VH and VV backscatter. Dry season images were used so that the index shows ground that stays wet without recent rain. Slope and elevation were derived from a digital elevation model in QGIS, with class breaks set from the statistics of the study area. Land cover from ESA WorldCover was added, and all layers were clipped to the urban boundary. The layers were reclassified and combined in a weighted sum in the QGIS raster calculator, and the area of each class was then calculated.</p>

        <h2>Results</h2>
        <h3>Flood factors in Chimanimani District</h3>
        <p>The factor maps show a clear contrast between the west and the east of the district (Map 2 and Map 3). Low NDVI and gentle slopes are concentrated in the western half, where farming has cleared much of the vegetation. Short flow lengths run along the western and southern edges. High TWI picks out the valley floors that collect water, and the distance layer shows narrow strips of very high susceptibility along the river channels. The eastern highlands score low on most factors because of their steep slopes and dense vegetation.</p>
        <Fig src={factorsA} cap="Map 2. Flood Factor Maps of Chimanimani District: NDVI, Drainage Density, Slope and Flow Length." />
        <Fig src={factorsB} cap="Map 3. Flood Factor Maps of Chimanimani District: Topographic Wetness Index and Distance to River." />

        <h3>Flood susceptibility zones and buildings in Chimanimani District</h3>
        <p>High and very high susceptibility follow the rivers and valley floors (Map 4). Together they cover 80 725 ha, or 24.2% of the district (Table 2). Low susceptibility is the largest zone (32.8%), and moderate susceptibility covers most of the centre of the district. A belt of high to very high susceptibility runs along the western edge through wards 2, 3, 4, 5, 8 and 20, from Birchenough Bridge and the Nyanyadzi River towards the north-west. Murare, Chakowa, Hotsprings and Nenohwe business centre lie inside this belt. Kopa shopping centre in Nyahode (ward 21) also lies in a high susceptibility zone. The eastern highlands, including wards 1, 7 and 11, fall in the lowest zones.</p>
        <Fig src={floodRisk} cap="Map 4. Flood Susceptibility Map of Chimanimani District." />
        <p>Buildings are not spread across the zones in proportion to their area. Of the 59 617 buildings, 26 537 (44.5%) stand in the high and very high zones, which cover 24.2% of the land. Only 2.7% of buildings stand in the very low zone, although it covers 14.7% of the district. The largest group of buildings (31.7%) is in the moderate zone.</p>
        <p className="cs__cap">Table 2. Area and buildings in each flood susceptibility zone of Chimanimani District</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Zone</th><th className="n">Area (ha)</th><th className="n">Area (%)</th><th className="n">Buildings</th><th className="n">Buildings (%)</th></tr></thead>
            <tbody>
              <Rows rows={T2} num={1} />
              <tr className="t"><td>Total</td><td className="n">333 460.0</td><td className="n">100.0</td><td className="n">59 617</td><td className="n">100.0</td></tr>
            </tbody>
          </table>
        </div>
        <p className="cs__src">Source: own analysis. Buildings from OpenStreetMap.</p>

        <h3>Flood susceptibility in Gweru Urban</h3>
        <p>The surface moisture index shows the ground that stays wet in the dry season, and the terrain index shows how slope and elevation steer water through the city (Map 5). In the combined map the highest susceptibility lies along the Gweru River and other low ground, where low ground and gentle slopes slow runoff. High and very high susceptibility together cover 7 414 ha, or 45.1% of the city (Table 3). Moderate is the largest class (32.9%), and low and very low cover the remaining 22.0%.</p>
        <Fig src={gwMaps} cap="Map 5. Surface Moisture, Terrain Index and Flood Susceptibility Maps of Gweru Urban (2024)." />
        <p className="cs__cap">Table 3. Area in each flood susceptibility class of Gweru Urban</p>
        <div className="cs__tw">
          <table>
            <thead><tr><th>Class</th><th className="n">Area (ha)</th><th className="n">Area (%)</th></tr></thead>
            <tbody>
              <Rows rows={T3} num={1} />
              <tr className="t"><td>Total</td><td className="n">16 438.0</td><td className="n">100.0</td></tr>
            </tbody>
          </table>
        </div>
        <p className="cs__src">Source: own analysis of Sentinel-1 imagery (2024 dry season), a digital elevation model and ESA WorldCover.</p>
        <p>Several of the high susceptibility zones match suburbs known to flood: Mkoba 6, Mtapa, Riverside, parts of Senga and the central business district. Some of them also show a wet radar signal in the dry season, which points to poor drainage, clay soils or blocked storm drains. Other high zones follow former wetlands and river banks. The lowest susceptibility is on the higher, better drained ground with trees and natural cover.</p>

        <h2>Discussion</h2>
        <p>The two models show that flood susceptibility in both places follows the shape of the land and the river network. In Chimanimani the most susceptible land is the low western part of the district, while the safest land is in the steep east. The building counts show that people live mostly on the more susceptible ground: nearly half of the buildings stand on the quarter of the district rated high or very high. This is partly because flat land near rivers is easier to farm and build on, and the safest mountain land has little room for settlement.</p>
        <p>In Gweru the high susceptibility zones along the Gweru River include suburbs that flooded in 2020/21, and some follow former wetlands that are now built up. This agrees with Matsa and Mupepi (2022), who found that development on former wetlands increased flood damage in the city.</p>
        <p>The maps have several limits. They are susceptibility maps: they show where terrain and land cover make flooding more likely, not where water will reach in a particular storm. The weights were set by judgement, and no test was made of how sensitive the zones are to them. The Chimanimani map was not compared with a mapped flood extent such as that of Cyclone Idai, and the Gweru results were only compared with known flood sites, which is a check of consistency rather than a measure of accuracy. OpenStreetMap may also miss some buildings, especially in rural wards.</p>

        <h2>Recommendations</h2>
        <p>Chimanimani District should use the susceptibility map to prioritise early warning, evacuation planning and flood works in the western wards (2, 3, 4, 5, 8 and 20) and around business centres such as Murare, Chakowa, Hotsprings, Nenohwe and Kopa.</p>
        <p>New settlement and building permits in both areas should be checked against the high and very high zones, and in Gweru development on former wetlands along the Gweru River should be stopped, as Matsa and Mupepi (2022) also recommend.</p>
        <p>Further work should check both maps against mapped flood extents, such as Sentinel-1 flood maps of Cyclone Idai and of the 2020/21 floods, and test how the zones change when the weights are varied.</p>

        <h2>Conclusion</h2>
        <p>The study met its three objectives. First, slope, distance to river, wetness, drainage density, vegetation and flow length all point to the low western part of Chimanimani District as the most flood prone, and the steep east as the least. Second, 24.2% of the district was rated high or very high susceptibility, and 44.5% of its 59 617 buildings stand in these zones, mostly in the western belt from Birchenough Bridge north-west. Third, 45.1% of Gweru Urban was rated high or very high susceptibility, mainly along the Gweru River and in suburbs that have flooded before. In both places the maps show where flood planning should begin.</p>

        <h2>References</h2>
        <div className="cs__ref">
          <p>ESA (2021) ESA WorldCover 10 m 2021. European Space Agency. <A href="https://esa-worldcover.org" /></p>
          <p>Matsa, M. and Mupepi, O. (2022) Flood risk and damage analysis in urban areas of Zimbabwe: a case of 2020/21 rain season floods in the city of Gweru. International Journal of Disaster Risk Reduction, 67. <A href="https://cris.library.msu.ac.zw/handle/11408/4796" /></p>
          <p>Matsvange, D. et al. (2020) Disaster risk reduction systems in the context of Cyclone Idai in Chimanimani. In Manatsa, D., Chatiza, K., Mushore, T.D. and Mudavanhu, C. (eds) Building resilience to natural disasters in populated African mountain ecosystems. Harare: Tsuro Trust.</p>
          <p>Munsaka, E. et al. (2021) When disaster risk management systems fail: the case of Cyclone Idai in Chimanimani District, Zimbabwe. International Journal of Disaster Risk Science, 12, 689–699. <A href="https://doi.org/10.1007/s13753-021-00370-6" /></p>
          <p>Nehanda Radio (2021) Massive flooding hits Gweru areas. 12 January 2021. <A href="https://nehandaradio.com/2021/01/12/massive-flooding-hits-gweru-areas/" /></p>
          <p>OpenStreetMap contributors (2024) Building footprints, Chimanimani District. <A href="https://www.openstreetmap.org" /></p>
        </div>
      </article>
      <SiteFooter />
    </>
  );
}
