import { useState, useEffect, useRef } from "react";
import profile from "./assets/profile_1.webp";
import erosionImg from "./assets/erosion.webp";
import watershedImg from "./assets/watershed.webp";
import lulcImg from "./assets/LULC.webp";
import webMapImg from "./assets/webmapping.webp";
import terrain3DImg from "./assets/3D.webp";
const TOOLS = [
  "ArcGIS Pro","QGIS","Google Earth Engine","Google Earth Pro",
  "SEPAL","Global Mapper","ENVI Classic","ArcGIS Online", "ArcMap",
  "OpenLayers","GRASS GIS","ArcGIS Experience Builder",
  "Leaflet.js","FME Desktop","ERDAS Imagine","ArcGIS StoryMaps"
];

const SERVICES = [
  { mark:"△", title:"Spatial Analysis", body:"Terrain modelling, watershed delineation, overlay analysis, and multi-criteria decision support — translating geographic complexity into clear, actionable intelligence." },
  { mark:"▦", title:"Remote Sensing & Image Classification", body:"Land cover and land use mapping, NDVI and vegetation health indices, and temporal change detection from multispectral and hyperspectral satellite imagery." },
  { mark:"◎", title:"Web Mapping & GIS Portals", body:"Interactive web maps, dashboards, and geoportals using ArcGIS Online, Experience Builder, StoryMaps, and open-source libraries — spatial data accessible to any audience." },
  { mark:"⟡", title:"Natural Resource Management", body:"Spatial analysis in support of conservation planning, biodiversity inventories, environmental impact assessment, and sustainable land-use decision making." },
];

const COMPETENCIES = [
  { label:"Spatial Analysis & Geoprocessing", pct:95 },
  { label:"Remote Sensing & Image Analysis", pct:90 },
  { label:"ESRI Platform — Pro, Online, StoryMaps", pct:93 },
  { label:"Open Source GIS — QGIS, GRASS, GDAL", pct:88 },
  { label:"Web Mapping & GIS Portals", pct:84 },
  { label:"Natural Resource Management", pct:90 },
];

const CONTACT_ITEMS = [
  { lbl:"Email", val:"kudzanaichakavarika67@gmail.com", href:"mailto:kudzanaichakavarika67@gmail.com" },
  { lbl:"Phone / WhatsApp", val:"+263 779 135 076", href:"tel:+263779135076" },
  { lbl:"LinkedIn", val:"Kudzanai Chakavarika", href:"https://linkedin.com/in/kudzanai-chakavarika" },
  { lbl:"GitHub", val:"Spatial Force", href:"https://github.com/spatialforce" },
  { lbl:"Website", val:"spatialforce.co.zw", href:"https://spatialforce.co.zw" },
];

const PROJECTS = [
  {
    id:"01",
    title:"Chimanimani District Watershed Delineation",
    tags:["Hydrology","Watershed Analysis","GIS"],
    desc:"Watershed delineation and drainage network extraction for Chimanimani District using digital elevation models (DEMs). The analysis identified catchment boundaries, stream networks, flow direction and flow accumulation patterns to support water resource management and environmental planning.",
    img: watershedImg
  },
  {
    id:"02",
    title:"Land Use/Land Cover (LULC) Mapping — Bulawayo",
    tags:["Remote Sensing","LULC","Sentinel-2","GIS"],
    desc:"Land Use/Land Cover classification of Bulawayo using satellite imagery and supervised classification techniques. The study mapped urban expansion, vegetation cover, bare land and built-up areas to support spatial planning and environmental monitoring.",
    img: lulcImg
  },
  {
    id:"03",
    title:"Fire Command & Response Web Mapping System — Bulawayo",
    tags:["Web GIS","Leaflet.js","Emergency Response","Dashboard"],
    desc:"An interactive fire response and dispatch system designed for Bulawayo. The platform allows users to report fire incidents in real time, which are then visualized on a central command dashboard. Fire locations are monitored spatially to support rapid resource allocation and efficient emergency response coordination.",
    img: webMapImg
  },
  {
    id:"04",
    title:"Masvingo Province Soil Erosion Modelling",
    tags:["RUSLE","GIS Modelling","Remote Sensing"],
    desc:"Soil erosion risk assessment across Masvingo Province using the Revised Universal Soil Loss Equation (RUSLE). Integrated rainfall erosivity, soil erodibility, slope factors, land cover, and conservation practices to identify erosion hotspots and support sustainable land management.",
    img: erosionImg
  },
  {
    id:"05",
    title:"3D Terrain Visualization & Relief Modelling",
    tags:["3D GIS","DEM","Terrain Analysis","Blender"],
    desc:"High-resolution 3D terrain visualization generated from Digital Surface Model (DSM) data. Elevation surfaces were processed and rendered into a realistic relief model to enhance the interpretation of topographic features, slope variation, drainage patterns and landscape morphology.",
    img: terrain3DImg
  }
];

const TAGLINES = [
  "I analyze hydrological systems, forests and urban environments",
  "I turn satellite data into field-ready answers",
  "I build web maps people actually use",
  "I turn spatial data into web maps that deliver real impact",
];

const GRID_REF = ["28°30'E","28°33'E","28°36'E","28°39'E","28°42'E","28°45'E","28°48'E"];

export default function App() {
  const [navOpen, setNavOpen] = useState(false);
  const [navScrolled, setNavScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setNavScrolled(window.scrollY > 50);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);
  return (
    <>
      <style>{CSS}</style>
      <Nav navOpen={navOpen} setNavOpen={setNavOpen} navScrolled={navScrolled} />
      <Hero />
      <About />
      <Projects />
      <Services />
      <Skills />
      <Contact />
      <SiteFooter />
    </>
  );
}

/* ── GRATICULE — the signature device. A coordinate ruler,
   reused thin between sections instead of plain hairlines. ── */
function Graticule({ variant = "full" }: { variant?: "full" | "thin" }) {
  return (
    <div className={`grat grat--${variant}`} aria-hidden="true">
      {GRID_REF.map((t, i) => (
        <div className="grat__tick" key={i}>
          <span className="grat__mark" />
          {variant === "full" && <span className="grat__label">{t}</span>}
        </div>
      ))}
    </div>
  );
}

/* ── NAV ──────────────────────────────────────────────────────── */
function Nav({ navOpen, setNavOpen, navScrolled }: { navOpen:boolean; setNavOpen:(v:boolean)=>void; navScrolled:boolean }) {
  const links = ["Home","About","Projects","Services","Skills","Contact"];

  useEffect(() => {
    document.body.style.overflow = navOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [navOpen]);

  useEffect(() => {
    if (!navOpen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setNavOpen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navOpen, setNavOpen]);

  return (
    <>
      <header className={`nav${navScrolled || navOpen ? " nav--scrolled" : ""}`}>
        <a href="#home" className="nav__mark">KC<span>/</span>SPATIAL</a>
        <ul className={`nav__menu${navOpen ? " open" : ""}`}>
          <li className="nav__menu-close">
            <button type="button" onClick={() => setNavOpen(false)} aria-label="Close menu">×</button>
          </li>
          {links.map((l,i) => (
            <li key={l}><a href={`#${l.toLowerCase()}`} onClick={() => setNavOpen(false)}><em>{String(i+1).padStart(2,"0")}</em>{l}</a></li>
          ))}
        </ul>
        <button className={`nav__burger${navOpen ? " open" : ""}`} onClick={() => setNavOpen(!navOpen)} aria-label="Menu">
          <span/><span/><span/>
        </button>
      </header>
      {navOpen && <button type="button" className="nav__backdrop" aria-label="Close menu" onClick={() => setNavOpen(false)} />}
    </>
  );
}

/* ── HERO ─────────────────────────────────────────────────────── */
function Hero() {
  const [roleIndex, setRoleIndex] = useState(0);
  const [displayed, setDisplayed] = useState("");
  const [deleting, setDeleting] = useState(false);
  const charRef = useRef(0);

  useEffect(() => {
    const target = TAGLINES[roleIndex];
    const speed = deleting ? 55 : 90;
    const timer = setTimeout(() => {
      if (!deleting) {
        if (charRef.current < target.length) {
          charRef.current++;
          setDisplayed(target.slice(0, charRef.current));
        } else {
          setTimeout(() => setDeleting(true), 1800);
        }
      } else {
        if (charRef.current > 0) {
          charRef.current--;
          setDisplayed(target.slice(0, charRef.current));
        } else {
          setDeleting(false);
          setRoleIndex(i => (i + 1) % TAGLINES.length);
        }
      }
    }, speed);
    return () => clearTimeout(timer);
  }, [displayed, deleting, roleIndex]);

  return (
    <section id="home" className="hero">
      <Graticule variant="full" />
      <div className="hero__inner">
        <div className="hero__text">
          <p className="hero__status"><span/>Available for new projects</p>
          <p className="hero__eyebrow">Geospatial Analyst — BSc GIS &amp; Remote Sensing in Natural Resources  Management</p>
          <h1 className="hero__heading">
            Kudzanai<br/><em>Chakavarika</em>
          </h1>
          <div className="hero__typing">{displayed}<span className="hero__cursor">_</span></div>
          <p className="hero__desc">
            I transform raw spatial data into clear decisions from satellite imagery to
            interactive web maps grounded in deep expertise across natural resources and
            the full ESRI &amp; open-source GIS stack.
          </p>
          <div className="hero__cta">
            <a href="#contact" className="btn-solid">Hire Me</a>
            <a href="/cv.pdf" target="_blank" rel="noopener noreferrer" className="btn-line">View CV</a>
            <div className="hero__socials">
              <a href="https://www.linkedin.com/in/kudzanai-chakavarika-65a847372" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>
              </a>
              <a href="https://github.com/spatialforce" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
              </a>
            </div>
          </div>
        </div>

        <div className="hero__photo">
        <img src={profile} alt="Kudzanai Chakavarika" decoding="async" />
          <div className="hero__readout">
            <div><strong>40+</strong><span>Projects completed</span></div>
            <div><strong>ZW</strong><span>Based, Bulawayo</span></div>
            <div><strong>Global</strong><span>Client reach</span></div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── ABOUT ────────────────────────────────────────────────────── */
function About() {
  return (
    <section id="about" className="about">
      <p className="section-tag">§ About</p>
      <div className="about__grid">
        <h2 className="about__lede">
          Spatial intelligence<br/>for complex, on the ground problems.
        </h2>
        <div className="about__copy">
          <p>I'm Kudzanai Chakavarika, a geospatial analyst with a BSc in Geographic Information Systems and Remote Sensing in Natural Resources Management, based in Bulawayo, Zimbabwe.</p>
          <p>My work spans the full geospatial workflow from acquiring and preprocessing satellite imagery to building analytical models, generating publication-quality cartography and deploying spatial data as interactive web experiences.</p>
          <p>I'm fluent across ESRI's professional stack -  ArcGIS Pro, ArcGIS Online, StoryMaps, Experience Builder as well as open-source, paid and cloud platforms including QGIS, Google Earth Engine, SEPAL, ENVI Classic and Global Mapper.</p>
          <ul className="about__facts">
            <li><span>Based</span>Bulawayo, Zimbabwe</li>
            <li><span>Education</span>BSc GIS &amp; Remote Sensing · NRM</li>
            <li><span>Availability</span>Open to projects globally</li>
            <li><span>Web</span>spatialforce.co.zw</li>
          </ul>
        </div>
      </div>
    </section>
  );
}


function Projects() {
  const [lightbox, setLightbox] = useState<number | null>(null);

  useEffect(() => {
    if (lightbox === null) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setLightbox(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [lightbox]);

  return (
    <section id="projects" className="projects">
      <p className="section-tag section-tag--light">§ Selected Work</p>

      <div className="proj-list">
        {PROJECTS.map((p, i) => (
          <article key={p.id} className="proj-row">
            <button
              type="button"
              className="proj-frame"
              onClick={() => setLightbox(i)}
              aria-label={`View larger image of ${p.title}`}
            >
              <img src={p.img} alt={p.title} loading="lazy" /> 
                <span className="proj-frame__tag">View full image ↗</span>
            </button>
            <div className="proj-info">
              <span className="proj-info__ref">Sheet No. {p.id}/{String(PROJECTS.length).padStart(2,"0")}</span>
              <h3>{p.title}</h3>
              <p>{p.desc}</p>
              <div className="proj-info__tags">{p.tags.map(t => <span key={t}>{t}</span>)}</div>
            </div>
          </article>
        ))}
      </div>

      {lightbox !== null && (
        <div className="lightbox" onClick={() => setLightbox(null)}>
          <button className="lightbox__close" onClick={() => setLightbox(null)} aria-label="Close">×</button>
          <img
            src={PROJECTS[lightbox].img}
            alt={PROJECTS[lightbox].title}
            className="lightbox__img"
            onClick={(e) => e.stopPropagation()}
          />
          <p className="lightbox__caption" onClick={(e) => e.stopPropagation()}>{PROJECTS[lightbox].title}</p>
        </div>
      )}
    </section>
  );
}

/* ── SERVICES — rendered as a map legend, not a 4-up card grid ── */
function Services() {
  return (
    <section id="services" className="services">
      <p className="section-tag">§ What I Do</p>
      <div className="legend">
        {SERVICES.map(s => (
          <div key={s.title} className="legend__row">
            <div className="legend__head">
              <span className="legend__mark">{s.mark}</span>
              <h3>{s.title}</h3>
            </div>
            <p>{s.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── SKILLS ───────────────────────────────────────────────────── */
function Skills() {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const ob = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold: 0.1 });
    if (ref.current) ob.observe(ref.current);
    return () => ob.disconnect();
  }, []);
  return (
    <section id="skills" className="skills" ref={ref}>
      <p className="section-tag section-tag--light">§ Tools &amp; Expertise</p>

      <h3 className="skills__sub">Professional toolkit</h3>
      <div className="tools-cloud">
        {TOOLS.map((t,i) => <span key={i} className="tool-chip">{t}</span>)}
      </div>

      <h3 className="skills__sub">Core expertise</h3>
      <div className="bars">
        {COMPETENCIES.map(({label,pct},i) => (
          <div key={label} className="bar">
            <div className="bar__head">
              <span>{label}</span>
              <span className="bar__pct">{pct}%</span>
            </div>
            <div className="bar__track">
              <div className="bar__fill" style={{
                width:`${pct}%`,
                transform: vis ? "scaleX(1)" : "scaleX(0)",
                transitionDelay: vis ? `${i*0.1}s` : "0s",
              }}/>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── CONTACT ──────────────────────────────────────────────────── */
function Contact() {
  return (
    <section id="contact" className="contact">
      <p className="section-tag">§ Get In Touch</p>
      <div className="contact__grid">
        <div>
          <h2 className="contact__lede">Let's work<br/><em>together.</em></h2>
          <p className="contact__copy">Available for freelance projects, consulting engagements and contract work - locally in Zimbabwe and internationally.</p>
          <a href="mailto:kudzanaichakavarika67@gmail.com" className="btn-solid">Send a Message</a>
          <div className="contact__socials">
            <a href="https://www.linkedin.com/in/kudzanai-chakavarika-65a847372" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>
            </a>
            <a href="https://github.com/spatialforce" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
            </a>
          </div>
        </div>
        <div className="contact__list">
          {CONTACT_ITEMS.map(({lbl,val,href}) => (
            <a key={lbl} href={href} className="citem"
              target={href.startsWith("https") ? "_blank" : undefined} rel="noopener noreferrer">
              <span>{lbl}</span>
              <strong>{val}</strong>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── FOOTER ───────────────────────────────────────────────────── */
function SiteFooter() {
  return (
    <footer className="footer">
      <span>© 2026 Kudzanai Chakavarika</span>
      <div className="footer__links">
        <a href="https://spatialforce.co.zw">spatialforce.co.zw</a>
        <a href="https://www.linkedin.com/in/kudzanai-chakavarika-65a847372" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        <a href="https://github.com/spatialforce" target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
      <span>20°09′S 28°35′E</span>
    </footer>
  );
}

/* ══════════════════════════════════════════════════════════════
   CSS
══════════════════════════════════════════════════════════════ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;700;800;900&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

:root {
  --paper:  #EFEAE0;
  --paper2: #E4DECE;
  --ink:    #201D18;
  --night:  #191B15;
  --night2: #22251C;
  --rust:   #B1502A;
  --rust-d: #8C3E20;
  --brass:  #C89B4A;
  --moss:   #5C6650;
  --cream:  #F7F3E9;
  --line:   rgba(32,29,24,0.13);
  --linew:  rgba(247,243,233,0.13);
  --fd: 'Big Shoulders Display', sans-serif;
  --fb: 'IBM Plex Sans', sans-serif;
  --fm: 'IBM Plex Mono', monospace;
}

html, body { width: 100%; min-height: 100%; background: var(--night); }
body { font-family: var(--fb); color: var(--ink); overflow-x: hidden; -webkit-font-smoothing: antialiased; }

/* Kill the Vite/CRA default #root container (max-width + auto margins +
   padding) that was leaving pale gutters down both sides of the page —
   that gutter, not anything in the sections themselves, was the bug. */
html, body, #root {
  width: 100% !important;
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
  text-align: initial !important;
}

/* ── shared section furniture ── */
.section-tag {
  font-family: var(--fm);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: var(--rust);
  padding: 3.5rem 6vw 1.5rem;
}
.section-tag--light { color: var(--brass); }

/* ── GRATICULE ── coordinate ruler, the recurring signature device.
   Sits in its own padded band so it never fights the fixed nav or
   the content below it for the same pixels. */
.grat { display: flex; width: 100%; box-sizing: border-box; }
.grat--full {
  height: 2.8rem; padding: 0.6rem 4vw 0; align-items: flex-start; gap: 0;
  border-bottom: 1px solid rgba(200,155,74,0.16);
  background: rgba(200,155,74,0.03);
}
.grat__tick { flex: 1; position: relative; display: flex; flex-direction: column; align-items: flex-start; }
.grat__mark { width: 1px; height: 8px; background: rgba(200,155,74,0.45); display: block; }
.grat__label { font-family: var(--fm); font-size: 0.6rem; color: rgba(200,155,74,0.55); margin-top: 0.35rem; white-space: nowrap; }
.grat--thin { height: 1.1rem; padding: 0 4vw; }
.grat--thin .grat__mark { height: 6px; background: var(--line); }

/* ── NAV ── */
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 200;
  padding: 1.5rem 4vw;
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(rgba(25,27,21,0.9), rgba(25,27,21,0.55) 70%, transparent);
  transition: background 0.3s, padding 0.3s;
}
.nav--scrolled {
  background: rgba(25,27,21,0.97);
  padding: 1rem 4vw;
  border-bottom: 1px solid var(--linew);
}
.nav__mark {
  font-family: var(--fm); font-weight: 600; font-size: 0.85rem;
  letter-spacing: 0.04em; color: var(--cream); text-decoration: none;
}
.nav__mark span { color: var(--rust); }
.nav__menu { display: flex; list-style: none; gap: 0.4rem; }
.nav__menu a {
  display: flex; align-items: baseline; gap: 0.35rem;
  font-family: var(--fm); font-size: 0.76rem; font-weight: 500;
  color: rgba(247,243,233,0.55); text-decoration: none;
  padding: 0.4rem 0.7rem; transition: color 0.18s;
}
.nav__menu a em { font-style: normal; color: var(--rust); font-size: 0.66rem; }
.nav__menu a:hover { color: var(--cream); }
.nav__menu-close { display: none; }
.nav__burger { display: none; flex-direction: column; gap: 5px; background: none; border: none; cursor: pointer; padding: 6px; }
.nav__burger span { display: block; width: 22px; height: 1.5px; background: var(--rust); transition: transform 0.25s, opacity 0.25s; }
.nav__burger.open span:nth-child(1) { transform: translateY(6.5px) rotate(45deg); }
.nav__burger.open span:nth-child(2) { opacity: 0; }
.nav__burger.open span:nth-child(3) { transform: translateY(-6.5px) rotate(-45deg); }
.nav__backdrop {
  position: fixed; inset: 0; z-index: 190; background: rgba(15,16,12,0.55);
  border: none; padding: 0; cursor: pointer; animation: lbFade 0.18s ease;
}

/* ── BUTTONS ── */
.btn-solid, .btn-line {
  display: inline-block; font-family: var(--fm); font-size: 0.8rem; font-weight: 600;
  letter-spacing: 0.04em; text-decoration: none; padding: 0.85rem 1.9rem;
  border-radius: 2px; cursor: pointer; transition: background 0.2s, color 0.2s, transform 0.15s;
}
.btn-solid { background: var(--rust); color: var(--cream); border: 1px solid var(--rust); }
.btn-solid:hover { background: var(--rust-d); border-color: var(--rust-d); transform: translateY(-2px); }
.btn-line { background: transparent; color: var(--brass); border: 1px solid rgba(200,155,74,0.5); }
.btn-line:hover { background: rgba(200,155,74,0.1); border-color: var(--brass); }

/* ══════════════════════════════════════════
   HERO — asymmetric, full-bleed photo, no boxed divider
══════════════════════════════════════════ */
.hero { position: relative; width: 100%; min-height: 100vh; background: var(--night); padding-top: 5.4rem; }
.hero__inner {
  display: grid; grid-template-columns: 1.15fr 0.85fr; align-items: stretch;
  min-height: calc(100vh - 5.4rem - 2.8rem);
}
.hero__text {
  padding: 4.5rem 4vw 4rem 4vw;
  display: flex; flex-direction: column; justify-content: center;
  max-width: 640px;
}
.hero__status {
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-family: var(--fm); font-size: 0.68rem; letter-spacing: 0.08em;
  text-transform: uppercase; color: rgba(247,243,233,0.45); margin-bottom: 1.4rem;
}
.hero__status span { width: 6px; height: 6px; border-radius: 50%; background: var(--rust); display: inline-block; }
.hero__eyebrow { font-family: var(--fm); font-size: 0.78rem; color: var(--brass); letter-spacing: 0.02em; margin-bottom: 1rem; }
.hero__heading {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(3rem, 6.4vw, 5.6rem); line-height: 0.92; letter-spacing: -0.01em;
  color: var(--cream); margin-bottom: 1.6rem;
}
.hero__heading em { font-style: normal; color: var(--rust); }
.hero__typing {
  font-family: var(--fm); font-size: clamp(0.95rem, 1.3vw, 1.15rem);
  color: var(--brass); line-height: 1.5; min-height: 3em; margin-bottom: 1.6rem;
}
.hero__cursor { animation: blink 0.8s steps(1) infinite; }
@keyframes blink { 0%,49% { opacity:1; } 50%,100% { opacity:0; } }
.hero__desc {
  font-size: 1rem; font-weight: 300; line-height: 1.85;
  color: rgba(247,243,233,0.55); max-width: 52ch; margin-bottom: 2.2rem;
}
.hero__cta { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.hero__socials { display: flex; gap: 0.6rem; margin-left: 0.4rem; }
.hero__socials a {
  width: 2.3rem; height: 2.3rem; display: inline-flex; align-items: center; justify-content: center;
  border: 1px solid rgba(200,155,74,0.35); border-radius: 50%; color: rgba(247,243,233,0.6);
  transition: border-color 0.2s, color 0.2s;
}
.hero__socials svg { width: 0.9rem; height: 0.9rem; }
.hero__socials a:hover { border-color: var(--brass); color: var(--brass); }

.hero__photo { position: relative; overflow: hidden; background: var(--night); }
.hero__photo img {
  width: 100%; height: 100%; object-fit: cover; object-position: center 15%; display: block;
  filter: sepia(18%) saturate(0.85) contrast(1.02) brightness(0.92);
  transform: scale(0.9); transform-origin: center 22%;  will-change: transform; transform: translateZ(0) scale(0.9);
}
.hero__photo::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(100deg, rgba(25,27,21,0.55) 0%, rgba(25,27,21,0.05) 30%, transparent 55%);
  pointer-events: none;
}
.hero__readout {
  position: absolute; left: 0; right: 0; bottom: 0;
  display: flex; background: rgba(25,27,21,0.82); backdrop-filter: blur(6px);
  border-top: 1px solid var(--linew);
  backdrop-filter: none
}
.hero__readout div { flex: 1; padding: 1.1rem 0.6rem; text-align: center; border-right: 1px solid var(--linew); }
.hero__readout div:last-child { border-right: none; }
.hero__readout strong { display: block; font-family: var(--fd); font-size: 1.35rem; color: var(--brass); }
.hero__readout span { font-family: var(--fm); font-size: 0.56rem; letter-spacing: 0.05em; color: rgba(247,243,233,0.5); text-transform: uppercase; }

/* ══════════════════════════════════════════
   ABOUT — single flowing column, no bordered split
══════════════════════════════════════════ */
.about { background: var(--paper); padding-bottom: 5rem; }
.about__grid { padding: 0 4vw; display: grid; grid-template-columns: 0.85fr 1.15fr; gap: 4vw; align-items: start; }
.about__lede {
  font-family: var(--fd); font-weight: 700; text-transform: uppercase;
  font-size: clamp(1.8rem, 2.9vw, 2.6rem); line-height: 1.05; letter-spacing: -0.01em;
  color: var(--ink); position: sticky; top: 6rem;
}
.about__copy p { font-size: 1rem; line-height: 1.85; color: #3C382F; max-width: 62ch; }
.about__copy p + p { margin-top: 1.1rem; }
.about__facts { list-style: none; margin-top: 2rem; display: flex; flex-wrap: wrap; gap: 0.6rem 0.9rem; }
.about__facts li {
  font-family: var(--fm); font-size: 0.76rem; color: var(--ink);
  border: 1px solid var(--line); padding: 0.5rem 0.85rem; border-radius: 2px;
  display: flex; gap: 0.5rem;
}
.about__facts li span { color: var(--rust); font-weight: 600; }
.about {
  content-visibility: auto;
  contain-intrinsic-size: auto 900px;
}
.projects {
  content-visibility: auto;
  contain-intrinsic-size: auto 3600px; /* this one is by far the tallest */
}
.services {
  content-visibility: auto;
  contain-intrinsic-size: auto 900px;
}
.skills {
  content-visibility: auto;
  contain-intrinsic-size: auto 1000px;
}
.contact {
  content-visibility: auto;
  contain-intrinsic-size: auto 700px;
}

/* ══════════════════════════════════════════
   PROJECTS — flexible image frames (bug fix), sheet references
══════════════════════════════════════════ */
.projects { background: var(--night); }
.proj-list { display: flex; flex-direction: column; }
.proj-row {
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 3vw;
  padding: 3.2rem 4vw; border-bottom: 1px solid var(--linew); align-items: center;
}
.proj-row:nth-child(even) { grid-template-columns: 1fr 1.3fr; }
.proj-row:nth-child(even) .proj-frame { order: 2; }
.proj-row:nth-child(even) .proj-info { order: 1; }

/* the actual fix: a light "map-table" mat instead of a dark void.
   Almost every deliverable here (RUSLE maps, DEM outputs, LULC panels)
   sits on a white background — matting it in paper rather than night
   means leftover space around a tall/odd image reads as a deliberate
   margin, not a sizing bug. No forced aspect-ratio; the image keeps
   its true proportions, capped by a generous max-height. */
.proj-frame {
  position: relative; display: flex; align-items: center; justify-content: center;
  width: 100%; padding: 1.75rem; border: none;
  background: var(--paper2);
  cursor: zoom-in; border-radius: 3px; overflow: hidden;
  border: 1px solid var(--line);
}
.proj-frame img {
  display: block; width: 100%; height: auto; max-height: 72vh;
  object-fit: contain; margin: 0 auto; border-radius: 1px;
}
.proj-frame__tag {
  position: absolute; bottom: 0.8rem; right: 0.8rem;
  font-family: var(--fm); font-size: 0.58rem; letter-spacing: 0.04em;
  color: var(--cream); background: rgba(32,29,24,0.78);
  border: 1px solid rgba(32,29,24,0.4); padding: 0.3rem 0.6rem; border-radius: 2px;
  opacity: 0; transition: opacity 0.2s;
}
.proj-frame:hover .proj-frame__tag { opacity: 1; }

.proj-info__ref { font-family: var(--fm); font-size: 0.68rem; color: var(--brass); letter-spacing: 0.04em; display: block; margin-bottom: 0.8rem; }
.proj-info h3 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: clamp(1.2rem, 1.9vw, 1.7rem); color: var(--cream); line-height: 1.15; margin-bottom: 0.9rem; }
.proj-info p { font-size: 0.92rem; font-weight: 300; line-height: 1.8; color: rgba(247,243,233,0.55); max-width: 50ch; margin-bottom: 1.1rem; }
.proj-info__tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.proj-info__tags span {
  font-family: var(--fm); font-size: 0.6rem; color: var(--brass);
  border: 1px solid rgba(200,155,74,0.3); padding: 0.25rem 0.55rem; border-radius: 2px;
}

.lightbox {
  position: fixed; inset: 0; z-index: 500; background: rgba(15,16,12,0.95);
  display: flex; align-items: center; justify-content: center; padding: 6vh 5vw;
  cursor: zoom-out; animation: lbFade 0.18s ease;
}
.lightbox__img { max-width: 100%; max-height: 82vh; object-fit: contain; border-radius: 3px; box-shadow: 0 25px 70px rgba(0,0,0,0.55); cursor: default; }
.lightbox__caption { position: absolute; bottom: 4vh; left: 50%; transform: translateX(-50%); font-family: var(--fm); font-size: 0.7rem; letter-spacing: 0.04em; color: rgba(247,243,233,0.55); max-width: 90vw; text-align: center; }
.lightbox__close {
  position: absolute; top: 2rem; right: 2rem; width: 2.4rem; height: 2.4rem; border-radius: 50%;
  border: 1px solid rgba(247,243,233,0.25); background: rgba(247,243,233,0.05); color: var(--cream);
  font-size: 1.3rem; line-height: 1; display: flex; align-items: center; justify-content: center; cursor: pointer;
}
.lightbox__close:hover { background: rgba(247,243,233,0.14); }
@keyframes lbFade { from { opacity: 0; } to { opacity: 1; } }

/* ══════════════════════════════════════════
   SERVICES — legend list, not a 4-up card grid
══════════════════════════════════════════ */
.services { background: var(--paper); padding-bottom: 5rem; }
.legend { padding: 0 4vw; display: flex; flex-direction: column; }
.legend__row {
  display: grid; grid-template-columns: 19rem 1fr; gap: 1.6rem; align-items: center;
  padding: 1.6rem 0; border-bottom: 1px solid var(--line);
}
.legend__row:first-child { border-top: 1px solid var(--line); }
.legend__head { display: flex; align-items: center; gap: 0.9rem; }
.legend__mark { font-size: 1.5rem; color: var(--rust); font-family: var(--fb); flex-shrink: 0; }
.legend__row h3 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: 1.15rem; color: var(--ink); letter-spacing: -0.01em; }
.legend__row p { font-size: 0.9rem; line-height: 1.75; color: #4A463C; max-width: 56ch; }

/* ══════════════════════════════════════════
   SKILLS
══════════════════════════════════════════ */
.skills { background: var(--night); padding: 0 4vw 5rem; }
.skills__sub { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: 1.4rem; color: var(--brass); letter-spacing: -0.01em; margin: 2rem 0 1.4rem; }
.tools-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tool-chip {
  font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.65);
  border: 1px solid var(--linew); padding: 0.4rem 0.8rem; border-radius: 2px;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.tool-chip:hover { background: var(--rust); color: var(--cream); border-color: var(--rust); }
.bars { display: flex; flex-direction: column; gap: 1.5rem; max-width: 640px; }
.bar__head { display: flex; justify-content: space-between; font-size: 0.88rem; color: var(--cream); margin-bottom: 0.5rem; }
.bar__pct { font-family: var(--fm); font-size: 0.7rem; color: var(--rust); }
.bar__track { height: 3px; background: var(--night2); border-radius: 2px; overflow: hidden; }
.bar__fill { height: 100%; background: linear-gradient(90deg, var(--rust-d), var(--brass)); transform-origin: left; transition: transform 1.3s cubic-bezier(0.16,1,0.3,1); }

/* ══════════════════════════════════════════
   CONTACT — field-report layout
══════════════════════════════════════════ */
.contact { background: var(--paper); }
.contact__grid { padding: 0 4vw 5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 4vw; align-items: end; }
.contact__lede { font-family: var(--fd); font-weight: 800; text-transform: uppercase; font-size: clamp(2.2rem, 4vw, 3.6rem); line-height: 0.95; color: var(--ink); margin-bottom: 1.4rem; }
.contact__lede em { font-style: normal; color: var(--rust); }
.contact__copy { font-size: 0.95rem; line-height: 1.8; color: #4A463C; max-width: 42ch; margin-bottom: 1.6rem; }
.contact__socials { display: flex; gap: 0.6rem; margin-top: 1.4rem; }
.contact__socials a {
  width: 2.4rem; height: 2.4rem; display: inline-flex; align-items: center; justify-content: center;
  border: 1px solid var(--line); border-radius: 50%; color: var(--moss); transition: border-color 0.2s, color 0.2s;
}
.contact__socials svg { width: 0.95rem; height: 0.95rem; }
.contact__socials a:hover { border-color: var(--rust); color: var(--rust); }
.contact__list { display: flex; flex-direction: column; }
.citem { display: flex; flex-direction: column; gap: 0.3rem; padding: 1.1rem 0; border-bottom: 1px solid var(--line); text-decoration: none; transition: padding-left 0.2s; }
.citem:first-child { border-top: 1px solid var(--line); }
.citem:hover { padding-left: 0.6rem; }
.citem span { font-family: var(--fm); font-size: 0.62rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--rust); }
.citem strong { font-weight: 500; font-size: 0.95rem; color: var(--ink); word-break: break-all; }
.citem:hover strong { color: var(--rust); }

/* ══════════════════════════════════════════
   FOOTER
══════════════════════════════════════════ */
.footer {
  width: 100%; background: var(--night); padding: 1.6rem 4vw;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
  font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4);
}
.footer__links { display: flex; gap: 1.4rem; }
.footer__links a { color: rgba(247,243,233,0.4); text-decoration: none; transition: color 0.2s; }
.footer__links a:hover { color: var(--rust); }

/* ══════════════════════════════════════════════════════
   RESPONSIVE — TABLET ≤ 1024px
══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .nav__menu { display: none; position: fixed; top: 0; right: 0; bottom: 0; width: min(78vw,320px); background: var(--night2); flex-direction: column; justify-content: center; gap: 0.2rem; padding: 5rem 2.2rem; z-index: 150; }
  .nav__menu.open { display: flex; }
  .nav__menu a { font-size: 1rem; padding: 0.8rem 0; color: rgba(247,243,233,0.7); border-bottom: 1px solid var(--linew); }
  .nav__burger { display: flex; }
  .nav__menu-close {
    display: block; position: absolute; top: 1.4rem; right: 1.6rem;
    border-bottom: none !important; padding: 0 !important;
  }
  .nav__menu-close button {
    width: 2.3rem; height: 2.3rem; border-radius: 50%;
    border: 1px solid rgba(247,243,233,0.25); background: rgba(247,243,233,0.05);
    color: var(--cream); font-size: 1.4rem; line-height: 1;
    display: flex; align-items: center; justify-content: center; cursor: pointer;
  }
  .nav__menu-close button:hover { background: rgba(247,243,233,0.14); }

  .grat--full { display: none; }
  .hero__inner { grid-template-columns: 1fr; min-height: auto; }
  .hero__photo { order: 1; height: 62vh; }
  .hero__text { order: 2; padding: 3.2rem 6vw 4rem; max-width: none; }

  .about__grid { grid-template-columns: 1fr; }
  .about__lede { position: static; margin-bottom: 1.8rem; }

  .proj-row { grid-template-columns: 1fr !important; padding: 2.4rem 6vw; }
  .proj-row .proj-frame, .proj-row .proj-info { order: initial !important; }

  .legend__row { grid-template-columns: 1fr; row-gap: 0.6rem; }

  .contact__grid { grid-template-columns: 1fr; }
  .contact__list { margin-top: 2rem; }
}

/* ══════════════════════════════════════════════════════
   RESPONSIVE — MOBILE ≤ 640px
══════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  .nav { padding: 1rem 6vw; }

  /* hero: photo shorter, readout slimmer so it stops eating the image.
     transform: scale(1) overrides the desktop 0.9 scale-down, which was
     shrinking the image inside its box and revealing the dark background
     as margins on the left/right — the photo now fills edge-to-edge. */
  .hero__photo { height: 40vh; }
  .hero__photo img { transform: scale(1); }
  .hero__readout div { padding: 0.55rem 0.4rem; }
  .hero__readout strong { font-size: 1rem; }
  .hero__readout span { font-size: 0.48rem; }

  /* hero: center the text block instead of hugging the left edge */
  .hero__text { align-items: center; text-align: center; padding: 3rem 7vw 3.2rem; }
  .hero__status, .hero__desc, .hero__typing { text-align: center; }
  .hero__heading { font-size: clamp(2.4rem, 12vw, 3.2rem); }

  /* buttons: .hero__cta was shrink-wrapping to its content, which is
     why Hire Me / Download CV rendered smaller than Send a Message —
     giving it full width lets the width:100% buttons below actually
     mean 100% of the same measure every other button uses. */
  .hero__cta { flex-direction: column; align-items: center; width: 100%; gap: 0.85rem; }
  .hero__socials { margin-left: 0; margin-top: 0.3rem; }
  .btn-solid, .btn-line { width: 100%; text-align: center; box-sizing: border-box; }

  /* headings + buttons: centered everywhere on mobile */
  .section-tag { padding: 3rem 6vw 1.2rem; text-align: center; }
  .about__grid { text-align: center; }
  .about__lede { text-align: center; }
  .about__copy { display: flex; flex-direction: column; align-items: center; }
  .about__facts { justify-content: center; }
  .proj-info { text-align: center; display: flex; flex-direction: column; align-items: center; }
  .proj-info__tags { justify-content: center; }
  .proj-info h3 { font-size: 1.3rem; }
  .legend__head { justify-content: center; }
  .legend__row { text-align: center; }
  .skills__sub { text-align: center; }
  .contact__grid { text-align: center; }
  .contact__grid > div:first-child { display: flex; flex-direction: column; align-items: center; }
  .contact__socials { justify-content: center; }
  .contact__list { align-items: center; }
  .citem { align-items: center; }

  /* projects: crop to a clean preview with a permanent "view full
     image" affordance instead of a tiny contained image — tapping
     opens the full-screen lightbox at true size. */
  .proj-frame { aspect-ratio: 4 / 3; padding: 0; align-items: stretch; }
  .proj-frame img { position: absolute; inset: 0; width: 100%; height: 100%; max-height: none; object-fit: cover; }
  .proj-frame::after {
    content: ''; position: absolute; left: 0; right: 0; bottom: 0; height: 40%;
    background: linear-gradient(to top, rgba(32,29,24,0.75), transparent); pointer-events: none;
  }
  .proj-frame__tag {
    opacity: 1; left: 50%; right: auto; bottom: 0.9rem; transform: translateX(-50%);
    background: rgba(32,29,24,0.85);
  }

  .lightbox { padding: 3vh 4vw; }
  .lightbox__img { max-height: 80vh; }

  .legend__row { grid-template-columns: 1fr; row-gap: 0.5rem; }

  .footer { flex-direction: column; align-items: center; text-align: center; gap: 0.7rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
`;
