import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { CASESTUDIES, PROJECTS, WEBMAPS, STORYMAPS } from "./catalogue";

// One place for every page's title, description and canonical address.
// Search engines run the site's JavaScript, so each route gets its own head tags as it opens.
export const SITE = "https://portfolio.spatialforce.co.zw";
const NAME = "Kudzanai Chakavarika";
const HOME = {
  title: `${NAME} | GIS and Remote Sensing Analyst`,
  text: "GIS and remote sensing analyst in Bulawayo, Zimbabwe. Case studies, web maps, story maps and 3D terrain work in spatial analysis, satellite imagery and cartography.",
};
const cut = (s: string) => (s.length > 158 ? s.slice(0, 155).replace(/\s+\S*$/, "") + "..." : s);

function lookup(path: string): { title: string; text: string } {
  const p = path.replace(/\/+$/, "") || "/";
  if (p === "/") return HOME;
  if (p === "/projects") return { title: `Case studies | ${NAME}`, text: "GIS and remote sensing case studies: population, rainfall and drought, land use change, mining, floods and forests, mostly in Zimbabwe." };
  if (p === "/projects/web-mapping") return { title: `Web maps | ${NAME}`, text: "Interactive web maps on earthquakes, cyclones, rivers, cities, health access, rainfall and more across Africa." };
  if (p === "/projects/story-maps") return { title: `Story maps | ${NAME}`, text: "ArcGIS story maps on Zimbabwe's wildlife heartlands and on different ways of mapping geospatial data." };
  let m = p.match(/^\/case-studies\/(.+)$/);
  if (m) { const c = CASESTUDIES.find((x) => x.slug === m![1]); if (c) return { title: `${c.title} | ${NAME}`, text: cut(c.text) }; }
  m = p.match(/^\/projects\/(.+)$/);
  if (m) { const c = PROJECTS.find((x) => x.slug === m![1]); if (c) return { title: `${c.title} | ${NAME}`, text: cut(c.text) }; }
  m = p.match(/^\/maps\/(.+)$/);
  if (m) { const w = WEBMAPS.find((x) => x.slug === m![1]); if (w) return { title: `${w.title} | Web map | ${NAME}`, text: cut(w.text) }; }
  m = p.match(/^\/stories\/(.+)$/);
  if (m) { const s = STORYMAPS.find((x) => x.slug === m![1]); if (s) return { title: `${s.title} | Story map | ${NAME}`, text: cut(s.text) }; }
  return HOME;
}

function setMeta(attr: "name" | "property", key: string, value: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
  if (!el) { el = document.createElement("meta"); el.setAttribute(attr, key); document.head.appendChild(el); }
  el.setAttribute("content", value);
}

export default function Seo() {
  const { pathname } = useLocation();
  useEffect(() => {
    const { title, text } = lookup(pathname);
    const url = SITE + (pathname === "/" ? "/" : pathname.replace(/\/+$/, ""));
    document.title = title;
    setMeta("name", "description", text);
    setMeta("property", "og:title", title);
    setMeta("property", "og:description", text);
    setMeta("property", "og:url", url);
    setMeta("name", "twitter:title", title);
    setMeta("name", "twitter:description", text);
    let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!link) { link = document.createElement("link"); link.rel = "canonical"; document.head.appendChild(link); }
    link.href = url;
  }, [pathname]);
  return null;
}
