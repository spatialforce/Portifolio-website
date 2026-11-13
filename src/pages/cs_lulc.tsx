import CaseLayout, { Facts } from "./CaseLayout";
import byo1987 from "../assets/LULC_1987.webp";
import byo2000 from "../assets/LULC_2000.webp";
import byo2013 from "../assets/LULC_2013.webp";
import byo2025 from "../assets/LULC_2025.webp";
import cowdray from "../assets/cowdray_park.webp";
import mahatshula from "../assets/Mahatshula.webp";
import richmond from "../assets/richmond.webp";
import mut1995 from "../assets/Mutare_LULC_1995.webp";
import mut2005 from "../assets/Mutare_LULC_2005.webp";
import mut2015 from "../assets/Mutare_LULC_2015.webp";
import mut2025 from "../assets/Mutare_LULC_2025.webp";

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

// Table 1: Bulawayo class areas (ha) 1987, 2000, 2013, 2025 and change 1987 to 2025
const T1: string[][] = [
  ["Woodland", "20 068.2", "13 958.4", "13 734.9", "12 484.9", "−7 583.3"],
  ["Grassland", "12 638.9", "19 996.7", "16 623.8", "14 633.0", "+1 994.1"],
  ["Cultivation", "6 031.9", "7 586.0", "11 021.9", "13 708.9", "+7 677.0"],
  ["Built up", "7 850.5", "8 249.5", "8 277.2", "8 535.0", "+684.6"],
  ["Dense vegetation", "6 020.6", "4 537.8", "4 719.2", "4 984.2", "−1 036.4"],
  ["Bare land", "110.9", "280.0", "217.0", "300.3", "+189.5"],
  ["Water", "210.4", "227.1", "241.4", "189.1", "−21.3"],
  ["Total", "52 931.4", "54 835.4", "54 835.4", "54 835.4", ""],
];

// Table 2: share of Bulawayo in each class (%)
const T2: string[][] = [
  ["Woodland", "37.9", "25.5", "25.0", "22.8"], ["Grassland", "23.9", "36.5", "30.3", "26.7"],
  ["Cultivation", "11.4", "13.8", "20.1", "25.0"], ["Built up", "14.8", "15.0", "15.1", "15.6"],
  ["Dense vegetation", "11.4", "8.3", "8.6", "9.1"], ["Bare land", "0.2", "0.5", "0.4", "0.5"], ["Water", "0.4", "0.4", "0.4", "0.3"],
];

// Table 3: origin of the land cultivated in 2025
const T3: string[][] = [
  ["Cultivated in both years", "7 120.0", "52.3"], ["Grassland", "4 150.0", "30.5"], ["Woodland", "1 500.0", "11.0"],
  ["Dense vegetation", "420.0", "3.1"], ["Bare land", "250.0", "1.8"], ["Built up", "155.0", "1.1"], ["Water", "16.6", "0.1"],
  ["Total", "13 611.6", "100.0"],
];

// Table 4: accuracy
const T4: string[][] = [["Overall accuracy (%)", "86.45", "88.24"], ["Kappa coefficient", "0.83", "0.86"]];

// Table 5: suburbs, ha (share %)
const T5: string[][] = [
  ["Cowdray Park", "Woodland", "388.2 (24.4)", "240.6 (15.1)", "193.2 (12.1)", "−195.1"],
  ["", "Grassland", "978.7 (61.4)", "646.5 (40.6)", "509.7 (32.0)", "−468.9"],
  ["", "Built up", "226.5 (14.2)", "706.3 (44.3)", "890.5 (55.9)", "+664.0"],
  ["Mahatshula", "Woodland", "250.6 (37.3)", "323.4 (48.2)", "220.1 (32.8)", "−30.4"],
  ["", "Grassland", "400.7 (59.7)", "197.7 (29.4)", "131.1 (19.5)", "−269.6"],
  ["", "Built up", "19.9 (3.0)", "150.5 (22.4)", "320.5 (47.7)", "+300.6"],
  ["Richmond", "Woodland", "100.0 (35.4)", "133.8 (47.4)", "88.8 (31.7)", "−11.2"],
  ["", "Grassland", "131.3 (46.5)", "68.2 (24.2)", "76.5 (27.3)", "−54.8"],
  ["", "Built up", "50.9 (18.1)", "80.3 (28.4)", "115.1 (41.0)", "+64.1"],
];

// Table 6: Ward 30 class areas (ha)
const T6: string[][] = [
  ["Woodland", "22 190.6", "21 785.7", "21 177.3", "19 919.5", "−2 271.1"],
  ["Cultivation", "12 812.1", "16 093.3", "16 156.7", "11 724.3", "−1 087.8"],
  ["Grassland", "4 031.1", "1 236.8", "870.5", "3 801.2", "−230.0"],
  ["Mine dumps and bare ground", "112.0", "87.6", "772.0", "3 413.6", "+3 301.6"],
  ["Riparian vegetation", "1 230.6", "1 153.0", "1 235.4", "1 441.6", "+211.1"],
  ["Water", "32.6", "52.6", "197.6", "109.5", "+76.9"],
  ["Total", "40 409.0", "40 409.0", "40 409.5", "40 409.7", ""],
];

// Table 7: Ward 30 shares (%)
const T7: string[][] = [
  ["Woodland", "54.9", "53.9", "52.4", "49.3"], ["Cultivation", "31.7", "39.8", "40.0", "29.0"],
  ["Grassland", "10.0", "3.1", "2.2", "9.4"], ["Mine dumps and bare ground", "0.3", "0.2", "1.9", "8.4"],
  ["Riparian vegetation", "3.0", "2.9", "3.1", "3.6"], ["Water", "0.1", "0.1", "0.5", "0.3"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;
const SRC = "Source: author's Random Forest classification of Landsat imagery in Google Earth Engine; areas tabulated in QGIS.";

export default function LulcCaseStudy() {
  return (
    <>
      <CaseLayout slug="land-use-land-cover">
        <h1>A Spatial Analysis of Land Use and Land Cover Change in Bulawayo and Ward 30 of Mutare Rural District from 1987 to 2025</h1>
        <p className="tc__by">Urban growth, cultivation and diamond mining mapped from Landsat.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (7 November 2025)</p>
        <Facts rows={[["Place", "Bulawayo and Ward 30 of Mutare Rural District"], ["Period", "1987 to 2025"], ["Data", "Landsat 5 and Landsat 8 surface reflectance"], ["Methods", "Supervised classification (Random Forest), post-classification change detection, accuracy assessment"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Land cover in Zimbabwe has changed quickly since the late 1980s, and the causes differ from place to place. In Bulawayo, the country's second city with 665 952 people at the 2022 census (ZIMSTAT, 2022), the pressure comes from residents farming open land for food and from new housing on the edge of the city. Banga (2013) found that in Emakhandeni every available open space had been parcelled out for cultivation, in spite of council by-laws and an urban agriculture policy. On the northern edge of the city, Cowdray Park and Mahatshula have grown from a few houses into large residential suburbs. In the east of the country, Ward 30 of Mutare Rural District holds the Chiadzwa part of the Marange diamond fields, where mining since 2006 has turned farmland and woodland into pits and dumps.</p>
        <p>Here these changes were measured from satellite imagery in three areas: the whole of Bulawayo from 1987 to 2025, three northern suburbs of Bulawayo (Cowdray Park, Mahatshula and Richmond) from 1990 to 2025, and Ward 30 of Mutare Rural District from 1995 to 2025. For each area the extent of each land cover class is reported, along with how it changed and what drove the change, followed by recommendations for planning and land management.</p>

        <h2>2 Study area</h2>
        <p>Bulawayo lies in the south west of Zimbabwe at about 1 350 m above sea level. Its rainfall is low and unreliable, about 525 mm in an average October to April season, with a coefficient of variation near 27% (case study 2). The mapped area is about 548 km². It takes in the city centre and industrial areas, the high density western suburbs, the low density eastern and northern suburbs, and a belt of grassland, woodland and stream valleys on the edge of the city.</p>
        <p>Cowdray Park lies on the north west edge of Bulawayo. Much of it was laid out under the Garikai/Hlalani Kuhle scheme, which the government began in June 2005, a month after Operation Murambatsvina destroyed informal homes across the country, to give stands to people who had lost their homes. About 3 300 of those households were given unserviced stands in Cowdray Park (NewsDay, n.d.). The council took over the scheme in 2012, and in 2025 it estimated that servicing the 15 000 stands of the Hlalani Kuhle development could take 16 years (NewsDay, 2025). Mahatshula lies north of the city along the Harare road, where the council and private partners have serviced several phases of medium density stands in Mahatshula East (The Herald, n.d.). Richmond, about 9 km north of the city centre, is an older low density suburb of large stands, where vacant land is still being subdivided.</p>
        <p>Ward 30 of Mutare Rural District covers about 404 km² in Manicaland Province, between the Odzi and Save rivers. Before mining it was communal land of woodland, grassland and small fields. Alluvial diamonds were found there in June 2006, and tens of thousands of informal miners moved into the fields (Human Rights Watch, 2009). Police cleared the miners in November 2006 and in October 2008 the army took control in Operation Hakudzokwi, during which Human Rights Watch (2009) reported more than 200 deaths. Mining companies were then given concessions, and from 2009 onward more than a thousand families were moved from Chiadzwa to Arda Transau, a former state farm near Odzi (Mongabay, 2022). In 2016 the government expelled the private companies and merged their operations into the state owned Zimbabwe Consolidated Diamond Company (Mongabay, 2022).</p>

        <h2>3 Data and methods</h2>
        <p>The imagery was Landsat Collection 2 Level 2 surface reflectance from the United States Geological Survey (USGS, 2024). Landsat 5 Thematic Mapper scenes covered 1987, 1990, 1995, 2000, 2005 and 2008, and Landsat 8 Operational Land Imager scenes 2013, 2015 and 2025. Only dry season scenes with less than 10% cloud were used, so that green crops and seasonal grass would not be mistaken for woodland.</p>
        <h3>Classification</h3>
        <p>Each scene was classified in Google Earth Engine (Gorelick et al., 2017) with the Random Forest classifier (Breiman, 2001), trained on points digitised over each class from the imagery and from high resolution Google Earth images. Bulawayo was classified into seven classes: water, woodland, grassland, bare land, built up, dense vegetation and cultivation. Ward 30 was classified into six classes: water, grassland, cultivation, riparian vegetation, woodland and mine dumps with bare ground. The three suburbs were classified into three classes: woodland, grassland and built up.</p>
        <h3>Area statistics and change</h3>
        <p>The classified rasters were exported to QGIS, where the area of each class was calculated from pixel counts (each 30 m pixel is 0.09 ha). Change was measured as the difference in area between the first and last years. For Bulawayo a change matrix between 1987 and 2025 was built to show which classes the 2025 cultivated land came from.</p>
        <h3>Accuracy assessment</h3>
        <p>The Bulawayo maps for 2013 and 2025 were checked against independent validation points not used in training. Overall accuracy and the Kappa coefficient were calculated from the confusion matrix. Accuracy was not assessed for the older Bulawayo maps, the suburb maps or the Ward 30 maps, because reliable reference imagery for those years was not available.</p>

        <h2>4 Results</h2>
        <h3>Land use and land cover change in Bulawayo (1987 to 2025)</h3>
        <p>The 1987 map (Map 1) is the baseline against which the later years are compared. In 1987 woodland was the largest class, covering 20 068.2 ha or 37.9% of the city, followed by grassland at 23.9%. Built up land covered 14.8%, and dense vegetation and cultivation 11.4% each. Bare land and water together covered less than 1% (Tables 1 and 2).</p>
        <div className="tc__one"><Fig src={byo1987} cap="Map 1. Land Use Land Cover Map Of Bulawayo (1987), the baseline." /></div>
        <p>Maps 2 to 4 show the city in 2000, 2013 and 2025. By 2025 cultivation had more than doubled, from 6 031.9 ha to 13 708.9 ha, and covered 25.0% of the city. It grew in every period, slowly from 1987 to 2000 and fastest from 2000 to 2013, when it added 3 435.9 ha. Over the same 38 years woodland fell by 7 583.3 ha, or 37.8%, and dense vegetation by 1 036.4 ha. Most of the woodland was lost between 1987 and 2000, when grassland grew from 23.9% to 36.5% of the city. Grassland then shrank in each later period as it was ploughed. Built up land grew only from 14.8% to 15.6%.</p>
        <div className="tc__row">
          <Fig src={byo2000} cap="Map 2. Bulawayo (2000)." />
          <Fig src={byo2013} cap="Map 3. Bulawayo (2013)." />
          <Fig src={byo2025} cap="Map 4. Bulawayo (2025)." />
        </div>
        <p className="tc__cap">Table 1. Area of each land cover class in Bulawayo in ha (1987 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>1987</th><th>2000</th><th>2013</th><th>2025</th><th>Change 1987 to 2025</th></tr></thead>
            <tbody><Rows rows={T1} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC} The 1987 total is 1 904 ha smaller because part of the 1987 scene had no data.</p>
        <p className="tc__cap">Table 2. Share of Bulawayo in each land cover class in % (1987 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>1987</th><th>2000</th><th>2013</th><th>2025</th></tr></thead>
            <tbody><Rows rows={T2} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>
        <p>The change matrix shows where the 2025 cultivated land came from (Table 3). About half of it (52.3%) was already cultivated in 1987. Of the land newly brought into cultivation, most had been grassland (4 150 ha) and woodland (1 500 ha). Smaller areas came from dense vegetation along streams and from bare land.</p>
        <p className="tc__cap">Table 3. Land cover in 1987 of the land cultivated in Bulawayo in 2025</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class in 1987</th><th>Area (ha)</th><th>Share of 2025 cultivation (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC} Matrix areas are rounded, so the total differs from Table 1 by 97 ha.</p>
        <p>The 2013 map has an overall accuracy of 86.45% and a Kappa coefficient of 0.83, and the 2025 map 88.24% and 0.86 (Table 4). Both are above the 85% often used as the minimum for land cover maps (Anderson et al., 1976).</p>
        <p className="tc__cap">Table 4. Accuracy of the Bulawayo land cover maps</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Measure</th><th>2013</th><th>2025</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>

        <h3>Residential expansion in Cowdray Park, Mahatshula and Richmond (1990 to 2025)</h3>
        <p>Built up land grew in all three suburbs (Table 5). Together they covered about 2 546 ha, of which 11.7% was built up in 1990 and 52.1% in 2025.</p>
        <Fig src={cowdray} cap="Map 5. Land Use Land Cover Maps Of Cowdray Park (1990, 2008 And 2025)." />
        <p>Cowdray Park changed most in absolute terms. Built up land grew from 226.5 ha (14.2%) to 890.5 ha (55.9%), and it overtook grassland as the largest class before 2008. Building was fastest from 1990 to 2008, at about 26.7 ha a year, the period in which the Hlalani Kuhle stands were allocated, and slowed to about 10.8 ha a year after 2008. Grassland lost 468.9 ha and woodland 195.1 ha, so both were roughly halved.</p>
        <Fig src={mahatshula} cap="Map 6. Land Use Land Cover Maps Of Mahatshula (1990, 2008 And 2025)." />
        <p>Mahatshula was almost undeveloped in 1990, with 3.0% built up. Built up land grew sixteenfold to 320.5 ha (47.7%) by 2025, and unlike Cowdray Park the rate increased over time, from about 7.3 ha a year before 2008 to 10.0 ha a year after it, which matches the servicing of the Mahatshula East phases. Grassland fell by 67%. Woodland first increased to 323.4 ha in 2008 and then fell to 220.1 ha, so the later building cleared trees as well as grassland.</p>
        <Fig src={richmond} cap="Map 7. Land Use Land Cover Maps Of Richmond (1990, 2008 And 2025)." />
        <p>Richmond, the smallest of the three, more than doubled its built up area from 50.9 ha (18.1%) to 115.1 ha (41.0%), at a steady 1.6 to 2.1 ha a year. It is the only suburb in which grassland increased after 2008. Its newer houses were built mainly on woodland, which fell from 133.8 ha in 2008 to 88.8 ha in 2025.</p>
        <p className="tc__cap">Table 5. Area of each class in the three suburbs in ha with the share of the suburb in % (1990 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Suburb</th><th>Class</th><th>1990</th><th>2008</th><th>2025</th><th>Change (ha)</th></tr></thead>
            <tbody><Rows rows={T5} num={2} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC} Mapped areas: Cowdray Park 1 593.4 ha, Mahatshula 671.2 to 671.7 ha, Richmond 282.2 ha (280.4 ha in 2025).</p>

        <h3>Diamond mining and land cover change in Ward 30, Mutare Rural District (1995 to 2025)</h3>
        <p>The 1995 map (Map 8) is the baseline, eleven years before diamonds were found. The ward was then communal farmland: woodland covered 22 190.6 ha or 54.9%, cultivation 31.7% and grassland 10.0%. Riparian vegetation lined the rivers on 3.0% of the ward, and mine dumps and bare ground covered only 112.0 ha, or 0.3% (Tables 6 and 7).</p>
        <div className="tc__one"><Fig src={mut1995} cap="Map 8. Land Use Land Cover Map Of Ward 30 Mutare Rural District (1995), the baseline." /></div>
        <p>Maps 9 to 11 show the ward in 2005, 2015 and 2025. In 2005, just before the rush, bare ground still covered only 87.6 ha. By 2015 the mined area had grown to 772.0 ha, and by 2025 to 3 413.6 ha, or 8.4% of the ward. More than three quarters of the growth (2 641.6 ha) came in the ten years after 2015, when the mines were merged under the state company.</p>
        <div className="tc__row">
          <Fig src={mut2005} cap="Map 9. Ward 30 (2005)." />
          <Fig src={mut2015} cap="Map 10. Ward 30 (2015)." />
          <Fig src={mut2025} cap="Map 11. Ward 30 (2025)." />
        </div>
        <p>Cultivation grew from 31.7% of the ward in 1995 to a peak of 40.0% in 2015, then fell to 29.0% in 2025, a loss of 4 432.4 ha in ten years. Over the same period grassland increased from 870.5 ha to 3 801.2 ha, which suggests that fields were left fallow and grassed over as well as dug up. Woodland fell steadily, by 2 271.1 ha over the 30 years, with the largest loss (1 257.8 ha) between 2015 and 2025. Water rose to 197.6 ha in 2015, partly because of pits and slimes dams holding water, and fell back to 109.5 ha by 2025.</p>
        <p className="tc__cap">Table 6. Area of each land cover class in Ward 30, Mutare Rural District in ha (1995 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>1995</th><th>2005</th><th>2015</th><th>2025</th><th>Change 1995 to 2025</th></tr></thead>
            <tbody><Rows rows={T6} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>
        <p className="tc__cap">Table 7. Share of Ward 30 in each land cover class in % (1995 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th>1995</th><th>2005</th><th>2015</th><th>2025</th></tr></thead>
            <tbody><Rows rows={T7} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">{SRC}</p>

        <h2>5 Discussion</h2>
        <p>Over 38 years the main change in Bulawayo has been cultivation spreading onto grassland and woodland, not buildings spreading. This agrees with Banga (2013), who found residents cultivating every open space in Emakhandeni outside the council's by-laws, at the cost of soil erosion and falling water tables. Cultivation grew fastest from 2000 to 2013, during the economic collapse of the 2000s, when food prices rose, formal jobs disappeared and many households turned to growing maize on open land. The land being ploughed is poorly suited to it. With a seasonal mean of about 525 mm and a coefficient of variation near 27%, Bulawayo's rainfall makes for an unreliable maize crop, and farming stream banks and vleis exposes them to erosion and silts the city's streams.</p>
        <p>The small increase in built up land, from 14.8% to 15.6%, is lower than that found by Sithole et al. (2024), who reported a 228% increase in built up area in Bulawayo from 1984 to 2022 using a Support Vector Machine classifier. The two studies differ in classes and in study area, but part of the difference comes from the 30 m pixel: in low density suburbs a single pixel holds a roof, a garden and trees, and is often classed as vegetation. The suburb maps show that growth on the edge of the city has been large where it was measured directly. Cowdray Park and Mahatshula went from mostly grassland to about half built up, and in Cowdray Park the timing follows the Hlalani Kuhle allocations after 2005. Many of those stands were allocated without water, sewer or roads, and the council still estimates that full servicing will take many years (NewsDay, 2025). Building there has run ahead of services.</p>
        <p>In Ward 30 the maps follow the history of the diamond fields closely. There is almost no mined land in 2005, a first wave of pits by 2015 after the companies took their concessions and the people of Chiadzwa were moved to Arda Transau, and a much larger expansion after 2015. The fall in cultivation after 2015 reflects both fields lost to mining and fields abandoned by relocated households. The loss of land is only one part of the environmental damage. Studies of the Save and Odzi rivers downstream found heavy siltation, high turbidity and raised iron, nickel, aluminium and manganese, which they linked to discharge from the diamond mines (ZELA, 2012; Njaya, 2017).</p>
        <p>The results have limits. Only the 2013 and 2025 Bulawayo maps were checked for accuracy, so the earlier maps, the suburb maps and the Ward 30 maps are unverified. Cultivated fields and grassland are hard to tell apart in dry season imagery, and this is the most likely source of error in the cultivation figures. The 1987 Bulawayo scene had a small area with no data. The mine class takes in all bare ground, so it may include some eroded land that mining did not cause.</p>

        <h2>6 Recommendations</h2>
        <p>Bulawayo City Council should map and allocate land for urban agriculture instead of relying on by-laws that are not enforced. Cultivation should be kept off stream banks, vleis and the remaining woodland, which are where most of the new fields came from, and directed to suitable plots with support for small grains and water harvesting, which suit the city's low and variable rainfall better than maize.</p>
        <p>In Cowdray Park and other new suburbs, services should be installed before or as stands are allocated. The Hlalani Kuhle stands that are already occupied should be serviced in order of population, starting with water and sanitation, and remaining woodland in Mahatshula and Richmond should be kept as public open space in the layout plans.</p>
        <p>In Ward 30, the Environmental Management Agency should require the Zimbabwe Consolidated Diamond Company to rehabilitate worked out pits and dumps, to contain slimes so that they do not reach the Save and Odzi rivers, and to publish environmental impact assessments for new areas. Households relocated to Arda Transau should be given title to their land and the farmland they were promised.</p>
        <p>Land cover in all three areas should be monitored every few years with the same method, and accuracy should be assessed for every map using field visits or high resolution imagery, so that the change figures can be relied on for planning.</p>

        <h2>7 Conclusion</h2>
        <p>Between 1987 and 2025 cultivation in Bulawayo more than doubled, from 11.4% to 25.0% of the city, mostly on former grassland and woodland, while woodland fell by 37.8% and built up land grew only slightly. In the three northern suburbs built up land rose from 11.7% to 52.1% between 1990 and 2025, fastest in Cowdray Park before 2008 and in Mahatshula after it. In Ward 30 of Mutare Rural District, mine dumps and bare ground grew from 112 ha in 1995 to 3 414 ha in 2025, mostly after 2015, and cultivation fell by 4 432 ha from its 2015 peak. In the city the change comes from many households acting on their own, and in the diamond fields from a single industry. In both places it has run ahead of planning and land management.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Anderson, J.R., Hardy, E.E., Roach, J.T. and Witmer, R.E. (1976) A land use and land cover classification system for use with remote sensor data. Professional Paper 964. US Geological Survey. <A href="https://doi.org/10.3133/pp964" /></p>
          <p>Banga, M. (2013) Illegal cultivation of open spaces in Emakhandeni, Bulawayo. Midlands State University. <A href="https://cris.library.msu.ac.zw/handle/11408/629" /></p>
          <p>Breiman, L. (2001) Random forests. Machine Learning, 45, 5–32. <A href="https://doi.org/10.1023/A:1010933404324" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D. and Moore, R. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18–27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Human Rights Watch (2009) Diamonds in the rough: human rights abuses in the Marange diamond fields of Zimbabwe. 26 June 2009. <A href="https://www.hrw.org/report/2009/06/26/diamonds-rough/human-rights-abuses-marange-diamond-fields-zimbabwe" /></p>
          <p>Mongabay (2022) Broken houses and promises: residents still in poverty near massive diamond project. October 2022. <A href="https://news.mongabay.com/2022/10/broken-houses-and-promises-residents-still-in-poverty-near-massive-diamond-project/" /></p>
          <p>NewsDay (n.d.) Murambatsvina victims instal sewer system. <A href="https://www.newsday.co.zw/news/article/275691/murambatsvina-victims-instal-sewer-system" /></p>
          <p>NewsDay (2025) Cowdray Park project faces six year delay. Southern Eye. <A href="https://www.newsday.co.zw/southerneye/local/article/200055140/cowdray-park-project-faces-six-year-delay" /></p>
          <p>Njaya, A. (2017) An assessment of the impact of diamond mining on water quality of the Save and Odzi rivers. MSc thesis, Midlands State University. <A href="https://cris.library.msu.ac.zw/handle/11408/2801" /></p>
          <p>Sithole, S.M., Musakwa, W., Magidi, J. and Kibangou, A.Y. (2024) Characterising landcover changes and urban sprawl using geospatial techniques and landscape metrics in Bulawayo, Zimbabwe (1984–2022). Heliyon, 10(6), e27275. <A href="https://doi.org/10.1016/j.heliyon.2024.e27275" /></p>
          <p>The Herald (n.d.) BCC delivers 650 serviced stands. <A href="https://www.heraldonline.co.zw/bcc-delivers-650-serviced-stands/" /></p>
          <p>USGS (2024) Landsat Collection 2 Level-2 science products. US Geological Survey. <A href="https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products" /></p>
          <p>ZELA (2012) Water quality of the Save and Odzi rivers in the Marange diamond mining area. Zimbabwe Environmental Law Association. <A href="https://www.zela.org" /></p>
          <p>ZIMSTAT (2022) 2022 Population and Housing Census: preliminary report. Zimbabwe National Statistics Agency, Harare. <A href="https://www.zimstat.co.zw" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
