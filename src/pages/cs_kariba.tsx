import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/kariba/map1_study_area.webp";
import map2 from "../assets/casestudies/kariba/map2_extent.webp";
import map3 from "../assets/casestudies/kariba/map3_exposed.webp";
import map4 from "../assets/casestudies/kariba/map4_bed_elevation.webp";
import map5 from "../assets/casestudies/kariba/map5_retreat.webp";
import fig1 from "../assets/casestudies/kariba/fig1_level.webp";
import fig2 from "../assets/casestudies/kariba/fig2_annual.webp";
import fig3 from "../assets/casestudies/kariba/fig3_area_level.webp";
import fig4 from "../assets/casestudies/kariba/fig4_storage.webp";

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
  ["DAHITI water level altimetry, Lake Kariba", "Point series", "1992 to 2026", "Lake level (2 080 readings)"],
  ["Landsat 5, 7, 8 and 9 Collection 2 surface reflectance", "30 m", "2000 to 2025", "Lake area in the high and low seasons"],
  ["JRC Global Surface Water 1.4 occurrence", "30 m", "1984 to 2021", "Filling cloud gaps, lake outline, drawdown zone"],
  ["Copernicus GLO-30 digital elevation model", "30 m", "2011 to 2015", "Relief on the study area map"],
  ["Zambezi River Authority lake levels and storage", "Daily bulletins", "2024 to 2026", "Datum check and storage check"],
  ["LSIB international boundaries", "Lines", "2017", "Zambia and Zimbabwe border"],
];

// Table 2: lake level, area and storage in the first and last decades
const T2: string[][] = [
  ["Mean level (m)", "483.17", "479.39", "−3.78"],
  ["Mean annual maximum (m)", "485.20", "481.55", "−3.65"],
  ["Mean annual minimum (m)", "481.49", "476.94", "−4.55"],
  ["Lake area at the mean level (km²)", "5 041", "4 742", "−299"],
  ["Live storage at the mean level (km³)", "36.3", "17.8", "−18.5"],
  ["Live storage at the mean level (% full)", "56.5", "27.7", "−28.8"],
  ["Live storage at the mean annual minimum (km³)", "28.0", "6.4", "−21.6"],
];

// Table 3: area, elevation and storage
const T3: string[][] = [
  ["475.5 (minimum operating level)", "4 435", "0", "0"],
  ["477", "4 553", "6.74", "10.5"],
  ["479", "4 712", "16.01", "24.9"],
  ["481", "4 870", "25.59", "39.8"],
  ["483", "5 028", "35.49", "55.2"],
  ["485", "5 186", "45.70", "71.0"],
  ["487", "5 344", "56.23", "87.4"],
  ["488.5 (maximum regulated level)", "5 463", "64.33", "100"],
];

// Table 4: validation against the Zambezi River Authority
const T4: string[][] = [
  ["Live storage at 480.19 m (1 November 2026)", "21.53 km³", "21.67 km³", "+0.7 %"],
  ["Per cent full at 480.19 m (1 November 2026)", "33.22", "33.68", "+0.46 points"],
  ["Per cent full at 479.98 m (10 November 2026)", "31.67", "32.12", "+0.45 points"],
  ["Per cent full at 476.67 m (10 November 2025)", "8.09", "8.15", "+0.06 points"],
  ["Live storage between 475.5 and 488.5 m", "64.8 km³", "64.33 km³", "−0.7 %"],
  ["Lake area at the maximum regulated level", "5 580 km²", "5 463 km²", "−2.1 %"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function KaribaCaseStudy() {
  return (
    <>
      <CaseLayout slug="lake-kariba">
        <h1>Area–Elevation–Storage Relationships and Water Level Decline at Lake Kariba (2000 to 2025)</h1>
        <p className="tc__by">Satellite altimetry paired with Landsat lake areas to build the storage curve.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (12 November 2026)</p>
        <Facts rows={[["Place", "Lake Kariba"], ["Period", "2000 to 2025"], ["Data", "DAHITI altimetry, Landsat, JRC surface water, Copernicus DEM"], ["Methods", "Satellite altimetry, surface water extraction (MNDWI), area–elevation–storage curve fitting"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Lake Kariba is the reservoir behind Kariba Dam on the Zambezi River, shared by Zambia and Zimbabwe. Water released through the dam's two power stations supplies a large part of the electricity used in both countries. When the lake falls towards its minimum operating level, the Zambezi River Authority has to cut the water allocated to the power stations. In December 2023 it reduced the allocation for 2024 from 30 to 16 billion m³, with 8 billion m³ for each country (ZRA, 2023).</p>
        <p>Knowing how much water is left means turning the level into a volume. For that, the area–elevation–storage relationship of the lake is needed: how its area and stored volume change as the level rises and falls. Here the relationship was built from satellite data alone, by pairing lake levels from satellite altimetry with lake areas mapped from images taken at the same time. The curve was then used to turn 26 years of levels into storage and to show how much of the lake bed was left dry as the level fell.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To analyse the change in the water level of Lake Kariba from 2000 to 2025 against its operating range.</li>
          <li>To derive the area–elevation relationship of the lake from paired altimetry levels and satellite water areas.</li>
          <li>To estimate the storage–elevation curve and validate it against the storage reported by the operator.</li>
          <li>To assess the lake bed left dry by the decline and the retreat of the shoreline.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Lake Kariba lies in the middle Zambezi valley and runs about 270 km from the south-west, near Binga, to Kariba Dam in the north-east (Map 1). The border between Zambia and Zimbabwe follows the old course of the river along the lake, so about 45 % of the lake lies in Zambia and 55 % in Zimbabwe. The dam was completed in 1959 (ZRA, 2026a). At its maximum regulated level the lake covers about 5 580 km² and holds about 185 km³, most of which lies below the minimum operating level and cannot be used for power (ZRA, 2026b). The usable range is 475.5 to 488.5 m above sea level (ZRA, 2026c). Kariba and Siavonga stand by the dam and Binga and Sinazongwe lie on the southern and northern shores.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p className="tc__cap">Table 1. Data used in the study</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: Schwatke et al. (2015); USGS (2020); Pekel et al. (2016); ESA (2021); ZRA (2026c, 2026d); US Department of State (2017). Landsat, surface water and elevation data were processed in Google Earth Engine (Gorelick et al., 2017).</p>

        <h3>Water level and its datum</h3>
        <p>Satellite altimeters measure the height of the water surface each time they pass over the lake. The level series used here combines several missions and has 1 827 readings between 2000 and 2025. Altimetry heights refer to a different datum from the dam's own gauge. On three dates with both, the altimetry level was 0.35 to 0.47 m below the gauge, so the mean difference of 0.41 m was added to every reading and all levels given here are on the gauge datum. Readings were averaged by month to show the seasonal cycle and the annual minimum and maximum levels were taken from the full series.</p>

        <h3>Lake area and the area–elevation curve</h3>
        <p>Lake area was mapped in two windows each year, the high season (April to June) and the low season (October to December). Every Landsat pixel with a modified normalised difference water index (MNDWI) above 0 was taken as water. Clouds and the Landsat 7 stripes leave gaps and these were filled using long-term water occurrence (Zhao and Gao, 2018). For each map, the occurrence level that best separates the observed water from the observed land was found and the lake was taken as every pixel at or above that level. Small dams and river reaches outside the lake were removed. Each area was paired with the median level in the same window. One window, the low season of 2025, was too hidden to use, which left 51 pairs. A straight line and a curve were fitted to these and the curve would only have been kept if it cut the error by more than 5 %.</p>

        <h3>Storage–elevation curve and validation</h3>
        <p>Live storage is the volume of water above the minimum operating level. It was found by adding up thin slices of the lake, each 0.01 m thick, using the area from the fitted line at each level: V(h) = ∫ A(z) dz from 475.5 m to h. The result was compared with the storage and per cent full that the Zambezi River Authority published for three dates and with its stated area at the maximum regulated level.</p>

        <h3>Dried lake bed and shoreline retreat</h3>
        <p>The lake outline at the highest level (high season 2000) and at the lowest level (low season 2024) were taken from the occurrence levels found for those two windows. The ground under water in 2000 but dry in 2024 is the dried lake bed. To show the shape of that ground, each occurrence level was given the lake level at which the fitted line gives the same area. This places the drawdown zone on a rough bed elevation surface. For the retreat, the distance from every 60 m cell on the 2000 shoreline to the nearest water at the 2024 low was measured.</p>

        <h2>5 Results</h2>
        <h3>Water level change</h3>
        <p>The lake stood at its highest, 487.60 m, on 21 May 2000 and at its lowest, 475.53 m, on 26 December 2022 (Figure 1). Each year the level rises once the rains reach the upper Zambezi and falls through the dry season, with a median rise and fall of 4.0 m. Beneath this cycle the lake dropped by about 0.28 m a year on average. It came within 1.5 m of the maximum regulated level in 2010 to 2013 and again in 2018, but after 2014 it never stayed up for long. The mean level of 2016 to 2025 was 3.78 m below that of 2000 to 2009 (Table 2).</p>
        <p>The annual minimum fell further than the annual maximum (Figure 2). From 2000 to 2014 the lowest level of each year never went below 477.7 m. From 2022 to 2025 it reached 475.5 to 475.7 m every year, within 0.2 m of the minimum operating level and in each of those years the lake spent one to three months less than 1 m above that level.</p>
        <Fig src={fig1} cap="Figure 1. Monthly mean level of Lake Kariba with its operating range (2000 to 2025)." />
        <Fig src={fig2} cap="Figure 2. Annual maximum and minimum level of Lake Kariba (2000 to 2025)." />
        <p className="tc__cap">Table 2. Lake level, area and live storage in the first and last decades</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Measure</th><th>2000 to 2009</th><th>2016 to 2025</th><th>Change</th></tr></thead>
            <tbody><Rows rows={T2} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Area and storage come from the curves in Table 3.</p>

        <h3>Area–elevation relationship</h3>
        <p>Lake area and level fall close to a straight line (Figure 3): Area = 79.05 h − 33 153, where h is the level in metres and the area is in km². The line explains 97.6 % of the variation in area, with a typical error of 41 km², under 1 % of the lake. A curve did not beat it by more than 5 %, so the line was kept. Each metre of level adds or removes about 79 km² of water and over the operating range the lake grows from 4 435 km² at 475.5 m to 5 463 km² at 488.5 m (Table 3). Map 2 shows the lake at its 2024 low and the bed that dried up after the high of 2000, mostly along shallow shores and bays.</p>
        <Fig src={fig3} cap="Figure 3. Lake area against lake level with the fitted line, 51 seasons (2000 to 2025)." />
        <Fig src={map2} cap="Map 2. Lake Kariba Extent Map (2000 and 2024), water at the 2024 low and the lake bed dried since 2000." />

        <h3>Storage–elevation curve</h3>
        <p>Live storage between 475.5 and 488.5 m is 64.3 km³ (Table 3, Figure 4). The lake is wider near the top of the range, so the top metre holds about 5.4 km³ and the lowest metre 4.5 km³. At the mean level of 2000 to 2009 the lake held 36.3 km³ of live storage (57 % full). At the mean level of 2016 to 2025 it held 17.8 km³ (28 % full), roughly half. At the low of December 2022 only 0.13 km³ was left above the minimum operating level and at the low of December 2024, 0.8 km³ (1.2 %).</p>
        <p className="tc__cap">Table 3. Area, elevation and live storage of Lake Kariba</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Level (m)</th><th>Area (km²)</th><th>Live storage (km³)</th><th>Live storage (% full)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Live storage is the volume above 475.5 m.</p>
        <p>The curve agrees closely with the operator's figures (Table 4). At 480.19 m on 1 November 2026, the authority reported 21.53 km³ of live storage and 33.22 % full and the curve gives 21.67 km³ and 33.68 %. On the other two dates, per cent full differs by less than half a point. The authority's figures imply a live storage of 64.8 km³ (21.53 km³ ÷ 33.22 %), close to the 64.3 km³ found here. The area at the maximum regulated level comes out 2.1 % below the authority's 5 580 km², because the line is fitted to levels that rarely reached the top of the range.</p>
        <Fig src={fig4} cap="Figure 4. Live storage curve of Lake Kariba with the storage reported by the operator." />
        <p className="tc__cap">Table 4. Validation against the Zambezi River Authority</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Check</th><th>Operator</th><th>This study</th><th>Difference</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: ZRA (2026b, 2026d); this study. The 2025 and 2026 checks lie after the study period and were not used to fit the curves.</p>

        <h3>Dried lake bed and shoreline retreat</h3>
        <p>Between the high of 2000 and the low of 2024 the lake shrank from 5 357 km² to 4 506 km² on the 60 m grid, leaving 850 km² of lake bed dry, 461 km² in Zimbabwe and 389 km² in Zambia. Map 3 shows three of the shores that lost the most. In a 28 by 18 km window around the eastern bays of Kariba District, 83 km² dried out. The Binga District shore lost 82 km² and the Sinazongwe shore of Zambia 64 km². In each long arms of the lake reaching into river valleys were left as dry ground.</p>
        <Fig src={map3} cap="Map 3. Dried Lake Bed Map (2000 to 2024), close views of three shores." />
        <p>Map 4 shows the bed elevation of the drawdown zone around the eastern basin. The flat floors of the bays and river mouths dry out first and over the widest area, while the steep shores of the main basin barely change. Nearly all the ground between 475.5 and 485 m lies in these shallow bays and that is why the low years of 2022 to 2025 exposed so much bed for each metre of fall.</p>
        <Fig src={map4} cap="Map 4. Drawdown Zone Bed Elevation Map, the lake level at which each part of the eastern basin falls dry." />
        <p>Along most of the lake the shoreline moved only a short way (Map 5). The median retreat was 300 m and 47 % of the 2000 shoreline moved less than 250 m. Retreat was greater on the Zimbabwe side (median 339 m) than on the Zambia side (247 m). Still, 7.7 % of the shoreline moved more than 2 km and 10 % more than 1.7 km, mostly at the heads of long bays. The largest retreat, 8.4 km, was in a bay on the southern shore of Binga District.</p>
        <Fig src={map5} cap="Map 5. Shoreline Retreat Map, distance from the 2000 shoreline to the water at the 2024 low." />

        <h2>6 Discussion</h2>
        <p>The lake has lost a large share of its usable water. A 3.8 m fall in mean level between the first and last decades looks small next to a lake about 100 m deep at the dam, but nearly all of it comes out of the 13 m operating range. Live storage at the mean level halved and from 2022 the lake hit the minimum operating level at the end of every dry season. The cuts in water for power fit this. The 2024 allocation was set in December 2023, when the level was only a few tenths of a metre above the minimum (ZRA, 2023). The level series shows the decline but not what caused it. Lower inflow from the upper Zambezi in dry years and the water released for power both play a part and separating them would need inflow and release records.</p>
        <p>With a straight line between area and level, the storage is simple to compute and easy to check. The line holds because the main basin has steep sides and most of the change in area happens in the bays, at a steady rate per metre. The close match with the authority's storage on dates after the study period shows that satellite data alone can track the live storage of a large reservoir to within about 1 %. There are limits. The altimetry series has gaps of several weeks. The occurrence data end in 2021, so later lake outlines rest on older patterns. The bed elevation map comes from how often each place was wet, not from a survey and it says nothing about the dead storage below 475.5 m. A 60 m grid also blurs narrow inlets.</p>

        <h2>7 Recommendations</h2>
        <ol>
          <li>Use the storage curve in Table 3 to report the live storage of Lake Kariba from altimetry levels alone, and update the curve each year as new pairs are added.</li>
          <li>Plan power allocations around the low-season level, since that is where the decline has been greatest and where the lake now meets its operating limit.</li>
          <li>Map the dried bays in Map 3 and Map 4 for land use and grazing on the newly dry ground, and take care that new uses do not block the lake when it refills.</li>
          <li>Add inflow and release records to separate the effects of drought and of water use on the decline.</li>
        </ol>

        <h2>8 Conclusion</h2>
        <p>Pairing satellite altimetry with satellite water areas gives a straight area–elevation line for Lake Kariba (Area = 79.05 h − 33 153, R² 0.976) and a live storage of 64.3 km³ between 475.5 and 488.5 m, within about 1 % of the operator's figures. The lake fell by about 0.28 m a year from 2000 to 2025. Its mean live storage halved between the first and last decades and from 2022 it reached the minimum operating level every year. The decline left 850 km² of lake bed dry, mostly in shallow bays, where the shoreline retreated by as much as 8.4 km.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Pekel, J.-F., Cottam, A., Gorelick, N. and Belward, A.S. (2016) High-resolution mapping of global surface water and its long-term changes. Nature, 540, 418-422. <A href="https://doi.org/10.1038/nature20584" /></p>
          <p>Schwatke, C., Dettmering, D., Bosch, W. and Seitz, F. (2015) DAHITI, an innovative approach for estimating water level time series over inland waters using multi-mission satellite altimetry. Hydrology and Earth System Sciences, 19, 4345-4364. <A href="https://doi.org/10.5194/hess-19-4345-2015" /></p>
          <p>US Department of State (2017) Large Scale International Boundaries (LSIB), simplified. Office of the Geographer.</p>
          <p>USGS (2020) Landsat Collection 2 Level-2 Science Products. United States Geological Survey. <A href="https://doi.org/10.5066/P9OGBGM6" /></p>
          <p>Zhao, G. and Gao, H. (2018) Automatic correction of contaminated images for assessment of reservoir surface area dynamics. Geophysical Research Letters, 45, 6092-6099. <A href="https://doi.org/10.1029/2018GL078343" /></p>
          <p>ZRA (2023) Press statement: water allocation at Kariba Dam, 28 December 2023. Zambezi River Authority, Lusaka. <A href="https://www.zambezira.org/sites/default/files/Press%20Statement%20-%20Water%20allocation%20at%20Kariba%20Dam_28%20December%202023_Final.pdf" /></p>
          <p>ZRA (2026a) Kariba Dam timeline. Zambezi River Authority. <A href="https://www.zambezira.org/media-centre/kariba-dam-timeline" /></p>
          <p>ZRA (2026b) Kariba hydro-electric scheme technical data. Zambezi River Authority. <A href="https://www.zambezira.org/hydro-electric-schemes/kariba-hes/kariba-hes-technical-data" /></p>
          <p>ZRA (2026c) Lake levels. Zambezi River Authority. <A href="https://www.zambezira.org/hydrology/lake-levels" /></p>
          <p>ZRA (2026d) Kariba reservoir data. Zambezi River Authority. <A href="https://www.zambezira.org/hydrology/kariba-reservoir-data" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
