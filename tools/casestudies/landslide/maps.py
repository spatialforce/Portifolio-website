"""Maps for the Chimanimani landslide susceptibility study (factor reclassification and AHP weighted overlay).
UTM 36S (EPSG:32736) with degree ticks on all four sides; framed title strip above each map; outer frame round the page.
Run from this folder after overlay.py. Output: out/*.png"""
import os, json
import numpy as np, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from pyproj import Transformer
from scipy import ndimage as nd

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
F = "../chimanimani_flood/"
AUTHOR = "© Kudzanai Chakavarika"; FG = "#222222"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
X0, Y0, RES, W, H = 430000, 7860000, 30, 2600, 2834
GX = (X0, X0 + W * RES, Y0 - H * RES, Y0)
S = dict(np.load(F + "rast/stack.npz")); M = S["mask"] == 1
R = dict(np.load("rast/scores.npz")); CLS = np.load("rast/lcls.npy"); ST = json.load(open("out/overlay.json"))
TO = Transformer.from_crs(4326, 32736, always_xy=True); FROM = Transformer.from_crs(32736, 4326, always_xy=True)
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(32736); chim = dist[dist.district == "Chimanimani"]
prov = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(32736)
VILL = [("Chimanimani", 32.8707, -19.8040), ("Cashel", 32.7906, -19.5420), ("Mutambara", 32.6889, -19.5290),
        ("Nyanyadzi", 32.4240, -19.7700), ("Chakohwa", 32.5184, -19.5470), ("Hot Springs", 32.4712, -19.6530),
        ("Machongwe", 32.8247, -19.9230), ("Rusitu", 32.8650, -20.0330), ("Nhedziwa", 32.6523, -19.5540),
        ("Chikukwa", 32.9293, -19.7120)]
CLS_C = ["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"]
CLS_N = ["Very low", "Low", "Moderate", "High", "Very high"]
CMAP = ListedColormap(CLS_C); NORM = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], 5)
CX, CY = (GX[0] + GX[1]) / 2, (GX[2] + GX[3]) / 2; HY = (GX[3] - GX[2]) / 2 + 7000; HXW = HY * 1.75
EXT = (CX - HXW, CX + HXW, CY - HY, CY + HY)          # landscape, about 1.75 : 1, district centred
FACE = "#f1f1f1"


def u(lon, lat): return TO.transform(lon, lat)


def hs():
    f = F + "rast/hs.npy"
    if not os.path.exists(f):
        np.save(f, LightSource(azdeg=315, altdeg=40).hillshade(S["elev"], vert_exag=1.5, dx=RES, dy=RES).astype(np.float32))
    return np.load(f)


def ticks(ax, ext, step=0.2, fs=8):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0, _ = FROM.transform(ext[0], ym); lo1, _ = FROM.transform(ext[1], ym); _, la0 = FROM.transform(xm, ext[2]); _, la1 = FROM.transform(xm, ext[3])
    lons = np.arange(np.ceil(lo0 / step - 1e-9) * step, lo1, step); lats = np.arange(np.ceil(la0 / step - 1e-9) * step, la1, step)
    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons], fontsize=fs)
    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats], fontsize=fs)
    ax.tick_params(length=2.5, top=True, right=True, labeltop=True, labelright=True, colors=FG)
    ax.tick_params(axis="y", labelrotation=90)
    plt.setp(ax.yaxis.get_ticklabels(), va="center")


def header(fig, ax, title, fs=13, h=0.052, gap=0.008):
    """Framed title strip directly above the map frame, same width as the map."""
    ax.apply_aspect(); p = ax.get_position()
    fig.canvas.draw(); tb = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    hx = fig.add_axes([p.x0, max(p.y1, tb.y1) + gap, p.width, h]); hx.set_xticks([]); hx.set_yticks([]); hx.set_facecolor("white")
    for s_ in hx.spines.values(): s_.set_color(FG); s_.set_linewidth(0.8)
    hx.text(0.5, 0.5, title, ha="center", va="center", fontsize=fs, fontweight="bold", color=FG)
    return hx


def narrow(ax, x, y, h=0.085):
    """Two-tone north arrow; (x, y) is the tip, in axes fraction."""
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, FG), (w, "white")):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=FG, lw=0.9, transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11, fontweight="bold", color=FG, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])


def scalebar(ax, ext, km, x=0.03, y=0.05, fs=8):
    L = km * 1000; x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.014
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, t, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=70))
    for v, xx in [(0, x0), (km / 2, x0 + L / 2), (km, x0 + L)]:
        ax.text(xx, y0 + t * 1.6, f"{v:g}", ha="center", va="bottom", fontsize=fs, zorder=70, path_effects=HALO)
    ax.text(x0 + L + (ext[1] - ext[0]) * 0.008, y0 + t / 2, "km", fontsize=fs, va="center", zorder=70, path_effects=HALO)


def legend_in(ax, handles, title, fs=9.5, at=(0.993, 0.05)):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=FG, facecolor="white", framealpha=1, borderpad=0.7, alignment="left",
                    handlelength=2.0, handleheight=1.1, labelspacing=0.5)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.set_zorder(90)
    ax.text(at[0], 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=90)
    return leg


def source(ax, text, y=-0.075):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.5, ha="left", va="top")


def save(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def frame(title, wd=10.0):
    ht = wd * 0.9 / ((EXT[1] - EXT[0]) / (EXT[3] - EXT[2])) / 0.8
    fig = plt.figure(figsize=(wd, ht), dpi=200); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.05, 0.1, 0.9, 0.8]); ax.set_facecolor(FACE)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(1); ticks(ax, EXT)
    for s_ in ax.spines.values(): s_.set_color(FG); s_.set_linewidth(0.8)
    header(fig, ax, title); narrow(ax, 0.045, 0.965)
    return fig, ax


def shade(rgb, k=0.38):
    return rgb * ((1 - k) + k * hs())[..., None]


def classed(arr, colours):
    rgba = np.zeros(arr.shape + (4,))
    for v, c in colours.items():
        m = (arr == v) & M; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    return rgba


def rivers(ax, color="#3a7dc9"):
    up = S["upa"]
    for thr, it in ((50, 1), (1000, 2)):
        k = nd.binary_dilation(up >= thr, iterations=it) if it > 1 else up >= thr
        k = (nd.maximum_filter(k, 3) & M)[::2, ::2]
        ax.imshow(np.ma.masked_where(~k, k), extent=GX, cmap=ListedColormap([color]), zorder=3, interpolation="nearest", alpha=0.9)


def outline(ax, lw=1.1): chim.boundary.plot(ax=ax, color="#111111", lw=lw, zorder=7)


def villages(ax, fs=8, sel=None):
    for n, lo, la in VILL:
        if sel and n not in sel: continue
        x, y = u(lo, la)
        ax.plot(x, y, "o", ms=4.2, mfc="white", mec="black", mew=0.9, zorder=30)
        ax.text(x + 1000, y + 600, n, fontsize=fs, zorder=30, path_effects=HALO)


def locator(ax, box=(0.775, 0.5, 0.215, 0.475)):
    la = ax.inset_axes(list(box)); la.set_zorder(85); la.set_facecolor("white")
    prov.plot(ax=la, fc="#e3e3e3", ec="white", lw=0.5)
    prov[prov.adm1_name == "Manicaland"].plot(ax=la, fc="#bdbdbd", ec="white", lw=0.5)
    chim.plot(ax=la, fc="#b30000", ec="none")
    x0, y0, x1, y1 = prov.total_bounds; px, py = (x1 - x0) * 0.05, (y1 - y0) * 0.05
    la.set_xlim(x0 - px, x1 + px); la.set_ylim(y0 - py, y1 + py * 4.2); la.set_aspect(1, adjustable="datalim"); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color(FG); s_.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.87), 1, 0.13, transform=la.transAxes, fc="white", ec=FG, lw=0.6, zorder=5))
    la.text(0.5, 0.935, "Manicaland, Zimbabwe", transform=la.transAxes, ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=6)


# ---- map 1: study area ----------------------------------------------------------------------
ELEV = [(0, 600, "#6a9a58", "< 600"), (600, 1000, "#b5c77a", "600 – 1 000"), (1000, 1400, "#e9dc9b", "1 000 – 1 400"),
        (1400, 1800, "#d1a46a", "1 400 – 1 800"), (1800, 9999, "#9c6a43", "> 1 800")]


def map1():
    fig, ax = frame("Study Area Map")
    e = S["elev"]; rgba = np.zeros(e.shape + (4,))
    for lo, hi, c, _ in ELEV:
        m = (e >= lo) & (e < hi) & M; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    rgba[..., :3] = shade(rgba[..., :3])
    ax.imshow(rgba, extent=GX, zorder=1, interpolation="bilinear")
    rivers(ax); outline(ax); villages(ax); locator(ax)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in ELEV][::-1]
    h += [Line2D([], [], color="#3a7dc9", lw=1.6, label="Rivers"),
          Line2D([], [], ls="none", marker="o", ms=5, mfc="white", mec="black", label="Villages"),
          Line2D([], [], color="#111111", lw=1.1, label="District boundary")]
    legend_in(ax, h, "Elevation (m)"); scalebar(ax, EXT, 20)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])
    source(ax, "Source: Copernicus GLO-30 DEM (hillshaded); rivers from the DEM by flow accumulation; boundaries OCHA COD-AB; place names OpenStreetMap. UTM zone 36S (WGS 84).")
    save(fig, "map1_study_area")


# ---- map 2: the eight reclassified factors ----------------------------------------------------
FAC = [("slope", "Slope"), ("rain", "Annual rainfall"), ("lulc", "Land cover"), ("clay", "Soil clay"),
       ("curv", "Curvature"), ("dstream", "Distance to streams"), ("elev", "Elevation"), ("aspect", "Aspect")]


RAMP = {"slope": ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],      # reds
        "rain": ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"],       # blues
        "lulc": ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"],       # greens
        "clay": ["#ffffd4", "#fed98e", "#fe9929", "#d95f0e", "#993404"],       # browns
        "curv": ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],       # purples
        "dstream": ["#f6eff7", "#bdc9e1", "#67a9cf", "#1c9099", "#016c59"],    # teals
        "elev": ["#f7f7f7", "#cccccc", "#969696", "#636363", "#252525"],       # greys
        "aspect": ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"]}     # pinks


def map2():
    wd = 10.0; cw = 0.29; aw = (GX[1] - GX[0]) / (GX[3] - GX[2])
    chh = cw * wd / aw                     # panel height in inches
    hh = 0.32; gap = 0.42; top = 0.62; bot = 0.55
    ht = top + 3 * (hh + chh) + 2 * gap + bot
    fig = plt.figure(figsize=(wd, ht), dpi=200); fig.patch.set_facecolor("white")
    xs = [0.045 + i * (cw + 0.03) for i in range(3)]
    shd = hs()[::2, ::2]; m2 = M[::2, ::2]
    axes = []
    for n in range(9):
        r, c = divmod(n, 3)
        y = (bot + (2 - r) * (chh + hh + gap)) / ht
        ax = fig.add_axes([xs[c], y, cw, chh / ht]); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color(FG); s_.set_linewidth(0.7)
        ax.set_xlim(GX[0], GX[1]); ax.set_ylim(GX[2], GX[3]); ax.set_aspect(1)
        axes.append(ax)
        if n == 8: continue
        k, name = FAC[n]
        sc = R[k][::2, ::2]; rgba = np.zeros(sc.shape + (4,))
        for v in range(1, 6):
            mm = (sc == v) & m2; rgba[mm, :3] = mpl.colors.to_rgb(RAMP[k][v - 1]); rgba[mm, 3] = 1
        rgba[..., :3] *= (0.72 + 0.28 * shd)[..., None]
        ax.imshow(rgba, extent=GX, zorder=1, interpolation="nearest")
        chim.boundary.plot(ax=ax, color="#111111", lw=0.6, zorder=3)
        ax.set_xlim(GX[0], GX[1]); ax.set_ylim(GX[2], GX[3])
        header(fig, ax, f"({'abcdefgh'[n]}) {name}", fs=10, h=hh / ht, gap=0.05 / ht)
    la = axes[8]; la.set_facecolor("white")
    la.text(0.06, 0.74, "Factor score", transform=la.transAxes, ha="left", va="center", fontsize=10.5, fontweight="bold")
    sw, sh, gx0, gy0 = 0.055, 0.075, 0.06, 0.66         # swatch grid: columns a to h, rows very high to very low
    for j, (k, _) in enumerate(FAC):
        la.text(gx0 + j * (sw + 0.012) + sw / 2, gy0, "abcdefgh"[j], transform=la.transAxes, ha="center", va="bottom", fontsize=8.5)
        for i in range(5):
            la.add_patch(Rectangle((gx0 + j * (sw + 0.012), gy0 - 0.01 - (i + 1) * (sh + 0.01)), sw, sh, transform=la.transAxes,
                                   fc=RAMP[k][4 - i], ec="#777777", lw=0.4))
    for i in range(5):
        la.text(gx0 + 8 * (sw + 0.012) + 0.01, gy0 - 0.01 - (i + 1) * (sh + 0.01) + sh / 2, CLS_N[4 - i], transform=la.transAxes,
                ha="left", va="center", fontsize=9)
    narrow(la, 0.5, 0.93, h=0.13)
    sx = GX[0] + 0.2 * (GX[1] - GX[0]); L = 30000; yb = GX[2] + 0.1 * (GX[3] - GX[2]); t = (GX[3] - GX[2]) * 0.02
    for i in range(4):
        la.add_patch(Rectangle((sx + i * L / 4, yb), L / 4, t, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=70))
    for v, xx in [(0, sx), (15, sx + L / 2), (30, sx + L)]: la.text(xx, yb + t * 1.6, f"{v}", ha="center", va="bottom", fontsize=8)
    la.text(sx + L + 1800, yb + t / 2, "km", fontsize=8, va="center")
    la.text(0.97, 0.02, AUTHOR, transform=la.transAxes, ha="right", va="bottom", fontsize=7, color="#555555")
    x0 = xs[0]; x1 = xs[2] + cw; y1 = (ht - top + 0.12) / ht
    hx = fig.add_axes([x0, y1, x1 - x0, 0.38 / ht]); hx.set_xticks([]); hx.set_yticks([])
    for s_ in hx.spines.values(): s_.set_color(FG); s_.set_linewidth(0.8)
    hx.text(0.5, 0.5, "Reclassified Landslide Conditioning Factors", ha="center", va="center", fontsize=13, fontweight="bold")
    fig.text(x0, (bot - 0.12) / ht, "Source: Copernicus GLO-30 DEM; CHIRPS 1991 to 2020; Esri 2018 land cover; OpenLandMap clay. Scores 1 (very low) to 5 (very high).",
             fontsize=7.5, ha="left", va="top")
    save(fig, "map2_factors")


# ---- map 3: landslide susceptibility --------------------------------------------------------
def map3():
    fig, ax = frame("Landslide Susceptibility Map")
    rgba = classed(CLS, dict(zip(range(1, 6), CLS_C))); rgba[..., :3] = shade(rgba[..., :3], 0.3)
    ax.imshow(rgba, extent=GX, zorder=1, interpolation="nearest")
    outline(ax); villages(ax)
    h = [Patch(fc=CLS_C[i], ec="#777777", lw=0.4, label=CLS_N[i]) for i in range(5)][::-1]
    h += [Line2D([], [], ls="none", marker="o", ms=5, mfc="white", mec="black", label="Villages"),
          Line2D([], [], color="#111111", lw=1.1, label="District boundary")]
    legend_in(ax, h, "Susceptibility"); scalebar(ax, EXT, 20)
    source(ax, "Source: weighted overlay of eight reclassified factors with AHP weights; classes by natural breaks. UTM zone 36S (WGS 84).")
    save(fig, "map3_susceptibility")


# ---- map 4: mapped landslides over the classes ----------------------------------------------
def map4():
    fig, ax = frame("Mapped Landslides and Susceptibility")
    rgba = classed(CLS, dict(zip(range(1, 6), CLS_C))); rgba[..., :3] = shade(rgba[..., :3], 0.3); rgba[..., 3] *= 0.75
    ax.imshow(rgba, extent=GX, zorder=1, interpolation="nearest")
    p = gpd.read_file(F + "data/dl/idai-landslide-source-points").to_crs(32736)
    p = p[p.within(chim.geometry.iloc[0])]
    ax.plot(p.geometry.x, p.geometry.y, ".", ms=0.7, color="#1d1d6b", alpha=0.7, ls="none", zorder=20)
    outline(ax); villages(ax, sel=["Chimanimani", "Machongwe", "Rusitu", "Chikukwa", "Cashel", "Nyanyadzi"])
    h = [Patch(fc=CLS_C[i], ec="#777777", lw=0.4, alpha=0.75, label=CLS_N[i]) for i in range(5)][::-1]
    h += [Line2D([], [], ls="none", marker="o", ms=3.5, color="#1d1d6b", label="Landslides"),
          Line2D([], [], ls="none", marker="o", ms=5, mfc="white", mec="black", label="Villages"),
          Line2D([], [], color="#111111", lw=1.1, label="District boundary")]
    legend_in(ax, h, "Susceptibility"); scalebar(ax, EXT, 20)
    source(ax, "Source: this study; landslide source points mapped after March 2019 (RMCA, 2025). UTM zone 36S (WGS 84).")
    print("points in district", len(p))
    save(fig, "map4_landslides")


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4"]): globals()[f]()
