"""Maps for the Lake Kariba area, elevation, storage and level decline study. UTM 35S (EPSG:32735) with degree ticks.
Map 1 relief with side column and locator; maps 2 to 5 fill the frame, legend in the lower-right corner inside the map.
Writes out/map*.png and out/mapstats.json."""
import os, sys, json
import numpy as np, geopandas as gpd, rasterio, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from rasterio import features
from matplotlib.colors import LightSource, ListedColormap
from matplotlib.patches import Patch, Polygon, Rectangle
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy import ndimage as nd
import contextily as ctx

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
O = np.load("rast/occ.npz"); OCC = O["occ"]; TF = O["tf"]; RES = 60
GX = (TF[2], TF[2] + OCC.shape[1] * RES, TF[5] - OCC.shape[0] * RES, TF[5])
LAKE = np.load("rast/lake.npy"); BED = np.load("rast/bed.npz")["bed"]
ST = json.load(open("out/stats.json")); T_HI, T_LO = ST["hi"]["t"], ST["lo"]["t"]
W00 = LAKE & (OCC >= T_HI) & (OCC <= 100); W24 = LAKE & (OCC >= T_LO) & (OCC <= 100); EXPOSED = W00 & ~W24
TO = Transformer.from_crs(4326, 32735, always_xy=True); FROM = Transformer.from_crs(32735, 4326, always_xy=True)
CT = gpd.read_file("data/countries.geojson").to_crs(32735)
ZM = CT[CT.country_na == "Zambia"]; ZW = CT[CT.country_na == "Zimbabwe"]
BORDER = ZM.geometry.union_all().boundary.intersection(ZW.geometry.union_all().buffer(200))
EXL = (425000, 745000, 7985000, 8212000)            # whole lake, landscape
TOWNS = [("Kariba", 28.7755, -16.5273, 1, (2000, -6500)), ("Siavonga", 28.7102, -16.5365, 1, (-21000, 2500)), ("Binga", 27.3425, -17.6210, 1, (2000, -4200)),
         ("Sinazongwe", 27.4606, -17.2609, 1, (-27000, 2000)), ("Maamba", 27.2242, -17.355, 0, (-19000, -1500)), ("Chipepo", 27.8601, -16.8043, 0, (-6000, 3000)),
         ("Bumi Hills", 28.3500, -16.8170, 0, (2000, -4200))]
DAM = (28.7615, -16.5214)
BLUE = "#2b6cb0"


def u(lon, lat): return TO.transform(lon, lat)


def ticks(ax, ext, step=0.5):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0 = FROM.transform(ext[0], ym)[0]; lo1 = FROM.transform(ext[1], ym)[0]; la0 = FROM.transform(xm, ext[2])[1]; la1 = FROM.transform(xm, ext[3])[1]
    lons = np.arange(np.ceil(lo0 / step) * step, lo1, step); lats = np.arange(np.ceil(la0 / step) * step, la1, step)
    f = "{:.1f}" if step < 1 else "{:.0f}"
    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f.format(l) + "°E" for l in lons])
    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f.format(-l) + "°S" for l in lats])
    ax.tick_params(length=2.5, labelsize=8, top=True, right=True, labeltop=True, labelright=True)


def narrow(ax, x=0.06, y=0.875, r=0.05, fg="#222222", bg="white"):
    """Compass rose north arrow: four main points and four short ones, each split dark and light, N above."""
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, fg), (1, bg)):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec=fg, lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec=fg, lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.008, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=12, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])


def scalebar(ax, ext, length, x=0.04, y=0.045, fg="#222222", bg="white"):
    L = length * 1000; x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.012
    halo = [pe.withStroke(linewidth=3.5, foreground=bg)]
    ax.plot([x0, x0 + L], [y0, y0], color=fg, lw=1.3, zorder=60, solid_capstyle="butt", path_effects=halo)
    for i in range(5):
        xx = x0 + i * L / 4; hh = t if i in (0, 2, 4) else t * 0.55
        ax.plot([xx, xx], [y0, y0 + hh], color=fg, lw=1.1, zorder=60, path_effects=halo)
    for v, xx in [(0, x0), (length / 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(xx, y0 + t * 1.5, f"{v:g}", ha="center", va="bottom", fontsize=8.5, color=fg, zorder=60, path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])
    ax.text(x0 + L + (ext[1] - ext[0]) * 0.008, y0, "km", fontsize=8.5, va="center", color=fg, zorder=60, path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])


_BM = {}


def basemap(kind="osm"):
    """Humanitarian OSM tiles (zoom 10) fetched once, warped to UTM 35S and cached; faded, or inverted grey for the dark map."""
    if kind in _BM: return _BM[kind]
    f = "rast/basemap_hot.npz"
    if not os.path.exists(f):
        img, ext = ctx.bounds2img(25.9, -18.75, 29.7, -15.85, zoom=10, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:32735")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn = img.max(2), img.min(2)   # strip the tiles' grey dashed admin lines and grey roads
    grey = nd.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1) & ~nd.binary_dilation(mx < 110, iterations=3)
    med = np.stack([nd.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255
    if kind == "dark":
        g = 1 - img.mean(axis=2, keepdims=True); img = np.repeat(0.05 + 0.30 * g, 3, axis=2)
    else:
        img = 0.72 * img + 0.28
    e = d["ext"]; _BM[kind] = (np.clip(img, 0, 1), (e[0], e[1], e[2], e[3]))
    return _BM[kind]


def frame(title, ext, width=11.0, dark=False, step=0.5, bm=True):
    h = width * 0.9 * (ext[3] - ext[2]) / (ext[1] - ext[0]) / 0.88
    fig = plt.figure(figsize=(width, h), dpi=200); ax = fig.add_axes([0.05, 0.06, 0.9, 0.88])
    fg = "#e6e6e6" if dark else "#222222"; bg = "#0b0b0b" if dark else "white"; fig.patch.set_facecolor(bg)
    if bm:
        img, bext = basemap("dark" if dark else "osm"); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1); ticks(ax, ext, step)
    ax.tick_params(colors=fg); [t.set_color(fg) for t in ax.get_xticklabels() + ax.get_yticklabels()]
    for s_ in ax.spines.values(): s_.set_color(fg); s_.set_linewidth(0.7)
    ax.text(0.5, 0.965, title, transform=ax.transAxes, ha="center", va="top", fontsize=14, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground=bg)])
    narrow(ax, fg=fg, bg=bg)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color=fg, zorder=70, path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])
    return fig, ax, fg, bg


def legend_br(ax, handles, title, fs=9.5, fg="#222222", bg="white", at=(0.992, 0.04)):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=fg, facecolor=bg, framealpha=0.94, alignment="left", labelcolor=fg,
                    borderpad=0.7, handlelength=2.0, handleheight=1.1, labelspacing=0.5)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)
    return leg


def show(ax, mask, color, alpha=1.0, z=5):
    ax.imshow(np.ma.masked_where(~mask, mask), extent=GX, cmap=ListedColormap([color]), interpolation="nearest", alpha=alpha, zorder=z)


def classes(ax, a, bins, colors, z=5):
    for lo, hi, c in zip(bins[:-1], bins[1:], colors): show(ax, (a >= lo) & (a < hi), c, z=z)


def towns(ax, fg="black", bg="white", fs=8, sel=None):
    for n, lo, la, big, (dx, dy) in TOWNS:
        if sel and n not in sel: continue
        x, y = u(lo, la)
        ax.plot(x, y, "s" if big else "o", ms=5.5 if big else 4, mfc=bg, mec=fg, mew=0.9, zorder=30, clip_on=True)
        ax.text(x + dx, y + dy, n, fontsize=fs + (0.5 if big else 0), fontweight="bold" if big else "normal", color=fg, zorder=30, clip_on=True,
                path_effects=[pe.withStroke(linewidth=2.2, foreground=bg)])


def border(ax, color="#555555", alpha=0.45, lw=0.8):
    gpd.GeoSeries([BORDER], crs=32735).plot(ax=ax, color=color, lw=lw, alpha=alpha, zorder=20)


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.15); plt.close(fig); print("saved", name)


def countries(ax, ext):
    """Zambia and Zimbabwe drawn as land names, each inside its own country."""
    for n, lo, la in (("ZAMBIA", 27.25, -16.55), ("ZIMBABWE", 28.35, -17.75)):
        x, y = u(lo, la)
        if ext[0] < x < ext[1] and ext[2] < y < ext[3]:
            ax.text(x, y, n, fontsize=10, color="#666666", style="italic", ha="center", zorder=25, path_effects=HALO)


# ---------------------------------------------------------------- map 1 study area (relief, side column, locator)
def map1():
    with rasterio.open("rast/dem.tif") as d: dem = d.read(1).astype(np.float32); db = d.bounds
    dem[dem < -100] = np.nan; dem = np.where(np.isnan(dem), np.nanmedian(dem), dem)
    hs = LightSource(azdeg=315, altdeg=40).hillshade(dem, vert_exag=6, dx=150, dy=150)
    rgb = plt.get_cmap("gist_earth")(mpl.colors.Normalize(300, 1500)(dem))[..., :3]
    img = 0.45 * rgb * (0.4 + 0.6 * hs[..., None]) + 0.55 * np.repeat((0.55 + 0.45 * hs)[..., None], 3, 2)
    ext = EXL
    fig = plt.figure(figsize=(10.4, 6.4), dpi=200); ax = fig.add_axes([0.04, 0.07, 0.66, 0.86])
    ax.imshow(img, extent=(db.left, db.right, db.bottom, db.top), zorder=0, interpolation="bilinear")
    show(ax, LAKE | ((OCC >= 1) & (OCC <= 100) & nd.binary_dilation(LAKE, iterations=2)), "#4f8fd0", z=5)
    ax.plot(*u(*DAM), marker="^", ms=8, mfc="#c0392b", mec="black", mew=0.8, zorder=31)
    ax.text(u(*DAM)[0] + 1500, u(*DAM)[1] + 4000, "Kariba Dam", fontsize=8, fontweight="bold", zorder=31, path_effects=HALO)
    towns(ax, sel=[t[0] for t in TOWNS])
    countries(ax, ext)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1, anchor="W"); ticks(ax, ext)
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    ax.text(0.5, 0.965, "Study Area Map", transform=ax.transAxes, ha="center", va="top", fontsize=14, fontweight="bold", zorder=70, path_effects=HALO)
    narrow(ax); scalebar(ax, ext, 50, x=0.62, y=0.05)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="#333333", zorder=70, path_effects=HALO)
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.05; w = 0.985 - x; gap = 0.03; h = (p.y1 - p.y0 - gap) / 2
    la = fig.add_axes([x, p.y0 + h + gap, w, h]); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    hd = [Patch(fc="#4f8fd0", ec="none", label="Lake Kariba"), Line2D([], [], marker="^", ls="", ms=8, mfc="#c0392b", mec="black", label="Kariba Dam"),
          Line2D([], [], marker="s", ls="", ms=5.5, mfc="white", mec="black", label="Towns"), Line2D([], [], marker="o", ls="", ms=4, mfc="white", mec="black", label="Villages")]
    leg = la.legend(handles=hd, title="Legend", loc="upper left", fontsize=9.5, title_fontsize=10.5, frameon=False, borderaxespad=0.8,
                    alignment="left", handlelength=2.2, handleheight=1.3, labelspacing=0.8); leg.get_title().set_fontweight("bold")
    lo = fig.add_axes([x, p.y0, w, h]); lo.set_facecolor("white")
    CT.plot(ax=lo, fc="#eeeeee", ec="white", lw=0.4); ZM.plot(ax=lo, fc="#c8d6c0", ec="white", lw=0.4); ZW.plot(ax=lo, fc="#e3d3b4", ec="white", lw=0.4)
    show(lo, LAKE, "#1f5fa8")
    lo.set_xlim(-300000, 1350000); lo.set_ylim(7350000, 9100000); lo.set_aspect(1); lo.set_xticks([]); lo.set_yticks([])
    for s_ in lo.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    lo.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=lo.transAxes, fc="white", ec="none", zorder=5))
    lo.plot([0, 1], [0.86, 0.86], transform=lo.transAxes, color="#222222", lw=0.6, zorder=6)
    lo.text(0.5, 0.93, "Zambia And Zimbabwe", transform=lo.transAxes, ha="center", va="center", fontsize=10, fontweight="bold", zorder=7)
    for n, lo_, la_ in (("Zambia", 26.3, -13.8), ("Zimbabwe", 30.0, -19.4)):
        lo.text(*u(lo_, la_), n, fontsize=8, ha="center", style="italic", zorder=8)
    save(fig, "map1_study_area")


# ---------------------------------------------------------------- map 2 water occurrence
OCC_B = [1, 25, 50, 75, 95, 101]; OCC_C = ["#fde68a", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"]; OCC_L = ["< 25", "25 – 50", "50 – 75", "75 – 95", "≥ 95"]


def map2():
    fig, ax, fg, bg = frame("Lake Kariba Extent Map (2000 and 2024)", EXL)
    show(ax, W24, "#2b6cb0", z=4); show(ax, EXPOSED, "#e8590c", z=5)
    towns(ax, sel=["Kariba", "Siavonga", "Binga", "Sinazongwe"]); countries(ax, EXL)
    legend_br(ax, [Patch(fc="#2b6cb0", label="Water (2024)"), Patch(fc="#e8590c", label="Dried lake bed")], "Lake Kariba")
    scalebar(ax, EXL, 50, x=0.56, y=0.05)
    save(fig, "map2_extent")


# ---------------------------------------------------------------- map 3 exposed lake bed at three shores (small multiples)
SITES = [("a", "Kariba District Shore"), ("b", "Binga District Shore"), ("c", "Sinazongwe District Shore")]


def map3():
    fig = plt.figure(figsize=(11.0, 8.0), dpi=200)
    L, B, Wd, Ht, top = 0.04, 0.04, 0.92, 0.84, 0.88
    cw, ch = Wd / 2, Ht / 2
    fig.text(0.5, 0.925, "Dried Lake Bed Map (2000 to 2024)", ha="center", va="center", fontsize=14, fontweight="bold")
    for n, (k, name) in enumerate(SITES):
        r, c = divmod(n, 2)
        ax = fig.add_axes([L + c * cw, B + (1 - r) * ch, cw, ch])
        with rasterio.open(f"rast/rgb_{k}.tif") as d: im = d.read([1, 2, 3]).transpose(1, 2, 0) / 255; b = d.bounds
        g = im.mean(2); g = 0.25 + 0.75 * g
        ax.imshow(np.repeat(g[..., None], 3, 2), extent=(b.left, b.right, b.bottom, b.top), zorder=0, interpolation="bilinear")
        show(ax, EXPOSED, "#e8590c", alpha=0.78, z=5); show(ax, W24, "#2b6cb0", alpha=0.55, z=4)
        ax.set_xlim(b.left, b.right); ax.set_ylim(b.bottom, b.top); ax.set_aspect(1); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.8)
        ax.text(0.02, 0.97, f"({k}) {name}", transform=ax.transAxes, ha="left", va="top", fontsize=10, fontweight="bold", zorder=70,
                bbox=dict(fc="white", ec="#222222", lw=0.5, pad=2.5))
        lon, lat = FROM.transform((b.left + b.right) / 2, (b.bottom + b.top) / 2)
        ax.text(0.98, 0.03, f"{lon:.2f}°E {-lat:.2f}°S", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, zorder=70, path_effects=HALO)
        if n == 0: ext_a = (b.left, b.right, b.bottom, b.top)
    sp = fig.add_axes([L + cw, B, cw, ch]); sp.set_xlim(0, 1); sp.set_ylim(0, 1); sp.set_xticks([]); sp.set_yticks([])
    for s_ in sp.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.8)
    narrow(sp, x=0.14, y=0.66, r=0.11)
    hd = [Patch(fc="#2b6cb0", alpha=0.55, label="Water (2024)"), Patch(fc="#e8590c", alpha=0.78, label="Dried lake bed")]
    leg = sp.legend(handles=hd, title="Lake Kariba", loc="upper left", bbox_to_anchor=(0.3, 0.92), fontsize=9.5, title_fontsize=10.5, frameon=False,
                    alignment="left", handlelength=2.0, handleheight=1.2, labelspacing=0.7); leg.get_title().set_fontweight("bold")
    # scale bar in the spare cell, at the panels' scale (each panel is 28 km wide)
    k_ = 10 / 28.0; x0 = 0.3; y0 = 0.3
    sp.plot([x0, x0 + k_], [y0, y0], color="#222222", lw=1.3, solid_capstyle="butt")
    for i in range(5):
        xx = x0 + i * k_ / 4; sp.plot([xx, xx], [y0, y0 + (0.03 if i % 2 == 0 else 0.017)], color="#222222", lw=1.1)
    for v, xx in ((0, x0), (5, x0 + k_ / 2), (10, x0 + k_)): sp.text(xx, y0 + 0.045, f"{v}", ha="center", va="bottom", fontsize=8.5)
    sp.text(x0 + k_ + 0.03, y0, "km", va="center", fontsize=8.5)
    sp.text(0.98, 0.03, AUTHOR, transform=sp.transAxes, ha="right", va="bottom", fontsize=7, color="#444444")
    save(fig, "map3_exposed")


# ---------------------------------------------------------------- map 4 lake bed elevation in the drawdown zone (eastern basin)
EXE = (610000, 727000, 8118000, 8182000)
BED_B = [475.5, 477, 479, 481, 483, 485, 487.5]; BED_C = ["#7a0177", "#c51b8a", "#f768a1", "#fbb4b9", "#fde0c5", "#fff7e0"]
BED_L = ["475.5 – 477", "477 – 479", "479 – 481", "481 – 483", "483 – 485", "> 485"]


def map4():
    fig, ax, fg, bg = frame("Drawdown Zone Bed Elevation Map", EXE, step=0.2)
    a = np.where(LAKE & (OCC < 100), BED, np.nan)
    classes(ax, np.nan_to_num(a, nan=0), BED_B, BED_C)
    show(ax, LAKE & ((OCC == 100) | (np.nan_to_num(BED, nan=0) < 475.5)) & (OCC <= 100), "#1f4e8c", z=5)
    towns(ax, sel=["Kariba", "Siavonga", "Bumi Hills"])
    ax.plot(*u(*DAM), marker="^", ms=7, mfc="#c0392b", mec="black", mew=0.8, zorder=31)
    hd = [Patch(fc="#1f4e8c", label="< 475.5")] + [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(BED_C, BED_L)]
    legend_br(ax, hd, "Bed elevation (m)")
    scalebar(ax, EXE, 10, x=0.52, y=0.05)
    save(fig, "map4_bed_elevation")


# ---------------------------------------------------------------- map 5 shoreline retreat (dark)
RET_B = [0, 250, 500, 1000, 2000, 1e9]; RET_C = ["#fff5b8", "#fec44f", "#fe9929", "#ec7014", "#cc4c02"]
RET_L = ["< 250", "250 – 500", "500 – 1 000", "1 000 – 2 000", "> 2 000"]


def retreat():
    edge = W00 & ~nd.binary_erosion(W00, iterations=1)
    d = nd.distance_transform_edt(~W24) * RES
    return edge, np.where(edge, d, np.nan)


def map5():
    edge, d = retreat()
    fig, ax, fg, bg = frame("Shoreline Retreat Map (2000 to 2024)", EXL, dark=True)
    show(ax, W24, "#16324f", z=3)
    big = nd.grey_dilation(np.nan_to_num(d, nan=-1), size=5); big = np.where(big >= 0, big, np.nan)
    for lo, hi, c in zip(RET_B[:-1], RET_B[1:], RET_C): show(ax, (big >= lo) & (big < hi), c, z=5 + lo / 1e4)
    towns(ax, fg="#e6e6e6", bg="#0b0b0b", sel=["Kariba", "Siavonga", "Binga", "Sinazongwe"])
    legend_br(ax, [Patch(fc=c, label=l) for c, l in zip(RET_C, RET_L)] + [Patch(fc="#16324f", ec="#888888", lw=0.4, label="Water (2024)")],
              "Shoreline retreat (m)", fg=fg, bg=bg)
    scalebar(ax, EXL, 50, x=0.56, y=0.05, fg=fg, bg=bg)
    save(fig, "map5_retreat")


def mapstats():
    with rasterio.open("rast/occ_0.tif") as d: crs = d.crs
    tf = rasterio.Affine(*TF)
    cz = features.rasterize([(g, 1) for g in ZM.geometry] + [(g, 2) for g in ZW.geometry], out_shape=OCC.shape, transform=tf)
    a = RES * RES / 1e6
    edge, d = retreat(); dv = d[edge]
    out = dict(exposed_km2=round(EXPOSED.sum() * a, 1), w00_km2=round(W00.sum() * a, 1), w24_km2=round(W24.sum() * a, 1),
               exposed_zm=round((EXPOSED & (cz == 1)).sum() * a, 1), exposed_zw=round((EXPOSED & (cz == 2)).sum() * a, 1),
               lake_zm=round((W00 & (cz == 1)).sum() * a, 1), lake_zw=round((W00 & (cz == 2)).sum() * a, 1),
               retreat_median=round(float(np.median(dv)), 0), retreat_p90=round(float(np.percentile(dv, 90)), 0), retreat_max=round(float(dv.max()), 0),
               retreat_share=[round(float(((dv >= lo) & (dv < hi)).mean() * 100), 1) for lo, hi in zip(RET_B[:-1], RET_B[1:])],
               retreat_med_zm=round(float(np.median(d[edge & (cz == 1)])), 0), retreat_med_zw=round(float(np.median(d[edge & (cz == 2)])), 0),
               shore_km_2000=round(edge.sum() * RES / 1000, 0),
               occ_share=[round(float(((OCC >= lo) & (OCC < hi) & LAKE).sum() / LAKE.sum() * 100), 1) for lo, hi in zip(OCC_B[:-1], OCC_B[1:])],
               bed_share=[round(float(((BED >= lo) & (BED < hi) & LAKE & (OCC < 100)).sum() * a), 1) for lo, hi in zip(BED_B[:-1], BED_B[1:])],
               bed_share_east=None)
    r0, c0 = int((GX[3] - EXE[3]) / RES), int((EXE[0] - GX[0]) / RES); r1, c1 = int((GX[3] - EXE[2]) / RES), int((EXE[1] - GX[0]) / RES)
    win = np.zeros(OCC.shape, bool); win[r0:r1, c0:c1] = True
    out["exposed_east_km2"] = round((EXPOSED & win).sum() * a, 1)
    # exposed bed in each 28 x 18 km Map 3 window (centres as in fetch_rgb.py)
    for k, (x, y) in {"a": (707940, 8157120), "b": (608280, 8118720), "c": (546720, 8071200)}.items():
        r0, c0 = int((GX[3] - (y + 9000)) / RES), int((x - 14000 - GX[0]) / RES); r1, c1 = int((GX[3] - (y - 9000)) / RES), int((x + 14000 - GX[0]) / RES)
        w = np.zeros(OCC.shape, bool); w[max(r0, 0):r1, max(c0, 0):c1] = True; out[f"exposed_site_{k}"] = round((EXPOSED & w).sum() * a, 1)
    dd = np.where(edge, d, 0); r, c = np.unravel_index(dd.argmax(), dd.shape)
    out["retreat_max_xy"] = [round(GX[0] + (c + 0.5) * RES), round(GX[3] - (r + 0.5) * RES)]
    json.dump(out, open("out/mapstats.json", "w"), indent=1); print(out)


if __name__ == "__main__":
    for n in sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "mapstats"]: globals()[n]()
