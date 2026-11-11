# Languages of Southern Africa: data

    python build.py    # writes public/webmaps/languages/languages.json and audio/

Glottolog CLDF files go in cache/ (languages.csv, values.csv from github.com/glottolog/glottolog-cldf).
Speaker numbers come from Wikidata and recordings from Lingua Libre on Wikimedia Commons; both are cached.
Commons rate-limits downloads, so the build waits between clips. Countries and lakes come from ../corridors/raw.
