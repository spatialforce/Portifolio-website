import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/shurugwi-soil-erosion/map1_study_area.webp";
import map2 from "../assets/casestudies/shurugwi-soil-erosion/map2_factors.webp";
import map3 from "../assets/casestudies/shurugwi-soil-erosion/map3_classes.webp";
import map4 from "../assets/casestudies/shurugwi-soil-erosion/map4_gully.webp";
import map6 from "../assets/casestudies/shurugwi-soil-erosion/map6_closeup.webp";
import fig1 from "../assets/casestudies/shurugwi-soil-erosion/fig1_classes.webp";
import fig2 from "../assets/casestudies/shurugwi-soil-erosion/fig2_landcover.webp";

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

function Sec({ n, title, children }: { n: string; title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2>{n ? `${n} ` : ""}{title}</h2>
      {children}
    </section>
  );
}

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

const T1 = [
  ["CHIRPS v2.0 rainfall", "5.5 km", "1991 to 2020", "Rainfall erosivity (R)"],
  ["iSDAsoil sand, silt, clay and organic carbon, 0 to 20 cm", "30 m", "Modelled (2021)", "Soil erodibility (K)"],
  ["Copernicus GLO-30 elevation model", "30 m", "2011 to 2015", "Slope length and steepness (LS), flow paths, hillshade"],
  ["Sentinel-2 surface reflectance (227 scenes)", "10 m", "December to March, 2019/20 to 2023/24", "Cover management (C)"],
  ["ESA WorldCover 10 m v200", "10 m", "2021", "Land cover, support practice (P)"],
  ["Esri World Imagery", "About 1 m", "Recent", "Visual check of gully risk (Map 5)"],
  ["Ward boundaries (ZimStat and OCHA)", "Areas", "2020", "District and ward boundaries"],
  ["OpenStreetMap", "Lines and points", "2026", "Rivers, roads and place names"],
];

const T2 = [
  ["R, rainfall erosivity (MJ mm ha⁻¹ h⁻¹ yr⁻¹)", "R = 0.0483 P^1.61, P = mean annual rainfall (mm)", "Renard and Freimund (1994)", "1 391 to 1 873"],
  ["K, soil erodibility (t ha h ha⁻¹ MJ⁻¹ mm⁻¹)", "EPIC equation from sand, silt, clay and organic carbon", "Williams (1995)", "0.017 to 0.020"],
  ["LS, slope length and steepness", "LS = (λ / 22.13)^0.4 (sin β / 0.0896)^1.3, λ ≤ 300 m", "Moore and Burch (1986)", "0.05 to 13.1"],
  ["C, cover management", "C = exp(−2 NDVI / (1 − NDVI)), rainy-season NDVI", "van der Knijff et al. (2000)", "0.001 to 0.53"],
  ["P, support practice", "Contouring values by slope on cropland, 1 elsewhere", "Wischmeier and Smith (1978)", "0.5 to 1"],
  ["Gully risk, from the stream power index (SPI)", "SPI = As tan β, As = drainage area per metre of contour", "Moore et al. (1991)", "Threshold 201.6"],
];

const T3 = [
  ["Very low (below 2)", "1 630.5", "45.4"],
  ["Low (2 to 5)", "1 029.6", "28.6"],
  ["Moderate (5 to 10)", "587.9", "16.4"],
  ["High (10 to 20)", "258.2", "7.2"],
  ["Very high (above 20)", "89.1", "2.5"],
  ["District land", "3 595.3", "100"],
];

const T4 = [
  ["Tree cover", "822.4", "0.033", "2.02", "2.8", "166", "8.4"],
  ["Shrubland", "1 447.2", "0.126", "4.86", "12.1", "703", "16.2"],
  ["Grassland", "991.9", "0.206", "5.67", "13.0", "562", "17.9"],
  ["Cropland", "307.0", "0.260", "2.52", "1.8", "77", "12.5"],
  ["Bare or sparse", "19.6", "0.723", "31.06", "68.9", "61", "43.0"],
];

// all 25 ward units, highest mean soil loss first; last column is land at high gully risk (%)
const T5 = [
  ["11", "75.3", "6.73", "21.1", "5.3", "11.2", "35.8"],
  ["Town", "133.9", "6.55", "15.7", "13.9", "5.4", "5.5"],
  ["16", "210.0", "5.81", "13.3", "7.7", "6.2", "15.7"],
  ["12", "76.7", "5.72", "15.5", "4.6", "19.1", "18.0"],
  ["7", "52.6", "5.57", "14.1", "4.5", "14.8", "26.1"],
  ["14", "68.6", "5.50", "13.2", "5.0", "11.3", "13.0"],
  ["13", "95.7", "5.41", "14.2", "5.2", "8.8", "8.8"],
  ["10", "74.1", "5.39", "13.7", "4.8", "16.1", "24.6"],
  ["9", "104.8", "4.97", "9.6", "4.4", "11.2", "19.0"],
  ["1", "276.4", "4.52", "10.7", "5.6", "8.4", "15.7"],
  ["24", "66.1", "4.33", "8.8", "4.3", "18.5", "18.8"],
  ["3", "77.1", "4.28", "9.0", "5.0", "1.5", "11.7"],
  ["5", "131.9", "4.22", "9.1", "4.5", "7.1", "21.3"],
  ["8", "63.4", "4.13", "8.0", "4.1", "16.4", "12.2"],
  ["17", "234.6", "4.12", "9.0", "6.5", "6.9", "6.7"],
  ["15", "81.0", "4.11", "9.2", "5.3", "6.6", "9.5"],
  ["19", "219.0", "4.06", "9.2", "6.7", "8.1", "10.8"],
  ["20", "200.4", "4.04", "9.1", "5.5", "7.1", "21.3"],
  ["21", "321.5", "3.95", "7.8", "4.9", "11.9", "16.4"],
  ["18", "333.3", "3.75", "8.2", "6.7", "7.4", "4.9"],
  ["22", "94.0", "3.62", "7.0", "4.3", "2.6", "17.0"],
  ["2", "206.8", "3.45", "6.2", "4.2", "10.0", "14.6"],
  ["6", "178.1", "3.42", "6.2", "4.3", "5.1", "23.2"],
  ["23", "143.4", "3.19", "4.9", "3.8", "6.7", "18.5"],
  ["4", "76.8", "2.86", "5.1", "4.4", "2.2", "7.5"],
];

export default function ShurugwiCaseStudy() {
  return (
    <>
      <CaseLayout slug="shurugwi-soil-erosion">
        <h1>Assessment of Soil Erosion and Gully Erosion Risk in Shurugwi District, Zimbabwe</h1>
        <p className="tc__by">A 30 m map of where soil is washed away and where gullies are likely to form, ranked by ward.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (22 January 2026)</p>
        <Facts rows={[["Place", "Shurugwi District, Midlands Province, Zimbabwe"], ["Area", "3 603 km², 24 rural wards and Shurugwi Town"], ["Period", "Rainy seasons 2019/20 to 2023/24"], ["Methods", "RUSLE soil loss model, gully risk from runoff paths"], ["Grid", "30 m, UTM zone 36S"], ["Tools", "Google Earth Engine, Python"]]} />

        <p style={{ marginTop: 22 }}><b>What was done.</b> Soil loss was estimated for every 30 m of land with the Revised Universal Soil Loss Equation. A separate gully risk map shows where runoff gathers strongly enough on thin cover to cut gullies.</p>
        <p><b>What was found.</b> The district loses about 1.57 million tonnes of soil a year. Soil loss is highest on the steep high ground of the north and west. Gully risk is highest on the lower ground of the south and east.</p>
        <p><b>What it means.</b> The two kinds of erosion need different work in different places. Ward 11 is high on both and is the first place to start.</p>

        <Sec n="1" title="Introduction">
          <div>
            <p>Soil erosion by water is one of the main forms of land degradation in Zimbabwe. On communal land, grazing and the clearing of woodland leave the ground thinly covered when the first storms of the rainy season arrive. Water then removes soil in two ways. Sheet and rill erosion strips a thin layer from the whole slope, while gully erosion cuts deep channels where runoff gathers along valley floors, paths and field edges. Gullies are often the more visible damage, since they remove land from use, cut roads and send sediment straight into rivers and dams.</p>
            <p>The Revised Universal Soil Loss Equation (RUSLE) estimates mean annual sheet and rill loss from rainfall, soil, slope and cover (Renard et al., 1997). It does not model gullies. Gully heads form where the drainage area and slope together give runoff enough power to cut the soil, and this can be ranked with a stream power index computed from an elevation model (Moore et al., 1991). Land use changes the threshold at which gullies begin, with lower thresholds on cultivated and bare ground (Torri and Poesen, 2014).</p>
            <p>This study applies both methods to Shurugwi District on a 30 m grid for a single recent period. Mapping soil loss and gully risk side by side shows whether the two kinds of erosion fall in the same places, and so whether one set of conservation measures would serve both.</p>
          </div>
        </Sec>

        <Sec n="2" title="Objectives">
          <div>
            <ol>
              <li>To estimate mean annual sheet and rill soil loss across Shurugwi District with RUSLE at 30 m.</li>
              <li>To map the risk of gully erosion from runoff paths and rainy-season cover.</li>
              <li>To compare both measures across land cover types and elevation.</li>
              <li>To rank wards by soil loss and gully risk for targeting conservation work.</li>
            </ol>
          </div>
          <div>
            <p>The study covers one period, the five rainy seasons from 2019/20 to 2023/24, and does not measure change over time. Results are relative estimates for ranking places, not measured losses.</p>
          </div>
        </Sec>

        <Sec n="3" title="Study area">
          <div>
            <p>Shurugwi District lies in Midlands Province in central Zimbabwe, between about 29.8°E and 30.5°E and 19.4°S and 20.1°S (Map 1). It covers 3 603 km², of which 3 595 km² is land. The district has 24 rural wards and the town of Shurugwi, whose 13 urban wards are treated here as a single unit.</p>
            <p>The land rises from about 950 m in the south to about 1 570 m in the north and on the ridge that runs through the west, where the Great Dyke ridge passes the town. Two thirds of the district lies below 1 200 m. The Ngezi, Mapongokwe and Runde rivers and their tributaries drain it. Mean annual rainfall from 1991 to 2020 was about 590 to 710 mm (Funk et al., 2015), falling mostly between November and March.</p>
            <p>Shrubland covers 40 % of the land, grassland 28 %, tree cover 23 % and cropland 9 %. Most of the rural land is communal, with small fields of maize and small grains and open grazing for cattle and goats.</p>
          </div>
          <div>
            <Fig src={map1} cap="Map 1. Shurugwi District: elevation, rivers, ward numbers and main places." />
          </div>
        </Sec>

        <Sec n="4" title="Data and methods">
          <div>
            <h3>Data</h3>
            <p>All data are open (Table 1). Rainfall, soil, elevation, land cover and Sentinel-2 imagery were prepared in Google Earth Engine (Gorelick et al., 2017) and resampled to one 30 m grid. Ward boundaries come from the ZimStat 2020 set published by OCHA.</p>
            <h3>Soil loss</h3>
            <p>Mean annual soil loss A, in tonnes per hectare per year, was calculated for every cell as A = R × K × LS × C × P (Table 2). R was taken from CHIRPS mean annual rainfall with the equation of Renard and Freimund (1994). K was calculated from iSDAsoil topsoil texture and organic carbon (Hengl et al., 2021; Williams, 1995). Rock and water cells without soil values (10 983 cells, under 0.3 % of the grid) took the value of the nearest cell with soil. LS was calculated from the filled elevation model with slope length taken from flow accumulation and capped at 300 m (Moore and Burch, 1986).</p>
            <p>C was calculated from the median NDVI of all cloud-masked Sentinel-2 scenes from December to March over five rainy seasons (van der Knijff et al., 2000), which gives the cover at the time when most erosive rain falls. C was set to 0 on built-up land and water. P was set from slope on cropland using contouring values and to 1 elsewhere (Wischmeier and Smith, 1978).</p>
          </div>
          <div>
            <Table cap="Table 1. Data used" head={["Dataset", "Resolution", "Period", "Use"]} rows={T1} num={9} />
          </div>
          <div>
            <Table cap="Table 2. Factors and their range across the district (1st to 99th percentile)" head={["Factor", "Equation", "Source", "Range"]} rows={T2} num={3} />
          </div>
          <div>
            <h3>Gully risk</h3>
            <p>Gullies start where a lot of runoff gathers in one line on a slope with thin cover. The stream power index SPI = As tan β was calculated for every cell, where As is the drainage area per metre of contour width and β is the slope (Moore et al., 1991). Cells draining 0.5 to 100 ha were considered, which covers overland and seasonal flow lines but leaves out the permanent rivers. A cell was taken as a likely gully path when its SPI was in the top 10 % (201.6 or more) and its rainy-season C was 0.10 or more, meaning the cover was thin.</p>
            <p>For every point, the length of likely gully paths within 500 m was divided by the land area around it, in km/km², and grouped into five classes: very low (below 0.15), low (0.15 to 0.3), moderate (0.3 to 0.6), high (0.6 to 1.0) and very high (above 1.0). The map shows where gullies are likely, not mapped gullies, and one high-risk area was checked against satellite imagery (Map 5).</p>
          </div>
          <div>
            <h3>Analysis</h3>
            <p>Soil loss was grouped into five classes: very low (below 2 t/ha/yr), low (2 to 5), moderate (5 to 10), high (10 to 20) and very high (above 20). The share of land above the upper tolerance of 11.2 t/ha/yr (Wischmeier and Smith, 1978) was also measured. For the soil erosion map, soil loss was averaged over about 250 m around each point and shown in the same five classes. Mean soil loss, the share of high and very high land and the share of land at high or very high gully risk were then summarised by land cover, elevation band and ward. Erosion changes gradually across the land and does not stop at ward boundaries, so the maps show it as a continuous surface. Ward boundaries are drawn on the maps only for reference, and the ward figures are used only as a planning summary, because a ward average hides the differences inside it. All statistics exclude open water.</p>
          </div>
          <div>
            <Fig src={map2} cap="Map 2. The five RUSLE factors and land cover. R rises towards the wetter north-east, K varies little, LS is highest on the ridge in the west, and C is lowest under the woodland along it." />
          </div>
        </Sec>

        <Sec n="5" title="Results">
          <div>
            <h3>Soil erosion</h3>
            <p>The mean soil loss over the district is 4.36 t/ha/yr and the median is 2.33 t/ha/yr, a total of about 1.57 million tonnes a year. Almost three quarters of the land is in the very low (45.4 %) or low (28.6 %) class (Table 3, Figure 1). High and very high loss covers 347.3 km², 9.7 % of the land, and 7.9 % of the land loses soil faster than 11.2 t/ha/yr. The 10 % of cells with the highest loss produce 44.2 % of all the soil lost.</p>
            <p>Loss rises with height. The mean is 4.17 t/ha/yr below 1 200 m, 4.55 between 1 200 and 1 350 m and 5.04 above 1 350 m, because the higher ground is steeper. The north half of the district averages 4.63 t/ha/yr against 4.10 in the south, and the west 4.52 against 4.21 in the east (Map 3). On the map, 3.8 % of the land is at high or very high risk and 22.5 % at moderate risk.</p>
          </div>
          <div>
            <Table cap="Table 3. Area in each soil loss class (t/ha/yr)" head={["Class", "Area (km²)", "Share (%)"]} rows={T3} num={1} total />
            <Fig src={fig1} cap="Figure 1. Area in each soil loss class." />
          </div>
          <div>
            <h3>Gully erosion</h3>
            <p>High or very high gully risk covers 529.4 km², 14.7 % of the land (11.6 % high and 3.2 % very high), and moderate risk a further 890.5 km² (24.8 %) (Map 4). The pattern is close to the reverse of soil erosion. High gully risk covers 18.0 % of the land below 1 200 m but only 8.1 % above 1 350 m, and it is more common in the south (18.6 %) than the north (10.7 %) and in the east (16.5 %) than the west (12.8 %).</p>
            <p>Only 15.1 % of the high gully risk area also has high soil loss. Long gentle slopes collect runoff from large areas, and the cover there is thinner in the rainy season (mean C 0.162 below 1 200 m, against 0.095 above 1 350 m). The steep hills lose more soil from their surface, but runoff there gathers less into single lines.</p>
          </div>
          <div className="tc__row tc__row--2">
            <Fig src={map3} cap="Map 3. Soil erosion risk in five classes, with ward boundaries for reference. High risk follows the hill slopes of the north and west and the hills around Shurugwi Town." />
            <Fig src={map4} cap="Map 4. Gully erosion risk in five classes, with ward boundaries for reference. High risk is spread across the lower ground of the south and east and is rare under the woodland of the ridge in the west." />
          </div>
          <div>
            <h3>Land cover</h3>
            <p>Bare and sparse ground loses the most soil, 31.06 t/ha/yr on average, but covers only 19.6 km² (Table 4). Grassland (5.67 t/ha/yr) and shrubland (4.86) are next, and together they produce 81 % of all the soil lost. Tree cover has the lowest loss, 2.02 t/ha/yr. Cropland has the highest C of the vegetated classes, 0.26, which means the thinnest cover, but a low mean of 2.52 t/ha/yr, because most fields lie on gentle ground. For gully risk, bare ground is again highest (43.0 % of it at high risk), followed by grassland (17.9 %) and shrubland (16.2 %), with tree cover lowest (8.4 %).</p>
          </div>
          <div>
            <Table cap="Table 4. Soil loss and gully risk by land cover" head={["Land cover", "Area (km²)", "Mean C", "Mean loss (t/ha/yr)", "High and very high (%)", "Loss (kt/yr)", "High gully risk (%)"]} rows={T4} num={1} src="Built-up land (6.7 km²) has C = 0 and is left out." />
          </div>
          <div>
            <Fig src={fig2} cap="Figure 2. (a) Mean soil loss and (b) share of land at high gully risk by land cover." />
          </div>
          <div>
            <Fig src={map6} cap="Map 5. Close-up of a high gully risk area in ward 20: (a) satellite image (Esri, Maxar, Earthstar Geographics) and (b) gully risk. The wooded ridge in the centre is low risk, while the open ground on both sides, where drainage lines run down to the main channels, is high risk." />
          </div>
          <div>
            <h3>Wards</h3>
            <p>Ward means range from 2.86 t/ha/yr in ward 4 to 6.73 in ward 11 (Table 5). Ward 11 has the highest mean and the largest share of high and very high land (21.1 %), and also the most land at high gully risk (35.8 %). Shurugwi Town is second for soil loss (6.55) because of its steep hills, with a median slope of 13.9 %, but has little gully risk (5.5 %).</p>
            <p>Gully risk is also high in wards 7 (26.1 %) and 10 (24.6 %) in the centre and in wards 6, 20 and 5 (21.3 to 23.2 %) in the south, several of which have low soil loss. Ward figures are averages over large areas and should be read with Maps 3 and 4, which show where inside each ward the risk lies.</p>
          </div>
          <div>
            <Table cap="Table 5. Soil loss and gully risk by ward, highest mean soil loss first" head={["Ward", "Area (km²)", "Mean loss (t/ha/yr)", "High and very high (%)", "Median slope (%)", "Cropland (%)", "High gully risk (%)"]} rows={T5} num={1} />
          </div>
        </Sec>

        <Sec n="6" title="Discussion">
          <div>
            <p>The main finding is that soil erosion and gully risk are driven by different things and fall in different places. Soil loss in RUSLE depends most on slope, so it peaks on the hills. Gully risk depends on how much water gathers in one line as well as on slope, so it peaks on the long, gentler slopes of the lower ground, where cover in the rainy season is also thinner. A plan based on RUSLE alone would send most of the conservation effort to the hills and miss the places where gullies are most likely to form.</p>
            <p>Grassland and shrubland stand out on both measures and hold most of the land at high gully risk. These are mostly the open grazing areas of the communal land, where cover is thin early in the rainy season. Cropland shows low loss on both measures, but this should be read with care. The cover factor comes from the median NDVI over the season, which hides the weeks after ploughing when fields are bare, and Torri and Poesen (2014) found the lowest gully thresholds on cropland.</p>
            <p>The results have several limits. The R equation was developed in the United States and has not been calibrated for Zimbabwe. K comes from a modelled soil map. The gully threshold is relative, the top 10 % of the district, and the risk map was not tested against mapped gullies. The imagery check in Map 5 is a single visual check, not a validation. Ward summaries depend on where the boundaries happen to fall, since erosion has no edge that matches them, so they are a guide for planning, not a measure of each ward. Culverts, roads and cattle tracks, which often start gullies, are not resolved on a 30 m grid. The values should be read as a ranking of places for field checks, not as measured losses.</p>
          </div>
        </Sec>

        <Sec n="7" title="Recommendations">
          <div>
            <p>Ward 11 should be the first target, since it ranks highest for both soil loss and gully risk. Grazing management and reseeding on its grassland and shrubland would address both.</p>
            <p>On the steep hills of the north, the west and around Shurugwi Town, where soil loss is highest, the priority is to keep tree cover and restore it on bare slopes. On the lower ground of wards 7, 10, 6, 20 and 5, where gully risk is highest, the priority is to slow runoff with stone lines, check dams and grassed waterways along the drainage lines.</p>
            <p>The gully map should be tested in the field. A sample of high and low risk sites in the worst wards would show how well the map predicts active gullies and allow the threshold to be set from local evidence.</p>
          </div>
        </Sec>

        <Sec n="8" title="Conclusion">
          <div>
            <p>Shurugwi District loses about 1.57 million tonnes of soil a year to sheet and rill erosion, a mean of 4.36 t/ha/yr, and 7.9 % of its land is above the tolerance of 11.2 t/ha/yr. Soil loss is highest on the steep high ground, while the 529 km² at high gully risk lie mostly on the thinly covered lower ground. Only 15 % of the high gully risk area also has high soil loss, so the two kinds of erosion need to be planned for separately. Ward 11 ranks high on both and should come first.</p>
          </div>
        </Sec>

        <Sec n="" title="References">
          <div className="tc__ref">
            <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
            <p>ESA (2024) Sentinel-2 MSI Level-2A surface reflectance. European Space Agency, Copernicus programme.</p>
            <p>Esri (2026) World Imagery. Esri, Maxar, Earthstar Geographics. <A href="https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9" /></p>
            <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
            <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
            <p>Hengl, T., Miller, M.A.E., Križan, J., Shepherd, K.D. et al. (2021) African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Scientific Reports, 11, 6130. <A href="https://doi.org/10.1038/s41598-021-85639-y" /></p>
            <p>Moore, I.D. and Burch, G.J. (1986) Physical basis of the length-slope factor in the Universal Soil Loss Equation. Soil Science Society of America Journal, 50, 1294-1298. <A href="https://doi.org/10.2136/sssaj1986.03615995005000050042x" /></p>
            <p>Moore, I.D., Grayson, R.B. and Ladson, A.R. (1991) Digital terrain modelling: a review of hydrological, geomorphological and biological applications. Hydrological Processes, 5, 3-30. <A href="https://doi.org/10.1002/hyp.3360050103" /></p>
            <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB), with ZimStat ward boundaries. Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
            <p>OpenStreetMap contributors (2026) OpenStreetMap. <A href="https://www.openstreetmap.org" /></p>
            <p>Renard, K.G. and Freimund, J.R. (1994) Using monthly precipitation data to estimate the R-factor in the revised USLE. Journal of Hydrology, 157, 287-306. <A href="https://doi.org/10.1016/0022-1694(94)90110-4" /></p>
            <p>Renard, K.G., Foster, G.R., Weesies, G.A., McCool, D.K. and Yoder, D.C. (1997) Predicting Soil Erosion by Water: A Guide to Conservation Planning with the Revised Universal Soil Loss Equation (RUSLE). Agriculture Handbook 703. US Department of Agriculture, Washington, DC.</p>
            <p>Torri, D. and Poesen, J. (2014) A review of topographic threshold conditions for gully head development in different environments. Earth-Science Reviews, 130, 73-85. <A href="https://doi.org/10.1016/j.earscirev.2013.12.006" /></p>
            <p>van der Knijff, J.M., Jones, R.J.A. and Montanarella, L. (2000) Soil Erosion Risk Assessment in Europe. EUR 19044 EN. European Soil Bureau, Joint Research Centre, Ispra.</p>
            <p>Williams, J.R. (1995) The EPIC model. In: Singh, V.P. (ed.) Computer Models of Watershed Hydrology. Water Resources Publications, Highlands Ranch, 909-1000.</p>
            <p>Wischmeier, W.H. and Smith, D.D. (1978) Predicting Rainfall Erosion Losses: A Guide to Conservation Planning. Agriculture Handbook 537. US Department of Agriculture, Washington, DC.</p>
            <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
          </div>
        </Sec>
      </CaseLayout>
    </>
  );
}
