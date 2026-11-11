# Elephant tracks: data

    python fetch.py    # Movebank Data Repository files into cache/ (resumes, the server drops connections)
    python build.py    # writes public/webmaps/elephants/{etosha,kruger}.{bin,jpg} and parks.json

Etosha: Tsalyuk et al. 2018, CC BY-NC 4.0 (fence outline comes with the data).
Kruger: Thaker et al. 2019, CC0 (park outline from WDPA through Earth Engine).
Backdrops are Sentinel-2 dry season 2022 medians from Earth Engine project directed-sun-490915-m4.
Delete a .jpg in public/webmaps/elephants to fetch it again.
