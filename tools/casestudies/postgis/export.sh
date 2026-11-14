#!/bin/sh
# Export the PostGIS results to CSV (geometry as WKT) for analysis.py, maps.py and graphs.py.
set -e -o pipefail
export MSYS_NO_PATHCONV=1
B="/c/Program Files/PostgreSQL/16/bin"; mkdir -p exp
Q() { "$B/psql" -q -v ON_ERROR_STOP=1 -p 5433 -U gis -d harare -c "\copy ($2) to 'exp/$1.csv' csv header"; echo "exported $1"; }
Q cell "select c.cid, round(st_x(st_transform(c.geom,4326))::numeric,6) lon, round(st_y(st_transform(c.geom,4326))::numeric,6) lat,
        c.pop, c.wid, a.dist dista, a.fid fida, b.dist distb, b.fid fidb
        from cell c join acc a on a.cid=c.cid and a.scen='A' join acc b on b.cid=c.cid and b.scen='B' order by c.cid"
Q fac "select fid, scen, src, name, kind, round(snap::numeric,1) snap, st_x(geom) x, st_y(geom) y from fac order by fid"
Q ward "select wid, name, round((st_area(geom)/1e6)::numeric,3) km2, st_astext(st_simplifypreservetopology(geom,20)) wkt from ward order by wid"
Q province "select round((st_area(geom)/1e6)::numeric,2) km2, st_astext(st_simplifypreservetopology(geom,20)) wkt from province"
Q roads "select highway, st_astext(st_simplify(geom,10)) wkt from osm_lines o
        where highway in ('trunk','primary','secondary','tertiary') and exists (select 1 from margin m where st_intersects(o.geom,m.geom))"
Q netlen "select highway, count(*) segs, round((sum(cost)/1000)::numeric,1) km from edge group by 1 order by 3 desc"
Q cand "select kid, node, round(sqpop::numeric) sqpop, st_x(geom) x, st_y(geom) y from cand order by kid"
Q cover "select kid, cid from cand_cover order by kid, cid"
Q netstat "select (select count(*) from edge) edges, (select round((sum(cost)/1000)::numeric,1) from edge) km,
        (select count(*) from vert) verts, (select count(*) from vmain) vmain, (select count(distinct comp) from vert) comps,
        (select round(max(snap)::numeric) from cell) cell_snap_max,
        (select round((percentile_cont(0.5) within group (order by snap))::numeric,1) from cell) cell_snap_med"
Q place "select name, place, st_x(p.geom) x, st_y(p.geom) y from osm_place p, province v where st_within(p.geom, v.geom) and name is not null"
