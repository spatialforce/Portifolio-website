import lulc from "../assets/LULC_2025.webp";
import cs4 from "../assets/casestudies/mazowe-valley/map2_bare_2025.webp";
import forest from "../assets/gwaai.webp";
import quakes from "../assets/webmap_earthquakes.webp";
import sadc from "../assets/webmap_sadc.webp";
import gallery from "../assets/webmap_gallery.webp";
import migration from "../assets/webmap_migration.webp";
import rivers from "../assets/webmap_rivers.webp";
import malaria from "../assets/webmap_malaria.webp";
import heat from "../assets/webmap_heat.webp";
import dust from "../assets/webmap_dust.webp";
import lagos from "../assets/webmap_lagos.webp";
import sealevel from "../assets/webmap_flood.webp";
import cities from "../assets/webmap_cities.webp";
import corridors from "../assets/webmap_corridors.webp";
import languages from "../assets/webmap_languages.webp";
import elephants from "../assets/webmap_elephants.webp";
import mining from "../assets/webmap_mining.webp";
import cyclones from "../assets/webmap_cyclones.webp";
import rains from "../assets/webmap_rains.webp";
import hararehealth from "../assets/webmap_harare_health.webp";
import wildlife from "../assets/storymap_wildlife.webp";
import mapping from "../assets/storymap_mapping.webp";
import cs1 from "../assets/casestudies/population/map3_density_district.webp";
import cs2 from "../assets/casestudies/rainfall-zimbabwe/map2_mean.webp";
import cs7 from "../assets/casestudies/solar-site-suitability/map5_suitability.webp";
import cs16 from "../assets/casestudies/hwange-carbon/map3_carbon.webp";
import cs14 from "../assets/casestudies/hwange-air/map2_no2_post.webp";
import cs17 from "../assets/casestudies/chimanimani-flood/map3_susceptibility.webp";
import csLs from "../assets/casestudies/chimanimani-landslide/map3_susceptibility.webp";
import csPg from "../assets/casestudies/harare-health-access/map2_distance_all.webp";
import cs18 from "../assets/casestudies/sugarcane/map2_vigour.webp";
import cs19 from "../assets/casestudies/kariba/map3_exposed.webp";
import cs20 from "../assets/casestudies/bulawayo-landfill/map4_suitability.webp";
import cs21 from "../assets/casestudies/shurugwi-soil-erosion/map4_gully.webp";
import cs22 from "../assets/casestudies/baobab-habitat-suitability/map4_suitability.webp";
import cs23 from "../assets/casestudies/hwange-chizarira-corridor/map5_corridor.webp";
import cs24 from "../assets/casestudies/mukuvisi-runoff/map6_runoff.webp";
import cs25 from "../assets/casestudies/rainfall-interpolation/map2_surfaces.webp";

// "/" on Vercel, "/Portifolio-website/" on GitHub Pages
import covidDash from "../assets/dashboards/covid.webp";

const BASE = import.meta.env.BASE_URL;

export type Project = { title: string; slug: string; text: string; sub?: string; card?: string; img?: string; place?: string; years?: string };

/* Case studies, in order. Each has its own page under /case-studies/<slug>. */
export const CASESTUDIES: Project[] = [
  { title: "Site Suitability Analysis for Utility-Scale Solar Farms in Matabeleland South Province of Zimbabwe Using the Analytic Hierarchy Process", slug: "solar-site-suitability", card: "Solar Farm Site Suitability in Matabeleland South", sub: "AHP weighted overlay of six siting criteria on a 250 m grid.", img: cs7, place: "Matabeleland South", years: "2026",
    text: "Six siting criteria weighted by pairwise comparison and overlaid on a 250 m grid, placing the best land for utility-scale solar in Bulilima and Mangwe along the Plumtree transmission corridor." },
  { title: "Habitat Suitability Modelling for the African Baobab (Adansonia digitata) in Zimbabwe Using Maximum Entropy (MaxEnt)", slug: "baobab-habitat-suitability", card: "Baobab Habitat Suitability in Zimbabwe", sub: "Where the climate suits the African baobab, and how much of that land is protected.", img: cs22, place: "Zimbabwe", years: "1981 to 2010 climate",
    text: "About a third of Zimbabwe, 121 857 km², has a climate suitable for the baobab, mainly in the warm south-east lowlands and the Zambezi Valley. Winter temperature is the main control, and only 21.6 % of suitable land lies in protected areas." },
  { title: "Least-Cost Corridor Analysis for Elephant Movement Between Hwange and Chizarira National Parks, Zimbabwe", slug: "hwange-chizarira-corridor", card: "Elephant Corridor Between Hwange and Chizarira", sub: "Five weighted resistance factors used to trace the cheapest route and corridor between the two parks.", img: cs23, place: "Hwange and Binga", years: "2020 to 2021",
    text: "The cheapest route for elephants between the two parks runs 152.6 km, mostly through woodland and four wildlife management areas, and crosses three main roads. The corridor is narrowest (2.2 km) beside the Binga road." },
  { title: "Comparison of Spatial Interpolation Methods for Mean Annual Rainfall in Zimbabwe: Inverse Distance Weighting, Kriging and Thin-Plate Splines", slug: "rainfall-interpolation", card: "Comparing Rainfall Interpolation Methods", sub: "Four ways of mapping rainfall from gauges, tested against the gauges and satellite estimates.", img: cs25, place: "Zimbabwe", years: "1961 to 1990",
    text: "Ordinary kriging, universal kriging and a thin-plate spline matched within 1 % at 65 gauges; inverse distance weighting was less accurate. The methods agreed within 50 mm over 60 % of the country." },
  { title: "Watershed Delineation and Surface Runoff Estimation for the Mukuvisi Catchment, Harare, Using the SCS Curve Number Method", slug: "mukuvisi-runoff", card: "Storm Runoff in the Mukuvisi Catchment", sub: "A catchment traced from elevation data and its storm runoff estimated from land cover and soil.", img: cs24, place: "Harare", years: "1981 to 2025",
    text: "The 224 km² catchment has a mean curve number of 82.4. A 10-year storm of 60 mm would send a peak of about 145 m³/s past the outlet, most of it from the built-up west of the city." },
  { title: "A Spatial Analysis of Population Distribution, Density and Growth in Zimbabwe Between the 2012 and 2022 Population Censuses", slug: "population-zimbabwe", card: "Population Distribution and Growth in Zimbabwe", sub: "District density, growth and sex ratio from the 2012 and 2022 censuses.", img: cs1, place: "Zimbabwe", years: "2012 and 2022",
    text: "District density and growth from the 2012 and 2022 censuses, a census-scaled 300 m population grid and the sex ratio of each district." },
  { title: "Assessing the Impact of Gold Mining on River Siltation in the Mazowe Valley from 2000 to 2025", slug: "mazowe-valley", card: "Gold Mining and River Siltation in the Mazowe Valley", sub: "Land disturbance and turbidity along 359 km of the Mazowe River.", img: cs4, place: "Mazowe Valley", years: "2000 to 2025",
    text: "Bare ground and turbidity along 359 km of the Mazowe River, with the clearest disturbance of the river corridor around Shamva." },
  { title: "A Spatial Analysis of Land Use and Land Cover Change in Bulawayo and Ward 30 of Mutare Rural District from 1987 to 2025", slug: "land-use-land-cover", card: "Land Use and Land Cover Change in Bulawayo and Mutare Ward 30", sub: "Urban growth, cultivation and diamond mining mapped from Landsat.", img: lulc, place: "Bulawayo and Mutare", years: "1987 to 2025",
    text: "Cultivation spreading over Bulawayo's grassland and woodland, house building in three northern suburbs and diamond mining across Ward 30 of Mutare Rural District." },
  { title: "Rainfall Variability and Drought Patterns in Zimbabwe from the 1991/92 to 2024/25 Agricultural Seasons", slug: "rainfall-zimbabwe", card: "Rainfall Variability and Drought in Zimbabwe", sub: "Seasonal rainfall, variability and drought frequency over 34 seasons.", img: cs2, place: "Zimbabwe", years: "1991 to 2025",
    text: "Mean October to April rainfall, its variability, the 2023/24 drought, drought frequency and trend by province from 34 seasons of rainfall data." },
  { title: "Above-Ground Carbon Stock Estimation in Hwange National Park Using GEDI LiDAR and Random Forest Regression (2019 to 2023)", slug: "hwange-carbon", card: "Above-Ground Carbon Stock of Hwange National Park", sub: "GEDI LiDAR footprints upscaled to a 100 m carbon map with Random Forest.", img: cs16, place: "Hwange National Park", years: "2019 to 2023",
    text: "Laser footprints from space upscaled to a 100 m map, placing about 7.87 Mt of above-ground carbon in the park (plausibly 4 to 12 Mt), two thirds of it in shrubland where a global biomass map gives far less." },
  { title: "Nitrogen Dioxide and Sulphur Dioxide Pollution from the Hwange Thermal Power Station Expansion Using Sentinel-5P (2019 to 2025)", slug: "hwange-air", card: "Air Pollution from the Hwange Power Station Expansion", sub: "Seven years of Sentinel-5P NO₂ and SO₂ before and after Units 7 and 8, against a control station.", img: cs14, place: "Hwange", years: "2019 to 2025",
    text: "NO₂ and SO₂ above the regional background about doubled over Hwange after Units 7 and 8 came into service, with no change at the Maamba control, and about 20 500 people now live where NO₂ is twice the background." },
  { title: "Flood Susceptibility Mapping of Chimanimani District Using GIS-Based Multi-Criteria Analysis and the Analytic Hierarchy Process", slug: "chimanimani-flood", card: "Flood Susceptibility of Chimanimani District", sub: "Eight factors reclassified, weighted with AHP and combined by weighted overlay.", img: cs17, place: "Chimanimani", years: "1991 to 2020",
    text: "High and very high flood susceptibility covers 31 % of the district, mostly the western lowlands and the valley floors of the highlands, and holds about 63 % of its buildings and people." },
  { title: "Landslide Susceptibility Mapping of Chimanimani District Using GIS-Based Multi-Criteria Analysis and the Analytic Hierarchy Process", slug: "chimanimani-landslide", card: "Landslide Susceptibility of Chimanimani District", sub: "Eight factors reclassified, weighted with AHP and checked against mapped landslides.", img: csLs, place: "Chimanimani", years: "1991 to 2020",
    text: "High and very high landslide susceptibility covers 39 % of the district, almost all on the steep, wet eastern highlands, and holds 95 % of the mapped landslides (AUC 0.867) and about 28 % of its buildings."},
  { title: "Network Analysis of Walking Access to Public Health Facilities in Harare Using PostGIS and pgRouting", slug: "harare-health-access", card: "Walking Access to Health Facilities in Harare", sub: "Shortest walks on the street network to the nearest clinic, worked out in PostGIS and pgRouting.", img: csPg, place: "Harare", years: "2025 to 2026",
    text: "57 % of the 2.69 million people in Harare Metropolitan Province live within a 2 km walk of a mapped clinic or hospital, but only 19 % of a listed public one, and five new clinics would bring about 239 000 more within 2 km."},
  { title: "Field-Level Sugarcane Monitoring at Triangle and Hippo Valley Using Remote Sensing (2019 to 2025)", slug: "sugarcane-triangle", card: "Sugarcane Field Monitoring at Triangle and Hippo Valley", sub: "Seven years of monthly satellite greenness and moisture, followed field by field.", img: cs18, place: "Triangle and Hippo Valley", years: "2019 to 2025",
    text: "1 947 cane fields covering 16 272 ha were traced from seven years of monthly Sentinel-2 images, with harvest month, vigour and consistently weak fields mapped for each." },
  { title: "Area–Elevation–Storage Relationships and Water Level Decline at Lake Kariba (2000 to 2025)", slug: "lake-kariba", card: "Water Level Decline at Lake Kariba", sub: "Satellite altimetry paired with Landsat lake areas to build the storage curve.", img: cs19, place: "Lake Kariba", years: "2000 to 2025",
    text: "Mean live storage halved between 2000 to 2009 and 2016 to 2025, the lake reached its minimum operating level every year from 2022, and 850 km² of lake bed was left dry. The satellite storage curve matches the operator's figures to within about 1 %." },
  { title: "Landfill Site Selection for Bulawayo Using GIS-Based Multi-Criteria Analysis", slug: "bulawayo-landfill", card: "Landfill Site Selection for Bulawayo", sub: "Six weighted criteria used to find land fit for a new landfill.", img: cs20, place: "Bulawayo", years: "2021 to 2024",
    text: "Only 51.4 km² (9.4 %) of Bulawayo is highly or very highly suitable for a landfill, while 43.5 % is very low. Four candidate sites of 154 to 1 864 ha were found, and the existing Richmond landfill falls in the very low class." },
  { title: "Assessment of Soil Erosion and Gully Erosion Risk in Shurugwi District, Zimbabwe", slug: "shurugwi-soil-erosion", card: "Soil Erosion and Gully Erosion Risk in Shurugwi", sub: "Where soil is washed away and where gullies are likely to form, ranked by ward.", img: cs21, place: "Shurugwi", years: "2019 to 2024",
    text: "Shurugwi loses about 1.57 million tonnes of soil a year, a mean of 4.36 t/ha/yr. Soil loss is highest on the steep northern and western hills, while the 529 km² at high gully risk lie mostly on the thinly covered lower ground of the south and east." },
  { title: "Mapping Encroachment and Land Loss in Seven Gazetted Forests of Matabeleland North, Zimbabwe (2024)", slug: "zimbabwe-gazetted-forests", card: "Forest Encroachment in Matabeleland North", sub: "Clearing for cultivation in seven gazetted forests.", img: forest, place: "Matabeleland North", years: "2024",
    text: "How much of seven gazetted forests has been cleared for cultivation, where the clearing sits and what it means for forest protection." },
];

export const PROJECTS: Project[] = [
  { title: "Web mapping", slug: "web-mapping", img: quakes, place: "In the browser",
    text: "Interactive maps built on open data." },
  { title: "Story maps", slug: "story-maps", img: wildlife, place: "Zimbabwe",
    text: "Maps and photographs told as a story you scroll through." },
  { title: "Remote sensing indices", slug: "remote-sensing-indices",
    text: "Spectral indices such as NDVI and NDWI from satellite imagery." },
  { title: "Fire susceptibility mapping", slug: "fire-susceptibility-mapping",
    text: "Wildfire risk zones from vegetation and climate data." },
];

export type StoryMap = { slug: string; title: string; text: string; img: string; src: string; stack: string[] };

export const STORYMAPS: StoryMap[] = [
  { slug: "zimbabwe-wildlife", title: "Zimbabwe's Wildlife Heartlands", img: wildlife,
    src: "https://storymaps.arcgis.com/stories/b02635a5e5b14dc38245b44ecc1ac632",
    text: "A journey through the parks and safari areas that keep Zimbabwe wild. From the elephant herds of Hwange to the rhinos of the Matobo Hills.",
    stack: ["ArcGIS StoryMaps", "ArcGIS Online"] },
  { slug: "mapping-geospatial-data", title: "Mapping Geospatial Data", img: mapping,
    src: "https://storymaps.arcgis.com/stories/8dd0af85af5e40dc97ecec44746021c8",
    text: "An exploration of different cartographic techniques and how they can be used to represent, interpret and communicate spatial information through maps of Zimbabwe.",
    stack: ["ArcGIS StoryMaps", "ArcGIS Online"] },
];

export const DASHBOARDS: StoryMap[] = [
  { slug: "covid-19", title: "COVID-19 Dashboard", img: covidDash,
    src: "https://public.tableau.com/views/covid_dashboard_17946409485600/COVID-19Dashboard?:showVizHome=no&:embed=true&:toolbar=bottom",
    text: "Cases, deaths and vaccination from 2020 to 2026: a world map of deaths per million, the SADC countries compared and weekly trends.",
    stack: ["Tableau Public", "Python"] },
];

export type WebMap = {
  slug: string; title: string; short: string; text: string; img: string; src: string;
  stack: string[]; data: string[];
};

export const WEBMAPS: WebMap[] = [
  { slug: "earthquakes", title: "Global Earthquake Distribution", src: BASE + "webmaps/earthquakes.html", img: quakes,
    short: "A 3D visualisation of earthquake locations, magnitudes and depths across the world.",
    text: "Earthquakes from around the world on a flat map or a globe. Filter by magnitude and year to see where the ground shakes most.",
    stack: ["three.js", "WebGL", "USGS API"], data: ["USGS Earthquake Hazards Program"] },
  { slug: "event-gallery", title: "A Gallery of Disasters", src: BASE + "event-gallery/", img: gallery,
    short: "Tracking the spatial extent and impacts of major natural disasters using satellite data.",
    text: "Floods and fires and eruptions mapped from satellite imagery with before and after views.",
    stack: ["React", "Leaflet", "Google Earth Engine", "Python"], data: ["Copernicus Sentinel-2", "Landsat", "GHSL", "NASA GIBS"] },
  { slug: "sadc", title: "Development Indicators Across Southern Africa", src: BASE + "webmaps/sadc.html", img: sadc,
    short: "A comparative analysis of socio-economic and development patterns across SADC member states.",
    text: "Compare the 16 SADC countries on World Bank indicators and follow how each has changed over time.",
    stack: ["D3", "Chart.js", "World Bank API"], data: ["World Bank Open Data"] },
  { slug: "mining-footprint", title: "Mining Activities Across Zimbabwe", src: BASE + "webmaps/mining.html", img: mining,
    short: "A satellite-based assessment of mining expansion.",
    text: "Seven mines seen from space before and after. Compare the two years side by side and see how much ground has been stripped bare.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["Copernicus Sentinel-2", "USGS Landsat 5 and 7", "JRC Global Surface Water"] },
  { slug: "rivers", title: "Mapping Africa's River Networks and Drainage Basins", src: BASE + "webmaps/rivers.html", img: rivers,
    short: "Exploring the continent's river systems and the pathways water follows from source to outlet.",
    text: "Every river in Africa drawn by how much water it carries. Explore a river system or drop rain anywhere and follow it downhill to the sea.",
    stack: ["Python", "GeoPandas", "WebGL"], data: ["HydroRIVERS", "HydroBASINS", "Natural Earth"] },
  { slug: "cities", title: "Urban Expansion Across Africa", src: BASE + "webmaps/cities.html", img: cities,
    short: "A spatial analysis of how selected African cities have expanded between 1975 and 2020.",
    text: "Ten African cities side by side on the same scale as their built-up land spreads. Press play to watch them grow or open a city for its growth curve.",
    stack: ["Python", "Earth Engine", "WebGL"], data: ["GHSL built-up surface (JRC)"] },
  { slug: "corridors", title: "Trade Corridors of Southern Africa", src: BASE + "webmaps/corridors.html", img: corridors,
    short: "Mapping the rail and road routes that link Southern Africa's interior to its seaports.",
    text: "Eight corridors from seven ports traced along the real rail and road network. Pick one to see its route and its border posts.",
    stack: ["Python", "GeoPandas", "NetworkX", "Canvas"], data: ["Natural Earth"] },
  { slug: "languages", title: "Mapping the Languages of Southern Africa", src: BASE + "webmaps/languages.html", img: languages,
    short: "Exploring the region's linguistic diversity and the geographical distribution of nearly 200 languages.",
    text: "Nearly two hundred languages coloured by group or by how endangered they are. Open one to see its speakers and hear native speakers where recordings exist.",
    stack: ["Python", "Shapely", "Canvas"], data: ["Glottolog", "Wikidata", "Lingua Libre", "Natural Earth"] },
  { slug: "elephants", title: "Elephant Movement Patterns", src: BASE + "webmaps/elephants.html", img: elephants,
    short: "GPS-tracked elephant movements across Etosha and Kruger National Parks.",
    text: "GPS-collared elephants played back through the wet and dry seasons. Follow one animal or show every path to see the herds return to the same waterholes.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["Movebank", "Copernicus Sentinel-2", "WDPA"] },
  { slug: "cyclones", title: "Tropical Cyclone Tracks in the South-West Indian Ocean", src: BASE + "webmaps/cyclones.html", img: cyclones,
    short: "Mapping the tracks and paths of tropical cyclones across the South-West Indian Ocean since 1980.",
    text: "Close to four hundred storms from Eline to Idai and Chido. Pick one to watch it cross the ocean coloured by its wind and see which countries it hit.",
    stack: ["Python", "GeoPandas", "Canvas"], data: ["IBTrACS (NOAA)", "Natural Earth"] },
  { slug: "rains", title: "Rainfall Onset Across Southern Africa", src: BASE + "webmaps/rains.html", img: rains,
    short: "Mapping the start date of the rainy season for every season since 1981.",
    text: "The date the rains properly start across Southern Africa for every season since 1981. Click any place to see whether its rains come earlier or later.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["CHIRPS v2.0", "Natural Earth"] },
  { slug: "malaria", title: "Malaria Prevalence Across Africa", src: BASE + "webmaps/malaria.html", img: malaria,
    short: "Tracking the prevalence of malaria among children across Africa from 2000 to 2025.",
    text: "The share of children carrying malaria parasites across Africa for every year from 2000 to 2025. Press play to watch it change or click any place for its own trend.",
    stack: ["Python", "Rasterio", "Canvas"], data: ["Malaria Atlas Project", "Natural Earth"] },
  { slug: "heat", title: "Urban Heat Islands in African Cities", src: BASE + "webmaps/heat.html", img: heat,
    short: "Mapping urban heat patterns and identifying cities where built-up areas experience higher temperatures than their surrounding rural landscapes.",
    text: "Ground temperature across African cities on a clear mid-morning from Landsat. See which neighbourhoods run hot and which stay cool and switch to the satellite image to see why.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["Landsat 8 and 9 (USGS)", "GHSL", "Copernicus Sentinel-2"] },
  { slug: "dust", title: "Saharan Dust Transport", src: BASE + "webmaps/dust.html", img: dust,
    short: "Visualising how dust from the Sahara travels across continents and oceans.",
    text: "Watch dust from the Sahara blow across the Atlantic to the Caribbean and north into Europe every three hours through major outbreaks from 2020 to 2026. Click anywhere for how much sunlight the dust blocked there.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["NASA MERRA-2 (GMAO)", "Natural Earth"] },
  { slug: "lagos", title: "Land Reclamation and Urban Expansion in Lagos", src: BASE + "webmaps/lagos.html", img: lagos,
    short: "Mapping the expansion of Lagos through land reclamation from the Atlantic Ocean and surrounding lagoons since 2001.",
    text: "The Lagos coast in 2001 and today side by side. Eko Atlantic and the filled lagoon shores are outlined and measured from the satellite images.",
    stack: ["Python", "Earth Engine", "Canvas"], data: ["Landsat 7 and 8 (USGS)", "Copernicus Sentinel-2"] },
  { slug: "flood", title: "Visualising Sea-Level Rise in Portsmouth", src: BASE + "webmaps/flood.html", img: sealevel,
    short: "A 3D exploration of Portsmouth's urban landscape under different sea-level rise scenarios.",
    text: "Raise the sea over a 3D model of Portsmouth with every building at its height from 1 m LiDAR. Water only reaches ground that is lower than the sea and open to it so land behind a wall stays dry until the wall is topped.",
    stack: ["Python", "LiDAR", "three.js"], data: ["Environment Agency LIDAR Composite", "OpenStreetMap"] },
  { slug: "harare-health", title: "Access to Health Facilities in Harare", img: hararehealth,
    src: "https://www.arcgis.com/apps/Embed/index.html?webmap=82868f52546a4e31bad6dae12c5dea96&zoom=true&scale=true&legendlayers=true",
    short: "A network analysis of walking times to the nearest clinic across Harare.",
    text: "Walking time to the nearest of Harare's 151 clinics measured along the real roads. About 980 000 people live more than 30 minutes away on foot. Five proposed sites would bring 270 000 of them within reach.",
    stack: ["ArcGIS Online", "Arcade", "Python", "SciPy"], data: ["Health facilities", "OpenStreetMap", "WorldPop 2025"] },
  { slug: "migration", title: "Seasonal Wildlife Migration Patterns", src: BASE + "webmaps/migration.html", img: migration,
    short: "Mapping the seasonal movements and migration routes of wildlife across different landscapes.",
    text: "Watch migratory species move across the world month by month.",
    stack: ["WebGL", "GBIF API", "Python"], data: ["GBIF", "Natural Earth", "Wikimedia Commons"] },
];
