-- 04_sites.sql: candidate sites for new clinics (scenario B, all mapped facilities).
-- Demand: people whose walk to the nearest facility is longer than 2 km.
-- Candidates: for every 1 km grid square holding at least 500 such people, the main-network node nearest to the
-- population-weighted centre of that square. Each candidate's 2 km walking catchment is found with one
-- multi-source pgr_drivingDistance call (equicost off, so catchments may overlap); the greedy choice is made in analysis.py.
DROP TABLE IF EXISTS cand;
CREATE TABLE cand AS
WITH far AS (
  SELECT c.cid, c.pop, c.geom, floor(ST_X(c.geom) / 1000) gx, floor(ST_Y(c.geom) / 1000) gy
  FROM cell c JOIN acc a ON a.cid = c.cid AND a.scen = 'B' WHERE a.dist > 2000),
sq AS (
  SELECT gx, gy, sum(pop) pop,
         ST_SetSRID(ST_MakePoint(sum(ST_X(geom) * pop) / sum(pop), sum(ST_Y(geom) * pop) / sum(pop)), 32736) g
  FROM far GROUP BY gx, gy HAVING sum(pop) >= 500)
SELECT row_number() OVER (ORDER BY gx, gy)::int AS kid, sq.pop AS sqpop, n.id AS node, n.geom
FROM sq CROSS JOIN LATERAL (SELECT id, geom FROM vmain v ORDER BY v.geom <-> sq.g LIMIT 1) n;

DROP TABLE IF EXISTS cand_reach;
CREATE TABLE cand_reach AS
SELECT d.start_vid AS node, d.node AS reached, d.agg_cost
FROM pgr_drivingDistance('SELECT id, source, target, cost FROM edge',
       (SELECT array_agg(DISTINCT node) FROM cand), 2000, false, false) d;
CREATE INDEX ON cand_reach (reached);

-- People each candidate would bring within 2 km (cell snap counted), as cid lists for the greedy step
DROP TABLE IF EXISTS cand_cover;
CREATE TABLE cand_cover AS
SELECT k.kid, c.cid, c.pop
FROM cand k JOIN cand_reach r ON r.node = k.node
JOIN cell c ON c.node = r.reached
JOIN acc a ON a.cid = c.cid AND a.scen = 'B'
WHERE a.dist > 2000 AND r.agg_cost + c.snap <= 2000;
