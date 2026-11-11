import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import Terrain3D from "./Terrain3D";
import SiteNav, { SiteFooter, NAME } from "./SiteChrome";
import { CASESTUDIES, PROJECTS, STORYMAPS, WEBMAPS } from "./catalogue";
import { GALLERY, RENDERS } from "./gallery";
import { useReveal } from "./reveal";
import profile from "../assets/myself.webp";
import "animate.css";
import "./page.css";

/* ---------------------------------- hero ---------------------------------- */
function Hero() {
  return (
    <header className="hero">
      <div className="hero__bg"><Terrain3D /></div>
      <div className="hero__in">
        <h1 className="hero__name">Kudzanai<br />Chakavarika</h1>
        <p className="hero__role">GIS &amp; Remote Sensing Analyst</p>
        <p className="hero__lede">I use geospatial technology to analyse real-world challenges, uncover spatial patterns and create impactful maps and applications.</p>
        <div className="hero__act">
          <a href="#webmaps" className="btn btn--light" onClick={(e) => { e.preventDefault(); document.getElementById("webmaps")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); }}>See my work</a>
          <a href="/cv.pdf" target="_blank" rel="noreferrer" className="btn btn--ghost"><i className="bi bi-download" aria-hidden="true" />Download CV</a>
        </div>
      </div>
    </header>
  );
}

/* ------------------------------ slideshow ------------------------------ */
// a row of cards that slides sideways with the arrows, a swipe or the trackpad
function Slider({ label, children, auto }: { label: string; children: ReactNode; auto?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [edge, setEdge] = useState({ l: true, r: false });
  const hold = useRef(false);
  // with "auto", the row moves on by a full set of cards every few seconds, back to the start at the end.
  // It waits while the pointer or focus is on it or it is off screen, and never runs for reduced motion.
  useEffect(() => {
    const el = ref.current;
    if (!auto || !el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let seen = false;
    const io = new IntersectionObserver(([e]) => { seen = e.isIntersecting; }, { threshold: 0.4 });
    io.observe(el);
    const t = window.setInterval(() => {
      if (!seen || hold.current || document.hidden) return;
      if (el.scrollLeft + el.clientWidth >= el.scrollWidth - 4) el.scrollTo({ left: 0, behavior: "smooth" });
      else el.scrollBy({ left: el.clientWidth, behavior: "smooth" });
    }, auto);
    return () => { window.clearInterval(t); io.disconnect(); };
  }, [auto]);
  const check = () => {
    const el = ref.current; if (!el) return;
    setEdge({ l: el.scrollLeft <= 4, r: el.scrollLeft + el.clientWidth >= el.scrollWidth - 4 });
  };
  useEffect(() => { check(); window.addEventListener("resize", check); return () => window.removeEventListener("resize", check); }, []);
  const move = (d: number) => {
    const el = ref.current; if (!el) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    el.scrollBy({ left: d * el.clientWidth, behavior: reduce ? "auto" : "smooth" });
  };
  return (
    <div className="sl" onMouseEnter={() => (hold.current = true)} onMouseLeave={() => (hold.current = false)}
      onFocus={() => (hold.current = true)} onBlur={() => (hold.current = false)}>
      <div className="sl__track" ref={ref} onScroll={check} role="region" aria-label={label} tabIndex={0}>{children}</div>
      {!edge.l && <button type="button" className="sl__btn sl__btn--l" aria-label="Previous" onClick={() => move(-1)}><i className="bi bi-chevron-left" /></button>}
      {!edge.r && <button type="button" className="sl__btn sl__btn--r" aria-label="Next" onClick={() => move(1)}><i className="bi bi-chevron-right" /></button>}
    </div>
  );
}

// centred section heading
function Head({ title, lede }: { title: string; lede: string }) {
  return (
    <div className="sh rv">
      <h2 className="h2">{title}</h2><p className="sec-lede">{lede}</p>
    </div>
  );
}

/* ------------------------------ show more ------------------------------ */
// Shows the first rows of cards in full and the top of the next row dimmed under a "See all" button.
// Clicking it opens the whole list in rows and columns.
type PeekItem = { key: string; node: ReactNode };
function Peek({ items, show = 6, grid = "" }: { items: PeekItem[]; show?: number; grid?: string }) {
  const [all, setAll] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const more = items.length > show;
  // the "See more" button slides up into view when it scrolls onto the screen
  const btn = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = btn.current;
    if (!el || seen) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setSeen(true); io.disconnect(); } }, { threshold: 0.6 });
    io.observe(el);
    return () => io.disconnect();
  }, [more, seen]);
  const less = () => {
    setAll(false);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    box.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  };
  return (
    <div className="pk" ref={box}>
      <div className={`wm-grid ${grid}`}>
        {items.map((it, k) => (
          <div key={it.key} style={!all && k >= show ? { display: "none" } : undefined}
            className={all && k >= show ? "animate__animated animate__fadeIn" : undefined}>{it.node}</div>
        ))}
      </div>
      {more && (
        <div ref={btn} className={`pk__more${seen ? " animate__animated animate__fadeInUp" : " pk__wait"}`}>
          {all
            ? <button type="button" className="btn btn--line" onClick={less}>Show less</button>
            : <button type="button" className="btn pk__see" onClick={() => setAll(true)}>See more<i className="bi bi-chevron-down" aria-hidden="true" /></button>}
        </div>
      )}
    </div>
  );
}

/* ------------------------------ map gallery ------------------------------ */
function MapGallery() {
  const [open, setOpen] = useState<number | null>(null);
  const n = GALLERY.length;
  const go = (k: number) => setOpen(((k % n) + n) % n);
  useEffect(() => {
    if (open === null) return;
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(null);
      if (e.key === "ArrowRight") go(open + 1);
      if (e.key === "ArrowLeft") go(open - 1);
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [open]);
  const s = open === null ? null : GALLERY[open];
  return (
    <>
      <Slider label="Map Galore" auto={5000}>
        {GALLERY.map((g, k) => (
          <button key={g.title} type="button" className="sl__item mg__item" onClick={() => setOpen(k)}>
            <span className="mg__img"><img src={g.img} alt={g.title} loading="lazy" draggable={false} /></span>
            <span className="mg__title">{g.title}</span>
          </button>
        ))}
      </Slider>
      {s && (
        <div className="plightbox" onClick={() => setOpen(null)}>
          <button className="plightbox__close" onClick={() => setOpen(null)} aria-label="Close"><i className="bi bi-x-lg" /></button>
          <button className="sl__btn sl__btn--l" type="button" aria-label="Previous map" onClick={(e) => { e.stopPropagation(); go(open! - 1); }}><i className="bi bi-chevron-left" /></button>
          <img src={s.img} alt={s.title} onClick={(e) => e.stopPropagation()} />
          <button className="sl__btn sl__btn--r" type="button" aria-label="Next map" onClick={(e) => { e.stopPropagation(); go(open! + 1); }}><i className="bi bi-chevron-right" /></button>
          <p className="plightbox__caption" onClick={(e) => e.stopPropagation()}><b>{s.title}</b></p>
        </div>
      )}
    </>
  );
}

/* ------------------------------ 3D renders ------------------------------ */
function Render3D({ r }: { r: (typeof RENDERS)[number] }) {
  const ref = useRef<HTMLVideoElement>(null);
  // videos play only while on screen, and not at all for people who prefer less motion
  useEffect(() => {
    const v = ref.current;
    if (!v || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) v.play().catch(() => {}); else v.pause(); }, { threshold: 0.25 });
    io.observe(v);
    return () => io.disconnect();
  }, []);
  return (
    <figure className="r3d rv">
      <div className={`r3d__media${r.light ? " r3d__media--light" : ""}`}>
        <div className="r3d__clip">
          {r.video
            ? <video ref={ref} src={r.video} poster={r.poster} muted loop playsInline preload="metadata" aria-label={r.title} />
            : <img src={r.img} alt={r.title} loading="lazy" />}
        </div>
      </div>
      <figcaption>
        <h3 className="h3">{r.title}</h3>
        <div><p>{r.text}</p><ul className="tags">{r.tools.map((t) => <li key={t}>{t}</li>)}</ul></div>
      </figcaption>
    </figure>
  );
}

/* ---------------------------------- page ---------------------------------- */
export default function Home() {
  useReveal();
  const work = [
    ...CASESTUDIES.map((p) => ({ ...p, href: `/case-studies/${p.slug}` })),
    ...PROJECTS.filter((p) => p.img && p.slug !== "web-mapping" && p.slug !== "story-maps").map((p) => ({ ...p, href: `/projects/${p.slug}` })),
  ];
  const stories = STORYMAPS;
  return (
    <>
      <SiteNav overlay />
      <Hero />

      {/* ------------------------------ web maps ------------------------------ */}
      <section className="band" id="webmaps">
        <div className="wrap wrap--wide">
          <Head title="Web maps" lede="Interactive maps you can explore right here." />
          <Peek items={WEBMAPS.map((m) => ({ key: m.slug, node: (
            <article className="wm-card">
              <Link to={`/maps/${m.slug}`} className="wm-card__img">
                <img src={m.img} alt={m.title} loading="lazy" draggable={false} />
              </Link>
              <h3 className="h3">{m.title}</h3>
              <p>{m.short}</p>
              <Link to={`/maps/${m.slug}`} className="arrow">Open the map</Link>
            </article>
          ) }))} />
        </div>
      </section>

      {/* -------------------------------- work -------------------------------- */}
      <section className="band band--cloud" id="work">
        <div className="wrap wrap--wide">
          <Head title="Case studies" lede="A collection of geospatial projects on population, land and hazards in Zimbabwe." />
          <Peek grid="cs-grid" items={work.map((p) => ({ key: p.slug, node: (
            <article className="wm-card cs-card">
              <Link to={p.href} className="wm-card__img cs-card__img">
                <img src={p.img} alt={p.title} loading="lazy" draggable={false} />
              </Link>
              <h3 className="h3"><Link to={p.href}>{p.card ?? p.title}</Link></h3>
              {p.sub && <p className="cs-card__sub">{p.sub}</p>}
            </article>
          ) }))} />

        </div>
      </section>

      {/* ------------------------------ story maps ------------------------------ */}
      {stories.length > 0 && (
        <section className="band band--white" id="stories">
          <div className="wrap wrap--wide">
            <Head title="Story maps" lede="Maps and photographs told as a story you scroll through." />
            <Slider label="Story maps">
              {stories.map((m) => (
                <article className="sl__item sl__item--wide story-card" key={m.slug}>
                  <Link to={`/stories/${m.slug}`} className="story__img">
                    <img src={m.img} alt={m.title} loading="lazy" draggable={false} />
                  </Link>
                  <div>
                    <h3 className="h3">{m.title}</h3>
                    <p>{m.text}</p>
                    <Link to={`/stories/${m.slug}`} className="arrow">Read the story</Link>
                  </div>
                </article>
              ))}
            </Slider>
          </div>
        </section>
      )}

      {/* ------------------------------ 3D terrain ------------------------------ */}
      <section className="band band--cloud" id="terrain">
        <div className="wrap wrap--wide">
          <div className="sec-top rv">
            <h2 className="h2">3D work</h2>
            <p className="sec-lede">Elevation data turned into landscapes you can read at a glance.</p>
          </div>
          <div className="r3d-list">
            {RENDERS.map((r) => <Render3D key={r.title} r={r} />)}
          </div>
        </div>
      </section>

      {/* ------------------------------ map gallery ------------------------------ */}
      <section className="band band--white" id="gallery">
        <div className="wrap wrap--wide">
          <Head title="Map Galore" lede="A selection of maps from my projects." />
          <MapGallery />
        </div>
      </section>

      {/* -------------------------------- about ------------------------------- */}
      <section className="band band--cloud" id="about">
        <div className="wrap about__grid">
          <figure className="about__photo rv">
            <img src={profile} alt={NAME} loading="lazy" />
          </figure>
          <div className="about__txt rv">
            <h2 className="h2">Hi, I'm Kudzanai</h2>
            <p>I am a First Class BSc graduate in GIS and Remote Sensing in Natural Resources Management, with skills in geospatial analysis, satellite imagery, spatial data management and web development. I specialise in analysing landscape changes and transforming geospatial data into meaningful insights through maps and interactive web applications. I am currently seeking opportunities as a GIS Specialist across various sectors where I can apply my skills and contribute to solving real-world problems.</p>

            <dl className="tools">
              {[["GIS", ["Cartography", "Spatial Modelling", "GIS Automation", "MCDA"]],
                ["Remote Sensing", ["Image Processing", "Spectral Indices", "Time Series Analysis"]],
                ["Database", ["PostGIS", "Spatial Database Design", "Geospatial Data Management"]],
                ["Web GIS", ["React", "Leaflet", "D3.js", "Three.js", "ArcGIS Online"]],
                ["Software", ["ArcGIS Pro", "QGIS", "SNAP", "MODFLOW", "Global Mapper", "Cloud based (GEE, SEPAL, Google Colab with Python)"]]].map(([k, v]) => (
                <div key={k as string} className="tagrow"><dt>{k as string}</dt><dd><ul className="tags">{(v as string[]).map((t) => <li key={t} className={t.startsWith("Cloud") ? "tags__own" : undefined}>{t}</li>)}</ul></dd></div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      <SiteFooter />
    </>
  );
}
