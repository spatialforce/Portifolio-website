"""Country borders for the atlas: the TopoJSON arcs shared by two countries in Natural Earth
1:50m (via world-atlas), written as delta encoded lines in hundredths of a degree."""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "migration")
SRC = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json"


def main():
    topo = json.loads(urllib.request.urlopen(SRC, timeout=60).read())
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    uses = {}

    def walk(a):
        if isinstance(a, int):
            k = a if a >= 0 else ~a
            uses[k] = uses.get(k, 0) + 1
        else:
            for b in a:
                walk(b)

    for g in topo["objects"]["countries"]["geometries"]:
        walk(g.get("arcs", []))
    lines = []
    for k, n in uses.items():
        if n < 2:
            continue  # coastline, not a border
        x = y = 0
        flat, lx, ly = [], 0, 0
        for dx, dy in topo["arcs"][k]:
            x += dx; y += dy
            ix, iy = round((x * sx + tx) * 100), round((y * sy + ty) * 100)
            flat += [ix - lx, iy - ly]
            lx, ly = ix, iy
        lines.append(flat)
    path = os.path.join(OUT, "borders.json")
    json.dump(lines, open(path, "w"), separators=(",", ":"))
    print(path, len(lines), "lines", os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
