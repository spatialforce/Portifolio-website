import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { STORYMAPS } from "./catalogue";
import { useReveal } from "./reveal";
import "./page.css";

export default function StoryMaps() {
  useReveal();
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Story maps</h1>
        <p className="ptitle__subtitle">Maps and photographs told as a story you scroll through.</p>
      </section>

      <section className="psection">
        <div className="wm-grid glist">
          {STORYMAPS.map((m) => (
            <article key={m.slug} className="wm-card rv">
              <Link to={`/stories/${m.slug}`} className="wm-card__img">
                <img src={m.img} alt={m.title} loading="lazy" />
              </Link>
              <h2 className="h3"><Link to={`/stories/${m.slug}`}>{m.title}</Link></h2>
              <p>{m.text}</p>
              <Link to={`/stories/${m.slug}`} className="arrow">Read the story</Link>
            </article>
          ))}
        </div>
      </section>
      <SiteFooter />
    </>
  );
}
