"""Six maps for case study 2: rainfall variability and drought in Zimbabwe (CHIRPS, 1991/92 to 2024/25).
Layout copied from ../population/maps.py. Run with PROJ_LIB set (see .projlib). Output: out/*.png"""
import os
import numpy as np, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import LightSource, BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
ASPECT = 1 / np.cos(np.radians(19))
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
LK = "../../corridors/raw/ne_10m_lakes.zip"
B = "../population/raw/bnd/"
world = gpd.read_file(f"zip://{NE}").cx[20:38, -26:-12]
lakes = gpd.read_file(f"zip://{LK}").cx[25:33.2, -22.6:-15.4]
prov = gpd.read_file(B + "zwe_admin1.shp")
zwe = gpd.read_file(B + "zwe_admin0.shp")
SADC = ["AGO", "BWA", "COM", "COD", "SWZ", "LSO", "MDG", "MWI", "MUS", "MOZ", "NAM", "SYC", "ZAF", "TZA", "ZMB", "ZWE"]
africa = gpd.read_file(f"zip://{NE}").cx[5:60, -40:10]
AUTHOR = "© Kudzanai Chakavarika"
CITIES = [("Harare", 31.052, -17.829), ("Bulawayo", 28.583, -20.150), ("Mutare", 32.670, -18.970), ("Gweru", 29.817, -19.450),
          ("Masvingo", 30.833, -20.074), ("Chinhoyi", 30.199, -17.367), ("Hwange", 26.500, -18.364), ("Victoria Falls", 25.840, -17.932),
          ("Beitbridge", 30.000, -22.217), ("Kariba", 28.800, -16.517), ("Gwanda", 29.000, -20.940), ("Chiredzi", 31.667, -21.050),
          ("Chipinge", 32.623, -20.188), ("Bindura", 31.330, -17.302)]
G = np.load("data/grids.npz")
with rasterio.open("rast/seasons.tif") as r:
    S = r.read().astype(float); RB = r.bounds
REXT = (RB.left, RB.right, RB.bottom, RB.top)
M0 = G["m0"]; S[:, ~M0] = np.nan
Y = np.arange(1991, 2025)
lat = RB.top - (np.arange(M0.shape[0]) + 0.5) * (RB.top - RB.bottom) / M0.shape[0]
WGT = np.cos(np.radians(lat))[:, None] * np.ones((1, M0.shape[1]))


def share(mask):
    return 100 * WGT[mask & M0].sum() / WGT[M0].sum()


# Layout: map frame on the left, a side column on the right for the legend (or colour bar) and the Harare
# enlargement, so nothing is drawn on top of the map. The title sits inside the map at the top centre.
EXT = (25.0, 33.2, -22.6, -14.85)
MAIN = [0.035, 0.07, 0.60, 0.88]
TY = 0.965          # vertical position of the title inside the map (axes fraction)
GAP = 0.03          # gap between the two equal boxes in the side column


def frame(title, dark=False, size=(11.6, 8.6), top=EXT[3]):
    fig = plt.figure(figsize=size, dpi=220); ax = fig.add_axes(MAIN)
    fg = "#dddddd" if dark else "#222222"; bg = "black" if dark else "white"
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg if dark else "#f4f4f4")
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], top); ax.set_aspect(ASPECT, anchor="W")
    ax.set_xticks(range(26, 34)); ax.set_yticks(range(-22, -14))
    ax.set_xticklabels([f"{x}°E" for x in range(26, 34)], color=fg); ax.set_yticklabels([f"{-y}°S" for y in range(-22, -14)], color=fg)
    ax.grid(color="#555555" if dark else "#bbbbbb", lw=0.3, ls=":"); ax.tick_params(length=2, colors=fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color=fg, zorder=50)
    # north arrow in the top-left corner, its tip level with the middle of the title
    yt = EXT[2] + TY * (top - EXT[2])
    ax.annotate("", xy=(25.3, yt), xytext=(25.3, yt - 0.5), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=fg, lw=1.2), zorder=20)
    ax.text(25.3, yt - 0.55, "N", ha="center", va="top", fontsize=10, fontweight="bold", color=fg, zorder=20)
    # attribution in the empty lower-right corner
    ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#999999" if dark else "#777777", zorder=50)
    return fig, ax, fg


def side(fig, ax):
    """Left edge of the side column, just right of the drawn map."""
    fig.canvas.draw(); p = ax.get_position()
    return p.x1 + 0.025, p.y0, p.y1


def boxes(fig, ax):
    """Two boxes of equal size in the side column: [upper, lower] as [x, y, w, h]."""
    x, y0, y1 = side(fig, ax); h = (y1 - y0 - GAP) / 2; w = 0.98 - x
    return [x, y0 + h + GAP, w, h], [x, y0, w, h]


def legend_side(fig, ax, handles, title, fg="#222222"):
    up, _ = boxes(fig, ax)
    la = fig.add_axes(up); la.set_xticks([]); la.set_yticks([]); la.set_facecolor("none")
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    leg = la.legend(handles=handles, title=title, loc="upper left", fontsize=10.5, title_fontsize=11, frameon=False,
                    borderaxespad=0.8, alignment="left", labelcolor=fg, handlelength=2.4, handleheight=1.5, labelspacing=0.9)
    leg.get_title().set_fontweight("bold")
    leg.get_title().set_color(fg)
    return la


def colorbar_side(fig, ax, sm, label, fg="#222222"):
    up, _ = boxes(fig, ax)
    h = up[3] * 0.86; yb = up[1] + (up[3] - h) / 2
    ca = fig.add_axes([up[0] + up[2] / 2 - 0.035, yb, 0.026, h])
    cb = fig.colorbar(sm, cax=ca); cb.set_label(label, color=fg, fontsize=10.5, fontweight="bold"); ca.tick_params(labelsize=9.5); cb.outline.set_edgecolor(fg); cb.outline.set_linewidth(0.5)
    ca.yaxis.set_tick_params(color=fg); plt.setp(ca.get_yticklabels(), color=fg)


def furniture(ax, fg, source):
    # scale bar and north arrow in the empty lower-left corner (Botswana), clear of Zimbabwe
    km = 111.32 * np.cos(np.radians(22)); L = 200 / km; x0, y0 = 25.3, -22.35
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.07, fc=fg if i % 2 == 0 else ("black" if fg != "#222222" else "white"), ec=fg, lw=0.6, zorder=20))
    for v, x in [(0, x0), (100, x0 + L / 2), (200, x0 + L)]:
        ax.text(x, y0 + 0.12, f"{v}", ha="center", va="bottom", fontsize=7, color=fg, zorder=20)
    ax.text(x0 + L + 0.08, y0 + 0.03, "km", fontsize=7, color=fg, va="center", zorder=20)
    ax.text(0, -0.055, source, transform=ax.transAxes, fontsize=6.5, color=fg, ha="left", va="top", wrap=True)


def neighbours(ax, fc="#e0e0e0", ec="#ffffff", lw=0.6):
    world.plot(ax=ax, fc=fc, ec=ec, lw=lw, zorder=1)


def labels_countries(ax, color="#888888"):
    for n, x, y in [("ZAMBIA", 27.6, -16.3), ("MOZAMBIQUE", 32.45, -16.0), ("BOTSWANA", 26.3, -20.9), ("SOUTH AFRICA", 30.8, -22.45)]:
        ax.text(x, y, n, fontsize=7, color=color, ha="center", style="italic", zorder=15)


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved", name)


def hillshade():
    with rasterio.open("../population/rast/dem.tif") as s:
        z = s.read(1).astype(float); b = s.bounds
    ls = LightSource(azdeg=315, altdeg=40)
    dx = (b.right - b.left) / z.shape[1] * 111320 * np.cos(np.radians(19)); dy = (b.top - b.bottom) / z.shape[0] * 111320
    hs = ls.hillshade(z, vert_exag=6, dx=dx, dy=dy)
    return z, hs, (b.left, b.right, b.bottom, b.top)


def clip_mask(shape, extent, geoms):
    from rasterio.features import geometry_mask
    T = rasterio.transform.from_bounds(extent[0], extent[2], extent[1], extent[3], shape[1], shape[0])
    return geometry_mask(geoms, out_shape=shape, transform=T, invert=True)




def locator(fig, ax, zc="#c0392b"):
    """Small map of SADC in the lower box of the side column, Zimbabwe in a colour from the map's palette."""
    _, lo = boxes(fig, ax)
    la = fig.add_axes(lo)
    sea, other, member, ec = ("#ffffff", "#f0f0f0", "#cfcfcf", "#ffffff")
    la.set_facecolor(sea)
    africa.plot(ax=la, fc=other, ec=ec, lw=0.3)
    africa[africa.ADM0_A3.isin(SADC)].plot(ax=la, fc=member, ec=ec, lw=0.3)
    africa[africa.ADM0_A3 == "ZWE"].plot(ax=la, fc=mpl.colors.to_hex(zc), ec="none")
    la.set_xlim(9, 52); la.set_ylim(-36, 6); la.set_aspect(1 / np.cos(np.radians(15)), adjustable="datalim")
    la.set_xticks([]); la.set_yticks([])
    fg = "#222222"
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.88), 1, 0.12, transform=la.transAxes, fc=sea, ec="none", zorder=5))
    la.plot([0, 1], [0.88, 0.88], transform=la.transAxes, color=fg, lw=0.6, zorder=6)
    la.text(0.5, 0.94, "SADC", transform=la.transAxes, ha="center", va="center", fontsize=11, fontweight="bold", color=fg, zorder=7)


HALO = [pe.withStroke(linewidth=2, foreground="white")]
SRC = "Source: CHIRPS v2.0 pentad rainfall (Funk et al. 2015), 0.05°, summed October to April; normal 1991/92 to 2020/21. Boundaries OCHA COD-AB; Natural Earth. WGS 84."


def overlays(ax, towns=6):
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=4)
    prov.boundary.plot(ax=ax, color="#444444", lw=0.45, ls="--", zorder=5)
    zwe.boundary.plot(ax=ax, color="#111111", lw=0.9, zorder=6)
    for n, x, y in CITIES[:towns]:
        ax.plot(x, y, "o", ms=3.2, mfc="white", mec="black", mew=0.7, zorder=7)
        ax.text(x + 0.07, y + 0.05, n, fontsize=7.5, zorder=7, path_effects=HALO)


def shade(ax, alpha=0.30):
    """Grey hillshade over Zimbabwe only, so relief shows through the rainfall colours."""
    z, hs, ext = hillshade()
    inside = clip_mask(z.shape, ext, zwe.geometry)
    rgba = np.zeros(z.shape + (4,)); rgba[..., 3] = np.where(inside, alpha * (1 - hs), 0)
    ax.imshow(rgba, extent=ext, zorder=3, interpolation="bilinear")


def raster(ax, a, cmap, norm, interp="nearest"):
    ax.imshow(np.ma.masked_invalid(a), extent=REXT, cmap=cmap, norm=norm, zorder=2, interpolation=interp)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])


def classed(fig, ax, a, bins, colors, labels, title):
    cmap = ListedColormap(colors); norm = BoundaryNorm(bins, cmap.N)
    raster(ax, a, cmap, norm)
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=f"{l}  ({share((a >= lo) & (a < hi)):.0f})")
          for c, l, lo, hi in zip(colors, labels, bins[:-1], bins[1:])]
    legend_side(fig, ax, hs, title + "\n(% of land area)")


# 1 Study area: grey hillshade, provinces and towns
def map1():
    z, hs, ext = hillshade()
    inside = clip_mask(z.shape, ext, zwe.geometry)
    fig, ax, fg = frame("Study Area Map")
    neighbours(ax, fc="#e8e8e8")
    g = np.where(inside, 0.35 + 0.6 * hs, np.nan)
    ax.imshow(np.ma.masked_invalid(g), extent=ext, cmap="gray", vmin=0, vmax=1, zorder=2, interpolation="bilinear")
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=4)
    prov.boundary.plot(ax=ax, color="#222222", lw=0.5, ls="--", zorder=5)
    zwe.boundary.plot(ax=ax, color="#000000", lw=1.0, zorder=6)
    for n, x, y in CITIES:
        big = n in ("Harare", "Bulawayo")
        ax.plot(x, y, "s" if big else "o", ms=5 if big else 3.2, mfc="white", mec="black", mew=0.7, zorder=7)
        ax.text(x + 0.07, y + 0.05, n, fontsize=8 if big else 7, fontweight="bold" if big else "normal", zorder=7, path_effects=HALO)
    for _, r in prov.iterrows():
        n = r.adm1_name
        if n in ("Harare", "Bulawayo"): continue
        c = r.geometry.representative_point()
        ax.text(c.x, c.y - 0.25, n.upper(), fontsize=6.5, color="#222222", ha="center", style="italic", zorder=7,
                path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    labels_countries(ax, "#666666")
    hs_ = [Line2D([], [], marker="s", ls="none", ms=6, mfc="white", mec="black", label="City"),
           Line2D([], [], marker="o", ls="none", ms=4.5, mfc="white", mec="black", label="Town"),
           Line2D([], [], color="#000000", lw=1.0, label="National boundary"),
           Line2D([], [], color="#222222", lw=0.6, ls="--", label="Provincial boundary"),
           Patch(fc="#a9c8e0", ec="none", label="Lake"),
           Patch(fc="#e8e8e8", ec="#999999", lw=0.4, label="Neighbouring country")]
    legend_side(fig, ax, hs_, "Legend")
    locator(fig, ax, zc="#6b6b6b")
    furniture(ax, fg, "Source: Copernicus GLO-30 DEM hillshade (500 m); boundaries OCHA COD-AB 2023; Natural Earth. Geographic coordinates, WGS 84.")
    save(fig, "map1_study_area")


# ---------------------------------------------------------------------------------------------------------------
# Maps 2 to 7 (v3). One full frame per map over an OpenStreetMap basemap; Zimbabwe is lifted off the basemap with a
# soft drop shadow; the legend sits in the lower-right corner over Mozambique. Only Map 1 carries the SADC locator.
import contextily as ctx
from scipy import ndimage
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Polygon
from shapely.geometry import Point
import pandas as pd
dist = gpd.read_file(B + "zwe_admin2.shp")
NY, NX = M0.shape
XS = REXT[0] + (np.arange(NX) + 0.5) * (REXT[1] - REXT[0]) / NX
YS = REXT[3] - (np.arange(NY) + 0.5) * (REXT[3] - REXT[2]) / NY
EX = (24.6, 36.7, -23.0, -14.75)          # wide frame: room east of Zimbabwe for the legend
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
SRC_SHORT = "Source: CHIRPS v2.0 (Funk et al. 2015), 0.05°, October to April totals; normal 1991/92 to 2020/21. Boundaries OCHA COD-AB. " + OSM + " WGS 84."
ZG = gpd.GeoSeries([zwe.geometry.union_all()], crs=zwe.crs)


_BM = {}


def basemap(kind="osm"):
    if kind in _BM: return _BM[kind]
    """Humanitarian OSM tiles (zoom 8) fetched once, warped to WGS 84 and cached; the dark map uses an inverted grey copy."""
    f = "rast/basemap_hot.npz"
    if not os.path.exists(f):
        img, ext = ctx.bounds2img(20.3, -24.2, 39.0, -13.3, zoom=8, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:4326")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    # strip the tiles' own grey dashed admin lines and grey roads (neutral grey pixels), keeping labels, water and parks
    mx, mn = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1)
    grey &= ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255
    if kind == "dark":
        g = 1 - img.mean(axis=2, keepdims=True); img = np.repeat(0.05 + 0.32 * g, 3, axis=2)
    else:
        img = 0.72 * img + 0.28                      # basemap at reduced opacity (blended toward white) so the data stands out
    _BM[kind] = (np.clip(img, 0, 1), tuple(d["ext"]))
    return _BM[kind]


def lift(ax, dark=False):
    """Soft drop shadow under Zimbabwe (or a glow on the dark map) so the data sits above the basemap."""
    if dark:
        ZG.boundary.plot(ax=ax, color="#feca8d", lw=1.0, zorder=6, path_effects=[pe.withStroke(linewidth=6, foreground="#feca8d", alpha=0.22)])
        return
    for k in range(1, 8):
        ZG.translate(0.022 * k, -0.022 * k).plot(ax=ax, fc="black", ec="none", alpha=0.055, zorder=1.5)
    ZG.plot(ax=ax, fc="white", ec="none", zorder=1.6)


def frame3(title, ext=EX, width=11.0, dark=False):
    """Map fills the whole frame; basemap behind; title top centre, north arrow top left, © lower right."""
    h = width * 0.92 * (ext[3] - ext[2]) * ASPECT / (ext[1] - ext[0]) / 0.9
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0.055, 0.075, 0.92, 0.9])
    fg = "#e6e6e6" if dark else "#222222"; bg = "#0b0b0b" if dark else "white"
    fig.patch.set_facecolor(bg)
    img, bext = basemap("dark" if dark else "osm")
    ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(ASPECT)
    xt = range(int(np.ceil(ext[0])), int(ext[1]) + 1); yt_ = range(int(np.ceil(ext[2])), int(ext[3]) + 1)
    ax.set_xticks(list(xt)); ax.set_yticks(list(yt_))
    ax.set_xticklabels([f"{x}°E" for x in xt], color=fg); ax.set_yticklabels([f"{-y}°S" for y in yt_], color=fg)
    ax.tick_params(length=2, colors=fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.7)
    halo = [pe.withStroke(linewidth=4, foreground=bg)]
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=15, fontweight="bold", color=fg, zorder=70, path_effects=halo)
    narrow(ax, 0.035, TY, fg, bg)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg, zorder=70, path_effects=halo)
    return fig, ax, fg


def narrow(ax, x, y, fg="#222222", bg="white", h=0.085):
    """Two-tone split arrowhead north arrow in axes units; its tip sits exactly at (x, y), N below the base."""
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9, transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def scalebar(ax, fg, x0, y0, alt="white"):
    km = 111.32 * np.cos(np.radians(22)); L = 200 / km
    ax.add_patch(Rectangle((x0 - 0.12, y0 - 0.1), L + 0.62, 0.48, fc=alt, ec="none", alpha=0.8, zorder=59))
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.07, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (100, x0 + L / 2), (200, x0 + L)]:
        ax.text(x, y0 + 0.12, f"{v}", ha="center", va="bottom", fontsize=7.5, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + 0.08, y0 + 0.03, "km", fontsize=7.5, color=fg, va="center", zorder=60, path_effects=halo)


def legend_br(ax, handles, title, fg="#222222", bg="white", ncol=1):
    """Framed legend in the lower-right corner, just above the attribution."""
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=(0.992, 0.045), fontsize=10.5, title_fontsize=11,
                    frameon=True, fancybox=False, edgecolor=fg, facecolor=bg, framealpha=0.94, alignment="left", labelcolor=fg, ncol=ncol,
                    borderpad=0.9, handlelength=2.4, handleheight=1.4, labelspacing=0.75, columnspacing=1.6)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65)
    leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)
    ax.figure.canvas.draw(); bb = leg.get_window_extent().transformed(ax.transData.inverted())
    from shapely.geometry import box as _box
    print("legend lon", round(bb.x0, 2), round(bb.x1, 2), "lat", round(bb.y0, 2), round(bb.y1, 2), "hits Zimbabwe:", ZG.intersects(_box(bb.x0, bb.y0, bb.x1, bb.y1)).any())
    return leg


def colorbar_br(fig, ax, sm, title, ticks, fg="#222222", w=0.30, h=0.15):
    """Framed box in the lower-right corner holding a horizontal colour bar, title in its top-left corner."""
    box = ax.inset_axes([0.992 - w, 0.045, w, h]); box.set_xticks([]); box.set_yticks([]); box.set_zorder(65)
    box.set_facecolor((1, 1, 1, 0.94))
    for sp in box.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    box.text(0.045, 0.86, title, transform=box.transAxes, ha="left", va="top", fontsize=11, fontweight="bold", color=fg, linespacing=1.3)
    ca = box.inset_axes([0.07, 0.26, 0.86, 0.17])
    cb = fig.colorbar(sm, cax=ca, orientation="horizontal", ticks=ticks); ca.tick_params(labelsize=9.5, length=2); cb.outline.set_linewidth(0.5)


def zclip(ax):
    """Zimbabwe outline as a clip patch, so contours stop at the border."""
    verts, codes = [], []
    for g in zwe.geometry:
        for poly in getattr(g, "geoms", [g]):
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords); verts += list(xy); codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    p = PathPatch(Path(verts, codes), transform=ax.transData, fc="none", ec="none"); ax.add_patch(p)
    return p


def fill_nan(a):
    idx = ndimage.distance_transform_edt(np.isnan(a), return_distances=False, return_indices=True)
    return a[tuple(idx)]


def towns(ax, n=6, color="black", halo="white", fs=7.5):
    for name, x, y in CITIES[:n]:
        ax.plot(x, y, "o", ms=3.4, mfc=halo, mec=color, mew=0.8, zorder=30)
        ax.text(x + 0.07, y + 0.05, name, fontsize=fs, color=color, zorder=30, path_effects=[pe.withStroke(linewidth=2.2, foreground=halo)])


def counts(a, bins):
    return [share((a >= lo) & (a < hi)) for lo, hi in zip(bins[:-1], bins[1:])]


def source(fig, ax, text, fg="#222222"):
    ax.set_aspect(ASPECT); ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3])   # geopandas resets the limits
    ax.text(0, -0.05, text, transform=ax.transAxes, fontsize=6.8, color=fg, ha="left", va="top")


def borders(ax, provlw=0.5, ls="-", pc="#555555", zc="#111111"):
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=4)
    prov.boundary.plot(ax=ax, color=pc, lw=provlw, ls=ls, zorder=5)
    ZG.boundary.plot(ax=ax, color=zc, lw=1.0, zorder=6)


# 2 Isohyet map: filled bands with labelled isohyets
def map2():
    fig, ax, fg = frame3("Mean Seasonal Rainfall Map (1991–2020)")
    lift(ax)
    m = ndimage.gaussian_filter(fill_nan(G["mean"]), 1.2)
    lv = [300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400]
    cols = [mpl.colors.to_hex(c) for c in plt.get_cmap("YlGnBu")(np.linspace(0.1, 0.95, len(lv) - 1))]
    cmap = ListedColormap(cols); norm = BoundaryNorm(lv, cmap.N)
    cf = ax.contourf(XS, YS, np.clip(m, 301, 1399), levels=lv, cmap=cmap, norm=norm, zorder=2)
    cl = ax.contour(XS, YS, m, levels=[400, 600, 800, 1000], colors="#1b2a3a", linewidths=0.7, zorder=3)
    clip = zclip(ax); cf.set_clip_path(clip); cl.set_clip_path(clip)
    for t in ax.clabel(cl, fmt="%d", fontsize=7.5, inline=True, inline_spacing=4):
        if not zwe.contains(Point(t.get_position())).any(): t.remove()
    borders(ax); towns(ax); scalebar(ax, fg, 25.0, -22.7)
    labs = ["300 to 400", "400 to 500", "500 to 600", "600 to 700", "700 to 800", "800 to 900", "900 to 1 000", "1 000 to 1 200", "Over 1 200"]
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=l) for c, l in zip(cols, labs)]
    hs.append(Line2D([], [], color="#1b2a3a", lw=0.8, label="Isohyet"))
    legend_br(ax, hs, "October to April rainfall (mm)")
    source(fig, ax, SRC_SHORT)
    save(fig, "map2_mean")


# 3 Continuous surface: smooth CV ramp with dashed labelled CV lines, colour bar box
def map3():
    fig, ax, fg = frame3("Rainfall Variability Map (1991–2020)")
    lift(ax)
    cv = G["cv"]; norm = mpl.colors.Normalize(15, 40); cmap = plt.get_cmap("YlOrRd")
    im = ax.imshow(np.ma.masked_invalid(np.where(M0, cv, np.nan)), extent=REXT, cmap=cmap, norm=norm, zorder=2, interpolation="bilinear")
    clip = zclip(ax); im.set_clip_path(clip)
    sm_ = ndimage.gaussian_filter(fill_nan(cv), 2.0)
    cl = ax.contour(XS, YS, sm_, levels=[20, 25, 30, 35], colors="#4a1500", linewidths=1.0, zorder=3)
    cl.set_clip_path(clip)
    for t in ax.clabel(cl, fmt="%d%%", fontsize=7.5, inline=True, inline_spacing=4):
        if not zwe.contains(Point(t.get_position())).any(): t.remove()
    borders(ax, provlw=0.4, pc="#9a9a9a"); towns(ax); scalebar(ax, fg, 25.0, -22.7)
    colorbar_br(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap), "Coefficient of variation (%)", [15, 20, 25, 30, 35, 40], w=0.30, h=0.15)
    source(fig, ax, SRC_SHORT + " Dark lines: coefficient of variation every 5%; grey lines: provinces.")
    save(fig, "map3_variability")


# 4 Small multiples: 2 x 3 grid of equal touching cells, title strip on top, legend cell bottom right
def map4():
    """Five seasons in a 2 x 3 grid of equal cells that touch; the sixth cell holds the north arrow, legend and scale bar.
    The title sits in its own strip above the grid so it never crosses a panel border."""
    seas = [1991, 1994, 2001, 2018, 2023]
    bins = [0, 50, 65, 75, 90, 110, 1000]
    cols = ["#8c510a", "#bf812d", "#dfc27d", "#f6e8c3", "#f5f5f5", "#5ab4ac"]
    labs = ["Under 50", "50 to 65", "65 to 75", "75 to 90", "90 to 110", "Over 110"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bins, cmap.N)
    lon0, lon1, lat0, lat1 = 24.95, 33.35, -22.65, -15.35
    W = 13.0; cw = W / 3; ch = cw * (lat1 - lat0) * ASPECT / (lon1 - lon0); TS = 0.62
    H = 2 * ch + TS; fh = ch / H
    fig = plt.figure(figsize=(W, H), dpi=220); fig.patch.set_facecolor("white"); fg = "#222222"
    img, bext = basemap("osm")
    pos = [[c / 3, fh, 1 / 3, fh] for c in range(3)] + [[c / 3, 0, 1 / 3, fh] for c in range(3)]
    for i, y in enumerate(seas):
        a = fig.add_axes(pos[i]); a.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
        lift(a)
        a.imshow(np.ma.masked_invalid(100 * S[y - 1991] / G["mean"]), extent=REXT, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
        borders(a, provlw=0.4)
        a.set_aspect(ASPECT); a.set_xlim(lon0, lon1); a.set_ylim(lat0, lat1); a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
        a.text(0.03, 0.965, f"{y}/{str(y + 1)[2:]}", transform=a.transAxes, fontsize=13, fontweight="bold", ha="left", va="top",
               zorder=70, bbox=dict(fc="white", ec=fg, lw=0.6, pad=3.5))
        if i == 0:
            for name, x, yy in CITIES[:2]:
                a.plot(x, yy, "o", ms=3, mfc="white", mec="black", mew=0.6, zorder=30)
                a.text(x + 0.1, yy + 0.08, name, fontsize=7.5, zorder=30, path_effects=HALO)
    # legend cell
    k = fig.add_axes(pos[5]); k.set_xlim(0, 1); k.set_ylim(0, 1); k.set_xticks([]); k.set_yticks([])
    for sp in k.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
    # legend drawn to fill the cell: framed box, title top left, three rows in two columns spaced evenly
    k.add_patch(Rectangle((0.05, 0.20), 0.90, 0.75, fc="white", ec=fg, lw=0.6))
    k.text(0.09, 0.915, "Rainfall (% of 1991–2020 normal)", ha="left", va="top", fontsize=12.5, fontweight="bold", color=fg)
    for j, (c, l) in enumerate(zip(cols, labs)):
        cx = 0.09 if j < 3 else 0.53; cy = [0.71, 0.525, 0.34][j % 3]
        k.add_patch(Rectangle((cx, cy - 0.06), 0.13, 0.12, fc=c, ec="#777777", lw=0.5))
        k.text(cx + 0.16, cy, l, ha="left", va="center", fontsize=12, color=fg)
    # bottom row: north arrow, scale bar, attribution
    narrow(k, 0.10, 0.165, fg, "white", h=0.095)
    km = 111.32 * np.cos(np.radians(19)); L = (200 / km) / (lon1 - lon0); x0 = 0.5 - L / 2 - 0.04; y0 = 0.085
    for j in range(4):
        k.add_patch(Rectangle((x0 + j * L / 4, y0), L / 4, 0.022, fc=fg if j % 2 == 0 else "white", ec=fg, lw=0.6))
    for v, x in [(0, x0), (100, x0 + L / 2), (200, x0 + L)]:
        k.text(x, y0 + 0.035, f"{v}", ha="center", va="bottom", fontsize=8.5, color=fg)
    k.text(x0 + L + 0.02, y0 + 0.011, "km", fontsize=8.5, color=fg, va="center")
    k.text(0.97, 0.025, AUTHOR, transform=k.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg)
    fig.text(0.5, 1 - (TS / 2) / H, "Drought Season Rainfall Anomaly Maps (1991–2024)", ha="center", va="center", fontsize=16, fontweight="bold")
    fig.text(0, -0.012, "Source: CHIRPS v2.0 (Funk et al. 2015), 0.05°. October to April total of each season as a percentage of the 1991/92 to 2020/21 mean. "
             "Boundaries OCHA COD-AB. " + OSM + " WGS 84.", fontsize=7.5, color=fg, ha="left", va="top")
    save(fig, "map4_drought_seasons")


# 5 Dark map over a dark OSM basemap: drought frequency, glowing classes
def map5():
    fig, ax, fg = frame3("Drought Frequency Map (1991–2025)", dark=True)
    bins = [0, 4, 6, 8, 10, 40]
    cols = ["#2c115f", "#721f81", "#b73779", "#f1605d", "#feca8d"]
    labs = ["2 to 3", "4 to 5", "6 to 7", "8 to 9", "10 to 12"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bins, cmap.N)
    ZG.plot(ax=ax, fc="#0b0b0b", ec="none", zorder=1.6)
    ax.imshow(np.ma.masked_invalid(G["drought"]), extent=REXT, cmap=cmap, norm=norm, zorder=2, interpolation="bilinear")
    lakes.plot(ax=ax, fc="#20384d", ec="none", zorder=4)
    prov.boundary.plot(ax=ax, color="#9a9a9a", lw=0.45, zorder=5)
    lift(ax, dark=True)
    towns(ax, color="#f0f0f0", halo="#0b0b0b"); scalebar(ax, fg, 25.0, -22.7, alt="#0b0b0b")
    hs = [Patch(fc=c, ec="#888888", lw=0.4, label=f"{l}  ({v:.0f})") for c, l, v in zip(cols, labs, counts(G["drought"], bins))]
    legend_br(ax, hs, "Drought seasons (% of land area)", fg=fg, bg="#0b0b0b")
    source(fig, ax, "Source: CHIRPS v2.0 (Funk et al. 2015), 0.05°. Count of the 34 seasons 1991/92 to 2024/25 below 75% of the 1991–2020 mean. "
           "Boundaries OCHA COD-AB. " + OSM + " WGS 84.", fg)
    save(fig, "map5_drought_frequency")


# 6 Flat categorical map with white district lines
def map6():
    k = np.argmin(np.where(np.isnan(S), np.inf, S), axis=0)
    yrs = np.where(M0, Y[k], 0)
    top = [y for y in (1991, 1994, 2023, 2001, 2018) if share(yrs == y) >= 2]
    code = np.full(k.shape, np.nan)
    for i, y in enumerate(top): code[yrs == y] = i
    code[M0 & np.isnan(code)] = len(top)
    cols = ["#e66101", "#5e3c99", "#1b9e77", "#fdb863", "#b2abd2"][:len(top)] + ["#d9d9d9"]
    labs = [f"{y}/{str(y + 1)[2:]}" for y in top] + ["Other seasons"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(list(np.arange(len(cols) + 1) - 0.5), cmap.N)
    fig, ax, fg = frame3("Driest Season Map (1991–2025)")
    lift(ax)
    ax.imshow(np.ma.masked_invalid(code), extent=REXT, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    dist.boundary.plot(ax=ax, color="white", lw=0.5, zorder=4)
    borders(ax, provlw=0.7, ls="-", pc="#333333")
    towns(ax); scalebar(ax, fg, 25.0, -22.7)
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=f"{l}  ({share(code == i):.0f})") for i, (c, l) in enumerate(zip(cols, labs))]
    hs.append(Line2D([], [], color="#bbbbbb", lw=1.2, label="District boundary"))
    legend_br(ax, hs, "Driest season (% of land area)")
    source(fig, ax, SRC_SHORT.replace("normal 1991/92 to 2020/21", "driest of the 34 seasons 1991/92 to 2024/25"))
    save(fig, "map6_driest_season")


# 7 District choropleth of the Sen slope
def map7():
    d = dist.merge(pd.read_csv("data/district_trend.csv")[["pcode", "slope", "p"]], left_on="adm2_pcode", right_on="pcode")
    bins = [-100, -10, -5, 0, 5, 10, 20, 100]
    cols = ["#b2182b", "#ef8a62", "#fddbc7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac"]
    labs = ["Below −10", "−10 to −5", "−5 to 0", "0 to 5", "5 to 10", "10 to 20", "Over 20"]
    fig, ax, fg = frame3("Seasonal Rainfall Trend By District Map (1991–2025)")
    lift(ax)
    d["cls"] = pd.cut(d.slope, bins, labels=False, right=False)
    for i, c in enumerate(cols): d[d.cls == i].plot(ax=ax, fc=c, ec="white", lw=0.5, zorder=2)
    borders(ax, provlw=0.8, ls="-", pc="#333333")
    towns(ax); scalebar(ax, fg, 25.0, -22.7)
    ax.set_aspect(ASPECT); ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3])
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=f"{l}  ({(d.cls == i).sum()} districts)") for i, (c, l) in enumerate(zip(cols, labs))]
    legend_br(ax, hs, "Sen slope (mm per decade)")
    source(fig, ax, "Source: CHIRPS v2.0 (Funk et al. 2015), 0.05°. Sen slope of the area-weighted October to April total of each district, 34 seasons 1991/92 to 2024/25.\n"
           "Boundaries OCHA COD-AB 2023 (91 districts). " + OSM + " WGS 84.")
    save(fig, "map7_trend_district")


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "map6", "map7"]): globals()[f]()
