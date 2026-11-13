import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/mazowe-valley/map1_study_area.webp";
import map2 from "../assets/casestudies/mazowe-valley/map2_bare_2025.webp";
import map3 from "../assets/casestudies/mazowe-valley/map3_hotspot_years.webp";
import map4 from "../assets/casestudies/mazowe-valley/map4_hotspot_change.webp";
import map5 from "../assets/casestudies/mazowe-valley/map5_turbidity.webp";
import fig1 from "../assets/casestudies/mazowe-valley/fig1_reach_profile.webp";
import fig2 from "../assets/casestudies/mazowe-valley/fig2_sections.webp";
import fig3 from "../assets/casestudies/mazowe-valley/fig3_ndti.webp";

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

// Table 1: district, corridor ha, bare ha 2000, bare ha 2025, % 2000, % 2025
const T1: string[][] = [
  ["Mazowe", "10 322", "135.5", "152.5", "1.3", "1.5"],
  ["Bindura Rural", "12 319", "176.9", "158.0", "1.4", "1.3"],
  ["Shamva", "7 556", "64.3", "172.2", "0.9", "2.3"],
  ["Uzumba Maramba Pfungwe", "27 061", "776.9", "1 130.0", "2.9", "4.2"],
  ["Mudzi", "7 426", "370.9", "577.1", "5.0", "7.8"],
];

// Table 2: section, window, corridor %, background %
const T2: string[][] = [
  ["Upper (0 to 130 km)", "1.38", "1.57", "0.64", "0.86", "0.80", "0.52", "1.37", "1.31"],
  ["Middle (130 to 210 km)", "1.28", "0.20", "2.80", "1.08", "1.46", "0.14", "2.43", "0.23"],
  ["Lower (210 to 359 km)", "3.79", "0.12", "5.65", "1.25", "4.56", "0.09", "5.62", "0.18"],
];

// Table 3: NDTI section medians by year
const T3: string[][] = [
  ["2019", "−0.26", "−0.02", "0.00"], ["2020", "−0.14", "0.08", "0.03"], ["2021", "−0.23", "0.14", "0.13"],
  ["2022", "−0.23", "0.15", "0.17"], ["2023", "−0.23", "0.08", "0.09"], ["2024", "−0.24", "0.07", "0.04"],
  ["2025", "−0.17", "0.11", "0.15"],
];

const SRC = "Source: own analysis of Landsat Collection 2 Level 2 wet-season imagery in Google Earth Engine.";

export default function MazoweCaseStudy() {
  return (
    <>
      <CaseLayout slug="mazowe-valley">
        <h1>Assessing the Impact of Gold Mining on River Siltation in the Mazowe Valley from 2000 to 2025</h1>
        <p className="tc__by">Land disturbance and turbidity along 359 km of the Mazowe River.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (9 August 2026)</p>
        <Facts rows={[["Place", "Mazowe River, 359 km with a 1 km corridor"], ["Period", "2000 to 2025"], ["Data", "Landsat 5, 7, 8 and 9; Sentinel-2"], ["Methods", "Change detection, spectral index analysis (NDTI)"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>The Mazowe River rises north of Harare and flows north-east across Mashonaland Central and Mashonaland East into Mozambique, where it joins the Zambezi. Its catchment covers about 39 000 km² and holds Mazowe Dam, built in 1920 with a capacity of about 35 million m³ near Mazowe village (Wikipedia, 2025). The valley crosses one of the main gold belts of the country, and alluvial and river-bank gold mining has grown along it over the last two decades.</p>
        <p>Small-scale and artisanal miners now supply most of Zimbabwe's gold. Of the 36.5 t delivered to Fidelity Gold Refinery in 2024, about 65% came from small-scale and artisanal producers, and of 46.7 t in 2025 they delivered 34.9 t (Business Times, n.d.; 360 Mozambique, 2026). A University of Zimbabwe study found that artisanal gold mining had overtaken farming as the main source of livelihood in the Mazowe catchment (University of Zimbabwe, n.d.). In 2018 the Environmental Management Agency (EMA) reported that gold panning was rampant in Mazowe, Bindura and Mount Darwin districts and that rivers were polluted and silted, threatening downstream farming (The Herald, 2018).</p>
        <p>Government has responded several times. Chinese-owned operations were ordered off the Mazowe and other rivers in 2013 (NewsDay, 2013), river-bank mining was banned in September 2020, although firms with heavy equipment were reported to be defying the ban months later (The Standard, 2020a; 2020b), and alluvial mining was banned by Statutory Instrument 188 of 2024. In 2026 a state of disaster was declared over 17 degraded rivers, the Mazowe among them, through SI 91 of 2026, later extended (NewsDay, 2026; The Herald, 2026). The Centre for Natural Resource Governance warned that the declaration lets rehabilitation contractors recover minerals from the rivers they restore (CNRG, 2026).</p>
        <p>Field studies on the river are few and local. One sampled sediment at five points from Mazowe Dam to about 25 km downstream and found heavy metals, which it put down largely to informal mining, though it noted that its sample was small (Charema, 2024). No study was found that measures disturbance along the whole river. Satellite imagery was used here to do that for the 359 km of main stem inside Zimbabwe.</p>

        <h2>2 Objectives</h2>
        <p>The aim was to assess land disturbance and sediment along the Mazowe River from 2000 to 2025. The specific objectives were:</p>
        <ol>
          <li>To assess the extent and distribution of bare ground along the Mazowe River corridor in 2025.</li>
          <li>To analyse the change in bare ground along the corridor between 2000 and 2025, compared with the land away from the river.</li>
          <li>To examine river turbidity as an indicator of sediment along the river from 2019 to 2025.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>The study area is the main stem of the Mazowe River from its western end north of Harare to the Mozambique border, and the land within 1 km of it (Map 1). Measured along the OpenStreetMap river line, the main stem inside Zimbabwe is 358.6 km long. Some sources give a much shorter length of about 130 km; that figure could not be reconciled with the mapped course and was not used. The river passes through five districts: Mazowe, where it passes about 1 km from Mazowe village at 26 km; Bindura Rural, passing about 6 km from Bindura at 91 km; Shamva, passing about 9 km from Shamva town at 161 km; Uzumba Maramba Pfungwe (UMP), which holds the longest stretch; and Mudzi, before it leaves the country near 33.0° E.</p>
        <p>The upper river runs across the plateau north of Harare. Below Shamva it descends towards the Zambezi valley, and in UMP and Mudzi it flows in a wide sandy bed that is partly dry outside the rains.</p>
        <div><Fig src={map1} cap="Map 1. Study Area Map." /></div>

        <h2>4 Data and methods</h2>
        <p>The river line was taken from OpenStreetMap (relation 2638607), clipped to the national boundary and cut into 36 reaches of 10 km from the western end. Each reach was given a 1 km corridor on each side, with overlaps removed, giving a corridor of 64 683 ha, and each reach was assigned to the district holding most of its length. District boundaries came from OCHA (2023). Imagery was processed in Google Earth Engine and the maps and charts were made in Python.</p>
        <p>Bare ground was mapped from Landsat Collection 2 Level 2 surface reflectance (USGS, 2021): Landsat 5 and 7 for the 2000 and 2009 windows and Landsat 8 and 9 for 2017 and 2025. Cloud, cloud shadow and fill were masked with the quality band. Only images from November to April were used, because in the rainy season crops, grass and trees are green, and land that is still bare is most likely to be mined, eroded or sand. For each window the median NDVI of three rainy seasons was calculated, for example 2023/24 to 2025/26 for the 2025 window, and a pixel was classed as bare where the median NDVI was below 0.3. Pixels that were water (median wet-season MNDWI above 0; Xu, 2006) and built-up land in ESA WorldCover 2021 (Zanaga et al., 2022) were removed. The windows used 85, 119, 153 and 287 images.</p>
        <p>The steps for each objective are set out below, in the same order as the objectives.</p>
        <h3>Extent and distribution of bare ground</h3>
        <p>The bare area in the 2025 window was summed inside each reach corridor and expressed as a percentage of the corridor area, which was drawn as one graduated symbol per reach (Map 2). The same totals were summed by district (Table 1). Reach and district shares were counted from the pixels, not read from the map.</p>
        <h3>Change in bare ground</h3>
        <p>The bare area was calculated in the same way for the 2000, 2009 and 2017 windows. Because the share of bare land can change for reasons that have nothing to do with the river, such as drought or land clearing, each reach was compared with a background band from 1 km to 5 km from the river, with the overlaps between reaches removed (226 053 ha). The river was split into an upper (reaches 1 to 13), middle (14 to 21) and lower (22 to 36) section and the bare share of the corridor and of the background was calculated for each section and window (Table 2). A rise in the corridor that is not matched in the background was taken as a sign of disturbance on the river. The Shamva reach (reaches 14 to 17), where the rise was largest, was mapped at 30 m for each window, and the 2000 and 2025 windows were compared pixel by pixel inside the corridor. The three sites with the most new bare ground, each 5.4 km by 4.2 km, were enlarged for the maps (Map 3 and Map 4). Areas in Map 4 are approximate because the pixels were reprojected for display.</p>
        <h3>Turbidity</h3>
        <p>Turbidity was estimated from Sentinel-2 surface reflectance (ESA, 2015) with the normalised difference turbidity index, NDTI = (red − green) / (red + green) (Lacaux et al., 2007). Water with more suspended sediment reflects more red light, so the index rises with turbidity. Images from April to July with less than 40% cloud were used, after the main rains when the river still carries water, from 2019 to 2025. Only pixels classed as water in the Sentinel-2 scene classification were used. The median NDTI was calculated for each reach and year, and a reach was left out of a year when it had fewer than 20 water pixels. Map 5 shows the median of 2021 to 2025, and Table 3 the median of the reaches in each section by year. NDTI is a relative index and was not calibrated against field measurements of sediment.</p>
        <h3>Rainfall</h3>
        <p>Because bare ground and exposed sand both depend on rainfall, the November to April rainfall over the corridor was taken from CHIRPS version 2.0 (Funk et al., 2015) for each season in the four windows.</p>

        <h2>5 Results</h2>
        <h3>Extent and distribution of bare ground in 2025</h3>
        <p>In the 2025 window 2 190 ha of the corridor was bare in the rainy season (3.4% of its area). The share rises steadily downstream (Map 2, Figure 1). Twelve reaches had less than 2% bare, nearly all in the upper river between Mazowe and Bindura. Twelve had 2% to 4%, six had 4% to 6% and six more than 6%. The six highest reaches all lie below 270 km in UMP and Mudzi, with the highest share of 9.6% in reach 34 (330 to 340 km) near the Mozambique border.</p>
        <Fig src={map2} cap="Map 2. Bare Ground Along The Mazowe River Map (2025), share of each 10 km reach corridor bare in the rainy season." />
        <p>By district, Mudzi had the highest share at 7.8% and UMP the largest area at 1 130 ha, more than half of all bare ground in the corridor (Table 1). The corridor in Mazowe and Bindura Rural was 1.3% to 1.5% bare, and in Shamva 2.3%.</p>
        <p className="tc__cap">Table 1. Bare ground in the 1 km river corridor by district (2000 and 2025 windows)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>District</th><th className="n">Corridor (ha)</th><th className="n">Bare 2000 (ha)</th><th className="n">Bare 2025 (ha)</th><th className="n">Bare 2000 (%)</th><th className="n">Bare 2025 (%)</th></tr></thead>
            <tbody>
              <Rows rows={T1} num={1} />
              <tr className="t"><td>Corridor</td><td className="n">64 683</td><td className="n">1 524.5</td><td className="n">2 189.8</td><td className="n">2.4</td><td className="n">3.4</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">{SRC} Each reach assigned to the district holding most of its length.</p>
        <Fig src={fig1} cap="Figure 1. Bare ground in each 10 km reach corridor (2000 and 2025 windows)." />

        <h3>Change in bare ground from 2000 to 2025</h3>
        <p>Bare ground in the corridor rose from 1 525 ha in the 2000 window to 2 088 ha in 2009, fell to 1 629 ha in 2017 and rose again to 2 190 ha in 2025, a net rise of 665 ha or 44%. Over the same period bare ground in the background band moved from 0.64% to 0.58%, so the land away from the river shows no comparable rise.</p>
        <p>The three sections behave very differently (Table 2, Figure 2). In the upper section the corridor and the background had nearly the same share in every window (1.4% and 1.3% in 2025), so the river shows no excess of bare ground there. In the middle section the corridor share almost doubled, from 1.28% to 2.43%, while the background stayed at about 0.2%, so by 2025 the corridor was more than ten times barer than the land around it. In the lower section the corridor was already 3.8% bare in 2000, about 30 times the background, and it rose to 5.6% while the background stayed below 0.2%.</p>
        <p>The 2009 window stands apart. Its background share rose to about 1% in the middle and lower sections, five to ten times that of the other windows, and fell back by 2017. The window was built from Landsat 5 and 7 images, many carrying the Landsat 7 stripes, and a rise outside the corridor suggests that part of the 2009 increase comes from the imagery rather than the ground. The 2009 values are shown, but change is described from 2000 to 2025.</p>
        <p className="tc__cap">Table 2. Bare ground in the corridor and in the background band by section and window (% of area)</p>
        <div className="tc__tw">
          <table>
            <thead>
              <tr><th rowSpan={2}>Section</th><th className="n" colSpan={2}>2000</th><th className="n" colSpan={2}>2009</th><th className="n" colSpan={2}>2017</th><th className="n" colSpan={2}>2025</th></tr>
              <tr><th className="n">Corridor</th><th className="n">Background</th><th className="n">Corridor</th><th className="n">Background</th><th className="n">Corridor</th><th className="n">Background</th><th className="n">Corridor</th><th className="n">Background</th></tr>
            </thead>
            <tbody>
              <Rows rows={T2} num={1} />
              <tr className="t"><td>Whole river</td><td className="n">2.36</td><td className="n">0.64</td><td className="n">3.23</td><td className="n">1.08</td><td className="n">2.52</td><td className="n">0.25</td><td className="n">3.39</td><td className="n">0.58</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">{SRC} Corridor within 1 km of the main stem; background band 1 km to 5 km from it.</p>
        <Fig src={fig2} cap="Figure 2. Bare ground in the corridor (columns) and in the background band (black lines) by section and window." />
        <p>The largest rise relative to the starting point was in the Shamva reach, reaches 14 to 17 (130 to 170 km), where bare ground in the corridor grew from 35 ha to 143 ha, about four times. Reach 15 alone rose from 5 ha to 51 ha and reach 16 from 3 ha to 38 ha. Map 3 enlarges the site with the most new bare ground, Site A, about 148 km down the river, over the rainy season satellite image of each window. Bare ground in the corridor at this site was about 1 ha in 2000, 21 ha in 2009, 1 ha in 2017 and 51 ha in 2025. The 2009 patch lay on irrigated fields south of the river and was green again by 2017, while the largest 2025 patch lies on the river bank at the western end of the site, where the dry season image of 2025 shows disturbed ground. One smaller 2025 patch falls on a centre pivot field, which shows that the method detects bare ground of any cause and that farmland left bare is counted together with mining ground.</p>
        <Fig src={map3} cap="Map 3. Bare Ground Maps Shamva Reach Site A (2000–2025), over the rainy season Landsat image of each window, with the dry season image of 2025." />
        <p>Comparing the two windows pixel by pixel inside the corridor of the four reaches, about 134 ha became bare, about 29 ha that had been bare was vegetated again, and only about 5 ha was bare in both windows. Map 4 shows the three sites with the most new bare ground: Site A (about 148 km), Site B (160 km) and Site C (168 km) down the river. At Sites A and B the new bare ground forms compact patches on the banks, and at Site C it follows the channel, where some ground that was bare in 2000 is vegetated again.</p>
        <Fig src={map4} cap="Map 4. Bare Ground Change Maps Shamva Reach Sites (2000–2025), inside the 1 km corridor, over the 2025 satellite image in grey." />

        <h3>Turbidity along the river</h3>
        <p>River water was clearest in the upper section, where the median NDTI stayed between −0.26 and −0.14 in every year (Table 3, Figure 3). Below Bindura the index rises sharply. Of the 32 reaches with enough water pixels in 2021 to 2025, eight had a median above 0.15 and eight between 0.10 and 0.15 (Map 5). The most turbid stretch runs from reach 18 to reach 27 (170 to 270 km), through Shamva and UMP, where all ten reaches had medians from 0.11 to 0.19. Reach 13, just below Bindura, also had a high median of 0.19. Towards the border in Mudzi the index fell again to between 0.06 and 0.12.</p>
        <Fig src={map5} cap="Map 5. River Turbidity Map (2021–2025), median NDTI of water pixels in each 10 km reach, April to July." />
        <p>In the middle and lower sections the index was lowest in 2019 and 2020, at about 0 to 0.08, and highest in 2021 and 2022, at 0.13 to 0.17. It fell in 2023 and 2024 and rose again in 2025. The upper section showed no such pattern. The middle and lower river was therefore more turbid than the upper river in all seven years.</p>
        <p className="tc__cap">Table 3. Median turbidity index (NDTI) of the reaches in each section, April to July (2019 to 2025)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Year</th><th className="n">Upper</th><th className="n">Middle</th><th className="n">Lower</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: own analysis of Sentinel-2 L2A imagery. Reaches with fewer than 20 water pixels in a year left out.</p>
        <Fig src={fig3} cap="Figure 3. Median turbidity index (NDTI) of water pixels by section of the river (2019 to 2025)." />

        <h2>6 Discussion</h2>
        <p>The results support the reports of siltation on the Mazowe, but they show it is not spread evenly along the river. In the upper river around Mazowe and Bindura, where the press reported gold panning, the corridor is no barer than the land around it and the water is clear. That does not rule out mining there. Pits and panning sites smaller than a 30 m Landsat pixel, and sites in fields that were already bare, would go undetected, and the sediment study below Mazowe Dam found contamination even where nothing is visible from space (Charema, 2024). Mercury and other metals cannot be seen in this kind of imagery at all.</p>
        <p>The clearest signal is in the middle river around Shamva. There the corridor share doubled while the background did not change, the new bare ground lies in and along the channel, and from this stretch downstream the water is turbid. This is the pattern expected from river-bed and bank mining, which strips the banks and loosens sediment that is then carried downstream. It agrees with the reports of firms using heavy equipment on the river after the 2020 ban (The Standard, 2020b). The data do not show who caused the disturbance, and some of it may come from sand mining, bank erosion or cultivation of the river banks.</p>
        <p>The lower river needs more careful reading. Most of its bare ground is sand in a wide, partly dry channel that was already 30 times barer than the background in 2000, and much of that is simply the natural form of a sandy lowveld river. Its rise from 3.8% to 5.6% fits sand being deposited in the channel, but rainfall fell too. Mean November to April rainfall over the corridor dropped from about 1 026 mm in the 2000 window to 664 mm in the 2025 window, and drier seasons leave more sand exposed. The rise in the lower river cannot therefore be put down to siltation alone. The middle section is less affected, because its background held steady through the same drop in rainfall.</p>
        <p>The turbidity results should also be read with care. NDTI is a relative index, and in narrow or shallow channels a 10 m pixel may mix water with sand or bank, which raises the index. The sharp step in turbidity below Bindura and the high values through Shamva and UMP match the bare-ground results, but field sampling of suspended sediment would be needed to turn the index into concentrations. The national figures reported by EMA on degraded riverine land also disagree with one another, so no direct comparison with official totals was possible.</p>

        <h2>7 Recommendations</h2>
        <p>Enforcement of the 2024 ban on alluvial mining and the 2026 rehabilitation programme should give priority to the middle river from Shamva to the UMP border (130 to 210 km), where disturbance of the corridor grew most and the water became turbid, rather than spreading effort evenly along the river.</p>
        <p>Rehabilitation contracts under the state of disaster should be monitored with repeated satellite measurements like those in this study, reach by reach, so that any new disturbance caused by contractors recovering minerals can be detected, as CNRG has warned.</p>
        <p>EMA and the Zimbabwe National Water Authority should set up fixed sampling points for suspended sediment and metals at Mazowe Dam, Bindura, Shamva and the Mozambique border, to calibrate the turbidity index and to measure what is carried across the border.</p>
        <p>Further work should use higher resolution imagery to map individual mining sites, and should repeat this analysis each year, separating the effect of rainfall from that of mining by comparing the corridor with the background band.</p>

        <h2>8 Conclusion</h2>
        <p>All three objectives were met. In the rainy seasons of 2023/24 to 2025/26 the 1 km corridor of the Mazowe River was 3.4% bare, rising from under 2% in the upper river to more than 6% in UMP and Mudzi, and UMP held over half of the bare area. Bare ground in the corridor rose by 44% from 2000 to 2025, while the land 1 km to 5 km away did not change. The rise was clearest around Shamva, where the corridor share doubled and bare ground in reaches 14 to 17 grew about four times, mostly in the river bed and on its banks. In the lower river the rise is partly explained by lower rainfall exposing more sand. The water was clear in the upper river and turbid from Bindura downstream, most of all from Shamva through UMP. The strongest evidence of mining-related disturbance and siltation is therefore on the middle Mazowe, and that is where the response should begin.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>360 Mozambique (2026) Zimbabwe gold production exceeded 2025 target with deliveries over 46 tons. <A href="https://360mozambique.com/world/africa/zimbabwe-gold-production-exceeded-2025-target-with-deliveries-over-46-tons/" /></p>
          <p>Business Times (n.d.) Gold deliveries to Fidelity surge. <A href="https://businesstimes.co.zw/gold-deliveries-to-fidelity-surge/" /></p>
          <p>Charema (2024) MSc research report on heavy metals in sediment of the Mazowe River downstream of Mazowe Dam, University of the Witwatersrand, Johannesburg. <A href="https://wiredspace.wits.ac.za/items/e3fa5ad5-5f8d-4524-bcf5-17506e4eb4dc" /></p>
          <p>CNRG (2026) River rehabilitation disaster declaration could open door to mining abuses. Centre for Natural Resource Governance. <A href="https://cnrgzim.org/news/river-rehabilitation-disaster-declaration-could-open-door-to-mining-abuses/" /></p>
          <p>ESA (2015) Sentinel-2 user handbook. European Space Agency. <A href="https://sentinel.esa.int/documents/247904/685211/Sentinel-2_User_Handbook" /></p>
          <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D., Verdin, J., Shukla, S., Husak, G., Rowland, J., Harrison, L., Hoell, A. and Michaelsen, J. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
          <p>Lacaux, J.P., Tourre, Y.M., Vignolles, C., Ndione, J.A. and Lafaye, M. (2007) Classification of ponds from high-spatial resolution remote sensing: application to Rift Valley Fever epidemics in Senegal. Remote Sensing of Environment, 106(1), 66–74. <A href="https://doi.org/10.1016/j.rse.2006.07.012" /></p>
          <p>NewsDay (2013) Govt cracks whip on Chinese. 21 October 2013. <A href="https://www.newsday.co.zw/2013/10/21/govt-cracks-whip-chinese" /></p>
          <p>NewsDay (2026) Masuka hails swift national disaster action on river degradation. <A href="https://www.newsday.co.zw/news/article/200056150/masuka-hails-swift-national-disaster-action-on-river-degradation" /></p>
          <p>OCHA (2023) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
          <p>OpenStreetMap contributors (2026) Mazowe River, relation 2638607. <A href="https://www.openstreetmap.org/relation/2638607" /></p>
          <p>The Herald (2018) Gold panning wreaks havoc in Mashonaland Central. 19 February 2018. <A href="https://www.pressreader.com/zimbabwe/the-herald-zimbabwe/20180219/281724090025999" /></p>
          <p>The Herald (2026) HE extends state of disaster on rivers. <A href="https://www.heraldonline.co.zw/he-extends-state-of-disaster-on-rivers/" /></p>
          <p>The Standard (2020a) The case and curse of Mazowe River. 27 September 2020. <A href="https://thestandard.co.zw/2020/09/27/the-case-and-curse-of-mazowe-river" /></p>
          <p>The Standard (2020b) VP brother name dropped as foreign firms defy govt ban on river bank mining. 27 December 2020. <A href="https://thestandard.co.zw/2020/12/27/vp-brother-name-dropped-as-foreign-firms-defy-govt-ban-on-river-bank-mining" /></p>
          <p>University of Zimbabwe (n.d.) Thesis on artisanal gold mining and livelihoods in the Mazowe catchment. UZ Institutional Repository, handle 10646/3460. <A href="https://ir.uz.ac.zw/handle/10646/3460" /></p>
          <p>USGS (2021) Landsat Collection 2 Level 2 science products. United States Geological Survey. <A href="https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products" /></p>
          <p>Wikipedia (2025) Mazowe River. <A href="https://en.wikipedia.org/wiki/Mazowe_River" /></p>
          <p>Xu, H. (2006) Modification of normalised difference water index (NDWI) to enhance open water features in remotely sensed imagery. International Journal of Remote Sensing, 27(14), 3025–3033. <A href="https://doi.org/10.1080/01431160600589179" /></p>
          <p>Zanaga, D. et al. (2022) ESA WorldCover 10 m 2021 v200. Zenodo. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
