"""Coastlines for the atlas: Natural Earth 1:50m land (via world-atlas), decoded from TopoJSON
into plain rings of [lon, lat] rounded to 0.01 degrees and delta encoded."""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "migration")
SRC = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-50m.json"


def main():
    topo = json.loads(urllib.request.urlopen(SRC, timeout=60).read())
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for a in idx:
            seg = arcs[a] if a >= 0 else arcs[~a][::-1]
            pts.extend(seg if not pts else seg[1:])
        return pts

    rings = []
    for geom in topo["objects"]["land"]["geometries"]:
        polys = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
        for poly in polys:
            for r in poly:
                pts = ring(r)
                # delta encode in hundredths of a degree, dropping repeated points
                flat, px, py = [], None, None
                lx = ly = 0
                for lon, lat in pts:
                    ix, iy = round(lon * 100), round(lat * 100)
                    if (ix, iy) == (px, py):
                        continue
                    flat += [ix - lx, iy - ly]
                    lx, ly, px, py = ix, iy, ix, iy
                if len(flat) >= 8:
                    rings.append(flat)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "land.json")
    json.dump(rings, open(path, "w"), separators=(",", ":"))
    print(path, len(rings), "rings", os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
