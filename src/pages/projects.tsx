import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/* ═══════════════════════════════════════════════════════════════
   TOPICS — the full project catalogue. Projects are still grouped
   by topic here (for the topic label shown on each card), but they
   all render into ONE shared grid below, so a project from Topic A
   sits in the same row as the next project from Topic B rather
   than each topic getting its own separate, mostly-empty grid.
═══════════════════════════════════════════════════════════════ */
const TOPICS = [
  {
    id: "forestry-conservation",
    label: "Forestry & Conservation",
    projects: [
      {
        slug: "zimbabwe-gazetted-forests",
        title: "Zimbabwe Gazetted Forests",
        summary: "Complete boundary documentation and conservation status for seven gazetted forests in Matabeleland province.",
        tags: ["Forestry", "Boundary Mapping", "Conservation"],
      },
    ],
  },
  {
    id: "study-area-maps",
    label: "Study Area Maps",
    projects: [
      {
        slug: "study-area-maps",
        title: "Study Area Maps",
        summary: "A running collection of study area and site location maps produced across various projects.",
        tags: ["Cartography", "Site Location", "Reference Maps"],
      },
    ],
  },
  {
    id: "land-use-land-cover",
    label: "Land Use & Land Cover",
    projects: [
      {
        slug: "land-use-land-cover",
        title: "Land Use Land Cover",
        summary: "Classification and change detection of land use and land cover across selected study areas.",
        tags: ["LULC", "Classification", "Change Detection"],
      },
    ],
  },
  {
    id: "flood-susceptibility-mapping",
    label: "Flood Susceptibility Mapping",
    projects: [
      {
        slug: "flood-susceptibility-mapping",
        title: "Flood Susceptibility Mapping",
        summary: "Modelling flood-prone areas using terrain, hydrological, and land cover indicators.",
        tags: ["Flood Risk", "Hydrology", "GIS Modelling"],
      },
    ],
  },
  {
    id: "remote-sensing-indices",
    label: "Remote Sensing Indices",
    projects: [
      {
        slug: "remote-sensing-indices",
        title: "Remote Sensing Indices",
        summary: "Derivation and analysis of spectral indices (NDVI, NDWI, and others) from satellite imagery.",
        tags: ["Remote Sensing", "Spectral Indices", "Satellite Imagery"],
      },
    ],
  },
  {
    id: "drought-analysis",
    label: "Drought Analysis",
    projects: [
      {
        slug: "drought-analysis",
        title: "Drought Analysis",
        summary: "Assessment of drought conditions and trends using climatic and remote sensing datasets.",
        tags: ["Drought", "Climate", "Time Series"],
      },
    ],
  },
  {
    id: "fire-susceptibility-mapping",
    label: "Fire Susceptibility Mapping",
    projects: [
      {
        slug: "fire-susceptibility-mapping",
        title: "Fire Susceptibility Mapping",
        summary: "Mapping wildfire risk zones based on vegetation, terrain, and climatic factors.",
        tags: ["Fire Risk", "Vegetation", "Susceptibility Modelling"],
      },
    ],
  },
  {
    id: "web-mapping",
    label: "Web Mapping",
    projects: [
      {
        slug: "web-mapping",
        title: "Web Mapping",
        summary: "Interactive, browser-based maps and dashboards for exploring spatial data online.",
        tags: ["Web GIS", "Interactive Maps", "Dashboards"],
      },
    ],
  },
  // Next topics and projects go here as they're ready.
];

const ALL_PROJECTS = TOPICS.flatMap((t) =>
  t.projects.map((p) => ({ ...p, topic: t.label }))
);

export default function ProjectsIndex() {
  const [navScrolled, setNavScrolled] = useState(false);

  useEffect(() => {
    const fn = () => setNavScrolled(window.scrollY > 50);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <>
      <style>{CSS}</style>

      <header className={`pnav${navScrolled ? " pnav--scrolled" : ""}`}>
        <a href="/" className="pnav__mark">KC<span>/</span>SPATIAL</a>
        <a href="/" className="pnav__back">← Home</a>
      </header>

      <section className="ptitle">
        <span className="p-ref">Project Index</span>
        <h1>All Projects</h1>
        <p className="ptitle__subtitle">A growing archive of GIS, remote sensing, and cartography work.</p>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">§ All Entries</p>
        <div className="cat-grid">
          {ALL_PROJECTS.map((p, i) => {
            const num = String(i + 1).padStart(2, "0");
            return (
              <Link key={p.slug} to={`/projects/${p.slug}`} className="cat-card">
                <span className="cat-card__ref">Entry {num} · {p.topic}</span>
                <h3>{p.title}</h3>
                <p>{p.summary}</p>
                <div className="cat-card__tags">
                  {p.tags.slice(0, 3).map((t) => <span key={t}>{t}</span>)}
                </div>
                <span className="cat-card__arrow">View project →</span>
              </Link>
            );
          })}
        </div>
      </section>

      <footer className="pfooter">
        <span>© 2026 Kudzanai Chakavarika</span>
        <a href="/">spatialforce.co.zw</a>
      </footer>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════
   CSS — same tokens/fonts as the rest of the site. One shared grid
   for the whole catalogue: auto-fill with a minmax floor so cards
   wrap into rows together regardless of which topic they belong
   to, rather than each topic forcing its own row.
═══════════════════════════════════════════════════════════════ */
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
  --cream:  #F7F3E9;
  --line:   rgba(32,29,24,0.13);
  --linew:  rgba(247,243,233,0.13);
  --fd: 'Big Shoulders Display', sans-serif;
  --fb: 'IBM Plex Sans', sans-serif;
  --fm: 'IBM Plex Mono', monospace;
}

html, body, #root { width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important; text-align: initial !important; background: var(--night); }
body { font-family: var(--fb); color: var(--ink); overflow-x: hidden; -webkit-font-smoothing: antialiased; }

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.6rem 4vw 1.2rem; }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

/* ── NAV ── */
.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

/* ── TITLE ── */
.ptitle { background: var(--night); padding: 6.4rem 4vw 2.2rem; }
.ptitle h1 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.9rem, 4.2vw, 3rem); line-height: 1.04; letter-spacing: -0.01em;
  color: var(--cream); margin: 0.5rem 0 0.7rem; max-width: 24ch;
}
.ptitle__subtitle { font-size: 0.98rem; font-weight: 300; color: rgba(247,243,233,0.6); max-width: 55ch; }

/* ── SECTIONS ── */
.psection { background: var(--night); padding-bottom: 0.5rem; }
.psection--paper { background: var(--paper); }
.psection--paper .section-tag { color: var(--rust); }

/* ── CATALOGUE GRID — one shared grid, auto-fill, ~3 per row on
   desktop, wraps into new rows together as entries are added ── */
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.6rem;
  padding: 0 4vw 3rem;
}
.cat-card {
  display: flex; flex-direction: column; text-decoration: none;
  border: 1px solid var(--line); border-radius: 3px;
  background: var(--cream); padding: 1.5rem 1.4rem 1.4rem;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.cat-card:hover { border-color: var(--rust); transform: translateY(-3px); box-shadow: 0 10px 24px rgba(32,29,24,0.12); }
.cat-card__ref { font-family: var(--fm); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--rust); display: block; margin-bottom: 0.55rem; }
.cat-card h3 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: 1.2rem; color: var(--ink); line-height: 1.15; margin-bottom: 0.55rem; }
.cat-card p { font-size: 0.84rem; line-height: 1.6; color: #4A463C; margin-bottom: 1rem; flex-grow: 1; }
.cat-card__tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 1.1rem; }
.cat-card__tags span { font-family: var(--fm); font-size: 0.58rem; color: var(--rust-d); border: 1px solid rgba(177,80,42,0.3); padding: 0.24rem 0.55rem; border-radius: 2px; }
.cat-card__arrow { font-family: var(--fm); font-size: 0.68rem; color: var(--ink); border-top: 1px solid var(--line); padding-top: 0.85rem; transition: color 0.2s; }
.cat-card:hover .cat-card__arrow { color: var(--rust-d); }

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

/* ══════════════════ TABLET ≤ 1024px ══════════════════ */
@media (max-width: 1024px) {
  .cat-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
}

/* ══════════════════ MOBILE ≤ 640px ══════════════════ */
@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.8rem; }
  .ptitle h1 { font-size: clamp(1.6rem, 7.5vw, 2.1rem); max-width: none; }
  .section-tag { padding: 1.4rem 6vw 1rem; }
  .cat-grid { grid-template-columns: 1fr; padding: 0 6vw 2rem; }
  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;
