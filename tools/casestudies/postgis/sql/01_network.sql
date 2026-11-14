-- 01_network.sql: study area, wards, health facilities and the walking network (pgRouting topology).
\timing off
-- Study area and wards (the 78 wards whose interior point lies in Harare Metropolitan Province)
DROP TABLE IF EXISTS ward;
CREATE TABLE ward AS
SELECT row_number() OVER (ORDER BY w.shapename)::int AS wid, w.shapename AS name, w.geom
FROM ward_all w, province p WHERE ST_Within(ST_PointOnSurface(w.geom), p.geom);
CREATE INDEX ON ward USING gist (geom);

-- Facilities. Scenario B: every OSM clinic and hospital (pharmacies, dentists, doctors' rooms, labs excluded).
-- A point that lies within 50 m of a mapped facility polygon is the same facility and is dropped.
DROP TABLE IF EXISTS fac;
CREATE TABLE fac AS
WITH poly AS (
  SELECT 'w' || coalesce(osm_way_id, osm_id) AS src, name,
         coalesce(amenity, substring(other_tags from '"amenity"=>"([^"]+)"')) AS am,
         substring(other_tags from '"healthcare"=>"([^"]+)"') AS hc, ST_PointOnSurface(geom) AS geom, geom AS shape
  FROM osm_hpoly),
pts AS (
  SELECT 'n' || osm_id AS src, name, substring(other_tags from '"amenity"=>"([^"]+)"') AS am,
         substring(other_tags from '"healthcare"=>"([^"]+)"') AS hc, geom
  FROM osm_hpts h
  WHERE NOT EXISTS (SELECT 1 FROM osm_hpoly q WHERE ST_DWithin(h.geom, q.geom, 50))),
allf AS (SELECT src, name, am, hc, geom FROM poly UNION ALL SELECT src, name, am, hc, geom FROM pts)
SELECT row_number() OVER (ORDER BY src)::int AS fid, 'B'::text AS scen, src, name,
       CASE WHEN am = 'hospital' OR hc = 'hospital' THEN 'Hospital' ELSE 'Clinic' END AS kind, a.geom
FROM allf a, province p
WHERE ST_Within(a.geom, p.geom)
  AND (am IN ('clinic', 'hospital') OR hc IN ('clinic', 'hospital', 'birthing_centre'))
  AND coalesce(hc, '') NOT IN ('pharmacy', 'dentist', 'laboratory', 'optometrist');
-- Facilities mapped twice (or two tags at one site) within 50 m are one site: keep the hospital, else the lower id
DELETE FROM fac a USING fac b
WHERE a.scen = 'B' AND b.scen = 'B' AND a.fid <> b.fid AND ST_DWithin(a.geom, b.geom, 50)
  AND (b.kind = 'Hospital' AND a.kind = 'Clinic' OR a.kind = b.kind AND b.fid < a.fid);
-- Scenario A: the public facilities of the Maina et al. (2019) master facility list
INSERT INTO fac
SELECT 1000 + m.id, 'A', 'mfl' || m.id, m.name,
       CASE WHEN m.ftype ILIKE '%hospital%' THEN 'Hospital' ELSE 'Clinic' END, m.geom
FROM mfl m, province p WHERE ST_Within(m.geom, p.geom);
CREATE INDEX ON fac USING gist (geom);

-- Walking network: all OSM ways a person can walk on (motorway-class and unbuilt ways excluded),
-- split into single segments so that every junction drawn as a shared vertex becomes a node.
-- Only ways that touch the province plus a 2 km margin are kept (so walks may leave the boundary briefly);
-- the margin polygon is subdivided so the spatial index can do the work.
DROP TABLE IF EXISTS margin;
CREATE TABLE margin AS SELECT ST_Subdivide(ST_Buffer(geom, 2000), 64) AS geom FROM province;
CREATE INDEX ON margin USING gist (geom);
CREATE INDEX IF NOT EXISTS osm_lines_gix ON osm_lines USING gist (geom);
DROP TABLE IF EXISTS edge;
CREATE TABLE edge AS
SELECT row_number() OVER ()::bigint AS id, l.highway, (d).geom AS geom
FROM (SELECT highway, ST_DumpSegments(ST_Force2D(geom)) AS d FROM osm_lines o
      WHERE highway NOT IN ('motorway', 'motorway_link', 'construction', 'proposed', 'raceway', 'bus_guideway', 'platform', 'corridor')
        AND EXISTS (SELECT 1 FROM margin m WHERE ST_Intersects(o.geom, m.geom))) l;
ALTER TABLE edge ADD PRIMARY KEY (id), ADD COLUMN source bigint, ADD COLUMN target bigint, ADD COLUMN cost float8;
UPDATE edge SET cost = ST_Length(geom);

-- pgr_extractVertices merges identical end points into one vertex and lists the edges leaving (out_edges)
-- and entering (in_edges) it, so source and target are set by edge id rather than by a geometry join.
DROP TABLE IF EXISTS vx;
CREATE TABLE vx AS SELECT * FROM pgr_extractVertices('SELECT id, geom FROM edge ORDER BY id');
DROP TABLE IF EXISTS vert;
CREATE TABLE vert AS SELECT id, geom FROM vx;
ALTER TABLE vert ADD PRIMARY KEY (id);
CREATE INDEX ON vert USING gist (geom);
CREATE TEMP TABLE es AS SELECT unnest(out_edges) AS eid, id AS vid FROM vx;
CREATE TEMP TABLE et AS SELECT unnest(in_edges) AS eid, id AS vid FROM vx;
UPDATE edge e SET source = s.vid FROM es s WHERE e.id = s.eid;
UPDATE edge e SET target = t.vid FROM et t WHERE e.id = t.eid;
CREATE INDEX ON edge (source); CREATE INDEX ON edge (target);

-- Connected components: keep only the main walking network (small islands are mostly unjoined driveways)
DROP TABLE IF EXISTS comp;
CREATE TABLE comp AS SELECT * FROM pgr_connectedComponents('SELECT id, source, target, cost, cost AS reverse_cost FROM edge');
ALTER TABLE vert ADD COLUMN comp bigint;
UPDATE vert v SET comp = c.component FROM comp c WHERE c.node = v.id;
DROP TABLE IF EXISTS main_comp;
CREATE TABLE main_comp AS SELECT comp FROM vert GROUP BY comp ORDER BY count(*) DESC LIMIT 1;
DROP TABLE IF EXISTS vmain;
CREATE TABLE vmain AS SELECT v.id, v.geom FROM vert v, main_comp m WHERE v.comp = m.comp;
ALTER TABLE vmain ADD PRIMARY KEY (id); CREATE INDEX ON vmain USING gist (geom);

-- Each facility enters the network at its nearest main-network node (KNN)
ALTER TABLE fac ADD COLUMN node bigint, ADD COLUMN snap float8;
UPDATE fac f SET node = n.id, snap = n.d
FROM fac f2 CROSS JOIN LATERAL (SELECT v.id, ST_Distance(v.geom, f2.geom) d FROM vmain v ORDER BY v.geom <-> f2.geom LIMIT 1) n
WHERE f.fid = f2.fid;
