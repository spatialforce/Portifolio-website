import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/rainfall-interpolation/map1_study_area.webp";
import map2 from "../assets/casestudies/rainfall-interpolation/map2_surfaces.webp";
import map3 from "../assets/casestudies/rainfall-interpolation/map3_cv_errors.webp";
import map4 from "../assets/casestudies/rainfall-interpolation/map4_agreement.webp";
import map5 from "../assets/casestudies/rainfall-interpolation/map5_uncertainty.webp";
import fig1 from "../assets/casestudies/rainfall-interpolation/fig1_semivariogram.webp";
import fig2 from "../assets/casestudies/rainfall-interpolation/fig2_cv_errors.webp";
import fig3 from "../assets/casestudies/rainfall-interpolation/fig3_observed_estimated.webp";
import fig4 from "../assets/casestudies/rainfall-interpolation/fig4_elevation.webp";

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
  ["GHCN-Monthly v2 station precipitation", "68 gauges, merged to 65 points", "1961 to 1990", "Mean annual rainfall at each gauge"],
  ["Copernicus DEM GLO-30", "Resampled to 500 m", "2011 to 2015", "Gauge elevation where none was recorded, and relief on Map 1"],
  ["CHIRPS v2.0 monthly rainfall", "0.05° (about 5 km)", "1981 to 2024", "Independent check of the surfaces"],
  ["FAO AQUASTAT long-term mean rainfall", "National figure", "Long-term mean", "Check of the national mean"],
  ["OCHA administrative boundaries", "Areas", "2020", "National border, provinces and districts"],
];

const T2 = [
  ["Inverse distance weighting", "Power 1, 1.5, 2, 2.5, 3, 4", "153.6, 135.7, 125.4, 123.0, 124.2, 126.7", "Power 2.5"],
  ["Ordinary kriging", "Spherical, exponential, Gaussian", "117.0, 116.9, 131.1", "Exponential"],
  ["Universal kriging", "Spherical, exponential, Gaussian", "116.2, 119.7, 116.8", "Spherical"],
  ["Thin-plate spline", "Smoothing 0 to 1 000", "116.6 to 117.8", "Smoothing 30"],
];

const T3 = [
  ["Inverse distance weighting", "10.6", "71.4", "123.0", "16.9", "0.592", "95.2"],
  ["Ordinary kriging", "4.4", "64.7", "116.9", "16.1", "0.631", "85.3"],
  ["Universal kriging", "4.8", "68.9", "116.2", "16.0", "0.636", "89.0"],
  ["Thin-plate spline", "4.9", "67.6", "116.6", "16.1", "0.633", "94.5"],
];

const T4 = [
  ["Inverse distance weighting", "697.2", "333", "1 630", "2.2", "36.3", "40.4", "19.1", "2.0"],
  ["Ordinary kriging", "688.9", "336", "1 611", "4.0", "38.7", "38.9", "16.2", "2.2"],
  ["Universal kriging", "688.9", "339", "1 579", "5.0", "39.4", "29.8", "23.4", "2.5"],
  ["Thin-plate spline", "683.3", "318", "1 825", "6.9", "37.2", "36.1", "16.6", "3.1"],
];

const T5 = [
  ["Inverse distance weighting", "0.824", "+51.7", "72.2"],
  ["Ordinary kriging", "0.835", "+43.3", "65.0"],
  ["Universal kriging", "0.781", "+43.4", "76.5"],
  ["Thin-plate spline", "0.796", "+37.7", "69.7"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function InterpolationCaseStudy() {
  return (
    <CaseLayout slug="rainfall-interpolation">
      <h1>Comparison of Spatial Interpolation Methods for Mean Annual Rainfall in Zimbabwe: Inverse Distance Weighting, Kriging and Thin-Plate Splines</h1>
      <p className="tc__by">Four ways of turning rain gauge records into a national rainfall map, tested against the gauges themselves and against satellite estimates.</p>
      <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (13 November 2026)</p>
      <Facts rows={[["Place", "Zimbabwe"], ["Period", "Rainfall normals 1961 to 1990"], ["Data", "GHCN-Monthly, Copernicus DEM, CHIRPS, FAO AQUASTAT"], ["Methods", "Inverse distance weighting, ordinary and universal kriging, thin-plate spline, leave-one-out cross-validation"]]} />

      <h2>1 Introduction</h2>
      <p>Rainfall is measured at points, but planners, farmers and water managers need it for every place. Maps of mean annual rainfall are used to zone land for farming, to size dams and to judge drought risk and in Zimbabwe they underlie the agro-ecological regions that guide land use. Turning a set of gauge readings into a continuous map requires spatial interpolation, the estimation of values at unmeasured places from the values at measured ones.</p>
      <p>Many interpolation methods exist and the same gauges can give quite different maps depending on which one is used. Simple methods weight nearby gauges by distance alone. Geostatistical methods first model how rainfall varies with distance and then use that model to weight the gauges (Isaaks and Srivastava, 1989). Reviews have found that no single method is best everywhere and that the result depends on how dense the gauges are and on the shape of the rainfall field (Goovaerts, 2000; Li and Heap, 2011). Four common methods were therefore compared here on one set of Zimbabwean gauges, to see how much the choice of method matters and where the maps can be trusted.</p>

      <h2>2 Objectives</h2>
      <ol>
        <li>To describe the rain gauge network and the spatial structure of mean annual rainfall in Zimbabwe.</li>
        <li>To generate mean annual rainfall surfaces with inverse distance weighting, ordinary kriging, universal kriging and a thin-plate spline.</li>
        <li>To compare the accuracy of the four methods by leave-one-out cross-validation.</li>
        <li>To assess where the four surfaces agree and where the estimates are most uncertain.</li>
        <li>To evaluate the surfaces against independent satellite rainfall estimates and the published national mean.</li>
      </ol>

      <h2>3 Study area</h2>
      <p>Zimbabwe is a landlocked country of about 391 000 km² in southern Africa, between about 15.6° S and 22.4° S and 25.2° E and 33.1° E (Map 1). Most of the country is a plateau, with a central watershed above 1 200 m running from the south-west to the north-east. The land falls to the Zambezi valley in the north and the Limpopo and Save lowlands in the south and south-east and rises to more than 2 500 m in the Eastern Highlands along the border with Mozambique.</p>
      <p>Almost all rain falls in a single season from November to March. Rainfall is highest in the Eastern Highlands, where moist air from the Indian Ocean is forced upward and lowest in the south and south-west, near the Limpopo. The country is divided into five natural regions, from Region I, with more than 1 000 mm a year, to Region V, with less than 450 mm and the class limits used on the maps below follow these broad bands.</p>
      <Fig src={map1} cap="Map 1. Study Area Map, showing elevation, the 65 rain gauges and the province boundaries." />

      <h2>4 Data and methods</h2>
      <p>The data used are listed in Table 1. Monthly rainfall at gauges was taken from the Global Historical Climatology Network, version 2 (Vose et al., 1992). The period 1961 to 1990 was chosen because it is the last standard period with many gauges reporting in Zimbabwe. Satellite rainfall estimates from CHIRPS (Funk et al. 2015) and the national mean published by FAO AQUASTAT were kept aside and used only to check the results. All distances were measured on an equal-area projection centred on Zimbabwe and the surfaces were computed on a grid of 0.025° (about 2.7 km).</p>
      <Table cap="Table 1. Data used in the study" head={["Dataset", "Resolution", "Period", "Use"]} rows={T1} num={9}
        src="Source: Vose et al. (1992); European Space Agency (2021); Funk et al. (2015); FAO (2024); OCHA (2020)." />

      <h3>Gauge network and spatial structure</h3>
      <p>For each gauge, the mean rainfall of each calendar month was taken over the years with a complete record. A gauge was kept only if every month had at least 20 years of data and the twelve monthly means were then added to give the mean annual rainfall. Sixty-eight gauges passed. Three pairs stood at the same location, in Harare, Mutare and Mvuma and each pair was merged by taking its mean, which left 65 points. The distance from each gauge to its nearest neighbour was measured to describe how evenly the network covers the country.</p>
      <p>Spatial structure was described in three ways. The correlation of rainfall with elevation, longitude and latitude showed whether rainfall follows the land or a regional trend. Global Moran's I (Moran, 1950), with weights equal to the inverse of distance and 9 999 random permutations, tested whether nearby gauges have more similar rainfall than distant ones. The experimental semivariogram, half the mean squared difference between pairs of gauges in distance classes of 25 km up to 400 km, showed how the difference grows with distance (Matheron, 1963).</p>

      <h3>Interpolation methods</h3>
      <p>Inverse distance weighting estimates each place as a weighted mean of the gauges, with weights equal to one over the distance raised to a power (Shepard, 1968). The power sets how quickly the influence of a gauge falls away.</p>
      <p>Ordinary kriging also uses a weighted mean, but the weights are chosen from a model of the semivariogram so that the expected error is as small as possible and has a mean of zero (Isaaks and Srivastava, 1989). Spherical, exponential and Gaussian models were fitted to the experimental semivariogram by weighted least squares, with each distance class weighted by its number of pairs. Universal kriging adds a trend in the east–west and north–south directions. The trend was fitted by least squares, the semivariogram was modelled on what was left after the trend was removed and the trend and the local estimate were then solved together (Cressie, 1993).</p>
      <p>The thin-plate spline fits the smoothest surface that passes close to all the gauges, in the sense of least bending (Wahba, 1990; Hutchinson, 1995). A smoothing value lets the surface miss the gauges slightly to avoid sharp bends.</p>
      <p>The setting of each method was chosen by cross-validation, as described below. The settings tested are listed in Table 2.</p>

      <h3>Cross-validation</h3>
      <p>Each gauge was removed in turn, its rainfall was estimated from the other 64 with the same method and the estimate was compared with the observed value. Accuracy was summarised by the mean error (bias), the mean absolute error, the root mean square error and the coefficient of determination (R²). The test was repeated without the wettest gauge, Inyanga Downs, which lies far above all others and separately for gauges with close neighbours and those with distant ones, split at the median nearest-neighbour distance.</p>

      <h3>Agreement and uncertainty</h3>
      <p>For every grid cell, the difference between the highest and the lowest of the four estimates was computed. This shows where the choice of method changes the map most. The kriging standard error, which is the expected error of the universal kriging estimate given by the semivariogram model, was mapped as a second measure of uncertainty. Each was placed in three simple classes so that the maps can be read without technical training.</p>

      <h3>Independent checks</h3>
      <p>The four surfaces were compared cell by cell with the mean annual rainfall from satellite estimates for 1981 to 2024, using the correlation, the mean difference and the mean absolute difference, all weighted by cell area. The area-weighted national mean of each surface was also compared with the published national mean of 657 mm. Because the satellite period is later than the gauge period, this check tests the pattern and the general level rather than exact values.</p>

      <h2>5 Results</h2>
      <h3>Gauge network and spatial structure</h3>
      <p>The 65 gauges had a median record of 28 years per month and stood between 421 m and 1 830 m above sea level. Mean annual rainfall ranged from 333 mm at Beitbridge, on the Limpopo, to 1 631 mm at Inyanga Downs in the Eastern Highlands. The mean was 726 mm and the median 739 mm, with a coefficient of variation of 26.7 %. The gauges were not spread evenly (Map 1). They cluster around Harare and in the east and thin out in the west and on the lowlands. The median distance to the nearest gauge was 33 km and the largest, at Gwaai in the north-west, was 128 km.</p>
      <p>Rainfall rose with elevation (Figure 1). The correlation was 0.59 and on average rainfall rose by about 37 mm for every 100 m. Rainfall rose almost as strongly towards the east (r = 0.60) and the north (r = 0.56). A plane fitted to these two directions alone explained 57 % of the variation in rainfall, at about 0.58 mm per kilometre towards the east and 0.59 mm per kilometre towards the north. Moran's I was 0.235, against an expected value of −0.016 with no pattern and the result was highly significant (p = 0.0001), so nearby gauges had more similar rainfall than distant ones.</p>
      <Fig src={fig4} cap="Figure 1. Mean annual rainfall and elevation at the 65 rain gauges." />
      <p>The semivariogram of the raw values kept rising up to 400 km and did not level off (Figure 2), which is what a regional trend produces. Once the trend was removed, the variance fell from 37 074 to 16 045 mm² and the semivariogram of what was left levelled off at a range of about 123 km, with a small nugget of 471 mm². Beyond about 120 km, then, gauges carry little information about each other once the regional slope is known.</p>
      <Fig src={fig1} cap="Figure 2. Experimental semivariograms of mean annual rainfall and the fitted models, for the raw values and for the values after the trend was removed." />

      <h3>Rainfall surfaces</h3>
      <p>The tuning chose a power of 2.5 for inverse distance weighting, the exponential model for ordinary kriging, the spherical model for universal kriging and a smoothing value of 30 for the spline (Table 2). For both kriging methods and the spline, the error changed by less than 1 % across most of the settings tested, but for inverse distance weighting a power of 1 gave an error 25 % higher than the best power.</p>
      <Table cap="Table 2. Settings tested for each method and the cross-validation error of each" head={["Method", "Settings tested", "Root mean square error (mm)", "Setting chosen"]} rows={T2} num={9}
        src="Source: this study. Errors from leave-one-out cross-validation at 65 gauges." />
      <p>All four surfaces show the same broad pattern: rainfall above 800 mm on the north-eastern plateau, above 1 000 mm in the Eastern Highlands and below 450 mm along the Limpopo (Map 2). The differences are in the detail. Inverse distance weighting draws rings around single gauges that are wetter or drier than their neighbours, as in the south-west and the south-east. The two kriging surfaces and the spline are smoother. Universal kriging carries the wetter band further across the north and its trend pushes a strip along the western border below 450 mm, where no gauges hold it back. The spline had the widest range, from 318 mm to 1 825 mm and its highest value is about 190 mm above the wettest gauge.</p>
      <Fig src={map2} cap="Map 2. Mean Annual Rainfall by Interpolation Method, 1961 to 1990, with the national mean and the cross-validation error of each surface." />
      <p>The national means of the four surfaces lay within 14 mm of one another, from 683 mm to 697 mm (Table 3). The share of the country in each rainfall class differed more. Universal kriging placed 23.4 % of the country in the 800 to 1 000 mm class, against 16.2 % to 19.1 % for the others and the spline placed 6.9 % below 450 mm, against 2.2 % for inverse distance weighting.</p>
      <Table cap="Table 3. Summary of the four rainfall surfaces" head={["Method", "National mean (mm)", "Lowest (mm)", "Highest (mm)", "< 450 mm (%)", "450–650 mm (%)", "650–800 mm (%)", "800–1 000 mm (%)", "≥ 1 000 mm (%)"]} rows={T4} num={1}
        src="Source: this study. Means are weighted by cell area over a land area of 392 860 km²." />

      <h3>Accuracy of the methods</h3>
      <p>The three methods other than inverse distance weighting were close in accuracy (Table 4, Figure 3). Their root mean square errors were 116.2 mm to 116.9 mm, about 16 % of the mean rainfall and they explained 63 % to 64 % of the variation between gauges. Ordinary kriging had the smallest mean absolute error, 64.7 mm and the smallest bias, 4.4 mm. Inverse distance weighting was the least accurate on every measure, with a root mean square error of 123.0 mm and a bias of 10.6 mm, so it tended to overestimate.</p>
      <Table cap="Table 4. Leave-one-out cross-validation results" head={["Method", "Mean error (mm)", "Mean absolute error (mm)", "Root mean square error (mm)", "Error as % of mean", "R²", "Root mean square error without Inyanga Downs (mm)"]} rows={T3} num={1}
        src="Source: this study. 65 gauges; mean observed rainfall 725.8 mm. Mean error is estimate minus observed." />
      <Fig src={fig2} cap="Figure 3. Mean absolute error and root mean square error of each method in cross-validation." />
      <p>Much of the error came from one gauge. Inyanga Downs, at 1 830 m, receives 1 631 mm, yet when it was left out all four methods put it at between 981 mm and 1 072 mm, short by more than 550 mm (Map 3, Figure 4). Without this gauge the root mean square errors fell to between 85 mm and 95 mm and ordinary kriging pulled clearly ahead at 85.3 mm. Other large errors were also in the east. Wet gauges next to the Eastern Highlands were underestimated and their drier neighbours a short distance away were overestimated. Over most of the plateau, errors stayed within 50 mm.</p>
      <Fig src={map3} cap="Map 3. Cross-Validation Error Map, the error of ordinary kriging at each gauge when that gauge was left out." />
      <Fig src={fig3} cap="Figure 4. Observed and estimated mean annual rainfall at each gauge for the four methods." />
      <p>Gauge spacing had a small effect. For gauges with distant neighbours, the mean absolute error of universal kriging and the spline rose by about 4 mm to 7 mm compared with gauges with close neighbours, while that of ordinary kriging did not rise at all. No method was best at every gauge. Inverse distance weighting and ordinary kriging each gave the closest estimate at 19 gauges, universal kriging at 14 and the spline at 13.</p>

      <h3>Agreement and uncertainty</h3>
      <p>The four methods agreed to within 50 mm over 60 % of the country (Map 4). They differed by 50 mm to 100 mm over 23 % and by 100 mm or more over 17 %. Agreement was best over the densely gauged central and north-eastern plateau. The largest differences, of up to 643 mm, were in the Eastern Highlands, where rainfall changes sharply over short distances and along the borders in the north-west, the Zambezi valley and the south-east, where the surfaces are extrapolated beyond the last gauges.</p>
      <Fig src={map4} cap="Map 4. Method Agreement Map, the difference between the highest and the lowest of the four estimates." />
      <p>The kriging standard error told a similar story (Map 5). It was low (under 75 mm) on 16 % of the country, close to the gauges, moderate (75 mm to 100 mm) on 38 % and high (100 mm or more) on 46 %, mostly in the west, the north-west and along the borders. The mean standard error was 98 mm for universal kriging and 110 mm for ordinary kriging, so taking out the trend cut the expected error by about a tenth.</p>
      <Fig src={map5} cap="Map 5. Estimation Uncertainty Map, the standard error of universal kriging in three classes." />

      <h3>Independent checks</h3>
      <p>All four surfaces followed the pattern of the satellite estimates closely, with correlations of 0.78 to 0.84 (Table 5). Ordinary kriging matched best, with the highest correlation and the smallest mean absolute difference, 65.0 mm. Universal kriging matched least well, partly because of its low values along the western border. All four surfaces were wetter than the satellite estimates, by 38 mm to 52 mm on average. The gauges themselves were 22 mm wetter than the satellite estimates at the same places, with a correlation of 0.97, so part of the difference lies between the two data sources and the two periods rather than in the methods.</p>
      <Table cap="Table 5. Comparison of the surfaces with satellite rainfall estimates" head={["Method", "Correlation", "Mean difference (mm)", "Mean absolute difference (mm)"]} rows={T5} num={1}
        src="Source: this study; Funk et al. (2015). Satellite national mean 645.6 mm (1981 to 2024). Differences are surface minus satellite, weighted by cell area." />
      <p>The national means of the surfaces, 683 mm to 697 mm, were 4 % to 6 % above the published national mean of 657 mm and 6 % to 8 % above the satellite mean of 646 mm.</p>

      <h2>6 Discussion</h2>
      <p>The three methods that model either the semivariogram or a smooth surface gave nearly the same accuracy and inverse distance weighting was clearly worse. This matches Goovaerts (2000) and the review by Li and Heap (2011), who found that kriging usually beats inverse distance weighting when the gauges are reasonably dense and the rainfall field has a clear structure. Here the gap was about 6 % in root mean square error and 10 % in mean absolute error. Inverse distance weighting also drew rings around single gauges, which a reader could easily take for real wet or dry spots.</p>
      <p>Universal kriging was expected to gain most from the strong east–west and north–south trend and it did lower the kriging standard error. Its cross-validation accuracy was still no better than that of ordinary kriging and its straight-line trend carried the low rainfall of the south-west into the far north-west, where no gauge could correct it. A trend fitted to the gauges needs care at the edges of a network. The semivariogram of the raw values had no clear sill, which points to a trend. Ordinary kriging coped because, over the distances that matter for each estimate, the trend is close to a straight slope that the method can follow.</p>
      <p>The largest errors came from the Eastern Highlands, where rainfall depends on height and on exposure to the wind and where a single gauge such as Inyanga Downs is much wetter than any gauge around it. None of the four methods uses elevation, so none can reproduce such a local peak. Since rainfall rose by about 37 mm for every 100 m, a method that uses elevation as a second variable, such as kriging with an external drift or a spline with elevation (Hutchinson, 1995), would probably improve the east.</p>
      <p>The work has limits. The gauge normals end in 1990 and fewer gauges have reported since then, so the surfaces describe the late twentieth century and not the present. The independent check uses a later period, so it tests the pattern rather than exact values. The west and the north-west have few gauges and none of the methods was tested there, so the high uncertainty shown on Maps 4 and 5 should be taken at face value. Cross-validation measures how well each gauge is estimated from the others, which is a fair test where gauges are dense, but it says little about places far from any gauge.</p>

      <h2>7 Recommendations</h2>
      <p>Mapping agencies that need a national mean rainfall map from gauges should use ordinary kriging or a thin-plate spline rather than inverse distance weighting and should publish the kriging standard error or a similar measure beside the map so that users can see where it is least reliable.</p>
      <p>Where a regional trend is used, as in universal kriging, the trend should be checked at the edges of the network and limited where it runs beyond the gauges. For the Eastern Highlands, elevation should be added as a second variable and the map should not be read in detail there without local gauge data.</p>
      <p>The Meteorological Services Department should give priority to new or restored gauges in the west and north-west, in the Zambezi valley and along the south-eastern border, where the methods disagree most and the uncertainty is highest. Open release of recent gauge records would allow the comparison to be repeated for a current period and the satellite estimates to be corrected against the ground.</p>

      <h2>8 Conclusion</h2>
      <p>Four interpolation methods were applied to mean annual rainfall at 65 gauges in Zimbabwe for 1961 to 1990. Rainfall rose towards the east and north and with elevation and it was clearly clustered. Ordinary kriging, universal kriging and the thin-plate spline were almost equally accurate, with errors of about 116 mm or 16 % of the mean. Inverse distance weighting was less accurate and drew rings around single gauges. Of the four, ordinary kriging was the most consistent, with the smallest bias and mean absolute error and the closest match to satellite estimates. The maps agreed to within 50 mm over 60 % of the country. Method mattered most in the Eastern Highlands and at the edges of the network and there more gauges and the use of elevation would improve the map more than a change of method.</p>

      <h2>References</h2>
      <div className="tc__ref">
        <p>Cressie, N. (1993) Statistics for Spatial Data. Revised edn. New York: Wiley.</p>
        <p>European Space Agency (2021) Copernicus Global Digital Elevation Model (GLO-30). <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
        <p>FAO (2024) AQUASTAT: FAO's Global Information System on Water and Agriculture. Rome: Food and Agriculture Organization of the United Nations. <A href="https://www.fao.org/aquastat/" /></p>
        <p>Funk, C., Peterson, P., Landsfeld, M., Pedreros, D. et al. (2015) The climate hazards infrared precipitation with stations, a new environmental record for monitoring extremes. Scientific Data, 2, 150066. <A href="https://doi.org/10.1038/sdata.2015.66" /></p>
        <p>Goovaerts, P. (2000) Geostatistical approaches for incorporating elevation into the spatial interpolation of rainfall. Journal of Hydrology, 228(1-2), 113-129. <A href="https://doi.org/10.1016/S0022-1694(00)00144-X" /></p>
        <p>Hutchinson, M.F. (1995) Interpolating mean rainfall using thin plate smoothing splines. International Journal of Geographical Information Systems, 9(4), 385-403. <A href="https://doi.org/10.1080/02693799508902045" /></p>
        <p>Isaaks, E.H. and Srivastava, R.M. (1989) An Introduction to Applied Geostatistics. New York: Oxford University Press.</p>
        <p>Li, J. and Heap, A.D. (2011) A review of comparative studies of spatial interpolation methods in environmental sciences: performance and impact factors. Ecological Informatics, 6(3-4), 228-241. <A href="https://doi.org/10.1016/j.ecoinf.2010.12.003" /></p>
        <p>Matheron, G. (1963) Principles of geostatistics. Economic Geology, 58(8), 1246-1266. <A href="https://doi.org/10.2113/gsecongeo.58.8.1246" /></p>
        <p>Moran, P.A.P. (1950) Notes on continuous stochastic phenomena. Biometrika, 37(1-2), 17-23. <A href="https://doi.org/10.2307/2332142" /></p>
        <p>OCHA (2020) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <A href="https://data.humdata.org/dataset/cod-ab-zwe" /></p>
        <p>Shepard, D. (1968) A two-dimensional interpolation function for irregularly-spaced data. In: Proceedings of the 1968 23rd ACM National Conference. New York: ACM, 517-524. <A href="https://doi.org/10.1145/800186.810616" /></p>
        <p>Vose, R.S., Schmoyer, R.L., Steurer, P.M., Peterson, T.C. et al. (1992) The Global Historical Climatology Network: Long-Term Monthly Temperature, Precipitation, Sea Level Pressure, and Station Pressure Data. ORNL/CDIAC-53, NDP-041. Oak Ridge: Carbon Dioxide Information Analysis Center. <A href="https://doi.org/10.3334/CDIAC/cli.ndp041" /></p>
        <p>Wahba, G. (1990) Spline Models for Observational Data. Philadelphia: Society for Industrial and Applied Mathematics. <A href="https://doi.org/10.1137/1.9781611970128" /></p>
      </div>
    </CaseLayout>
  );
}
