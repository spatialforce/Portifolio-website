import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/sugarcane/map1_fields.webp";
import map2 from "../assets/casestudies/sugarcane/map2_vigour.webp";
import map3 from "../assets/casestudies/sugarcane/map3_weak.webp";
import fig1 from "../assets/casestudies/sugarcane/fig1_series.webp";
import fig2 from "../assets/casestudies/sugarcane/fig2_harvest.webp";
import fig3 from "../assets/casestudies/sugarcane/fig3_years.webp";

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

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

const DATA: string[][] = [
  ["Sentinel-2 L2A surface reflectance", "20 m", "Jan 2019 to Dec 2025", "Monthly median NDVI and NDMI"],
  ["Sentinel-2 scene classification layer", "20 m", "Jan 2019 to Dec 2025", "Cloud and shadow masking"],
  ["CHIRPS v2.0 rainfall", "about 5 km", "Jul 2018 to Dec 2025", "Monthly and seasonal rainfall"],
];

// Year by year, from out/stats.json and out/fig_stats.json
const YEARS: string[][] = [
  ["2019", "384", "0.795", "0.230", "73"],
  ["2020", "472", "0.785", "0.225", "80"],
  ["2021", "759", "0.775", "0.219", "80"],
  ["2022", "436", "0.775", "0.224", "78"],
  ["2023", "402", "0.767", "0.206", "66"],
  ["2024", "434", "0.793", "0.198", "71"],
  ["2025", "708", "0.800", "0.201", "80"],
];

// weak_counts in out/fig_stats.json
const WEAK: string[][] = [
  ["0", "1 084", "55.7"],
  ["1 – 2", "756", "38.8"],
  ["3 – 4", "101", "5.2"],
  ["≥ 5", "6", "0.3"],
  ["Total", "1 947", "100.0"],
];

export default function SugarcaneCaseStudy() {
  return (
    <>
      <CaseLayout slug="sugarcane-triangle">
        <h1>Field-Level Sugarcane Monitoring at Triangle and Hippo Valley Using Remote Sensing (2019 to 2025)</h1>
        <p className="tc__by">Seven years of monthly satellite greenness and moisture, followed field by field.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (15 December 2025)</p>
        <Facts rows={[["Place", "Triangle and Hippo Valley estates"], ["Period", "2019 to 2025, monthly"], ["Data", "Sentinel-2, 20 m"], ["Methods", "Vegetation index time series (NDVI, NDMI), zonal statistics"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Sugarcane is the main irrigated crop of Zimbabwe's south-eastern lowveld and most of it is grown on the estates around Triangle and Hippo Valley in Chiredzi District. Lowveld rainfall is low and unreliable, so the crop depends almost entirely on irrigation. An estate covers many thousands of hectares and trouble in single fields, such as poor water supply, old ratoons or late replanting, is hard to spot without regular field visits.</p>
        <p>Optical satellite images give a regular, low-cost record of crop condition. Sentinel-2 passes over the area every five days at 10 to 20 m resolution (Drusch et al., 2012) and two indices derived from it can follow growth, harvest and water stress through the season: greenness (NDVI; Tucker, 1979) and canopy water content (NDMI; Gao, 1996). A seven-year record of these images was applied here to the Triangle and Hippo Valley estates. Two questions were asked. Can the cane fields and their harvest calendar be recovered from the images alone and can fields that stay weaker than the rest year after year be picked out?</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To assess whether irrigated sugarcane fields can be delineated from a monthly remote sensing time series without field records.</li>
          <li>To analyse the seasonal cycle of cane greenness and canopy moisture in relation to rainfall.</li>
          <li>To examine the timing of harvest across the estates.</li>
          <li>To compare cane condition between years against the rainfall of each season.</li>
          <li>To evaluate differences in vigour between and within fields and identify fields that are persistently weak.</li>
        </ol>

        <h2>3 Study area and data</h2>
        <p>The study covers a box from 31.33 to 31.80° E and 20.93 to 21.19° S, about 49 by 29 km. The box includes the Triangle and Hippo Valley estates and the smaller cane schemes around them.</p>
        <p>Seasonal rainfall (July to June) over the box averaged 514 mm in the seven seasons studied. It ranged from 384 mm in 2018/19 to 759 mm in 2020/21. The months from June to October received only 30 to 69 mm in each year.</p>
        <p>The data used are listed in Table 1. All processing of the satellite images took place in Google Earth Engine (Gorelick et al. 2017). The field analysis was done in Python.</p>
        <p className="tc__cap">Table 1. Data used in the study</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Resolution</th><th>Period</th><th>Use</th></tr></thead>
            <tbody><Rows rows={DATA} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: Drusch et al. (2012); Funk et al. (2015).</p>

        <h2>4 Methodology</h2>
        <h3>Image compositing</h3>
        <p>Cloud and cloud shadow were removed from every scene with the scene classification layer. Only pixels classed as vegetation, bare soil, water or snow were kept. The remaining pixels were reduced to a monthly median at 20 m, giving 84 monthly images from January 2019 to December 2025.</p>
        <p>NDVI was computed from the red and near-infrared bands. NDMI was computed from the near-infrared and shortwave infrared bands. After masking 99.6 % of the monthly values over the cane had a clear observation. The remaining gaps were filled by linear interpolation between neighbouring months.</p>

        <h3>Cane identification and field delineation</h3>
        <p>Cane was separated from natural vegetation and other crops by how it behaves over time, not by a single image. A pixel was classed as cane when it met three conditions. It had to be strongly green in the dry season (NDVI above 0.6), when the surrounding bush has died back, in at least five of the seven years. It had to show at least three harvest-like drops, meaning a fall in NDVI to below 0.35 within three months of a value above 0.6; this rules out riverine woodland, which stays green but is never cut. And it had to have a clear value in more than 40 % of months.</p>
        <p>Cane pixels were then grouped into fields with the graph-based segmentation of Felzenszwalb and Huttenlocher (2004), applied to the seven-year NDVI series. Neighbouring pixels that shared the same growth and harvest rhythm formed one field. Segments smaller than 5 ha were discarded.</p>

        <h3>Seasonal cycle</h3>
        <p>For each month, the mean NDVI and NDMI of every field were calculated. These were averaged across all fields, weighted by field area. The resulting series was compared with monthly rainfall over the study box.</p>

        <h3>Harvest timing</h3>
        <p>A field was recorded as harvested in the first month in which its mean NDVI fell below 0.35, provided it had been above 0.6 in the preceding three months. This gives at most one harvest month per field per year. The harvested area in each month was summed for each year and averaged over the seven years.</p>

        <h3>Inter-annual comparison</h3>
        <p>Two values were computed for each year. Peak NDVI is the area-weighted mean of the highest monthly NDVI of each field in that year. Dry-season NDMI is the mean NDMI of standing cane (NDVI above 0.5) from August to October, the driest months, when leaf moisture depends on irrigation.</p>
        <p>Both values were compared with the rainfall of the preceding season (July to June) using Pearson's correlation coefficient. A linear trend was fitted to the dry-season NDMI series.</p>

        <h3>Field vigour and persistent weakness</h3>
        <p>The seven annual peaks of each field were averaged to give a mean peak NDVI. Fields were grouped into five classes at intervals of 0.02. Variation within fields was measured as the coefficient of variation of the pixel values inside each field.</p>
        <p>A single poor year can follow a late harvest or a replant, so on its own it does not mean lasting weakness. To tell the two apart, the fields whose peak NDVI fell in the lowest 10 % of all fields were flagged in each year. A field flagged in five or more of the seven years was classed as persistently weak.</p>

        <h2>5 Results</h2>
        <h3>Cane fields</h3>
        <p>The method delineated 1 947 cane fields covering 16 272 ha (Map 1). The median field size is 7.0 ha and 80 % of fields lie between 5.3 and 11.7 ha (10th to 90th percentile). The field outlines follow the estate blocks visible in the images.</p>
        <p>The 16 272 ha is cane that was harvested regularly over the period. The classification rules exclude land that was fallow or under replanting for long stretches.</p>
        <Fig src={map1} cap="Map 1. Sugarcane fields delineated from the remote sensing record, 2019 to 2025." />

        <h3>Seasonal cycle of greenness and moisture</h3>
        <p>The cane follows the same cycle in every year (Figure 1). Area-weighted NDVI is highest in March or April, at about 0.72 and lowest in August or September, at about 0.44. NDMI follows the same pattern at lower values.</p>
        <p>The seasonal low comes in the harvest season, not at the end of the rains. Harvested fields drop to bare stubble while uncut fields stay green, which pulls down the area-weighted mean. Most rain falls from November to February, yet the cane goes on greening after the rains end, so growth is being kept up by irrigation.</p>
        <Fig src={fig1} cap="Figure 1. Area-weighted NDVI and NDMI of the cane fields (top) and monthly rainfall (bottom), January 2019 to December 2025." />

        <h3>Harvest timing</h3>
        <p>Harvesting starts in May, peaks in September with an average of 2 238 ha cut and tails off through November (Figure 2). May to November accounts for 94.5 % of the harvested area. In every month the spread between the lowest and highest year is small, so the harvest calendar barely changes from year to year.</p>
        <p>In any one year between 66 % and 80 % of fields showed a harvest (Table 2). The rest were replanted or left on a longer cycle. Some may have been cut and regrown within a single month, in which case the monthly composite would miss the drop.</p>
        <Fig src={fig2} cap="Figure 2. Area harvested by month, mean of 2019 to 2025, with the lowest and highest year." />

        <h3>Differences between years</h3>
        <p>Cane condition differed little from year to year (Table 2, Figure 3). Peak NDVI ranged from 0.767 in 2023 to 0.800 in 2025. Dry-season NDMI declined from 0.230 in 2019 to 0.198 in 2024 and 0.201 in 2025, a fitted trend of about −0.0055 per year.</p>
        <p>Neither value was related to seasonal rainfall. The correlation with rainfall is 0.12 for peak NDVI and −0.21 for dry-season NDMI. The wettest season, 2020/21 with 759 mm, did not give the greenest cane and dry-season NDMI stayed low in 2025 despite 708 mm of rain.</p>
        <p className="tc__cap">Table 2. Annual values for the cane fields, 2019 to 2025</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Year</th><th className="n">Rain, preceding season (mm)</th><th className="n">Peak NDVI</th><th className="n">Dry-season NDMI</th><th className="n">Fields harvested (%)</th></tr></thead>
            <tbody><Rows rows={YEARS} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; Funk et al. (2015). Rain is the total from July of the previous year to June. Peak NDVI is the area-weighted mean of field peaks.</p>
        <Fig src={fig3} cap="Figure 3. Peak NDVI and dry-season NDMI of the cane by year, with the rainfall of the preceding season under each year." />

        <h3>Field vigour</h3>
        <p>Mean peak NDVI varies little between fields (Map 2). The median is 0.785 and 90 % of fields lie between 0.753 and 0.817. In total 184 fields average below 0.76 and 68 above 0.82. The lowest and highest fields are scattered across the estates instead of grouped in one area. That points to causes acting field by field, such as cane age, variety and water delivery, more than to soil or climate gradients across the area.</p>
        <p>Variation inside fields is low as well. The median within-field coefficient of variation of peak NDVI is 3.1 % and 90 % of fields are below 4.4 %. The pixels furthest from their field mean lay along field margins, roads and canals, where a 20 m pixel mixes cane with other surfaces and they did not form coherent patches. At 20 m the fields look uniform, so no management zones within fields could be defined. That would need the 10 m bands or drone imagery.</p>
        <Fig src={map2} cap="Map 2. Mean peak NDVI of each field, 2019 to 2025." />

        <h3>Persistently weak fields</h3>
        <p>Most low years were one-offs (Table 3, Map 3). Over half of the fields (1 084) never ranked in the lowest 10 % and another 756 did so in only one or two years. A smaller group of 101 fields ranked low in three or four years. Six fields, covering 42.2 ha, ranked low in five of the seven years and are classed as persistently weak.</p>
        <p>The mean peak NDVI of the six persistently weak fields is 0.726 to 0.740, against the median of 0.785 for all fields. Four of the six lie in the west of the study area, between 31.41 and 31.47° E.</p>
        <p className="tc__cap">Table 3. Fields by number of years in the lowest 10 % for peak NDVI</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Years in lowest 10 %</th><th className="n">Fields</th><th className="n">Share of fields (%)</th></tr></thead>
            <tbody><Rows rows={WEAK} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study.</p>
        <Fig src={map3} cap="Map 3. Number of years each field ranked in the lowest 10 % for peak NDVI, 2019 to 2025. Persistently weak fields are circled." />

        <h2>6 Discussion</h2>
        <p>A free, cloud-masked satellite record turns out to be enough to monitor these estates field by field. The time-based rules found the cane without any field map and the segmentation gave fields of a realistic size. The clear lowveld skies help. Almost every month was observed, so harvests could be dated to the month and the seasonal cycle followed without gaps.</p>
        <p>A weak link between cane condition and rainfall is what a fully irrigated system should show. Peak greenness and the harvest calendar held steady across seasons with 384 to 759 mm of rain. The drop in dry-season NDMI since 2023 is therefore unlikely to come from local rainfall. Changes in irrigation supply or scheduling, or in the age of the cane, are more likely. Seven years is too short to tell these apart and no irrigation data were available to test them.</p>
        <p>There are several limitations. NDVI and NDMI describe the canopy, not yield and no mill or field yield records were available to check them against. Monthly composites date harvests only to the month, so a field cut and regrown within one month may be missed. The classification rules leave out land that was fallow or being replanted for long periods, so the cane area is a lower bound. The field outlines also come from the images rather than estate records and two neighbouring fields with the same planting history may have been merged into one.</p>

        <h2>7 Recommendations</h2>
        <ol>
          <li>Prioritise the six persistently weak fields for field inspection, followed by the 101 fields that ranked low in three or four years.</li>
          <li>Compare the decline in dry-season NDMI since 2023 with irrigation delivery and scheduling records for the same period.</li>
          <li>Validate peak NDVI against mill delivery or field yield records, so that the index can be expressed as expected yield.</li>
          <li>Use 10 m satellite bands or drone surveys where variation within fields needs to be assessed.</li>
        </ol>

        <h2>8 Conclusion</h2>
        <p>From a seven-year monthly satellite record, 1 947 sugarcane fields covering 16 272 ha were identified at Triangle and Hippo Valley without any field records. The cane follows a steady yearly cycle set by irrigation and the cutting calendar, with harvest running from May to November and peaking in September.</p>
        <p>Cane condition changed little between years and did not follow seasonal rainfall, though dry-season canopy moisture has been lower since 2023. At 20 m the fields are uniform inside and differ only slightly from one another. Six fields, covering 42.2 ha, were among the weakest tenth in five of the seven years and they are the clearest places to check on the ground.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Drusch, M., Del Bello, U., Carlier, S., Colin, O. et al. (2012) Sentinel-2: ESA's optical high-resolution mission for GMES operational services. Remote Sensing of Environment, 120, 25-36. <A href="https://doi.org/10.1016/j.rse.2011.11.026" /></p>
          <p>Felzenszwalb, P.F. and Huttenlocher, D.P. (2004) Efficient graph-based image segmentation. International Journal of Computer Vision, 59(2), 167-181. <A href="https://doi.org/10.1023/B:VISI.0000022288.19776.77" /></p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations: a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>Gao, B.-C. (1996) NDWI: a normalized difference water index for remote sensing of vegetation liquid water from space. Remote Sensing of Environment, 58(3), 257-266. <A href="https://doi.org/10.1016/S0034-4257(96)00067-3" /></p>
          <p>Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S. et al. (2017) Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, 202, 18-27. <A href="https://doi.org/10.1016/j.rse.2017.06.031" /></p>
          <p>Tucker, C.J. (1979) Red and photographic infrared linear combinations for monitoring vegetation. Remote Sensing of Environment, 8(2), 127-150. <A href="https://doi.org/10.1016/0034-4257(79)90013-0" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
