import slovenia from "../assets/gallery/slovenia_landcover_2025.webp";
import zimbabwe from "../assets/Zimbabwe.webp";
import erosion from "../assets/gallery/masvingo_soil_erosion.webp";
import mbire from "../assets/Mbire.webp";
import austria from "../assets/gallery/austria_landcover_2025.webp";
import gambia from "../assets/gallery/gambia_landcover_2025.webp";
import matopo from "../assets/matopo.webp";
import bulawayo from "../assets/bulawayo.webp";
import mutare from "../assets/mutare.webp";
import gweru from "../assets/gweru.webp";
import matopo2 from "../assets/matopo2.webp";
import gokwe from "../assets/gokwe.webp";
import chirumhanzu from "../assets/Chirumhanzu.webp";
import dhlodhlo from "../assets/gallery/dhlodhlo_species_distribution_2025.webp";
import karibaPoster from "../assets/gallery/kariba_3d_rotating_poster.webp";
import flyoverPoster from "../assets/gallery/terrain_3d_flyover_poster.webp";

export type Slide = { img: string; title: string };

/* The map gallery on the home page, in this order. */
export const GALLERY: Slide[] = [
  { img: slovenia, title: "Slovenia land cover" },
  { img: zimbabwe, title: "Zimbabwe study area" },
  { img: erosion, title: "Masvingo soil erosion" },
  { img: mbire, title: "Mbire District" },
  { img: austria, title: "Austria land cover" },
  { img: gambia, title: "The Gambia land cover" },
  { img: matopo, title: "Matopo National Park" },
  { img: bulawayo, title: "Bulawayo" },
  { img: mutare, title: "Mutare" },
  { img: gweru, title: "Gweru" },
  { img: matopo2, title: "Matopo mining claims" },
  { img: gokwe, title: "Gokwe" },
  { img: chirumhanzu, title: "Chirumhanzu" },
  { img: dhlodhlo, title: "Dhlodhlo species distribution" },
];

export type Render = { title: string; text: string; video?: string; poster: string; img?: string; light?: boolean; ratio: string; tools: string[] };

/* 3D terrain work. Videos live in public/videos so they stream instead of being bundled.
   Both loop without a jump: the model turns there and back, the fly through fades its end into its start.
   ?v= changes whenever a video file is replaced so browsers do not keep the old one. */
export const RENDERS: Render[] = [
  { title: "3D model", video: import.meta.env.BASE_URL + "videos/kariba_3d_rotating.mp4?v=7", poster: karibaPoster, light: true, ratio: "16 / 9",
    text: "A block model turning slowly so the relief reads from every side.", tools: ["Elevation model", "Hillshade", "3D render"] },
  { title: "3D fly through", video: import.meta.env.BASE_URL + "videos/terrain_3d_flyover.mp4?v=2", poster: flyoverPoster, ratio: "16 / 9",
    text: "A low flight over terrain with colour following elevation from valley floor to summit.", tools: ["Elevation model", "Hypsometric tints", "3D render"] },
];
