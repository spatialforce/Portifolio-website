import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { DASHBOARDS } from "./catalogue";
import { useReveal } from "./reveal";
import "./page.css";

export default function Dashboards() {
  useReveal();
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Dashboards</h1>
        <p className="ptitle__subtitle">Interactive dashboards built in Tableau from open data.</p>
      </section>

      <section className="psection">
        <div className="wm-grid glist">
          {DASHBOARDS.map((m) => (
            <article key={m.slug} className="wm-card rv">
              <Link to={`/dashboards/${m.slug}`} className="wm-card__img">
                <img src={m.img} alt={m.title} loading="lazy" />
              </Link>
              <h2 className="h3"><Link to={`/dashboards/${m.slug}`}>{m.title}</Link></h2>
              <p>{m.text}</p>
              <Link to={`/dashboards/${m.slug}`} className="arrow">Open the dashboard</Link>
            </article>
          ))}
        </div>
      </section>
      <SiteFooter />
    </>
  );
}
