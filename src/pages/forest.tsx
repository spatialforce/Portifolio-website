import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/gazetted-forests/map1_study_area.webp";
import fig1 from "../assets/casestudies/gazetted-forests/fig1_share.webp";
import fig2 from "../assets/casestudies/gazetted-forests/fig2_lost.webp";
import Gwaai from "../assets/gwaai.webp";
import Bembesi from "../assets/Mbembesi.webp";
import Kavira from "../assets/kavira.webp";
import LakeAlice from "../assets/lake_alice.webp";
import Gwampa from "../assets/gwampa.webp";
import InsezeExt from "../assets/inseze_extension.webp";
import Chesa from "../assets/chesa.webp";

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

// Areas from the legends of the 2024 Forestry Commission maps (forest + cultivation + other = gazetted area).
// forest, gazetted ha, forest or woodland ha, cultivation ha, other cleared ha, land lost ha, lost %
const T1: string[][] = [
  ["Gwaai", "144 265", "127 880.1", "16 061.6", "322.8", "16 384.4", "11.4"],
  ["Bembesi", "55 100", "47 506.0", "7 539.1", "", "7 539.1", "13.7"],
  ["Lake Alice", "39 000", "34 765.4", "4 235.6", "", "4 235.6", "10.9"],
  ["Gwampa", "47 000", "43 579.8", "3 420.2", "", "3 420.2", "7.3"],
  ["Chesa", "14 250", "12 915.0", "1 199.8", "", "1 199.8", "8.4"],
  ["Inseze Extension", "8 400", "7 885.1", "514.9", "", "514.9", "6.1"],
  ["Kavira", "28 200", "28 013.4", "186.6", "", "186.6", "0.7"],
];

// forest, where cultivation lies, features beside it
const T2: string[][] = [
  ["Gwaai", "A wide band across the north-east of the forest and strips along the north-west, west and south edges", "Main road, river valley, dams"],
  ["Bembesi", "A belt across the centre and east between the road and the river", "Main road, river"],
  ["Lake Alice", "Along the whole northern boundary and in the southern arm", "Forest edge, dam"],
  ["Gwampa", "The south-east corner of the forest", "Roads entering the forest"],
  ["Chesa", "The north-east corner and the south corner", "Main road, forest edge"],
  ["Inseze Extension", "The southern tip only", "River on the boundary"],
  ["Kavira", "Small fields in the south-west corner", "Road on the boundary"],
];

export default function ForestResourcesProject() {
  return (
    <>
      <CaseLayout slug="zimbabwe-gazetted-forests">
        <h1>Mapping Encroachment and Land Loss in Seven Gazetted Forests of Matabeleland North, Zimbabwe (2024)</h1>
        <p className="tc__by">Clearing for cultivation in seven gazetted forests.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (2 December 2024)</p>
        <Facts rows={[["Place", "Matabeleland North, seven gazetted forests, 336 215 ha"], ["Period", "March to November 2024"], ["Data", "Forestry Commission forest maps, 1:50 000 topographic maps, satellite imagery"], ["Methods", "Digitising, land cover mapping, area calculation, overlay analysis"], ["Tools", "QGIS"]]} />

        <h2>1 Introduction</h2>
        <p>Gazetted forests are state forests declared under the Forest Act (Chapter 19:05) and managed by the Forestry Commission of Zimbabwe. Most of them lie on the Kalahari sands of Matabeleland North, where they protect indigenous woodland, soils, water catchments and wildlife, and supply timber, grazing and other forest products to nearby communities.</p>
        <p>Many of these forests are under pressure from settlement, cultivation and infrastructure, and their boundaries are not always clear on the ground. Accurate maps are needed to show what land belongs to each forest, how much of it is still forest and where it is being cleared. This study maps seven gazetted forests and the land lost inside them in 2024, as part of the mapping and inventory work of the Forestry Commission with Chesa Research Station.</p>

        <h2>2 Objectives</h2>
        <p>The aim of the study is to map the extent and pattern of encroachment in gazetted forests of Matabeleland North. The specific objectives are:</p>
        <ol>
          <li>To map forest cover and encroachment within the gazetted boundaries of seven forests.</li>
          <li>To quantify and compare the land lost in each forest.</li>
          <li>To analyse the spatial pattern of encroachment in relation to forest edges, roads and rivers.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>The seven forests lie in Matabeleland North, between Bulawayo in the south and Lake Kariba in the north (Map 1). Six of them form a group in the south-east of the province, across Lupane, Nkayi, Bubi and Umguza districts. Gwaai is the largest at 144 265 ha and lies along the Bulawayo to Victoria Falls road, with Bembesi beside it to the south-east. Lake Alice and Gwampa lie in Nkayi district, and Inseze Extension and Chesa lie in Umguza district, north-west of Bulawayo. Chesa also holds the offices of Chesa Research Station. Kavira lies apart from the others in Binga district, near Lake Kariba. Together the seven forests cover 336 215 ha.</p>
        <Fig src={map1} cap="Map 1. Study Area Map of the Seven Gazetted Forests in Matabeleland North (2024)." />

        <h2>4 Data and methods</h2>
        <p>Each forest was mapped in QGIS by the Forestry Commission Mapping and Inventory Unit between March and November 2024. The gazetted boundary of each forest was taken from its legal description and the 1:50 000 Topographic Series of the Surveyor-General. The steps used for each objective are described below.</p>
        <h3>Forest cover and encroachment</h3>
        <p>Inside each boundary the land was mapped as forest or woodland, cultivation, vlei, dams, plantation or powerline, from satellite imagery and field checks. Roads, rivers, firelines, block boundaries, offices and camps were added for reference, and a map was produced for each forest.</p>
        <h3>Land lost in each forest</h3>
        <p>The area of each class was calculated in hectares. Land lost was taken as the area under cultivation, together with the powerline clearing in Gwaai. The eucalyptus plantation in Chesa was not counted as lost, as it is a forest use. The share lost was calculated as land lost divided by the gazetted area of the forest, and the class areas were checked to make sure they add up to the gazetted area.</p>
        <h3>Spatial pattern of encroachment</h3>
        <p>The position of the cultivated land in each forest was compared with the forest edge, the roads and the rivers shown on the maps, and the forests were then compared with each other.</p>

        <h2>5 Results</h2>
        <h3>Forest cover and encroachment</h3>
        <p>Gwaai has the largest area of cultivation of the seven forests (Map 2). Most of it lies in a wide band across the north-east, where the main road and a river valley cross the forest near Forest Hill. Narrower strips of fields follow the north-western, western and southern edges. A powerline clears a straight strip of 322.8 ha across the south-western block, and the railway passes through Gwaai Station in the south. The interior blocks between the firelines are still forest, with vleis along the drainage lines. More land is being cleared for the Gwaai-Shangani pipeline.</p>
        <Fig src={Gwaai} cap="Map 2. Gwaai Forest Reserve Land Cover Map (2024)." />
        <p>In Bembesi the fields form a belt across the centre and east of the forest, between the main road and the river on its northern side (Map 3). The cultivation follows the river closely and spreads south towards the road, leaving only scattered patches of woodland. The western arm and the southern block, away from the river, are still almost all woodland.</p>
        <Fig src={Bembesi} cap="Map 3. Bembesi Forest Reserve Land Cover Map (2024)." />
        <p>The two Nkayi forests show different patterns (Map 4 and Map 5). In Lake Alice the fields run along almost the whole length of the northern boundary and into the narrow southern arm, while the core of the forest is intact. In Gwampa the fields are all in the south-east corner, around the roads that enter the forest there, and the western two-thirds of the forest, where the offices are, has no cultivation.</p>
        <div className="tc__row tc__row--2">
          <Fig src={LakeAlice} cap="Map 4. Lake Alice Forest Reserve Land Cover Map (2024)." />
          <Fig src={Gwampa} cap="Map 5. Gwampa Forest Reserve Land Cover Map (2024)." />
        </div>
        <p>In the two Umguza forests the fields are also at the edges (Map 6 and Map 7). In Inseze Extension all the cultivation lies in the southern tip, along the river that forms the boundary. In Chesa there are two cleared areas, one in the north-east corner beside the main road and a larger one in the south corner. The 135.2 ha of plantation lies along the eastern road near the Chesa offices.</p>
        <div className="tc__row tc__row--2">
          <Fig src={InsezeExt} cap="Map 6. Inseze Extension Forest Reserve Land Cover Map (2024)." />
          <Fig src={Chesa} cap="Map 7. Chesa Forest Reserve Land Cover Map (2024)." />
        </div>
        <p>Kavira is the least affected forest (Map 8). Only a few small fields lie in the south-west corner, next to the road on its southern boundary. Roads, paths, camps and a lodge are found across the forest, but these have not led to clearing.</p>
        <Fig src={Kavira} cap="Map 8. Kavira Forest Reserve Land Cover Map (2024)." />

        <h3>Land lost in each forest</h3>
        <p>A total of 33 480.6 ha, or 10.0% of the seven forests, has been lost (Table 1). Cultivation accounts for 33 157.8 ha (99.0%) of this, and the Gwaai powerline for the rest. Gwaai has lost the most land (16 384.4 ha), which is 48.9% of all the land lost, and Bembesi the next most (7 539.1 ha). Together these two forests account for 71.4% of the loss.</p>
        <p className="tc__cap">Table 1. Land cover and land lost in seven gazetted forests (2024)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Forest</th><th className="n">Gazetted area (ha)</th><th className="n">Forest or woodland (ha)</th><th className="n">Cultivation (ha)</th><th className="n">Powerline (ha)</th><th className="n">Land lost (ha)</th><th className="n">Lost (%)</th></tr></thead>
            <tbody>
              <Rows rows={T1} num={1} />
              <tr className="t"><td>Total</td><td className="n">336 215</td><td className="n">302 544.8</td><td className="n">33 157.8</td><td className="n">322.8</td><td className="n">33 480.6</td><td className="n">10.0</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: Forestry Commission of Zimbabwe (2024). Chesa also has 135.2 ha of plantation, and Bembesi has 54.9 ha not given a class on its map.</p>
        <p>As a share of each forest, Bembesi has lost the most (13.7%), followed by Gwaai (11.4%) and Lake Alice (10.9%) (Figure 1). Chesa (8.4%), Gwampa (7.3%) and Inseze Extension (6.1%) fall in the middle, and Kavira has lost only 0.7%. The ranking by share is not the same as the ranking by area (Figure 2). Lake Alice and Chesa have lost a larger share than Gwampa, although Gwampa is a larger forest.</p>
        <Fig src={fig1} cap="Figure 1. Share of each forest under forest or woodland, cultivation and other land (2024)." />
        <Fig src={fig2} cap="Figure 2. Land lost in each forest (2024)." />

        <h3>Spatial pattern of encroachment</h3>
        <p>In every forest the cultivated land lies at the edge of the forest or along a road or river, and not in the interior (Table 2). In four forests (Gwaai, Bembesi, Inseze Extension and Kavira) the fields follow a river or a road on or near the boundary. In Lake Alice they follow the northern boundary itself, and in Gwampa and Chesa they spread in from the roads and corners. The two forests with the highest share lost, Bembesi and Gwaai, are also the two where a main road and a river run through the forest close together.</p>
        <p className="tc__cap">Table 2. Location of cultivated land in each forest (2024)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Forest</th><th>Where the cultivation lies</th><th>Features beside it</th></tr></thead>
            <tbody><Rows rows={T2} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: own analysis of Map 2 to Map 8.</p>

        <h2>6 Discussion</h2>
        <p>The results show that a tenth of the land in the seven forests had been cleared by 2024, almost all of it for cultivation. The clearing is not spread evenly. It is heaviest in the large forests next to Bulawayo, Lupane and Nkayi, and it starts at the edges and along roads and rivers before moving inwards. Roads make it easy for people to reach the forest and take produce out, and river valleys are likely to offer water and better soils for farming. Where a road and a river run together, as in Gwaai and Bembesi, the two pull the fields deep into the forest. The forest interiors, far from roads and rivers, are still largely intact.</p>
        <p>Kavira stands apart, with less than 1% lost although it has roads, camps and a lodge. It is the only forest far from the farming districts around Bulawayo, which suggests that distance from settlement does more to protect a forest than the absence of roads. Infrastructure is a second and growing cause of loss, as the powerline and the Gwaai-Shangani pipeline through Gwaai show.</p>
        <p>The study has some limits. The maps show the forests at one time in 2024, so they do not show how fast the clearing is happening. Bembesi was mapped in March and the others in November, and on the Bembesi map 54.9 ha of the gazetted area is not given a class. The maps do not show whether the cultivation is new or old, or who is farming it. Satellite imagery from earlier years would allow the rate of loss to be measured.</p>

        <h2>7 Recommendations</h2>
        <p>The Forestry Commission should give first attention to Bembesi and Gwaai, which have lost the largest share and the largest area, and in particular to the land between the main roads and the rivers in these two forests.</p>
        <p>The gazetted boundaries along the northern edge of Lake Alice, the south-east of Gwampa and the south of Chesa and Inseze Extension should be marked on the ground and patrolled, as this is where clearing has started.</p>
        <p>New infrastructure, such as the Gwaai-Shangani pipeline, should follow routes that clear as little forest as possible. The 2024 maps should be used as a baseline for regular monitoring with satellite imagery, so that new clearing can be found and acted on early.</p>

        <h2>8 Conclusion</h2>
        <p>The study met its three objectives. First, forest cover and encroachment were mapped inside the gazetted boundaries of seven forests covering 336 215 ha. Second, 33 480.6 ha (10.0%) of this land has been lost, almost all to cultivation, with the largest area in Gwaai (16 384.4 ha) and the largest share in Bembesi (13.7%), while Kavira has lost less than 1%. Third, the clearing lies at the forest edges and along roads and rivers in every forest, and is heaviest where a road and a river run through the forest together. The maps give the Forestry Commission a clear baseline for protecting these forests.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Forestry Commission of Zimbabwe (2024) Gazetted forest maps of Matabeleland North: Gwaai, Bembesi, Lake Alice, Gwampa, Inseze Extension, Chesa and Kavira. Mapping and Inventory Unit, Chesa Research Station.</p>
          <p>Government of Zimbabwe. Forest Act (Chapter 19:05). Harare: Government Printer.</p>
          <p>Natural Earth. Admin 0 countries and lakes, 1:10 m. <a href="https://www.naturalearthdata.com" target="_blank" rel="noopener noreferrer">https://www.naturalearthdata.com</a></p>
          <p>OCHA (2023) Zimbabwe subnational administrative boundaries (COD-AB). <a href="https://data.humdata.org/dataset/cod-ab-zwe" target="_blank" rel="noopener noreferrer">https://data.humdata.org/dataset/cod-ab-zwe</a></p>
          <p>Surveyor-General of Zimbabwe. 1:50 000 Topographic Map Series. Harare: Department of the Surveyor-General.</p>
        </div>
      </CaseLayout>
    </>
  );
}
