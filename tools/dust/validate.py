"""Compare MERRA-2 dust optical depth (map) with AERONET coarse-mode optical depth (ground)."""
import os, sys, csv, io, urllib.request, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import EVENTS, CACHE, LON0, LAT1, DX, DY, W, H, HOURS
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aeronet"); os.makedirs(RAW, exist_ok=True)
URL = ("https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3?year={a.year}&month={a.month}&day={a.day}"
       "&year2={b.year}&month2={b.month}&day2={b.day}&SDA15=1&AVG=10&lat1=-5&lon1=-100&lat2=60&lon2=60&if_no_html=1")

def fetch_day(d):
    p = os.path.join(RAW, d.isoformat() + ".csv")
    for k in range(5):
        if os.path.exists(p): break
        try:
            data = urllib.request.urlopen(URL.format(a=d, b=d), timeout=300).read()
            open(p + ".part", "wb").write(data); os.replace(p + ".part", p)
        except Exception as e:
            print("retry", d, e, flush=True)
    return open(p, encoding="latin-1").read().splitlines()

def fetch(a, b):
    out, hdr = [], None
    for n in range((b - a).days):
        ls = fetch_day(a + dt.timedelta(n))
        i0 = next((i for i, l in enumerate(ls) if l.startswith("AERONET_Site,")), None)
        if i0 is None: continue
        hdr = ls[i0]; out += ls[i0 + 1:]
    return [hdr] + out

def stats(m, g):
    m, g = np.array(m), np.array(g)
    if len(m) < 3: return "n<3"
    r = np.corrcoef(m, g)[0, 1]
    return f"N {len(m):5d}  r {r:.2f}  bias {np.mean(m-g):+.2f}  rmse {np.sqrt(np.mean((m-g)**2)):.2f}  within 0.1+20% {np.mean(abs(m-g) <= 0.1+0.2*g)*100:.0f}%"

allm, allg, dm, dg = [], [], [], []
for eid, a, b in EVENTS:
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    lines = fetch(a, b); i0 = 0
    rows = list(csv.reader(lines[i0 + 1:]))
    hdr = [h.strip() for h in lines[i0].split(",")]; ci = hdr.index("Coarse_Mode_AOD_500nm[tau_c]")
    la, lo = hdr.index("Site_Latitude(Degrees)"), hdr.index("Site_Longitude(Degrees)")
    acc = {}
    for r in rows:
        try:
            tc = float(r[ci]); lat, lon = float(r[la]), float(r[lo])
        except (ValueError, IndexError): continue
        if tc < 0: continue
        d = dt.datetime.strptime(r[1] + " " + r[2], "%d:%m:%Y %H:%M:%S")
        if d.hour % 3: continue                      # map frames are hourly means at 00,03..21 UTC
        acc.setdefault((r[0], lat, lon, d.date(), d.hour), []).append(tc)
    em, eg, sites = [], [], set()
    for (s, lat, lon, day, h), v in acc.items():
        j, i = int(round((LAT1 - lat) / DY)), int(round((lon - LON0) / DX))
        if not (0 <= j < H and 0 <= i < W): continue
        p = os.path.join(CACHE, day.isoformat() + ".npy")
        if not os.path.exists(p): continue
        m = float(np.load(p, mmap_mode="r")[HOURS.index(h), 0, j, i])
        g = float(np.mean(v))
        em.append(m); eg.append(g); sites.add(s)
        if max(m, g) >= 0.3: dm.append(m); dg.append(g)
    allm += em; allg += eg
    print(f"{eid:8s} sites {len(sites):3d}  {stats(em, eg)}")
print(f"{'all':8s}            {stats(allm, allg)}")
print(f"{'dusty':8s}            {stats(dm, dg)}   (map or ground >= 0.3)")
