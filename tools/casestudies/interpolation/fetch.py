"""GHCN version 2 monthly precipitation (NOAA NCEI, archived), Zimbabwe stations only (country code 156).
Keeps the station inventory lines and the monthly data lines for Zimbabwe. Output: raw/zw.prcp, raw/zw.inv"""
import gzip, io, urllib.request
U = "https://www.ncei.noaa.gov/pub/data/ghcn/v2/"
inv = urllib.request.urlopen(U + "v2.prcp.inv", timeout=300).read().decode("latin-1").splitlines()
open("raw/zw.inv", "w").write("\n".join(l for l in inv if l.startswith("156")) + "\n")
raw = gzip.decompress(urllib.request.urlopen(U + "v2.prcp.gz", timeout=600).read()).decode("latin-1").splitlines()
z = [l for l in raw if l.startswith("156")]
open("raw/zw.prcp", "w").write("\n".join(z) + "\n"); print("stations", sum(1 for l in inv if l.startswith("156")), "lines", len(z))
