import lulc from "../assets/LULC_2025.webp";
import cs4 from "../assets/casestudies/mazowe-valley/map2_bare_2025.webp";
import flood from "../assets/Chimanimani_Flood_Risk.webp";
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

// "/" on Vercel, "/Portifolio-website/" on GitHub Pages
const BASE = import.meta.env.BASE_URL;

export type Project = { title: string; slug: string; text: string; sub?: string; card?: string; img?: string; place?: string; years?: string };

/* Case studies, in order. Each has its own page under /case-studies/<slug>. */
export const CASESTUDIES: Project[] = [
  { title: "A Spatial Analysis of Population Distribution, Density and Growth in Zimbabwe Between the 2012 and 2022 Population Censuses", slug: "population-zimbabwe", card: "Population Distribution and Growth in Zimbabwe", sub: "District density, growth and sex ratio from the 2012 and 2022 censuses.", img: cs1, place: "Zimbabwe", years: "2012 and 2022",
    text: "District density and growth from the 2012 and 2022 censuses, a census-scaled 300 m population grid and the sex ratio of each district." },
  { title: "Assessing the Impact of Gold Mining on River Siltation in the Mazowe Valley from 2000 to 2025", slug: "mazowe-valley", card: "Gold Mining and River Siltation in the Mazowe Valley", sub: "Land disturbance and turbidity along 359 km of the Mazowe River.", img: cs4, place: "Mazowe Valley", years: "2000 to 2025",
    text: "Bare ground and turbidity along 359 km of the Mazowe River, with the clearest disturbance of the river corridor around Shamva." },
  { title: "A Spatial Analysis of Land Use and Land Cover Change in Bulawayo and the Marange Diamond Fields from 1987 to 2025", slug: "land-use-land-cover", card: "Land Use and Land Cover Change in Bulawayo and Marange", sub: "Urban growth, cultivation and diamond mining mapped from Landsat.", img: lulc, place: "Bulawayo and Mutare", years: "1987 to 2025",
    text: "Cultivation spreading over Bulawayo's grassland and woodland, house building in three northern suburbs and diamond mining across Ward 30 of Mutare Rural District." },
  { title: "Rainfall Variability and Drought Patterns in Zimbabwe from the 1991/92 to 2024/25 Agricultural Seasons", slug: "rainfall-zimbabwe", card: "Rainfall Variability and Drought in Zimbabwe", sub: "Seasonal rainfall, variability and drought frequency over 34 seasons.", img: cs2, place: "Zimbabwe", years: "1991 to 2025",
    text: "Mean October to April rainfall, its variability, the 2023/24 drought, drought frequency and trend by province from 34 seasons of rainfall data." },
];

export const PROJECTS: Project[] = [
  { title: "Flood Susceptibility Mapping of Chimanimani District and Gweru Urban Using Weighted Overlay Analysis", slug: "flood-susceptibility-mapping", card: "Flood Susceptibility in Chimanimani and Gweru", sub: "Weighted overlay of rainfall, slope, soils, drainage and land cover.", img: flood, place: "Chimanimani and Gweru",
    text: "Weighted overlay of rainfall, slope, elevation, soils, drainage and land cover to show where floods are most likely in a mountain district and a flat city." },
  { title: "Mapping Encroachment and Land Loss in Seven Gazetted Forests of Matabeleland North, Zimbabwe (2024)", slug: "zimbabwe-gazetted-forests", card: "Forest Encroachment in Matabeleland North", sub: "Clearing for cultivation in seven gazetted forests.", img: forest, place: "Matabeleland North",
    text: "How much of seven gazetted forests has been cleared for cultivation, where the clearing sits and what it means for forest protection." },
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
