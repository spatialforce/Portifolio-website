import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";

export const NAME = "Kudzanai Chakavarika";
export const EMAIL = "kudzanaichakavarika67@gmail.com";

/* overlay: transparent over the home hero until the page scrolls */
export default function SiteNav({ overlay = false }: { overlay?: boolean }) {
  const [open, setOpen] = useState(false);
  const [solid, setSolid] = useState(!overlay);

  useEffect(() => {
    if (!overlay) return;
    const f = () => setSolid(window.scrollY > window.innerHeight * 0.75);
    f();
    window.addEventListener("scroll", f, { passive: true });
    return () => window.removeEventListener("scroll", f);
  }, [overlay]);

  return (
    <nav className={`snav ${solid ? "snav--solid" : ""} ${open ? "snav--open" : ""}`}>
      <Link to="/" className="snav__brand" onClick={() => setOpen(false)}>{NAME}</Link>
      <button className="snav__burger" aria-label="Menu" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span /><span />
      </button>
      <div className="snav__links" onClick={() => setOpen(false)}>
        <NavLink to="/projects" end>Case studies</NavLink>
        <NavLink to="/projects/web-mapping">Web maps</NavLink>
        <NavLink to="/projects/story-maps">Story maps</NavLink>
        <Link to="/#about">About</Link>
        <Link to="/#contact">Contact</Link>
        <a href="/cv.pdf" target="_blank" rel="noreferrer" className="snav__cv">CV</a>
      </div>
    </nav>
  );
}

export function SiteFooter() {
  return (
    <footer id="contact" className="sfoot">
      <div className="sfoot__in">
        <h2 className="sfoot__h">Have a project in mind?</h2>
        <p className="sfoot__p">Open to GIS opportunities across all sectors. Email is the quickest way to reach me.</p>
        <a className="sfoot__mail" href={`mailto:${EMAIL}`}>{EMAIL}</a>
        <div className="sfoot__row">
          <div className="sfoot__links">
            <a href="https://www.linkedin.com/in/kudzanai-chakavarika-65a847372" target="_blank" rel="noreferrer"><i className="bi bi-linkedin" aria-hidden="true" /> LinkedIn</a>
            <a href="https://github.com/spatialforce" target="_blank" rel="noreferrer"><i className="bi bi-github" aria-hidden="true" /> GitHub</a>
            <a href="/cv.pdf" target="_blank" rel="noreferrer"><i className="bi bi-file-earmark-text" aria-hidden="true" /> CV</a>
          </div>
          <span className="sfoot__base">© {NAME}</span>
        </div>
        <p className="sfoot__note">Every map and chart on this site is drawn from measured, cited open datasets using GIS software and code. None is an AI-generated image. Each file carries its author and data-source details in its metadata.</p>
      </div>
    </footer>
  );
}
