# Zimbabwe's lost trees: data

    python build.py    # writes public/webmaps/forestloss/lossyear.png and forest.json

Hansen Global Forest Change v1.13 and FAO GAUL 2025 provinces, through Earth Engine project
directed-sun-490915-m4. The 300 m display grid and the 30 m province statistics are cached in cache/;
delete them to recompute. Statistics run one province per request, because one request for the whole
country runs out of time.
