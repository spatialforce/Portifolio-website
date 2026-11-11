import lulc from "../assets/LULC_2025.webp";
import zim from "../assets/Zimbabwe.webp";
import flood from "../assets/Chimanimani_Flood_Risk.webp";
import drought from "../assets/Drought_Province_Choropleth.webp";
import forest from "../assets/gwaai.webp";

export type Project = { title: string; slug: string; text: string; img?: string };

export const PROJECTS: Project[] = [
  { title: "Land Use & Land Cover Change", slug: "land-use-land-cover", img: lulc,
    text: "Satellite-based change analysis: urban cultivation in Bulawayo from 1987 to 2025, diamond mining at Chiyadzwa in Mutare, and built-up growth in three Bulawayo suburbs." },
  { title: "Study Area Maps", slug: "study-area-maps", img: zim,
    text: "A collection of study area and site location maps produced for projects across Zimbabwe." },
  { title: "Flood Susceptibility Mapping", slug: "flood-susceptibility-mapping", img: flood,
    text: "A weighted-overlay flood risk map of Chimanimani District, and a Sentinel-1 radar study of Gweru Urban." },
  { title: "Drought Hotspots in Zimbabwe", slug: "drought-analysis", img: drought,
    text: "Satellite vegetation and temperature records turned into a national picture of drought severity by province." },
  { title: "Zimbabwe Gazetted Forests", slug: "zimbabwe-gazetted-forests", img: forest,
    text: "Boundary maps, legal status and encroachment figures for seven gazetted forests in Matabeleland." },
  { title: "Remote Sensing Indices", slug: "remote-sensing-indices",
    text: "Spectral indices such as NDVI and NDWI derived from satellite imagery. Coming soon." },
  { title: "Fire Susceptibility Mapping", slug: "fire-susceptibility-mapping",
    text: "Wildfire risk zones based on vegetation, terrain and climate. Coming soon." },
  { title: "Web Mapping", slug: "web-mapping",
    text: "Interactive web maps and dashboards. Coming soon." },
];
