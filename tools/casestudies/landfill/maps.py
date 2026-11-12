"""Maps for the Bulawayo landfill site selection study. UTM 35S (EPSG:32735) with degree ticks. Writes out/map*.png."""
import json, sys
import numpy as np, geopandas as gpd, rasterio, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy import ndimage as nd
from shapely.geometry import LineString

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
AUTHOR = "© Kudzanai Chakavarika"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
TO = Transformer.from_crs(4326, 32735, always_xy=True); FROM = Transformer.from_crs(32735, 4326, always_xy=True)


def rd(n): return rasterio.open(f"rast/{n}.tif").read(1)


_s = rasterio.open("rast/lc.tif"); T = _s.transform; GX = (T.c, T.c + _s.width * 30, T.f - _s.height * 30, T.f)
CITY = gpd.read_file("data/bulawayo.gpkg"); CM = rd("city") == 1
b = CITY.total_bounds; CX, CY = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
EXT = (CX - 27500, CX + 27500, CY - 18300, CY + 18300)      # landscape frame (1.5 : 1)
SUIT_C = ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"]; SUIT_L = ["Very low", "Low", "Moderate", "High", "Very high"]
GREY = "#cfcfcf"


def osm_lines(name):
    geo, tags = [], []
    for e in json.load(open(f"data/osm_{name}.json")):
        if e["type"] == "way" and len(e.get("geometry", [])) > 1:
            geo.append(LineString([(q["lon"], q["lat"]) for q in e["geometry"]])); tags.append(e.get("tags", {}))
    return gpd.GeoDataFrame({"tags": tags}, geometry=geo, crs=4326).to_crs(32735)


RIV = osm_lines("rivers"); ROAD = osm_lines("roads")
RIV["big"] = RIV.tags.apply(lambda t: t.get("waterway") == "river")
LF = gpd.read_file("out/landfill.gpkg"); SITES = gpd.read_file("out/sites.gpkg")
AERO = [e for e in json.load(open("data/osm_aero.json")) if e.get("tags", {}).get("name", "").startswith("Joshua")][0]
AX, AY = TO.transform(np.mean([q["lon"] for q in AERO["geometry"]]), np.mean([q["lat"] for q in AERO["geometry"]]))


def u(lon, lat): return TO.transform(lon, lat)


def ticks(ax, ext, step=0.1):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0 = FROM.transform(ext[0], ym)[0]; lo1 = FROM.transform(ext[1], ym)[0]; la0 = FROM.transform(xm, ext[2])[1]; la1 = FROM.transform(xm, ext[3])[1]
    lons = np.arange(np.ceil(lo0 / step) * step, lo1, step); lats = np.arange(np.ceil(la0 / step) * step, la1, step)
    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons])
    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats])
    ax.tick_params(length=2.5, labelsize=8, top=True, right=True, labeltop=True, labelright=True)


def narrow(ax, x=0.06, y=0.875, r=0.05, fg="#222222", bg="white"):
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, fg), (1, bg)):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec=fg, lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec=fg, lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.008, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=12, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])


def scalebar(ax, ext, length, x=0.04, y=0.045, fg="#222222"):
    L = length * 1000; x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.012
    halo = [pe.withStroke(linewidth=3.5, foreground="white")]
    ax.plot([x0, x0 + L], [y0, y0], color=fg, lw=1.3, zorder=60, solid_capstyle="butt", path_effects=halo, clip_on=False)
    for i in range(5):
        xx = x0 + i * L / 4; hh = t if i in (0, 2, 4) else t * 0.55
        ax.plot([xx, xx], [y0, y0 + hh], color=fg, lw=1.1, zorder=60, path_effects=halo, clip_on=False)
    for v, xx in [(0, x0), (length / 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(xx, y0 + t * 1.5, f"{v:g}", ha="center", va="bottom", fontsize=8.5, color=fg, zorder=60, path_effects=HALO)
    ax.text(x0 + L * 1.06, y0, "km", fontsize=8.5, va="center", color=fg, zorder=60, path_effects=HALO)


_BM = {}


def basemap():
    if "b" in _BM: return _BM["b"]
    d = np.load("rast/basemap_hot.npz"); img = d["img"][..., :3].astype(float)
    mx, mn = img.max(2), img.min(2)
    grey = nd.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1) & ~nd.binary_dilation(mx < 110, iterations=3)
    med = np.stack([nd.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255; img = 0.72 * img + 0.28
    e = d["ext"]; _BM["b"] = (np.clip(img, 0, 1), (e[0], e[1], e[2], e[3])); return _BM["b"]


def lift(ax):
    """City raised off the basemap: soft shadow, then a white face."""
    for i, (dx, a) in enumerate([(700, 0.10), (450, 0.14), (250, 0.18)]):
        CITY.translate(dx, -dx).plot(ax=ax, fc="black", ec="none", alpha=a, zorder=2 + i * 0.1)
    CITY.plot(ax=ax, fc="white", ec="none", zorder=3)


def outline(ax, lw=1.2, z=40): CITY.boundary.plot(ax=ax, color="#222222", lw=lw, zorder=z)


def frame(title, ext=EXT, width=11.0):
    h = width * 0.9 * (ext[3] - ext[2]) / (ext[1] - ext[0]) / 0.88
    fig = plt.figure(figsize=(width, h), dpi=200); ax = fig.add_axes([0.05, 0.06, 0.9, 0.88])
    img, bext = basemap(); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1); ticks(ax, ext)
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    ax.text(0.5, 0.965, title, transform=ax.transAxes, ha="center", va="top", fontsize=14, fontweight="bold", zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    narrow(ax)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, zorder=70, path_effects=HALO)
    return fig, ax


def legend_br(ax, handles, title, at=(0.992, 0.04), fs=9.5, loc="lower right", frame=True):
    leg = ax.legend(handles=handles, title=title, loc=loc, bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=frame, fancybox=False, edgecolor="#222222", facecolor="white", framealpha=0.94, alignment="left",
                    borderpad=0.7, handlelength=2.0, handleheight=1.1, labelspacing=0.5)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold"); return leg


def show(ax, mask, color, alpha=1.0, z=5, ext=GX):
    ax.imshow(np.ma.masked_where(~mask, mask), extent=ext, cmap=ListedColormap([color]), interpolation="nearest", alpha=alpha, zorder=z)


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15); plt.close(fig); print("saved", name)


def pnl_box(ax, s):
    ax.text(0.03, 0.97, s, transform=ax.transAxes, ha="left", va="top", fontsize=8.5, fontweight="bold", zorder=70,
            bbox=dict(fc="white", ec="#222222", lw=0.5, pad=2.0))


def side_frame(ax):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.8)


# ---------------------------------------------------------------- map 1 study area
def map1():
    fig = plt.figure(figsize=(10.4, 6.4), dpi=200); ax = fig.add_axes([0.04, 0.07, 0.66, 0.86])
    ext = (b[0] - 6500, b[2] + 6500, b[1] - 2500, b[3] + 2500)
    img, bext = basemap(); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    CITY.plot(ax=ax, fc="#f3e9d2", ec="none", alpha=0.55, zorder=2)
    RIV[RIV.big].plot(ax=ax, color="#2b6cb0", lw=1.0, alpha=0.45, zorder=10); RIV[~RIV.big].plot(ax=ax, color="#4f8fd0", lw=0.5, alpha=0.35, zorder=10)
    ROAD.plot(ax=ax, color="#555555", lw=0.7, alpha=0.4, zorder=11)
    outline(ax, lw=1.6)
    ax.plot(LF.centroid.x, LF.centroid.y, "s", ms=8, mfc="#c0392b", mec="black", mew=0.8, zorder=31)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1, anchor="W"); ticks(ax, ext)
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    ax.text(0.5, 0.965, "Study Area Map", transform=ax.transAxes, ha="center", va="top", fontsize=14, fontweight="bold", zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    narrow(ax); scalebar(ax, ext, 10, x=0.6, y=0.05)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, zorder=70, path_effects=HALO)
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.05; w = 0.985 - x; gap = 0.03; h = (p.y1 - p.y0 - gap) / 2
    la = fig.add_axes([x, p.y0, w, h]); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    hd = [Patch(fc="#f3e9d2", ec="#222222", lw=1.2, label="City boundary"), Line2D([], [], color="#2b6cb0", lw=1.0, alpha=0.45, label="Rivers"),
          Line2D([], [], color="#555555", lw=0.7, alpha=0.4, label="Main roads"),
          Line2D([], [], marker="s", ls="", ms=8, mfc="#c0392b", mec="black", label="Existing landfills")]
    leg = la.legend(handles=hd, title="Legend", loc="upper left", fontsize=9.5, title_fontsize=10.5, frameon=False, borderaxespad=0.8,
                    alignment="left", handlelength=2.2, handleheight=1.3, labelspacing=0.8); leg.get_title().set_fontweight("bold")
    lo = fig.add_axes([x, p.y0 + h + gap, w, h]); lo.set_facecolor("white")
    pv = gpd.read_file("../population/data/districts.gpkg").to_crs(32735).dissolve("province")
    pv.plot(ax=lo, fc="#eeeeee", ec="#888888", lw=0.4); CITY.plot(ax=lo, fc="#c0392b", ec="#c0392b", lw=1.5)
    pb = pv.total_bounds; cx, cy = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2; hw = (pb[2] - pb[0]) / 2 * 1.08
    lo.set_xlim(cx - hw, cx + hw); lo.set_ylim(cy - hw * 0.92, cy + hw * 1.25); lo.set_aspect(1); lo.set_xticks([]); lo.set_yticks([])
    for s_ in lo.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    lo.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=lo.transAxes, fc="white", ec="none", zorder=5))
    lo.plot([0, 1], [0.86, 0.86], transform=lo.transAxes, color="#222222", lw=0.6, zorder=6)
    lo.text(0.5, 0.93, "Zimbabwe", transform=lo.transAxes, ha="center", va="center", fontsize=10, fontweight="bold", zorder=7)
    save(fig, "map1_study_area")


# ---------------------------------------------------------------- map 2 factor scores (small multiples)
FACT = ["(a) Distance From Settlements", "(b) Distance From Surface Water", "(c) Soil Clay", "(d) Slope", "(e) Distance To Roads", "(f) Land Cover"]


def city_ext(pad=1200): return (b[0] - pad, b[2] + pad, b[1] - pad, b[3] + pad)


def suit_panel(ax, a, ext):
    img, bext = basemap(); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear"); lift(ax)
    for c in range(1, 6): show(ax, CM & (a == c), SUIT_C[c - 1], z=5)
    outline(ax, lw=0.9); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.8)


def map2():
    e0 = city_ext(2500); ext = (e0[0], e0[1], e0[2], e0[3] + 3000); cw = 2.75; ch = cw * (ext[3] - ext[2]) / (ext[1] - ext[0]); strip = 0.55
    W, H = 4 * cw, 2 * ch + strip; fig = plt.figure(figsize=(W, H), dpi=200)
    fig.text(0.5, 1 - strip / 2 / H, "Factor Suitability Maps", ha="center", va="center", fontsize=14, fontweight="bold")
    for i in range(6):
        r, c = divmod(i, 4); ax = fig.add_axes([c / 4, (1 - r) * ch / H, 1 / 4, ch / H])
        suit_panel(ax, rd(f"f{i}"), ext); pnl_box(ax, FACT[i])
    sp = fig.add_axes([2 / 4, 0, 2 / 4, ch / H]); side_frame(sp)
    narrow(sp, x=0.1, y=0.62, r=0.14)
    hd = [Patch(fc=SUIT_C[k], ec="#555555", lw=0.4, label=SUIT_L[k]) for k in range(4, -1, -1)]
    legend_br(sp, hd, "Suitability", at=(0.42, 0.55), loc="center left", frame=False)
    # scale bar at panel scale: the spare cell is two panels wide, so its x span is twice a panel's
    sb = fig.add_axes([2 / 4, 0, 1 / 4, ch / H]); sb.set_xlim(ext[0], ext[1]); sb.set_ylim(ext[2], ext[3]); sb.set_aspect(1); sb.axis("off")
    scalebar(sb, ext, 10, x=0.06, y=0.1)
    sp.text(0.99, 0.02, AUTHOR, transform=sp.transAxes, ha="right", va="bottom", fontsize=7)
    save(fig, "map2_factors")


# ---------------------------------------------------------------- map 3 exclusion zones
def map3():
    fig, ax = frame("Constraint Zones Map"); lift(ax)
    mask = rd("mask") == 1
    show(ax, CM & ~mask, "#9e3a26", z=5); show(ax, mask, "#f1dfa5", z=5); outline(ax)
    legend_br(ax, [Patch(fc="#9e3a26", label="Constrained land"), Patch(fc="#f1dfa5", label="Unconstrained land")], "Land")
    scalebar(ax, EXT, 10, x=0.62, y=0.05); save(fig, "map3_exclusion")


# ---------------------------------------------------------------- map 4 suitability
def map4():
    fig, ax = frame("Landfill Suitability Map"); lift(ax)
    s = rd("suit")
    for c in range(1, 6): show(ax, s == c, SUIT_C[c - 1], z=6)
    outline(ax)
    hd = [Patch(fc=SUIT_C[k], ec="#555555", lw=0.4, label=SUIT_L[k]) for k in range(4, -1, -1)]
    legend_br(ax, hd, "Suitability"); scalebar(ax, EXT, 10, x=0.62, y=0.05); save(fig, "map4_suitability")


# ---------------------------------------------------------------- map 5 candidate sites over the satellite image
def map5(win=6500):
    s2 = rasterio.open("rast/s2.tif"); im = s2.read([1, 2, 3]).transpose(1, 2, 0) / 255; sb_ = s2.bounds
    g = 0.25 + 0.75 * im.mean(2); grey = np.repeat(g[..., None], 3, 2); SX = (sb_.left, sb_.right, sb_.bottom, sb_.top)
    sett = rd("sett") == 1
    items = [(f"({chr(97 + i)}) Site {r.site} ({r.ha:.0f} ha)", r.geometry, "site") for i, r in SITES.iterrows()]
    items.append((f"({chr(97 + len(items))}) Richmond Landfill", LF.geometry.iloc[0], "lf"))
    cw = 3.6; strip = 0.55; W, H = 3 * cw, 2 * cw + strip; fig = plt.figure(figsize=(W, H), dpi=200)
    fig.text(0.5, 1 - strip / 2 / H, "Candidate Landfill Sites Map", ha="center", va="center", fontsize=14, fontweight="bold")
    for i, (lab, geom, kind) in enumerate(items):
        r, c = divmod(i, 3); ax = fig.add_axes([c / 3, (1 - r) * cw / H, 1 / 3, cw / H])
        x, y = geom.centroid.x, geom.centroid.y; e = (x - win / 2, x + win / 2, y - win / 2, y + win / 2)
        ax.imshow(grey, extent=SX, zorder=0, interpolation="bilinear")
        show(ax, sett, "#e8590c", alpha=0.55, z=4)
        ROAD.plot(ax=ax, color="white", lw=2.2, zorder=9); ROAD.plot(ax=ax, color="#333333", lw=1.0, zorder=10)
        RIV.plot(ax=ax, color="#2b6cb0", lw=1.2, zorder=10)
        col = "#ffd43b" if kind == "site" else "#c0392b"
        gs = gpd.GeoSeries([geom]).boundary
        gs.plot(ax=ax, color="black", lw=3.2, zorder=20); gs.plot(ax=ax, color=col, lw=1.9, zorder=21)
        ax.set_xlim(e[0], e[1]); ax.set_ylim(e[2], e[3]); ax.set_aspect(1); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.8)
        pnl_box(ax, lab)
        lon, lat = FROM.transform(x, y)
        ax.text(0.97, 0.03, f"{lon:.2f}°E {-lat:.2f}°S", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, zorder=70, path_effects=HALO)
    sp = fig.add_axes([2 / 3, 0, 1 / 3, cw / H]); side_frame(sp)
    narrow(sp, x=0.15, y=0.8, r=0.09)
    hd = [Patch(fc="none", ec="#ffd43b", lw=2, label="Candidate sites"), Patch(fc="none", ec="#c0392b", lw=2, label="Existing landfill"),
          Patch(fc="#e8590c", alpha=0.55, label="Settlements"), Line2D([], [], color="#333333", lw=1.0, label="Main roads"),
          Line2D([], [], color="#2b6cb0", lw=1.2, label="Rivers")]
    legend_br(sp, hd, "Legend", at=(0.32, 0.58), loc="center left", frame=False)
    sb = fig.add_axes([2 / 3, 0, 1 / 3, cw / H]); sb.set_xlim(0, win); sb.set_ylim(0, win); sb.axis("off")
    scalebar(sb, (0, win, 0, win), 2, x=0.08, y=0.1)
    sp.text(0.99, 0.02, AUTHOR, transform=sp.transAxes, ha="right", va="bottom", fontsize=7)
    save(fig, "map5_sites")


if __name__ == "__main__":
    for m in sys.argv[1:] or ["map1", "map2", "map4", "map5"]: globals()[m]()
