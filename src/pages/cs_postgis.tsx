import CaseLayout, { Facts } from "./CaseLayout";
import map1 from "../assets/casestudies/harare-health-access/map1_study_area.webp";
import map2 from "../assets/casestudies/harare-health-access/map2_distance_all.webp";
import map3 from "../assets/casestudies/harare-health-access/map3_distance_public.webp";
import map4 from "../assets/casestudies/harare-health-access/map4_wards.webp";
import map5 from "../assets/casestudies/harare-health-access/map5_catchments.webp";
import map6 from "../assets/casestudies/harare-health-access/map6_sites.webp";
import fig1 from "../assets/casestudies/harare-health-access/fig1_bands.webp";
import fig2 from "../assets/casestudies/harare-health-access/fig2_cumulative.webp";
import fig3 from "../assets/casestudies/harare-health-access/fig3_load.webp";
import fig4 from "../assets/casestudies/harare-health-access/fig4_sites.webp";

function Fig({ src, cap }: { src: string; cap: string }) {
  return (
    <figure>
      <a href={src} target="_blank" rel="noopener noreferrer"><img src={src} alt={cap} loading="lazy" /></a>
      <figcaption>{cap}</figcaption>
    </figure>
  );
}

function Rows({ rows, num }: { rows: string[][]; num: number }) {
  return <>{rows.map((r) => <tr key={r.join("|")} className={r[0] === "Total" ? "t" : undefined}>{r.map((c, i) => <td key={i} className={i >= num ? "n" : undefined}>{c}</td>)}</tr>)}</>;
}

const Sql = ({ children }: { children: string }) => (
  <pre style={{ fontFamily: "Consolas, 'Courier New', monospace", fontSize: 13, lineHeight: 1.5, background: "#f6f6f6", padding: "10px 12px", overflowX: "auto", margin: "0 0 6px" }}>{children}</pre>
);

// Table 1: data
const T1: string[][] = [
  ["OpenStreetMap roads, paths and tracks (Geofabrik extract)", "Lines", "2026", "Walking network"],
  ["OpenStreetMap clinics and hospitals", "Points, polygons", "2026", "Destinations, scenario B"],
  ["Public health facility list for sub-Saharan Africa (Maina et al.)", "Points", "2019", "Destinations, scenario A"],
  ["WorldPop constrained population, R2025A", "100 m", "2025", "Demand points"],
  ["geoBoundaries province (ADM1) and wards (ADM3)", "Polygons", "2023", "Study area, wards"],
  ["OpenStreetMap place names", "Points", "2026", "Map labels, site names"],
];

// Table 2: walking network by OSM class
const T2: string[][] = [
  ["Residential street", "116 482", "5 308.9"],
  ["Service road", "44 777", "1 179.3"],
  ["Track", "36 393", "1 179.2"],
  ["Tertiary road", "12 276", "685.6"],
  ["Unclassified road", "12 720", "658.4"],
  ["Path", "20 478", "536.4"],
  ["Trunk road", "3 181", "262.2"],
  ["Secondary road", "3 908", "209.4"],
  ["Primary road", "2 675", "177.1"],
  ["Other (cycleway, footway, links, steps)", "3 610", "111.0"],
  ["Total", "256 500", "10 307.5"],
];

// Table 3: people in each walking distance band
const T3: string[][] = [
  ["Under 1 km", "144 730", "5.4", "557 657", "20.8"],
  ["1 to 2 km", "357 474", "13.3", "973 955", "36.3"],
  ["2 to 3 km", "410 346", "15.3", "562 301", "20.9"],
  ["3 to 5 km", "618 873", "23.0", "415 243", "15.5"],
  ["Over 5 km", "1 153 589", "43.0", "175 856", "6.5"],
  ["Total", "2 685 012", "100", "2 685 012", "100"],
];

// Table 4: local authorities
const T4: string[][] = [
  ["Harare", "45", "1 650 227", "1 853", "35.7", "73.3"],
  ["Harare Rural (ward 1)", "1", "395 815", "3 727", "76.6", "98.7"],
  ["Chitungwiza", "25", "410 740", "2 267", "45.8", "86.1"],
  ["Epworth", "7", "228 230", "1 765", "31.8", "100.0"],
  ["Total", "78", "2 685 012", "2 185", "43.0", "81.3"],
];

// Table 5: wards with the largest share beyond 2 km (all mapped facilities)
const T5: string[][] = [
  ["Chitungwiza 1", "9 897", "3 368", "100.0"],
  ["Chitungwiza 2", "11 599", "3 417", "100.0"],
  ["Chitungwiza 3", "11 752", "4 101", "100.0"],
  ["Chitungwiza 4", "33 009", "4 757", "100.0"],
  ["Chitungwiza 5", "9 448", "4 833", "100.0"],
  ["Chitungwiza 6", "39 039", "3 883", "100.0"],
  ["Chitungwiza 7", "7 548", "2 631", "100.0"],
  ["Chitungwiza 8", "9 193", "2 833", "98.7"],
  ["Chitungwiza 20", "11 023", "2 455", "98.5"],
  ["Epworth 4", "41 720", "2 883", "89.7"],
];

// Table 6: greedy choice of new clinic sites
const T6: string[][] = [
  ["1", "St Mary's", "Chitungwiza 6", "85 754", "85 754"],
  ["2", "Southlea Park", "Harare Rural 1", "51 834", "137 588"],
  ["3", "Chinamano", "Epworth 4", "34 163", "171 751"],
  ["4", "Eyestone Park", "Harare Rural 1", "33 895", "205 647"],
  ["5", "Cold Comfort", "Harare 15", "32 970", "238 617"],
  ["6", "St Mary's (east)", "Chitungwiza 2", "30 711", "269 329"],
  ["7", "Budiriro", "Harare 43", "27 453", "296 782"],
  ["8", "Dzivarasekwa", "Harare 40", "26 510", "323 292"],
  ["9", "Glen Forest", "Harare 42", "24 047", "347 340"],
  ["10", "Waterfalls", "Harare 23", "22 126", "369 465"],
];

const SQL1 = `-- Nodes from segment end points, then source and target by edge id
CREATE TABLE vx AS SELECT * FROM pgr_extractVertices('SELECT id, geom FROM edge ORDER BY id');
UPDATE edge e SET source = s.vid FROM (SELECT unnest(out_edges) eid, id vid FROM vx) s WHERE e.id = s.eid;
UPDATE edge e SET target = t.vid FROM (SELECT unnest(in_edges)  eid, id vid FROM vx) t WHERE e.id = t.eid;
-- Keep the largest connected piece of the network
CREATE TABLE comp AS SELECT * FROM pgr_connectedComponents(
  'SELECT id, source, target, cost, cost AS reverse_cost FROM edge');`;

const SQL2 = `-- One shortest-path tree for all facilities: a virtual node 0 is joined to every facility's
-- network node by an edge as long as the facility's snap distance
SELECT d.node, d.pred, d.agg_cost
FROM pgr_drivingDistance(
  'SELECT id, source, target, cost FROM edge
   UNION ALL SELECT 1000000000 + fid, 0, node, snap FROM fac WHERE scen = ''B''',
  0, 30000, false) d;`;

const SQL3 = `-- 2 km walking catchment of every candidate node in one call (catchments may overlap)
CREATE TABLE cand_reach AS
SELECT d.start_vid AS node, d.node AS reached, d.agg_cost
FROM pgr_drivingDistance('SELECT id, source, target, cost FROM edge',
       (SELECT array_agg(DISTINCT node) FROM cand), 2000, false, false) d;`;

const A = ({ href }: { href: string }) => <a href={href} target="_blank" rel="noopener noreferrer">{href}</a>;

export default function HarareHealthAccessCaseStudy() {
  return (
    <>
      <CaseLayout slug="harare-health-access">
        <h1>Network Analysis of Walking Access to Public Health Facilities in Harare Using PostGIS and pgRouting</h1>
        <p className="tc__by">Shortest walks on the street network from every populated 100 m cell to the nearest clinic or hospital, worked out inside a spatial database.</p>
        <p className="tc__by" style={{ marginTop: 10 }}>Kudzanai Chakavarika (13 November 2026)</p>
        <Facts rows={[["Place", "Harare Metropolitan Province"], ["Period", "2025 population, 2026 network"], ["Data", "OpenStreetMap, public facility list, WorldPop, geoBoundaries"], ["Methods", "Network analysis, shortest-path trees (Dijkstra), network catchments, maximal coverage location"], ["Tools", "PostgreSQL, PostGIS, pgRouting, GDAL, Python"]]} />

        <h2>1 Introduction</h2>
        <p>Most people in Harare reach a clinic on foot. How far they must walk depends on where the clinics are and on the streets that lead to them, not on the straight line between the two. A home 1 km from a clinic across a river, a railway or a fenced estate may be a walk of 3 km. Measuring access along the street network gives a truer picture of who lives close to care and who does not (Weiss et al., 2020).</p>
        <p>This study works out the shortest walk from every populated 100 m cell in Harare Metropolitan Province to its nearest clinic or hospital. The whole analysis was done in a PostgreSQL database with the PostGIS spatial extension and the pgRouting network library. The walking network of 10 300 km of streets and paths was built from OpenStreetMap, the population came from WorldPop and two sets of facilities were compared: the public facilities on a published list and every clinic and hospital mapped in OpenStreetMap. The same database was then used to find the places where a new clinic would bring the most people within a 2 km walk.</p>

        <h2>2 Objectives</h2>
        <ol>
          <li>To build a routable walking network for Harare from OpenStreetMap in PostGIS and pgRouting.</li>
          <li>To measure the shortest walking distance from every populated cell to the nearest health facility for two sets of facilities.</li>
          <li>To analyse how walking distance varies across the province, its local authorities and its wards.</li>
          <li>To assess the number of people served by each facility through its network catchment.</li>
          <li>To identify candidate sites where new clinics would bring the most people within a 2 km walk.</li>
        </ol>

        <h2>3 Study area</h2>
        <p>Harare Metropolitan Province covers 940 km² in north-eastern Zimbabwe (Map 1). It holds four local authorities: the City of Harare, the dormitory town of Chitungwiza to the south, the informal and peri-urban settlement of Epworth to the south-east, and one large rural ward to the south-west that is filling with new housing schemes such as Southlea Park and Caledonia. The province had about 2.43 million people at the 2022 census (ZIMSTAT, 2022) and WorldPop places 2.69 million there in 2025.</p>
        <p>The City of Harare runs 12 polyclinics, 7 primary care clinics and 2 infectious diseases hospitals (City of Harare, 2026). Government central hospitals, mission, mine and private clinics add to these. The low-density northern suburbs are served largely by private practices, while the high-density south and west depend on the council clinics.</p>
        <Fig src={map1} cap="Map 1. Study Area and Health Facilities." />

        <h2>4 Data and methods</h2>
        <p className="tc__cap">Table 1. Data used in the study</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Dataset</th><th>Type</th><th>Date</th><th>Used for</th></tr></thead>
            <tbody><Rows rows={T1} num={9} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: OpenStreetMap contributors (2026); Maina et al. (2019); WorldPop (2025); Runfola et al. (2020). All layers were loaded into PostGIS with GDAL (ogr2ogr and raster2pgsql) and stored in UTM zone 36S so that lengths are in metres.</p>

        <h3>Walking network</h3>
        <p>Every OpenStreetMap way that a person can walk on was kept, from trunk roads to footpaths and tracks. Motorways and ways that are planned or under construction were left out. Ways were kept if they touch the province or a 2 km margin around it, so that a walk may leave the boundary briefly. Each way was split into its single segments with ST_DumpSegments, so that every shared vertex where two ways meet becomes a junction. The cost of a segment is its length in metres and walks may go either way along it.</p>
        <p>Network nodes were made with pgr_extractVertices, which merges identical end points and lists the edges that leave and enter each node, so the source and target of every edge could be set by edge id. pgr_connectedComponents then split the network into its connected pieces. The largest piece holds 234 838 of the 236 018 nodes. The other 93 pieces are mostly short driveways and paths not joined to a street, and they were dropped so that no cell or facility could be stranded on one.</p>
        <Sql>{SQL1}</Sql>
        <p className="tc__cap">Table 2. Walking network by OpenStreetMap class</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Class</th><th className="n">Segments</th><th className="n">Length (km)</th></tr></thead>
            <tbody><Rows rows={T2} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study; OpenStreetMap contributors (2026). Residential streets make up just over half of the network.</p>

        <h3>Health facilities in two scenarios</h3>
        <p>Scenario A uses the 27 public facilities in the province on the master list of Maina et al. (2019), 24 clinics and 3 hospitals. Scenario B uses every clinic and hospital mapped in OpenStreetMap, 84 clinics and 21 hospitals. Pharmacies, dentists, laboratories and opticians were left out. A facility drawn as a point within 50 m of the same facility drawn as an outline was counted once, as were two points within 50 m of each other. Scenario A is the core public network on a fixed list. Scenario B is closer to all the care on the ground, public, mission and private, but it is only as complete as the mapping.</p>

        <h3>Population as demand points</h3>
        <p>Each populated 100 m cell of the WorldPop 2025 constrained grid was turned into a point with ST_PixelAsCentroids. That gives 101 890 cells holding 2 685 012 people. Each cell and each facility was joined to its nearest network node with a KNN search (the &lt;-&gt; operator on a spatial index). The median cell is 50.5 m from a node and the median facility 38.7 m. The walk from a cell is the straight line to its node, plus the network distance, plus the line from the facility's node to the facility.</p>

        <h3>Shortest walk to the nearest facility</h3>
        <p>pgRouting finds shortest paths with Dijkstra's algorithm (Dijkstra, 1959). Rather than routing from each of the 101 890 cells, one shortest-path tree was grown per scenario from a virtual source node joined to every facility, with pgr_drivingDistance. The cost of each joining edge is the facility's snap distance. The distance from the virtual source to any node is then the walk to the nearest facility and following each node's predecessor back up the tree gives the facility that serves it. The walk was capped at 30 km, which no cell reached.</p>
        <Sql>{SQL2}</Sql>
        <p>The people in each cell were then given to the facility that serves it, which forms a network catchment for every facility. The share of people within 1, 2, 3 and 5 km was summed for the province, each local authority and each ward. A 2 km walk, about 25 minutes, was used as the main measure of good access in a city. The 5 km figure often quoted in Zimbabwe was also reported, though it was set for rural areas.</p>

        <h3>Candidate sites for new clinics</h3>
        <p>The people more than 2 km from any facility in scenario B were grouped into 1 km squares. For each square holding at least 500 such people, the network node nearest to its population-weighted centre became a candidate site, which gave 461 candidates. The 2 km walking catchment of every candidate was found in one multi-source pgr_drivingDistance call. Sites were then chosen one at a time by the greedy method for the maximal covering location problem (Church and ReVelle, 1974): each pick is the candidate that brings the most people not yet covered within 2 km.</p>
        <Sql>{SQL3}</Sql>

        <h2>5 Results</h2>
        <h3>Walking distance to the nearest facility</h3>
        <p>With all mapped clinics and hospitals the population-weighted mean walk is 2.19 km and the median 1.78 km (Map 2). 57.0 % of people live within 2 km of a facility and 93.5 % within 5 km (Table 3, Figure 1). The short walks lie in the older high-density suburbs of the south and west, such as Mbare, Highfield, Glen View, Budiriro and Kuwadzana, and in the city centre, where clinics are a few streets apart. The long walks lie on the growing edges of the city: the new schemes in Harare Rural ward 1, the north-western farms around Hopley, Hatcliffe in the north and the north of Chitungwiza. 175 856 people (6.5 %) walk more than 5 km.</p>
        <Fig src={map2} cap="Map 2. Walking Distance to the Nearest Mapped Facility (scenario B)." />
        <p>With only the 27 listed public facilities the picture is very different (Map 3). The mean walk rises to 4.96 km and the median to 4.15 km. Only 18.7 % of people live within 2 km and 43.0 % walk more than 5 km. Each listed facility serves a wide area, so green rings appear only around the council clinics and the hospitals, and most of Chitungwiza, Epworth and the southern edge lie beyond 5 km.</p>
        <Fig src={map3} cap="Map 3. Walking Distance to the Nearest Listed Public Facility (scenario A)." />
        <p className="tc__cap">Table 3. People in each walking distance band</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Walking distance</th><th className="n">People, A</th><th className="n">Share A (%)</th><th className="n">People, B</th><th className="n">Share B (%)</th></tr></thead>
            <tbody><Rows rows={T3} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. A: 27 listed public facilities (Maina et al., 2019). B: 105 clinics and hospitals mapped in OpenStreetMap.</p>
        <Fig src={fig1} cap="Figure 1. Share of people in each walking distance band, scenarios A and B." />
        <Fig src={fig2} cap="Figure 2. Cumulative share of people within a given walking distance, scenarios A and B. Dashed lines mark 2 km and 5 km." />

        <h3>Network distance against straight-line distance</h3>
        <p>Walks are on average 1.48 times the straight-line distance to the nearest facility in scenario B and 1.39 times in scenario A. Measured in a straight line, 77.1 % of people would appear to be within 2 km of a mapped facility, against 57.0 % along the network. For 12.7 % of people the facility nearest by the network is not the one nearest in a straight line, because a river, railway, wetland or closed estate lies between. No walk was shorter than its straight line, which is a basic check on the network.</p>

        <h3>Local authorities and wards</h3>
        <p>Access is poorest in Harare Rural ward 1, where 76.6 % of the 395 815 people walk more than 2 km even to the nearest mapped facility (Table 4, Map 4). Chitungwiza follows with 45.8 %. In the City of Harare the share is 35.7 % and in Epworth 31.8 %. Eleven wards have more than 80 % of their people beyond 2 km. Seven of them, Chitungwiza wards 1 to 7 in the north of the town, have no one within 2 km (Table 5). Eleven wards, most of them in the inner high-density suburbs, have everyone within 2 km.</p>
        <p className="tc__cap">Table 4. Walking access by local authority</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Local authority</th><th className="n">Wards</th><th className="n">People</th><th className="n">Mean walk, B (m)</th><th className="n">Over 2 km, B (%)</th><th className="n">Over 2 km, A (%)</th></tr></thead>
            <tbody><Rows rows={T4} num={1} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. Means and shares are weighted by population.</p>
        <Fig src={map4} cap="Map 4. People More Than 2 km from a Facility, by Ward (scenario B)." />
        <p className="tc__cap">Table 5. Wards with the largest share of people more than 2 km from a mapped facility</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Ward</th><th className="n">People</th><th className="n">Mean walk, B (m)</th><th className="n">Over 2 km, B (%)</th></tr></thead>
            <tbody><Rows rows={T5} num={1} /></tbody>
          </table>
        </div>

        <h3>People served by each facility</h3>
        <p>Network catchments differ greatly in size (Map 5, Figure 3). In scenario B the median facility is the nearest one for 13 545 people, but the largest catchments hold more than 100 000. Grace Family Clinic, the nearest mapped clinic for most of the new housing in Harare Rural ward 1, has 159 382 people in its catchment. Kuwadzana Polyclinic, Hopley Satellite Clinic, Overspill Clinic in Epworth and Chidodo Clinic in Chitungwiza each have more than 100 000. Many clinics in the northern suburbs serve fewer than 5 000. In scenario A the median listed facility serves 40 706 people and Chitungwiza Central Hospital, the only listed facility in Chitungwiza, serves 462 857.</p>
        <Fig src={map5} cap="Map 5. People Served by Each Facility Catchment (scenario B)." />
        <Fig src={fig3} cap="Figure 3. People in the walking catchment of each mapped facility, largest first (scenario B)." />

        <h3>Candidate sites for new clinics</h3>
        <p>1 153 399 people live more than 2 km from a mapped facility. Five new clinics placed by the greedy method would bring 238 617 of them within 2 km (20.7 %) and ten would bring 369 465 (32.0 %) (Table 6, Map 6, Figure 4). This would raise the share of the province within 2 km from 57.0 % to 65.9 % with five clinics and to 70.8 % with ten. The first site, near St Mary's in the north of Chitungwiza, adds 85 754 people on its own. The next picks lie in Southlea Park, at Chinamano in Epworth, at Eyestone Park and at Cold Comfort. The gain falls with each pick, from 85 754 for the first to 22 126 for the tenth.</p>
        <p className="tc__cap">Table 6. Candidate sites chosen by greedy maximal coverage</p>
        <div className="tc__tw">
          <table>
            <thead><tr><th>Site</th><th>Nearest place</th><th>Ward</th><th className="n">People added</th><th className="n">Running total</th></tr></thead>
            <tbody><Rows rows={T6} num={3} /></tbody>
          </table>
        </div>
        <p className="tc__src">Source: this study. People added are those more than 2 km from any mapped facility today who would be within a 2 km walk of the new site and of no earlier pick.</p>
        <Fig src={map6} cap="Map 6. Candidate Sites for Five New Clinics and the people each would bring within 2 km." />
        <Fig src={fig4} cap="Figure 4. People brought within 2 km by each new clinic and the running total, in order of choice." />

        <h2>6 Discussion</h2>
        <p>The gap between the two scenarios shows how much Harare relies on care outside the core public list. On the 27 listed public facilities alone, four in ten people would walk more than 5 km. Mission, private and newer council clinics shorten most walks to under 2 km, but private clinics charge fees that many households in the high-density suburbs cannot meet, so scenario B gives the better picture of distance and scenario A of affordable care. True access for the poorest households probably lies between the two.</p>
        <p>The long walks follow the growth of the city. Southlea Park, Caledonia, Hopley, Hatcliffe and the edges of Epworth have filled with people faster than clinics were built, and the largest catchments in Map 5 lie there. The results for northern Chitungwiza and parts of Epworth need care, however. OpenStreetMap holds only five clinics and three hospitals in Chitungwiza and three clinics in Epworth, fewer than the council and mission clinics known to exist, so some of these wards are probably better served than the map shows. The candidate sites should be read as places to check on the ground before any decision, not as final locations.</p>
        <p>The method has other limits. Walks are measured on mapped ways only, so short cuts across open land are missed and some walks are too long, while busy roads and unsafe crossings are treated as easy to walk. Distance is not time: slope, heat and the wait at the clinic are not counted. The nearest facility is not always the one people use, since services, fees, hours and staff differ. WorldPop spreads people over mapped buildings with a model, not a count, and its 2025 total is higher than the 2022 census. The facility list of Maina et al. (2019) is now several years old.</p>
        <p>The database approach worked well for a task of this size. One shortest-path tree per scenario replaced more than 100 000 separate searches and the whole chain, from loading the data to the candidate sites, runs again in about 13 minutes. Because every step is a SQL script, the analysis can be rerun when OpenStreetMap is updated or a new clinic opens.</p>

        <h2>7 Recommendations</h2>
        <ol>
          <li>Check the facility record in northern Chitungwiza, Epworth and Harare Rural ward 1 with the councils and the Ministry of Health and Child Care, and add missing clinics to OpenStreetMap so that analyses such as this one are complete.</li>
          <li>Give priority for new clinics or outreach points to the areas around the first five candidate sites, after the facility record there has been checked.</li>
          <li>Plan a clinic as part of each new housing scheme on the edge of the city, before the people arrive.</li>
          <li>Repeat the analysis with walking time, including slope and road crossings, and with fee-free public facilities only.</li>
        </ol>

        <h2>8 Conclusion</h2>
        <p>A walking network of 10 300 km was built from OpenStreetMap in PostGIS and pgRouting and the shortest walk was worked out for 2.69 million people in Harare Metropolitan Province. With all 105 mapped clinics and hospitals, 57.0 % of people live within 2 km and the median walk is 1.78 km. With only the 27 listed public facilities, 18.7 % live within 2 km and 43.0 % walk more than 5 km. Walks are about 1.5 times the straight-line distance. The longest walks lie in the new housing of Harare Rural ward 1, northern Chitungwiza and Epworth. Five well-placed clinics would bring about 239 000 more people within 2 km, once the gaps in the facility record have been checked on the ground.</p>

        <h2>References</h2>
        <div className="tc__ref">
          <p>Church, R. and ReVelle, C. (1974) The maximal covering location problem. Papers of the Regional Science Association, 32, 101-118. <A href="https://doi.org/10.1007/BF01942293" /></p>
          <p>City of Harare (2026) Health services. Harare City Council. <A href="https://www.hararecity.co.zw" /></p>
          <p>Dijkstra, E.W. (1959) A note on two problems in connexion with graphs. Numerische Mathematik, 1, 269-271. <A href="https://doi.org/10.1007/BF01386390" /></p>
          <p>Maina, J., Ouma, P.O., Macharia, P.M., Alegana, V.A. et al. (2019) A spatial database of health facilities managed by the public health sector in sub Saharan Africa. Scientific Data, 6, 134. <A href="https://doi.org/10.1038/s41597-019-0142-2" /></p>
          <p>OpenStreetMap contributors (2026) OpenStreetMap data for Zimbabwe, extract by Geofabrik. <A href="https://download.geofabrik.de/africa/zimbabwe.html" /></p>
          <p>pgRouting contributors (2024) pgRouting 3.6. <A href="https://pgrouting.org" /></p>
          <p>PostGIS Project Steering Committee (2024) PostGIS 3.4. <A href="https://postgis.net" /></p>
          <p>Runfola, D., Anderson, A., Baier, H., Crittenden, M. et al. (2020) geoBoundaries: a global database of political administrative boundaries. PLoS ONE, 15(4), e0231866. <A href="https://doi.org/10.1371/journal.pone.0231866" /></p>
          <p>Weiss, D.J., Nelson, A., Vargas-Ruiz, C.A., Gligorić, K. et al. (2020) Global maps of travel time to healthcare facilities. Nature Medicine, 26, 1835-1838. <A href="https://doi.org/10.1038/s41591-020-1059-1" /></p>
          <p>WorldPop (2025) Global 2 population counts 2015 to 2030, 100 m, R2025A. School of Geography and Environmental Science, University of Southampton. <A href="https://doi.org/10.5258/SOTON/WP00839" /></p>
          <p>ZIMSTAT (2022) 2022 Population and Housing Census: preliminary report on population figures. Zimbabwe National Statistics Agency, Harare. <A href="https://www.zimstat.co.zw" /></p>
        </div>
      </CaseLayout>
    </>
  );
}
