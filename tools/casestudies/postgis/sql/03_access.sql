-- 03_access.sql: walking distance from every populated cell to its nearest facility, scenarios A and B.
-- One shortest-path tree per scenario from a virtual source (node 0) joined to each facility's network node by an
-- edge whose cost is the facility's snap distance. agg_cost is then the walk from the facility door to each node,
-- and following pred back to node 0 gives the facility that serves the node (nearest by network).
CREATE OR REPLACE FUNCTION tree(sc text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM reach WHERE scen = sc;
  INSERT INTO reach (scen, node, pred, agg_cost)
  SELECT sc, d.node, d.pred, d.agg_cost
  FROM pgr_drivingDistance(format(
        'SELECT id, source, target, cost FROM edge
         UNION ALL SELECT 1000000000 + fid, 0, node, snap FROM fac WHERE scen = %L', sc),
        0, 30000, false) d;
  -- facility for each node: walk the tree down from the facility nodes (children of node 0)
  WITH RECURSIVE t AS (
    SELECT r.node, f.fid FROM reach r
    JOIN LATERAL (SELECT fid FROM fac WHERE scen = sc AND node = r.node ORDER BY snap LIMIT 1) f ON true
    WHERE r.scen = sc AND r.pred = 0
    UNION ALL
    SELECT r.node, t.fid FROM reach r JOIN t ON r.pred = t.node WHERE r.scen = sc AND r.node <> 0)
  UPDATE reach r SET fid = t.fid FROM t WHERE r.scen = sc AND r.node = t.node;
END $$;

DROP TABLE IF EXISTS reach;
CREATE TABLE reach (scen text, node bigint, pred bigint, agg_cost float8, fid int);
CREATE INDEX ON reach (scen, pred); CREATE INDEX ON reach (scen, node);
SELECT tree('A');
SELECT tree('B');

-- Per cell and scenario: serving facility and total walking distance (cell to node + node to facility door), metres
DROP TABLE IF EXISTS acc;
CREATE TABLE acc AS
SELECT s.scen, c.cid, c.wid, c.pop, r.fid, c.snap + r.agg_cost AS dist
FROM cell c CROSS JOIN (VALUES ('A'), ('B')) s(scen)
JOIN reach r ON r.scen = s.scen AND r.node = c.node;
CREATE INDEX ON acc (scen, cid);
