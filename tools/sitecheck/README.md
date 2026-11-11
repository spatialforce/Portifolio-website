# Where to open next: data

Builds `public/webmaps/sites/harare.json` for `public/webmaps/sites.html`.

    pip install --target vendor osmium duckdb      # once
    # raw/: zimbabwe.osm.pbf (Geofabrik), zwe_pop_2020.tif (WorldPop),
    #       zwe_ADM1.geojson and zwe_ADM3.geojson (geoBoundaries)
    python extract.py harare      # OpenStreetMap outlets
    python places.py harare       # Overture Maps outlets, saved as cache/harare/overture_all.parquet
    python analyse.py harare

Checks built into analyse.py: WorldPop is compared with the 2022 census for the province
(Harare 2,401,567 against 2,427,209). Outlet lists from OpenStreetMap and Overture are merged
and reported as "listed" outlets because neither is complete.
