#!/bin/sh
# Load the raw inputs into the local PostGIS database "harare" (port 5433, started by pg_ctl; see VERIFICATION.md).
# ogr2ogr writes each layer as SQL (PGDump driver) and psql runs it. All layers are stored in WGS 84 / UTM zone 36S
# (EPSG:32736) so that lengths and areas are in metres.
set -e -o pipefail
export MSYS_NO_PATHCONV=1                            # stop Git Bash rewriting /vsistdout/
B="/c/Program Files/PostgreSQL/16/bin"
BB="30.80 -18.12 31.30 -17.60"                      # Harare Metropolitan Province plus a small margin
SQL() { "$B/psql" -q -v ON_ERROR_STOP=1 -p 5433 -U gis -d harare; }
LOAD() { name=$1; shift; "$B/ogr2ogr" -f PGDump /vsistdout/ -nln $name -lco GEOMETRY_NAME=geom -lco FID=id -lco DROP_TABLE=IF_EXISTS \
         -lco CREATE_SCHEMA=OFF -t_srs EPSG:32736 "$@" | SQL; echo "loaded $name"; }

LOAD province dl/gb/zwe_adm1.geojson -nlt MULTIPOLYGON -where "shapeName = 'Harare'"
LOAD ward_all dl/gb/zwe_adm3.geojson -nlt MULTIPOLYGON -spat $BB
LOAD osm_lines dl/osm/zimbabwe.osm.pbf lines -nlt MULTILINESTRING -spat $BB -where "highway IS NOT NULL" -select highway,name,osm_id
LOAD osm_hpts dl/osm/zimbabwe.osm.pbf points -spat $BB -select name,osm_id,other_tags \
    -where "other_tags LIKE '%\"amenity\"=>\"clinic\"%' OR other_tags LIKE '%\"amenity\"=>\"hospital\"%' OR other_tags LIKE '%\"healthcare\"=>%'"
LOAD osm_hpoly dl/osm/zimbabwe.osm.pbf multipolygons -nlt MULTIPOLYGON -spat $BB -select name,amenity,osm_id,osm_way_id,other_tags \
    -where "amenity IN ('clinic','hospital') OR other_tags LIKE '%\"healthcare\"=>%'"
LOAD mfl data/mfl_harare.csv -s_srs EPSG:4326 -oo X_POSSIBLE_NAMES=Long -oo Y_POSSIBLE_NAMES=Lat -oo KEEP_GEOM_COLUMNS=NO -nlt POINT
# Population: WorldPop 2025 constrained 100 m (clipped by clip_pop in VERIFICATION.md), loaded as a raster
"$B/raster2pgsql" -d -s 4326 -t 100x100 -I data/pop_harare.tif pop_rast | SQL; echo "loaded pop_rast"
# Place names (suburbs and towns) for map labels and for naming wards in the text
LOAD osm_place dl/osm/zimbabwe.osm.pbf points -spat $BB -select name,place,osm_id -where "place IN ('suburb','town','city','neighbourhood','village')"
