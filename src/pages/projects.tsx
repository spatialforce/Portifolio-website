import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { PROJECTS, CASESTUDIES } from "./catalogue";
import { useReveal } from "./reveal";
import "./page.css";

export default function ProjectsIndex() {
  useReveal();
  const ready = [
    ...CASESTUDIES.map((p) => ({ ...p, href: `/case-studies/${p.slug}` })),
    ...PROJECTS.filter((p) => p.img).map((p) => ({ ...p, href: `/projects/${p.slug}` })),
  ];
  const soon = PROJECTS.filter((p) => !p.img);
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Case studies</h1>
        <p className="ptitle__subtitle">GIS analysis and remote sensing and web maps. Most of it is in Zimbabwe.</p>
      </section>
      <section className="psection">
        <div className="wm-grid cs-grid glist">
          {ready.map((p) => (
            <article key={p.slug} className="wm-card cs-card rv">
              <Link to={p.href} className="wm-card__img cs-card__img">
                <img src={p.img} alt={p.title} loading="lazy" />
              </Link>
              <h2 className="h3"><Link to={p.href}>{p.card ?? p.title}</Link></h2>
              {p.sub && <p className="cs-card__sub">{p.sub}</p>}
            </article>
          ))}
        </div>
        {soon.length > 0 && (
          <div className="plist__soon">
            <h2>Coming next</h2>
            <p>
              {soon.map((p, i) => (
                <span key={p.slug}>{i > 0 && " and "}<Link to={`/projects/${p.slug}`}>{p.title}</Link></span>
              ))}. Both are in progress.
            </p>
          </div>
        )}
      </section>
      <SiteFooter />
    </>
  );
}
