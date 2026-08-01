import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function RemoteSensingIndices() {
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

      <section className="ptitle">
        <span className="p-ref">Project · Remote Sensing Indices</span>
        <h1>Remote Sensing Indices</h1>
        <p className="ptitle__subtitle">
          Derivation and analysis of spectral indices (NDVI, NDWI, and others) from satellite imagery.
        </p>
      </section>

      <section className="psection psection--paper">
        <p className="section-tag">§ Overview</p>
        <div className="proj-body">
          <p className="proj-placeholder">
            Full project details, maps, and imagery for this entry are coming soon.
          </p>
        </div>
      </section>

      <footer className="pfooter">
        <span>© 2026 Kudzanai Chakavarika</span>
        <a href="/">spatialforce.co.zw</a>
      </footer>
    </>
  );
}

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;700;800;900&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

:root {
  --paper:  #EFEAE0;
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

.section-tag { font-family: var(--fm); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; color: var(--rust); padding: 1.6rem 4vw 1.2rem; }
.p-ref { font-family: var(--fm); font-size: 0.74rem; color: var(--brass); letter-spacing: 0.06em; }

.pnav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 1.4rem 4vw; background: linear-gradient(rgba(25,27,21,0.9), transparent); transition: background 0.3s, padding 0.3s; }
.pnav--scrolled { background: rgba(25,27,21,0.97); padding: 1rem 4vw; border-bottom: 1px solid var(--linew); }
.pnav__mark { font-family: var(--fm); font-weight: 600; font-size: 0.85rem; letter-spacing: 0.04em; color: var(--cream); text-decoration: none; }
.pnav__mark span { color: var(--rust); }
.pnav__back { font-family: var(--fm); font-size: 0.74rem; color: rgba(247,243,233,0.6); text-decoration: none; transition: color 0.2s; }
.pnav__back:hover { color: var(--brass); }

.ptitle { background: var(--night); padding: 6.4rem 4vw 2.2rem; }
.ptitle h1 {
  font-family: var(--fd); font-weight: 800; text-transform: uppercase;
  font-size: clamp(1.9rem, 4.2vw, 3rem); line-height: 1.04; letter-spacing: -0.01em;
  color: var(--cream); margin: 0.5rem 0 0.7rem; max-width: 24ch;
}
.ptitle__subtitle { font-size: 0.98rem; font-weight: 300; color: rgba(247,243,233,0.6); max-width: 55ch; }

.psection { background: var(--night); padding-bottom: 0.5rem; }
.psection--paper { background: var(--paper); }
.psection--paper .section-tag { color: var(--rust); }

.proj-body { padding: 0 4vw 4rem; }
.proj-placeholder {
  font-size: 0.95rem; line-height: 1.7; color: #4A463C;
  border: 1px dashed rgba(177,80,42,0.4); border-radius: 3px;
  background: var(--cream); padding: 1.6rem; max-width: 60ch;
}

.pfooter { background: var(--night); padding: 1.4rem 4vw; display: flex; align-items: center; justify-content: space-between; font-family: var(--fm); font-size: 0.66rem; color: rgba(247,243,233,0.4); }
.pfooter a { color: rgba(247,243,233,0.4); text-decoration: none; }

@media (max-width: 640px) {
  .pnav { padding: 1rem 6vw; }
  .ptitle { padding: 5.6rem 6vw 1.8rem; }
  .ptitle h1 { font-size: clamp(1.6rem, 7.5vw, 2.1rem); max-width: none; }
  .section-tag { padding: 1.4rem 6vw 1rem; }
  .proj-body { padding: 0 6vw 2rem; }
  .pfooter { flex-direction: column; gap: 0.5rem; text-align: center; }
}
`;
