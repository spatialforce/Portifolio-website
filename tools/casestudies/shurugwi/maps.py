"""Maps for the Shurugwi soil loss and gully study. UTM 36S (EPSG:32736) with degree ticks. Writes out/map*.png. Run: maps.py map1 map2 ..."""

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

DIST = gpd.read_file("data/shurugwi.gpkg").to_crs(32736); DM = rd("dist") == 1; LC = rd("lc"); LAND = DM & (LC != 80)

WARDS = gpd.read_file("out/wards.gpkg")

b = DIST.total_bounds; EXT = (b[0] - 4000, b[2] + 4000, b[1] - 3500, b[3] + 7500)

CLS_C = ["#ffffd4", "#fed98e", "#fe9929", "#d95f0e", "#7f2704"]

CLS_L = ["Very low (< 2)", "Low (2 – 5)", "Moderate (5 – 10)", "High (10 – 20)", "Very high (> 20)"]


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


def ticks(ax, ext, step=0.2, fs=9.5):

    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)

    lo0 = FROM.transform(ext[0], ym)[0]; lo1 = FROM.transform(ext[1], ym)[0]; la0 = FROM.transform(xm, ext[2])[1]; la1 = FROM.transform(xm, ext[3])[1]

    lons = np.arange(np.ceil(lo0 / step) * step, lo1, step); lats = np.arange(np.ceil(la0 / step) * step, la1, step)

    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons], fontweight="bold")

    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats], fontweight="bold", rotation=90, va="center")

    ax.tick_params(length=2.5, labelsize=fs, top=True, right=True, labeltop=True, labelright=True)


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


def setup(ax, ext, tk=True, fs=9.5):

    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1)

    if tk: ticks(ax, ext, fs=fs)

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


def frame(fig):
    fig.patches.append(Rectangle((0.003, 0.003), 0.994, 0.994, transform=fig.transFigure, fill=False, ec="#222222", lw=1.0, zorder=100))


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


# ---------------------------------------------------------------- map 1 study area (elevation tint over hillshade)

ELEV = ListedColormap(["#5a8f4e", "#93b46b", "#cfd59a", "#ead9a4", "#d8b07c", "#b07d55", "#8a5a3c"])

ELEV_B = [850, 1100, 1200, 1300, 1400, 1450, 1500, 1600]


def map1():

    fig = plt.figure(figsize=(11.6, 8.6), dpi=200); ax = fig.add_axes([0.04, 0.05, 0.64, 0.9])

    base(ax)

    dem = rd("dem").astype(float); img = ELEV(BoundaryNorm(ELEV_B, 7)(dem)); drape(ax, img)

    big_rivers(ax); ROAD.plot(ax=ax, color="#222222", lw=0.9, alpha=0.75, zorder=11)

    WARDS.boundary.plot(ax=ax, color="#444444", lw=0.45, ls="--", zorder=12); outline(ax, lw=1.6)

    for i, g in zip(WARDS.ward, WARDS.geometry):

        if i == "Town": continue

        q = g.representative_point()

        ax.text(q.x, q.y, i, ha="center", va="center", fontsize=7.5, color="#222222", zorder=45, path_effects=HALO)

    places(ax); setup(ax, EXT, fs=11); title(ax, "Study Area Map"); narrow(ax); scalebar(ax, EXT, 20, x=0.05, y=0.03); credit(ax)

    p, x, w = side_layout(fig, ax); gap = 0.03; h = (p.y1 - p.y0 - gap) * 0.42

    lo = fig.add_axes([x, p.y1 - h, w, h]); lo.set_facecolor("white")

    pv = gpd.read_file("../population/data/districts.gpkg").to_crs(32736).dissolve("province")

    pv.plot(ax=lo, fc="#eeeeee", ec="#888888", lw=0.4); DIST.plot(ax=lo, fc="#c0392b", ec="#c0392b", lw=1.0)

    pb = pv.total_bounds; cx, cy = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2; hw = (pb[2] - pb[0]) / 2 * 1.08

    lo.set_xlim(cx - hw, cx + hw); lo.set_ylim(cy - hw * 0.92, cy + hw * 1.25); lo.set_aspect(1); lo.set_xticks([]); lo.set_yticks([])

    for s_ in lo.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)

    lo.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=lo.transAxes, fc="white", ec="none", zorder=5))

    lo.plot([0, 1], [0.86, 0.86], transform=lo.transAxes, color="#222222", lw=0.6, zorder=6)

    lo.text(0.5, 0.93, "Zimbabwe", transform=lo.transAxes, ha="center", va="center", fontsize=10, fontweight="bold", zorder=7)

    la = fig.add_axes([x, p.y0, w, p.y1 - h - gap - p.y0]); la.set_xticks([]); la.set_yticks([])

    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)

    hd = [Patch(fc="none", ec="#222222", lw=1.6, label="District boundary"), Line2D([], [], color="#444444", lw=0.6, ls="--", label="Ward boundary and number"),

          Line2D([], [], color="#2b6cb0", lw=1.0, label="Main rivers"), Line2D([], [], color="#222222", lw=0.9, alpha=0.75, label="Main roads"),

          Line2D([], [], marker="o", ls="", ms=5, mfc="black", mec="black", label="Town"),

          Line2D([], [], marker="o", ls="", ms=3.5, mfc="white", mec="black", label="Villages")]

    leg = la.legend(handles=hd, title="Legend", loc="upper left", fontsize=10.5, title_fontsize=12, frameon=False, borderaxespad=1.0,

                    alignment="left", handlelength=2.4, handleheight=1.3, labelspacing=1.45); leg.get_title().set_fontweight("bold")

    cax = la.inset_axes([0.08, 0.07, 0.84, 0.05])

    cb = fig.colorbar(mpl.cm.ScalarMappable(BoundaryNorm(ELEV_B, 7), ELEV), cax=cax, orientation="horizontal", spacing="uniform")

    cb.set_ticks(ELEV_B); cb.ax.tick_params(labelsize=8, length=2); cb.outline.set_linewidth(0.5)

    cax.set_title("Elevation (m)", fontsize=10.5, fontweight="bold", loc="left", pad=4)

    frame(fig); save(fig, "map1_study_area")


# ---------------------------------------------------------------- map 2 RUSLE factors

def map2():

    R, K, LS, C, P = (rd(n).astype(float) for n in ("R", "K", "LS", "C", "P"))

    PAN = [("(a) Rainfall Erosivity (R)", R, "YlGnBu", Normalize(*np.percentile(R[LAND], [1, 99])), r"MJ mm ha$^{-1}$ h$^{-1}$ yr$^{-1}$"),

           ("(b) Soil Erodibility (K)", K, "YlOrBr", Normalize(*np.percentile(K[LAND], [1, 99])), r"t ha h ha$^{-1}$ MJ$^{-1}$ mm$^{-1}$"),

           ("(c) Slope Length And Steepness (LS)", np.maximum(LS, 0.01), "magma_r", LogNorm(0.05, 20), "no unit, log scale"),

           ("(d) Cover Management (C)", C, "RdYlGn_r", Normalize(0, 0.7), "0 = full cover, 1 = bare"),

           ("(e) Support Practice (P)", P, ListedColormap(["#2c7fb8", "#7fcdbb", "#c7e9b4", "#edf8b1", "#fdbb84", "#f0f0f0"]),

            BoundaryNorm([0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.05], 6), "contouring on cropland")]

    fig = plt.figure(figsize=(11.0, 8.3), dpi=200)

    W, H = 0.3, 0.42

    pos = [(0.02 + i % 3 * 0.33, 0.53 - (i // 3) * 0.5) for i in range(6)]

    for (ttl, a, cm, nrm, unit), (x0, y0) in zip(PAN, pos):

        ax = fig.add_axes([x0, y0 + 0.04, W, H]); base(ax)

        img = plt.get_cmap(cm)(nrm(np.where(LAND, a, np.nan))); img[~LAND] = (1, 1, 1, 1); img[DM & (LC == 80)] = (0.6, 0.75, 0.9, 1)

        drape(ax, img); outline(ax, lw=0.8); setup(ax, EXTZ, tk=False); pnl_box(ax, ttl); narrow(ax, x=0.92, y=0.84, r=0.04)

        cax = fig.add_axes([x0 + 0.03, y0 + 0.015, W - 0.06, 0.012])

        cb = fig.colorbar(mpl.cm.ScalarMappable(nrm, cm), cax=cax, orientation="horizontal"); cb.ax.tick_params(labelsize=7.5, length=2); cb.outline.set_linewidth(0.5)

        if ttl.startswith("(e)"): cb.set_ticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

        cb.set_label(unit, fontsize=7.5, labelpad=1.5)

    ax = fig.add_axes([pos[5][0], pos[5][1] + 0.04, W, H]); base(ax)

    lcc = {10: "#1b7837", 20: "#a6a14b", 30: "#d9ef8b", 40: "#f4a582", 50: "#b2182b", 60: "#d8d2c4", 80: "#6baed6"}

    img = np.ones(LC.shape + (4,))

    for k, c in lcc.items(): img[DM & (LC == k)] = (*mpl.colors.to_rgb(c), 1)

    drape(ax, img); outline(ax, lw=0.8); setup(ax, EXTZ, tk=False); pnl_box(ax, "(f) Land Cover (WorldCover)"); narrow(ax, x=0.92, y=0.84, r=0.04)

    nm = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare", 80: "Water"}

    lax = fig.add_axes([pos[5][0], pos[5][1] - 0.005, W, 0.04]); lax.axis("off")

    lax.legend(handles=[Patch(fc=lcc[k], ec="#555555", lw=0.4, label=nm[k]) for k in lcc], loc="center", ncol=4, fontsize=7.5, frameon=False,

               handlelength=1.2, columnspacing=0.9, handletextpad=0.4)

    fig.text(0.985, 0.005, AUTHOR, ha="right", va="bottom", fontsize=7)

    save(fig, "map2_factors")


# ---------------------------------------------------------------- map 3 soil loss classes (side legend panel)

def cls_img():

    cl = rd("cls"); img = np.ones(cl.shape + (4,))

    for c in range(1, 6): img[cl == c] = (*mpl.colors.to_rgb(CLS_C[c - 1]), 1)

    img[DM & (LC == 80)] = (0.6, 0.75, 0.9, 1); img[DM & (LC == 50)] = (0.55, 0.55, 0.55, 1); return img


def side_legend(fig, ax, handles, ttl):

    p, x, w = side_layout(fig, ax); la = fig.add_axes([x, p.y0, w, p.y1 - p.y0]); la.set_xticks([]); la.set_yticks([])

    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)

    leg = la.legend(handles=handles, title=ttl, loc="upper left", fontsize=9, title_fontsize=10, frameon=False, borderaxespad=0.9,

                    alignment="left", handlelength=2.0, handleheight=1.3, labelspacing=0.75); leg.get_title().set_fontweight("bold"); return la


EXT2 = (EXT[0] - 2000, EXT[1] + 24000, EXT[2] - 9000, EXT[3])   # room on the east for the legend and below for the scale bar
EXTZ = (EXT[0] - 6000, EXT[1] + 9000, EXT[2] - 4000, EXT[3] + 11000)   # factor panels: zoomed out for the north arrow
GR_C = ["#a6d96a", "#fee08b", "#d7301f"]; GR_L = ["Low", "Moderate", "High"]
C5 = ["#1a9850", "#a6d96a", "#fee08b", "#fc8d59", "#d73027"]


def risk5(ax, name, labs, ttl, title_):
    c = rd(name); img = np.zeros(c.shape + (4,))
    for i, col in enumerate(C5): img[c == i + 1] = (*mpl.colors.to_rgb(col), 1)
    img[DM & (LC == 80)] = (*mpl.colors.to_rgb("#99bfe6"), 1); drape(ax, img)
    WARDS.boundary.plot(ax=ax, color="#333333", lw=0.5, ls="--", zorder=12); outline(ax, lw=1.4)
    for i, g in zip(WARDS.ward, WARDS.geometry):
        q = g.representative_point(); ax.text(q.x, q.y, "T" if i == "Town" else i, ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=45, path_effects=HALO)
    setup(ax, EXT2); title(ax, title_); narrow(ax, x=0.06); scalebar(ax, EXT2, 20, x=0.04, y=0.03); credit(ax)
    hd = [Patch(fc=c_, ec="#555555", lw=0.4, label=l) for c_, l in zip(C5, labs)] + [Patch(fc="#99bfe6", ec="#555555", lw=0.4, label="Water"),
          Line2D([], [], color="#333333", lw=0.6, ls="--", label="Ward boundary"), Line2D([], [], ls="", marker="$7$", color="#222222", ms=6, label="Ward number (T = town)")]
    legend(ax, hd, ttl, at=(0.985, 0.05), fs=10)
def map3():
    fig = plt.figure(figsize=(12.6, 9.6), dpi=200); ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); base(ax)
    risk5(ax, "erisk5", ["Very low (< 2)", "Low (2 – 5)", "Moderate (5 – 10)", "High (10 – 20)", "Very high (> 20)"], "Soil loss (t/ha/yr)", "Soil Erosion Risk")
    save(fig, "map3_classes")


# ---------------------------------------------------------------- map 4 gully-prone flow paths

def gully_lines(ax, color="#b2182b", z=20, it=1):
    g = rd("gully") == 1
    if it: g = nd.binary_dilation(g, iterations=it)   # wider so thin paths show at page size
    img = np.zeros(g.shape + (4,)); img[g] = (*mpl.colors.to_rgb(color), 1); ax.imshow(img, extent=GX, zorder=z, interpolation="nearest")

    g = rd("gully") == 1; g = nd.binary_dilation(g, iterations=1)   # one cell wider so thin paths show at page size

    img = np.zeros(g.shape + (4,)); img[g] = (*mpl.colors.to_rgb(color), 1); ax.imshow(img, extent=GX, zorder=z, interpolation="nearest")


def grisk_img(a=1.0):
    c = rd("grisk"); img = np.zeros(c.shape + (4,))
    for i, col in enumerate(GR_C): img[c == i + 1] = (*mpl.colors.to_rgb(col), a)
    img[DM & (LC == 80)] = (*mpl.colors.to_rgb("#99bfe6"), a); return img


def map4():
    fig = plt.figure(figsize=(12.6, 9.6), dpi=200); ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); base(ax)
    risk5(ax, "grisk5", ["Very low", "Low", "Moderate", "High", "Very high"], "Gully risk", "Gully Erosion Risk")
    save(fig, "map4_gully")


# ---------------------------------------------------------------- map 5 ward comparison (two choropleths)

def map5():

    fig = plt.figure(figsize=(12.4, 6.6), dpi=200)

    SP = [("(a) Soil Erosion", "mean", [0, 3.5, 4.5, 5.5, 7], "Mean soil loss (t/ha/yr)", ["< 3.5", "3.5 – 4.5", "4.5 – 5.5", "> 5.5"], "Oranges"),

          ("(b) Gully Erosion Risk", "ghi", [0, 10, 15, 20, 100], "Land at high gully risk (%)", ["< 10", "10 – 15", "15 – 20", "> 20"], "Reds")]

    for k, (ttl, col, br, lt, labs, cmn) in enumerate(SP):

        ax = fig.add_axes([0.01 + k * 0.495, 0.03, 0.48, 0.94]); ax.set_facecolor("white")

        cm = ListedColormap(plt.get_cmap(cmn)(np.linspace(0.15, 0.85, 4))); nrm = BoundaryNorm(br, 4)

        WARDS.plot(ax=ax, column=col, cmap=cm, norm=nrm, ec="#444444", lw=0.5, zorder=5)

        for i, g in zip(WARDS.ward, WARDS.geometry):

            q = g.representative_point(); ax.text(q.x, q.y, "T" if i == "Town" else i, ha="center", va="center", fontsize=7.5, fontweight="bold", zorder=45, path_effects=HALO)

        outline(ax, lw=1.3); setup(ax, EXT, tk=False); pnl_box(ax, ttl)

        legend(ax, [Patch(fc=cm(j), ec="#444444", lw=0.5, label=l) for j, l in enumerate(labs)], lt, at=(0.99, 0.02), fs=8.5)

        if k == 0: narrow(ax, x=0.06, y=0.8, r=0.05); scalebar(ax, EXT, 20, x=0.05, y=0.03)

    fig.text(0.5, 0.006, "T = Shurugwi town (13 urban wards combined)", ha="center", fontsize=8)

    fig.text(0.995, 0.006, AUTHOR, ha="right", va="bottom", fontsize=7)

    save(fig, "map5_wards")


# ---------------------------------------------------------------- map 6 close-up on high-resolution imagery

def map6():
    z = np.load("rast/esri.npz"); e = z["ext"]; win = tuple(z["win"])
    fig = plt.figure(figsize=(12.4, 4.9), dpi=200)
    for k in range(2):
        ax = fig.add_axes([0.01 + k * 0.495, 0.06, 0.48, 0.9]); ax.imshow(z["img"][..., :3], extent=(e[0], e[1], e[2], e[3]), zorder=0, interpolation="bilinear")
        if k:
            c = rd("grisk5"); img = np.zeros(c.shape + (4,))
            for q, al in ((5, 0.6), (4, 0.5), (3, 0.4)): img[c == q] = (*mpl.colors.to_rgb(C5[q - 1]), al)
            ax.imshow(img, extent=GX, zorder=5, interpolation="bilinear")
        setup(ax, win, tk=False); pnl_box(ax, ["(a) Satellite Image", "(b) Gully Erosion Risk"][k])
        if k == 0: narrow(ax, x=0.93, y=0.865, r=0.06, fg="#222222"); scalebar(ax, win, 2, x=0.05, y=0.06)
    legend(fig.axes[-1], [Patch(fc=C5[4], alpha=0.7, label="Very high"), Patch(fc=C5[3], alpha=0.7, label="High"), Patch(fc=C5[2], alpha=0.7, label="Moderate")], "Gully risk", at=(0.985, 0.03), fs=8.5)
    fig.text(0.01, 0.012, "Imagery: Esri, Maxar, Earthstar Geographics", ha="left", va="bottom", fontsize=7)
    fig.text(0.995, 0.012, AUTHOR, ha="right", va="bottom", fontsize=7)
    save(fig, "map6_closeup")


if __name__ == "__main__":

    for n in sys.argv[1:] or ["map1", "map2", "map3", "map4", "map6"]: globals()[n]()

