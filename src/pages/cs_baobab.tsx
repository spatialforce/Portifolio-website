import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { CASESTUDIES } from "./catalogue";
import "./casestudy_toc.css";
import map1 from "../assets/casestudies/baobab-habitat-suitability/map1_study_area.webp";
import map2 from "../assets/casestudies/baobab-habitat-suitability/map2_records.webp";
import map3 from "../assets/casestudies/baobab-habitat-suitability/map3_climate.webp";
import map4 from "../assets/casestudies/baobab-habitat-suitability/map4_suitability.webp";
import map5 from "../assets/casestudies/baobab-habitat-suitability/map5_protected.webp";
import fig1 from "../assets/casestudies/baobab-habitat-suitability/fig1_importance.webp";
import fig2 from "../assets/casestudies/baobab-habitat-suitability/fig2_response.webp";

const SLUG = "baobab-habitat-suitability";

// contents list: id, label, sub-heading?
const TOC: [string, string, boolean?][] = [
  ["intro", "1 Introduction"], ["objectives", "2 Objectives"], ["area", "3 Study area"],
  ["methods", "4 Data and methods"], ["m-data", "Data", true], ["m-records", "Baobab records", true], ["m-climate", "Climate factors", true], ["m-model", "Model and testing", true],
  ["results", "5 Results"], ["r-map", "Where baobabs can grow", true], ["r-factors", "What controls it", true], ["r-prov", "Provinces", true], ["r-pa", "Protected areas", true],
  ["discussion", "6 Discussion"], ["limits", "7 Limitations"], ["conclusion", "8 Conclusion and recommendations"], ["refs", "References"],
];

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

function Table({ cap, head, rows, num, total, src }: { cap: string; head: string[]; rows: string[][]; num: number; total?: boolean; src?: string }) {
  return (
    <>
      <p className="tc__cap">{cap}</p>
      <div className="tc__tw">
        <table>
          <thead><tr>{head.map((h, i) => <th key={h} className={i >= num ? "n" : undefined}>{h}</th>)}</tr></thead>
          <tbody>
            {rows.map((r, k) => (
              <tr key={r.join("|")} className={total && k === rows.length - 1 ? "t" : undefined}>
                {r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {src && <p className="tc__src">{src}</p>}
    </>
  );
}

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

const T1 = [
  ["GBIF occurrence records of Adansonia digitata", "Points", "1886 to 2026", "Places where baobabs were seen"],
  ["CHELSA V2.1 climate (bio11, bio12, bio15)", "30 arc-seconds (about 1 km)", "1981 to 2010", "Climate factors for the model"],
  ["SRTM elevation model", "15 arc-seconds (about 500 m)", "2000", "Study area map and elevation summary"],
  ["World Database on Protected Areas", "Areas", "2026", "National parks, safari areas and other protected land"],
  ["OCHA administrative boundaries", "Areas", "2020", "National and province boundaries"],
  ["Natural Earth lakes and countries", "Areas", "Version 5", "Lakes and neighbouring countries"],
];

const T2 = [
  ["High", "0.6 and above", "73 171", "18.8", "88"],
  ["Moderate", "0.4 to 0.6", "48 686", "12.5", "19"],
  ["Low", "0.2 to 0.4", "140 820", "36.2", "24"],
  ["Not suitable", "below 0.2", "126 783", "32.6", "14"],
  ["Total", "", "389 459", "100.0", "145"],
];

const T3 = [
  ["Below 600 m", "100.0", "80"],
  ["600 to 900 m", "66.2", "29"],
  ["900 to 1 200 m", "6.7", "25"],
  ["1 200 to 1 500 m", "0.4", "9"],
  ["Above 1 500 m", "0.0", "2"],
];

const T4 = [
  ["Masvingo", "56 613", "32 532", "8 205", "40 737", "72.0"],
  ["Mashonaland West", "56 313", "11 535", "10 386", "21 921", "38.9"],
  ["Matabeleland South", "54 270", "9 948", "7 459", "17 407", "32.1"],
  ["Manicaland", "35 946", "6 587", "4 104", "10 691", "29.7"],
  ["Matabeleland North", "74 720", "3 967", "6 124", "10 090", "13.5"],
  ["Midlands", "49 526", "985", "8 557", "9 542", "19.3"],
  ["Mashonaland Central", "28 298", "7 022", "1 999", "9 021", "31.9"],
  ["Mashonaland East", "32 283", "594", "1 854", "2 447", "7.6"],
  ["Harare and Bulawayo", "1 489", "0", "0", "0", "0.0"],
  ["Zimbabwe", "389 459", "73 171", "48 686", "121 857", "31.3"],
];

const T5 = [
  ["Safari areas", "16", "18 969", "10 655", "56.2"],
  ["National parks", "11", "26 956", "8 713", "32.3"],
  ["Sanctuaries", "10", "6 251", "5 316", "85.0"],
  ["State forests", "32", "8 629", "773", "9.0"],
  ["Recreation parks", "14", "1 391", "765", "55.0"],
  ["Botanical reserves", "10", "481", "142", "29.5"],
  ["All protected areas", "93", "62 594", "26 309", "42.0"],
];

const T6 = [
  ["Gonarezhou", "National park", "4 936", "4 936"],
  ["Save Conservancy", "Sanctuary", "3 498", "3 498"],
  ["Chewore", "Safari area", "3 406", "2 208"],
  ["Hurungwe", "Safari area", "2 885", "2 158"],
  ["Mana Pools", "National park", "2 124", "1 739"],
  ["Charara", "Safari area", "1 724", "1 306"],
  ["Sapi", "Safari area", "1 195", "1 187"],
  ["Matusadona", "National park", "1 426", "1 121"],
];

function useActive(ids: string[]) {
  const [on, setOn] = useState(ids[0]);
  useEffect(() => {
    const els = ids.map((i) => document.getElementById(i)).filter(Boolean) as HTMLElement[];
    const pick = () => {
      let cur = ids[0];
      for (const el of els) if (el.getBoundingClientRect().top < 140) cur = el.id;
      setOn(cur);
    };
    pick();
    window.addEventListener("scroll", pick, { passive: true });
    return () => window.removeEventListener("scroll", pick);
  }, [ids]);
  return on;
}

const IDS = TOC.map((t) => t[0]);

export default function BaobabCaseStudy() {
  const on = useActive(IDS);
  const go = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    history.replaceState(null, "", `#${id}`);
  };
  const others = CASESTUDIES.filter((c) => c.slug !== SLUG);

  return (
    <>
      <SiteNav />
      <div className="tc">
        <nav className="tc__toc" aria-label="Contents">
          <p>Contents</p>
          <ol>
            {TOC.map(([id, label, sub]) => (
              <li key={id} className={sub ? "s" : undefined}>
                <a href={`#${id}`} className={on === id ? "on" : undefined} onClick={(e) => go(e, id)}>{label}</a>
              </li>
            ))}
          </ol>
        </nav>

        <main className="tc__main">
          <h1>Habitat Suitability Modelling for the African Baobab (Adansonia digitata) in Zimbabwe Using Maximum Entropy (MaxEnt)</h1>
          <p className="tc__by">A national map of where the climate suits the baobab, and how much of that land lies in protected areas.</p>
          <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (13 November 2026)</p>
          <dl className="tc__facts">
            <dt>Place</dt><dd>Zimbabwe, 389 459 km² of land</dd>
            <dt>Species</dt><dd>African baobab, Adansonia digitata L.</dd>
            <dt>Records</dt><dd>145 GBIF records, after cleaning 535</dd>
            <dt>Climate</dt><dd>CHELSA V2.1, 1981 to 2010</dd>
            <dt>Methods</dt><dd>Species distribution modelling, maximum entropy (MaxEnt)</dd>
            <dt>Tools</dt><dd>Python (elapid, rasterio, geopandas), Google Earth Engine</dd>
          </dl>

          <section>
            <h2 id="intro">1 Introduction</h2>
            <p>The African baobab is one of the best known trees of the dry savanna. It can live for well over a thousand years and stores water in its trunk and rural households eat, sell and use its fruit, leaves and bark. In Zimbabwe the fruit pulp is now traded for export. That adds value to the tree, but it also adds pressure. Baobabs grow very slowly and their young are often eaten by livestock and wildlife, so knowing where the climate allows them to grow helps to plan both harvesting and protection.</p>
            <p>Species distribution models link the places where a species has been recorded to the conditions at those places and then map where similar conditions occur. Maximum entropy, or MaxEnt, is widely used for this when only presence records are available, as is the case for most plants (Phillips et al., 2006). It has been used for the baobab across Africa (Sanchez et al. 2011) and in Zimbabwe (Moyo et al., 2019), where winter temperature and altitude were found to limit the tree.</p>
            <p>Here a simple MaxEnt model was built for the whole of Zimbabwe from public records and climate data for one period, 1981 to 2010. The model was used to map where the climate is suitable, to find what limits the tree and to measure how much of the suitable land lies inside the country's protected areas.</p>
          </section>

          <section>
            <h2 id="objectives">2 Objectives</h2>
            <ol className="tc__list">
              <li>To model the climatic habitat suitability of the African baobab across Zimbabwe with MaxEnt.</li>
              <li>To identify the climate factors that most limit where the baobab can grow.</li>
              <li>To quantify the area of suitable habitat in each province.</li>
              <li>To evaluate how much suitable habitat lies inside protected areas.</li>
            </ol>
          </section>

          <section>
            <h2 id="area">3 Study area</h2>
            <p>Zimbabwe is a landlocked country in southern Africa between about 25°E and 33°E and 15.6°S and 22.4°S (Map 1). A central plateau above 1 200 m runs from south-west to north-east, with the Eastern Highlands rising above 2 500 m on the border with Mozambique. The land falls to below 500 m in the Zambezi Valley in the north and in the Save and Limpopo lowlands of the south-east.</p>
            <p>Rain falls mainly from November to March and decreases from over 1 000 mm a year in the east to under 450 mm in the south and west. Winters are dry and cool on the plateau, with frost in places, but stay warm in the low valleys. Most of the land outside the plateau is savanna woodland of mopane, miombo and mixed trees, where baobabs are a common sight.</p>
            <Fig src={map1} cap="Map 1. Zimbabwe: elevation, provinces and main towns." />
          </section>

          <section>
            <h2 id="methods">4 Data and methods</h2>
            <h3 id="m-data">Data</h3>
            <p>All data are open (Table 1). The model uses climate only, so that the map shows where the climate suits the tree, not where it happens to have been recorded or where land use allows it.</p>
            <Table cap="Table 1. Data used" head={["Dataset", "Resolution", "Period", "Use"]} rows={T1} num={9} />

            <h3 id="m-records">Baobab records</h3>
            <p>All 535 GBIF records of Adansonia digitata in Zimbabwe with coordinates were downloaded, 513 of them field observations and 22 herbarium specimens. Removing records with coordinate errors or an uncertainty above 5 km left 461 and removing duplicates and points off land left 410. The records cluster along roads and around parks, which would push the model towards well-visited places, so only one record was kept in each 10 km block. That left 145 records for the model (Map 2).</p>
            <Fig src={map2} cap="Map 2. Baobab records. Filled dots are the 145 records used in the model; hollow dots are records removed as near duplicates or as imprecise." />

            <h3 id="m-climate">Climate factors</h3>
            <p>Nine climate layers from CHELSA (Karger et al. 2017) were compared first. Many of them are closely related, which makes a model hard to read. Three were kept, each describing a different part of the climate and only weakly related to the others (correlation 0.43 or less):</p>
            <ol className="tc__list">
              <li>Winter temperature: the mean temperature of the coldest three months (bio11).</li>
              <li>Annual rainfall (bio12).</li>
              <li>Rainfall seasonality: how unevenly rain falls through the year (bio15).</li>
            </ol>
            <p>Elevation was not used as a factor because it is closely tied to winter temperature (correlation −0.85). It is used only to describe the results. The three factors are shown in Map 3.</p>
            <Fig src={map3} cap="Map 3. The three climate factors used in the model: (a) winter temperature, (b) annual rainfall and (c) rainfall seasonality." />

            <h3 id="m-model">Model and testing</h3>
            <p>MaxEnt compares the climate at the 145 records with the climate at 10 000 random points across the country. The model was fitted with the elapid package in Python (Anderson, 2023), using simple linear and quadratic responses and a regularisation multiplier of 1.5 to keep the curves smooth. The output is a suitability score from 0 to 1 for every 1 km cell.</p>
            <p>The model was tested by dividing the country into 50 km blocks in a checkerboard pattern, training on one set of blocks and testing on the other. Accuracy is given as the area under the curve (AUC), where 0.5 is no better than chance and 1 is perfect. The importance of each factor was measured by how much the AUC drops when that factor is shuffled. Scores were grouped into four classes: not suitable (below 0.2), low (0.2 to 0.4), moderate (0.4 to 0.6) and high (0.6 and above). Moderate and high together are called suitable habitat. Areas were measured on the exact area of each grid cell.</p>
          </section>

          <section>
            <h2 id="results">5 Results</h2>
            <h3 id="r-map">Where baobabs can grow</h3>
            <p>The model separated record points from random points well, with a checkerboard test AUC of 0.765 (0.736 and 0.794 for the two halves). Suitable habitat covers 121 857 km², or 31.3 % of the land (Table 2, Map 4). Most of it lies in two large areas. One is the south-east lowlands of the Save, Runde and Limpopo rivers and the other is the Zambezi Valley and the slopes above Lake Kariba in the north. Smaller patches follow the Gwayi and Shangani valleys in the north-west and the Mozambique border in Manicaland. The central plateau and the Eastern Highlands are not suitable.</p>
            <p>Of the 145 records, 107 (73.8 %) fall in moderate or high suitability and 88 in the high class alone.</p>
            <Fig src={map4} cap="Map 4. Habitat suitability for the African baobab in four classes. Dark green shows the land where the climate suits the tree best." />
            <Table cap="Table 2. Area in each suitability class" head={["Class", "Score", "Area (km²)", "Share of land (%)", "Records"]} rows={T2} num={2} total />

            <h3 id="r-factors">What controls it</h3>
            <p>Winter temperature is by far the most important factor, with 73.2 % of the model's importance (Figure 1). Rainfall seasonality adds 22.2 % and annual rainfall only 4.6 %. Suitability climbs steeply as winters get warmer (Figure 2). Where the coldest months average under about 16.3 °C it is below 0.2 and it reaches the high class at about 18.6 °C. Half of the records lie where the coldest months average 18.6 °C or more, while the figure for the country as a whole is 17.1 °C. Suitability drops as rainfall becomes more seasonal.</p>
            <Fig src={fig1} cap="Figure 1. Share of the model's importance for each climate factor." />
            <Fig src={fig2} cap="Figure 2. How habitat suitability changes with winter temperature, with the other two factors held at typical values. The dashed line is the median at the records." />
            <p>Because winter temperature falls with height, suitability follows elevation closely (Table 3). All land below 600 m is suitable, two thirds of land between 600 and 900 m and almost none above 1 200 m. Half of the records lie below 558 m.</p>
            <Table cap="Table 3. Suitable habitat by elevation" head={["Elevation", "Land suitable (%)", "Records"]} rows={T3} num={1} />

            <h3 id="r-prov">Provinces</h3>
            <p>Masvingo has the most suitable habitat, 40 737 km² or 72.0 % of its land and holds 44.5 % of all high suitability land in the country (Table 4). Mashonaland West (21 921 km²) and Matabeleland South (17 407 km²) follow. Matabeleland North is the largest province but only 13.5 % of it is suitable, mostly in the valleys. Mashonaland East, on the plateau, has the least (7.6 %) and Harare and Bulawayo have none.</p>
            <Table cap="Table 4. Suitable habitat by province (km²), largest first" head={["Province", "Land", "High", "Moderate", "Suitable", "Share suitable (%)"]} rows={T4} num={1} total />

            <h3 id="r-pa">Protected areas</h3>
            <p>The 93 protected areas studied cover 62 594 km², 16.1 % of the land. Inside them are 26 309 km² of suitable habitat, which is 21.6 % of all suitable habitat in the country and 26.9 % of the high class (Map 5). Nearly four fifths of the land where baobabs can grow is therefore outside protected areas, mostly on communal land in Masvingo, Matabeleland South and the Zambezi Valley.</p>
            <p>Safari areas hold the most suitable habitat, 10 655 km² (Table 5), followed by national parks (8 713 km²) and sanctuaries (5 316 km²). Gonarezhou National Park and the Save Conservancy are entirely suitable and together they hold almost a third of the suitable land inside protected areas (Table 6). State forests, mostly on the higher ground of the west, are only 9.0 % suitable.</p>
            <Fig src={map5} cap="Map 5. Suitable habitat inside (dark green) and outside (orange) protected areas. NP is national park and SA is safari area." />
            <Table cap="Table 5. Suitable habitat by type of protected area" head={["Type", "Number", "Area (km²)", "Suitable (km²)", "Share suitable (%)"]} rows={T5} num={1} total />
            <Table cap="Table 6. Protected areas with the most suitable habitat" head={["Protected area", "Type", "Area (km²)", "Suitable (km²)"]} rows={T6} num={2} />
          </section>

          <section>
            <h2 id="discussion">6 Discussion</h2>
            <p>On this map the baobab is a tree of Zimbabwe's warm lowlands. Winter temperature alone explains most of the pattern. Moyo et al. (2019) likewise found the temperature of the coldest quarter and altitude to be key for the baobab in Zimbabwe and Sanchez et al. (2011) found cold to limit the tree across Africa. Young baobabs are easily damaged by frost and frost is common on the plateau in June and July. That is probably why so few trees grow above about 1 200 m.</p>
            <p>Rainfall matters much less. The baobab grows from about 430 to almost 1 000 mm a year in Zimbabwe and its water-storing trunk lets it survive long dry seasons. The small negative effect of seasonality probably reflects the hot, very seasonal far south-west near Botswana, where few baobabs were recorded.</p>
            <p>The low share of suitable habitat inside protected areas matters for the fruit trade. Most harvesting takes place on communal land, where goats and cattle browse the young trees. The future of the baobab outside the parks will be decided on the large areas of suitable land in Masvingo and Matabeleland South.</p>
          </section>

          <section>
            <h2 id="limits">7 Limitations</h2>
            <p>The model shows where the climate suits the baobab, not where it actually grows. Soil, fire, browsing, clearing and harvesting are left out. GBIF records are uneven, with more of them along roads and in parks, even after thinning. When whole regions were held out in turn the AUC was lower (mean 0.652, ranging from 0.517 to 0.863), so the model is less reliable where records are few, such as the far west. The climate data cover 1981 to 2010 and change over time was not modelled.</p>
          </section>

          <section>
            <h2 id="conclusion">8 Conclusion and recommendations</h2>
            <p>About a third of Zimbabwe, 121 857 km², has a climate that suits the African baobab, mainly in the warm south-east lowlands and the Zambezi Valley. Winter temperature is the main control and above 1 200 m there is almost no suitable land. Only 21.6 % of the suitable land lies in protected areas.</p>
            <ol className="tc__list">
              <li>Focus baobab monitoring and harvesting rules on the communal lands of Masvingo, Matabeleland South and the Zambezi Valley, where most suitable habitat lies.</li>
              <li>Protect young trees from browsing in these areas, for example with community nurseries and fenced seedlings.</li>
              <li>Use Gonarezhou, the Save Conservancy and the Zambezi Valley parks as reference sites for counting and ageing trees.</li>
              <li>Test the map with field counts in the far west, where records are few.</li>
            </ol>
          </section>

          <section className="tc__ref">
            <h2 id="refs">References</h2>
            <p>Anderson, C.B. (2023) elapid: species distribution modeling tools for Python. Journal of Open Source Software, 8(84), 4930. <A href="https://doi.org/10.21105/joss.04930" /></p>
            <p>GBIF.org (2026) Occurrence search: Adansonia digitata L. in Zimbabwe. Global Biodiversity Information Facility. <A href="https://www.gbif.org/species/5406695" /></p>
            <p>Karger, D.N., Conrad, O., Böhner, J., Kawohl, T. et al. (2017) Climatologies at high resolution for the earth's land surface areas. Scientific Data, 4, 170122. <A href="https://doi.org/10.1038/sdata.2017.122" /></p>
            <p>Moyo, S., Gwitira, I., Murwira, A., Zengeya, F.M. and Shekede, M.D. (2019) Spatial distribution and abundance of the African baobab (Adansonia digitata) in Zimbabwe. Transactions of the Royal Society of South Africa, 74(3), 213-218. <A href="https://doi.org/10.1080/0035919X.2019.1650309" /></p>
            <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
            <p>Phillips, S.J., Anderson, R.P. and Schapire, R.E. (2006) Maximum entropy modeling of species geographic distributions. Ecological Modelling, 190, 231-259. <A href="https://doi.org/10.1016/j.ecolmodel.2005.03.026" /></p>
            <p>Sanchez, A.C., Osborne, P.E. and Haq, N. (2011) Climate change and the African baobab (Adansonia digitata L.): the need for better conservation strategies. African Journal of Ecology, 49, 234-245. <A href="https://doi.org/10.1111/j.1365-2028.2011.01257.x" /></p>
            <p>UNEP-WCMC and IUCN (2026) Protected Planet: The World Database on Protected Areas (WDPA). Cambridge, UK. <A href="https://www.protectedplanet.net" /></p>
          </section>
        </main>

        <aside className="tc__more" aria-label="Other case studies">
          <p>Other case studies</p>
          <ul>
            {others.map((c) => (
              <li key={c.slug}><Link to={`/case-studies/${c.slug}`}>{c.card ?? c.title}</Link></li>
            ))}
          </ul>
        </aside>
      </div>
      <SiteFooter />
    </>
  );
}
