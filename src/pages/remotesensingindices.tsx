import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import "./page.css";

export default function RemoteSensingIndices() {
  return (
    <>
      <SiteNav />
      <section className="ptitle">
        <h1>Remote sensing indices</h1>
        <p className="ptitle__subtitle">Spectral indices such as NDVI and NDWI from satellite imagery.</p>
      </section>
      <section className="psection" style={{ paddingBottom: 96 }}>
        <p className="soon">I'm still working on this one. The maps and write up will be here soon. In the meantime you can <Link to="/projects" className="arrow">see my other work</Link></p>
      </section>
      <SiteFooter />
    </>
  );
}
