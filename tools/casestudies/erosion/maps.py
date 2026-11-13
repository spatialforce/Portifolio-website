"""Maps for the Chivi RUSLE soil loss study. UTM 36S (EPSG:32736) with degree ticks. Writes out/map*.png. Run: maps.py map1 map2 ..."""
import json, sys
import numpy as np, geopandas as gpd, rasterio, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap, LightSource, Normalize, LogNorm, BoundaryNorm
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy import ndimage as nd
from shapely.geometry import LineString, Point

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
AUTHOR = "© Kudzanai Chakavarika"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
TO = Transformer.from_crs(4326, 32736, always_xy=True); FROM = Transformer.from_crs(32736, 4326, always_xy=True)


def rd(n, b=1): return rasterio.open(f"rast/{n}.tif").read(b)


_s = rasterio.open("rast/dem.tif"); T = _s.transform; GX = (T.c, T.c + _s.width * 30, T.f - _s.height * 30, T.f)
DIST = gpd.read_file("data/chivi.gpkg").to_crs(32736); DM = rd("dist") == 1; LC = rd("lc"); LAND = DM & (LC != 80)
WARDS = gpd.read_file("out/wards.gpkg")
b = DIST.total_bounds; EXT = (b[0] - 16000, b[2] + 3000, b[1] - 2500, b[3] + 10000)
CLS_C = ["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c"]
CLS_L = ["Very low (< 2)", "Low (2 to 5)", "Moderate (5 to 10)", "High (10 to 20)", "Very high (> 20)"]


def osm_lines(name):
    geo, tags = [], []
    for e in json.load(open(f"data/osm_{name}.json")):
        if e["type"] == "way" and len(e.get("geometry", [])) > 1:
            geo.append(LineString([(q["lon"], q["lat"]) for q in e["geometry"]])); tags.append(e.get("tags", {}))
    return gpd.GeoDataFrame({"tags": tags}, geometry=geo, crs=4326).to_crs(32736)


RIV = osm_lines("rivers"); ROAD = osm_lines("roads")
PL = [(e["tags"]["name"], *TO.transform(e["lon"], e["lat"]), e["tags"]["place"]) for e in json.load(open("data/osm_places.json")) if "lon" in e]
PL = [p for p in PL if DIST.buffer(-1500).contains(Point(p[1], p[2])).any()]


def u(lon, lat): return TO.transform(lon, lat)


def ticks(ax, ext, step=0.2):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0 = FROM.transform(ext[0], ym)[0]; lo1 = FROM.transform(ext[1], ym)[0]; la0 = FROM.transform(xm, ext[2])[1]; la1 = FROM.transform(xm, ext[3])[1]
    lons = np.arange(np.ceil(lo0 / step) * step, lo1, step); lats = np.arange(np.ceil(la0 / step) * step, la1, step)
    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons])
    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats])
    ax.tick_params(length=2.5, labelsize=8, top=True, right=True, labeltop=True, labelright=True)


def narrow(ax, x=0.07, y=0.9, r=0.045, fg="#222222", bg="white"):
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, fg), (1, bg)):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec=fg, lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec=fg, lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.008, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=12, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])


def scalebar(ax, ext, length, x=0.04, y=0.035, fg="#222222"):
    L = length * 1000; x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.01
    halo = [pe.withStroke(linewidth=3.5, foreground="white")]
    ax.plot([x0, x0 + L], [y0, y0], color=fg, lw=1.3, zorder=60, solid_capstyle="butt", path_effects=halo)
    for i in range(5):
        xx = x0 + i * L / 4; hh = t if i in (0, 2, 4) else t * 0.55
        ax.plot([xx, xx], [y0, y0 + hh], color=fg, lw=1.1, zorder=60, path_effects=halo)
    for v, xx in [(0, x0), (length / 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(xx, y0 + t * 1.5, f"{v:g}", ha="center", va="bottom", fontsize=8.5, color=fg, zorder=60, path_effects=HALO)
    ax.text(x0 + L * 1.06, y0, "km", fontsize=8.5, va="center", color=fg, zorder=60, path_effects=HALO)


_HS = {}


def hill():
    if "h" not in _HS:
        from rasterio.features import rasterize
        dem = rd("dem").astype(float); _HS["h"] = LightSource(315, 45).hillshade(dem, vert_exag=3, dx=30, dy=30)
        w = rasterio.open("rast/dem_wide.tif"); wt = w.transform; dw = w.read(1).astype(float)
        _HS["w"] = LightSource(315, 45).hillshade(dw, vert_exag=3, dx=90, dy=90)
        _HS["wm"] = rasterize(DIST.geometry, out_shape=dw.shape, transform=wt) == 1
        _HS["wx"] = (wt.c, wt.c + w.width * 90, wt.f - w.height * 90, wt.f)
    return _HS


def base(ax, faded=True):
    """Hillshade: wide 90 m outside the district (faded), 30 m inside."""
    hs = hill(); out = np.where(hs["wm"], np.nan, 0.55 * hs["w"] + 0.45)
    ax.imshow(out, extent=hs["wx"], cmap="gray", vmin=0, vmax=1, zorder=0, interpolation="bilinear")
    if not faded: ax.imshow(np.where(DM, hs["h"], np.nan), extent=GX, cmap="gray", vmin=0, vmax=1, zorder=0.5, interpolation="bilinear")
    ax.set_facecolor("white")


def drape(ax, img, alpha=0.82):
    """Colour layer laid over hillshade inside the district."""
    h = hill()["h"]; rgb = img[..., :3] * (0.55 + 0.45 * h[..., None]) if alpha else img[..., :3]
    a = np.where(DM, 1.0, 0.0); ax.imshow(np.dstack([np.clip(rgb, 0, 1), a]), extent=GX, zorder=5, interpolation="nearest")


def outline(ax, lw=1.2, z=40): DIST.boundary.plot(ax=ax, color="#222222", lw=lw, zorder=z)


def setup(ax, ext, tk=True):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1)
    if tk: ticks(ax, ext)
    else: ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)


def title(ax, s, fs=14):
    ax.text(0.5, 0.975, s, transform=ax.transAxes, ha="center", va="top", fontsize=fs, fontweight="bold", zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])


def credit(ax): ax.text(0.992, 0.008, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, zorder=70, path_effects=HALO)


def legend(ax, handles, ttl, at=(0.99, 0.03), fs=9, loc="lower right"):
    leg = ax.legend(handles=handles, title=ttl, loc=loc, bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5, frameon=True, fancybox=False,
                    edgecolor="#222222", facecolor="white", framealpha=0.95, alignment="left", borderpad=0.7, handlelength=2.0, handleheight=1.1, labelspacing=0.5)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold"); return leg


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15); plt.close(fig); print("saved", name)


def side_layout(fig, ax):
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.04; w = 0.985 - x; return p, x, w


def pnl_box(ax, s):
    ax.text(0.03, 0.97, s, transform=ax.transAxes, ha="left", va="top", fontsize=8.5, fontweight="bold", zorder=70,
            bbox=dict(fc="white", ec="#222222", lw=0.5, pad=2.0))


def big_rivers(ax, a1=0.8, a2=0.5):
    big = RIV[RIV.tags.apply(lambda t: "name" in t)]
    big.plot(ax=ax, color="#2b6cb0", lw=1.0, alpha=a1, zorder=10); RIV[~RIV.index.isin(big.index)].plot(ax=ax, color="#4f8fd0", lw=0.5, alpha=a2, zorder=10)


def places(ax, fs=8.5, z=50):
    for nm, x, y, k in PL:
        ax.plot(x, y, "o", ms=5 if k == "town" else 3.5, mfc="black" if k == "town" else "white", mec="black", mew=0.8, zorder=z)
        ax.text(x + 1200, y + 600, nm, fontsize=fs, zorder=z, path_effects=HALO, fontweight="bold" if k == "town" else "normal")


# ---------------------------------------------------------------- map 1 study area
def map1():
    fig = plt.figure(figsize=(10.4, 8.6), dpi=200); ax = fig.add_axes([0.05, 0.05, 0.62, 0.9])
    base(ax, faded=False)
    big_rivers(ax); ROAD.plot(ax=ax, color="#8b2e16", lw=0.9, alpha=0.7, zorder=11)
    WARDS.boundary.plot(ax=ax, color="#555555", lw=0.45, ls="--", zorder=12); outline(ax, lw=1.6)
    for i, g in zip(WARDS.ward, WARDS.geometry):
        q = g.representative_point(); dy = -3500 if i == 30 else 0
        ax.text(q.x, q.y + dy, str(i), ha="center", va="center", fontsize=7.5, color="#333333", zorder=45, path_effects=HALO)
    places(ax); setup(ax, EXT); title(ax, "Study Area Map"); narrow(ax); scalebar(ax, EXT, 20, x=0.05, y=0.03); credit(ax)
    p, x, w = side_layout(fig, ax); gap = 0.03; h = (p.y1 - p.y0 - gap) / 2
    lo = fig.add_axes([x, p.y0 + h + gap, w, h]); lo.set_facecolor("white")
    pv = gpd.read_file("../population/data/districts.gpkg").to_crs(32736).dissolve("province")
    pv.plot(ax=lo, fc="#eeeeee", ec="#888888", lw=0.4); DIST.plot(ax=lo, fc="#c0392b", ec="#c0392b", lw=1.0)
    pb = pv.total_bounds; cx, cy = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2; hw = (pb[2] - pb[0]) / 2 * 1.08
    lo.set_xlim(cx - hw, cx + hw); lo.set_ylim(cy - hw * 0.92, cy + hw * 1.25); lo.set_aspect(1); lo.set_xticks([]); lo.set_yticks([])
    for s_ in lo.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    lo.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=lo.transAxes, fc="white", ec="none", zorder=5))
    lo.plot([0, 1], [0.86, 0.86], transform=lo.transAxes, color="#222222", lw=0.6, zorder=6)
    lo.text(0.5, 0.93, "Zimbabwe", transform=lo.transAxes, ha="center", va="center", fontsize=10, fontweight="bold", zorder=7)
    la = fig.add_axes([x, p.y0, w, h]); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    hd = [Patch(fc="none", ec="#222222", lw=1.6, label="District boundary"), Line2D([], [], color="#555555", lw=0.6, ls="--", label="Ward boundary and number"),
          Line2D([], [], color="#2b6cb0", lw=1.0, label="Main rivers"), Line2D([], [], color="#4f8fd0", lw=0.5, alpha=0.6, label="Other rivers"),
          Line2D([], [], color="#8b2e16", lw=0.9, alpha=0.7, label="Main roads"),
          Line2D([], [], marker="o", ls="", ms=5, mfc="black", mec="black", label="Town"),
          Line2D([], [], marker="o", ls="", ms=3.5, mfc="white", mec="black", label="Village or mission")]
    leg = la.legend(handles=hd, title="Legend", loc="upper left", fontsize=9, title_fontsize=10.5, frameon=False, borderaxespad=0.8,
                    alignment="left", handlelength=2.2, handleheight=1.3, labelspacing=0.8); leg.get_title().set_fontweight("bold")
    save(fig, "map1_study_area")


# ---------------------------------------------------------------- map 2 RUSLE factors
def map2():
    R, K, LS, C, P = (rd(n).astype(float) for n in ("R", "K", "LS", "C", "P"))
    PAN = [("(a) Rainfall Erosivity (R)", R, "YlGnBu", Normalize(*np.percentile(R[LAND], [1, 99])), r"MJ mm ha$^{-1}$ h$^{-1}$ yr$^{-1}$"),
           ("(b) Soil Erodibility (K)", K, "YlOrBr", Normalize(*np.percentile(K[LAND], [1, 99])), r"t ha h ha$^{-1}$ MJ$^{-1}$ mm$^{-1}$"),
           ("(c) Slope Length And Steepness (LS)", np.maximum(LS, 0.01), "magma_r", LogNorm(0.05, 20), "no unit, log scale"),
           ("(d) Cover Management (C)", C, "RdYlGn_r", Normalize(0, 0.7), "0 = full cover, 1 = bare"),
           ("(e) Support Practice (P)", P, ListedColormap(["#2c7fb8", "#7fcdbb", "#c7e9b4", "#edf8b1", "#fdbb84", "#f0f0f0"]),
            BoundaryNorm([0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.05], 6), "contouring on cropland")]
    fig = plt.figure(figsize=(11.0, 9.6), dpi=200)
    W, H = 0.3, 0.42
    pos = [(0.02 + i % 3 * 0.33, 0.53 - (i // 3) * 0.5) for i in range(6)]
    for (ttl, a, cm, nrm, unit), (x0, y0) in zip(PAN, pos):
        ax = fig.add_axes([x0, y0 + 0.04, W, H]); base(ax)
        img = plt.get_cmap(cm)(nrm(np.where(LAND, a, np.nan))); img[~LAND] = (1, 1, 1, 1); img[DM & (LC == 80)] = (0.6, 0.75, 0.9, 1)
        drape(ax, img); outline(ax, lw=0.8); setup(ax, EXT, tk=False); pnl_box(ax, ttl)
        cax = fig.add_axes([x0 + 0.03, y0 + 0.015, W - 0.06, 0.012])
        cb = fig.colorbar(mpl.cm.ScalarMappable(nrm, cm), cax=cax, orientation="horizontal"); cb.ax.tick_params(labelsize=7.5, length=2); cb.outline.set_linewidth(0.5)
        if ttl.startswith("(e)"): cb.set_ticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        cb.set_label(unit, fontsize=7.5, labelpad=1.5)
    ax = fig.add_axes([pos[5][0], pos[5][1] + 0.04, W, H]); base(ax)
    lcc = {10: "#1b7837", 20: "#a6a14b", 30: "#d9ef8b", 40: "#f4a582", 50: "#b2182b", 60: "#d8d2c4", 80: "#6baed6"}
    img = np.ones(LC.shape + (4,))
    for k, c in lcc.items(): img[DM & (LC == k)] = (*mpl.colors.to_rgb(c), 1)
    drape(ax, img); outline(ax, lw=0.8); setup(ax, EXT, tk=False); pnl_box(ax, "(f) Land Cover (WorldCover)")
    nm = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare", 80: "Water"}
    lax = fig.add_axes([pos[5][0], pos[5][1] - 0.005, W, 0.04]); lax.axis("off")
    lax.legend(handles=[Patch(fc=lcc[k], ec="#555555", lw=0.4, label=nm[k]) for k in lcc], loc="center", ncol=4, fontsize=7.5, frameon=False,
               handlelength=1.2, columnspacing=0.9, handletextpad=0.4)
    ax0 = fig.axes[0]; narrow(ax0, x=0.1, y=0.82, r=0.05)
    fig.text(0.985, 0.005, AUTHOR, ha="right", va="bottom", fontsize=7)
    save(fig, "map2_factors")


# ---------------------------------------------------------------- map 3 soil loss classes
def cls_img():
    cl = rd("cls"); img = np.ones(cl.shape + (4,))
    for c in range(1, 6): img[cl == c] = (*mpl.colors.to_rgb(CLS_C[c - 1]), 1)
    img[DM & (LC == 80)] = (0.6, 0.75, 0.9, 1); return img


def map3():
    fig = plt.figure(figsize=(8.6, 9.6), dpi=200); ax = fig.add_axes([0.06, 0.05, 0.88, 0.9]); base(ax)
    drape(ax, cls_img()); big_rivers(ax, 0.55, 0.0); outline(ax, lw=1.4)
    setup(ax, EXT); title(ax, "Soil Loss Classes"); narrow(ax); scalebar(ax, EXT, 20, x=0.05, y=0.03); credit(ax)
    legend(ax, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(CLS_C, CLS_L)] + [Patch(fc="#99bfe6", ec="#555555", lw=0.4, label="Water"),
           Line2D([], [], color="#2b6cb0", lw=1.0, alpha=0.55, label="Main rivers")], "Soil loss (t/ha/yr)", at=(0.01, 0.09), loc="lower left")
    save(fig, "map3_classes")


# ---------------------------------------------------------------- map 4 ward means
def map4():
    fig = plt.figure(figsize=(8.6, 9.6), dpi=200); ax = fig.add_axes([0.06, 0.05, 0.88, 0.9]); base(ax)
    br = [0, 3, 5, 8, 10, 40]; cm = ListedColormap(["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]); nrm = BoundaryNorm(br, 5)
    WARDS.plot(ax=ax, column="mean", cmap=cm, norm=nrm, ec="#444444", lw=0.6, zorder=5)
    for i, g, m in zip(WARDS.ward, WARDS.geometry, WARDS["mean"]):
        q = g.representative_point()
        ax.text(q.x, q.y, f"{i}", ha="center", va="center", fontsize=8, fontweight="bold", zorder=45, path_effects=HALO)
    outline(ax, lw=1.4); setup(ax, EXT); title(ax, "Mean Soil Loss By Ward"); narrow(ax); scalebar(ax, EXT, 20, x=0.05, y=0.03); credit(ax)
    lab = ["Under 3", "3 to 5", "5 to 8", "8 to 10", "Over 10"]
    legend(ax, [Patch(fc=cm(i), ec="#444444", lw=0.5, label=l) for i, l in enumerate(lab)], "Mean (t/ha/yr)", at=(0.01, 0.09), loc="lower left")
    save(fig, "map4_wards")


# ---------------------------------------------------------------- map 5 hot spot over Sentinel-2
def hot_ext():
    A = np.where(LAND, rd("A").astype(float), 0); s = nd.uniform_filter((A >= 10).astype(float), 400)
    s[~nd.binary_erosion(DM, iterations=250)] = 0; r, c = np.unravel_index(np.argmax(s), s.shape)
    x, y = T.c + c * 30, T.f - r * 30; return (x - 7500, x + 7500, y - 5500, y + 5500)


def map5():
    ext = hot_ext(); print("hot spot", FROM.transform((ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2))
    rgb = np.dstack([rd("rgb", i) for i in (1, 2, 3)]).astype(float) / 255
    fig = plt.figure(figsize=(12.0, 4.9), dpi=200)
    for k in range(2):
        ax = fig.add_axes([0.01 + k * 0.495, 0.05, 0.48, 0.9]); ax.imshow(rgb, extent=GX, zorder=0, interpolation="bilinear")
        if k:
            cl = rd("cls"); img = np.zeros(cl.shape + (4,))
            for c in (4, 5): img[cl == c] = (*mpl.colors.to_rgb(CLS_C[c - 1]), 0.62)
            ax.imshow(img, extent=GX, zorder=5, interpolation="nearest")
        WARDS.boundary.plot(ax=ax, color="white", lw=0.8, ls="--", zorder=12); big_rivers(ax, 0.9, 0.7)
        setup(ax, ext, tk=False); pnl_box(ax, ["(a) Sentinel-2 True Colour, 2023 to 2024", "(b) High and Very High Soil Loss"][k])
        if k == 0: narrow(ax, x=0.06, y=0.78, r=0.06); scalebar(ax, ext, 4, x=0.05, y=0.05)
        for i, g in zip(WARDS.ward, WARDS.geometry):
            gi = g.intersection(mpl_box(ext)); q = gi.representative_point() if gi.area > 0.15 * mpl_box(ext).area else None
            if q is not None and not q.is_empty: ax.text(q.x, q.y, f"Ward {i}", ha="center", fontsize=8, color="white", fontweight="bold", zorder=45,
                                                         path_effects=[pe.withStroke(linewidth=2, foreground="black")])
    legend(fig.axes[-1], [Patch(fc=CLS_C[3], alpha=0.8, label="High (10 to 20)"), Patch(fc=CLS_C[4], alpha=0.8, label="Very high (> 20)")],
           "Soil loss (t/ha/yr)", at=(0.985, 0.03), fs=8.5)
    fig.text(0.995, 0.005, AUTHOR, ha="right", va="bottom", fontsize=7)
    save(fig, "map5_hotspot")


def mpl_box(e):
    from shapely.geometry import box; return box(e[0], e[2], e[1], e[3])


if __name__ == "__main__":
    for n in sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5"]: globals()[n]()
