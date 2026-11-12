"""Maps for the Chimanimani flood susceptibility study (factor reclassification and AHP weighted overlay).
UTM 36S (EPSG:32736) with degree ticks; legends boxed in the lower-right corner; titles above the frame."""
import os, json
import numpy as np, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy import ndimage as nd

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834
GX = (X0, X0 + W * RES, Y0 - H * RES, Y0)
PAD = 6000
EXD = (GX[0] - PAD, GX[1] + PAD, GX[2] - PAD, GX[3] + PAD)   # zoomed out a little round the district
EXW = (GX[0] - 9000, GX[1] + 14500, GX[2] - 14500, GX[3] + 14500)   # zoomed out inside the 15 km DEM buffer; legend sits on the map, lower right
S = dict(np.load("rast/stack.npz")); M = S["mask"] == 1
ST = json.load(open("out/overlay.json"))
TO = Transformer.from_crs(4326, 32736, always_xy=True); FROM = Transformer.from_crs(32736, 4326, always_xy=True)
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(32736)
chim = dist[dist.district == "Chimanimani"]
TOWNS = [("Chimanimani", 32.8707, -19.8040, 1), ("Cashel", 32.7906, -19.5420, 0), ("Mutambara", 32.6889, -19.5290, 0),
         ("Nyanyadzi", 32.4240, -19.7700, 0), ("Chakohwa", 32.5184, -19.5470, 0), ("Hot Springs", 32.4712, -19.6530, 0),
         ("Machongwe", 32.8247, -19.9230, 0), ("Rusitu", 32.8650, -20.0330, 0), ("Nhedziwa", 32.6523, -19.5540, 0),
         ("Chikukwa", 32.9293, -19.7120, 0)]
CLS_C = ["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c"]
CLS_N = ["Very low", "Low", "Moderate", "High", "Very high"]


def u(lon, lat): return TO.transform(lon, lat)
def sp(v): return f"{v:,.0f}".replace(",", " ")


def hillshade():
    f = "rast/hs.npy"
    if not os.path.exists(f):
        np.save(f, LightSource(azdeg=315, altdeg=40).hillshade(S["elev"], vert_exag=1.5, dx=RES, dy=RES).astype(np.float32))
    return np.load(f)


def ticks(ax, ext, step=0.1):
    ym, xm = (ext[2] + ext[3]) / 2, (ext[0] + ext[1]) / 2
    lo0, la0 = FROM.transform(ext[0], ext[2]); lo1, la1 = FROM.transform(ext[1], ext[3])
    lons = np.arange(np.ceil(lo0 / step) * step, lo1, step); lats = np.arange(np.ceil(la0 / step) * step, la1, step)
    ax.set_xticks([u(l, FROM.transform(xm, ym)[1])[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons])
    ax.set_yticks([u(FROM.transform(xm, ym)[0], l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats])
    ax.tick_params(length=2.5, labelsize=8, top=True, right=True, labeltop=True, labelright=True)


def narrow(ax, x=0.08, y=0.875, r=0.05):
    """Compass rose north arrow: four main points and four short ones, each split dark and light, N above."""
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, "#222222"), (1, "white")):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec="#222222", lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec="#222222", lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.008, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=12, fontweight="bold", zorder=70, path_effects=HALO)


def scalebar(ax, ext, length, x=0.04, y=0.045):
    L = length * 1000; x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.012
    ax.plot([x0, x0 + L], [y0, y0], color="#222222", lw=1.3, zorder=60, solid_capstyle="butt", path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])
    for i in range(5):
        xx = x0 + i * L / 4; hh = t if i in (0, 2, 4) else t * 0.55
        ax.plot([xx, xx], [y0, y0 + hh], color="#222222", lw=1.1, zorder=60, path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    for v, xx in [(0, x0), (length / 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(xx, y0 + t * 1.5, f"{v:g}", ha="center", va="bottom", fontsize=8.5, zorder=60, path_effects=HALO)
    ax.text(x0 + L * 1.07, y0, "km", fontsize=8.5, va="center", zorder=60, path_effects=HALO)


def frame(title, ext=EXD, size=(11.2, 8.4), side=True):
    if side:
        fig = plt.figure(figsize=size, dpi=200); ax = fig.add_axes([0.04, 0.07, 0.60, 0.86])
    else:   # map fills the frame; legend goes in the lower-right corner inside it
        wd = 10.0; hh = wd * 0.88 * (ext[3] - ext[2]) / (ext[1] - ext[0]) / 0.86
        fig = plt.figure(figsize=(wd, hh), dpi=200); ax = fig.add_axes([0.06, 0.07, 0.88, 0.86])
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1, anchor="W"); ticks(ax, ext)
    ax.set_facecolor("#eeeeee")
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    if side:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=22)   # above the frame, clear of the top tick labels
    else:   # inside the map frame at the top, in the margin left above the district
        ax.text(0.5, 0.975, title, transform=ax.transAxes, ha="center", va="top", fontsize=14, fontweight="bold", zorder=70, path_effects=HALO)
    narrow(ax)
    ax.text(0.988, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="#444444", zorder=70, path_effects=HALO)
    return fig, ax


EXT = (GX[0] - 3000, GX[1] + 30000, GX[2] - 4000, GX[3] + 11000)   # district pushed left so the legend sits clear of it, lower right


def wide(title, ext=EXT, H=7.0, col=0.0):
    """Landscape layout: map on the left with the title inside at the top, legend column on the right."""
    mw = H * 0.88 * (ext[1] - ext[0]) / (ext[3] - ext[2]); W = 0.65 + mw + 0.75 + col
    fig = plt.figure(figsize=(W, H), dpi=200); ax = fig.add_axes([0.65 / W, 0.07, mw / W, 0.88])
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1, anchor="W"); ticks(ax, ext)
    ax.set_facecolor("#eeeeee")
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    ax.text(0.5, 0.975, title, transform=ax.transAxes, ha="center", va="top", fontsize=15, fontweight="bold", zorder=70, path_effects=HALO)
    narrow(ax)
    ax.text(0.988, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color="#444444", zorder=70, path_effects=HALO)
    return fig, ax


def legend_col(fig, ax, handles, title, fs=11):
    """Legend in the right-hand column, centred on the map's height."""
    p = ax.get_position(); x = p.x1 + 0.75 / fig.get_figwidth()
    leg = fig.legend(handles=handles, title=title, loc="center left", bbox_to_anchor=(x, (p.y0 + p.y1) / 2), fontsize=fs, title_fontsize=fs + 1,
                     frameon=True, fancybox=False, edgecolor="#222222", facecolor="white", alignment="left",
                     borderpad=0.8, handlelength=2.2, handleheight=1.2, labelspacing=0.55)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold")


def boxes(fig, ax, gap=0.03):
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.06; w = 0.985 - x; h = (p.y1 - p.y0 - gap) / 2
    return [x, p.y0 + h + gap, w, h], [x, p.y0, w, h]


def legend_side(fig, ax, handles, title, fs=9.5):
    up, _ = boxes(fig, ax); la = fig.add_axes(up); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
    leg = la.legend(handles=handles, title=title, loc="upper left", fontsize=fs, title_fontsize=fs + 0.5, frameon=False, borderaxespad=0.8,
                    alignment="left", handlelength=2.2, handleheight=1.3, labelspacing=0.75)
    leg.get_title().set_fontweight("bold")


def legend_br(ax, handles, title, fs=9, loc="lower right", at=(0.992, 0.04)):
    """Framed legend in the lower-right corner inside the map, the attribution under it."""
    leg = ax.legend(handles=handles, title=title, loc=loc, bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor="#222222", facecolor="white", framealpha=0.94, alignment="left",
                    borderpad=0.6, handlelength=2.0, handleheight=1.1, labelspacing=0.42)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold")


import rasterio
with rasterio.open("rast/dem_buf.tif") as d_: DB = d_.read(1).astype(np.float32); BX = (d_.bounds.left, d_.bounds.right, d_.bounds.bottom, d_.bounds.top)
MB = np.zeros(DB.shape, bool); c0, r0 = int((X0 - BX[0]) / RES), int((BX[3] - Y0) / RES); MB[r0:r0 + H, c0:c0 + W] = M


def base(ax, fade=0.55, tint=False):
    """Hillshade (tinted by elevation if asked) on the 15 km buffered DEM, faded outside the district."""
    f = "rast/hsb.npy"
    if not os.path.exists(f):
        np.save(f, LightSource(azdeg=315, altdeg=40).hillshade(DB, vert_exag=1.5, dx=RES, dy=RES).astype(np.float32))
    hs = np.load(f)
    grey = np.repeat((0.55 + 0.45 * hs)[..., None], 3, 2)
    if tint:   # elevation colours inside the district only; grey hillshade outside, so the buffer edge blends into the frame
        rgb = plt.get_cmap("gist_earth")(mpl.colors.Normalize(0, 2600)(DB))[..., :3]
        img = rgb * (0.35 + 0.65 * hs[..., None]); fade = 0.6
    else:
        img = grey
    img = np.where(MB[..., None], img, grey * (1 - fade) + fade)
    ax.imshow(img, extent=BX, zorder=0, interpolation="bilinear")


def rivers(ax, a=50, color="#3a7dc9"):
    up = S["upa"]
    for thr, it in ((a, 1), (1000, 2)):
        k = nd.binary_dilation(up >= thr, iterations=it) if it > 1 else up >= thr
        k = (nd.maximum_filter(k, 3) & M)[::2, ::2]   # drawn inside the district only
        ax.imshow(np.ma.masked_where(~k, k), extent=GX, cmap=ListedColormap([color]), zorder=3, interpolation="nearest", alpha=0.9)


def towns(ax, fs=7.5, sel=None):
    for n, lo, la, big in TOWNS:
        if sel and n not in sel: continue
        x, y = u(lo, la)
        ax.plot(x, y, "s" if big else "o", ms=6 if big else 4, mfc="white", mec="black", mew=0.9, zorder=30, clip_on=True)
        ax.text(x + 900, y + 500, n, fontsize=fs + (1 if big else 0), fontweight="bold" if big else "normal", zorder=30, path_effects=HALO, clip_on=True)


def finish(fig, ax, text, name, ext=EXD, km=10):
    scalebar(ax, ext, km)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.text(0, -0.05, text, transform=ax.transAxes, fontsize=6.5, ha="left", va="top", wrap=True)
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig); print("saved", name)


# ---- reclassification tables (shared with the page) -----------------------------------------
R = dict(np.load("rast/scores.npz"))
FAC = [("driver", "Distance to river (m)", ["> 2 000", "1 000 – 2 000", "500 – 1 000", "250 – 500", "< 250"]),
       ("slope", "Slope (degrees)", ["> 25", "15 – 25", "10 – 15", "5 – 10", "< 5"]),
       ("elev", "Elevation (m)", ["> 1 600", "1 300 – 1 600", "1 000 – 1 300", "700 – 1 000", "< 700"]),
       ("twi", "Topographic wetness index", ["< 6", "6 – 7", "7 – 8", "8 – 10", "> 10"]),
       ("rain", "Mean annual rainfall (mm)", ["< 800", "800 – 950", "950 – 1 100", "1 100 – 1 250", "> 1 250"]),
       ("dd", "Drainage density (km/km²)", ["< 0.3", "0.3 – 0.6", "0.6 – 0.9", "0.9 – 1.2", "> 1.2"]),
       ("lulc", "Land use and land cover", ["Trees", "Rangeland", "Cropland", "Built area, bare ground", "Water, flooded vegetation"]),
       ("clay", "Soil clay content (%)", ["< 28", "28 – 30", "30 – 32", "32 – 34", "> 34"])]
CMAP = ListedColormap(CLS_C); NORM = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], 5)


# ---- map 1: study area ----------------------------------------------------------------------
def map1():
    fig, ax = wide("Study Area Map")
    base(ax, tint=True); rivers(ax)
    chim.boundary.plot(ax=ax, color="#111111", lw=1.1, zorder=7); towns(ax)
    for n, lo, la, rot in (("Rusitu River", 32.80, -19.99, -20), ("Nyanyadzi River", 32.60, -19.73, 25)):
        ax.text(*u(lo, la), n, fontsize=7, color="#1f5fa8", style="italic", rotation=rot, ha="center", zorder=9, path_effects=HALO)
    cm = plt.get_cmap("gist_earth"); nrm = mpl.colors.Normalize(0, 2600)
    el = [(300, "< 600"), (600, "600 – 1 000"), (1000, "1 000 – 1 400"), (1400, "1 400 – 1 800"), (1800, "> 1 800")]
    hs_ = [Patch(fc=cm(nrm(v + 150)), ec="#777777", lw=0.4, label=l) for v, l in el][::-1]
    hs_ += [Line2D([], [], color="#3a7dc9", lw=1.6, label="River"),
            Line2D([], [], color="#111111", lw=1.1, label="District boundary")]
    legend_br(ax, hs_, "Elevation (m)", fs=9.5, at=(0.992, 0.035))
    finish(fig, ax, "Source: Copernicus GLO-30 DEM (30 m, hillshaded); rivers derived from the DEM by flow accumulation; district boundary "
           "OCHA COD-AB 2023; place names OpenStreetMap. UTM zone 36S (WGS 84).", "map1_study_area", ext=EXT)


# ---- map 2: the eight reclassified factors on one layout ---------------------------------------
def map2():
    fig = plt.figure(figsize=(13.6, 10.2), dpi=200)
    aw = 0.215; ah = aw * 13.6 / 10.2 * (GX[3] - GX[2]) / (GX[1] - GX[0])
    xs = [0.035 + i * 0.2435 for i in range(4)]; ys = [0.60, 0.155]
    hs = hillshade()[::2, ::2]
    for n, (k, name, labs) in enumerate(FAC):
        ax = fig.add_axes([xs[n % 4], ys[n // 4], aw, ah]); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.6)
        ax.imshow(np.ma.masked_where(~M[::2, ::2], hs), extent=GX, cmap="Greys_r", vmin=0, vmax=1.2, zorder=0, interpolation="bilinear")
        sc = np.ma.masked_where(~M[::2, ::2], R[k][::2, ::2])
        ax.imshow(sc, extent=GX, cmap=CMAP, norm=NORM, alpha=0.88, zorder=1, interpolation="nearest")
        chim.boundary.plot(ax=ax, color="#111111", lw=0.6, zorder=3)
        ax.set_xlim(GX[0], GX[1]); ax.set_ylim(GX[2], GX[3]); ax.set_aspect(1)
        ax.set_title(f"({'abcdefgh'[n]}) {name}", fontsize=9.5, fontweight="bold", loc="center")
        ax.text(0.03, 0.97, f"Weight {ST['weights'][k] * 100:.1f} %", transform=ax.transAxes, ha="left", va="top", fontsize=8.5,
                fontweight="bold", zorder=70, bbox=dict(fc="white", ec="#222222", lw=0.5, pad=2.5))
        h = [Patch(fc=CLS_C[i], ec="#555555", lw=0.4, label=f"{labs[i]}") for i in range(5)][::-1]
        leg = ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, -0.01), fontsize=7.5, frameon=False, ncol=1,
                        handlelength=1.6, handleheight=1.0, labelspacing=0.3, borderaxespad=0.2)
        if n == 0: narrow(ax, x=0.9, y=0.84, r=0.07); scalebar(ax, GX, 20, x=0.05, y=0.04)
    h = [Patch(fc=CLS_C[i], ec="#555555", lw=0.4, label=f"{i + 1}  {CLS_N[i]}") for i in range(5)][::-1]
    fig.legend(handles=h, title="Susceptibility score", loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=5, fontsize=8.5, title_fontsize=9, frameon=False).get_title().set_fontweight("bold")
    fig.suptitle("Reclassified Flood Conditioning Factors", fontsize=14, fontweight="bold", y=0.985)
    fig.text(0.985, 0.004, AUTHOR, ha="right", va="bottom", fontsize=7, color="#444444")
    fig.savefig("out/map2_factors.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig); print("saved map2")


# ---- map 3: flood susceptibility ------------------------------------------------------------
def map3():
    fig, ax = wide("Flood Susceptibility Map")
    base(ax, fade=0.6)
    cls = np.load("rast/fcls.npy")
    ax.imshow(np.ma.masked_where(cls == 0, cls), extent=GX, cmap=CMAP, norm=NORM, alpha=0.8, zorder=2, interpolation="nearest")
    chim.boundary.plot(ax=ax, color="#111111", lw=1.1, zorder=7)
    towns(ax, sel=["Chimanimani", "Nyanyadzi", "Cashel", "Machongwe", "Mutambara", "Hot Springs", "Rusitu", "Chikukwa"])
    C = ST["classes"]
    hs_ = [Patch(fc=CLS_C[i], ec="#555555", lw=0.4, alpha=0.8, label=f"{CLS_N[i]}  ({C[i]['pct']:.1f} %)") for i in range(5)][::-1]
    hs_ += [Line2D([], [], color="#111111", lw=1.1, label="District boundary")]
    legend_br(ax, hs_, "Flood susceptibility", fs=9.5, at=(0.992, 0.035))
    finish(fig, ax, "Source: weighted overlay of eight reclassified factors (AHP weights, consistency ratio 0.02), classes by natural breaks. Factors from "
           "Copernicus GLO-30 DEM, CHIRPS 1991 to 2020, Esri 2018 land cover and OpenLandMap soil. UTM zone 36S (WGS 84).", "map3_susceptibility", ext=EXT)


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3"]): globals()[f]()
