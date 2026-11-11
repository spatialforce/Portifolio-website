import { useEffect } from "react";
import SiteNav, { SiteFooter } from "./SiteChrome";
import "./page.css";
import { Figure, Stats, ProjectContact } from "./parts";

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

// Bulawayo suburbs (Case III) - each image is ONE layout holding the 1990 / 2008 / 2025 maps side by side.
// Rename these files to match yours, or edit the three paths below.
import cowdrayMap from "../assets/cowdray_park.webp";
import mahatshulaMap from "../assets/Mahatshula.webp";
import richmondMap from "../assets/richmond.webp";

const SUBURB_MAPS = {
  cowdray: cowdrayMap,
  mahatshula: mahatshulaMap,
  richmond: richmondMap,
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
  { cls: "Bare land",      y1: 110.867,   y2: 279.963,   y3: 216.988,   y4: 300.347 },
  { cls: "Built up",       y1: 7850.456,  y2: 8249.450,  y3: 8277.169,  y4: 8535.046 },
  { cls: "Dense vegetation", y1: 6020.591, y2: 4537.787, y3: 4719.211, y4: 4984.152 },
  { cls: "Cultivation",    y1: 6031.894,  y2: 7586.040,  y3: 11021.915, y4: 13708.850, highlight: true },
];

// Table 4.1.2 — Summary of transitions to cultivation, 1987–2025
const TRANSITION_TABLE = [
  { conv: "Stayed cultivated",            area: "7 120.00",   pct: "52.31%" },
  { conv: "Grassland to cultivation",       area: "4 150.00",   pct: "30.49%" },
  { conv: "Woodland to cultivation",        area: "1 500.00",   pct: "11.02%" },
  { conv: "Dense vegetation to cultivation", area: "420.00",    pct: "3.09%" },
  { conv: "Bare land to cultivation",       area: "250.00",     pct: "1.84%" },
  { conv: "Built up to cultivation",        area: "155.00",     pct: "1.14%" },
  { conv: "Water to cultivation",           area: "16.646",     pct: "0.12%" },
  { conv: "Total (2025 area)",             area: "13 611.646", pct: "100.00%", total: true },
];

// Table 4.1.3 — Accuracy assessment
const ACCURACY_TABLE = [
  { metric: "Overall accuracy", y2013: "86.45%", y2025: "88.24%" },
  { metric: "Kappa coefficient", y2013: "0.83",   y2025: "0.86" },
];

// Headline stats for the callout strip
const BULAWAYO_STATS = [
  { value: "11%", label: "Share of the city under cultivation in 1987" },
  { value: "25%", label: "Share under cultivation in 2025" },
  { value: "+13.3%", label: "Net rise in cultivated area since 1987" },
  { value: "38 years", label: "Of satellite record in the study" },
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
  { cls: "Riparian vegetation", y1: 1230.597,  y2: 1153.029,  y3: 1235.379,  y4: 1441.649 },
  { cls: "Woodland",            y1: 22190.572, y2: 21785.728, y3: 21177.292, y4: 19919.497 },
  { cls: "Mine dumps and bare ground", y1: 111.995,  y2: 87.603,    y3: 772.000,   y4: 3413.571, highlight: true },
];

const MUTARE_STATS = [
  { value: "30×", label: "Growth in mine dumps and bare ground since 1995" },
  { value: "8.4%", label: "Of the ward under mine dumps and bare ground in 2025" },
  { value: "2,271 ha", label: "Of woodland lost since 1995" },
  { value: "27%", label: "Drop in cultivation since its 2015 peak" },
];

/* ═══════════════════════════════════════════════════════════════
   SEO — canonical URL, meta description, Open Graph / Twitter Card
   data, and the JSON-LD payload used further down. Kept as plain
   constants so page copy only needs updating in one place.
═══════════════════════════════════════════════════════════════ */
const SITE_URL = "https://spatialforce.co.zw";
const PAGE_PATH = "/projects/land-use-land-cover";
const AUTHOR_NAME = "Kudzanai Chakavarika";

const SEO = {
  title: "Land Use and Land Cover Change in Bulawayo and Mutare | Kudzanai Chakavarika",
  description:
    "Land use and land cover change from satellite imagery: 38 years of urban farming in Bulawayo, 30 years of diamond mining at Chiyadzwa in Mutare and three Bulawayo suburbs from 1990 to 2025. By GIS and remote sensing analyst Kudzanai Chakavarika.",
  keywords:
    "land use land cover change Zimbabwe, LULC Bulawayo, Chiyadzwa diamond mine, Marange diamond fields, Mutare Ward 30 land cover, remote sensing Zimbabwe, Landsat classification Zimbabwe, urban agriculture Bulawayo, mine dump mapping, SEPAL Google Earth Engine, Cowdray Park, Mahatshula, Richmond, Bulawayo suburbs land cover, Kudzanai Chakavarika",
  canonical: `${SITE_URL}${PAGE_PATH}`,
  image: `${SITE_URL}/assets/LULC_2025.webp`,
};

export default function LandUseLandCover() {


  /* ── SEO: head tags ──
     Sets <title>, meta description/keywords/author, canonical link,
     Open Graph and Twitter Card tags, and robots directive. Each
     tag is created once and cleaned up on unmount so navigating to
     another route doesn't leave stale tags behind for the next page. */
  useEffect(() => {
    const prevTitle = document.title;
    document.title = SEO.title;

    const created: HTMLElement[] = [];

    const upsertMeta = (attr: "name" | "property", key: string, content: string) => {
      let tag = document.querySelector<HTMLMetaElement>(`meta[${attr}="${key}"]`);
      if (!tag) {
        tag = document.createElement("meta");
        tag.setAttribute(attr, key);
        document.head.appendChild(tag);
        created.push(tag);
      }
      tag.setAttribute("content", content);
    };

    upsertMeta("name", "description", SEO.description);
    upsertMeta("name", "keywords", SEO.keywords);
    upsertMeta("name", "author", AUTHOR_NAME);
    upsertMeta("name", "robots", "index, follow");

    // Open Graph
    upsertMeta("property", "og:type", "article");
    upsertMeta("property", "og:title", SEO.title);
    upsertMeta("property", "og:description", SEO.description);
    upsertMeta("property", "og:url", SEO.canonical);
    upsertMeta("property", "og:image", SEO.image);
    upsertMeta("property", "og:site_name", "KC/Spatial");

    // Twitter Card
    upsertMeta("name", "twitter:card", "summary_large_image");
    upsertMeta("name", "twitter:title", SEO.title);
    upsertMeta("name", "twitter:description", SEO.description);
    upsertMeta("name", "twitter:image", SEO.image);

    // Canonical link
    let canonical = document.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.setAttribute("rel", "canonical");
      document.head.appendChild(canonical);
      created.push(canonical);
    }
    canonical.setAttribute("href", SEO.canonical);

    // JSON-LD structured data — Article covering both case studies,
    // with each case study modelled as a Dataset, plus author + breadcrumb.
    const jsonLd = {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: "Land Use & Land Cover Change in Zimbabwe: Bulawayo & Chiyadzwa Diamond Mine, Mutare",
      description: SEO.description,
      url: SEO.canonical,
      inLanguage: "en",
      author: {
        "@type": "Person",
        name: AUTHOR_NAME,
      },
      about: [
        {
          "@type": "Dataset",
          name: "Bulawayo Land Use & Land Cover, 1987–2025",
          description:
            "Land cover classification of Bulawayo across four epochs (1987, 2000, 2013, 2025) tracking urban cultivation expansion.",
          temporalCoverage: "1987/2025",
          spatialCoverage: "Bulawayo, Zimbabwe",
        },
        {
          "@type": "Dataset",
          name: "Chiyadzwa Diamond Mine, Mutare Ward 30 Land Use & Land Cover, 1995–2025",
          description:
            "Land cover classification of Mutare Ward 30 across four epochs (1995, 2005, 2015, 2025) tracking diamond mining expansion at Chiyadzwa (Marange).",
          temporalCoverage: "1995/2025",
          spatialCoverage: "Mutare Ward 30, Manicaland, Zimbabwe",
        },
        {
          "@type": "Dataset",
          name: "Bulawayo Suburbs Land Use & Land Cover, 1990-2025",
          description:
            "Three-class land cover classification (woodland, grassland, built-up) of Cowdray Park, Mahatshula and Richmond, Bulawayo, across three epochs (1990, 2008, 2025) tracking built-up expansion.",
          temporalCoverage: "1990/2025",
          spatialCoverage: "Cowdray Park, Mahatshula and Richmond, Bulawayo, Zimbabwe",
        },
      ],
      breadcrumb: {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Projects", item: `${SITE_URL}/projects` },
          { "@type": "ListItem", position: 3, name: "Land Use & Land Cover", item: SEO.canonical },
        ],
      },
    };

    const ldScript = document.createElement("script");
    ldScript.type = "application/ld+json";
    ldScript.text = JSON.stringify(jsonLd);
    document.head.appendChild(ldScript);
    created.push(ldScript);

    return () => {
      document.title = prevTitle;
      created.forEach((el) => el.parentNode?.removeChild(el));
    };
  }, []);

  return (
    <>
      <SiteNav />

      <section className="ptitle">
        <h1>Land use and land cover change</h1>
        <p className="ptitle__subtitle">
          Three case studies from Zimbabwe. Decades of satellite imagery show how farming and mining and
          housing have reshaped the land.
        </p>
      </section>

      <nav className="case-nav" aria-label="Case studies">
        <b>On this page</b>
        <a href="#case-bulawayo">Urban farming in Bulawayo</a>
        <a href="#case-mutare">Chiyadzwa diamond fields</a>
        <a href="#case-suburbs">Three Bulawayo suburbs</a>
      </nav>

      {/* Case I: Bulawayo */}
      <section className="case-divider" id="case-bulawayo">
        <h2>Urban farming in Bulawayo</h2>
        <p>
          Bulawayo's land cover mapped four times between 1987 and 2025. Unregulated farming spread into
          grassland and woodland and sensitive wetlands.
        </p>
      </section>

      <Stats items={BULAWAYO_STATS} />

      <section className="psection">
        <div className="proj-grid">
          <div>
            <h3 className="proj-h2">Study area</h3>
            <p className="proj-p">
              Bulawayo lies in the southwest of Zimbabwe and covers about 546 km² of semi arid land. It
              takes in high, medium and low density suburbs, industrial areas and open green strips along
              streams and wetlands. The 2022 census counted close to 666,000 residents. Rising food prices
              and informal work have pushed more and more farming into those open spaces.
            </p>
          </div>
          <div>
            <h3 className="proj-h2">Method</h3>
            <p className="proj-p">
              I classified land cover for 1987, 2000, 2013 and 2025 using Landsat 5 for the first two years
              and Landsat 8 for the last two (Level 2, Collection 2). Processing ran in Google Earth Engine
              and SEPAL. I used dry season scenes with less than 10% cloud so that seasonal greening would
              not blur the classes. Each mosaic was sorted into seven classes: water, woodland, grassland,
              bare land, built up, dense vegetation and cultivation.
            </p>
          </div>
        </div>
      </section>

      <section className="psection">
        <h3 className="sec-h">The 1987 baseline</h3>
        <div className="fig-solo">
          <Figure src={BULAWAYO_MAPS["1987"]} alt="Land use land cover map of Bulawayo, 1987" name="Figure 1.">
            Land cover in Bulawayo in 1987. This is before the urban agriculture policy changes of 2000
            and before farming started to spread.
          </Figure>
        </div>
      </section>

      <section className="psection">
        <h3 className="sec-h">2000, 2013 and 2025</h3>
        <div className="fig-three">
          {(["2000", "2013", "2025"] as const).map((yr) => (
            <Figure key={yr} src={BULAWAYO_MAPS[yr]} alt={`Land use land cover map of Bulawayo, ${yr}`} name={yr} />
          ))}
        </div>
        <p className="map-caption">
          <b>Figure 2.</b> Land cover in Bulawayo from 2000 to 2025. Cultivation grew from 13.8% of the
          city in 2000 to 20.1% in 2013 and 25% by 2025. The biggest jump came between 2000 and 2013.
        </p>
      </section>

      <section className="psection">
        <h3 className="sec-h">Area of each class</h3>
        <LulcTable columns={["1987 (ha)", "2000 (ha)", "2013 (ha)", "2025 (ha)"]} rows={BULAWAYO_AREA_TABLE} />
        <p className="tbl-note">
          Cultivation (shaded) more than doubled from 6,031.9 ha in 1987 to 13,708.9 ha in 2025. Over the
          same years woodland fell from 20,068.2 ha to 12,484.9 ha.
        </p>
      </section>

      <section className="psection">
        <h3 className="sec-h">Where the new farmland came from</h3>
        <div className="tbl-wrap">
          <table className="dtable">
            <thead>
              <tr>
                <th>Change from 1987 to 2025</th>
                <th>Area (ha)</th>
                <th>Share of 2025 farmland</th>
              </tr>
            </thead>
            <tbody>
              {TRANSITION_TABLE.map((r) => (
                <tr key={r.conv} className={r.total ? "dtable__row--total" : ""}>
                  <td className="dtable__label">{r.conv}</td>
                  <td className="dtable__num">{r.area}</td>
                  <td>{r.pct}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="tbl-note">
          About half of the land farmed in 2025 was already farmed in 1987. Most of the rest was grassland,
          which accounts for 30.5% of today's farmland.
        </p>
      </section>

      <section className="psection">
        <h3 className="sec-h">Accuracy</h3>
        <div className="tbl-wrap tbl-wrap--narrow">
          <table className="dtable">
            <thead>
              <tr>
                <th>Measure</th>
                <th>2013</th>
                <th>2025</th>
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
          Both years pass the 85% overall accuracy usually expected for land cover maps. The 2025 map has
          a Kappa of 0.86.
        </p>
      </section>

      {/* Case II: Chiyadzwa, Mutare Ward 30 */}
      <section className="case-divider" id="case-mutare">
        <h2>Chiyadzwa diamond fields in Mutare</h2>
        <p>
          Ward 30 in Mutare holds the Chiyadzwa (Marange) diamond fields. Mapped four times over 30 years
          it shows woodland and farmland giving way to mine dumps and bare ground.
        </p>
      </section>

      <Stats items={MUTARE_STATS} />

      <section className="psection">
        <div className="proj-grid">
          <div>
            <h3 className="proj-h2">Study area</h3>
            <p className="proj-p">
              Ward 30 is in Mutare District, Manicaland. Its diamond fields are among the largest alluvial
              deposits in Zimbabwe. They were dug informally in the mid 2000s before large formal mines took
              over. Outside the fields the ward is mostly communal woodland, grassland and farmland, with
              riparian vegetation along its streams.
            </p>
          </div>
          <div>
            <h3 className="proj-h2">Method</h3>
            <p className="proj-p">
              I classified land cover for 1995, 2005, 2015 and 2025 into six classes: water, grassland,
              cultivation, riparian vegetation, woodland and mine dumps with bare ground. 1995 is the
              baseline before mining. 2005 shows the early informal digging, 2015 the height of formal
              mining and 2025 the situation today.
            </p>
          </div>
        </div>
      </section>

      <section className="psection">
        <h3 className="sec-h">The 1995 baseline</h3>
        <div className="fig-solo">
          <Figure src={MUTARE_MAPS["1995"]} alt="Land use land cover map of Mutare Ward 30, 1995" name="Figure 3.">
            Land cover in Ward 30 in 1995, before informal diamond digging began. The ward is almost all
            woodland and farmland.
          </Figure>
        </div>
      </section>

      <section className="psection">
        <h3 className="sec-h">2005, 2015 and 2025</h3>
        <div className="fig-three">
          {(["2005", "2015", "2025"] as const).map((yr) => (
            <Figure key={yr} src={MUTARE_MAPS[yr]} alt={`Land use land cover map of Mutare Ward 30, ${yr}`} name={yr} />
          ))}
        </div>
        <p className="map-caption">
          <b>Figure 4.</b> Land cover in Ward 30 from 2005 to 2025. Mine dumps and bare ground barely show
          in 2005. They grew almost ninefold by 2015 as formal mining scaled up, then more than fourfold
          again by 2025.
        </p>
      </section>

      <section className="psection">
        <h3 className="sec-h">Area of each class</h3>
        <LulcTable columns={["1995 (ha)", "2005 (ha)", "2015 (ha)", "2025 (ha)"]} rows={MUTARE_AREA_TABLE} />
        <p className="tbl-note">
          Mine dumps and bare ground (shaded) grew about thirtyfold from 112.0 ha in 1995 to 3,413.6 ha in
          2025. Woodland fell from 22,190.6 ha to 19,919.5 ha. Cultivation rose until 2015 and then
          shrank, most likely because mining and resettlement took over farmland.
        </p>
      </section>

      <section className="psection">
        <h3 className="sec-h">What the numbers show</h3>
        <div className="proj-grid">
          <div>
            <h3 className="proj-h2">Mine dumps spread fast</h3>
            <p className="proj-p">
              Mine dumps and bare ground covered only 0.28% of the ward in 1995 and 0.22% in 2005. Then they
              took off, reaching 1.9% by 2015 and 8.4% by 2025 as formal mining spread across Chiyadzwa.
              Most of that growth happened in the last ten years.
            </p>
          </div>
          <div>
            <h3 className="proj-h2">Farming went up, then down</h3>
            <p className="proj-p">
              Cultivation grew from 31.7% of the ward in 1995 to a peak of 40.0% in 2015. By 2025 it had
              dropped to 29.0%, a loss of about 4,432 ha. That fits with farmland being taken over by mine
              dumps, tailings and mine infrastructure.
            </p>
          </div>
        </div>
      </section>

      <SuburbCase />

      <ProjectContact>
        If you need the full classification data or a similar study for your area, send me an email.
      </ProjectContact>

      <SiteFooter />
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════
   LulcTable — shared land-cover-by-class table renderer.
═══════════════════════════════════════════════════════════════ */
type LulcRow = {
  cls: string;
  y1: number;
  y2: number;
  y3: number;
  y4: number;
  highlight?: boolean;
};

type LulcTableProps = {
  columns: string[];
  rows: LulcRow[];
};

function LulcTable({ columns, rows }: LulcTableProps) {
  return (
    <div className="tbl-wrap">
      <table className="dtable">
        <thead>
          <tr>
            <th>Class</th>
            {columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.cls} className={r.highlight ? "dtable__row--hl" : ""}>
              <td className="dtable__label">{r.cls}</td>
              <td className="dtable__num">{r.y1.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td className="dtable__num">{r.y2.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td className="dtable__num">{r.y3.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
              <td className="dtable__num">{r.y4.toLocaleString(undefined, { minimumFractionDigits: 3 })}</td>
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

/* ═══════════════════════════════════════════════════════════════
   CASE III — BULAWAYO SUBURBS: COWDRAY PARK / MAHATSHULA / RICHMOND
   Three-class LULC (woodland / grassland / built-up), 1990 / 2008 / 2025.
   ha = area in hectares, pct = share of the suburb's mapped area.
═══════════════════════════════════════════════════════════════ */

type SuburbRow = { cls: string; ha: number[]; pct: number[]; highlight?: boolean };

type Suburb = {
  id: string;
  name: string;
  src?: string;
  alt: string;
  fig: string;
  tbl: string;
  caption: string;
  reading: string;
  note: string;
  rows: SuburbRow[];
};

const SUBURB_EPOCHS = ["1990", "2008", "2025"];

const SUBURB_STATS = [
  { value: "4.5×", label: "Growth in built up area across the three suburbs since 1990" },
  { value: "52%", label: "Of the three suburbs built up by 2025, up from 11.7% in 1990" },
  { value: "16×", label: "Growth in built up area in Mahatshula, the fastest of the three" },
  { value: "793 ha", label: "Of grassland lost across the three suburbs since 1990" },
];

const SUBURBS: Suburb[] = [
  {
    id: "cowdray-park",
    name: "Cowdray Park",
    src: SUBURB_MAPS.cowdray,
    alt: "Land use land cover maps of Cowdray Park, 1990, 2008 and 2025",
    fig: "Fig 6.1",
    tbl: "Table 6.1",
    caption:
      "Land cover in Cowdray Park in 1990, 2008 and 2025.",
    reading:
      "Cowdray Park is the largest of the three at about 1,593 ha and has seen the most land converted. Built up land grew almost fourfold from 226.5 ha (14.2%) to 890.5 ha (55.9%). It overtook grassland as the main class between 1990 and 2008. Building was fastest in those first 18 years at about 26.7 ha a year. After 2008 it slowed to about 10.8 ha a year as open land ran out. Grassland fell by 468.9 ha and woodland by 195.1 ha, so both roughly halved.",
    note: "The mapped area is 1,593.36 ha in all three years. Built up land (shaded) is the only class that grew.",
    rows: [
      { cls: "Woodland", ha: [388.22, 240.63, 193.16], pct: [24.36, 15.1, 12.12] },
      { cls: "Grassland", ha: [978.65, 646.45, 509.74], pct: [61.42, 40.57, 31.99] },
      { cls: "Built up", ha: [226.49, 706.28, 890.46], pct: [14.21, 44.33, 55.89], highlight: true },
    ],
  },
  {
    id: "mahatshula",
    name: "Mahatshula",
    src: SUBURB_MAPS.mahatshula,
    alt: "Land use land cover maps of Mahatshula, 1990, 2008 and 2025",
    fig: "Fig 6.2",
    tbl: "Table 6.2",
    caption:
      "Land cover in Mahatshula in 1990, 2008 and 2025.",
    reading:
      "Mahatshula was almost empty in 1990, with only 3.0% built up. It has changed the most of the three. Built up land grew about sixteenfold to 320.5 ha (47.7%) by 2025. Unlike Cowdray Park the pace picked up over time, from about 7.3 ha a year before 2008 to 10.0 ha a year after. Grassland shrank from 400.7 ha to 131.1 ha, a loss of 67%. Woodland grew to 323.4 ha in 2008 and then fell back to 220.1 ha. So the building after 2008 took trees as well as open grassland.",
    note: "The mapped area is 671.2 ha, 671.5 ha and 671.7 ha in the three years. Built up land (shaded) rose from 19.9 ha to 320.5 ha.",
    rows: [
      { cls: "Woodland", ha: [250.55, 323.35, 220.11], pct: [37.33, 48.15, 32.77] },
      { cls: "Grassland", ha: [400.69, 197.66, 131.07], pct: [59.7, 29.44, 19.51] },
      { cls: "Built up", ha: [19.91, 150.48, 320.54], pct: [2.97, 22.41, 47.72], highlight: true },
    ],
  },
  {
    id: "richmond",
    name: "Richmond",
    src: SUBURB_MAPS.richmond,
    alt: "Land use land cover maps of Richmond, 1990, 2008 and 2025",
    fig: "Fig 6.3",
    tbl: "Table 6.3",
    caption:
      "Land cover in Richmond in 1990, 2008 and 2025.",
    reading:
      "Richmond is the smallest suburb at about 282 ha. Built up land more than doubled from 50.9 ha (18.1%) to 115.1 ha (41.0%). It grew at a steady 1.6 ha a year to 2008 and 2.1 ha a year after. Richmond is the only suburb where grassland came back a little after 2008, from 68.2 ha to 76.5 ha. The newer building mostly replaced woodland, which dropped from 133.8 ha to 88.8 ha.",
    note: "The mapped area is 282.19 ha in 1990 and 2008 but 280.35 ha in 2025, so the 2025 shares are of a slightly smaller area. Built up land is shaded.",
    rows: [
      { cls: "Woodland", ha: [100.0, 133.79, 88.83], pct: [35.44, 47.41, 31.68] },
      { cls: "Grassland", ha: [131.26, 68.15, 76.47], pct: [46.52, 24.15, 27.28] },
      { cls: "Built up", ha: [50.93, 80.25, 115.05], pct: [18.05, 28.44, 41.04], highlight: true },
    ],
  },
];

const fmtHa = (n: number) =>
  n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const fmtDelta = (n: number) => (n > 0 ? "+" : "") + fmtHa(n);

function SuburbTable({ rows }: { rows: SuburbRow[] }) {
  return (
    <div className="tbl-wrap">
      <table className="dtable">
        <thead>
          <tr>
            <th>Class</th>
            {SUBURB_EPOCHS.map((y) => (
              <th key={y}>{y} (ha)</th>
            ))}
            <th>Change since 1990 (ha)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.cls} className={r.highlight ? "dtable__row--hl" : ""}>
              <td className="dtable__label">{r.cls}</td>
              {r.ha.map((v, i) => (
                <td key={i} className="dtable__num">
                  {fmtHa(v)}
                  <span className="dtable__pct">{r.pct[i].toFixed(1)}%</span>
                </td>
              ))}
              <td className="dtable__num">{fmtDelta(r.ha[2] - r.ha[0])}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SuburbCase() {
  const total = (s: Suburb, i: number) => s.rows.reduce((a, r) => a + r.ha[i], 0);
  const built = (s: Suburb, i: number) => s.rows.find((r) => r.highlight)?.ha[i] ?? 0;

  const compare = [
    ...SUBURBS.map((s) => ({
      name: s.name,
      all: false,
      shares: [0, 1, 2].map((i) => (built(s, i) / total(s, i)) * 100),
    })),
    {
      name: "All three together",
      all: true,
      shares: [0, 1, 2].map(
        (i) =>
          (SUBURBS.reduce((a, s) => a + built(s, i), 0) /
            SUBURBS.reduce((a, s) => a + total(s, i), 0)) *
          100
      ),
    },
  ];

  return (
    <>
      <section className="case-divider" id="case-suburbs">
        <h2>Three Bulawayo suburbs</h2>
        <p>
          Cowdray Park and Mahatshula and Richmond in 1990 and 2008 and 2025. Houses replaced grassland and
          woodland in each suburb in a different way.
        </p>
      </section>

      <Stats items={SUBURB_STATS} />

      <section className="psection">
        <div className="proj-grid">
          <div>
            <h3 className="proj-h2">Study area</h3>
            <p className="proj-p">
              Cowdray Park (about 1,593 ha), Mahatshula (about 672 ha) and Richmond (about 282 ha) cover
              roughly 2,545 ha together. Mapping at this scale shows how the citywide trend in the first case
              study looks on the ground and how quickly open land is being built on in each place.
            </p>
          </div>
          <div>
            <h3 className="proj-h2">Method</h3>
            <p className="proj-p">
              Each suburb was classified for 1990, 2008 and 2025 into three classes: woodland, grassland and
              built up. Areas are in hectares from pixel counts, next to each class's share of the suburb.
              There is no separate cultivation class here. Each suburb's three years are shown together in
              one map layout.
            </p>
          </div>
        </div>
      </section>

      {SUBURBS.map((s, n) => (
        <section key={s.id} className="psection" id={`suburb-${s.id}`}>
          <h3 className="sec-h">{s.name}</h3>
          {s.src && (
            <Figure src={s.src} alt={s.alt} name={`Figure ${5 + n}.`}>{s.caption}</Figure>
          )}
          <p className="proj-p" style={{ marginTop: 18 }}>{s.reading}</p>
          <SuburbTable rows={s.rows} />
          <p className="tbl-note">{s.note}</p>
        </section>
      ))}

      <section className="psection">
        <h3 className="sec-h">Share of each suburb that is built up</h3>
        <div className="cmp">
          {compare.map((c) => (
            <div key={c.name} className={`cmp__col${c.all ? " cmp__col--all" : ""}`}>
              <h4 className="cmp__name">{c.name}</h4>
              {c.shares.map((v, i) => (
                <div key={SUBURB_EPOCHS[i]} className="cmp__row">
                  <span>{SUBURB_EPOCHS[i]}</span>
                  <div className="cmp__track">
                    <div className="cmp__bar" style={{ width: `${v}%` }} />
                  </div>
                  <span className="cmp__val">{v.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          ))}
        </div>
        <p className="tbl-note">
          Mahatshula started lowest at 3.0% and caught up fastest, reaching 47.7% by 2025. Cowdray Park is
          still the most built up at 55.9%. These are net figures, so they show how much land ended up built
          up but not what each new built up pixel used to be.
        </p>
      </section>
    </>
  );
}
