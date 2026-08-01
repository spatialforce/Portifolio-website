import { useState, useEffect } from "react";
import Matopo from "../assets/matopo.webp"
import Bulawayo from "../assets/bulawayo.webp"
import Gweru from "../assets/gweru.webp"
import Mutare from "../assets/mutare.webp"
import Zimbabwe from "../assets/Zimbabwe.webp"
import Matopo2 from "../assets/matopo2.webp"
import Chirumhanzu from"../assets/Chirumhanzu.webp"
import Gokwe from "../assets/gokwe.webp";
import Mbire from "../assets/Mbire.webp";

const PAGE = {
  title: "Study Area Maps",
  subtitle: "A running collection of study area and site location maps.",
  intro:
    "This page collects sample study area maps produced across various projects in Zimbabwe. Content is being added continuously, so check back for new entries.",
};

const MAPS = [
  {
    id: 1,
    title: "Matopo National Park",
    province: "Matebeleland South",
    focus: "Data Sampling Sites and Vegetation Studies",
    coords: "20.55°S, 28.51°E",
    img: Matopo,
  },
  {
    id: 2,
    title: "Bulawayo",
    province: "Bulawayo Province",
    focus: "Industrial land-use decline & re-purposing",
    coords: "20.15°S, 28.58°E",
    img: Bulawayo,
  },
  {
    id: 3,
    title: "Mutare",
    province: "Manicaland",
    focus: " Two study areas in one map",
    coords: "18.97°S, 32.65°E",
    img: Mutare,
  },
  {
    id: 4,
    title: "Gweru",
    province: "Midlands",
    focus: "General Study Area Map , showcase",
    coords: "19.45°S, 29.82°E",
    img: Gweru
  },
  {
    id: 6,
    title: "Zimbabwe",
    province: "SADC",
    focus: "Colourful Study Area Maps",
    coords: "18.93°S, 29.82°E",
    img: Zimbabwe
  },
  {
    id: 7,
    title: "Matopo",
    province: "Matebeleland South",
    focus: "Mining Claims Study Area Map",
    coords: "17.37°S, 30.20°E",
    img: Matopo2,
  },
  {
    id: 7,
    title: "Mbire",
    province: "Mashonaland Central",
    focus: " District Electoral and Administrative Wards",
    coords: "16.00°S, 30.90°E",
    img: Mbire,
  },
  {
    id: 10,
    title: "Gokwe",
    province: "Midlands",
    focus: "Simple study Area Map Design",
    coords: "18.20°S, 28.93°E",
    img: Gokwe,
  },
  {
    id: 12,
    title: "Chirumhanzu",
    province: "Midlands",
    focus: " Baseline Infrastructure and Biophysical Map",
    coords: "19.30°S, 30.52°E" ,
    img: Chirumhanzu,
  },
];

export default function StudyAreaMaps() {
  const [navScrolled, setNavScrolled] = useState(false);
  const [lightbox, setLightbox] = useState<number | null>(null);

  useEffect(() => {
    const fn = () => setNavScrolled(window.scrollY > 50);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  useEffect(() => {
    if (lightbox === null) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setLightbox(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [lightbox]);

  return (
    <>
      <style>{CSS}</style>

      <header className={`pnav${navScrolled ? " pnav--scrolled" : ""}`}>
        <a href="/" className="pnav__mark">KC<span>/</span>SPATIAL</a>
        <a href="/projects" className="pnav__back">← All Projects</a>
      </header>

      <section className="ptitle">
        <span className="p-ref">Field Report</span>
        <h1>{PAGE.title}</h1>
        <p className="ptitle__subtitle">{PAGE.subtitle}</p>
      </section>

      <section className="psection">
        <p className="section-tag">§ About This Collection</p>
        <p className="poverview">{PAGE.intro}</p>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">§ Sample Maps · Zimbabwe</p>
        <div className="map-grid">
          {MAPS.map((m, i) => (
            <button key={m.id} type="button" className="map-card" onClick={() => setLightbox(i)} aria-label={`View larger version of ${m.title}`}>
              <img src={m.img} alt={m.title} loading="lazy" />
              <span className="map-card__tag">View full map</span>
              <span className="map-card__info">
                <span className="map-card__label">{m.title}</span>
                <span className="map-card__province">{m.province}</span>
                <span className="map-card__focus">{m.focus}</span>
                <span className="map-card__coords">{m.coords}</span>
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className="psection psection--paper pcta">
        <h2>Want the full details of this project?</h2>
        <p>This page covers a sample of study area maps. For full-resolution maps, raw survey data, or additional study areas not yet published here, get in touch directly.</p>
        <div className="pcta__actions">
          <a href="/#contact" className="btn-solid">Consult on This Project</a>
          <a href="mailto:kudzanaichakavarika67@gmail.com" className="btn-line">Email Directly</a>
        </div>
      </section>

      <footer className="pfooter">
        <span>© 2026 Kudzanai Chakavarika</span>
        <a href="/">spatialforce.co.zw</a>
      </footer>

      {lightbox !== null && (
        <div className="plightbox" onClick={() => setLightbox(null)}>
          <button className="plightbox__close" onClick={() => setLightbox(null)} aria-label="Close">×</button>
          <img src={MAPS[lightbox].img} alt={MAPS[lightbox].title} onClick={(e) => e.stopPropagation()} />
          <div className="plightbox__caption" onClick={(e) => e.stopPropagation()}>
            <p className="plightbox__title">{MAPS[lightbox].title} <span>· {MAPS[lightbox].province}</span></p>
            <p className="plightbox__focus">{MAPS[lightbox].focus}</p>
            <p className="plightbox__coords">{MAPS[lightbox].coords}</p>
          </div>
        </div>
      )}
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════
   CSS — same tokens/fonts as the rest of the site. Map cards are
   matted and contain-fit, same fix used everywhere else on the
   site, so real maps display at their true proportions once added.
   The info block (province / focus / coords) is always visible;
   the "view full map" tag stays hover-revealed on desktop, shown
   permanently on touch devices since there's no hover there.
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

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.6rem 4vw 1rem; }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

/* ── NAV ── */
.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

/* ── TITLE ── */
.ptitle { background: var(--night); padding: 6.4rem 4vw 1.2rem; }
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
.poverview { padding: 0 4vw 1.6rem; font-size: 0.96rem; line-height: 1.8; color: rgba(247,243,233,0.6); max-width: 74ch; }

/* ── MAP GRID — 4 per row on desktop ── */
.map-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.8rem;
  padding: 0 4vw 3rem;
}
.map-card {
  position: relative; display: block; width: 100%; padding: 0;
  border: 1px solid var(--line); background: var(--paper2); border-radius: 3px;
  overflow: hidden; cursor: zoom-in; text-align: left;
}
.map-card img { width: 100%; height: 18rem; object-fit: contain; display: block; padding: 1.1rem; box-sizing: border-box; }
.map-card__tag {
  position: absolute; top: 0.6rem; right: 0.6rem;
  font-family: var(--fm); font-size: 0.56rem; color: var(--cream);
  background: rgba(32,29,24,0.78); padding: 0.24rem 0.5rem; border-radius: 2px;
  opacity: 0; transition: opacity 0.2s;
}
.map-card:hover .map-card__tag { opacity: 1; }

.map-card__info {
  display: flex; flex-direction: column; gap: 0.22rem;
  border-top: 1px solid var(--line); padding: 0.65rem 0.75rem 0.8rem;
}
.map-card__label { font-family: var(--fd); font-weight: 700; font-size: 1rem; letter-spacing: 0.01em; color: var(--ink); text-transform: uppercase; }
.map-card__province { font-family: var(--fm); font-size: 0.62rem; letter-spacing: 0.04em; color: var(--rust-d); }
.map-card__focus { font-family: var(--fb); font-size: 0.74rem; line-height: 1.4; color: rgba(32,29,24,0.72); }
.map-card__coords { font-family: var(--fm); font-size: 0.6rem; color: rgba(32,29,24,0.42); margin-top: 0.1rem; }

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

/* ── CTA ── */
.pcta { padding: 2.6rem 4vw 3.6rem; text-align: left; border-top: 1px solid var(--line); }
.pcta h2 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.5rem, 2.8vw, 2.1rem); line-height: 1.08; letter-spacing: -0.01em;
  color: var(--ink); max-width: 26ch; margin-bottom: 0.9rem;
}
.pcta p { font-size: 0.94rem; line-height: 1.75; color: rgba(32,29,24,0.68); max-width: 62ch; margin-bottom: 1.6rem; }
.pcta__actions { display: flex; gap: 0.9rem; flex-wrap: wrap; }
.btn-solid, .btn-line {
  font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.04em;
  padding: 0.85rem 1.5rem; border-radius: 2px; text-decoration: none; transition: background 0.2s, color 0.2s, border-color 0.2s;
  display: inline-block;
}
.btn-solid { background: var(--rust); color: var(--cream); border: 1px solid var(--rust); }
.btn-solid:hover { background: var(--rust-d); border-color: var(--rust-d); }
.btn-line { background: transparent; color: var(--ink); border: 1px solid var(--line); }
.btn-line:hover { border-color: var(--rust); color: var(--rust-d); }

/* ── LIGHTBOX ── */
.plightbox { position: fixed; inset: 0; z-index: 500; background: rgba(15,16,12,0.95); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 6vh 5vw; cursor: zoom-out; }
.plightbox img { max-width: 100%; max-height: 74vh; object-fit: contain; border-radius: 3px; cursor: default; }
.plightbox__caption { margin-top: 1.2rem; text-align: center; cursor: default; max-width: 90vw; }
.plightbox__title { font-family: var(--fd); font-weight: 800; text-transform: uppercase; font-size: 1.3rem; color: var(--cream); letter-spacing: 0.01em; }
.plightbox__title span { font-family: var(--fm); font-weight: 500; font-size: 0.72rem; text-transform: none; color: var(--brass); margin-left: 0.4rem; }
.plightbox__focus { font-family: var(--fb); font-size: 0.86rem; color: rgba(247,243,233,0.65); margin-top: 0.35rem; }
.plightbox__coords { font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.35); margin-top: 0.3rem; }
.plightbox__close { position: absolute; top: 2rem; right: 2rem; width: 2.4rem; height: 2.4rem; border-radius: 50%; border: 1px solid rgba(247,243,233,0.25); background: rgba(247,243,233,0.05); color: var(--cream); font-size: 1.3rem; display: flex; align-items: center; justify-content: center; cursor: pointer; }

/* ══════════════════ TABLET ≤ 1024px ══════════════════
   Below this width there's no hover, so the "view full map" tag
   is shown permanently rather than hidden behind a hover state. ══ */
@media (max-width: 1024px) {
  .map-grid { grid-template-columns: repeat(2, 1fr); }
  .map-card img { height: 14rem; }
  .map-card__tag { opacity: 1; }
}

/* ══════════════════ MOBILE ≤ 640px ══════════════════ */
@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.2rem; }
  .ptitle h1 { font-size: clamp(1.6rem, 7.5vw, 2.1rem); max-width: none; }
  .section-tag { padding: 1.4rem 6vw 1rem; }
  .poverview { padding: 0 6vw 1.2rem; }
  .map-grid { grid-template-columns: 1fr; padding: 0 6vw 2rem; gap: 1.2rem; }
  .map-card img { height: 12rem; padding: 0.8rem; }
  .map-card__label { font-size: 0.9rem; }
  .map-card__focus { font-size: 0.68rem; }
  .pcta { padding: 2rem 6vw 2.6rem; }
  .pcta__actions { flex-direction: column; }
  .btn-solid, .btn-line { text-align: center; width: 100%; }
  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;
