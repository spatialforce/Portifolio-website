import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/population/map1_study_area.webp";
import map2 from "../assets/casestudies/population/map2_density_grid.webp";
import map3 from "../assets/casestudies/population/map3_density_district.webp";
import map4 from "../assets/casestudies/population/map4_growth.webp";
import map5 from "../assets/casestudies/population/map5_sex_ratio.webp";
import fig1 from "../assets/casestudies/population/fig1_census_totals.webp";
import fig2 from "../assets/casestudies/population/fig2_provinces.webp";

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

const PROV: [string, string, string, string, string, string][] = [
  ["Bulawayo", "653 337", "665 940", "0.19", "546", "1 220.2"],
  ["Harare", "2 123 132", "2 427 209", "1.35", "940", "2 582.2"],
  ["Manicaland", "1 752 698", "2 037 762", "1.52", "35 845", "56.9"],
  ["Mashonaland Central", "1 152 520", "1 384 891", "1.85", "28 195", "49.1"],
  ["Mashonaland East", "1 344 955", "1 731 181", "2.56", "32 171", "53.8"],
  ["Mashonaland West", "1 501 656", "1 893 578", "2.35", "57 677", "32.8"],
  ["Masvingo", "1 485 090", "1 638 539", "0.99", "56 456", "29.0"],
  ["Matabeleland North", "749 017", "827 626", "1.00", "75 456", "11.0"],
  ["Matabeleland South", "683 893", "760 345", "1.07", "54 125", "14.0"],
  ["Midlands", "1 614 941", "1 811 908", "1.16", "49 363", "36.7"],
];

const FAST: [string, string, string, string, string][] = [
  ["Harare Rural", "Harare", "113 599", "357 860", "12.16"],
  ["Seke", "Mashonaland East", "100 756", "200 476", "7.12"],
  ["Goromonzi", "Mashonaland East", "224 987", "386 199", "5.55"],
  ["Ruwa Local Board", "Mashonaland East", "56 678", "94 083", "5.20"],
  ["Mvurwi", "Mashonaland Central", "10 549", "15 645", "4.02"],
  ["Beitbridge Urban", "Matabeleland South", "42 137", "58 574", "3.35"],
];
const SLOW: [string, string, string, string, string][] = [
  ["Bulilima", "Matabeleland South", "90 561", "85 600", "-0.56"],
  ["Mangwe", "Matabeleland South", "66 218", "65 562", "-0.10"],
  ["Harare Urban", "Harare", "1 485 231", "1 491 740", "0.04"],
  ["Tsholotsho", "Matabeleland North", "115 119", "115 782", "0.06"],
  ["Mbire", "Mashonaland Central", "82 380", "83 724", "0.16"],
  ["Matobo", "Matabeleland South", "93 940", "95 696", "0.19"],
];

const SEXP: [string, string, string, string, string][] = [
  ["Bulawayo", "307 983", "357 957", "49 974", "86.0"],
  ["Harare", "1 159 543", "1 267 666", "108 123", "91.5"],
  ["Manicaland", "965 532", "1 072 230", "106 698", "90.0"],
  ["Mashonaland Central", "681 313", "703 578", "22 265", "96.8"],
  ["Mashonaland East", "835 264", "895 917", "60 653", "93.2"],
  ["Mashonaland West", "934 821", "958 757", "23 936", "97.5"],
  ["Masvingo", "763 537", "875 002", "111 465", "87.3"],
  ["Matabeleland North", "400 188", "427 438", "27 250", "93.6"],
  ["Matabeleland South", "370 713", "389 632", "18 919", "95.1"],
  ["Midlands", "870 664", "941 244", "70 580", "92.5"],
];

const LOWSR: [string, string, string, string, string][] = [
  ["Gokwe Centre", "Midlands", "14 933", "18 142", "82.3"],
  ["Binga", "Matabeleland North", "72 393", "87 589", "82.7"],
  ["Chipinge Urban", "Manicaland", "15 880", "19 079", "83.2"],
  ["Zaka", "Masvingo", "90 910", "107 979", "84.2"],
  ["Bikita", "Masvingo", "80 844", "95 991", "84.2"],
  ["Masvingo Urban", "Masvingo", "41 321", "48 965", "84.4"],
  ["Chivi", "Masvingo", "79 556", "93 423", "85.2"],
  ["Gutu", "Masvingo", "95 842", "112 318", "85.3"],
];
const HIGHSR: [string, string, string, string, string][] = [
  ["Bubi", "Matabeleland North", "39 063", "35 021", "111.5"],
  ["Umguza", "Matabeleland North", "59 144", "54 121", "109.3"],
  ["Umzingwane", "Matabeleland South", "36 984", "34 876", "106.0"],
  ["Mhondoro-Ngezi", "Mashonaland West", "71 605", "69 386", "103.2"],
  ["Makonde", "Mashonaland West", "106 296", "103 651", "102.6"],
  ["Insiza", "Matabeleland South", "62 124", "60 779", "102.2"],
  ["Sanyati", "Mashonaland West", "70 202", "69 031", "101.7"],
  ["Kwekwe Rural", "Midlands", "98 794", "98 269", "100.5"],
];

function Rows({ rows, num }: { rows: string[][]; num: number }) {
  return <>{rows.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}</tr>)}</>;
}

export default function PopulationCaseStudy() {
  return (
    <>
      <CaseLayout slug="population-zimbabwe">
        <h1>A Spatial Analysis of Population Distribution, Density and Growth in Zimbabwe Between the 2012 and 2022 Population Censuses</h1>
        <p className="tc__by">District density, growth and sex ratio from the 2012 and 2022 censuses.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (5 May 2025)</p>
        <Facts rows={[["Place", "Zimbabwe, 91 districts"], ["Period", "2012 and 2022 censuses"], ["Data", "ZIMSTAT census totals, WorldPop population grid"], ["Methods", "Choropleth mapping, population density analysis, change analysis"], ["Tools", "Google Earth Engine, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Zimbabwe held its fifth post-independence population and housing census in April 2022. The preliminary results counted 15 178 979 people, up from 13 061 239 in the 2012 census. A national total says little, though, about where people live or where the growth is happening and those are the questions that matter when schools, clinics, water supply and roads are planned.</p>
        <p>The district totals of the 2012 and 2022 censuses, a gridded population surface and the male and female counts of the 2022 census were used here to answer three questions: how the people of Zimbabwe are spread across the country, how fast each district grew between the two censuses and where men are missing from the population.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To map the distribution and density of the population of Zimbabwe in 2022 at district level and on a 300 m grid.</li>
          <li>To calculate the average annual population growth rate of each district and province between 2012 and 2022.</li>
          <li>To map the sex ratio of each district in 2022 and relate it to growth and migration.</li>
          <li>To recommend where planning and service delivery should be directed based on these results.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Zimbabwe is a landlocked country in southern Africa covering about 390 757 km². It borders Zambia to the north, Mozambique to the east, South Africa to the south and Botswana to the west. The country is divided into ten provinces, including the two metropolitan provinces of Harare and Bulawayo and 91 districts as used in the 2022 census.</p>
        <p>The central watershed, the highveld, runs from south-west to north-east at 1 200 m to 1 600 m above sea level and carries most of the large towns, including Harare, Bulawayo, Gweru and Kwekwe. The Eastern Highlands along the Mozambique border rise above 2 500 m at Mount Nyangani. The lowveld in the south and south-east lies mostly below 900 m and the Zambezi valley in the north below 600 m. Both are hotter and drier than the highveld (Map 1).</p>
        <Fig src={map1} cap="Map 1. Study Area Map." />

        <h2>4 Data and methods</h2>
        <p>District totals for 2022 were taken from the 2022 Population and Housing Census Preliminary Report (ZIMSTAT, 2022). The tables were extracted from the report text and the 91 district totals were checked against the published national total, which they matched exactly. District totals for 2002 and 2012 were taken from the compilation of census results by City Population (Brinkhoff, 2025). The 2012 district totals summed exactly to the official 2012 census total of 13 061 239. The final 2022 census totals published later differ from the preliminary figures by 22 people nationally and by at most 55 people in any district, so the preliminary figures were used throughout.</p>
        <p>District boundaries were taken from the OCHA administrative boundaries for Zimbabwe (OCHA, 2023) and joined to the census tables by district name. District areas were calculated in the Africa Albers Equal Area projection. The total area obtained was 390 772 km², which is within 0.01% of the official figure. Population density was calculated as people per km² of district area and the average annual growth rate between 2012 and 2022 was calculated as an exponential rate, r = (P2022 / P2012)^(1/10) − 1.</p>
        <p>District totals hide how people are spread within each district. To show this, the WorldPop 2020 constrained population grid at 100 m (Bondarenko et al., 2020) was aggregated to 300 m and the cells of each district were rescaled to sum to its 2022 census total. The scaling factors ranged from 0.85 to 2.38, with a median of 1.03. Harare Rural needed the largest factor, because WorldPop 2020 placed far fewer people there than the census counted.</p>
        <p>The male and female totals of each district were extracted from the same preliminary report. In each district table the male and female totals are the only pair of figures that add up to the district total. The 91 district pairs summed exactly to the national totals of 7 289 558 males and 7 889 421 females and their province sums matched the province totals of the report. The sex ratio was calculated as the number of males per 100 females.</p>
        <p>Elevation for the study area map was taken from the Copernicus GLO-30 digital elevation model (ESA, 2021) and country borders and lakes from Natural Earth. All processing and mapping were done in Python with geopandas, rasterio and matplotlib. Each figure was cross checked against a second source and the checks are recorded in the verification note kept with the analysis.</p>

        <h2>5 Results</h2>
        <h3>Population change since 1982</h3>
        <p>The population of Zimbabwe doubled between 1982 and 2022 (Figure 1). Growth was fastest between 1982 and 1992 and slowed between 1992 and 2002. Between 2012 and 2022 the population grew by 2 117 740 people, an average of 1.51% per year. City Population gives the 1982 total as 7 608 432, while one ZIMSTAT table gives 7 546 041; the first value is shown in Figure 1.</p>
        <Fig src={fig1} cap="Figure 1. Population of Zimbabwe at each census (1982 to 2022)." />

        <h3>Distribution and density</h3>
        <p>The 300 m population grid (Map 2) shows that people are concentrated along the central watershed and in the north-east. The densest belt runs from Harare through Chitungwiza, Ruwa and Epworth, with further concentrations around Bulawayo, Gweru, Kwekwe, Kadoma and Mutare and in the communal lands of Masvingo, Manicaland and Mashonaland East. Large parts of the west and north-west, including Hwange National Park, the Zambezi valley and the Gonarezhou area, have few or no settled people.</p>
        <Fig src={map2} cap="Map 2. Population Density Map (2022), 300 m grid scaled to district census totals." />
        <p>At district level (Map 3), the national average density was 38.8 people per km² and the median district had 48.8 people per km². Twenty-three rural districts had fewer than 25 people per km². Together they covered 223 970 km², or 57% of the land area and held 3 121 661 people, or 21% of the population. Most urban districts had densities above 1 000 people per km² and the province of Harare had 2 582 people per km².</p>
        <Fig src={map3} cap="Map 3. Population Density By District Map (2022)." />
        <p>Table 1 gives the population, growth, area and density of each province. Harare was the most populous province in 2022 with 2 427 209 people, followed by Manicaland with 2 037 762. Matabeleland South had the smallest population of the eight rural provinces. Figure 2 compares the provinces in 2012 and 2022.</p>
        <p className="tc__cap">Table 1. Population, growth, area and density by province (2012 and 2022)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Province</th><th className="n">Population 2012</th><th className="n">Population 2022</th><th className="n">Growth (% per year)</th><th className="n">Area (km²)</th><th className="n">Density 2022 (people per km²)</th></tr></thead>
            <tbody>
              <Rows rows={PROV} num={1} />
              <tr className="t"><td>Zimbabwe</td><td className="n">13 061 239</td><td className="n">15 178 979</td><td className="n">1.51</td><td className="n">390 772</td><td className="n">38.8</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: ZIMSTAT (2012, 2022); areas calculated in Africa Albers Equal Area.</p>
        <Fig src={fig2} cap="Figure 2. Population by province (2012 and 2022 censuses)." />

        <h3>Growth between 2012 and 2022</h3>
        <p>Growth was uneven across the country (Map 4). Mashonaland East grew fastest at 2.56% per year, followed by Mashonaland West at 2.35%. Bulawayo grew by only 0.19% per year and the urban district of Harare by 0.04% per year. The fastest growth was in the districts that surround Harare: Harare Rural grew by 12.16% per year, Seke by 7.12%, Goromonzi by 5.55% and Ruwa by 5.20% (Table 2). Two districts lost population, both in south-western Matabeleland South along the Botswana border: Bulilima at −0.56% per year and Mangwe at −0.10% per year.</p>
        <Fig src={map4} cap="Map 4. Population Growth By District Map (2012–2022), average annual rate." />
        <p className="tc__cap">Table 2. Districts with the fastest and slowest population growth (2012 to 2022)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>District</th><th>Province</th><th className="n">Population 2012</th><th className="n">Population 2022</th><th className="n">Growth (% per year)</th></tr></thead>
            <tbody>
              <tr><td colSpan={5}><i>Fastest growth</i></td></tr>
              <Rows rows={FAST} num={2} />
              <tr><td colSpan={5}><i>Slowest growth</i></td></tr>
              <Rows rows={SLOW} num={2} />
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: ZIMSTAT (2022); Brinkhoff (2025) for 2012 district totals.</p>

        <h3>Sex ratio</h3>
        <p>The 2022 census counted 7 289 558 males and 7 889 421 females, a sex ratio of 92 males per 100 females. Women outnumbered men in every province (Table 3). The lowest ratios were in Bulawayo (86.0) and Masvingo (87.3) and Masvingo had 111 465 more women than men, the largest gap of any province. The highest ratios were in Mashonaland West (97.5) and Mashonaland Central (96.8).</p>
        <Fig src={map5} cap="Map 5. Sex Ratio By District Map (2022), males per 100 females." />
        <p className="tc__cap">Table 3. Male and female population and sex ratio by province (2022)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Province</th><th className="n">Males</th><th className="n">Females</th><th className="n">Females minus males</th><th className="n">Males per 100 females</th></tr></thead>
            <tbody>
              <Rows rows={SEXP} num={1} />
              <tr className="t"><td>Zimbabwe</td><td className="n">7 289 558</td><td className="n">7 889 421</td><td className="n">599 863</td><td className="n">92.4</td></tr>
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: ZIMSTAT (2022).</p>
        <p>At district level (Map 5) the ratio ranged from 82.3 in Gokwe Centre to 111.5 in Bubi. Thirty-three of the 91 districts had fewer than 90 males per 100 females and 12 of the 19 districts of Masvingo and Matabeleland South were in this group. Five of the eight lowest ratios were in Masvingo province: Zaka, Bikita, Masvingo Urban, Chivi and Gutu (Table 4). Several of these districts also grew slowly between 2012 and 2022, Gutu by 0.25% per year and Chivi by 0.41%. Bulilima, one of the two districts that lost population, had a ratio of 85.8.</p>
        <p>Only ten districts had 100 or more males per 100 females. Most of them are mining and commercial farming districts of Matabeleland North, Matabeleland South, Mashonaland West and Midlands, among them Bubi, Umguza, Umzingwane, Insiza, Mhondoro-Ngezi, Makonde, Sanyati and Kwekwe Rural.</p>
        <p className="tc__cap">Table 4. Districts with the lowest and highest sex ratios (2022)</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>District</th><th>Province</th><th className="n">Males</th><th className="n">Females</th><th className="n">Males per 100 females</th></tr></thead>
            <tbody>
              <tr><td colSpan={5}><i>Lowest</i></td></tr>
              <Rows rows={LOWSR} num={2} />
              <tr><td colSpan={5}><i>Highest</i></td></tr>
              <Rows rows={HIGHSR} num={2} />
            </tbody>
          </table>
        </div>
        <p className="tc__src">Source: ZIMSTAT (2022).</p>

        <h2>6 Discussion</h2>
        <p>The results show a population that is still mostly rural but whose growth has moved to the edges of Harare. Harare Urban, the core city, barely grew between 2012 and 2022, while the districts around it grew by between 5% and 12% per year. This reflects the expansion of housing into Harare Rural, Seke, Goromonzi, Ruwa and Epworth, where land is cheaper and new settlements have been laid out. Bulawayo shows a similar pattern of very slow growth in the city itself. The 2022 preliminary report put the rural share of the population at 61.4%, compared with about 67% reported for 2012, which agrees with this shift towards towns and their surroundings.</p>
        <p>The fastest growth rates need careful reading. The 2012 and 2022 figures were matched by district name and some district boundaries around Harare were redrawn between the two censuses. Part of the very high growth in Harare Rural is therefore likely to come from the new boundaries rather than from people moving in or being born. Province totals are not affected by this and they confirm that Mashonaland East and Mashonaland West grew fastest.</p>
        <p>The decline in Bulilima and Mangwe and the slow growth in Tsholotsho and Matobo, fit the long history of migration from south-western Zimbabwe to South Africa and Botswana. Anyone working abroad on census night was not counted in these districts.</p>
        <p>The sex ratio map points the same way. A ratio well below 100 in a rural district usually means that many working-age men are absent. The census counted 908 914 Zimbabweans who had emigrated from households still living in the country, with 85% of them (773 246) in South Africa (Sowetan, 2022). Masvingo had the largest number of emigrants of any province (153 384), of whom 104 716 were men (TellZim News, 2022) and in Matabeleland South about a third of households reported a member living abroad (Victoria Falls Live, 2022). The low ratios and slow growth of Masvingo and the south-west therefore describe the same process. The districts with more men than women are likely to reflect men moving to mines and commercial farms within the country, although this was not tested directly here.</p>
        <p>The analysis has several limits. The sex ratio counts people present on census night, so men working elsewhere in Zimbabwe are counted where they were, not where their families live and the emigration figures cover only emigrants who left a household behind. The population grid is based on WorldPop 2020 building patterns, scaled to 2022 totals, so new settlements built after 2020 may be placed in the wrong cells within their district. The results are best used to compare areas, not as exact counts for a single village.</p>

        <h2>7 Recommendations</h2>
        <p>Planning for housing, water and sanitation around Harare should treat Harare Rural, Seke, Goromonzi, Ruwa and Epworth as one growing urban area, since most of the growth of the capital now takes place outside the city boundary. Local authorities in these districts need budgets and staff that match populations that have doubled or tripled in ten years.</p>
        <p>In Masvingo and the border districts of Matabeleland South, where many men work abroad, agricultural extension, credit and land programmes should be designed with women farmers and female-headed households in mind. Remittances are an important source of income in these districts, so measures that lower the cost of sending money from South Africa and Botswana would reach many households.</p>
        <p>In the districts with more men than women, such as Bubi, Umguza, Umzingwane, Insiza and Mhondoro-Ngezi, health and housing plans should allow for a larger working-age male population around mining settlements.</p>
        <p>ZIMSTAT should publish district boundaries for 2012 and 2022 together with ward-level census tables by sex and age, so that growth can be measured on matching boundaries. The analysis should be repeated with the final 2022 ward totals when these become available.</p>

        <h2>8 Conclusion</h2>
        <p>Zimbabwe grew from 13 061 239 people in 2012 to 15 178 979 in 2022, an average of 1.51% per year. People are concentrated along the central watershed and in the north-east, while 57% of the land holds just 21% of the population, at fewer than 25 people per km². Growth was strongest in the districts around Harare and weakest in the cities of Harare and Bulawayo and in south-western Matabeleland South, where two districts lost people. Women outnumbered men by 599 863. The gap was widest in Masvingo, where low sex ratios and slow growth both point to men leaving for South Africa. These districts and the fast-growing ring around Harare are where planning and services should go first.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Bondarenko, M., Kerr, D., Sorichetta, A. and Tatem, A.J. (2020) Census/projection-disaggregated gridded population datasets for 51 countries across sub-Saharan Africa in 2020 using building footprints. WorldPop, University of Southampton. <a href="https://doi.org/10.5258/SOTON/WP00682" target="_blank" rel="noopener noreferrer">https://doi.org/10.5258/SOTON/WP00682</a></p>
          <p>Brinkhoff, T. (2025) Zimbabwe: Administrative Division. City Population. <a href="https://www.citypopulation.de/en/zimbabwe/admin/" target="_blank" rel="noopener noreferrer">https://www.citypopulation.de/en/zimbabwe/admin/</a></p>
          <p>ESA (2021) Copernicus DEM GLO-30. European Space Agency. <a href="https://doi.org/10.5270/ESA-c5d3d65" target="_blank" rel="noopener noreferrer">https://doi.org/10.5270/ESA-c5d3d65</a></p>
          <p>Natural Earth (2024) Admin 0 countries and lakes, 1:10 million. <a href="https://www.naturalearthdata.com" target="_blank" rel="noopener noreferrer">https://www.naturalearthdata.com</a></p>
          <p>OCHA (2023) Zimbabwe: Subnational Administrative Boundaries (COD-AB). Humanitarian Data Exchange. <a href="https://data.humdata.org/dataset/cod-ab-zwe" target="_blank" rel="noopener noreferrer">https://data.humdata.org/dataset/cod-ab-zwe</a></p>
          <p>Sowetan (2022) Most emigrants who left Zimbabwe are in SA or Botswana, statistics show. 7 September 2022. <a href="https://www.sowetan.co.za/news/africa/2022-09-07-most-emigrants-who-left-zimbabwe-are-in-sa-or-botswana-statistics-show/" target="_blank" rel="noopener noreferrer">https://www.sowetan.co.za/news/africa/2022-09-07-most-emigrants-who-left-zimbabwe-are-in-sa-or-botswana-statistics-show/</a></p>
          <p>TellZim News (2022) Masvingo province tops emigrants stats. <a href="https://tellzim.com/masvingo-province-tops-emigrants-stats/" target="_blank" rel="noopener noreferrer">https://tellzim.com/masvingo-province-tops-emigrants-stats/</a></p>
          <p>Victoria Falls Live (2022) Matabeleland has highest number of people living out of Zimbabwe. <a href="https://vicfallslive.co.zw/matabeleland-has-highest-number-of-people-living-out-of-zimbabwe" target="_blank" rel="noopener noreferrer">https://vicfallslive.co.zw/matabeleland-has-highest-number-of-people-living-out-of-zimbabwe</a></p>
          <p>ZIMSTAT (2012) Census 2012 National Report. Zimbabwe National Statistics Agency, Harare. <a href="https://www.zimstat.co.zw" target="_blank" rel="noopener noreferrer">https://www.zimstat.co.zw</a></p>
          <p>ZIMSTAT (2022) 2022 Population and Housing Census: Preliminary Report on Population Figures. Zimbabwe National Statistics Agency, Harare. <a href="https://www.zimstat.co.zw" target="_blank" rel="noopener noreferrer">https://www.zimstat.co.zw</a></p>
        </div>
      </CaseLayout>
    </>
  );
}
