import { useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { DASHBOARDS, STORYMAPS, WEBMAPS } from "./catalogue";
import "./page.css";

type Item = { slug: string; title: string; src: string };

/* A web map or story map filling the screen, with a thin bar to get back to the site. */
export default function MapViewer({ kind = "map" }: { kind?: "map" | "story" | "dashboard" }) {
  const { slug } = useParams();
  const items: Item[] = kind === "story" ? STORYMAPS : kind === "dashboard" ? DASHBOARDS : WEBMAPS;
  const back = kind === "story" ? "/projects/story-maps" : kind === "dashboard" ? "/projects/dashboards" : "/projects/web-mapping";
  const base = kind === "story" ? "/stories" : kind === "dashboard" ? "/dashboards" : "/maps";
  const i = items.findIndex((m) => m.slug === slug);
  const m = items[i];
  const [loaded, setLoaded] = useState(false);
  const navigate = useNavigate();
  // go back in history when there is some, so the list reopens where the visitor left it
  const goBack = (e: React.MouseEvent) => {
    if (window.history.state && window.history.state.idx > 0) { e.preventDefault(); navigate(-1); }
  };

  useEffect(() => { setLoaded(false); }, [slug]);
  useEffect(() => {
    if (m) document.title = `${m.title} | Kudzanai Chakavarika`;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, [m]);

  if (!m) return <Navigate to={back} replace />;
  const next = items.length > 1 ? items[(i + 1) % items.length] : null;

  return (
    <div className="viewer">
      <div className="viewer__bar">
        <Link to={back} className="viewer__back" onClick={goBack}>Back</Link>
        <b className="viewer__title">{m.title}</b>
        <div className="viewer__right">
          {next && <Link to={`${base}/${next.slug}`} replace className="viewer__next">Next: {next.title}</Link>}
          <a href={m.src} target="_blank" rel="noreferrer">Full screen</a>
        </div>
      </div>
      <div className="viewer__stage">
        {!loaded && <div className="viewer__load">{kind === "story" ? "Loading the story..." : kind === "dashboard" ? "Loading the dashboard..." : "Loading the map..."}</div>}
        <iframe key={m.slug} src={m.src} title={m.title} onLoad={() => setLoaded(true)}
          allow="fullscreen; geolocation" />
      </div>
    </div>
  );
}
