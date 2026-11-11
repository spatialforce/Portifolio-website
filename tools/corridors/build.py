"""Trade corridors of Southern Africa: data build.

Routes each corridor from its port inland along the Natural Earth rail or road
network (shortest path between waypoints), then works out its length and the
countries it crosses.

    raw/: Natural Earth 10m railroads, roads, admin 0 countries, lakes
    python build.py    # writes public/webmaps/corridors/corridors.json
"""
import json
import math
import os

import geopandas as gpd
import networkx as nx
from pyproj import Transformer
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "corridors")
BBOX = (8, -36, 44, -1)

# Lambert azimuthal equal area centred on the region, output in km
TO = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=-17 +lon_0=27 +units=km", always_xy=True)

PLACES = {
    "Beira": (34.84, -19.83), "Mutare": (32.67, -18.97), "Harare": (31.05, -17.83),
    "Nacala": (40.67, -14.56), "Nampula": (39.27, -15.12), "Cuamba": (36.54, -14.80),
    "Blantyre": (35.01, -15.79), "Lilongwe": (33.78, -13.97), "Mchinji": (32.88, -13.80),
    "Maputo": (32.57, -25.97), "Mbombela": (30.97, -25.47), "Johannesburg": (28.05, -26.20),
    "Durban": (31.03, -29.87), "Pietermaritzburg": (30.38, -29.60), "Polokwane": (29.45, -23.90),
    "Beitbridge": (30.00, -22.22), "Masvingo": (30.83, -20.07), "Chirundu": (28.85, -16.03),
    "Lusaka": (28.28, -15.42), "Kapiri Mposhi": (28.68, -13.97), "Ndola": (28.64, -12.97),
    "Lubumbashi": (27.48, -11.66), "Dar es Salaam": (39.27, -6.82), "Mbeya": (33.46, -8.90),
    "Tunduma": (32.77, -9.30), "Mpika": (31.45, -11.83), "Lobito": (13.55, -12.35),
    "Huambo": (15.74, -12.78), "Kuito": (16.93, -12.38), "Luena": (19.91, -11.78),
    "Luau": (22.23, -10.71), "Kolwezi": (25.47, -10.71), "Walvis Bay": (14.51, -22.95),
    "Windhoek": (17.08, -22.57), "Gobabis": (18.97, -22.45), "Gaborone": (25.91, -24.65),
    "Pretoria": (28.19, -25.75), "Otjiwarongo": (16.65, -20.46), "Grootfontein": (18.11, -19.57),
    "Rundu": (19.77, -17.92), "Katima Mulilo": (24.27, -17.50), "Livingstone": (25.85, -17.85),
    "Kafue": (28.18, -15.77),
}

CORRIDORS = [
    dict(slug="north-south", name="North–South", port="Durban", mode="road",
         via=["Durban", "Pietermaritzburg", "Johannesburg", "Polokwane", "Beitbridge", "Masvingo",
              "Harare", "Chirundu", "Kafue", "Lusaka", "Kapiri Mposhi", "Ndola", "Lubumbashi"],
         borders=["Beitbridge", "Chirundu", "Kasumbalesa"],
         text="The busiest road in the region, carrying copper south and fuel and goods north."),
    dict(slug="beira", name="Beira", port="Beira", mode="rail",
         via=["Beira", "Mutare", "Harare"], borders=["Forbes–Machipanda"],
         text="Zimbabwe's shortest way to the sea."),
    dict(slug="maputo", name="Maputo", port="Maputo", mode="road",
         via=["Maputo", "Mbombela", "Johannesburg"], borders=["Lebombo–Ressano Garcia"],
         text="Links Gauteng to the nearest deep water port, about 90 km from the border."),
    dict(slug="nacala", name="Nacala", port="Nacala", mode="rail",
         via=["Nacala", "Nampula", "Cuamba", "Blantyre", "Lilongwe", "Mchinji"],
         borders=["Entre Lagos–Nayuchi", "Mchinji–Mwami"],
         text="A natural deep harbour serving landlocked Malawi and eastern Zambia."),
    dict(slug="tazara", name="Dar es Salaam", port="Dar es Salaam", mode="rail",
         via=["Dar es Salaam", "Mbeya", "Tunduma", "Mpika", "Kapiri Mposhi"],
         borders=["Tunduma–Nakonde"],
         text="The TAZARA railway, built in the 1970s to give Zambia an outlet that avoided Rhodesia and South Africa."),
    dict(slug="lobito", name="Lobito", port="Lobito", mode="rail",
         via=["Lobito", "Huambo", "Kuito", "Luena", "Luau", "Kolwezi"],
         borders=["Luau–Dilolo"],
         text="The Benguela Railway, rebuilt after the Angolan war to carry copper west to the Atlantic."),
    dict(slug="trans-kalahari", name="Trans-Kalahari", port="Walvis Bay", mode="road",
         via=["Walvis Bay", "Windhoek", "Gobabis", "Gaborone", "Pretoria"],
         borders=["Buitepos–Mamuno", "Skilpadshek–Pioneer Gate"],
         text="A road across the Kalahari linking the Atlantic to Gauteng."),
    dict(slug="walvis-ndola", name="Walvis Bay–Ndola", port="Walvis Bay", mode="road",
         via=["Walvis Bay", "Otjiwarongo", "Grootfontein", "Rundu", "Katima Mulilo", "Livingstone",
              "Lusaka", "Kapiri Mposhi", "Ndola", "Lubumbashi"],
         borders=["Katima Mulilo–Sesheke", "Kasumbalesa"],
         text="Through the Caprivi Strip to the Copperbelt."),
]


def graph(lines, snap=3.0):
    """Line network as a graph; ends closer than `snap` km are joined."""
    G = nx.Graph()
    key = lambda p: (round(p[0] / snap), round(p[1] / snap))
    for geom in lines:
        parts = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
        for ln in parts:
            pts = [TO.transform(x, y) for x, y in ln.coords]
            for a, b in zip(pts, pts[1:]):
                ka, kb = key(a), key(b)
                if ka == kb:
                    continue
                G.add_node(ka, p=a); G.add_node(kb, p=b)
                G.add_edge(ka, kb, w=math.dist(a, b))
    # join near-touching ends of separate pieces
    nodes = list(G.nodes)
    ends = [n for n in nodes if G.degree(n) == 1]
    for e in ends:
        pe = G.nodes[e]["p"]
        best, bd = None, 12.0
        for n in nodes:
            if n == e or G.has_edge(e, n):
                continue
            d = math.dist(pe, G.nodes[n]["p"])
            if d < bd:
                best, bd = n, d
        if best is not None:
            G.add_edge(e, best, w=bd)
    return G


def nearest(G, p):
    return min(G.nodes, key=lambda n: math.dist(G.nodes[n]["p"], p))


def route(G, names):
    path = []
    for a, b in zip(names, names[1:]):
        na, nb = nearest(G, TO.transform(*PLACES[a])), nearest(G, TO.transform(*PLACES[b]))
        seg = nx.shortest_path(G, na, nb, weight="w")
        path += seg if not path else seg[1:]
    pts = [G.nodes[n]["p"] for n in path]
    # start exactly at the port
    pts.insert(0, TO.transform(*PLACES[names[0]]))
    return pts


def rings(gdf, tol):
    out = []
    for g in gdf.geometry:
        polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
        for p in polys:
            r = [TO.transform(x, y) for x, y in p.exterior.coords]
            s = LineString(r).simplify(tol)
            if len(s.coords) > 3:
                out.append([[round(x, 1), round(y, 1)] for x, y in s.coords])
    return out


def lines_out(gdf, tol):
    out = []
    for g in gdf.geometry:
        parts = g.geoms if g.geom_type == "MultiLineString" else [g]
        for ln in parts:
            s = LineString([TO.transform(x, y) for x, y in ln.coords]).simplify(tol)
            out.append([[round(x, 1), round(y, 1)] for x, y in s.coords])
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    rail = gpd.read_file(f"zip://{RAW}/ne_10m_railroads.zip", bbox=BBOX)
    road = gpd.read_file(f"zip://{RAW}/ne_10m_roads.zip", bbox=BBOX)
    road = road[road.scalerank <= 7]
    countries = gpd.read_file(f"zip://{RAW}/ne_10m_admin_0_countries.zip", bbox=BBOX)
    countries = countries[countries.CONTINENT == "Africa"]
    lakes = gpd.read_file(f"zip://{RAW}/ne_10m_lakes.zip", bbox=BBOX)
    lakes = lakes[lakes.scalerank <= 3]

    nets = {"rail": graph(rail.geometry), "road": graph(road.geometry)}
    cp = countries.to_crs("+proj=laea +lat_0=-17 +lon_0=27 +units=km")

    out = []
    for c in CORRIDORS:
        pts = route(nets[c["mode"]], c["via"])
        ln = LineString(pts)
        # countries in the order the route passes through them
        seen = []
        for i in range(0, 201):
            q = ln.interpolate(i / 200, normalized=True)
            hit = cp[cp.contains(q)]
            if len(hit):
                n = hit.iloc[0].NAME
                if not seen or seen[-1] != n:
                    seen.append(n)
        dedup = []
        for n in seen:
            if n not in dedup:
                dedup.append(n)
        s = ln.simplify(1.0)
        out.append(dict(slug=c["slug"], name=c["name"], port=c["port"], mode=c["mode"], text=c["text"],
                        borders=c["borders"], end=c["via"][-1], km=round(ln.length / 10) * 10,
                        countries=dedup, line=[[round(x, 1), round(y, 1)] for x, y in s.coords]))
        print(f'{c["name"]:18} {c["mode"]:4} {ln.length:6.0f} km  {" > ".join(dedup)}')

    clip = box(*BBOX).buffer(6)
    countries = countries.assign(geometry=countries.geometry.intersection(clip))
    ports = sorted({c["port"] for c in CORRIDORS})
    towns = sorted({p for c in CORRIDORS for p in c["via"]} - set(ports))
    rnd = lambda p: [round(v, 1) for v in TO.transform(*PLACES[p])]
    json.dump(dict(
        corridors=out,
        land=rings(countries, 2.5), lakes=rings(lakes, 1.5),
        rail=lines_out(rail, 1.5), road=lines_out(road, 1.5),
        ports=[[p, *rnd(p)] for p in ports], towns=[[t, *rnd(t)] for t in towns],
        labels=[[r.NAME, *[round(v, 1) for v in TO.transform(r.LABEL_X, r.LABEL_Y)]] for r in countries.itertuples()
                if BBOX[0] < r.LABEL_X < BBOX[2] and BBOX[1] < r.LABEL_Y < BBOX[3]],
    ), open(os.path.join(OUT, "corridors.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print("written", os.path.getsize(os.path.join(OUT, "corridors.json")) // 1024, "KB")


if __name__ == "__main__":
    main()
