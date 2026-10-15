import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

// Exported from the docx at 2800px wide. Put the three files in /src/assets/ (or edit the paths).
import factorsA from "../assets/Chimanimani_Factors_A.webp"; // NDVI, drainage density, slope, flow length
import factorsB from "../assets/Chimanimani_Factors_B.webp"; // TWI, distance to river
import floodRisk from "../assets/Chimanimani_Flood_Risk.webp"; // final flood risk map

/* ═══════════════════════════════════════════════════════════════
   DATA — Chimanimani flood susceptibility (weighted overlay)
═══════════════════════════════════════════════════════════════ */

// Six factors, reclassified to 1 (very low) – 5 (very high) risk.
const FACTORS = [
  { name: "Slope", weight: 25, high: "0 – 6.85°", why: "Gentle ground holds water instead of shedding it." },
  { name: "Distance to river", weight: 20, high: "0 – 250 m", why: "Closest to channels that overtop first." },
  { name: "Topographic Wetness Index", weight: 20, high: "9.68 – 20.82", why: "Terrain shaped to collect and retain water." },
  { name: "Drainage density", weight: 15, high: "0.25 – 0.37 km/km²", why: "Dense channel networks concentrate runoff." },
  { name: "NDVI", weight: 10, high: "-0.14 – 0.14", why: "Bare ground sheds rain and infiltrates little." },
  { name: "Flow length", weight: 10, high: "0 – 10,213 m", why: "Short flow paths reach channels quickly." },
];

// Final flood risk map — area by class
const RISK_CLASSES = ["Very low", "Low", "Moderate", "High", "Very high"];
const AREA_HA = [49108.295, 109474.26, 94152.638, 55824.501, 24900.268];

// OpenStreetMap buildings by risk class
const BUILDINGS = [1617, 12571, 18892, 17684, 8853];

const sum = (a: number[]) => a.reduce((x, y) => x + y, 0);
const TOTAL_HA = sum(AREA_HA); // 333,459.962 ha
const TOTAL_BLD = sum(BUILDINGS); // 59,617
const areaPct = AREA_HA.map((v) => (v / TOTAL_HA) * 100);
const bldPct = BUILDINGS.map((v) => (v / TOTAL_BLD) * 100);
const HIGH_AREA = areaPct[3] + areaPct[4]; // 24.2
const HIGH_BLD = bldPct[3] + bldPct[4]; // 44.5

const STATS = [
  { value: `${HIGH_AREA.toFixed(1)}%`, label: "Of the district rated high or very high flood risk" },
  { value: `${HIGH_BLD.toFixed(1)}%`, label: "Of 59,617 buildings sit in high or very high risk zones" },
  { value: `${(HIGH_BLD / HIGH_AREA).toFixed(1)}×`, label: "Buildings are over-represented in high-risk land versus its share of area" },
  { value: "6", label: "Environmental and physical factors combined in a weighted overlay" },
];

// Gweru (Case II) maps - rename to match your files or edit the two paths.
import gwStudyArea from "../assets/Gweru_Study_Area.webp";
import gwMaps from "../assets/Gweru_Flood_Susceptibility_Maps.webp"; // 3 maps in one layout
const SEO = {
  title: "Flood Susceptibility Mapping — Chimanimani District, Zimbabwe | Kudzanai Chakavarika",
  description:
    "GIS and remote sensing flood susceptibility map for Chimanimani District, Zimbabwe: six weighted factors, 24.2% of the district at high or very high risk, and 44.5% of 59,617 buildings exposed. By Kudzanai Chakavarika.",
};

const f1 = (n: number) => n.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const f0 = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 0 });
const f3 = (n: number) => n.toLocaleString(undefined, { minimumFractionDigits: 3, maximumFractionDigits: 3 });

export default function FloodSusceptibilityMapping() {
  const [navScrolled, setNavScrolled] = useState(false);

  useEffect(() => {
    const fn = () => setNavScrolled(window.scrollY > 50);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  useEffect(() => {
    const prev = document.title;
    document.title = SEO_ALL.title;
    let tag = document.querySelector<HTMLMetaElement>('meta[name="description"]');
    const created = !tag;
    if (!tag) {
      tag = document.createElement("meta");
      tag.setAttribute("name", "description");
      document.head.appendChild(tag);
    }
    const prevDesc = tag.getAttribute("content");
    tag.setAttribute("content", SEO_ALL.description);
    return () => {
      document.title = prev;
      if (created) tag?.parentNode?.removeChild(tag);
      else if (prevDesc !== null) tag?.setAttribute("content", prevDesc);
    };
  }, []);

  return (
    <>
      <style>{CSS}</style>

      <header className={`pnav${navScrolled ? " pnav--scrolled" : ""}`}>
        <a href="/" className="pnav__mark">KC<span>/</span>SPATIAL</a>
        <Link to="/projects" className="pnav__back">← All Projects</Link>
      </header>

      <section className="ptitle">
        <span className="p-ref">Project · Flood Susceptibility Mapping</span>
        <h1>Flood Susceptibility Mapping — Zimbabwe Case Studies</h1>
        <p className="ptitle__subtitle">
          Two GIS and remote sensing flood susceptibility studies in Zimbabwe: a weighted-overlay map of Chimanimani, one of the country's most
          flood-prone districts, and a Sentinel-1 radar map of Gweru Urban.
        </p>
      </section>

      <nav className="case-nav">
        <a href="#case-chimanimani">Case I &middot; Chimanimani District, Weighted Overlay</a>
        <a href="#case-gweru">Case II &middot; Gweru Urban, SAR Moisture</a>
      </nav>

      <section className="case-divider" id="case-chimanimani">
        <span className="p-ref">Case Study I</span>
        <h2>Chimanimani District - Flood Susceptibility</h2>
        <p>
          Six environmental and physical factors combined in a weighted overlay to map flood risk across
          the district hit by Cyclone Idai, and to count the buildings standing in high-risk ground.
        </p>
      </section>

      <section className="stat-strip">
        {STATS.map((s) => (
          <div key={s.label} className="stat-strip__item">
            <span className="stat-strip__value">{s.value}</span>
            <span className="stat-strip__label">{s.label}</span>
          </div>
        ))}
      </section>

      {/* ── CONTEXT ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Context</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Why Chimanimani</h2>
              <p className="proj-p">
                Floods are among the most common natural disasters worldwide, and the burden falls hardest on
                low and middle-income countries. Zimbabwe has seen it first-hand: Cyclone Eline in 2000 killed
                more than 700 people across Zimbabwe and Mozambique, and in 2019 Cyclone Idai brought floods and
                landslides that affected at least half of Chimanimani's population, killing over 300 people with
                hundreds more missing (Matsvange et al., 2020).
              </p>
              <p className="proj-p" style={{ marginTop: "0.9rem" }}>
                Idai exposed weaknesses in the district's disaster risk management and early warning. A simple,
                repeatable map of flood-prone ground is a practical first step towards mitigation and planning.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Objectives</h2>
              <p className="proj-p">
                1. Assess how environmental and physical factors shape flood risk in the district.
              </p>
              <p className="proj-p" style={{ marginTop: "0.6rem" }}>
                2. Map the spatial distribution of flood risk zones using overlay analysis.
              </p>
              <p className="proj-p" style={{ marginTop: "0.6rem" }}>
                3. Identify the areas and communities most vulnerable, to support disaster risk management.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── METHOD + FACTOR TABLE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Method — Six Factors, One Weighted Overlay</p>
        <div className="proj-body">
          <p className="proj-p" style={{ marginBottom: "1.2rem", maxWidth: "72ch" }}>
            Six layers were derived for the district: slope, distance to rivers, drainage density, Topographic
            Wetness Index (TWI), NDVI and flow length. Each was reclassified into five classes from very low (1)
            to very high (5) flood risk, then combined in a weighted overlay where each layer's weight reflects
            its relative importance to flood occurrence. The river network behind the distance analysis was
            extracted using a flow accumulation threshold of more than 35,000 cells.
          </p>
          <div className="tbl-wrap">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Factor</th>
                  <th>Weight</th>
                  <th>Very high risk class</th>
                  <th>Why it raises risk</th>
                </tr>
              </thead>
              <tbody>
                {FACTORS.map((f) => (
                  <tr key={f.name}>
                    <td className="dtable__label">{f.name}</td>
                    <td>{f.weight}%</td>
                    <td>{f.high}</td>
                    <td>{f.why}</td>
                  </tr>
                ))}
                <tr className="dtable__row--total">
                  <td className="dtable__label">Total</td>
                  <td>{FACTORS.reduce((a, f) => a + f.weight, 0)}%</td>
                  <td></td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            Slope carries the largest weight. Steeper slopes, greater distance from rivers, lower drainage
            density, lower wetness, denser vegetation and longer flow paths all score as lower risk.
          </p>
        </div>
      </section>

      {/* ── MAPS: FACTORS ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 1 — Factor Maps: NDVI, Drainage Density, Slope, Flow Length</p>
        <div className="proj-body">
          <MapFrame src={factorsA} alt="Chimanimani flood risk factor maps: NDVI, drainage density, slope and flow length" label="Factor maps" />
          <p className="map-caption">
            <strong>Fig 1</strong> — NDVI, drainage density, slope and flow length for Chimanimani, each
            reclassified to five risk classes from very low (green) to very high (red). Low NDVI and gentle
            slopes cluster across the western half of the district, and short flow lengths ring its western
            and southern edges.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 2 — Factor Maps: TWI and Distance to River</p>
        <div className="proj-body">
          <MapFrame src={factorsB} alt="Chimanimani flood risk factor maps: Topographic Wetness Index and distance to river" label="Factor maps" />
          <p className="map-caption">
            <strong>Fig 2</strong> — Topographic Wetness Index and distance to river. TWI highlights terrain
            that naturally collects water; the distance layer isolates the narrow corridors along the
            district's river channels, derived from the flow accumulation threshold above.
          </p>
        </div>
      </section>

      {/* ── FINAL MAP ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 3 — Flood Risk Zones</p>
        <div className="proj-body">
          <MapFrame src={floodRisk} alt="Chimanimani flood risk map, 2026" label="Flood risk map · 2026" />
          <p className="map-caption">
            <strong>Fig 3</strong> — Final flood risk map from the weighted overlay. High and very high
            risk follow river channels and valley bottoms. Moderate risk dominates the central district, while
            low and very low risk run from the centre towards the east. The western end shows broader zones of
            higher risk than anywhere else.
          </p>
        </div>
      </section>

      {/* ── AREA TABLE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 1 — Area by Flood Risk Class</p>
        <div className="proj-body">
          <div className="tbl-wrap tbl-wrap--narrow">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Risk level</th>
                  <th>Area (ha)</th>
                  <th>Share of district</th>
                </tr>
              </thead>
              <tbody>
                {RISK_CLASSES.map((c, i) => (
                  <tr key={c} className={i >= 3 ? "dtable__row--hl" : ""}>
                    <td>{i + 1}</td>
                    <td className="dtable__label">{c}</td>
                    <td>{f3(AREA_HA[i])}</td>
                    <td>{areaPct[i].toFixed(2)}%</td>
                  </tr>
                ))}
                <tr className="dtable__row--total">
                  <td></td>
                  <td className="dtable__label">Total</td>
                  <td>{f3(TOTAL_HA)}</td>
                  <td>100%</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            About 80,725 ha — {HIGH_AREA.toFixed(1)}% of the district — falls in the high and very high classes
            (highlighted). Low risk is the largest single class at {areaPct[1].toFixed(1)}%.
          </p>
        </div>
      </section>

      {/* ── EXPOSURE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 2 — Buildings by Flood Risk Class</p>
        <div className="proj-body">
          <p className="proj-p" style={{ marginBottom: "1.2rem", maxWidth: "72ch" }}>
            Overlaying OpenStreetMap building footprints on the risk map assessed {f0(TOTAL_BLD)} buildings
            across the district. {HIGH_BLD.toFixed(1)}% of them — {f0(BUILDINGS[3] + BUILDINGS[4])} structures —
            sit in the high and very high classes. Only {bldPct[0].toFixed(1)}% stand on very low risk land,
            even though that class covers {areaPct[0].toFixed(1)}% of the district: safe ground is scarce
            in this mountainous terrain, and settlement is pushed onto hazardous land.
          </p>

          <div className="cmp">
            {RISK_CLASSES.map((c, i) => (
              <div key={c} className="cmp__col">
                <h3 className="cmp__name">{c}</h3>
                <div className="cmp__row">
                  <span>Area</span>
                  <div className="cmp__track"><div className="cmp__bar cmp__bar--area" style={{ width: `${areaPct[i]}%` }} /></div>
                  <span className="cmp__val">{f1(areaPct[i])}%</span>
                </div>
                <div className="cmp__row">
                  <span>Bldgs</span>
                  <div className="cmp__track"><div className="cmp__bar" style={{ width: `${bldPct[i]}%` }} /></div>
                  <span className="cmp__val">{f1(bldPct[i])}%</span>
                </div>
                <p className="cmp__n">{f0(BUILDINGS[i])} buildings</p>
              </div>
            ))}
          </div>

          <div className="tbl-wrap tbl-wrap--narrow">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Score</th>
                  <th>Risk class</th>
                  <th>Buildings</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {[4, 3, 2, 1, 0].map((i) => (
                  <tr key={i} className={i >= 3 ? "dtable__row--hl" : ""}>
                    <td>{i + 1}</td>
                    <td className="dtable__label">{RISK_CLASSES[i]}</td>
                    <td>{f0(BUILDINGS[i])}</td>
                    <td>{bldPct[i].toFixed(1)}%</td>
                  </tr>
                ))}
                <tr className="dtable__row--total">
                  <td></td>
                  <td className="dtable__label">Total</td>
                  <td>{f0(TOTAL_BLD)}</td>
                  <td>100%</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            The largest group, {bldPct[2].toFixed(1)}% of buildings, sits in moderate risk: structures that may
            survive ordinary rains but stay exposed in extreme events such as cyclones.
          </p>
        </div>
      </section>

      {/* ── WHERE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Reading the Map — Where Risk Concentrates</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">The western high-risk belt</h2>
              <p className="proj-p">
                A belt of high to very high risk runs along the western edge of the district, through wards 2,
                3, 4, 5, 8 and 20, stretching from Birchenough Bridge and the Nyanyadzi River towards the
                north-west. Near-flat slopes, low elevation, short flow lengths and low NDVI from cultivation
                combine here. Satellite imagery places communities including Murare, Chakowa, Hotsprings and
                Nenohwe business centre inside it, and Kopa shopping centre in Nyahode (ward 21) remains
                critical given its flood history.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">The eastern highlands</h2>
              <p className="proj-p">
                By contrast the eastern highlands, including wards 1, 7 and 11, fall in the safest classes.
                Higher elevation and rugged terrain shed water away from settlements. Because so little ground
                is genuinely safe, that contrast is the planning problem: the places people can settle most
                safely are the places there is least room to settle.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── LIMITS ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Limitations and Next Steps</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">What the map is</h2>
              <p className="proj-p">
                A susceptibility map: it shows where terrain and land cover make flooding more likely, not
                where water will reach in a given storm. The weights express relative importance and the
                method is consistent with other multi-factor GIS studies in Africa and Asia, including work
                in West Africa reporting 77–81% accuracy.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">What would strengthen it</h2>
              <p className="proj-p">
                Validation against recorded flood events, such as the Idai flood extent or
                community-based verification, and a sensitivity test on the factor weights. Both would show
                how far the classes can be trusted at ward and settlement scale.
              </p>
            </div>
          </div>
        </div>
      </section>

      <GweruCase />

      <footer className="pfooter">
        <span>© 2026 Kudzanai Chakavarika</span>
        <a href="/">spatialforce.co.zw</a>
      </footer>
    </>
  );
}

/* One map per card, framed with breathing room so it is never cropped or over-zoomed. */
function MapFrame({ src, alt, label }: { src?: string; alt: string; label: string }) {
  return (
    <div className="map-card">
      <div className="map-card__head">
        <span className="map-card__year">{label}</span>
      </div>
      <div className="map-frame">
        {src ? (
          <img src={src} alt={alt} className="map-img" />
        ) : (
          <div className="map-ph"><span className="map-ph__note">Map coming soon</span></div>
        )}
      </div>
      <div className="map-card__foot">
        {src ? (
          <a className="map-view" href={src} target="_blank" rel="noopener noreferrer">View full map ↗</a>
        ) : (
          <span className="map-view map-view--disabled">Awaiting upload</span>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   CSS — same design tokens as the LULC page
═══════════════════════════════════════════════════════════════ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;700;800;900&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

:root {
  --paper: #EFEAE0; --paper2: #E4DECE; --ink: #201D18; --night: #191B15;
  --rust: #B1502A; --rust-d: #8C3E20; --brass: #C89B4A; --cream: #F7F3E9;
  --line: rgba(32,29,24,0.13); --linew: rgba(247,243,233,0.13);
  --fd: 'Big Shoulders Display', sans-serif; --fb: 'IBM Plex Sans', sans-serif; --fm: 'IBM Plex Mono', monospace;
}

html, body, #root { width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important; text-align: initial !important; background: var(--night); }
body { font-family: var(--fb); color: var(--ink); overflow-x: hidden; -webkit-font-smoothing: antialiased; }

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.8rem 4vw 1.1rem; text-transform: uppercase; }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

.ptitle { background: var(--night); padding: 6.4rem 4vw 2.2rem; }
.ptitle h1 { font-family: var(--fd); font-weight: 800; text-transform: uppercase; font-size: clamp(1.8rem, 3.6vw, 2.7rem); line-height: 1.06; letter-spacing: -0.01em; color: var(--cream); margin: 0.5rem 0 0.9rem; max-width: 26ch; }
.ptitle__subtitle { font-size: 0.98rem; font-weight: 300; color: rgba(247,243,233,0.62); max-width: 62ch; line-height: 1.6; }

.stat-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background-color: var(--linew); border-top: 3px solid var(--rust); border-bottom: 1px solid var(--linew); }
.stat-strip__item { background: var(--night); padding: 1.6rem 1.4rem; display: flex; flex-direction: column; gap: 0.35rem; }
.stat-strip__value { font-family: var(--fd); font-weight: 800; font-size: clamp(1.4rem, 2.4vw, 2.1rem); color: var(--rust); line-height: 1; }
.stat-strip__label { font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.55); letter-spacing: 0.02em; line-height: 1.4; }

.psection { background: var(--night); padding-bottom: 0.5rem; }
.psection--paper { background: var(--paper); }
.proj-body { padding: 0 4vw 3rem; }
.proj-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2.4rem; }
.proj-h2 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: 1.15rem; color: var(--ink); margin-bottom: 0.7rem; letter-spacing: 0.01em; }
.proj-p { font-size: 0.9rem; line-height: 1.75; color: #4A463C; max-width: 60ch; }

/* map cards: header strip, padded contain-fit window, footer strip; nothing overlays the map */
.map-card { display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 3px; overflow: hidden; background: var(--cream); box-shadow: 0 8px 20px rgba(32,29,24,0.08); max-width: 980px; margin-bottom: 1rem; }
.map-card__head { display: flex; align-items: center; padding: 0.6rem 0.9rem; background: var(--night); }
.map-card__year { font-family: var(--fd); font-weight: 800; font-size: 1rem; letter-spacing: 0.03em; color: var(--cream); text-transform: uppercase; }
.map-frame { background: var(--cream); padding: 1.6rem 1.8rem; display: block; overflow: hidden; }
.map-img { width: 100%; height: auto; max-height: 640px; object-fit: contain; display: block; }
.map-card__foot { display: flex; align-items: center; justify-content: flex-end; padding: 0.6rem 0.9rem; background: var(--paper2); border-top: 1px solid var(--line); }
.map-view { font-family: var(--fm); font-size: 0.62rem; letter-spacing: 0.03em; background: var(--rust); color: var(--cream); text-decoration: none; padding: 0.4rem 0.75rem; border-radius: 2px; text-transform: uppercase; transition: background 0.2s; }
.map-view:hover { background: var(--rust-d); }
.map-view--disabled { background: transparent; color: rgba(140,62,32,0.5); border: 1px dashed rgba(177,80,42,0.4); }
.map-caption { font-size: 0.84rem; line-height: 1.65; color: #4A463C; max-width: 72ch; }
.map-caption strong { color: var(--rust-d); font-family: var(--fm); font-weight: 600; }
.map-ph { height: 320px; display: flex; align-items: center; justify-content: center; border: 1px dashed rgba(177,80,42,0.35); }
.map-ph__note { font-family: var(--fm); font-size: 0.68rem; color: rgba(140,62,32,0.6); text-transform: uppercase; letter-spacing: 0.05em; }

.tbl-wrap { overflow-x: auto; margin-bottom: 1rem; border: 1px solid var(--line); border-radius: 3px; background: var(--cream); }
.tbl-wrap--narrow { max-width: 640px; }
.dtable { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 480px; }
.dtable thead th { font-family: var(--fm); font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.05em; text-align: left; color: var(--cream); background: var(--night); padding: 0.75rem 1rem; }
.dtable tbody td { padding: 0.65rem 1rem; border-top: 1px solid var(--line); color: #3A3630; }
.dtable__label { font-weight: 500; color: var(--ink); }
.dtable__row--hl { background: rgba(177,80,42,0.08); }
.dtable__row--hl .dtable__label { color: var(--rust-d); font-weight: 600; }
.dtable__row--total td { border-top: 2px solid var(--rust); font-weight: 600; color: var(--ink); }
.tbl-note { font-size: 0.78rem; line-height: 1.6; color: #6b665a; max-width: 72ch; }

/* area vs buildings comparison */
.cmp { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1rem; margin-bottom: 1.4rem; }
.cmp__col { background: var(--cream); border: 1px solid var(--line); border-radius: 3px; padding: 0.9rem 1rem 1rem; }
.cmp__name { font-family: var(--fd); font-weight: 800; font-size: 0.95rem; letter-spacing: 0.03em; text-transform: uppercase; color: var(--ink); margin-bottom: 0.3rem; }
.cmp__row { display: grid; grid-template-columns: 2.6rem 1fr 3rem; align-items: center; gap: 0.5rem; margin-top: 0.55rem; font-family: var(--fm); font-size: 0.66rem; color: #3A3630; }
.cmp__track { height: 10px; background: rgba(32,29,24,0.08); border-radius: 2px; overflow: hidden; }
.cmp__bar { height: 100%; background: var(--rust); }
.cmp__bar--area { background: var(--brass); }
.cmp__val { text-align: right; font-weight: 600; color: var(--rust-d); }
.cmp__n { margin-top: 0.7rem; font-family: var(--fm); font-size: 0.64rem; color: #6b665a; }

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

/* -- two-case layout -- */
.case-nav { background: var(--night); display: flex; flex-wrap: wrap; gap: 0.7rem; padding: 0 4vw 2rem; border-bottom: 1px solid var(--linew); }
.case-nav a { font-family: var(--fm); font-size: 0.72rem; letter-spacing: 0.02em; text-decoration: none; color: var(--cream); background: rgba(247,243,233,0.06); border: 1px solid var(--linew); padding: 0.55rem 1rem; border-radius: 999px; transition: background 0.2s, border-color 0.2s; }
.case-nav a:hover { background: rgba(177,80,42,0.18); border-color: var(--rust); }
.case-divider { background: var(--night); padding: 3.4rem 4vw 2.2rem; border-top: 3px solid var(--rust); }
.case-divider h2 { font-family: var(--fd); font-weight: 800; text-transform: uppercase; font-size: clamp(1.5rem, 3vw, 2.15rem); line-height: 1.08; color: var(--cream); margin: 0.5rem 0 0.8rem; max-width: 30ch; }
.case-divider p { font-size: 0.92rem; font-weight: 300; line-height: 1.65; color: rgba(247,243,233,0.6); max-width: 66ch; }
.case-divider + .stat-strip { border-top: 0; }
.dtable__bar { width: 34%; }
.bar { height: 10px; background: rgba(32,29,24,0.08); border-radius: 2px; overflow: hidden; }
.bar__fill { height: 100%; background: var(--rust); }
@media (max-width: 640px) {
  .case-nav { padding: 0 6vw 1.6rem; }
  .case-divider { padding: 2.4rem 6vw 1.8rem; }
}

@media (max-width: 1024px) {
  .proj-grid { grid-template-columns: 1fr; gap: 1.6rem; }
  .stat-strip { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.6rem; }
  .ptitle h1 { font-size: clamp(1.5rem, 6.5vw, 2rem); max-width: none; }
  .section-tag { padding: 1.4rem 6vw 1rem; }
  .proj-body { padding: 0 6vw 2rem; }
  .stat-strip__item { padding: 1.2rem 1rem; }
  .map-frame { padding: 0.8rem; overflow-x: auto; }
  .map-img { width: auto; min-width: 600px; max-width: none; max-height: none; }
  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;

/* ===============================================================
   CASE II - GWERU URBAN: SENTINEL-1 SAR MOISTURE + TERRAIN
   Weighted overlay, five susceptibility classes. Reuses MapFrame and the page CSS above.
=============================================================== */

const SEO_ALL = {
  title: "Flood Susceptibility Mapping in Zimbabwe - Chimanimani and Gweru | Kudzanai Chakavarika",
  description:
    SEO.description +
    " Case II maps Gweru Urban with Sentinel-1 SAR moisture and terrain: 45.1% of the city rated high or very high susceptibility.",
};

const GW_STUDY_HA = 16438;

// NOTE: the source results table lists "7.8" ha for Very low, which is the % value repeated.
// 1,280.1 ha is derived: 16,438 total minus the other four classes (= 7.8% of the area).
const GW_CLASSES = [
  { name: "Very high", pct: 18.7, ha: 3073.9 },
  { name: "High", pct: 26.4, ha: 4340.5 },
  { name: "Moderate", pct: 32.9, ha: 5410.1 },
  { name: "Low", pct: 14.2, ha: 2333.4 },
  { name: "Very low", pct: 7.8, ha: 1280.1 },
];

// Weights exactly as stated in the assignment. They currently add up to 1.5, not 1.0 - confirm before publishing.
const GW_LAYERS = [
  { name: "SAR moisture index", weight: "0.5", role: "Sentinel-1 VH - VV backscatter difference, dry season 2024. Marks ground that holds moisture." },
  { name: "Proximity to rivers", weight: "0.4", role: "Closeness to the Gweru river system and its drainage lines." },
  { name: "Slope", weight: "0.3", role: "Flat ground slows runoff and lets water stand." },
  { name: "Elevation", weight: "0.2", role: "Low-lying ground collects water from higher land." },
  { name: "Land cover", weight: "0.1", role: "ESA WorldCover surface types: vegetation aids infiltration, built surfaces add runoff." },
];

const GW_HIGH_PCT = GW_CLASSES[0].pct + GW_CLASSES[1].pct; // 45.1
const GW_HIGH_HA = GW_CLASSES[0].ha + GW_CLASSES[1].ha; // 7,414.4

const GW_STATS = [
  { value: `${GW_HIGH_PCT.toFixed(1)}%`, label: "Of Gweru Urban rated high or very high flood susceptibility" },
  { value: `${Math.round(GW_HIGH_HA).toLocaleString()} ha`, label: "Of the 16,438 ha study area in those two classes" },
  { value: "5", label: "Weighted layers: SAR moisture, rivers, slope, elevation and land cover" },
  { value: "Dry 2024", label: "Sentinel-1 season used, to map where water naturally persists" },
];

function GweruCase() {
  return (
    <>
      <section className="case-divider" id="case-gweru">
        <span className="p-ref">Case Study II</span>
        <h2>Gweru Urban - Flood Susceptibility from SAR</h2>
        <p>
          Sentinel-1 radar and terrain analysis combined to map how prone each part of Gweru is to
          flooding, as a graded scale rather than a flooded or not-flooded split.
        </p>
      </section>

      <section className="stat-strip">
        {GW_STATS.map((s) => (
          <div key={s.label} className="stat-strip__item">
            <span className="stat-strip__value">{s.value}</span>
            <span className="stat-strip__label">{s.label}</span>
          </div>
        ))}
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Context</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">A city not seen as flood-prone</h2>
              <p className="proj-p">
                Gweru sits on the central plateau, between Harare and Bulawayo, and is often thought of as
                less exposed than Zimbabwe's other cities. Yet low-lying suburbs such as Ascot, Mtapa, Mambo,
                Mkoba and Riverside, and parts of the CBD, have flooded repeatedly, including in the 2020/21
                rainy season (Matsa &amp; Mupepi, 2022). Intense rainfall, blocked stormwater channels and
                settlement growth onto floodplains all feed it, and planning remains mostly reactive.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Why radar</h2>
              <p className="proj-p">
                Ground surveys are slow, costly and patchy. Synthetic Aperture Radar sees through cloud and
                works in any weather, so it can monitor flooding at any time. Many studies still output a
                binary flood map, which hides how moisture varies across a landscape. This case builds a
                graded susceptibility surface for the whole city instead.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Fig 4 &mdash; Gweru Urban Study Area</p>
        <div className="proj-body">
          <MapFrame src={gwStudyArea} alt="Gweru Urban study area with its 18 numbered wards, located within Gweru District and Zimbabwe" label="Gweru Urban" />
          <p className="map-caption">
            <strong>Fig 4</strong> &mdash; Gweru Urban, the Midlands provincial capital, covers about 16,438 ha
            of gently undulating plateau terrain. The map shows its 18 numbered wards, with Gweru District
            and Zimbabwe for location.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Method &mdash; SAR Moisture + Terrain, Weighted Overlay</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Data and processing</h2>
              <p className="proj-p">
                Sentinel-1 radar scenes were processed in the Sentinel Application Platform: orbit file
                correction, thermal noise removal, radiometric calibration, speckle filtering and
                range-Doppler terrain correction. A moisture index was then taken from the VH - VV backscatter
                difference, which responds strongly to surface water while limiting terrain and speckle
                effects. Slope and elevation came from a digital elevation model in QGIS, with class
                thresholds set from the area's own statistics and physiography. Everything was clipped to the
                level-2 administrative boundary for Gweru Urban.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Why the dry season</h2>
              <p className="proj-p">
                Dry-season 2024 imagery was used on purpose. With rainfall interference removed, radar shows
                the ground that holds moisture naturally. That makes the result a map of susceptibility, where
                water tends to collect, rather than of one storm's temporary pooling.
              </p>
            </div>
          </div>

          <p className="section-tag" style={{ padding: "2rem 0 0.9rem" }}>&sect; Table 3 &mdash; Layers and Weights</p>
          <div className="tbl-wrap">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Layer</th>
                  <th>Weight</th>
                  <th>What it captures</th>
                </tr>
              </thead>
              <tbody>
                {GW_LAYERS.map((l) => (
                  <tr key={l.name}>
                    <td className="dtable__label">{l.name}</td>
                    <td>{l.weight}</td>
                    <td>{l.role}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            Layers were combined with a weighted overlay in the QGIS raster calculator, and the result was
            classified into five zones from very low to very high susceptibility.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Fig 5 &mdash; Moisture, Terrain, Combined Susceptibility</p>
        <div className="proj-body">
          <MapFrame src={gwMaps} alt="Three Gweru Urban maps: SAR surface moisture, terrain susceptibility index, and combined flood susceptibility" label="Objective maps" />
          <p className="map-caption">
            <strong>Fig 5</strong> &mdash; Left to right: SAR-derived surface moisture, the terrain susceptibility
            index from slope and elevation, and the combined flood susceptibility map. The first shows where
            water is likely to persist after rainfall, the second how landform steers it, and the third merges
            both with river proximity and land cover.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Table 4 &mdash; Gweru Area by Susceptibility Class</p>
        <div className="proj-body">
          <div className="tbl-wrap tbl-wrap--narrow">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Susceptibility</th>
                  <th>Area (ha)</th>
                  <th>Share</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {GW_CLASSES.map((c, i) => (
                  <tr key={c.name} className={i < 2 ? "dtable__row--hl" : ""}>
                    <td className="dtable__label">{c.name}</td>
                    <td>{c.ha.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</td>
                    <td>{c.pct.toFixed(1)}%</td>
                    <td className="dtable__bar">
                      <div className="bar"><div className="bar__fill" style={{ width: `${(c.pct / 35) * 100}%` }} /></div>
                    </td>
                  </tr>
                ))}
                <tr className="dtable__row--total">
                  <td className="dtable__label">Total</td>
                  <td>{GW_STUDY_HA.toLocaleString(undefined, { minimumFractionDigits: 1 })}</td>
                  <td>100%</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            Moderate is the largest class ({GW_CLASSES[2].pct}%), but high and very high together
            (highlighted) cover {GW_HIGH_PCT.toFixed(1)}%, about {Math.round(GW_HIGH_HA).toLocaleString()} ha.
            Low and very low make up the remaining {(GW_CLASSES[3].pct + GW_CLASSES[4].pct).toFixed(1)}%.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Reading the Gweru Map</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Along the Gweru river</h2>
              <p className="proj-p">
                High and very high susceptibility concentrates in a northwest&ndash;southeast band that follows
                the Gweru river. Low elevation and very gentle slopes weaken runoff and keep water standing
                after heavy rain. Several of these zones coincide with places already known for flooding in
                local reports: Mkoba 6, Mtapa, Riverside, sections of Senga and the CBD. Parts of them also
                return a wet radar signal, pointing to poor drainage, compacted or clay soils, or inadequate
                stormwater systems.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Wetlands and land cover</h2>
              <p className="proj-p">
                Some high-susceptibility zones line up with wetland traces and riparian ground, which should
                act as natural flood buffers. Where settlement has spread beside former wetlands, as in
                parts of Riverside and Mkoba, that storage is reduced and the land carries floodwater instead
                of absorbing it. The calmer end of the map sits on higher, better-drained uplands, where
                woodland and natural cover improve infiltration and the radar response is drier.
              </p>
            </div>
          </div>
          <p className="proj-p" style={{ marginTop: "1.6rem", maxWidth: "72ch" }}>
            Taken together, flood risk in Gweru is not spread evenly. It follows a predictable pattern set by
            topography, hydrology and land-use pressure, which is what makes it plannable: before new
            development, relocation or protective works, the map shows where to look first.
          </p>
        </div>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">&sect; Gweru Limitations and Next Steps</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">How it was checked</h2>
              <p className="proj-p">
                Results were cross-checked against known flood-prone locations, drainage patterns and
                low-lying terrain, and they agree spatially. That is a consistency check, not a quantified
                accuracy test.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">What would strengthen it</h2>
              <p className="proj-p">
                Validation against recorded flood extents from the 2020/21 rains, event-based radar imagery
                alongside the dry-season baseline, and a sensitivity test on the layer weights.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
