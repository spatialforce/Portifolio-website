"""Maps for the Hwange GEDI carbon case study (same layout rules as the solar maps)."""
import os, json
import numpy as np, pandas as pd, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from rasterio.warp import reproject, calculate_default_transform, Resampling
from matplotlib.colors import LightSource, BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon, PathPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path
from scipy import ndimage

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
LAT = 19.2
ASPECT = 1 / np.cos(np.radians(LAT))
AUTHOR = "© Kudzanai Chakavarika"
B = "../population/raw/bnd/"
park = gpd.read_file("data/wdpa_hwange.geojson").to_crs(4326)
PG = gpd.GeoSeries([park.geometry.union_all()], crs=4326)
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(4326)
zwe_p = gpd.read_file(B + "zwe_admin1.shp"); zwe = gpd.read_file(B + "zwe_admin0.shp")
mn = zwe_p[zwe_p.adm1_name == "Matabeleland North"]
world = gpd.read_file("zip://../../corridors/raw/ne_10m_admin_0_countries.zip").cx[20:36, -27:-14]
TOWNS = [("Hwange", 26.500, -18.364), ("Dete", 26.862, -18.619), ("Main Camp", 27.007, -18.729),
         ("Sinamatella", 26.318, -18.588), ("Robins Camp", 25.983, -18.612)]
EX = (25.45, 27.95, -20.12, -18.22)
TY = 0.955
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
S = json.load(open("out/stats.json"))
_W = {}


def warp(name, categorical=False, src="out"):
    k = (name, src)
    if k in _W: return _W[k]
    with rasterio.open(f"{src}/{name}.tif") as s:
        tr, w, h = calculate_default_transform(s.crs, "EPSG:4326", s.width, s.height, *s.bounds)
        d = np.full((h, w), np.nan, "float32")
        reproject(rasterio.band(s, 1), d, dst_transform=tr, dst_crs="EPSG:4326", src_nodata=np.nan,
                  resampling=Resampling.nearest if categorical else Resampling.bilinear, dst_nodata=np.nan)
    _W[k] = (d, (tr.c, tr.c + tr.a * w, tr.f + tr.e * h, tr.f)); return _W[k]


def basemap():
    if "b" in _W: return _W["b"]
    import contextily as ctx
    f = "rast/basemap_hot.npz"
    if not os.path.exists(f):
        img, ext = ctx.bounds2img(25.0, -20.6, 28.4, -17.8, zoom=10, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:4326")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn_ = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn_ < 22) & (mx > 110) & (mx < 228), iterations=1)
    grey &= ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = 0.72 * np.where(grey[..., None], med, img) / 255 + 0.28
    _W["b"] = (np.clip(img, 0, 1), tuple(d["ext"])); return _W["b"]


def narrow(ax, x, y, fg="#222222", bg="white", h=0.085):
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9,
                             transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11,
            fontweight="bold", color=fg, zorder=70, path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def scalebar(ax, fg, y0, length=50, end_ax=0.965, ext=EX, alt="white"):
    km = 111.32 * np.cos(np.radians(LAT)); L = length / km
    x0 = ext[0] + end_ax * (ext[1] - ext[0]) - L
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.022, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (length // 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(x, y0 + 0.035, f"{v}", ha="center", va="bottom", fontsize=7.5, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + 0.025, y0 + 0.01, "km", fontsize=7.5, color=fg, va="center", zorder=60, path_effects=halo)


def legend_bl(ax, handles, title, fg="#222222", fs=10, sp=0.6):
    leg = ax.legend(handles=handles, title=title, loc="lower left", bbox_to_anchor=(0.008, 0.012), fontsize=fs,
                    title_fontsize=fs + 0.5, frameon=True, fancybox=False, edgecolor=fg, facecolor="white",
                    framealpha=0.94, alignment="left", labelcolor=fg, borderpad=0.9, handlelength=2.4,
                    handleheight=1.3, labelspacing=sp)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold")


def colorbar_bl(fig, ax, sm, title, ticks, fg="#222222", w=0.34, h=0.14, ext="neither"):
    box = ax.inset_axes([0.008, 0.012, w, h]); box.set_xticks([]); box.set_yticks([]); box.set_zorder(65)
    box.set_facecolor((1, 1, 1, 0.94))
    for s in box.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    box.text(0.045, 0.86, title, transform=box.transAxes, ha="left", va="top", fontsize=10.5,
             fontweight="bold", color=fg, linespacing=1.3)
    ca = box.inset_axes([0.07, 0.26, 0.86, 0.17])
    cb = fig.colorbar(sm, cax=ca, orientation="horizontal", ticks=ticks, extend=ext)
    ca.tick_params(labelsize=9, length=2); cb.outline.set_linewidth(0.5)


def pclip(ax, g=PG):
    verts, codes = [], []
    for geom in g:
        for poly in getattr(geom, "geoms", [geom]):
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords); verts += list(xy)
                codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    p = PathPatch(Path(verts, codes), transform=ax.transData, fc="none", ec="none"); ax.add_patch(p); return p


def lift(ax):
    for k in range(1, 8):
        PG.translate(0.006 * k, -0.006 * k).plot(ax=ax, fc="black", ec="none", alpha=0.055, zorder=1.5)
    PG.plot(ax=ax, fc="white", ec="none", zorder=1.6)


def ticks(ax, ext, fg, step=0.5):
    xt = np.arange(np.ceil(ext[0] / step) * step, ext[1], step); yt = np.arange(np.ceil(ext[2] / step) * step, ext[3], step)
    ax.set_xticks(xt); ax.set_yticks(yt)
    ax.set_xticklabels([f"{x:g}°E" for x in xt], color=fg); ax.set_yticklabels([f"{-y:g}°S" for y in yt], color=fg)
    ax.tick_params(length=2, colors=fg)


def frame(title, width=11.0):
    h = width * 0.92 * (EX[3] - EX[2]) * ASPECT / (EX[1] - EX[0]) / 0.9
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0.055, 0.075, 0.92, 0.9])
    fg = "#222222"; fig.patch.set_facecolor("white")
    img, bext = basemap(); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3]); ax.set_aspect(ASPECT); ticks(ax, EX, fg)
    for s in ax.spines.values(): s.set_color(fg); s.set_linewidth(0.7)
    halo = [pe.withStroke(linewidth=4, foreground="white")]
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=15, fontweight="bold",
            color=fg, zorder=70, path_effects=halo)
    narrow(ax, 0.965, TY + 0.02, fg)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg, zorder=70, path_effects=halo)
    return fig, ax, fg


HALO = [pe.withStroke(linewidth=2.2, foreground="white")]


def towns(ax, fs=8):
    for n, x, y in TOWNS:
        ax.plot(x, y, "o", ms=3.6, mfc="white", mec="black", mew=0.8, zorder=30)
        dy = -0.045 if n == "Hwange" else 0.018          # Hwange label below its dot, clear of the title
        ax.text(x + 0.02, y + dy, n, fontsize=fs, zorder=30, path_effects=HALO)


def outline(ax):
    dist.boundary.plot(ax=ax, color="#777777", lw=0.5, zorder=5)
    PG.boundary.plot(ax=ax, color="#111111", lw=1.0, zorder=6)


def finish(fig, ax, text, name):
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3])
    ax.text(0, -0.05, text, transform=ax.transAxes, fontsize=6.8, color="#222222", ha="left", va="top")
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig); print("saved", name)


# ---- map 1: study area ----------------------------------------------------------
EXT1 = (25.55, 27.75, -20.05, -18.08)


def map1():
    elev, eext = warp("elev", src="rast")
    dx = (eext[1] - eext[0]) / elev.shape[1] * 111320 * np.cos(np.radians(LAT)); dy = (eext[3] - eext[2]) / elev.shape[0] * 111320
    hs = LightSource(315, 40).hillshade(np.nan_to_num(elev, nan=np.nanmean(elev)), vert_exag=12, dx=dx, dy=dy)
    fig = plt.figure(figsize=(11.6, 7.4), dpi=220); ax = fig.add_axes([0.035, 0.07, 0.60, 0.88])
    fg = "#222222"; fig.patch.set_facecolor("white"); ax.set_facecolor("#f4f4f4")
    ax.set_xlim(EXT1[0], EXT1[1]); ax.set_ylim(EXT1[2], EXT1[3]); ax.set_aspect(ASPECT, anchor="W"); ticks(ax, EXT1, fg)
    ax.grid(color="#bbbbbb", lw=0.3, ls=":")
    for s in ax.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    ax.text(0.5, TY + 0.01, "Study Area Map", transform=ax.transAxes, ha="center", va="center", fontsize=14,
            fontweight="bold", color=fg, zorder=50, path_effects=HALO)
    fig.canvas.draw(); narrow(ax, 0.95, TY + 0.025, fg, h=0.10)
    ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#777777", zorder=50)
    world.plot(ax=ax, fc="#e8e8e8", ec="#ffffff", lw=0.6, zorder=1)
    zwe.plot(ax=ax, fc="#f0ede8", ec="none", zorder=1.2)
    im = ax.imshow(0.35 + 0.6 * hs, extent=eext, cmap="gray", vmin=0, vmax=1, zorder=2, interpolation="bilinear")
    im.set_clip_path(pclip(ax))
    ax.set_xlim(EXT1[0], EXT1[1]); ax.set_ylim(EXT1[2], EXT1[3])
    zwe.boundary.plot(ax=ax, color="#8c6d4f", lw=1.6, zorder=7)
    outline(ax); towns(ax)
    for n, x, y in [("HWANGE RURAL", 26.62, -18.40), ("TSHOLOTSHO", 27.45, -19.55), ("LUPANE", 27.55, -18.75)]:
        ax.text(x, y, n, fontsize=6.5, ha="center", style="italic", zorder=7, path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    ax.text(25.78, -19.55, "BOTSWANA", fontsize=7.5, color="#777777", ha="center", style="italic", rotation=90, zorder=15)
    ax.text(26.55, -19.15, "HWANGE\nNATIONAL PARK", fontsize=9, fontweight="bold", ha="center", zorder=15,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    hs_ = [Line2D([], [], marker="o", ls="none", ms=4.5, mfc="white", mec="black", label="Town or camp"),
           Line2D([], [], color="#111111", lw=1.0, label="National park boundary"),
           Line2D([], [], color="#777777", lw=0.6, label="District boundary"),
           Line2D([], [], color="#8c6d4f", lw=1.6, label="International boundary"),
           Patch(fc="#e8e8e8", ec="#999999", lw=0.4, label="Neighbouring country")]
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.025; h = (p.y1 - p.y0 - 0.03) / 2; w = 0.98 - x
    la = fig.add_axes([x, p.y0 + h + 0.03, w, h]); la.set_xticks([]); la.set_yticks([])
    for s in la.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    leg = la.legend(handles=hs_, title="Legend", loc="upper left", fontsize=10.5, title_fontsize=11, frameon=False,
                    borderaxespad=0.8, alignment="left", handlelength=2.4, handleheight=1.5, labelspacing=0.9)
    leg.get_title().set_fontweight("bold")
    lc = fig.add_axes([x, p.y0, w, h]); lc.set_facecolor("white")
    world.plot(ax=lc, fc="#f0f0f0", ec="#ffffff", lw=0.3); zwe.plot(ax=lc, fc="#d9d9d9", ec="none")
    mn.plot(ax=lc, fc="#a6a6a6", ec="none"); zwe_p.boundary.plot(ax=lc, color="#ffffff", lw=0.4)
    PG.plot(ax=lc, fc="#333333", ec="none")
    lc.set_xlim(24.3, 34.0); lc.set_ylim(-23.4, -14.0); lc.set_aspect(ASPECT, adjustable="datalim"); lc.set_xticks([]); lc.set_yticks([])
    for s in lc.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    lc.add_patch(Rectangle((0, 0.88), 1, 0.12, transform=lc.transAxes, fc="white", ec="none", zorder=5))
    lc.plot([0, 1], [0.88, 0.88], transform=lc.transAxes, color=fg, lw=0.6, zorder=6)
    lc.text(0.5, 0.94, "ZIMBABWE", transform=lc.transAxes, ha="center", va="center", fontsize=11, fontweight="bold", zorder=7)
    lc.legend(handles=[Patch(fc="#a6a6a6", label="Matabeleland North"), Patch(fc="#333333", label="Hwange NP")],
              loc="lower right", fontsize=7.5, frameon=False, handlelength=1.4)
    km = 111.32 * np.cos(np.radians(LAT)); L = 50 / km; x0, y0 = 26.95, -19.98
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.022, fc=fg if i % 2 == 0 else "white", ec=fg, lw=0.6, zorder=20))
    for v, xx in [(0, x0), (25, x0 + L / 2), (50, x0 + L)]:
        ax.text(xx, y0 + 0.035, f"{v}", ha="center", va="bottom", fontsize=7, zorder=20)
    ax.text(x0 + L + 0.025, y0 + 0.01, "km", fontsize=7, va="center", zorder=20)
    ax.text(0, -0.055, "Source: park boundary WDPA (UNEP-WCMC & IUCN 2025); Copernicus GLO-30 DEM hillshade (100 m); "
            "boundaries OCHA COD-AB 2023; Natural Earth. WGS 84.", transform=ax.transAxes, fontsize=6.5, ha="left", va="top")
    fig.savefig("out/map1_study_area.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved map1_study_area")


# ---- map 2: GEDI footprints -------------------------------------------------------
def map2():
    fig, ax, fg = frame("GEDI Footprint Map (2019 to 2023)")
    lift(ax)
    # out/gedi_1km.tif = mean of the footprints in each 1 km cell, written by grid_gedi.py
    a, ext = warp("gedi_1km", categorical=True)
    bounds = [0, 2, 5, 10, 20, 40, 200]; cols = ["#f7f1d6", "#d9e3a3", "#a5c96b", "#5fa443", "#2c7a2e", "#0b4219"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax))
    outline(ax); towns(ax); scalebar(ax, fg, -20.07)
    lab = ["0 – 2", "2 – 5", "5 – 10", "10 – 20", "20 – 40", "40 – 200"]
    legend_bl(ax, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(cols, lab)],
              "Mean footprint AGBD (Mg/ha)", fs=9.5, sp=0.45)
    finish(fig, ax, "Source: GEDI L4A footprint AGBD v2.1 (Dubayah et al. 2022), April 2019 to March 2023; quality flag 1, "
           "no degrade, beam sensitivity ≥ 0.95. Mean of the 25 m footprints (721 522 shots) in each 1 km cell; 95% of the park's 1 km cells hold at least one footprint. " + OSM + " WGS 84.", "map2_footprints")


# ---- map 3: carbon density ----------------------------------------------------------
def map3():
    fig, ax, fg = frame("Above-Ground Carbon Density Map (2020 to 2023)")
    lift(ax)
    a, ext = warp("agbd_pred"); c = a * 0.47
    bounds = [0, 1, 2, 4, 6, 10, 15, 60]; cols = ["#fbf6e4", "#e8e5b0", "#c4d68a", "#8fbd62", "#529a3f", "#2a7130", "#0d4222"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(np.ma.masked_invalid(c), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax)); outline(ax); towns(ax); scalebar(ax, fg, -20.07)
    lab = ["< 1", "1 – 2", "2 – 4", "4 – 6", "6 – 10", "10 – 15", "> 15"]
    legend_bl(ax, [Patch(fc=cc, ec="#555555", lw=0.4, label=l) for cc, l in zip(cols, lab)][::-1], "Carbon (Mg C/ha)", fs=9.5, sp=0.45)
    t = S["totals"]
    finish(fig, ax, f"Source: Random Forest on GEDI L4A cells with Sentinel-2, Sentinel-1 and GLO-30 predictors, 100 m. "
           f"Carbon = AGB × 0.47 (IPCC 2006). Park total {t['C_Mt']:.1f} Mt C. " + OSM + " WGS 84.", "map3_carbon")


# ---- map 4: uncertainty --------------------------------------------------------------
def map4():
    fig, ax, fg = frame("Prediction Uncertainty Map (2020 to 2023)")
    lift(ax)
    a, ext = warp("agbd_sd"); c = a * 0.47
    norm = mpl.colors.Normalize(0, 8); cmap = plt.get_cmap("RdPu")
    im = ax.imshow(np.ma.masked_invalid(c), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax)); outline(ax); towns(ax); scalebar(ax, fg, -20.07)
    colorbar_bl(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap), "Tree spread SD (Mg C/ha)", [0, 2, 4, 6, 8], ext="max")
    finish(fig, ax, "Source: standard deviation of 50 of the 200 Random Forest trees for each 100 m cell, converted with the 0.47 "
           "carbon fraction. It shows where the model is unsure, not total map error. " + OSM + " WGS 84.", "map4_uncertainty")


# ---- map 5: difference from ESA CCI ----------------------------------------------------
def map5():
    fig, ax, fg = frame("Difference from ESA CCI Biomass Map (2020)")
    lift(ax)
    a, ext = warp("agbd_pred"); b, _ = warp("cci_agb", src="rast")
    b = np.where(np.isfinite(b) | np.isnan(a), b, 0); b[~np.isfinite(b)] = 0
    d = (a - b) * 0.47
    norm = mpl.colors.TwoSlopeNorm(0, -10, 10); cmap = plt.get_cmap("BrBG")
    im = ax.imshow(np.ma.masked_invalid(d), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax)); outline(ax); towns(ax); scalebar(ax, fg, -20.07)
    colorbar_bl(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap), "This study minus CCI (Mg C/ha)", [-10, -5, 0, 5, 10], ext="both")
    finish(fig, ax, "Source: this study's 100 m carbon map minus ESA CCI Biomass v5 (2020, 100 m) × 0.47; CCI cells with no value "
           "are read as 0 Mg/ha. Green: this study higher. " + OSM + " WGS 84.", "map5_difference")


if __name__ == "__main__":
    import sys
    for n in (sys.argv[1:] or ["1", "2", "3", "4", "5"]): globals()[f"map{n}"]()
