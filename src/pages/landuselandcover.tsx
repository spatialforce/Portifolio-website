import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

// Bulawayo map imagery — swap these files in /src/assets/ to update the maps site-wide
import lulc1987 from "../assets/LULC_1987.webp";
import lulc2000 from "../assets/LULC_2000.webp";
import lulc2013 from "../assets/LULC_2013.webp";
import lulc2025 from "../assets/LULC_2025.webp";

const BULAWAYO_MAPS = {
  "1987": lulc1987,
  "2000": lulc2000,
  "2013": lulc2013,
  "2025": lulc2025,
};

// Chiyadzwa / Mutare Ward 30 map imagery
import mutare1995 from "../assets/Mutare_LULC_1995.webp";
import mutare2005 from "../assets/Mutare_LULC_2005.webp";
import mutare2015 from "../assets/Mutare_LULC_2015.webp";
import mutare2025 from "../assets/Mutare_LULC_2025.webp";

const MUTARE_MAPS = {
  "1995": mutare1995,
  "2005": mutare2005,
  "2015": mutare2015,
  "2025": mutare2025,
};

/* ═══════════════════════════════════════════════════════════════
   DATA — BULAWAYO — pulled from the dissertation (Chapter III
   methodology + Chapter IV results).
═══════════════════════════════════════════════════════════════ */

// Table 4.1.0 — Summary of land cover total area, 1987 / 2000 / 2013 / 2025
const BULAWAYO_AREA_TABLE = [
  { cls: "Water",          y1: 210.439,   y2: 227.082,   y3: 241.357,   y4: 189.108 },
  { cls: "Woodland",       y1: 20068.249, y2: 13958.398, y3: 13734.917, y4: 12484.930 },
  { cls: "Grassland",      y1: 12638.904, y2: 19996.680, y3: 16623.833, y4: 14632.967 },
  { cls: "Bare-land",      y1: 110.867,   y2: 279.963,   y3: 216.988,   y4: 300.347 },
  { cls: "Built-up",       y1: 7850.456,  y2: 8249.450,  y3: 8277.169,  y4: 8535.046 },
  { cls: "Dense Vegetation", y1: 6020.591, y2: 4537.787, y3: 4719.211, y4: 4984.152 },
  { cls: "Cultivation",    y1: 6031.894,  y2: 7586.040,  y3: 11021.915, y4: 13708.850, highlight: true },
];

// Table 4.1.2 — Summary of transitions to cultivation, 1987–2025
const TRANSITION_TABLE = [
  { conv: "Stable cultivation",            area: "7 120.00",   pct: "52.31%" },
  { conv: "Grassland → Cultivation",       area: "4 150.00",   pct: "30.49%" },
  { conv: "Woodland → Cultivation",        area: "1 500.00",   pct: "11.02%" },
  { conv: "Dense Vegetation → Cultivation", area: "420.00",    pct: "3.09%" },
  { conv: "Bare-land → Cultivation",       area: "250.00",     pct: "1.84%" },
  { conv: "Built-up → Cultivation",        area: "155.00",     pct: "1.14%" },
  { conv: "Water → Cultivation",           area: "16.646",     pct: "0.12%" },
  { conv: "TOTAL (2025 Area)",             area: "13 611.646", pct: "100.00%", total: true },
];

// Table 4.1.3 — Accuracy assessment
const ACCURACY_TABLE = [
  { metric: "Overall accuracy", y2013: "86.45%", y2025: "88.24%" },
  { metric: "Kappa coefficient", y2013: "0.83",   y2025: "0.86" },
];

// Headline stats for the callout strip
const BULAWAYO_STATS = [
  { value: "11%", label: "Cultivation share of land cover, 1987" },
  { value: "25%", label: "Cultivation share of land cover, 2025" },
  { value: "+13.3%", label: "Net increase in cultivated area, 1987–2025" },
  { value: "38 yrs", label: "Study period spanned by the classification" },
];

/* ═══════════════════════════════════════════════════════════════
   DATA — CHIYADZWA DIAMOND MINE, MUTARE WARD 30
   Sourced from LULC area tabulation (1995 / 2005 / 2015 / 2025),
   Ward 30, Mutare — the ward covering the Chiyadzwa (Marange)
   diamond fields.
═══════════════════════════════════════════════════════════════ */

const MUTARE_AREA_TABLE = [
  { cls: "Water",               y1: 32.622,    y2: 52.570,    y3: 197.625,   y4: 109.518 },
  { cls: "Grassland",           y1: 4031.146,  y2: 1236.786,  y3: 870.494,   y4: 3801.166 },
  { cls: "Cultivation",         y1: 12812.111, y2: 16093.327, y3: 16156.732, y4: 11724.342 },
  { cls: "Riparian Vegetation", y1: 1230.597,  y2: 1153.029,  y3: 1235.379,  y4: 1441.649 },
  { cls: "Woodland",            y1: 22190.572, y2: 21785.728, y3: 21177.292, y4: 19919.497 },
  { cls: "Mine Dump / Bareland", y1: 111.995,  y2: 87.603,    y3: 772.000,   y4: 3413.571, highlight: true },
];

const MUTARE_STATS = [
  { value: "30×", label: "Growth in mine dump / bareland area, 1995–2025" },
  { value: "8.4%", label: "Ward area under mine dump / bareland by 2025" },
  { value: "-2,271 ha", label: "Woodland lost since 1995" },
  { value: "-27%", label: "Cultivation decline since its 2015 peak" },
];

export default function LandUseLandCover() {
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
        <Link to="/projects" className="pnav__back">← All Projects</Link>
      </header>

      {/* ── TITLE ── */}
      <section className="ptitle">
        <span className="p-ref">Project · Land Use & Land Cover</span>
        <h1>Land Use &amp; Land Cover Change</h1>
        <p className="ptitle__subtitle">
          A running set of LULC case studies across Zimbabwe — tracking how cultivation,
          mining and settlement reshape the landscape over decades of satellite record.
        </p>
      </section>

      {/* ── CASE NAV ── */}
      <nav className="case-nav">
        <a href="#case-bulawayo">Case I · Bulawayo Urban Cultivation</a>
        <a href="#case-mutare">Case II · Chiyadzwa Diamond Mine, Mutare Ward 30</a>
      </nav>

      {/* ═══════════════════════════ CASE I — BULAWAYO ═══════════════════════════ */}

      <section className="case-divider" id="case-bulawayo">
        <span className="p-ref">Case Study I</span>
        <h2>Bulawayo — Urban Cultivation Expansion</h2>
        <p>
          A 38-year classification of Bulawayo's land cover, 1987 to 2025, tracking the
          expansion of unregulated urban cultivation into grassland, woodland and
          ecologically sensitive zones.
        </p>
      </section>

      {/* ── STAT STRIP ── */}
      <section className="stat-strip">
        {BULAWAYO_STATS.map((s) => (
          <div key={s.label} className="stat-strip__item">
            <span className="stat-strip__value">{s.value}</span>
            <span className="stat-strip__label">{s.label}</span>
          </div>
        ))}
      </section>

      {/* ── OVERVIEW ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Overview</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Study Area</h2>
              <p className="proj-p">
                Bulawayo lies in south-western Zimbabwe and covers approximately 546 km² of
                semi-arid terrain, spanning high, medium and low-density suburbs, industrial
                zones and open green corridors along streams and wetlands. As of the 2022
                census the city holds close to 666,000 residents, and rising food prices and
                informal livelihoods have driven a steady expansion of unregulated farming
                into these open spaces.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Method</h2>
              <p className="proj-p">
                Land cover was classified for four epochs — 1987, 2000, 2013 and 2025 — using
                Landsat 5 (1987, 2000) and Landsat 8 (2013, 2025) Level-2 Collection 2 imagery,
                processed in Google Earth Engine and the SEPAL platform. Dry-season scenes
                with under 10% cloud cover were mosaicked to minimise vegetation greening
                noise, then supervised-classified into seven land cover classes: water,
                woodland, grassland, bare-land, built-up, dense vegetation, and cultivation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── MAP 1: 1987 STANDALONE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 4.1 — Baseline Classification</p>
        <div className="proj-body">
          <div className="map-solo">
            <MapFrame
              year="1987"
              src={BULAWAYO_MAPS["1987"]}
              alt="Land use land cover map of Bulawayo, 1987"
              solo
            />
            <p className="map-caption">
              <strong>Fig 4.1</strong> — Land use / land cover map for 1987, Bulawayo. This
              baseline predates the urban agriculture policy shifts of 2000 and captures the
              city's land cover prior to major cultivation expansion.
            </p>
          </div>
        </div>
      </section>

      {/* ── MAP 2-4: 2000 / 2013 / 2025 TRIPTYCH ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 4.2 — Post-Policy Change Series</p>
        <div className="proj-body">
          <div className="map-triptych">
            {["2000", "2013", "2025"].map((yr) => (
              <MapFrame
                key={yr}
                year={yr}
                src={BULAWAYO_MAPS[yr]}
                alt={`Land use land cover map of Bulawayo, ${yr}`}
              />
            ))}
          </div>
          <p className="map-caption">
            <strong>Fig 4.2</strong> — Land use / land cover change maps for Bulawayo, 2000 to
            2025. Cultivation grew from 13.8% of total land cover in 2000 to 20.1% in 2013,
            reaching 25% by 2025 — a 6-point jump in the 2000–2013 window alone.
          </p>
        </div>
      </section>

      {/* ── TABLE 4.1.0 ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 4.1.0 — Land Cover Area by Class</p>
        <div className="proj-body">
          <LulcTable
            columns={["1987 (ha)", "2000 (ha)", "2013 (ha)", "2025 (ha)"]}
            rows={BULAWAYO_AREA_TABLE}
          />
          <p className="tbl-note">
            Source: Dissertation Table 4.1.0. Cultivation (highlighted) rose from 6,031.9 ha in
            1987 to 13,708.9 ha in 2025 — more than double — while woodland fell from 20,068.2
            ha to 12,484.9 ha over the same period.
          </p>
        </div>
      </section>

      {/* ── TABLE 4.1.2 ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 4.1.2 — Transitions to Cultivation (1987–2025)</p>
        <div className="proj-body">
          <div className="tbl-wrap">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Class Conversion</th>
                  <th>Area (ha)</th>
                  <th>% of 2025 Cultivation</th>
                </tr>
              </thead>
              <tbody>
                {TRANSITION_TABLE.map((r) => (
                  <tr key={r.conv} className={r.total ? "dtable__row--total" : ""}>
                    <td className="dtable__label">{r.conv}</td>
                    <td>{r.area}</td>
                    <td>{r.pct}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            Source: Dissertation Table 4.1.2. Grassland-to-cultivation conversion accounts for
            the largest share of new farmland (30.49%) after stable cultivation itself; 52% of
            land under cultivation in 1987 remained cultivated in 2025.
          </p>
        </div>
      </section>

      {/* ── TABLE 4.1.3 — ACCURACY ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 4.1.3 — Accuracy Assessment</p>
        <div className="proj-body">
          <div className="tbl-wrap tbl-wrap--narrow">
            <table className="dtable">
              <thead>
                <tr>
                  <th>Assessed Metric</th>
                  <th>2013 Classification</th>
                  <th>2025 Classification</th>
                </tr>
              </thead>
              <tbody>
                {ACCURACY_TABLE.map((r) => (
                  <tr key={r.metric}>
                    <td className="dtable__label">{r.metric}</td>
                    <td>{r.y2013}</td>
                    <td>{r.y2025}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="tbl-note">
            Source: Dissertation Table 4.1.3. Both epochs exceed the 85% overall accuracy
            threshold generally accepted for land cover classification, with 2025 achieving a
            Kappa coefficient of 0.86.
          </p>
        </div>
      </section>

      {/* ═══════════════════════ CASE II — CHIYADZWA / MUTARE WARD 30 ═══════════════════════ */}

      <section className="case-divider" id="case-mutare">
        <span className="p-ref">Case Study II</span>
        <h2>Chiyadzwa Diamond Mine — Mutare Ward 30</h2>
        <p>
          A 30-year classification of Ward 30, Mutare — home to the Chiyadzwa (Marange)
          diamond fields — tracking the conversion of woodland, grassland and cultivated
          land into mine dumps and bare ground as alluvial and formal diamond extraction
          expanded across the ward.
        </p>
      </section>

      {/* ── STAT STRIP ── */}
      <section className="stat-strip">
        {MUTARE_STATS.map((s) => (
          <div key={s.label} className="stat-strip__item">
            <span className="stat-strip__value">{s.value}</span>
            <span className="stat-strip__label">{s.label}</span>
          </div>
        ))}
      </section>

      {/* ── OVERVIEW ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Overview</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Study Area</h2>
              <p className="proj-p">
                Ward 30 sits within Mutare District, Manicaland Province, and covers the
                Chiyadzwa (Marange) diamond fields — one of Zimbabwe's largest alluvial
                diamond deposits, worked informally in the mid-2000s before formal,
                large-scale mining took hold. The ward is otherwise dominated by
                communal woodland, grassland and cultivated land, with riparian
                vegetation lining its drainage lines.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Method</h2>
              <p className="proj-p">
                Land cover was classified for four epochs — 1995, 2005, 2015 and 2025 — into
                six classes: water, grassland, cultivation, riparian vegetation, woodland,
                and mine dump / bareland. The 1995 epoch serves as the pre-mining baseline,
                against which the 2005 (early informal digging), 2015 (peak formal
                operations) and 2025 (current) epochs are compared.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── MAP 1: 1995 STANDALONE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 5.1 — Baseline Classification</p>
        <div className="proj-body">
          <div className="map-solo">
            <MapFrame
              year="1995"
              src={MUTARE_MAPS["1995"]}
              alt="Land use land cover map of Mutare Ward 30, 1995"
              solo
            />
            <p className="map-caption">
              <strong>Fig 5.1</strong> — Land use / land cover map for 1995, Mutare Ward 30.
              This baseline predates informal diamond digging in Chiyadzwa and captures the
              ward's land cover as almost entirely woodland and cultivation.
            </p>
          </div>
        </div>
      </section>

      {/* ── MAP 2-4: 2005 / 2015 / 2025 TRIPTYCH ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Fig 5.2 — Mining Expansion Series</p>
        <div className="proj-body">
          <div className="map-triptych">
            {["2005", "2015", "2025"].map((yr) => (
              <MapFrame
                key={yr}
                year={yr}
                src={MUTARE_MAPS[yr]}
                alt={`Land use land cover map of Mutare Ward 30, ${yr}`}
              />
            ))}
          </div>
          <p className="map-caption">
            <strong>Fig 5.2</strong> — Land use / land cover change maps for Mutare Ward 30,
            2005 to 2025. Mine dump / bareland cover was negligible through 2005, then grew
            nearly 9-fold between 2005 and 2015 as formal extraction scaled up, and more than
            4-fold again between 2015 and 2025.
          </p>
        </div>
      </section>

      {/* ── AREA TABLE ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Table 5.1 — Land Cover Area by Class</p>
        <div className="proj-body">
          <LulcTable
            columns={["1995 (ha)", "2005 (ha)", "2015 (ha)", "2025 (ha)"]}
            rows={MUTARE_AREA_TABLE}
          />
          <p className="tbl-note">
            Mine dump / bareland (highlighted) grew from 111.995 ha in 1995 to 3,413.571 ha in
            2025 — roughly a 30-fold increase — while woodland fell from 22,190.6 ha to
            19,919.5 ha. Cultivation rose steadily through 2015 before contracting by 2025,
            likely reflecting land taken up by mining and associated resettlement.
          </p>
        </div>
      </section>

      {/* ── READING THE TREND ── */}
      <section className="psection psection--paper">
        <p className="section-tag">§ Reading the Trend</p>
        <div className="proj-body">
          <div className="proj-grid">
            <div>
              <h2 className="proj-h2">Mine Dump Expansion</h2>
              <p className="proj-p">
                Mine dump / bareland cover was marginal through 2005 (0.28% → 0.22% of the
                ward), then accelerated sharply — reaching 1.9% by 2015 and 8.4% by 2025 as
                formal diamond mining operations scaled up across Chiyadzwa. The bulk of this
                growth occurred in the most recent decade.
              </p>
            </div>
            <div>
              <h2 className="proj-h2">Cultivation Reversal</h2>
              <p className="proj-p">
                Cultivation expanded from 31.7% of the ward in 1995 to a peak of exactly 40.0%
                in 2015, then dropped to 29.0% by 2025 — a loss of roughly 4,432 ha from its
                peak, consistent with farmland being displaced by mine dumps, tailings and
                associated infrastructure.
              </p>
            </div>
          </div>
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
   MapFrame — shared map display block for both case studies.
   Renders the real image with a "View full map" link when a src
   is supplied, otherwise falls back to a placeholder panel.
═══════════════════════════════════════════════════════════════ */
function MapFrame({ year, src, alt, solo }) {
  return (
    <div className={`map-card${solo ? " map-card--solo" : ""}`}>
      <div className="map-card__head">
        <span className="map-card__year">{year}</span>
      </div>

      <div className="map-frame">
        {src ? (
          <img src={src} alt={alt} className="map-img" />
        ) : (
          <div className="map-ph">
            <span className="map-ph__note">Map coming soon</span>
          </div>
        )}
      </div>

      <div className="map-card__foot">
        {src ? (
          <a
            className="map-view"
            href={src}
            target="_blank"
            rel="noopener noreferrer"
          >
            View full map ↗
          </a>
        ) : (
          <span className="map-view map-view--disabled">Awaiting upload</span>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   LulcTable — shared land-cover-by-class table renderer.
═══════════════════════════════════════════════════════════════ */
function LulcTable({ columns, rows }) {
  return (
    <div className="tbl-wrap">
      <table className="dtable">
        <thead>
          <tr>
            <th>LULC Class</th>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.cls} className={r.highlight ? "dtable__row--hl" : ""}>
              <td className="dtable__label">{r.cls}</td>
              <td>{r.y1.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td>{r.y2.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td>{r.y3.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td>{r.y4.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
   CSS
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

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.8rem 4vw 1.1rem; text-transform: uppercase; }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

/* ── NAV ── */
.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

/* ── TITLE ── */
.ptitle { background: var(--night); padding: 6.4rem 4vw 2rem; }
.ptitle h1 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.8rem, 3.6vw, 2.7rem); line-height: 1.06; letter-spacing: -0.01em;
  color: var(--cream); margin: 0.5rem 0 0.9rem; max-width: 26ch;
}
.ptitle__subtitle { font-size: 0.98rem; font-weight: 300; color: rgba(247,243,233,0.62); max-width: 62ch; line-height: 1.6; }

/* ── CASE NAV ── */
.case-nav {
  background: var(--night); display: flex; flex-wrap: wrap; gap: 0.7rem;
  padding: 0 4vw 2rem; border-bottom: 1px solid var(--linew);
}
.case-nav a {
  font-family: var(--fm); font-size: 0.72rem; letter-spacing: 0.02em; text-decoration: none;
  color: var(--cream); background: rgba(247,243,233,0.06); border: 1px solid var(--linew);
  padding: 0.55rem 1rem; border-radius: 999px; transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.case-nav a:hover { background: rgba(177,80,42,0.18); border-color: var(--rust); color: var(--cream); }

/* ── CASE DIVIDER ── */
.case-divider {
  background: var(--night); padding: 3.4rem 4vw 2.2rem; border-top: 3px solid var(--rust);
}
.case-divider h2 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.5rem, 3vw, 2.15rem); line-height: 1.08; color: var(--cream);
  margin: 0.5rem 0 0.8rem; max-width: 30ch;
}
.case-divider p { font-size: 0.92rem; font-weight: 300; line-height: 1.65; color: rgba(247,243,233,0.6); max-width: 66ch; }

/* ── STAT STRIP ── */
.stat-strip {
  background: var(--night); display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1px; background-color: var(--linew); border-bottom: 1px solid var(--linew);
}
.stat-strip__item { background: var(--night); padding: 1.6rem 1.4rem; display: flex; flex-direction: column; gap: 0.35rem; }
.stat-strip__value { font-family: var(--fd); font-weight: 800; font-size: clamp(1.4rem, 2.4vw, 2.1rem); color: var(--rust); line-height: 1; }
.stat-strip__label { font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.55); letter-spacing: 0.02em; line-height: 1.4; }

/* ── SECTIONS ── */
.psection { background: var(--night); padding-bottom: 0.5rem; }
.psection--paper { background: var(--paper); }
.psection--paper .section-tag { color: var(--rust); }
.proj-body { padding: 0 4vw 3rem; }

.proj-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2.4rem; }
.proj-h2 { font-family: var(--fd); font-weight: 700; text-transform: uppercase; font-size: 1.15rem; color: var(--ink); margin-bottom: 0.7rem; letter-spacing: 0.01em; }
.proj-p { font-size: 0.9rem; line-height: 1.75; color: #4A463C; max-width: 56ch; }

/* ── MAP CARDS — year sits in its own header strip, the map fills a
   fixed-height contain-fit window in the middle, and "View full map"
   sits in its own footer strip. Nothing is ever overlaid on top of
   the map image itself, so labels never collide with map content. ── */
.map-solo { display: flex; flex-direction: column; gap: 1rem; }
.map-card {
  display: flex; flex-direction: column; border: 1px solid var(--line); border-radius: 3px;
  overflow: hidden; background: var(--cream); box-shadow: 0 8px 20px rgba(32,29,24,0.08);
}
.map-card--solo { max-width: 640px; }
.map-card__head {
  display: flex; align-items: center; padding: 0.6rem 0.9rem; background: var(--night);
}
.map-card__year {
  font-family: var(--fd); font-weight: 800; font-size: 1rem; letter-spacing: 0.03em;
  color: var(--cream); text-transform: uppercase;
}
.map-frame {
  position: relative; background: var(--cream); overflow: hidden;
  display: flex; align-items: center; justify-content: center; height: 400px;
}
/* Solo maps (e.g. the single baseline year) hug the image's own aspect
   ratio instead of being forced into a fixed box — this is what stops
   empty side gaps from appearing when the map is wider than it is tall. */
.map-card--solo .map-frame {
  height: auto; display: block;
}
.map-card--solo .map-img {
  width: 100%; height: auto; max-height: none;
}
.map-triptych { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin-bottom: 1rem; align-items: start; }
.map-img { max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; display: block; }
.map-card__foot {
  display: flex; align-items: center; justify-content: flex-end; padding: 0.6rem 0.9rem;
  background: var(--paper2); border-top: 1px solid var(--line);
}
.map-view {
  font-family: var(--fm); font-size: 0.62rem; letter-spacing: 0.03em; background: var(--rust);
  color: var(--cream); text-decoration: none; padding: 0.4rem 0.75rem; border-radius: 2px;
  text-transform: uppercase; transition: background 0.2s;
}
.map-view:hover { background: var(--rust-d); }
.map-view--disabled { background: transparent; color: rgba(140,62,32,0.5); border: 1px dashed rgba(177,80,42,0.4); }
.map-caption { font-size: 0.84rem; line-height: 1.65; color: #4A463C; max-width: 72ch; }
.map-caption strong { color: var(--rust-d); font-family: var(--fm); font-weight: 600; }

/* ── MAP PLACEHOLDER (used until real imagery is supplied) ── */
.map-ph {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background:
    repeating-linear-gradient(45deg, rgba(177,80,42,0.06) 0, rgba(177,80,42,0.06) 2px, transparent 2px, transparent 14px),
    var(--cream);
  border: 1px dashed rgba(177,80,42,0.35);
}
.map-ph__note { font-family: var(--fm); font-size: 0.68rem; color: rgba(140,62,32,0.6); text-transform: uppercase; letter-spacing: 0.05em; }

/* ── TABLES ── */
.tbl-wrap { overflow-x: auto; margin-bottom: 1rem; border: 1px solid var(--line); border-radius: 3px; background: var(--cream); }
.tbl-wrap--narrow { max-width: 640px; }
.dtable { width: 100%; border-collapse: collapse; font-size: 0.85rem; min-width: 480px; }
.dtable thead th {
  font-family: var(--fm); font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.05em;
  text-align: left; color: var(--cream); background: var(--night); padding: 0.75rem 1rem;
}
.dtable thead th:first-child { border-top-left-radius: 2px; }
.dtable tbody td { padding: 0.65rem 1rem; border-top: 1px solid var(--line); color: #3A3630; }
.dtable__label { font-weight: 500; color: var(--ink); }
.dtable__row--hl { background: rgba(177,80,42,0.08); }
.dtable__row--hl .dtable__label { color: var(--rust-d); font-weight: 600; }
.dtable__row--total td { border-top: 2px solid var(--rust); font-weight: 600; color: var(--ink); }
.tbl-note { font-size: 0.78rem; line-height: 1.6; color: #6b665a; max-width: 72ch; }

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

/* ══════════════════ TABLET ≤ 1024px ══════════════════ */
@media (max-width: 1024px) {
  .proj-grid { grid-template-columns: 1fr; gap: 1.6rem; }
  .stat-strip { grid-template-columns: repeat(2, 1fr); }
  .map-frame { height: 320px; }
}

/* ══════════════════ MOBILE ≤ 640px ══════════════════ */
@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.6rem; }
  .ptitle h1 { font-size: clamp(1.5rem, 6.5vw, 2rem); max-width: none; }
  .case-nav { padding: 0 6vw 1.6rem; }
  .case-divider { padding: 2.4rem 6vw 1.8rem; }
  .section-tag { padding: 1.4rem 6vw 1rem; }
  .proj-body { padding: 0 6vw 2rem; }
  .stat-strip { grid-template-columns: repeat(2, 1fr); }
  .stat-strip__item { padding: 1.2rem 1rem; }
  .map-triptych { grid-template-columns: 1fr; }
  .map-frame { height: 280px; }
  .map-card--solo { max-width: none; }
  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;
