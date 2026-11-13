import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/hwange-carbon/map1_study_area.webp";
import map2 from "../assets/casestudies/hwange-carbon/map2_footprints.webp";
import map3 from "../assets/casestudies/hwange-carbon/map3_carbon.webp";
import map4 from "../assets/casestudies/hwange-carbon/map4_uncertainty.webp";
import map5 from "../assets/casestudies/hwange-carbon/map5_difference.webp";
import fig1 from "../assets/casestudies/hwange-carbon/fig1_cv.webp";
import fig2 from "../assets/casestudies/hwange-carbon/fig2_classes.webp";
import fig3 from "../assets/casestudies/hwange-carbon/fig3_importance.webp";

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

// Table 1: predictors
const T1: string[][] = [
  ["Optical, dry season (June to October)", "Blue, green, red, red edge, near infrared and two shortwave infrared bands, NDVI", "8"],
  ["Optical, wet season (December to March)", "Red, near infrared, shortwave infrared, NDVI", "4"],
  ["Radar, dry season", "VV and VH backscatter", "2"],
  ["Terrain", "Elevation and slope", "2"],
];

// Table 2: spatial cross-validation
const T2: string[][] = [
  ["Coefficient of determination (R²)", "0.575"],
  ["Root mean square error (Mg/ha)", "8.04"],
  ["Relative root mean square error (%)", "73.5"],
  ["Mean absolute error (Mg/ha)", "5.14"],
  ["Mean bias (Mg/ha)", "+0.16"],
  ["Mean observed AGBD (Mg/ha)", "10.94"],
  ["Validation cells", "211 509"],
];

// Table 3: by land cover class
const T3: string[][] = [
  ["Tree cover", "1 818", "12.4", "29.1", "13.7", "2.49", "31.6"],
  ["Shrubland", "11 408", "77.7", "9.5", "4.5", "5.09", "64.7"],
  ["Grassland", "1 355", "9.2", "4.3", "2.0", "0.27", "3.5"],
  ["Cropland", "90", "0.6", "3.1", "1.5", "0.01", "0.2"],
  ["Wetland, water and bare ground", "17", "0.1", "4.8", "2.3", "0.00", "0.0"],
];

// Table 4: comparison with other estimates
const T4: string[][] = [
  ["This study (100 m Random Forest map)", "11.39", "5.35", "7.87", "—"],
  ["GEDI footprints inside the park", "10.81", "5.08", "—", "—"],
  ["GEDI gridded product (1 km, 90.5% of park)", "10.47", "4.92", "—", "0.66"],
  ["Global biomass map (100 m, 2020)", "3.50", "1.64", "2.41", "0.79"],
];

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function CarbonCaseStudy() {
  return (
    <>
      <CaseLayout slug="hwange-carbon">
        <h1>Above-Ground Carbon Stock Estimation in Hwange National Park Using GEDI LiDAR and Random Forest Regression (2019 to 2023)</h1>
        <p className="tc__by">GEDI LiDAR footprints upscaled to a 100 m carbon map with Random Forest.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (30 April 2026)</p>
        <Facts rows={[["Place", "Hwange National Park"], ["Period", "2019 to 2023"], ["Data", "GEDI L4A footprints, Sentinel-2, Sentinel-1, elevation"], ["Methods", "Random Forest regression, LiDAR biomass upscaling"], ["Tools", "Python (scikit-learn, rasterio, geopandas)"]]} />

        <h2>1 Introduction</h2>
        <p>The woodlands of Zimbabwe hold most of the country's land carbon and clearing them is the largest source of its land-use emissions. Under the Paris Agreement, Zimbabwe's forest reference emission level, as modified after technical assessment, is 5 187 697.6 t CO2e a year (UNFCCC, 2024). Any claim of reduced deforestation, whether in national reporting or in a voluntary carbon project, has to rest on maps of how much carbon the woodland holds and where. Field inventories are accurate at a few plots but cannot cover a large protected area and the global biomass maps are known to do poorly in dry, open savanna, where much of the biomass sits in small trees and shrubs.</p>
        <p>The Global Ecosystem Dynamics Investigation (GEDI), a laser altimeter on the International Space Station, measured the height structure of vegetation in 25 m footprints between 2019 and 2023. Each footprint was converted into an estimate of above-ground biomass density (AGBD) with models fitted to field plots (Dubayah et al., 2022). The footprints are a sample, not a map. They lie along tracks with gaps of several hundred metres between them. Those gaps were filled here for Hwange National Park, the largest national park in Zimbabwe. A Random Forest regression (Breiman, 2001) was trained on the footprints with satellite radar, optical and terrain predictors to give a wall-to-wall map of biomass and carbon at 100 m. The result was then checked by independent cross-validation, against the published woodland inventory of the region and against two existing biomass products.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To assess the density and range of the GEDI footprint biomass estimates over Hwange National Park.</li>
          <li>To evaluate the accuracy of a Random Forest model that upscales the footprints to a 100 m map, using spatial block cross-validation.</li>
          <li>To quantify the above-ground carbon stock of the park and analyse its distribution by land cover class.</li>
          <li>To compare the result with an existing global biomass map, the gridded GEDI product and published field inventory values.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Hwange National Park lies in Hwange District of Matabeleland North Province, in the north-west of Zimbabwe, along the border with Botswana (Map 1). It covers 14 699 km² in this analysis, within 0.3% of the 14 651 km² reported to the World Database on Protected Areas. The park is almost flat: elevation runs from 828 m to 1 148 m, with a median of 1 017 m and the mean slope is 0.7°. Most of the park lies on deep Kalahari sands, where Zambezi teak (Baikiaea plurijuga) woodland grows on the old dune crests and open shrubland and grassland fill the hollows between them; mopane (Colophospermum mopane) woodland and scrub dominate the basalt and clay soils in the north around Sinamatella and Robins Camp (Childes and Walker, 1987). Rain falls in a single summer season and there is no permanent river across the sands, so the park's wildlife, including one of the largest elephant populations in Africa, depends in the dry season on pumped waterholes. Elephant browsing around these waterholes opens the woodland: around artificial watering points in the north of the park, damage to woody plants was 23% where elephant use was high and 11% where it was low (Mukwashi et al. 2012). The main tourist and management centres are Main Camp near Dete in the east, Sinamatella and Robins Camp in the north.</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p>The training data were the GEDI Level 4A footprint AGBD estimates, version 2.1 (Dubayah et al., 2022), for April 2019 to March 2023. Only footprints with the quality flag set, no degraded pointing and a beam sensitivity of at least 0.95 were used. The predictors were assembled on a 100 m grid in the UTM zone 35S projection covering the park and a 5 km buffer, 1 860 by 1 633 cells: Sentinel-2 surface reflectance (Drusch et al. 2012) with clouds and shadows masked by the scene classification layer, as median composites for the dry and wet seasons of 2020 to 2023; Sentinel-1 C-band radar backscatter (Torres et al., 2012) in both polarisations, as a dry-season median; and elevation and slope from the Copernicus GLO-30 elevation model (ESA, 2021). Land cover was taken from ESA WorldCover 2021 (Zanaga et al. 2022) and used only to summarise the result. For comparison, two existing products were read on the same grid: the ESA Climate Change Initiative Biomass map version 5 for 2020 at 100 m (Santoro and Cartus, 2024), referred to below as the global biomass map and the GEDI Level 4B gridded AGBD version 2.1 at 1 km (Dubayah et al., 2023), referred to as the gridded GEDI product. The park boundary is from the World Database on Protected Areas (UNEP-WCMC and IUCN, 2025). The park area was measured in an equal-area projection (EPSG:6933); the UTM cells used for totals differ from true area by less than 0.1% at this longitude.</p>

        <h3>Footprint screening</h3>
        <p>Footprints with AGBD below 0 or above 200 Mg/ha were removed as implausible for this savanna, which removed 18 of 721 540 footprints. The remaining 721 522 footprints were averaged into the 100 m cells they fell in and cells with fewer than two footprints were dropped, so that each training value represents more than one laser shot. This gave 211 509 training cells.</p>

        <h3>Random Forest model and validation</h3>
        <p>A Random Forest of 200 trees, with at least five samples per leaf and 40% of the predictors tried at each split, was trained to predict the mean cell AGBD from the sixteen predictors in Table 1. Because neighbouring cells are similar, a random split of training and test cells overstates accuracy (Roberts et al. 2017; Ploton et al., 2020), so the model was tested by five-fold cross-validation on 10 km by 10 km blocks: every cell in a block was held out together and predicted by a model that had seen no cell in that block. Predictor importance was taken as the mean decrease in impurity of the final model.</p>
        <p className="tc__cap">Table 1. Predictors used in the model</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Group</th><th>Variables</th><th className="n">Number</th></tr></thead>
            <tbody><Rows rows={T1} num={2} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. NDVI is the normalised difference vegetation index.</p>

        <h3>Carbon stock and uncertainty</h3>
        <p>The final model, trained on all cells, predicted AGBD for every cell of the grid. Biomass was converted to carbon with the default carbon fraction of 0.47 (IPCC, 2006) and to carbon dioxide equivalent by the ratio 44/12. Each cell covers one hectare, so the park totals are the sums over the cells inside the boundary. The spread of the model was mapped as the standard deviation of the predictions of 50 of the 200 trees in each cell. Totals and means were then summarised by WorldCover class.</p>

        <h3>Comparison</h3>
        <p>The 100 m map was compared cell by cell with the global biomass map and the gridded GEDI product, by mean and by Pearson correlation over the park. The global map leaves cells with zero biomass empty and these were read as 0 Mg/ha. The gridded GEDI product covers 90.5% of the park, so its mean was compared with the mean of this study over the same cells. The class means were finally compared with the woodland inventory of the SADC REDD pilot in north-west Zimbabwe (GIZ, 2015).</p>

        <h2>5 Results</h2>
        <h3>GEDI footprint biomass</h3>
        <p>The park received 721 522 usable footprints over four years, about 49 per km², arranged along the oblique orbital tracks of the space station. Averaged into 1 km cells they reach 95% of the park, leaving only small gaps between tracks (Map 2). Most of the 2023 data are missing because the instrument was stored from March 2023. The footprint values are strongly skewed. The median footprint holds 4.7 Mg/ha, half the footprints hold less than 5 Mg/ha and 68.7% less than 10 Mg/ha, while 5.2% exceed 40 Mg/ha and the mean is 10.8 Mg/ha. The high values cluster in bands along the tracks where they cross the woodland ridges of the centre and north and the lowest values lie on the open grassland of the south and around the pans.</p>
        <Fig src={map2} cap="Map 2. GEDI Footprint Map (2019 to 2023), mean biomass density of the usable footprints in each 1 km cell." />

        <h3>Model accuracy</h3>
        <p>Under spatial block cross-validation the model explained 57.5% of the variance in cell AGBD (R² 0.575), with a root mean square error of 8.04 Mg/ha (73.5% of the mean) and a mean bias of +0.16 Mg/ha (Table 2, Figure 1). Overall the model is close to unbiased. Like all regression models of this kind, though, it pulls extreme values toward the mean. The 4.1% of cells observed above 40 Mg/ha, which average 49.9 Mg/ha, were predicted at 29.1 Mg/ha on average, while cells observed below 5 Mg/ha, averaging 2.7 Mg/ha, were predicted at 5.5 Mg/ha. Dense woodland is therefore somewhat underestimated and open land somewhat overestimated and in the park total the two largely cancel.</p>
        <p className="tc__cap">Table 2. Accuracy of the model under five-fold spatial block cross-validation</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Measure</th><th className="n">Value</th></tr></thead>
            <tbody><Rows rows={T2} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Blocks of 10 km by 10 km; each cell is the mean of at least two footprints.</p>
        <Fig src={fig1} cap="Figure 1. Observed against predicted AGBD for the 211 509 cross-validation cells, shown as a random sample of 5 000 cells with the mean prediction in each 5 Mg/ha class and the one-to-one line." />
        <p>Radar backscatter did most of the work (Figure 3). The two radar bands account for 53.0% of the importance and the VV band alone for 30.7%, because C-band backscatter responds directly to the woody stems and branches that hold the biomass. The twelve optical bands together contribute 37.7%, led by the wet-season red band. Elevation and slope add 9.3%, probably by separating the northern basalt from the sands.</p>
        <Fig src={fig3} cap="Figure 3. Importance of each predictor in the final model." />

        <h3>Carbon stock and its distribution</h3>
        <p>The park holds an estimated 16.73 Mt of above-ground biomass, or 7.87 Mt of carbon (28.84 Mt CO2e). The mean density is 11.39 Mg/ha of biomass (5.35 Mg C/ha) and the median 7.63 Mg/ha. The carbon is unevenly spread (Map 3). The densest woodland lies in the north and north-east, between Sinamatella, Main Camp and the railway and along the line of old dunes in the centre, where the teak woodland on each crest shows as a stripe running west to east. The south and west of the park, toward the Botswana border, are open shrubland and grassland with less than 4 Mg C/ha.</p>
        <Fig src={map3} cap="Map 3. Above-Ground Carbon Density Map (2020 to 2023), predicted carbon at 100 m." />
        <p>Shrubland covers 77.7% of the park and holds 64.7% of its carbon, 5.09 Mt C at 4.5 Mg C/ha (Table 3). Tree cover is only 12.4% of the area but at 13.7 Mg C/ha holds 31.6% of the carbon, 2.49 Mt C. Grassland, 9.2% of the park, holds 3.5%. The large shrubland share means that most of the park's carbon sits in low, scattered woody plants rather than in closed woodland.</p>
        <p className="tc__cap">Table 3. Biomass and carbon by land cover class inside the park</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Land cover class</th><th className="n">Area (km²)</th><th className="n">Share of park (%)</th><th className="n">Mean AGBD (Mg/ha)</th><th className="n">Mean carbon (Mg C/ha)</th><th className="n">Carbon (Mt C)</th><th className="n">Share of carbon (%)</th></tr></thead>
            <tbody>
              <Rows rows={T3} num={1} />
              <tr className="t"><td>Hwange National Park</td><td className="n">14 689</td><td className="n">100.0</td><td className="n">11.4</td><td className="n">5.4</td><td className="n">7.87</td><td className="n">100.0</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; land cover classes from ESA WorldCover 2021. Area is the count of one-hectare UTM cells; the equal-area measure of the boundary is 14 699 km². Built-up land (under 1 km²) is included in the total only.</p>
        <p>The tree-level spread of the model averages 5.25 Mg/ha of biomass, or 2.5 Mg C/ha, about half of the predicted value in a typical cell (Map 4). The spread is highest in the dense northern woodland and on the woodland stripes, where the footprints themselves vary most and lowest on the open grassland. It measures how far the trees of the model disagree, not the full error of the map, which the cross-validation gives.</p>
        <Fig src={map4} cap="Map 4. Prediction Uncertainty Map (2020 to 2023), standard deviation of 50 model trees in each cell." />

        <h3>Comparison with other estimates</h3>
        <p>The map agrees closely with the GEDI data at coarser scale (Table 4). Its mean of 11.39 Mg/ha is 5.4% above the 10.81 Mg/ha mean of the footprints inside the park and on the 90.5% of the park covered by the gridded GEDI product its mean of 11.17 Mg/ha is 6.6% above that product's 10.47 Mg/ha. The correlation with the 1 km product is 0.66, lower mainly because the 1 km cells average across the dune stripes the 100 m map resolves.</p>
        <p>The global biomass map is much lower. Its park mean is 3.50 Mg/ha, less than a third of this study and it gives 2.41 Mt C against 7.87 Mt C here, although the two maps are well correlated (r 0.79) and place the woodland in the same areas (Map 5). The difference lies almost entirely in the open land: the global map gives shrubland 2.2 Mg/ha against 9.5 Mg/ha here and grassland 0.1 Mg/ha against 4.3 Mg/ha, so that much of the south is treated as having no biomass at all, while in tree cover the gap is narrower, 14.3 against 29.1 Mg/ha (Figure 2). The field inventory of the SADC REDD pilot gives 29.44 t/ha for teak woodland in north-west Zimbabwe (GIZ, 2015), which matches the 29.1 Mg/ha of the tree cover class in this study and is twice the global map's value for the same class.</p>
        <p className="tc__cap">Table 4. Above-ground biomass and carbon of Hwange National Park from four sources</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Source</th><th className="n">Mean AGBD (Mg/ha)</th><th className="n">Mean carbon (Mg C/ha)</th><th className="n">Park carbon (Mt C)</th><th className="n">Correlation with this study (r)</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; GEDI L4A and L4B v2.1 (Dubayah et al., 2022, 2023); ESA CCI Biomass v5 (Santoro and Cartus, 2024). Carbon = AGBD × 0.47. No park total is given for the footprints, which are a sample, or for the gridded product, which does not cover the whole park.</p>
        <Fig src={map5} cap="Map 5. Difference from ESA CCI Biomass Map (2020), this study minus the global biomass map in carbon." />
        <Fig src={fig2} cap="Figure 2. Mean AGBD by land cover class from this study and the global biomass map, with the field inventory value for teak woodland." />

        <h2>6 Discussion</h2>
        <p>The model's accuracy is in line with published work in southern African savanna. Li et al. (2024) tested GEDI footprint biomass against airborne lidar and field plots in South African savanna. The standard footprint product reached R² 0.42 with an error of 12 Mg/ha (79.5%), while locally fitted Random Forest models reached R² 0.71 with an error of 53.3%. The R² of 0.575 and relative error of 73.5% here lie between the two, for a harder task: predicting unseen 10 km blocks from satellite images rather than footprints from lidar. A relative error of 73.5% sounds large, but it comes from the low mean, since an error of 8 Mg/ha on a cell holding 11 Mg/ha is a big share of a small number. Because the errors are nearly unbiased, they average out over large areas and the park total is far more reliable than the value of any single hectare.</p>
        <p>The total depends on the GEDI footprint estimates and those carry their own error that the cross-validation cannot see. The published checks disagree on its direction. Li et al. (2024) found the footprint estimates too low in South African savanna, with a mean systematic deviation of up to −37%, while Hasoba and Czimber (2026) found them about 2.1 times the field values in Sudanian savanna woodland in the Blue Nile region of Sudan. Against these, the agreement of the tree cover class with the 29.44 t/ha inventory value of GIZ (2015) is the strongest local evidence that the footprint estimates are of the right size in Hwange. One forest class matching one inventory value is not a test of the whole park, however and no field plots exist in its shrubland. Given the size of the published footprint errors, the total of 7.87 Mt C could plausibly lie anywhere from about half to about one and a half times that value (roughly 4 to 12 Mt C).</p>
        <p>The gap with the global biomass map is large and it cannot be settled here. That map is built from radar and tuned for forest. In open savanna its signal comes close to the level it can tell apart from bare ground and it sets much of the park's shrubland and grassland to zero. The GEDI footprints and the gridded GEDI product both put the park's mean biomass near 10 to 11 Mg/ha and the one field value available agrees with this study in woodland. No field data, however, show which map is closer in the shrubland, where most of the difference lies. Until plots are measured, the two products are best treated as an upper and a lower view of the stock.</p>
        <p>The analysis has further limits. The predictors describe 2020 to 2023 while the footprints span April 2019 to March 2023, so a fire or clearing in that period mixes two states. WorldCover classes are used only to report results and some of what it calls shrubland is open teak woodland. Below-ground biomass, dead wood and soil carbon are not included and would add substantially to the total. Finally, the Random Forest cannot predict beyond the range of its training data, which is why the densest woodland is underestimated.</p>

        <h2>7 Recommendations</h2>
        <p>Carbon reporting for Zimbabwe's savanna protected areas should not rely on any single biomass map, since the GEDI-based estimate and the global map differ here by a factor of three. The Forestry Commission and the Zimbabwe Parks and Wildlife Management Authority should establish a small set of permanent plots in the shrubland of the park, which holds 64.7% of its carbon but has the least field data, to test the footprint estimates directly.</p>
        <p>Management should focus carbon protection on the woodland of the north and the dune crests. These areas cover about an eighth of the park but hold almost a third of its carbon and they are where fire and elephant browsing around waterholes do the most damage. The placement of new waterholes should take account of the carbon map so that pressure is not moved into the densest woodland.</p>
        <p>The map should be repeated when further GEDI data are released, since the instrument resumed measurements after 2024, to measure change rather than a single stock. The same method can be applied to the neighbouring forest and safari areas of Matabeleland North, where clearing for cultivation is reducing woodland outside the park.</p>

        <h2>8 Conclusion</h2>
        <p>All four objectives were met. The park was covered by 721 522 usable GEDI footprints, about 49 per km², with a median of 4.7 Mg/ha and a mean of 10.8 Mg/ha of above-ground biomass. A Random Forest model on radar, optical and terrain predictors upscaled them to 100 m with a spatial cross-validated R² of 0.575, an error of 8.04 Mg/ha and almost no bias and radar backscatter was the leading predictor. The park holds an estimated 7.87 Mt of above-ground carbon (28.84 Mt CO2e), at a mean of 5.35 Mg C/ha. Shrubland holds 64.7% of it and tree cover, on 12.4% of the land, holds 31.6%. The result agrees within 7% with the GEDI footprints and gridded product and matches the field inventory value for teak woodland, but it is more than three times the estimate of the global biomass map, which treats much of the open savanna as bare. Without field plots the total stays uncertain (about 4 to 12 Mt C). Both maps agree on where the carbon lies, though and the open shrubland is where the estimates most need testing.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Breiman, L. (2001) Random forests. Machine Learning, 45, 5-32. <A href="https://doi.org/10.1023/A:1010933404324" /></p>
          <p>Childes, S.L. and Walker, B.H. (1987) Ecology and dynamics of the woody vegetation on the Kalahari sands in Hwange National Park, Zimbabwe. Vegetatio, 72(2), 111-128. <A href="https://doi.org/10.1007/BF00044841" /></p>
          <p>Drusch, M., Del Bello, U., Carlier, S., Colin, O. et al. (2012) Sentinel-2: ESA's optical high-resolution mission for GMES operational services. Remote Sensing of Environment, 120, 25-36. <A href="https://doi.org/10.1016/j.rse.2011.11.026" /></p>
          <p>Dubayah, R.O., Armston, J., Kellner, J.R., Duncanson, L. et al. (2022) GEDI L4A Footprint Level Aboveground Biomass Density, Version 2.1. ORNL DAAC, Oak Ridge. <A href="https://doi.org/10.3334/ORNLDAAC/2056" /></p>
          <p>Dubayah, R.O., Armston, J., Healey, S.P., Yang, Z. et al. (2023) GEDI L4B Gridded Aboveground Biomass Density, Version 2.1. ORNL DAAC, Oak Ridge. <A href="https://doi.org/10.3334/ORNLDAAC/2299" /></p>
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <A href="https://doi.org/10.5270/ESA-c5d3d65" /></p>
          <p>GIZ (2015) Baikiaea woodlands: SADC REDD pilot, biomass and carbon results for north-west Zimbabwe. Deutsche Gesellschaft für Internationale Zusammenarbeit, Gaborone. <A href="https://www.giz.de/en/downloads/giz2015-en-baikiaea-woodlands-sadc-redd.pdf" /></p>
          <p>Hasoba and Czimber (2026) Spatial domain mismatch between field plots and GEDI inflates aboveground biomass model accuracy in a Sudanian savanna woodland. Remote Sensing, 18(16), 2751. <A href="https://doi.org/10.3390/rs18162751" /></p>
          <p>IPCC (2006) 2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 4: Agriculture, Forestry and Other Land Use. IGES, Hayama. <A href="https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol4.html" /></p>
          <p>Li, X. et al. (2024) Evaluation of GEDI footprint level biomass models in Southern African savannas using airborne LiDAR and field measurements. Science of Remote Sensing, 10, 100161. <A href="https://doaj.org/article/a59a0dd5346d4e06939219adef3184bd" /></p>
          <p>Mukwashi, K., Gandiwa, E. and Kativu, S. (2012) Impact of African elephants on Baikiaea plurijuga woodland around natural and artificial watering points in northern Hwange National Park, Zimbabwe. International Journal of Environmental Sciences, 2(3), 1355-1368. <A href="https://ir.uz.ac.zw/handle/10646/870" /></p>
          <p>Ploton, P., Mortier, F., Réjou-Méchain, M., Barbier, N. et al. (2020) Spatial validation reveals poor predictive performance of large-scale ecological mapping models. Nature Communications, 11, 4540. <A href="https://doi.org/10.1038/s41467-020-18321-y" /></p>
          <p>Roberts, D.R., Bahn, V., Ciuti, S., Boyce, M.S. et al. (2017) Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8), 913-929. <A href="https://doi.org/10.1111/ecog.02881" /></p>
          <p>Santoro, M. and Cartus, O. (2024) ESA Biomass Climate Change Initiative (Biomass_cci): Global datasets of forest above-ground biomass, version 5. NERC EDS Centre for Environmental Data Analysis. <A href="https://doi.org/10.5285/bf535053562141c6bb7ad831f5998d77" /></p>
          <p>Torres, R., Snoeij, P., Geudtner, D., Bibby, D. et al. (2012) GMES Sentinel-1 mission. Remote Sensing of Environment, 120, 9-24. <A href="https://doi.org/10.1016/j.rse.2011.05.028" /></p>
          <p>UNEP-WCMC and IUCN (2025) World Database on Protected Areas. Protected Planet. <A href="https://www.protectedplanet.net" /></p>
          <p>UNFCCC (2024) Report on the technical assessment of the proposed forest reference emission level of Zimbabwe. FCCC/TAR/2024/ZWE. <A href="https://unfccc.int/documents/644803" /></p>
          <p>Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W. et al. (2022) ESA WorldCover 10 m 2021 v200. <A href="https://doi.org/10.5281/zenodo.7254221" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
