"""Languages of Southern Africa: data build.

    cache/languages.csv, values.csv   Glottolog CLDF (github.com/glottolog/glottolog-cldf)
    Wikidata                          speaker numbers, matched on Glottocode
    Wikimedia Commons, Lingua Libre   native speaker recordings (Afrikaans, Northern Sotho only)
    ../corridors/raw                  Natural Earth countries and lakes

Each language is a point in Glottolog. Its area on the map is the part of the land
closer to that point than to any other living language's, capped at RADIUS km, so it
shows roughly where a language sits, not a surveyed boundary. Extinct and contact
languages are kept as points.

    python build.py    # writes public/webmaps/languages/languages.json and audio/
"""
import io
import json
import os
import wave

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer
from shapely import voronoi_polygons
from shapely.geometry import MultiPoint, Point, box
from shapely.ops import transform, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "languages")
NE = os.path.join(HERE, "..", "corridors", "raw")
UA = {"User-Agent": "portfolio-webmap-build/1.0"}
BBOX = (11, -35, 41, -8)
RADIUS = 320
CRS = "+proj=laea +lat_0=-20 +lon_0=26 +units=km"
TO = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)

# group = first rule whose node name appears in the language's Glottolog path
GROUPS = [
    ("Nguni", ["Nguni (S.40)"]),
    ("Sotho-Tswana", ["Sotho-Tswana (S.30)", "Sotho-Tswana"]),
    ("Shona", ["Shona (S.10)"]),
    ("Tsonga and Chopi", ["Tswa-Ronga (S.50)", "Tswa-Ronga", "Copi (S.60)", "Copi"]),
    ("Other Southern Bantu", ["Southern Bantu"]),
    ("Nyanja and Sena", ["Tumbuka-Sena-Nyanja"]),
    ("Makua and Lomwe", ["North Mozambique Bantu"]),
    ("Bemba and Luba", ["Sabi", "Luban"]),
    ("Tonga and Lozi", ["Botatwe", "Greater Luyana"]),
    ("Angola and Namibia", ["Njila", "West-Coastal Bantu"]),
    ("Other Bantu", ["Narrow Bantu", "Atlantic-Congo"]),
    ("Khoe", ["Khoe-Kwadi"]),
    ("Tuu and Kx'a", ["Tuu", "Kxa"]),
    ("Afrikaans", ["Indo-European"]),
    ("Contact languages", ["Pidgin", "Speech Register"]),
]
NAMES = {"pedi1238": "Northern Sotho (Sepedi)", "nort2795": "Ndebele (Zimbabwe)", "sout2808": "Ndebele (South Africa)"}
# Wikidata keeps some speaker figures on the parent group
SPEAKERS_FROM = {"pedi1238": "nort3233"}
SKIP = {"Sign Language", "Bookkeeping", "Unclassifiable"}

STATUS = {"not_endangered": "Not endangered", "threatened": "Threatened", "shifting": "Shifting",
          "moribund": "Moribund", "nearly_extinct": "Nearly extinct", "extinct": "Extinct"}
COUNTRY = {"AO": "Angola", "BW": "Botswana", "CD": "DR Congo", "LS": "Lesotho", "MW": "Malawi", "MZ": "Mozambique",
           "NA": "Namibia", "SZ": "Eswatini", "TZ": "Tanzania", "ZA": "South Africa", "ZM": "Zambia", "ZW": "Zimbabwe",
           "MG": "Madagascar", "CG": "Congo", "KE": "Kenya", "BI": "Burundi", "RW": "Rwanda", "UG": "Uganda"}

# six everyday words, recorded by native speakers on Lingua Libre (CC BY-SA 4.0), spelt as the speaker titled them
AUDIO = {
    "afri1274": ("Oesjaar", [
        ("Hello", "hallo", "LL-Q14196 (afr)-Oesjaar-hallo.wav"),
        ("Thank you", "dankie", "LL-Q14196 (afr)-Oesjaar-dankie.wav"),
        ("Goodbye", "totsiens", "LL-Q14196 (afr)-Oesjaar-totsiens.wav"),
        ("Water", "water", "LL-Q14196 (afr)-Oesjaar-water.wav"),
        ("Rain", "reën", "LL-Q14196 (afr)-Oesjaar-reën.wav"),
        ("Love", "liefde", "LL-Q14196 (afr)-Oesjaar-liefde.wav")]),
    "pedi1238": ("Mndetatsin", [
        ("Good morning", "lekae aretsogile", "LL-Q12068060(nso)-Mndetatsin-lekae-aretsogile(Bonjour).wav"),
        ("Thank you", "kaleboga", "LL-Q2728730(nso)-Mndetatsin-kaleboga(Merci).wav"),
        ("Goodbye", "tsamaya hantle", "LL-Q65219927(nso)-Mndetatsin-tsamaya hantle(Aurevoir).wav"),
        ("Water", "metsi", "LL-Q283(nso)-Mndetatsin-metsi(l'eau).wav"),
        ("It is raining", "pula yana", "LL-Q19174467(nso)-Mndetatsin-pula yana(Il pleut).wav"),
        ("I love you", "ka gorata", "LL-Q26186450(nso)-Mndetatsin-ka gorata(je t'aime).wav")]),
}


def speakers(codes):
    path = os.path.join(CACHE, "speakers.json")
    if not os.path.exists(path):
        g = " ".join(f'"{c}"' for c in codes)
        q = f"""SELECT ?gc ?n WHERE {{ VALUES ?gc {{ {g} }} ?item wdt:P1394 ?gc . ?item wdt:P1098 ?n . }}"""
        r = requests.post("https://query.wikidata.org/sparql", data={"query": q},
                          headers={**UA, "Accept": "application/sparql-results+json"}, timeout=120)
        r.raise_for_status()
        out = {}
        for b in r.json()["results"]["bindings"]:
            out[b["gc"]["value"]] = max(out.get(b["gc"]["value"], 0), float(b["n"]["value"]))
        json.dump(out, open(path, "w"))
    return json.load(open(path))


def clip(fname, dest):
    """Download a recording, make it mono, trim the silence and save it at 22 kHz."""
    if os.path.exists(dest):
        return
    import time
    for wait in (6, 45, 120, 240):
        time.sleep(wait)              # Commons limits how fast files can be fetched
        r = requests.get("https://commons.wikimedia.org/wiki/Special:FilePath/" + fname, headers=UA, timeout=60)
        if r.status_code != 429:
            break
    r.raise_for_status()
    w = wave.open(io.BytesIO(r.content))
    ch, sw, fr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    assert sw == 2, f"{fname}: {sw * 8}-bit audio"
    a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch).mean(axis=1)
    loud = np.where(np.abs(a) > np.abs(a).max() * 0.04)[0]
    a = a[max(0, loud[0] - fr // 10): loud[-1] + fr // 6]
    step = max(1, fr // 22050)
    a = a[::step]
    a = (a / max(1, np.abs(a).max()) * 30000).astype(np.int16)
    o = wave.open(dest, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(fr // step)
    o.writeframes(a.tobytes()); o.close()


def main():
    os.makedirs(os.path.join(OUT, "audio"), exist_ok=True)
    d = pd.read_csv(os.path.join(CACHE, "languages.csv"))
    name = d.set_index("ID").Name
    v = pd.read_csv(os.path.join(CACHE, "values.csv"), usecols=["Language_ID", "Parameter_ID", "Value", "Code_ID"])
    cl = v[v.Parameter_ID == "classification"].set_index("Language_ID").Value
    aes = v[v.Parameter_ID == "aes"].set_index("Language_ID").Code_ID

    f = d[(d.Level == "language") & d.Longitude.between(BBOX[0], BBOX[2]) & d.Latitude.between(BBOX[1], BBOX[3])]
    f = f[~f.Family_ID.map(name).isin(SKIP)]
    # dialects of each language, by name
    dia = d[d.Level == "dialect"]
    dialects = {}
    for r in dia.itertuples():
        p = str(cl.get(r.ID, "")).split("/")
        for anc in p:
            if anc in set(f.ID):
                dialects.setdefault(anc, []).append(r.Name)
    spk = speakers(list(f.ID) + list(SPEAKERS_FROM.values()))
    for a, b in SPEAKERS_FROM.items():
        spk.setdefault(a, spk.get(b, 0))

    langs = []
    for r in f.itertuples():
        path = [name.get(x, x) for x in str(cl.get(r.ID, "")).split("/") if x]
        hit = next(((g, k) for g, keys in GROUPS for k in keys if k in path), None)
        if hit is None:
            print("no group:", r.Name, path); continue
        grp, node = hit
        top = "Bantu" if "Narrow Bantu" in path else path[0]
        sub = node.split(" (")[0]
        fam = top if sub in (top, "Narrow Bantu", "Atlantic-Congo", "Southern Bantu") else f"{top} › {sub}"
        fam = fam.replace("Kxa", "Kx'a")
        st = str(aes.get(r.ID, "")).replace("aes-", "")
        x, y = TO.transform(r.Longitude, r.Latitude)
        L = dict(id=r.ID, name=NAMES.get(r.ID, r.Name), group=grp, x=round(x, 1), y=round(y, 1),
                 family=fam,
                 status=STATUS.get(st, ""), speakers=int(spk.get(r.ID, 0)),
                 countries=[COUNTRY.get(c, c) for c in str(r.Countries).split(";") if c and c != "nan"],
                 dialects=sorted(dialects.get(r.ID, []))[:12])
        if r.ID in AUDIO:
            who, words = AUDIO[r.ID]
            L["audio"] = []
            for gloss, word, fn in words:
                dest = f"{r.ID}-{len(L['audio'])}.wav"
                clip(fn, os.path.join(OUT, "audio", dest))
                L["audio"].append([gloss, word, "audio/" + dest])
            L["speaker"] = who
        langs.append(L)

    # areas: Voronoi cells over the land, capped at RADIUS around each point
    cty = gpd.read_file(f"zip://{NE}/ne_10m_admin_0_countries.zip", bbox=(BBOX[0] - 4, BBOX[1] - 3, BBOX[2] + 4, BBOX[3] + 4))
    cty = cty[cty.CONTINENT == "Africa"].to_crs(CRS)
    land = unary_union(cty.geometry).simplify(2)
    lakes = gpd.read_file(f"zip://{NE}/ne_10m_lakes.zip", bbox=BBOX).to_crs(CRS)
    lakes = lakes[lakes.scalerank <= 4]
    land = land.difference(unary_union(lakes.geometry).buffer(0))
    # extinct languages and urban contact languages are shown as points, not areas
    for L in langs:
        L["point"] = L["status"] == "Extinct" or L["group"] == "Contact languages"
        L["area"] = []
    living = [L for L in langs if not L["point"]]
    pts = MultiPoint([(L["x"], L["y"]) for L in living])
    cells = voronoi_polygons(pts, extend_to=land.envelope.buffer(500))
    for L in living:
        p = Point(L["x"], L["y"])
        cell = next(c for c in cells.geoms if c.contains(p) or c.distance(p) < 1e-6)
        a = cell.intersection(p.buffer(RADIUS, 32)).intersection(land).simplify(1.5)
        L["area"] = [[[round(x, 1), round(y, 1)] for x, y in poly.exterior.coords]
                     for poly in (a.geoms if a.geom_type == "MultiPolygon" else [a]) if poly.geom_type == "Polygon" and poly.area > 20]

    view = box(*TO.transform(BBOX[0] - 2, BBOX[1] - 1)[:2], *TO.transform(BBOX[2] + 2, BBOX[3] + 2)[:2]).buffer(400)
    rings = lambda geom: [[[round(x, 1), round(y, 1)] for x, y in poly.exterior.coords]
                          for poly in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom]) if poly.area > 30]
    borders = []
    for g in cty.geometry:
        g = g.intersection(view).simplify(2)
        if not g.is_empty:
            borders += rings(g)
    json.dump(dict(groups=[g for g, _ in GROUPS], languages=langs, land=borders,
                   lakes=[r for g in lakes.geometry for r in rings(g.simplify(1.5))]),
              open(os.path.join(OUT, "languages.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    from collections import Counter
    print(len(langs), "languages;", Counter(L["group"] for L in langs).most_common())
    print("with speakers:", sum(1 for L in langs if L["speakers"]), " status:", Counter(L["status"] for L in langs))
    print(os.path.getsize(os.path.join(OUT, "languages.json")) // 1024, "KB")


if __name__ == "__main__":
    main()
