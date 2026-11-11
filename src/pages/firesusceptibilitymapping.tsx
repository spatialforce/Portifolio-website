import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import "./page.css";

export default function FireSusceptibilityMapping() {
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Fire susceptibility mapping</h1>
        <p className="ptitle__subtitle">Wildfire risk mapped from vegetation and climate data.</p>
      </section>
      <section className="psection" style={{ paddingBottom: 96 }}>
        <p className="soon">I'm still working on this one. The maps and write up will be here soon. In the meantime you can <Link to="/projects" className="arrow">see my other work</Link></p>
      </section>
      <SiteFooter />
    </>
  );
}
