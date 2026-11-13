import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/mukuvisi-runoff/map1_study_area.webp";
import map2 from "../assets/casestudies/mukuvisi-runoff/map2_drainage.webp";
import map3 from "../assets/casestudies/mukuvisi-runoff/map3_landcover.webp";
import map4 from "../assets/casestudies/mukuvisi-runoff/map4_soil.webp";
import map5 from "../assets/casestudies/mukuvisi-runoff/map5_cn.webp";
import map6 from "../assets/casestudies/mukuvisi-runoff/map6_runoff.webp";
import fig1 from "../assets/casestudies/mukuvisi-runoff/fig1_design_storms.webp";
import fig2 from "../assets/casestudies/mukuvisi-runoff/fig2_hydrographs.webp";
import fig3 from "../assets/casestudies/mukuvisi-runoff/fig3_subcatchments.webp";

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
  ["Copernicus DEM GLO-30", "30 m", "2011 to 2015", "Catchment, streams, sub-catchments, flow length and slope"],
  ["ESA WorldCover v200", "10 m, resampled to 30 m (majority)", "2021", "Land cover for curve numbers"],
  ["iSDAsoil sand and clay content", "30 m, 0 to 30 cm", "2021", "Soil texture and hydrologic soil group"],
  ["CHIRPS v2.0 daily rainfall", "0.05° (about 5 km), 19 cells", "1981/82 to 2024/25", "Annual maximum daily rainfall and design storms"],
  ["OpenStreetMap rivers, roads, dams and suburbs", "Lines, areas and points", "2026", "Outlet, check of the main stem and map detail"],
  ["OCHA administrative boundaries", "Areas", "2020", "Harare Province and districts"],
];

const T2 = [
  ["Tree cover", "Woods, fair condition", "36", "60", "73", "79", "25.5"],
  ["Shrubland", "Brush, weed and grass mixture, fair", "35", "56", "70", "77", "2.7"],
  ["Grassland", "Pasture, grassland or range, fair", "49", "69", "79", "84", "14.5"],
  ["Cropland", "Row crops, straight row, good", "67", "78", "85", "89", "16.7"],
  ["Built-up", "Residential, 1/8 acre lots (65 % impervious)", "77", "85", "90", "92", "39.9"],
  ["Bare ground", "Fallow, bare soil", "77", "86", "91", "94", "0.6"],
  ["Open water", "Water surface", "98", "98", "98", "98", "0.1"],
  ["Wetland", "Herbaceous wetland", "85", "85", "85", "85", "< 0.1"],
];

const T3 = [
  ["2", "42.1", "13.2", "0.31", "2.95", "73.9"],
  ["5", "52.8", "20.1", "0.38", "4.51", "114.9"],
  ["10", "59.9", "25.1", "0.42", "5.62", "144.5"],
  ["25", "68.8", "31.7", "0.46", "7.11", "184.2"],
  ["50", "75.5", "36.8", "0.49", "8.26", "214.8"],
  ["100", "82.1", "42.0", "0.51", "9.43", "246.1"],
];

const T4 = [
  ["1 Greendale", "12.2", "78.1", "17.0", "2.4", "19.0", "0.32", "16.0", "1.31", "30.2"],
  ["2 Upper Mukuvisi", "41.1", "81.0", "24.1", "3.4", "22.8", "0.38", "52.5", "1.28", "92.8"],
  ["3 Eastlea–Highlands", "22.1", "80.7", "21.9", "1.8", "22.2", "0.37", "41.8", "1.90", "75.8"],
  ["4 Hatfield", "31.4", "80.2", "31.3", "3.0", "22.3", "0.37", "42.8", "1.36", "76.0"],
  ["5 City Centre", "22.4", "85.5", "63.5", "3.1", "29.4", "0.49", "41.0", "1.83", "67.1"],
  ["6 Glen Norah", "11.2", "87.0", "66.5", "2.6", "31.2", "0.52", "24.8", "2.22", "40.3"],
  ["7 Waterfalls–Mbare", "67.0", "83.8", "56.1", "4.8", "27.5", "0.46", "84.1", "1.26", "140.0"],
  ["8 Glen View", "16.9", "82.3", "21.0", "3.0", "24.6", "0.41", "26.4", "1.57", "45.9"],
];

const T5 = [
  ["I (dry)", "10.3", "0.17", "2.30", "54.6"],
  ["II (average)", "25.1", "0.42", "5.62", "144.5"],
  ["III (wet)", "39.1", "0.65", "8.76", "231.3"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function MukuvisiCaseStudy() {
  return (
    <CaseLayout slug="mukuvisi-runoff">
      <h1>Watershed Delineation and Surface Runoff Estimation for the Mukuvisi Catchment, Harare, Using the SCS Curve Number Method</h1>
      <p className="tc__by">A catchment, its streams and sub-catchments traced from elevation data, and storm runoff estimated from land cover and soil.</p>
      <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (13 November 2026)</p>
      <Facts rows={[["Place", "Harare, Harare Province"], ["Period", "Land cover 2021; rainfall 1981/82 to 2024/25"], ["Data", "Copernicus DEM, ESA WorldCover, iSDAsoil, CHIRPS, OpenStreetMap"], ["Methods", "D8 watershed delineation, SCS curve number, Gumbel design storms, SCS unit hydrograph"], ["Tools", "Python (pysheds, rasterio, GeoPandas)"]]} />

      <h2>1 Introduction</h2>
      <p>The Mukuvisi River rises in the east of Harare, near Mabvuku, and flows west and south-west through the city centre, Mbare, Waterfalls and Glen View before it joins the Manyame River, which feeds Lake Chivero, the main water supply of the city. Its catchment holds the central business district, the industrial areas of Workington and Southerton and some of the most crowded high-density suburbs of Harare. As the city has grown, roofs, roads and paving have replaced grassland and woodland, so that more of the rain runs off the ground and less soaks in. Gumindoga et al. (2014) found that urban land in the catchment grew from 21 to 56 km² between 1986 and 2008, and that streamflow rose with it. Flooding of homes in Mbare, Glen View and Budiriro during heavy storms has become a common event.</p>
      <p>Planning drains and keeping homes off the flood plain need an estimate of how much water a storm will send down the river and its tributaries, and where that water comes from. The Soil Conservation Service curve number method is widely used for such estimates where streamflow records are short or missing (USDA, 1986). It gives every piece of land a curve number from its land cover and soil, which sets how much of a storm becomes runoff. This study traces the Mukuvisi catchment from elevation data and uses the curve number method to estimate the runoff and the flood peaks that storms of different sizes would produce.</p>

      <h2>2 Objectives</h2>
      <ol>
        <li>To delineate the Mukuvisi catchment, its drainage network and its sub-catchments from a digital elevation model.</li>
        <li>To derive curve numbers for the catchment from land cover and soil texture.</li>
        <li>To estimate design storm depths for return periods of 2 to 100 years from satellite rainfall data.</li>
        <li>To estimate the runoff depth, volume and peak discharge of these storms at the catchment outlet and in each sub-catchment.</li>
        <li>To evaluate how sensitive the runoff is to the wetness of the soil before a storm.</li>
      </ol>

      <h2>3 Study area</h2>
      <p>The Mukuvisi catchment lies wholly within Harare Province, between about 30.90° E and 31.19° E and 17.79° S and 17.95° S (Map 1). The outlet was placed on the Mukuvisi just above its confluence with the Manyame, south-west of Glen View. The land is a gently rolling plateau that falls from about 1 600 m in the east to about 1 370 m at the outlet, with a mean height of 1 476 m. The climate is subtropical highland, with a single rainy season from about November to March. Over the 44 seasons from 1981/82 to 2024/25 the catchment received a mean of 780 mm between October and April, most of it in heavy afternoon storms. The soils are mainly deep red and brown sandy clay loams formed on granite and greenstone.</p>
      <Fig src={map1} cap="Map 1. Study Area Map, showing elevation, the main roads, the dams and the suburbs of the catchment." />

      <h2>4 Data and methods</h2>
      <p>All data were projected to UTM zone 36S and placed on one grid of 30 m cells (Table 1). Areas, lengths and slopes were measured on this grid.</p>
      <Table cap="Table 1. Data used in the study" head={["Dataset", "Resolution", "Date", "Use"]} rows={T1} num={9}
        src="Source: European Space Agency (2021); Zanaga et al. (2022); Hengl et al. (2021); Funk et al. (2015); OpenStreetMap contributors (2026); OCHA (2020)." />

      <h3>Watershed delineation</h3>
      <p>Pits and depressions in the elevation model were filled and flat areas resolved, so that every cell drains to the edge of the grid. The direction of flow from every cell was set to the steepest of its eight neighbours (the D8 method), and the number of cells draining through every cell was counted (Bartos, 2020). The outlet was placed on the mapped river 600 m above its end at the Manyame and moved to the cell of greatest flow within 120 m. The catchment was taken as every cell draining to the outlet. Streams were defined as cells draining 1 km² or more and given a Strahler order. The main stem was followed upstream from the outlet along the larger branch at every junction. The catchment was then split into sub-catchments, one for every tributary draining 8 km² or more and one for each stretch of the main stem between them. Each sub-catchment was named after the suburb it mainly drains.</p>

      <h3>Curve numbers</h3>
      <p>Sand and clay content were averaged over the top 30 cm of the soil and used to place every cell in a USDA texture class. Texture classes were grouped into the four hydrologic soil groups of the SCS method, from A (sandy, fast to soak up water) to D (clayey, slow): sand, loamy sand and sandy loam were placed in group A, loam and silt loam in group B, sandy clay loam in group C and the clayey textures in group D. Each land cover class was matched to a cover type of the USDA (1986) tables, and each cell was given the curve number of its cover type and soil group (Table 2). These values are for average soil moisture before a storm (antecedent moisture condition II).</p>
      <Table cap="Table 2. Curve numbers by land cover and hydrologic soil group" head={["Land cover", "Cover type in USDA (1986)", "A", "B", "C", "D", "Share of catchment (%)"]} rows={T2} num={2}
        src="Source: USDA (1986), Table 2-2; shares from ESA WorldCover 2021." />

      <h3>Design storms</h3>
      <p>Daily rainfall for the 19 satellite cells that cover the catchment was averaged, with each cell weighted by the share of the catchment it covers. The wettest day of each rainy season (October to April) was taken for the 44 seasons from 1981/82 to 2024/25. A Gumbel distribution was fitted to these 44 annual maxima by the method of moments (Gumbel, 1958), and the 24-hour rainfall was read from it for return periods of 2, 5, 10, 25, 50 and 100 years.</p>

      <h3>Runoff and peak discharge</h3>
      <p>The runoff depth Q (mm) from a storm of depth P (mm) was found from the curve number equation Q = (P − 0.2S)² / (P + 0.8S) when P is greater than 0.2S, and Q = 0 otherwise, where S = 25 400 / CN − 254 is the potential retention of the soil (USDA, 1986). The equation was applied to every cell, so that the runoff of each cover and soil was found before it was averaged, rather than from a single mean curve number. The runoff coefficient is Q divided by P, and the runoff volume is Q times the area.</p>
      <p>The time of concentration was found from the length and the mean slope of the longest flow path with the Kirpich (1940) formula, and the lag time was taken as 0.6 times this value. Each storm was spread over 24 hours with the SCS Type II pattern in steps of 15 minutes, and the runoff of each step was turned into flow with the SCS dimensionless unit hydrograph (NRCS, 2007). The peak of the resulting hydrograph is the peak discharge. The same steps were repeated for each sub-catchment on its own.</p>

      <h3>Sensitivity to soil moisture</h3>
      <p>The 10-year storm was run again with the curve numbers converted to dry (I) and wet (III) soil conditions with the formulas of Chow et al. (1988), to show how much the runoff depends on rain that fell in the days before the storm.</p>

      <h2>5 Results</h2>
      <h3>Catchment and drainage network</h3>
      <p>The catchment covers 224.2 km² (Map 2). Its main stem is 46.5 km long from the outlet to its source near Mabvuku, and the streams draining 1 km² or more have a total length of 149.3 km. The network reaches the third Strahler order. Of the points along the mapped river, 91 % lay within 100 m of the derived main stem. The catchment was split into eight sub-catchments, from 11.2 km² (Glen Norah) to 67.0 km² (Waterfalls–Mbare). The largest is the lower main stem, which takes in Mbare, Southerton, Waterfalls and the industrial land south of the city centre.</p>
      <Fig src={map2} cap="Map 2. Drainage Network and Sub-Catchments Map, the streams by Strahler order and the eight sub-catchments." />

      <h3>Land cover, soil and curve numbers</h3>
      <p>Built-up land was the largest land cover class, at 39.9 % of the catchment, followed by tree cover (25.5 %), cropland (16.7 %) and grassland (14.5 %) (Map 3). Built-up land fills the centre and the west of the catchment, from the city centre through Mbare to Glen Norah and Glen View. Tree cover and grassland are found mainly in the low-density suburbs of the east and north, around Highlands, Greendale and Hatfield, and in the Mukuvisi Woodlands. Much of the cropland is small plots on open land along the rivers.</p>
      <Fig src={map3} cap="Map 3. Land Cover Map (2021)." />
      <p>The soils were remarkably uniform (Map 4). The mean sand content was 56.4 % and the mean clay content 26.4 %, so that 90.6 % of the catchment fell in the sandy clay loam texture and in soil group C. Clay loam and other clayey soils (group D, 6.4 %) were found mainly in the north-east, where they cover 41 % of the Eastlea–Highlands sub-catchment and 16 % of Greendale, and sandy loams (group A, 3.0 %) in small patches in the south and west. Soil group B was almost absent.</p>
      <Fig src={map4} cap="Map 4. Soil Clay Content Map, the mean clay content of the top 30 cm of the soil." />
      <p>Because the soil varies so little, the curve number follows the land cover closely (Map 5). The mean curve number of the catchment was 82.4. Values of 87 and above cover the built-up land and bare ground of the city centre, Mbare and the western suburbs, while values below 77 are found under the woodland of the east. By sub-catchment, the mean curve number ranged from 78.1 in Greendale to 87.0 in Glen Norah.</p>
      <Fig src={map5} cap="Map 5. Curve Number Map, for average soil moisture before a storm." />

      <h3>Design storms</h3>
      <p>The wettest day of each season averaged 44.1 mm over the catchment, with a standard deviation of 12.1 mm. It ranged from 26.2 mm to 68.6 mm, the largest falling on 8 March 2003. The fitted Gumbel distribution followed the annual maxima closely (Figure 1). It gave a 24-hour rainfall of 42.1 mm for the 2-year storm, 59.9 mm for the 10-year storm and 82.1 mm for the 100-year storm (Table 3).</p>
      <Fig src={fig1} cap="Figure 1. Annual maximum daily rainfall over the Mukuvisi catchment and the fitted Gumbel distribution." />

      <h3>Runoff and peak discharge at the outlet</h3>
      <p>The 2-year storm produced 13.2 mm of runoff over the catchment, about a third (0.31) of the rain that fell, and a volume of 2.95 million m³ (Table 3). The share of the rain that ran off grew with the size of the storm, to 0.42 for the 10-year storm and 0.51 for the 100-year storm, because the soil can hold only a fixed amount of water before the rest runs off. The 100-year storm sent 9.43 million m³ of water past the outlet.</p>
      <Table cap="Table 3. Design storms and runoff at the catchment outlet" head={["Return period (years)", "24-hour rainfall (mm)", "Runoff depth (mm)", "Runoff coefficient", "Runoff volume (million m³)", "Peak discharge (m³/s)"]} rows={T3} num={0}
        src="Source: this study. Catchment area 224.2 km²; average soil moisture before the storm." />
      <p>The longest flow path was 46.6 km long, with a mean slope of 0.5 %, which gave a time of concentration of 9.9 hours and a lag time of 6.1 hours. The peak discharge at the outlet was 74 m³/s for the 2-year storm, 145 m³/s for the 10-year storm and 246 m³/s for the 100-year storm (Figure 2). In each case the peak reached the outlet about 19 hours after the start of the storm, or about 7 hours after its heaviest rain. The 10-year peak is equal to 0.64 m³/s from every square kilometre of the catchment.</p>
      <Fig src={fig2} cap="Figure 2. Flood hydrographs at the catchment outlet for the 2-, 10- and 100-year storms." />

      <h3>Runoff across the catchment</h3>
      <p>Map 6 shows the runoff depth that the 10-year storm of 59.9 mm would produce on every cell. Runoff was low (under 20 mm) on 44.4 % of the catchment (99.7 km²), mainly under woodland and grassland, and high (30 mm or more) on 39.5 % (88.6 km²), almost all of it built-up land. Built-up land shed a mean of 35.2 mm, cropland 26.5 mm, grassland 18.3 mm and tree cover only 13.3 mm. High runoff forms an almost unbroken block from the city centre through Mbare, Southerton, Glen Norah and Glen View, while the low-density suburbs of the east appear as a mix of low and moderate runoff.</p>
      <Fig src={map6} cap="Map 6. 10-Year Storm Runoff Map, the runoff depth of a 24-hour storm of 59.9 mm." />
      <p>The same pattern shows by sub-catchment (Table 4, Figure 3). Glen Norah, the City Centre and Waterfalls–Mbare, where more than half of the land is built up, had runoff coefficients of 0.46 to 0.52 in the 10-year storm. Greendale, with 17 % built-up land and much woodland, had the lowest coefficient (0.32). Glen Norah produced the highest peak per square kilometre (2.22 m³/s), because it is both densely built and small, so that its water arrives at its outlet together. Waterfalls–Mbare produced the largest peak in total (84 m³/s), because of its size.</p>
      <Table cap="Table 4. Runoff from each sub-catchment" head={["Sub-catchment", "Area (km²)", "Curve number", "Built-up (%)", "Time of concentration (h)", "10-year runoff (mm)", "10-year runoff coefficient", "10-year peak (m³/s)", "10-year peak per km² (m³/s)", "100-year peak (m³/s)"]} rows={T4} num={1}
        src="Source: this study. Peaks are for each sub-catchment on its own and do not add up to the peak at the outlet, because they arrive at different times." />
      <Fig src={fig3} cap="Figure 3. Runoff coefficient of each sub-catchment in the 10-year storm, with its share of built-up land." />

      <h3>Sensitivity to soil moisture</h3>
      <p>The wetness of the soil before the storm changed the result more than any other factor (Table 5). If the 10-year storm fell on dry soil, the runoff would be 10.3 mm and the peak 55 m³/s. On soil already wet from earlier rain, it would be 39.1 mm and 231 m³/s, close to the peak of the 100-year storm on average soil. Late in the rainy season, when the soil is often wet, a storm of a given size is therefore much more dangerous than the same storm in November.</p>
      <Table cap="Table 5. Runoff from the 10-year storm under three soil moisture conditions" head={["Soil moisture before the storm", "Runoff depth (mm)", "Runoff coefficient", "Runoff volume (million m³)", "Peak discharge (m³/s)"]} rows={T5} num={1}
        src="Source: this study. 24-hour rainfall 59.9 mm; curve numbers converted with the formulas of Chow et al. (1988)." />

      <h2>6 Discussion</h2>
      <p>The catchment traced in this study agrees well with earlier work. Gumindoga et al. (2014) gave an area of 223.1 km² and a longest flow path of 44.7 km for the Mukuvisi catchment, against 224.2 km² and 46.5 km here, and most of the derived main stem lies within 100 m of the mapped river. The 30 m elevation model is therefore good enough to define the catchment and its main tributaries, though small streams in the flat, built-up parts of the city, where water follows drains and roads, will be less accurate.</p>
      <p>The results show that land cover, not soil, controls where runoff comes from in the Mukuvisi catchment. The soils are almost all sandy clay loams, so the difference between a curve number of 73 under woodland and 90 under houses comes from the land cover alone. Built-up land now covers about 40 % of the catchment, against about 25 % in 2008 (Gumindoga et al., 2014), and sheds almost three times as much water as woodland in the same storm. The western sub-catchments of Glen Norah, Waterfalls–Mbare and the City Centre, which hold most of the built-up land, are where flooding is most likely, and this matches the places where flooding is reported most often.</p>
      <p>The estimates have limits. The design storms are means over the whole catchment taken from satellite cells of about 5 km, and such data are known to smooth out the heaviest falls. The same Gumbel fit applied to the single wettest cell gave 86 mm for the 10-year storm and 119 mm for the 100-year storm, well above the catchment means, so the peaks given here should be taken as lower values. The SCS Type II pattern and the curve numbers of USDA (1986) were developed in the United States and have not been fitted to Zimbabwe. The built-up class of the land cover data does not separate the dense housing of Mbare from the large plots of the eastern suburbs, so all built-up land was given the curve number of 65 % impervious cover, which overstates runoff in the low-density suburbs and may understate it in the city centre. Water stored in the small dams of the catchment and the drains of the city were not modelled, and the results have not been tested against measured streamflow.</p>

      <h2>7 Recommendations</h2>
      <p>The City of Harare should give priority to drains and flood plain controls in the Glen Norah, Waterfalls–Mbare and City Centre sub-catchments, which produce the most runoff for every millimetre of rain. New building on the flood plain of the Mukuvisi and its tributaries in these areas should not be allowed.</p>
      <p>The woodland and open land of the east of the catchment, including the Mukuvisi Woodlands and the open land around Greendale and Hatfield, should be kept, since they hold back much of the rain that falls on them. New developments should be required to keep the runoff from their plots at the level it was before building, through soak pits, permeable paving and small detention ponds.</p>
      <p>The Zimbabwe National Water Authority and the Meteorological Services Department should set up a streamflow gauge near the outlet and recording rain gauges in the catchment, so that the curve numbers and the design storms can be checked against measured data. The analysis should be repeated with land cover that separates high-density and low-density housing.</p>

      <h2>8 Conclusion</h2>
      <p>The Mukuvisi catchment covers 224.2 km² and drains through a main stem of 46.5 km and eight sub-catchments. Its mean curve number is 82.4, set mainly by the 40 % of the catchment that is built up. A 10-year storm of 60 mm would produce about 25 mm of runoff, 5.6 million m³ of water and a peak of about 145 m³/s at the outlet, and a 100-year storm a peak of about 246 m³/s. Most of this water comes from the densely built western half of the catchment, where Glen Norah, the City Centre and Waterfalls–Mbare shed about half of the rain that falls on them. Wet soil before a storm could raise the peak by more than half again.</p>

      <h2>References</h2>
      <div className="tc__ref">
        <p>Bartos, M. (2020) pysheds: simple and fast watershed delineation in Python. Zenodo. <A href="https://doi.org/10.5281/zenodo.3822494" /></p>
        <p>Chow, V.T., Maidment, D.R. and Mays, L.W. (1988) Applied Hydrology. New York: McGraw-Hill.</p>
        <p>European Space Agency (2021) Copernicus Global Digital Elevation Model (GLO-30). <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
        <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
        <p>Gumbel, E.J. (1958) Statistics of Extremes. New York: Columbia University Press.</p>
        <p>Gumindoga, W., Rientjes, T.H.M., Shekede, M.D., Rwasoka, D.T. et al. (2014) Hydrological impacts of urbanization of two catchments in Harare, Zimbabwe. Remote Sensing, 6(12), 12544-12574. <A href="https://doi.org/10.3390/rs61212544" /></p>
        <p>Hengl, T., Miller, M.A.E., Križan, J., Shepherd, K.D. et al. (2021) African soil properties and nutrients mapped at 30 m spatial resolution using two-scale ensemble machine learning. Scientific Reports, 11, 6130. <A href="https://doi.org/10.1038/s41598-021-85639-y" /></p>
        <p>Kirpich, Z.P. (1940) Time of concentration of small agricultural watersheds. Civil Engineering, 10(6), 362.</p>
        <p>NRCS (2007) National Engineering Handbook, Part 630 Hydrology, Chapter 16: Hydrographs. Washington, DC: United States Department of Agriculture. <A href="https://directives.sc.egov.usda.gov/OpenNonWebContent.aspx?content=17755.wba" /></p>
        <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
        <p>OpenStreetMap contributors (2026) OpenStreetMap data for Harare, retrieved through the Overpass API. <A href="https://www.openstreetmap.org" /></p>
        <p>USDA (1986) Urban Hydrology for Small Watersheds. Technical Release 55. Washington, DC: Soil Conservation Service. <A href="https://www.nrcs.usda.gov/sites/default/files/2022-10/tr55.pdf" /></p>
        <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
      </div>
    </CaseLayout>
  );
}
