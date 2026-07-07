import { useState, useEffect, useRef } from "react";
import profile from "./assets/profile_1.png";

const TOOLS = [
  "ArcGIS Pro","QGIS","Google Earth Engine","Google Earth Pro",
  "SEPAL","Global Mapper","ENVI Classic","ArcGIS Online",
  "ArcMap","ArcGIS StoryMaps","Drone2Map","GeoPandas",
  "OpenLayers","GRASS GIS","ArcGIS Experience Builder",
  "Leaflet.js","FME Desktop","ERDAS Imagine",
];

const SERVICES = [
  { num:"01", title:"Spatial Analysis", body:"Terrain modelling, watershed delineation, overlay analysis, and multi-criteria decision support — translating geographic complexity into clear, actionable intelligence." },
  { num:"02", title:"Remote Sensing & Image Classification", body:"Land cover and land use mapping, NDVI and vegetation health indices, and temporal change detection from multispectral and hyperspectral satellite imagery." },
  { num:"03", title:"Web Mapping & GIS Portals", body:"Interactive web maps, dashboards, and geoportals using ArcGIS Online, Experience Builder, StoryMaps, and open-source libraries — spatial data accessible to any audience." },
  { num:"04", title:"Natural Resource Management", body:"Spatial analysis in support of conservation planning, biodiversity inventories, environmental impact assessment, and sustainable land-use decision making." },
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
  { lbl:"LinkedIn", val:"linkedin.com/in/kudzanai-chakavarika", href:"https://linkedin.com/in/kudzanai-chakavarika" },
  { lbl:"GitHub", val:"github.com/kudzanaichakavarika", href:"https://github.com/kudzanaichakavarika" },
  { lbl:"Website", val:"spatialforce.co.zw", href:"https://spatialforce.co.zw" },
];

const PROJECTS = [
  { id:"01", title:"Watershed Delineation — Limpopo Basin", tags:["Hydrology","ArcGIS Pro","Terrain Analysis"], desc:"Multi-level watershed delineation and flow accumulation modelling across the upper Limpopo catchment.", img:"https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=900&q=80" },
  { id:"02", title:"Land-Cover Change Detection — Hwange", tags:["Remote Sensing","NDVI","GEE"], desc:"Supervised classification of Sentinel-2 time-series to quantify deforestation rates over 10 years.", img:"https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=900&q=80" },
  { id:"03", title:"Interactive Web Map — Biodiversity Atlas", tags:["Leaflet.js","ArcGIS Online","Web GIS"], desc:"Public-facing geoportal for a national conservation NGO visualising species and protected areas.", img:"https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=900&q=80" },
  { id:"04", title:"Drone Survey — Matobo Hills Erosion", tags:["Drone2Map","Photogrammetry","DEM"], desc:"High-resolution DEM and orthomosaic from UAV flights to assess gully erosion dynamics.", img:"https://images.unsplash.com/photo-1527576539890-dfa815648363?w=900&q=80" },
];

const TAGLINES = [
  "I map watersheds, forests, and cities",
  "I turn satellite data into field-ready answers",
  "I build web maps people actually use",
  "I bridge remote sensing and real-world action",
];

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

/* ── NAV ──────────────────────────────────────────────────────── */
function Nav({ navOpen, setNavOpen, navScrolled }: { navOpen:boolean; setNavOpen:(v:boolean)=>void; navScrolled:boolean }) {
  const links = ["Home","About","Projects","Services","Skills","Contact"];
  return (
    <header className={`nav${navScrolled ? " nav--scrolled" : ""}`}>
      <a href="#home" className="nav__tagline">Beyond the coordinates</a>
      <ul className={`nav__menu${navOpen ? " open" : ""}`}>
        {links.map(l => (
          <li key={l}><a href={`#${l.toLowerCase()}`} onClick={() => setNavOpen(false)}>{l}</a></li>
        ))}
      </ul>
      <button className={`nav__burger${navOpen ? " open" : ""}`} onClick={() => setNavOpen(!navOpen)} aria-label="Menu">
        <span/><span/><span/>
      </button>
    </header>
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
      <div className="hero__inner">
        {/* LEFT — photo */}
        <div className="hero__photo-side">
          <div className="hero__photo-frame">
            <img src={profile} alt="Kudzanai Chakavarika" className="hero__photo" />
          </div>
          {/* Floating stat strip below photo */}
          <div className="hero__stats">
            <div className="hero__stat"><strong>18</strong><span>GIS Tools</span></div>
            <div className="hero__stat-div"/>
            <div className="hero__stat"><strong>ZW</strong><span>Based</span></div>
            <div className="hero__stat-div"/>
            <div className="hero__stat"><strong>Global</strong><span>Reach</span></div>
          </div>
        </div>

        {/* RIGHT — text */}
        <div className="hero__text-side">
          <p className="hero__eyebrow">Geospatial Analyst &nbsp;/&nbsp; BSc GIS &amp; Remote Sensing</p>
          <h1 className="hero__heading">
            <span className="hero__name-white">Kudzanai</span>
            <span className="hero__name-orange">Chakavarika</span>
          </h1>
          {/* Typing row — reserved height so it never bumps content below */}
          <div className="hero__typing-row">
            <span className="hero__typing-text">{displayed}<span className="hero__cursor" aria-hidden="true">|</span></span>
          </div>
          <p className="hero__desc">
            Transforming raw spatial data into clear decisions — from satellite imagery to
            interactive web maps, grounded in deep expertise across natural resources and
            the full ESRI &amp; open-source GIS stack.
          </p>
          <div className="hero__socials">
            <a href="https://linkedin.com/in/kudzanai-chakavarika" target="_blank" rel="noopener noreferrer" className="soc-btn" aria-label="LinkedIn">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>
            </a>
            <a href="https://github.com/kudzanaichakavarika" target="_blank" rel="noopener noreferrer" className="soc-btn" aria-label="GitHub">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
            </a>
          </div>
          <div className="hero__cta">
            <a href="#contact" className="btn-orange">Hire Me</a>
            <a href="/cv.pdf" download className="btn-outline">Download CV</a>
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
      <div className="sec-head"><h2 className="sec-title">About</h2></div>
      <div className="about__body">
        <div className="about__left">
          <dl className="about__facts">
            {[
              ["Based in","Bulawayo, Zimbabwe"],
              ["Education","BSc GIS & Remote Sensing · NRM"],
              ["Expertise","Spatial Analysis, Remote Sensing, Web Mapping"],
              ["Availability","Open to projects globally"],
              ["Website","spatialforce.co.zw"],
            ].map(([k,v]) => (
              <div key={k} className="about__fact">
                <dt>{k}</dt><dd>{v}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="about__right">
          <h3 className="about__sub">Spatial intelligence for complex problems</h3>
          <p>I'm Kudzanai Chakavarika, a geospatial analyst with a BSc in Geographic Information Systems and Remote Sensing in Natural Resources Management, based in Bulawayo, Zimbabwe.</p>
          <p>My work spans the full geospatial workflow: from acquiring and preprocessing satellite imagery to building analytical models, generating publication-quality cartography, and deploying spatial data as interactive web experiences.</p>
          <p>I'm fluent across ESRI's professional stack — ArcGIS Pro, ArcGIS Online, StoryMaps, Experience Builder — as well as open-source and cloud platforms including QGIS, Google Earth Engine, SEPAL, ENVI Classic, and Global Mapper.</p>
        </div>
      </div>
    </section>
  );
}

/* ── PROJECTS ─────────────────────────────────────────────────── */
function Projects() {
  return (
    <section id="projects" className="projects">
      <div className="sec-head sec-head--dark"><h2 className="sec-title sec-title--light">Selected Work</h2></div>
      <div className="proj-grid">
        {PROJECTS.map((p, i) => (
          <article key={p.id} className={`proj-card${i === 0 ? " proj-card--wide" : ""}`}>
            <div className="proj-card__img-wrap">
              <img src={p.img} alt={p.title} className="proj-card__img"/>
            </div>
            <div className="proj-card__body">
              <span className="proj-card__num">{p.id}</span>
              <div className="proj-card__tags">{p.tags.map(t => <span key={t}>{t}</span>)}</div>
              <h3 className="proj-card__title">{p.title}</h3>
              <p className="proj-card__desc">{p.desc}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

/* ── SERVICES ─────────────────────────────────────────────────── */
function Services() {
  return (
    <section id="services" className="services">
      <div className="sec-head"><h2 className="sec-title">What I Do</h2></div>
      <div className="svc-grid">
        {SERVICES.map(s => (
          <div key={s.num} className="svc-card">
            <span className="svc-card__num">{s.num}</span>
            <h3 className="svc-card__title">{s.title}</h3>
            <p className="svc-card__body">{s.body}</p>
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
    <section id="skills" className="skills">
      <div className="sec-head sec-head--dark"><h2 className="sec-title sec-title--light">Tools &amp; Expertise</h2></div>
      <div className="skills__body">
        <div className="skills__left">
          <h3 className="skills__sub">Professional Toolkit</h3>
          <div className="tools-cloud">
            {TOOLS.map((t,i) => <span key={i} className="tool-chip">{t}</span>)}
          </div>
        </div>
        <div className="skills__right" ref={ref}>
          <h3 className="skills__sub">Core Expertise</h3>
          {COMPETENCIES.map(({label,pct},i) => (
            <div key={label} className="bar">
              <div className="bar__head">
                <span className="bar__label">{label}</span>
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
      </div>
    </section>
  );
}

/* ── CONTACT ──────────────────────────────────────────────────── */
function Contact() {
  return (
    <section id="contact" className="contact">
      <div className="sec-head"><h2 className="sec-title">Get In Touch</h2></div>
      <div className="contact__body">
        <div className="contact__left">
          <h3 className="contact__sub">Let's work together.</h3>
          <p className="contact__copy">Available for freelance projects, consulting engagements, and contract work — locally in Zimbabwe and internationally.</p>
          <a href="mailto:kudzanaichakavarika67@gmail.com" className="btn-orange">Send a Message</a>
          <div className="contact__socials">
            <a href="https://linkedin.com/in/kudzanai-chakavarika" target="_blank" rel="noopener noreferrer" className="soc-btn" aria-label="LinkedIn">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>
            </a>
            <a href="https://github.com/kudzanaichakavarika" target="_blank" rel="noopener noreferrer" className="soc-btn" aria-label="GitHub">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/></svg>
            </a>
          </div>
        </div>
        <div className="contact__right">
          {CONTACT_ITEMS.map(({lbl,val,href}) => (
            <a key={lbl} href={href} className="citem"
              target={href.startsWith("https") ? "_blank" : undefined} rel="noopener noreferrer">
              <span className="citem__lbl">{lbl}</span>
              <span className="citem__val">{val}</span>
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
        <a href="https://linkedin.com/in/kudzanai-chakavarika" target="_blank" rel="noopener noreferrer">LinkedIn</a>
        <a href="https://github.com/kudzanaichakavarika" target="_blank" rel="noopener noreferrer">GitHub</a>
      </div>
      <span>20°09′S 28°35′E</span>
    </footer>
  );
}

/* ══════════════════════════════════════════════════════════════
   CSS
══════════════════════════════════════════════════════════════ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700;800;900&family=Archivo+Black&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

:root {
  --bg:      #0C1018;
  --bg2:     #111820;
  --bg3:     #0A0F15;
  --orange:  #3AA898;
  --orange2: #2B7E71;
  --white:   #FFFFFF;
  --cream:   #F4F1EC;
  --ink:     #1A2535;
  --dim:     #8899AA;
  --line:    rgba(58,168,152,0.16);
  --linew:   rgba(255,255,255,0.08);
  --f:  'Archivo', sans-serif;
  --fh: 'Archivo Black', sans-serif;
}

html, body {
  width: 100%;
  min-height: 100%;
  background: var(--bg);
}
body {
  font-family: var(--f);
  color: var(--white);
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

/* ── NAV ─────────────────────────────────── */
.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 200;
  padding: 1.4rem 5vw;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background 0.3s, padding 0.3s;
}
.nav--scrolled {
  background: rgba(12,16,24,0.96);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid var(--line);
  padding: 1rem 5vw;
}
.nav__tagline {
  font-family: var(--f);
  font-size: 0.66rem;
  font-weight: 400;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.38);
  text-decoration: none;
  transition: color 0.2s;
  white-space: nowrap;
}
.nav__tagline:hover { color: rgba(255,255,255,0.7); }
.nav__menu {
  display: flex;
  list-style: none;
  gap: 0.25rem;
}
.nav__menu a {
  font-size: 0.82rem;
  font-weight: 500;
  color: rgba(255,255,255,0.6);
  text-decoration: none;
  padding: 0.4rem 0.85rem;
  border-radius: 3px;
  letter-spacing: 0.02em;
  transition: color 0.18s;
  position: relative;
}
.nav__menu a::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0.85rem; right: 0.85rem;
  height: 1.5px;
  background: var(--orange);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.22s;
}
.nav__menu a:hover { color: var(--white); }
.nav__menu a:hover::after { transform: scaleX(1); }

.nav__burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  margin-left: auto;
}
.nav__burger span {
  display: block;
  width: 24px; height: 1.5px;
  background: var(--orange);
  border-radius: 2px;
  transition: transform 0.25s, opacity 0.25s;
}
.nav__burger.open span:nth-child(1) { transform: translateY(6.5px) rotate(45deg); }
.nav__burger.open span:nth-child(2) { opacity: 0; }
.nav__burger.open span:nth-child(3) { transform: translateY(-6.5px) rotate(-45deg); }

/* ── SECTION SHARED ──────────────────────── */
.sec-head {
  padding: 6rem 6vw 3.5rem;
  border-bottom: 1px solid rgba(0,0,0,0.08);
  background: var(--cream);
}
.sec-head--dark {
  background: var(--bg3);
  border-bottom: 1px solid var(--linew);
}
.sec-title {
  font-family: var(--fh);
  font-size: clamp(2.6rem, 5vw, 5rem);
  letter-spacing: -0.03em;
  line-height: 1;
  color: var(--ink);
}
.sec-title--light { color: var(--white); }

/* ── BUTTONS ─────────────────────────────── */
.btn-orange {
  display: inline-block;
  font-family: var(--f);
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
  padding: 0.95rem 2.4rem;
  background: var(--orange);
  color: var(--bg);
  border-radius: 3px;
  border: 2px solid var(--orange);
  transition: background 0.2s, transform 0.18s;
  cursor: pointer;
}
.btn-orange:hover { background: var(--orange2); border-color: var(--orange2); transform: translateY(-2px); }

.btn-outline {
  display: inline-block;
  font-family: var(--f);
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
  padding: 0.95rem 2.4rem;
  background: transparent;
  color: var(--orange);
  border: 2px solid var(--orange);
  border-radius: 3px;
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
}
.btn-outline:hover { background: var(--orange); color: var(--bg); }

/* Social icon buttons */
.soc-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.6rem; height: 2.6rem;
  border: 1.5px solid rgba(58,168,152,0.4);
  border-radius: 50%;
  color: var(--dim);
  text-decoration: none;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}
.soc-btn svg { width: 1rem; height: 1rem; }
.soc-btn:hover { border-color: var(--orange); color: var(--orange); background: rgba(58,168,152,0.08); }

/* ══════════════════════════════════════════
   HERO — Desktop: two columns, full bleed
══════════════════════════════════════════ */
.hero {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: var(--bg);
  overflow: hidden;
}
/* Subtle orange glow top-right */
.hero::before {
  content: '';
  position: absolute;
  top: -20%;
  right: -10%;
  width: 60vw;
  height: 60vw;
  background: radial-gradient(circle, rgba(58,168,152,0.05) 0%, transparent 65%);
  pointer-events: none;
}

.hero__inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 40% 60%;
  min-height: 100vh;
}

/* ── LEFT: photo side ──
   Inset, framed, and muted so the portrait reads as a
   composed element rather than a full-bleed, loud image. ── */
.hero__photo-side {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--linew);
  padding: 2.75rem 2.75rem 0 2.75rem;
}
.hero__photo-frame {
  flex: 1;
  overflow: hidden;
  position: relative;
  border-radius: 8px;
  border: 1px solid var(--linew);
  max-height: 560px;
}
.hero__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 8%;
  display: block;
  filter: grayscale(28%) brightness(0.9) contrast(0.96) saturate(0.85);
  transition: filter 0.4s;
}
.hero__photo:hover { filter: grayscale(10%) brightness(1) contrast(1) saturate(1); }
/* Subtle orange tint overlay at bottom */
.hero__photo-frame::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 35%;
  background: linear-gradient(to top, rgba(58,168,152,0.1), transparent);
  pointer-events: none;
}

/* Stats bar — flush, full-bleed strip beneath the framed photo */
.hero__stats {
  flex-shrink: 0;
  display: flex;
  align-items: stretch;
  background: var(--bg2);
  border-top: 1px solid var(--linew);
  margin: 1.75rem -2.75rem 0;
}
.hero__stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 1.4rem 0.5rem;
}
.hero__stat strong {
  font-family: var(--fh);
  font-size: 1.6rem;
  color: var(--orange);
  letter-spacing: -0.03em;
  line-height: 1;
}
.hero__stat span {
  font-size: 0.56rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--dim);
}
.hero__stat-div {
  width: 1px;
  background: var(--linew);
  align-self: stretch;
}

/* ── RIGHT: text side ── */
.hero__text-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8rem 6vw 5rem 5vw;
  gap: 0; /* gaps controlled per element via margin-bottom */
  min-width: 0; /* allow children to shrink instead of overflowing */
}
.hero__eyebrow {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--orange);
  margin-bottom: 1.8rem;
}
.hero__heading {
  display: flex;
  flex-direction: column;
  line-height: 0.95;
  margin-bottom: 2rem;
  min-width: 0;
}
.hero__name-white {
  font-family: var(--fh);
  font-size: clamp(2.4rem, 4.6vw, 4.6rem);
  color: var(--white);
  letter-spacing: -0.03em;
  overflow-wrap: break-word;
  word-break: break-word;
}
.hero__name-orange {
  font-family: var(--fh);
  font-size: clamp(2.2rem, 4.2vw, 4.2rem);
  color: var(--orange);
  letter-spacing: -0.03em;
  overflow-wrap: break-word;
  word-break: break-word;
}

/* ── TYPING ROW ──
   CRITICAL: Fixed height container = no layout shift ever.
   Font sizes are capped conservatively so the longest role
   string ("Remote Sensing Specialist") always fits the column
   without clipping.
── */
.hero__typing-row {
  display: flex;
  align-items: flex-start;
  min-height: 3.6rem;        /* reserves room for up to two lines — no jump */
  margin-bottom: 2rem;
  max-width: 40ch;
}
.hero__typing-text {
  font-family: var(--fh);
  font-size: clamp(1rem, 1.5vw, 1.3rem);
  line-height: 1.35;
  color: var(--cream);
  white-space: normal;
  overflow-wrap: break-word;
  letter-spacing: -0.01em;
}
.hero__cursor {
  display: inline-block;
  width: 2px;
  color: var(--cream);
  animation: blink 0.7s steps(1) infinite;
  margin-left: 1px;
}
@keyframes blink { 0%,49% { opacity:1; } 50%,100% { opacity:0; } }

.hero__desc {
  font-size: clamp(0.9rem, 1.1vw, 1rem);
  font-weight: 300;
  line-height: 1.8;
  color: rgba(255,255,255,0.48);
  max-width: 46ch;
  margin-bottom: 2.4rem;
}
.hero__socials {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  max-width: 46ch;
  margin-bottom: 2rem;
}
.hero__cta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* ══════════════════════════════════════════
   ABOUT
══════════════════════════════════════════ */
.about { background: var(--cream); width: 100%; }
.about .sec-head { background: var(--cream); }
.about__body {
  display: grid;
  grid-template-columns: 34% 1fr;
  background: var(--cream);
}
.about__left {
  padding: 4.5rem 5vw 4.5rem 6vw;
  border-right: 1px solid rgba(0,0,0,0.08);
}
.about__right { padding: 4.5rem 6vw 4.5rem 5vw; }
.about__facts { display: flex; flex-direction: column; }
.about__fact {
  padding: 0.95rem 0;
  border-bottom: 1px solid rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.about__fact:first-child { border-top: 1px solid rgba(0,0,0,0.07); }
.about__fact dt {
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--orange);
}
.about__fact dd { font-size: 0.9rem; font-weight: 600; color: var(--ink); }
.about__sub {
  font-family: var(--fh);
  font-size: clamp(1.5rem, 2.4vw, 2.1rem);
  color: var(--ink);
  letter-spacing: -0.025em;
  line-height: 1.15;
  margin-bottom: 2rem;
}
.about__right p { font-size: 0.97rem; font-weight: 400; line-height: 1.85; color: #3A4A5A; }
.about__right p + p { margin-top: 1.2rem; }

/* ══════════════════════════════════════════
   PROJECTS
══════════════════════════════════════════ */
.projects { background: var(--bg3); width: 100%; }
.projects .sec-head--dark { background: var(--bg3); }
.proj-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid var(--linew);
}
.proj-card {
  background: var(--bg2);
  border-right: 1px solid var(--linew);
  border-bottom: 1px solid var(--linew);
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.25s;
}
.proj-card:hover { box-shadow: inset 0 0 0 1.5px var(--orange2); }
.proj-card--wide {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
}
.proj-card__img-wrap { overflow: hidden; flex-shrink: 0; }
.proj-card--wide .proj-card__img-wrap { min-height: 420px; }
.proj-card:not(.proj-card--wide) .proj-card__img-wrap { aspect-ratio: 4/3; }
.proj-card__img {
  width: 100%; height: 100%;
  object-fit: cover; display: block;
  transition: transform 0.55s ease, filter 0.55s;
  filter: saturate(0.8) brightness(0.9);
}
.proj-card:hover .proj-card__img { transform: scale(1.04); filter: saturate(1) brightness(1); }
.proj-card__body {
  padding: 2.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  flex: 1;
}
.proj-card--wide .proj-card__body { padding: 3.5rem; justify-content: center; }
.proj-card__num {
  font-family: var(--fh);
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  color: var(--orange);
  display: block;
}
.proj-card__tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.proj-card__tags span {
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--dim);
  background: rgba(58,168,152,0.08);
  border: 1px solid rgba(58,168,152,0.2);
  padding: 0.2rem 0.6rem;
  border-radius: 2px;
}
.proj-card__title {
  font-family: var(--fh);
  font-size: clamp(1rem, 1.4vw, 1.25rem);
  color: var(--white);
  letter-spacing: -0.015em;
  line-height: 1.22;
}
.proj-card__desc { font-size: 0.87rem; font-weight: 300; line-height: 1.75; color: var(--dim); }

/* ══════════════════════════════════════════
   SERVICES
══════════════════════════════════════════ */
.services { background: var(--cream); width: 100%; }
.services .sec-head { background: var(--cream); }
.svc-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  background: var(--cream);
  border-top: 1px solid rgba(0,0,0,0.07);
}
.svc-card {
  padding: 3rem 3vw;
  border-right: 1px solid rgba(0,0,0,0.07);
  border-bottom: 1px solid rgba(0,0,0,0.07);
  transition: background 0.2s;
}
.svc-card:last-child { border-right: none; }
.svc-card:hover { background: rgba(58,168,152,0.04); }
.svc-card__num {
  display: block;
  font-family: var(--fh);
  font-size: 2.2rem;
  color: var(--orange);
  opacity: 0.3;
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 1.5rem;
}
.svc-card__title {
  font-family: var(--fh);
  font-size: 1.05rem;
  color: var(--ink);
  letter-spacing: -0.01em;
  margin-bottom: 1rem;
  line-height: 1.25;
}
.svc-card__body { font-size: 0.86rem; font-weight: 400; line-height: 1.8; color: #5A6A7A; }

/* ══════════════════════════════════════════
   SKILLS
══════════════════════════════════════════ */
.skills { background: var(--bg3); width: 100%; }
.skills .sec-head--dark { background: var(--bg3); }
.skills__body {
  display: grid;
  grid-template-columns: 40% 1fr;
  background: var(--bg3);
}
.skills__left {
  padding: 4.5rem 5vw 4.5rem 6vw;
  border-right: 1px solid var(--linew);
}
.skills__right { padding: 4.5rem 6vw; display: flex; flex-direction: column; gap: 1.6rem; }
.skills__sub {
  font-family: var(--fh);
  font-size: 1.3rem;
  color: var(--orange);
  letter-spacing: -0.015em;
  margin-bottom: 1.5rem;
}
.tools-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tool-chip {
  font-size: 0.64rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: rgba(255,255,255,0.65);
  background: rgba(58,168,152,0.07);
  border: 1px solid rgba(58,168,152,0.2);
  padding: 0.32rem 0.75rem;
  border-radius: 2px;
  cursor: default;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.tool-chip:hover { background: var(--orange); color: var(--bg); border-color: var(--orange); }
.bar__head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem; }
.bar__label { font-size: 0.84rem; font-weight: 500; color: var(--white); }
.bar__pct { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em; color: var(--orange); }
.bar__track { height: 2px; background: rgba(58,168,152,0.12); border-radius: 1px; overflow: hidden; }
.bar__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--orange2), var(--orange));
  border-radius: 1px;
  transform-origin: left;
  transition: transform 1.3s cubic-bezier(0.16,1,0.3,1);
}

/* ══════════════════════════════════════════
   CONTACT
══════════════════════════════════════════ */
.contact { background: var(--bg); width: 100%; }
.contact .sec-head { background: var(--bg); border-bottom: 1px solid var(--linew); }
.contact .sec-title { color: var(--white); }
.contact__body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: var(--bg);
  min-height: 60vh;
}
.contact__left {
  padding: 6rem 5vw 6rem 6vw;
  border-right: 1px solid var(--linew);
  display: flex;
  flex-direction: column;
  gap: 1.8rem;
  align-items: flex-start;
  justify-content: center;
}
.contact__sub {
  font-family: var(--fh);
  font-size: clamp(1.8rem,3vw,3rem);
  color: var(--white);
  letter-spacing: -0.03em;
  line-height: 1.1;
}
.contact__copy { font-size: 0.95rem; font-weight: 300; line-height: 1.8; color: rgba(255,255,255,0.4); max-width: 40ch; }
.contact__socials { display: flex; gap: 0.75rem; }
.contact__right {
  padding: 6rem 6vw 6rem 5vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.citem {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--linew);
  text-decoration: none;
  transition: padding-left 0.2s;
}
.citem:first-child { border-top: 1px solid var(--linew); }
.citem:hover { padding-left: 0.7rem; }
.citem__lbl { font-size: 0.56rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--orange); }
.citem__val { font-size: 0.95rem; font-weight: 500; color: var(--white); word-break: break-all; }
.citem:hover .citem__val { color: var(--orange); }

/* ══════════════════════════════════════════
   FOOTER
══════════════════════════════════════════ */
.footer {
  width: 100%;
  background: var(--bg2);
  border-top: 1px solid var(--linew);
  padding: 1.8rem 6vw;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.64rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--dim);
}
.footer__links { display: flex; gap: 1.5rem; }
.footer__links a { color: rgba(255,255,255,0.3); text-decoration: none; transition: color 0.2s; font-size: 0.64rem; font-weight: 600; letter-spacing: 0.06em; }
.footer__links a:hover { color: var(--orange); }

/* ══════════════════════════════════════════════════════
   RESPONSIVE — TABLET  ≤ 1024px
   Mobile/tablet layout is unchanged from the original —
   the inset-photo treatment above is desktop-only, so it
   is reset back to full-bleed here.
══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .nav__menu { display: none; position: fixed; top: 0; right: 0; bottom: 0; width: min(75vw,320px); background: var(--bg2); flex-direction: column; justify-content: center; gap: 0.3rem; padding: 5rem 2.5rem; border-left: 1px solid var(--linew); z-index: 150; }
  .nav__menu.open { display: flex; }
  .nav__menu a { font-size: 1.1rem; padding: 0.8rem 0; color: rgba(255,255,255,0.7); border-bottom: 1px solid var(--linew); }
  .nav__menu a:hover { color: var(--orange); }
  .nav__burger { display: flex; }
  .nav__tagline { font-size: 0.6rem; }

  .hero__inner { grid-template-columns: 1fr; min-height: auto; }
  .hero__photo-side { order: 1; border-right: none; border-bottom: 1px solid var(--linew); padding: 3.4rem 0 0 0; }
  .hero__photo-frame { aspect-ratio: 4/4.2; flex: none; max-height: none; border-radius: 0; border: none; }
  .hero__stats { margin: 0; }
  .hero__text-side { order: 2; padding: 4rem 5vw 5rem; }
  .hero__name-white { font-size: clamp(2.8rem,10vw,5rem); }
  .hero__name-orange { font-size: clamp(2.5rem,9.5vw,4.6rem); }
  .hero__desc { max-width: none; }
  .hero__socials { max-width: none; }

  .about__body { grid-template-columns: 1fr; }
  .about__left { border-right: none; border-bottom: 1px solid rgba(0,0,0,0.07); padding: 3rem 5vw; }
  .about__right { padding: 3rem 5vw; }
  .sec-head { padding: 5rem 5vw 3rem; }

  .proj-grid { grid-template-columns: 1fr; }
  .proj-card--wide { grid-column: 1; grid-template-columns: 1fr; }
  .proj-card--wide .proj-card__img-wrap { min-height: 260px; aspect-ratio: 16/8; }

  .svc-grid { grid-template-columns: 1fr 1fr; }
  .svc-card:nth-child(2) { border-right: none; }

  .skills__body { grid-template-columns: 1fr; }
  .skills__left { border-right: none; border-bottom: 1px solid var(--linew); padding: 3rem 5vw; }
  .skills__right { padding: 3rem 5vw; }

  .contact__body { grid-template-columns: 1fr; min-height: auto; }
  .contact__left { border-right: none; border-bottom: 1px solid var(--linew); padding: 4rem 5vw; justify-content: flex-start; }
  .contact__right { padding: 4rem 5vw; justify-content: flex-start; }
}

/* ══════════════════════════════════════════════════════
   RESPONSIVE — MOBILE  ≤ 640px
══════════════════════════════════════════════════════ */
@media (max-width: 640px) {
  /* Nav */
  .nav { padding: 0.9rem 5vw; }
  .nav__tagline { font-size: 0.54rem; }

  /* Hero */
  .hero__photo-frame { aspect-ratio: 3/3.5; }
  .hero__text-side { padding: 3rem 5vw 4rem; }
  .hero__eyebrow { font-size: 0.62rem; margin-bottom: 1.2rem; }
  .hero__name-white { font-size: clamp(2.4rem, 13vw, 3.5rem); }
  .hero__name-orange { font-size: clamp(2.2rem, 12vw, 3.2rem); }
  .hero__heading { margin-bottom: 1.4rem; }
  .hero__typing-row { min-height: 3.2rem; margin-bottom: 1.4rem; max-width: none; }
  .hero__typing-text { font-size: 0.95rem; }
  .hero__desc { font-size: 0.9rem; margin-bottom: 1.8rem; }
  .hero__stat { padding: 1.2rem 0.25rem; }
  .hero__stat strong { font-size: 1.4rem; }
  .hero__cta { flex-direction: column; }
  .btn-orange, .btn-outline { text-align: center; }

  /* Section heads */
  .sec-head { padding: 4rem 5vw 2.5rem; }
  .sec-title { font-size: clamp(2rem, 9vw, 3rem); }

  /* About */
  .about__sub { font-size: clamp(1.3rem, 5.5vw, 1.7rem); }

  /* Projects */
  .proj-card__body { padding: 1.6rem; }
  .proj-card--wide .proj-card__body { padding: 1.6rem; }

  /* Services */
  .svc-grid { grid-template-columns: 1fr; }
  .svc-card { padding: 2.5rem 5vw; border-right: none; }

  /* Contact */
  .contact__left { align-items: center; text-align: center; }
  .contact__sub { font-size: clamp(1.5rem, 6vw, 2.2rem); }
  .contact__copy { max-width: 34ch; }
  .contact__socials { justify-content: center; }
  .citem__val { font-size: 0.85rem; }

  /* Footer */
  .footer { flex-direction: column; align-items: flex-start; gap: 0.8rem; padding: 1.6rem 5vw; }
}

/* ══════════════════════════════════════════════════════
   RESPONSIVE — SMALL  ≤ 380px
══════════════════════════════════════════════════════ */
@media (max-width: 380px) {
  .hero__name-white { font-size: clamp(2rem, 14vw, 2.8rem); }
  .hero__name-orange { font-size: clamp(1.85rem, 13vw, 2.6rem); }
  .hero__typing-row { min-height: 2.8rem; }
  .hero__typing-text { font-size: 0.85rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
`;
