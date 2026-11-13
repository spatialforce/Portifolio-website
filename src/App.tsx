import { useEffect, useLayoutEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigationType } from "react-router-dom";
import Home from "./pages/home";
import ProjectsPage from "./pages/projects";
import ForestResourcesProject from "./pages/forest";
import RemoteSensingIndices from "./pages/remotesensingindices";
import FireSusceptibilityMapping from "./pages/firesusceptibilitymapping";
import WebMapping from "./pages/webmapping";
import MapViewer from "./pages/mapviewer";
import StoryMaps from "./pages/storymaps";
import PopulationCaseStudy from "./pages/cs_population";
import RainfallCaseStudy from "./pages/cs_rainfall";
import LulcCaseStudy from "./pages/cs_lulc";
import MazoweCaseStudy from "./pages/cs_mazowe";
import SolarCaseStudy from "./pages/cs_solar";
import CarbonCaseStudy from "./pages/cs_carbon";
import AirQualityCaseStudy from "./pages/cs_airquality";
import ChimanimaniFloodCaseStudy from "./pages/cs_chimflood";
import SugarcaneCaseStudy from "./pages/cs_sugarcane";
import KaribaCaseStudy from "./pages/cs_kariba";
import LandfillCaseStudy from "./pages/cs_landfill";
import ShurugwiCaseStudy from "./pages/cs_shurugwi";
import BaobabCaseStudy from "./pages/cs_baobab";
import Seo from "./pages/seo";

/* New page: start at the top, or at the #section the link points to.
   Back/forward: return to the exact link the visitor clicked (e.g. the map thumbnail),
   at the same height on screen; fall back to the saved scroll position. */
type Spot = { y: number; href?: string; nth?: number; top?: number };
const saved: Record<string, Spot> = (() => {
  try { return JSON.parse(sessionStorage.getItem("scrollSpots") || "{}"); } catch { return {}; }
})();
const persist = () => { try { sessionStorage.setItem("scrollSpots", JSON.stringify(saved)); } catch { /* ignore */ } };

function ScrollManager() {
  const { pathname, hash, key } = useLocation();
  const type = useNavigationType();

  useEffect(() => {
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  }, []);

  // track scroll, and remember which link was clicked on this page
  useEffect(() => {
    let t = 0;
    const onScroll = () => {
      saved[key] = { y: window.scrollY };
      clearTimeout(t);
      t = window.setTimeout(persist, 150);
    };
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element | null)?.closest?.("a[href]") as HTMLAnchorElement | null;
      if (!a || a.target === "_blank") return;
      const href = a.getAttribute("href")!;
      if (!href.startsWith("/")) return;
      const same = Array.from(document.querySelectorAll(`a[href="${CSS.escape(href)}"]`));
      saved[key] = { y: window.scrollY, href, nth: same.indexOf(a), top: a.getBoundingClientRect().top };
      persist();
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("click", onClick, true);
    return () => {
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("click", onClick, true);
      clearTimeout(t);
      persist();
    };
  }, [key]);

  // layout effect: the page is put back in place before the browser paints it, so it never
  // shows the top first and then jumps
  useLayoutEffect(() => {
    const spot = saved[key];
    if (type === "POP" && spot) {
      // coming back: show the cards as they were, without fading them in again
      document.querySelectorAll(".rv").forEach((el) => el.classList.add("rv-now", "in"));
      const target = () => {
        if (spot.href !== undefined) {
          const el = document.querySelectorAll(`a[href="${CSS.escape(spot.href)}"]`)[spot.nth ?? 0];
          if (el) return window.scrollY + el.getBoundingClientRect().top - (spot.top ?? 0);
        }
        return spot.y;
      };
      // images and lists may still be loading and shifting the page: keep re-aiming briefly,
      // but stop as soon as the visitor scrolls themselves
      let stop = false;
      const cancel = () => { stop = true; };
      window.addEventListener("wheel", cancel, { passive: true });
      window.addEventListener("touchstart", cancel, { passive: true });
      window.addEventListener("keydown", cancel);
      let tries = 0;
      let id = 0;
      // only move if the target really shifted, so the page does not twitch
      const attempt = () => {
        if (stop) return;
        const y = Math.max(0, Math.round(target()));
        if (Math.abs(y - window.scrollY) > 1) window.scrollTo(0, y);
        if (tries++ < 10) id = window.setTimeout(attempt, 100);
      };
      attempt();
      return () => {
        clearTimeout(id);
        window.removeEventListener("wheel", cancel);
        window.removeEventListener("touchstart", cancel);
        window.removeEventListener("keydown", cancel);
      };
    }
    if (!hash) { window.scrollTo(0, 0); return; }
    const go = () => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: "smooth" });
    const id = setTimeout(go, 60);
    return () => clearTimeout(id);
  }, [pathname, hash, key, type]);
  return null;
}

function App() {
  return (
    <Router basename={import.meta.env.BASE_URL}>
      <ScrollManager />
      <Seo />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/zimbabwe-gazetted-forests" element={<ForestResourcesProject />} />
        <Route path="/projects/land-use-land-cover" element={<Navigate to="/case-studies/land-use-land-cover" replace />} />
        <Route path="/projects/remote-sensing-indices" element={<RemoteSensingIndices />} />
        <Route path="/projects/fire-susceptibility-mapping" element={<FireSusceptibilityMapping />} />
        <Route path="/projects/web-mapping" element={<WebMapping />} />
        <Route path="/case-studies/population-zimbabwe" element={<PopulationCaseStudy />} />
        <Route path="/case-studies/rainfall-zimbabwe" element={<RainfallCaseStudy />} />
        <Route path="/case-studies/land-use-land-cover" element={<LulcCaseStudy />} />
        <Route path="/case-studies/mazowe-valley" element={<MazoweCaseStudy />} />
        <Route path="/case-studies/solar-site-suitability" element={<SolarCaseStudy />} />
        <Route path="/case-studies/hwange-carbon" element={<CarbonCaseStudy />} />
        <Route path="/case-studies/hwange-air" element={<AirQualityCaseStudy />} />
        <Route path="/case-studies/chimanimani-flood" element={<ChimanimaniFloodCaseStudy />} />
        <Route path="/case-studies/sugarcane-triangle" element={<SugarcaneCaseStudy />} />
        <Route path="/case-studies/lake-kariba" element={<KaribaCaseStudy />} />
        <Route path="/case-studies/bulawayo-landfill" element={<LandfillCaseStudy />} />
        <Route path="/case-studies/shurugwi-soil-erosion" element={<ShurugwiCaseStudy />} />
        <Route path="/case-studies/baobab-habitat-suitability" element={<BaobabCaseStudy />} />
        <Route path="/case-studies" element={<Navigate to="/projects" replace />} />
        <Route path="/maps/:slug" element={<MapViewer />} />
        <Route path="/projects/story-maps" element={<StoryMaps />} />
        <Route path="/stories/:slug" element={<MapViewer kind="story" />} />
        <Route path="/projects/study-area-maps" element={<Navigate to="/#gallery" replace />} />
        <Route path="/projects/drought-analysis" element={<Navigate to="/projects" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
