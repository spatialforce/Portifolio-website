# Migration atlas data

Builds the files in `public/webmaps/migration/` used by `public/webmaps/migration.html`.

    python fetch.py    # GBIF monthly grids, cached in cache/ and grids/ (slow the first time)
    python geo.py      # coastlines (Natural Earth 1:50m)
    python borders.py  # country borders (Natural Earth 1:50m)
    python photos.py   # species photos and credits from Wikimedia Commons
    python build.py    # reporting rate atlases and atlas.json

To add a species, add it to `species.py` and run all four again. Only the new species is downloaded.
