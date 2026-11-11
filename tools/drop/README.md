# One drop of rain: data

    # needs tools/rivers/raw (HydroRIVERS, Natural Earth) and raw/hybas_af_lev12.zip (HydroBASINS level 12)
    python build.py   # writes public/webmaps/drop/net.bin, basins.png, meta.json

The web page also reads public/webmaps/rivers/land.json for the coastline and lakes.
