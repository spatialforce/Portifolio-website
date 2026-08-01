import { useState, useEffect } from "react";
import Gwaai from "../assets/gwaai.webp"
import Bembesi from "../assets/Mbembesi.webp"
import Kavira from "../assets/kavira.webp"
import Lake_alice from "../assets/lake_alice.webp"
import Gwampa from "../assets/gwampa.webp"
import Inseze_ext from "../assets/inseze_extension.webp"
import Chesa from "../assets/chesa.webp"

/* ═══════════════════════════════════════════════════════════════
   REAL CONTENT — Matabeleland North Gazetted Forests dataset.
═══════════════════════════════════════════════════════════════ */
const PAGE = {
  sheetRef: "Field Report 06/06",
  title: "Matabeleland North Gazetted Forests",
  subtitle: "Complete boundary documentation and conservation status",
  tags: ["Forestry", "Boundary Mapping", "Conservation", "Forest Act Cap 19:05", "GIS"],
  intro:
    "This document provides complete boundary descriptions, conservation status, and threat assessments for seven gazetted forests in Matabeleland province. Some forests are still missing from this dataset. We are working to gather additional records and will update this resource as new data becomes available. All maps and information were produced by Spatial Force in collaboration with Chesa Research Station, and content complies with the Forest Act (Chapter 19:05). If you have information that could improve this resource, please get in touch so we can better serve stakeholders.",
  dataSource: "Forestry Commission of Zimbabwe, Chesa Research Station (2024 Survey)",
  mapsReference: "1:50,000 Topographic Series (Surveyor-General)",
};

const FORESTS = [
  {
    fig: "Fig 1",
    name: "Gwaai Forest",
    img: Gwaai,
    location: "Matabeleland North, along the Bulawayo to Victoria Falls Road",
    totalArea: "144,265 ha",
    remaining: "127,880.06 ha (88.6%, 2024)",
    legalStatus: "Major Reserve Forest",
    boundary:
      "Bounded from Pioneer Block East SW beacon to Franklands Farm, along the Umguza/Gwaai Rivers to Gutamegwa, Railway Strip 244 Matupula, Sunbeam, Melrose, and back via Bembezi River to the Bulawayo–Victoria Falls Road.",
    settlements: "Along Gwayi River and Mbembesi River.",
    features:
      "One of the largest reserve forests in Matabeleland North. Bisected by the Bulawayo–Victoria Falls Road. Contains sections of the Gwayi and Mbembesi rivers.",
    threats:
      "16,061.60 ha under cultivation with homesteads. 322.80 ha lost to powerline buffer clearance. Ongoing vegetation clearance for the Gwaai-Shangani pipeline. Riverine settlements along the Gwayi and Mbembesi rivers.",
    encroachment: "16,061.60 ha lost to cultivation and homesteads, plus 322.80 ha to powerlines. Pipeline clearance is ongoing.",
  },
  {
    fig: "Fig 2",
    name: "Bembesi Forest Reserve",
    img: Bembesi,
    location: "Bubi District, southeast forms the Umguza District boundary",
    totalArea: "55,100 ha",
    remaining: "47,506 ha (86.2%)",
    legalStatus: "Forest Reserve",
    boundary:
      "Bounded from Pioneer Block East SE beacon to Westgate, along Bembezi River to Glenarton West, Nthobi Ranch, Eland Block, Franklands Farm, and back to the starting point.",
    settlements: "Northern boundary shows cultivation along the Mbembesi River, running west to east.",
    features: "Major riverine forest along the Mbembesi River. Forms a cross-district boundary between Bubi and Umguza.",
    threats: "7,539.10 ha affected by cultivation. Riverine settlements along the Mbembesi River. Northern boundary encroachment.",
    encroachment: "7,539.10 ha converted to cultivation and settlements, primarily along the Mbembesi River and the northern boundary.",
  },
  {
    fig: "Fig 3",
    name: "Kavira Forest",
    img: Kavira,
    location: "Binga District",
    totalArea: "28,200 ha",
    remaining: "28,013.44 ha (99.3%)",
    legalStatus: "Gazetted Forest",
    boundary:
      "Bounded by a line from Mlibizi River into Lake Kariba, south to Liwando River, southwest to the game fence at 35KNL074050, to MK861922 on the Gwai River, north to Lake Kariba full-supply level. References: 1:50,000 maps Masutu 1827A1 and Boma 1826B2.",
    settlements: "Minimal. This is the least affected gazetted forest in the dataset.",
    features: "Minimal human impact compared to other forests in the dataset. Boundary integrity is well preserved.",
    threats: "Minor cultivation encroachment.",
    encroachment: "Only 186.5 ha lost to cultivation.",
  },
  {
    fig: "Fig 4",
    name: "Lake Alice Forest",
    img: Lake_alice,
    location: "Southern boundary of Nkayi District",
    totalArea: "39,000 ha",
    remaining: "34,765.60 ha (89.1%, 2024)",
    legalStatus: "Under severe pressure from human activities",
    boundary:
      "The northern boundary has lost 3,420.6 ha to human settlements and cultivation, affecting Lake Alice Dam's water retention capacity.",
    settlements: "Encroachment along the northern and southern edges, with visible conversion of forest to farmland.",
    features: "Critical watershed for Lake Alice Dam. A significant woodland area in Nkayi District. Dam water retention is declining due to forest loss.",
    threats: "3,420.6 ha converted to agriculture and settlements. Northern and southern boundary encroachment. Reduced water retention in Lake Alice Dam.",
    encroachment: "3,420.6 ha lost, primarily to cultivation and settlements.",
  },
  {
    fig: "Fig 5",
    name: "Gwampa Forest",
    img: Gwampa,
    location: "Matabeleland, Nkayi District, shares a boundary with Lake Alice",
    totalArea: "47,000 ha",
    remaining: "43,579.82 ha",
    legalStatus: "Forestry Commission of Zimbabwe, Conservation and Extension Unit",
    boundary:
      "Bounded by the Gwampa River from map reference 35KPJ992752 south to Kenilworth Block at 35KQJ000699, then southwest to Goodwood Block at 35KPJ510811, north to the Gwampa River at PJ509904.",
    settlements: "Primary encroachment runs from the east to the southeast sections.",
    features: "Shares a watershed with Lake Alice Forest.",
    threats: "Human encroachment in the eastern and southeastern sections.",
    encroachment: "3,420.18 ha lost, out of a total area of 47,000 ha.",
  },
  {
    fig: "Fig 6",
    name: "Inseze extension",
    img: Inseze_ext,
    location: "Western side of Umguza District",
    totalArea: "8,400 ha",
    remaining: "7,928 ha (94.4%)",
    legalStatus: "Protected Forest Area",
    boundary:
      "Bounded by a line from Seafield Valley's western beacon southeast to its southern beacon, southwest to the Khami River, down river to the Seafield Estate boundary.",
    settlements: "Primary loss is due to cultivation activities.",
    features: "Relatively well-preserved forest cover.",
    threats: "Cultivation encroachment.",
    encroachment: "514.89 ha lost to cultivation.",
  },
  {
    fig: "Fig 7",
    name: "Chesa Forest",
    img: Chesa,
    location: "Umguza District",
    totalArea: "14,250 ha",
    remaining: "12,915 ha",
    legalStatus: "Protected Forest Area",
    boundary:
      "Bounded by a line from Compensation's SW beacon east to Bongolo, north to Caithness, southeast to Imvani, south to Mandau, southwest to Naseby, northwest to the starting point.",
    settlements: "Primary encroachment is at the southwest and northeast ends.",
    features: "Includes 135 ha of eucalyptus plantations.",
    threats: "Human cultivation encroachment. Settlement expansion.",
    encroachment: "199.83 ha lost, out of a total area of 14,250 ha.",
  },
];

export default function ForestResourcesProject() {
  const [navScrolled, setNavScrolled] = useState(false);
  const [lightbox, setLightbox] = useState<{ src: string; caption: string } | null>(null);

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

      {/* ── TITLE — plain text, no photo. ── */}
      <section className="ptitle">
        <span className="p-ref">{PAGE.sheetRef}</span>
        <h1>{PAGE.title}</h1>
        <p className="ptitle__subtitle">{PAGE.subtitle}</p>
        <div className="ptags">
          {PAGE.tags.map((t) => <span key={t}>{t}</span>)}
        </div>
      </section>

      {/* ── INTRO ── */}
      <section className="psection">
        <p className="section-tag">§ About This Record</p>
        <p className="poverview">{PAGE.intro}</p>
      </section>

      {/* ── FOREST SHEETS ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Forest Reserves: Boundary and Status</p>

        <div className="fsheet-list">
          {FORESTS.map((f, i) => {
            const caption = `${f.fig}: ${f.name} boundary map`;
            return (
              <article key={f.name} className={`fsheet${i % 2 === 1 ? " fsheet--rev" : ""}`}>
                <button
                  type="button"
                  className="fsheet__frame"
                  onClick={() => setLightbox({ src: f.img, caption })}
                  aria-label={`View larger map of ${f.name}`}
                >
                  <img src={f.img} alt={caption} loading="lazy" />
                  <span className="fsheet__tag">View full map</span>
                </button>

                <div className="fsheet__info">
                  <span className="fsheet__ref">{f.fig}, Sheet {String(i + 1).padStart(2, "0")}/07</span>
                  <h3>{f.name}</h3>
                  <p className="fsheet__location">{f.location}</p>

                  <p className="fsheet__stats">
                    <span className="stat-label">Total Area</span> <strong>{f.totalArea}</strong>
                    <span className="stat-sep">·</span>
                    <span className="stat-label">Remaining</span> <strong>{f.remaining}</strong>
                    <span className="stat-sep">·</span>
                    <span className="stat-label">Legal Status</span> <strong>{f.legalStatus}</strong>
                  </p>

                  <div className="fsheet__block">
                    <span className="fsheet__block-label">Boundary Description</span>
                    <p>{f.boundary}</p>
                  </div>

                  <div className="fsheet__block">
                    <span className="fsheet__block-label">Settlements</span>
                    <p>{f.settlements}</p>
                  </div>

                  <div className="fsheet__block">
                    <span className="fsheet__block-label">Key Ecological Features</span>
                    <p>{f.features}</p>
                  </div>

                  <div className="fsheet__block">
                    <span className="fsheet__block-label">Major Threats</span>
                    <p>{f.threats}</p>
                  </div>

                  <div className="fsheet__block fsheet__block--last">
                    <span className="fsheet__block-label">Human Encroachment</span>
                    <p>{f.encroachment}</p>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* ── SOURCES ── */}
      <section className="psection">
        <p className="section-tag section-tag--light">§ Data and References</p>
        <ul className="psources">
          <li><span>Data Source</span>{PAGE.dataSource}</li>
          <li><span>Maps Reference</span>{PAGE.mapsReference}</li>
        </ul>
      </section>

      {/* ── CTA ── */}
      <section className="psection psection--paper pcta">
        <h2>Want the full details of this project?</h2>
        <p>This page covers the core boundary and conservation data. For full-resolution maps, raw survey data, or additional forests not yet published here, get in touch directly.</p>
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
          <img src={lightbox.src} alt={lightbox.caption} onClick={(e) => e.stopPropagation()} />
          <p onClick={(e) => e.stopPropagation()}>{lightbox.caption}</p>
        </div>
      )}
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════
   CSS — hero photo removed entirely. Stat cards replaced with a
   single document-style line. Lists replaced with plain paragraphs
   (no bullets, no dash markers). Spacing tightened throughout.
   The map-view label is always visible below tablet width, since
   touch devices have no hover state to reveal it.
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

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.6rem 6vw 1rem; }
.section-tag--light { color: var(--brass); }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

.btn-solid, .btn-line { display: inline-block; font-family: var(--fm); font-size: 0.8rem; font-weight: 600; letter-spacing: 0.04em; text-decoration: none; padding: 0.85rem 1.9rem; border-radius: 2px; cursor: pointer; transition: background 0.2s, color 0.2s, transform 0.15s; }
.btn-solid { background: var(--rust); color: var(--cream); border: 1px solid var(--rust); }
.btn-solid:hover { background: var(--rust-d); border-color: var(--rust-d); transform: translateY(-2px); }
.btn-line { background: transparent; color: var(--brass); border: 1px solid rgba(200,155,74,0.5); }
.btn-line:hover { background: rgba(200,155,74,0.1); border-color: var(--brass); }

/* ── NAV ── */
.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

/* ══════════════════════════════════════════
   TITLE — plain text block, no image. Just enough top padding to
   clear the fixed nav.
══════════════════════════════════════════ */
.ptitle { background: var(--night); padding: 6.4rem 4vw 1.2rem; }
.ptitle h1 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.9rem, 4.2vw, 3rem); line-height: 1.04; letter-spacing: -0.01em;
  color: var(--cream); margin: 0.5rem 0 0.7rem; max-width: 24ch;
}
.ptitle__subtitle { font-size: 0.98rem; font-weight: 300; color: rgba(247,243,233,0.6); max-width: 55ch; margin-bottom: 1.1rem; }
.ptags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.ptags span { font-family: var(--fm); font-size: 0.64rem; color: var(--brass); border: 1px solid rgba(200,155,74,0.35); padding: 0.3rem 0.6rem; border-radius: 2px; }

/* ── SECTIONS ── */
.psection { background: var(--night); padding-bottom: 0.5rem; }
.psection--paper { background: var(--paper); }
.psection--paper .section-tag { color: var(--rust); }
.poverview { padding: 0 4vw 1.6rem; font-size: 0.96rem; line-height: 1.8; color: rgba(247,243,233,0.6); max-width: 74ch; }

/* ── FOREST SHEETS ── */
.fsheet-list { display: flex; flex-direction: column; padding: 0 4vw 0.5rem; }
.fsheet { display: grid; grid-template-columns: 1fr 1.35fr; gap: 2.6vw; padding: 2.2rem 0; border-bottom: 1px solid var(--line); align-items: start; }
.fsheet:first-child { border-top: 1px solid var(--line); }
.fsheet--rev { grid-template-columns: 1.35fr 1fr; }
.fsheet--rev .fsheet__frame { order: 2; }
.fsheet--rev .fsheet__info { order: 1; }

/* map frame: matted, contain-fit, so real survey maps keep their
   true proportions instead of being force-cropped. */
.fsheet__frame {
  position: relative; display: flex; align-items: center; justify-content: center;
  width: 100%; padding: 1rem; border: 1px solid var(--line);
  background: var(--paper2); border-radius: 3px; overflow: hidden;
  cursor: zoom-in; align-self: start;
}
.fsheet__frame img { width: 100%; height: auto; max-height: 26rem; object-fit: contain; display: block; border-radius: 1px; }
.fsheet__tag {
  position: absolute; bottom: 0.6rem; right: 0.6rem;
  font-family: var(--fm); font-size: 0.58rem; color: var(--cream);
  background: rgba(32,29,24,0.78); padding: 0.28rem 0.55rem; border-radius: 2px;
  opacity: 0; transition: opacity 0.2s;
}
.fsheet__frame:hover .fsheet__tag { opacity: 1; }

.fsheet__ref { font-family: var(--fm); font-size: 0.66rem; color: var(--rust); letter-spacing: 0.04em; display: block; margin-bottom: 0.4rem; }
.fsheet__info h3 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: clamp(1.15rem, 1.8vw, 1.5rem); color: var(--ink); line-height: 1.1; margin-bottom: 0.3rem; }
.fsheet__location { font-size: 0.85rem; color: #4A463C; font-style: italic; margin-bottom: 0.9rem; }

/* stats: one plain document line, not cards. */
.fsheet__stats { font-size: 0.84rem; color: var(--ink); line-height: 1.9; margin-bottom: 1rem; }
.fsheet__stats .stat-label { font-family: var(--fm); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--rust); }
.fsheet__stats strong { font-weight: 600; }
.fsheet__stats .stat-sep { color: var(--line); margin: 0 0.55rem; }

.fsheet__block { margin-bottom: 0.85rem; }
.fsheet__block--last { margin-bottom: 0; }
.fsheet__block-label { font-family: var(--fm); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--rust); display: block; margin-bottom: 0.3rem; }
.fsheet__block p { font-size: 0.85rem; line-height: 1.65; color: #3C382F; max-width: 60ch; }

/* ── SOURCES ── */
.psources { list-style: none; padding: 0 4vw 2.2rem; display: flex; flex-direction: column; gap: 0.6rem; max-width: 60ch; }
.psources li { font-size: 0.86rem; color: rgba(247,243,233,0.6); display: flex; gap: 0.6rem; }
.psources li span { font-family: var(--fm); font-size: 0.66rem; color: var(--brass); text-transform: uppercase; letter-spacing: 0.03em; flex-shrink: 0; min-width: 9rem; }

/* ── CTA ── */
.pcta { padding: 2.6rem 4vw 3rem; text-align: center; }
.pcta h2 { font-family: var(--fd); font-weight: 800; text-transform: uppercase; font-size: clamp(1.4rem, 2.6vw, 2rem); color: var(--ink); margin-bottom: 0.6rem; }
.pcta p { color: #4A463C; margin-bottom: 1.3rem; max-width: 55ch; margin-left: auto; margin-right: auto; }
.pcta__actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

/* ── LIGHTBOX ── */
.plightbox { position: fixed; inset: 0; z-index: 500; background: rgba(15,16,12,0.95); display: flex; align-items: center; justify-content: center; padding: 6vh 5vw; cursor: zoom-out; }
.plightbox img { max-width: 100%; max-height: 82vh; object-fit: contain; border-radius: 3px; cursor: default; }
.plightbox p { position: absolute; bottom: 4vh; left: 50%; transform: translateX(-50%); font-family: var(--fm); font-size: 0.7rem; color: rgba(247,243,233,0.6); max-width: 90vw; text-align: center; }
.plightbox__close { position: absolute; top: 2rem; right: 2rem; width: 2.4rem; height: 2.4rem; border-radius: 50%; border: 1px solid rgba(247,243,233,0.25); background: rgba(247,243,233,0.05); color: var(--cream); font-size: 1.3rem; display: flex; align-items: center; justify-content: center; cursor: pointer; }

/* ══════════════════ TABLET ≤ 900px ══════════════════
   Below this width there's no hover, so the map-view label is
   shown permanently rather than hidden behind a hover state. ══ */
@media (max-width: 900px) {
  .fsheet, .fsheet--rev { grid-template-columns: 1fr; }
  .fsheet--rev .fsheet__frame, .fsheet--rev .fsheet__info { order: initial; }
  .fsheet__frame img { max-height: 20rem; }
  .fsheet__tag { opacity: 1; }
}

/* ══════════════════ MOBILE ≤ 640px ══════════════════ */
@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.8rem; }
  .ptitle h1 { font-size: clamp(1.6rem, 7.5vw, 2.1rem); max-width: none; }

  .section-tag { padding: 1.8rem 6vw 0.9rem; }
  .poverview { padding: 0 6vw 1.2rem; }

  .fsheet-list { padding: 0 6vw 0.5rem; }
  .fsheet { padding: 1.6rem 0; gap: 1.1rem; }
  .fsheet__frame img { max-height: 16rem; }
  .fsheet__stats { line-height: 1.7; }
  .fsheet__stats .stat-sep { display: block; height: 0.3rem; margin: 0; }

  .psources { padding: 0 6vw 2rem; }
  .psources li { flex-direction: column; gap: 0.15rem; }
  .psources li span { min-width: 0; }

  .pcta { padding: 2.2rem 6vw 2.4rem; }
  .pcta__actions { flex-direction: column; align-items: stretch; }
  .pcta__actions a { width: 100%; text-align: center; box-sizing: border-box; }

  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;
