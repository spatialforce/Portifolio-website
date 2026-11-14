-- 02_cells.sql: demand points (populated 100 m cells), snapped to the walking network.
-- Walking distance = cell centre to nearest network node (straight line) + network distance + node to facility.

-- Demand points: WorldPop 2025 constrained cells inside the province, as centroids in UTM 36S
DROP TABLE IF EXISTS cell;
CREATE TABLE cell AS
SELECT row_number() OVER ()::int AS cid, c.val::float8 AS pop, ST_Transform(c.geom, 32736) AS geom
FROM pop_rast r, LATERAL ST_PixelAsCentroids(r.rast, 1, true) c
WHERE c.val > 0;
CREATE INDEX ON cell USING gist (geom);
DROP TABLE IF EXISTS prov_sub;
CREATE TABLE prov_sub AS SELECT ST_Subdivide(geom, 64) AS geom FROM province;
CREATE INDEX ON prov_sub USING gist (geom);
DELETE FROM cell c WHERE NOT EXISTS (SELECT 1 FROM prov_sub p WHERE ST_Intersects(c.geom, p.geom));
ALTER TABLE cell ADD PRIMARY KEY (cid), ADD COLUMN node bigint, ADD COLUMN snap float8, ADD COLUMN wid int;
UPDATE cell c SET node = n.id, snap = n.d
FROM cell c2 CROSS JOIN LATERAL (SELECT v.id, ST_Distance(v.geom, c2.geom) d FROM vmain v ORDER BY v.geom <-> c2.geom LIMIT 1) n
WHERE c.cid = c2.cid;
UPDATE cell c SET wid = w.wid FROM ward w WHERE ST_Within(c.geom, w.geom);

