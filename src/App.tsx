import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/home";
import ProjectsPage from "./pages/projects";
import StudyAreaMaps from "./pages/studyareamaps";
import ForestResourcesProject from "./pages/forest";
import LandUseLandCover from "./pages/landuselandcover";
import FloodSusceptibilityMapping from "./pages/floodsusceptibilitymapping";
import RemoteSensingIndices from "./pages/remotesensingindices";
import DroughtAnalysis from "./pages/droughtanalysis";
import FireSusceptibilityMapping from "./pages/firesusceptibilitymapping";
import WebMapping from "./pages/webmapping";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/projects" element={<ProjectsPage />} />

        {/* Simply add "/projects" in front of the path layout */}
        <Route path="/projects/study-area-maps" element={<StudyAreaMaps />} />
        <Route path="/projects/zimbabwe-gazetted-forests" element={<ForestResourcesProject />} />
        <Route path="/projects/land-use-land-cover" element={<LandUseLandCover />} />
        <Route path="/projects/flood-susceptibility-mapping" element={<FloodSusceptibilityMapping />} />
        <Route path="/projects/remote-sensing-indices" element={<RemoteSensingIndices />} />
        <Route path="/projects/drought-analysis" element={<DroughtAnalysis />} />
        <Route path="/projects/fire-susceptibility-mapping" element={<FireSusceptibilityMapping />} />
        <Route path="/projects/web-mapping" element={<WebMapping />} />
      </Routes>
    </Router>
  );
}

export default App;
