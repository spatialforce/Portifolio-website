import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { WEBMAPS } from "./catalogue";
import { useReveal } from "./reveal";
import "./page.css";

export default function WebMapping() {
  useReveal();
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Web maps</h1>
        <p className="ptitle__subtitle">Interactive maps built on open data. Open one and explore it for yourself.</p>
      </section>

      <section className="psection">
        <div className="wm-grid glist">
          {WEBMAPS.map((m) => (
            <article key={m.slug} className="wm-card rv">
              <Link to={`/maps/${m.slug}`} className="wm-card__img">
                <img src={m.img} alt={m.title} loading="lazy" />
              </Link>
              <h2 className="h3"><Link to={`/maps/${m.slug}`}>{m.title}</Link></h2>
              <p>{m.text}</p>
              <Link to={`/maps/${m.slug}`} className="arrow">Open the map</Link>
            </article>
          ))}
        </div>
      </section>
      <SiteFooter />
    </>
  );
}
