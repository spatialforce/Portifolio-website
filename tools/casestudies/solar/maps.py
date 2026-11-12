"""Five maps for case study 7: AHP solar farm site suitability, Matabeleland South.
Layout ported from ../rainfall/maps.py. Rasters are EPSG:32735 and get warped to
WGS 84 for display. Run with PROJ_LIB/PROJ_DATA set to rasterio's proj_data.
Output: out/*.png"""
import os, json
import numpy as np, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from rasterio.warp import reproject, calculate_default_transform, Resampling
from matplotlib.colors import LightSource, BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from scipy import ndimage
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)

ASPECT = 1 / np.cos(np.radians(21))
AUTHOR = "© Kudzanai Chakavarika"
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
B = "../population/raw/bnd/"

prov = gpd.read_file("data/province.gpkg").to_crs(4326)
dist = gpd.read_file("data/districts_ms.gpkg").to_crs(4326)
zwe_p = gpd.read_file(B + "zwe_admin1.shp")
zwe = gpd.read_file(B + "zwe_admin0.shp")
world = gpd.read_file(f"zip://{NE}").cx[24:34, -25:-17]
PG = gpd.GeoSeries([prov.geometry.union_all()], crs=4326)

TOWNS = [("Gwanda", 29.009, -20.936), ("Beitbridge", 30.003, -22.217),
         ("Plumtree", 27.814, -20.485), ("Esigodini", 28.939, -20.287),
         ("Filabusi", 29.283, -20.530), ("West Nicholson", 29.361, -21.060),
         ("Maphisa", 28.503, -21.057)]
BYO = ("Bulawayo", 28.583, -20.150)   # context, outside the province

SITES = [("Blanket Mine (12 MW)", -20.8552, 28.9130),
         ("Gwanda Timber Farm (100 MW)", -20.9426, 29.0016),
         ("ZPC-Intratrek Gwanda (100 MW)", -20.7365, 28.9396),
         ("Nottingham Estate (4.5 MW)", -22.1124, 29.6454),
         ("Falcon College (1 MW)", -20.2172, 28.9684),
         ("Mashaba Mini-Grid (99 kW)", -21.7342, 28.9758)]

# full-frame extent: province plus room lower right for the legend
EX = (26.35, 31.95, -22.75, -19.25)
TY = 0.962
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
SRC = ("Source: Global Solar Atlas v2 (Solargis) GHI; Copernicus GLO-30 slope; ESA WorldCover 2021; "
       "OpenStreetMap lines and roads; GHS-SMOD 2020; WDPA. 250 m grid, UTM 35S. " + OSM + " WGS 84.")

_WARP = {}


def warp(name, categorical=False):
    """Read rast/<name>.tif (EPSG:32735) warped to WGS 84 for display: (array, extent)."""
    key = (name, categorical)
    if key in _WARP: return _WARP[key]
    with rasterio.open(f"rast/{name}.tif") as s:
        tr, w, h = calculate_default_transform(s.crs, "EPSG:4326", s.width, s.height, *s.bounds)
        dst = np.full((h, w), np.nan, dtype="float32")
        reproject(rasterio.band(s, 1), dst, dst_transform=tr, dst_crs="EPSG:4326",
                  resampling=Resampling.nearest if categorical else Resampling.bilinear,
                  dst_nodata=np.nan)
        if s.nodata is not None:
            dst[dst == s.nodata] = np.nan
    ext = (tr.c, tr.c + tr.a * w, tr.f + tr.e * h, tr.f)
    _WARP[key] = (dst, ext)
    return _WARP[key]


_BM = {}


def basemap():
    if "osm" in _BM: return _BM["osm"]
    import contextily as ctx
    f = "rast/basemap_hot.npz"
    if not os.path.exists(f):
        img, ext = ctx.bounds2img(25.6, -23.4, 32.8, -18.7, zoom=8, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:4326")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1)
    grey &= ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255
    img = 0.72 * img + 0.28
    _BM["osm"] = (np.clip(img, 0, 1), tuple(d["ext"]))
    return _BM["osm"]


def narrow(ax, x, y, fg="#222222", bg="white", h=0.085):
    """Two-tone split arrowhead north arrow in axes units; tip at (x, y)."""
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9,
                             transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11,
            fontweight="bold", color=fg, zorder=70, path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def scalebar(ax, fg, x0, y0, alt="white", length=100, end_ax=None):
    km = 111.32 * np.cos(np.radians(21)); L = length / km
    if end_ax is not None:  # right end of bar sits under this axes-x (e.g. north arrow centre)
        x0 = EX[0] + end_ax * (EX[1] - EX[0]) - L
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.055, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (length // 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(x, y0 + 0.09, f"{v}", ha="center", va="bottom", fontsize=7.5, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + 0.06, y0 + 0.025, "km", fontsize=7.5, color=fg, va="center", zorder=60, path_effects=halo)


def legend_br(ax, handles, title, fg="#222222", bg="white", ncol=1, loc="lower left", anchor=(0.008, 0.012), fs=10.5, sp=0.75):
    leg = ax.legend(handles=handles, title=title, loc=loc, bbox_to_anchor=anchor,
                    fontsize=fs, title_fontsize=fs + 0.5, frameon=True, fancybox=False, edgecolor=fg,
                    facecolor=bg, framealpha=0.94, alignment="left", labelcolor=fg, ncol=ncol,
                    borderpad=0.9, handlelength=2.4, handleheight=1.4, labelspacing=sp, columnspacing=1.6)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65)
    leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)
    return leg


def colorbar_br(fig, ax, sm, title, ticks, fg="#222222", w=0.30, h=0.15, x=0.008, y=0.012):
    box = ax.inset_axes([x, y, w, h]); box.set_xticks([]); box.set_yticks([]); box.set_zorder(65)
    box.set_facecolor((1, 1, 1, 0.94))
    for sp in box.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    box.text(0.045, 0.86, title, transform=box.transAxes, ha="left", va="top", fontsize=11,
             fontweight="bold", color=fg, linespacing=1.3)
    ca = box.inset_axes([0.07, 0.26, 0.86, 0.17])
    cb = fig.colorbar(sm, cax=ca, orientation="horizontal", ticks=ticks)
    ca.tick_params(labelsize=9.5, length=2); cb.outline.set_linewidth(0.5)


def pclip(ax):
    """Province outline as a clip patch."""
    verts, codes = [], []
    for g in prov.geometry:
        for poly in getattr(g, "geoms", [g]):
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords)
                verts += list(xy); codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    p = PathPatch(Path(verts, codes), transform=ax.transData, fc="none", ec="none"); ax.add_patch(p)
    return p


def lift(ax):
    """Soft drop shadow under the province so the data sits above the basemap."""
    for k in range(1, 8):
        PG.translate(0.016 * k, -0.016 * k).plot(ax=ax, fc="black", ec="none", alpha=0.055, zorder=1.5)
    PG.plot(ax=ax, fc="white", ec="none", zorder=1.6)


def frame3(title, ext=EX, width=11.0):
    h = width * 0.92 * (ext[3] - ext[2]) * ASPECT / (ext[1] - ext[0]) / 0.9
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0.055, 0.075, 0.92, 0.9])
    fg = "#222222"; fig.patch.set_facecolor("white")
    img, bext = basemap()
    ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(ASPECT)
    xt = range(int(np.ceil(ext[0])), int(ext[1]) + 1); yt = range(int(np.ceil(ext[2])), int(ext[3]) + 1)
    ax.set_xticks(list(xt)); ax.set_yticks(list(yt))
    ax.set_xticklabels([f"{x}°E" for x in xt], color=fg); ax.set_yticklabels([f"{-y}°S" for y in yt], color=fg)
    ax.tick_params(length=2, colors=fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.7)
    halo = [pe.withStroke(linewidth=4, foreground="white")]
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=15,
            fontweight="bold", color=fg, zorder=70, path_effects=halo)
    narrow(ax, 0.965, TY, fg, "white")
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5,
            color=fg, zorder=70, path_effects=halo)
    return fig, ax, fg


HALO = [pe.withStroke(linewidth=2.2, foreground="white")]


def towns(ax, n=7, fs=7.5, byo=True):
    for name, x, y in TOWNS[:n]:
        ax.plot(x, y, "o", ms=3.4, mfc="white", mec="black", mew=0.8, zorder=30)
        ax.text(x + 0.05, y + 0.04, name, fontsize=fs, color="black", zorder=30, path_effects=HALO)
    if byo:
        n, x, y = BYO
        ax.plot(x, y, "s", ms=4.5, mfc="white", mec="black", mew=0.8, zorder=30)
        ax.text(x + 0.05, y + 0.04, n, fontsize=fs + 0.5, fontweight="bold", zorder=30, path_effects=HALO)


def borders(ax, dc="#555555", pc="#111111"):
    dist.boundary.plot(ax=ax, color=dc, lw=0.45, ls="--", zorder=5)
    PG.boundary.plot(ax=ax, color=pc, lw=1.0, zorder=6)


def source(fig, ax, text, fg="#222222", ext=EX):
    ax.set_aspect(ASPECT); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.text(0, -0.05, text, transform=ax.transAxes, fontsize=6.8, color=fg, ha="left", va="top")


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print("saved", name)


# ---- map 1: study area (side column + Zimbabwe locator) ----------------------
EXT1 = (26.45, 31.35, -22.65, -19.0)
MAIN = [0.035, 0.07, 0.60, 0.88]
GAP = 0.03


def boxes(fig, ax):
    fig.canvas.draw(); p = ax.get_position()
    x = p.x1 + 0.025; h = (p.y1 - p.y0 - GAP) / 2; w = 0.98 - x
    return [x, p.y0 + h + GAP, w, h], [x, p.y0, w, h]


def map1():
    elev, eext = warp("elev")
    ls = LightSource(azdeg=315, altdeg=40)
    dx = (eext[1] - eext[0]) / elev.shape[1] * 111320 * np.cos(np.radians(21))
    dy = (eext[3] - eext[2]) / elev.shape[0] * 111320
    hs = ls.hillshade(np.nan_to_num(elev, nan=np.nanmean(elev)), vert_exag=8, dx=dx, dy=dy)

    fig = plt.figure(figsize=(11.6, 7.6), dpi=220); ax = fig.add_axes(MAIN)
    fg = "#222222"; fig.patch.set_facecolor("white"); ax.set_facecolor("#f4f4f4")
    ax.set_xlim(EXT1[0], EXT1[1]); ax.set_ylim(EXT1[2], EXT1[3]); ax.set_aspect(ASPECT, anchor="W")
    xt = range(27, 32); yt = range(-22, -19)
    ax.set_xticks(list(xt)); ax.set_yticks(list(yt))
    ax.set_xticklabels([f"{x}°E" for x in xt], color=fg); ax.set_yticklabels([f"{-y}°S" for y in yt], color=fg)
    ax.grid(color="#bbbbbb", lw=0.3, ls=":"); ax.tick_params(length=2, colors=fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    ax.text(0.5, TY, "Study Area Map", transform=ax.transAxes, ha="center", va="center",
            fontsize=14, fontweight="bold", color=fg, zorder=50)
    fig.canvas.draw(); narrow(ax, 0.95, TY + 0.015, fg, "white", h=0.10)
    ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#777777", zorder=50)

    world.plot(ax=ax, fc="#e8e8e8", ec="#ffffff", lw=0.6, zorder=1)
    zwe.plot(ax=ax, fc="#f0ede8", ec="none", zorder=1.2)
    g = 0.35 + 0.6 * hs
    im = ax.imshow(g, extent=eext, cmap="gray", vmin=0, vmax=1, zorder=2, interpolation="bilinear")
    im.set_clip_path(pclip(ax))
    ax.set_xlim(EXT1[0], EXT1[1]); ax.set_ylim(EXT1[2], EXT1[3])
    zwe_p.boundary.plot(ax=ax, color="#999999", lw=0.5, zorder=4)
    borders(ax)
    towns(ax)
    for _, r in dist.iterrows():
        if "Urban" in r["district"] or r["district"] in ("Beitbridge", "Plumtree"): continue
        c = r.geometry.representative_point()
        ax.text(c.x, c.y + 0.12, r["district"].replace(" Rural", "").upper(), fontsize=6.5, color="#222222",
                ha="center", style="italic", zorder=7, path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
    for n, x, y in [("BOTSWANA", 27.0, -21.8), ("SOUTH AFRICA", 29.9, -22.5), ("ZIMBABWE", 30.1, -19.55)]:
        ax.text(x, y, n, fontsize=7, color="#888888", ha="center", style="italic", zorder=15)

    hs_ = [Line2D([], [], marker="s", ls="none", ms=6, mfc="white", mec="black", label="City"),
           Line2D([], [], marker="o", ls="none", ms=4.5, mfc="white", mec="black", label="Town"),
           Line2D([], [], color="#111111", lw=1.0, label="Province boundary"),
           Line2D([], [], color="#555555", lw=0.6, ls="--", label="District boundary"),
           Line2D([], [], color="#999999", lw=0.6, label="Other provinces"),
           Patch(fc="#e8e8e8", ec="#999999", lw=0.4, label="Neighbouring country")]
    up, lo = boxes(fig, ax)
    la = fig.add_axes(up); la.set_xticks([]); la.set_yticks([]); la.set_facecolor("none")
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    leg = la.legend(handles=hs_, title="Legend", loc="upper left", fontsize=10.5, title_fontsize=11,
                    frameon=False, borderaxespad=0.8, alignment="left", labelcolor=fg,
                    handlelength=2.4, handleheight=1.5, labelspacing=0.9)
    leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)

    # locator: Zimbabwe with the province highlighted
    lc = fig.add_axes(lo); lc.set_facecolor("#ffffff")
    world.plot(ax=lc, fc="#f0f0f0", ec="#ffffff", lw=0.3)
    zwe.plot(ax=lc, fc="#cfcfcf", ec="#ffffff", lw=0.3)
    zwe_p.boundary.plot(ax=lc, color="#ffffff", lw=0.4)
    PG.plot(ax=lc, fc="#6b6b6b", ec="none")
    lc.set_xlim(24.3, 34.0); lc.set_ylim(-23.4, -14.0); lc.set_aspect(ASPECT, adjustable="datalim")
    lc.set_xticks([]); lc.set_yticks([])
    for sp in lc.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    lc.add_patch(Rectangle((0, 0.88), 1, 0.12, transform=lc.transAxes, fc="white", ec="none", zorder=5))
    lc.plot([0, 1], [0.88, 0.88], transform=lc.transAxes, color=fg, lw=0.6, zorder=6)
    lc.text(0.5, 0.94, "ZIMBABWE", transform=lc.transAxes, ha="center", va="center",
            fontsize=11, fontweight="bold", color=fg, zorder=7)

    km = 111.32 * np.cos(np.radians(22)); L = 100 / km; x0, y0 = 26.6, -22.45
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.05, fc=fg if i % 2 == 0 else "white", ec=fg, lw=0.6, zorder=20))
    for v, x in [(0, x0), (50, x0 + L / 2), (100, x0 + L)]:
        ax.text(x, y0 + 0.09, f"{v}", ha="center", va="bottom", fontsize=7, color=fg, zorder=20)
    ax.text(x0 + L + 0.06, y0 + 0.02, "km", fontsize=7, color=fg, va="center", zorder=20)
    ax.text(0, -0.055, "Source: Copernicus GLO-30 DEM hillshade (250 m); boundaries OCHA COD-AB 2023; Natural Earth. Geographic coordinates, WGS 84.",
            transform=ax.transAxes, fontsize=6.5, color=fg, ha="left", va="top")
    save(fig, "map1_study_area")


# ---- map 2: GHI --------------------------------------------------------------
def map2():
    fig, ax, fg = frame3("Global Horizontal Irradiance Map")
    lift(ax)
    ghi, gext = warp("ghi")
    norm = mpl.colors.Normalize(5.0, 6.2); cmap = plt.get_cmap("YlOrRd")
    im = ax.imshow(np.ma.masked_invalid(ghi), extent=gext, cmap=cmap, norm=norm, zorder=2, interpolation="bilinear")
    clip = pclip(ax); im.set_clip_path(clip)
    sm = ndimage.gaussian_filter(np.nan_to_num(ghi, nan=np.nanmean(ghi)), 3)
    xs = np.linspace(gext[0], gext[1], ghi.shape[1]); ys = np.linspace(gext[3], gext[2], ghi.shape[0])
    cl = ax.contour(xs, ys, sm, levels=[5.4, 5.6, 5.8, 6.0], colors="#4a1500", linewidths=0.8, zorder=3)
    cl.set_clip_path(clip)
    ax.clabel(cl, fmt="%.1f", fontsize=7.5, inline=True, inline_spacing=4)
    borders(ax); towns(ax); scalebar(ax, fg, 30.5, -22.6, end_ax=0.965)
    colorbar_br(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                "GHI (kWh/m²/day)", [5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2], w=0.30, h=0.15)
    source(fig, ax, "Source: Global Solar Atlas v2 (Solargis), long-term average daily GHI, ~250 m. "
           "Dark lines every 0.2 kWh/m²/day; dashed lines: districts. " + OSM + " WGS 84.")
    save(fig, "map2_ghi")


# ---- map 3: criteria score small multiples -----------------------------------
SCORE_COLS = ["#d73027", "#fdae61", "#ffffbf", "#a6d96a", "#1a9850"]


def map3():
    panels = [("ghi_s", "GHI (44.4%)"), ("d_grid_s", "Distance to grid (21.5%)"),
              ("slope_s", "Slope (13.6%)"), ("d_road_s", "Distance to roads (8.3%)"),
              ("lc_s", "Land cover (8.3%)"), ("d_sett_s", "Distance to settlements (3.8%)")]
    lon0, lon1, lat0, lat1 = 26.3, 31.5, -22.6, -18.95
    Wf = 13.0; cw = Wf / 3; ch = cw * (lat1 - lat0) * ASPECT / (lon1 - lon0); TS = 0.62
    Hf = 3 * ch + TS; fh = ch / Hf
    fig = plt.figure(figsize=(Wf, Hf), dpi=220); fig.patch.set_facecolor("white"); fg = "#222222"
    img, bext = basemap()
    cmap = ListedColormap(SCORE_COLS); norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], cmap.N)
    pos = ([[c / 3, 2 * fh, 1 / 3, fh] for c in range(3)] +
           [[c / 3, fh, 1 / 3, fh] for c in range(3)] +
           [[c / 3, 0, 1 / 3, fh] for c in range(3)])
    for i, (name, lab) in enumerate(panels):
        a = fig.add_axes(pos[i]); a.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
        lift(a)
        arr, ext = warp(name, categorical=True)
        im = a.imshow(np.ma.masked_invalid(arr), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
        im.set_clip_path(pclip(a))
        PG.boundary.plot(ax=a, color="#111111", lw=0.8, zorder=6)
        a.set_aspect(ASPECT); a.set_xlim(lon0, lon1); a.set_ylim(lat0, lat1); a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
        a.text(0.03, 0.955, lab, transform=a.transAxes, fontsize=12, fontweight="bold", ha="left", va="top",
               zorder=70, bbox=dict(fc="white", ec=fg, lw=0.6, pad=3.5))
    # constraints panel
    a = fig.add_axes(pos[6]); a.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    lift(a)
    m, ext = warp("mask", categorical=True)
    pv, _ = warp("prov", categorical=True)
    excl = np.where(pv == 1, 1 - m, np.nan)
    im = a.imshow(np.ma.masked_invalid(excl), extent=ext, cmap=ListedColormap(["#f0f0f0", "#636363"]),
                  norm=BoundaryNorm([-0.5, 0.5, 1.5], 2), zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(a))
    PG.boundary.plot(ax=a, color="#111111", lw=0.8, zorder=6)
    a.set_aspect(ASPECT); a.set_xlim(lon0, lon1); a.set_ylim(lat0, lat1); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
    a.text(0.03, 0.955, "Excluded areas", transform=a.transAxes, fontsize=12, fontweight="bold", ha="left", va="top",
           zorder=70, bbox=dict(fc="white", ec=fg, lw=0.6, pad=3.5))
    # legend cell spanning the last two cells
    k = fig.add_axes([1 / 3, 0, 2 / 3, fh]); k.set_xlim(0, 1); k.set_ylim(0, 1); k.set_xticks([]); k.set_yticks([])
    for sp in k.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
    k.add_patch(Rectangle((0.03, 0.20), 0.94, 0.75, fc="white", ec=fg, lw=0.6))
    k.text(0.055, 0.915, "Criterion score (AHP weight in panel titles)", ha="left", va="top",
           fontsize=12.5, fontweight="bold", color=fg)
    labs = ["1  Least suitable", "2  Low", "3  Moderate", "4  High", "5  Most suitable"]
    for j, (c, l) in enumerate(zip(SCORE_COLS, labs)):
        cx = 0.055 if j < 3 else 0.52; cy = [0.71, 0.525, 0.34][j % 3]
        k.add_patch(Rectangle((cx, cy - 0.055), 0.065, 0.11, fc=c, ec="#777777", lw=0.5))
        k.text(cx + 0.085, cy, l, ha="left", va="center", fontsize=11.5, color=fg)
    k.add_patch(Rectangle((0.52, 0.34 - 0.055), 0.065, 0.11, fc="#636363", ec="#777777", lw=0.5))
    k.text(0.605, 0.34, "Excluded (constraints)", ha="left", va="center", fontsize=11.5, color=fg)
    narrow(k, 0.07, 0.165, fg, "white", h=0.10)
    km = 111.32 * np.cos(np.radians(21)); L = (100 / km) / ((lon1 - lon0) * 2); x0 = 0.42; y0 = 0.075
    for j in range(4):
        k.add_patch(Rectangle((x0 + j * L / 4, y0), L / 4, 0.022, fc=fg if j % 2 == 0 else "white", ec=fg, lw=0.6))
    for v, x in [(0, x0), (50, x0 + L / 2), (100, x0 + L)]:
        k.text(x, y0 + 0.035, f"{v}", ha="center", va="bottom", fontsize=8.5, color=fg)
    k.text(x0 + L + 0.015, y0 + 0.011, "km", fontsize=8.5, color=fg, va="center")
    k.text(0.97, 0.03, AUTHOR, transform=k.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg)
    fig.text(0.5, 1 - (TS / 2) / Hf, "Criteria Score Maps", ha="center", va="center", fontsize=16, fontweight="bold")
    fig.text(0, -0.012, SRC, fontsize=7.5, color=fg, ha="left", va="top")
    save(fig, "map3_criteria")


# ---- map 4: exclusion constraints by cause -----------------------------------
def map4():
    fig, ax, fg = frame3("Exclusion Constraints Map")
    lift(ax)
    slope, ext = warp("slope")
    wc, _ = warp("worldcover", categorical=True)
    water, _ = warp("water", categorical=True)
    built, _ = warp("builtup", categorical=True)
    pa, _ = warp("protected", categorical=True)
    pv, _ = warp("prov", categorical=True)
    code = np.full(slope.shape, np.nan)
    code[slope > 5] = 1
    code[(water == 1) | (wc == 80) | (wc == 90) | (wc == 95)] = 2
    code[(built == 1)] = 3
    code[pa == 1] = 4
    code[pv != 1] = np.nan
    cols = ["#b35806", "#2b8cbe", "#636363", "#31a354"]
    cmap = ListedColormap(cols); norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)
    im = ax.imshow(np.ma.masked_invalid(code), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax))
    borders(ax); towns(ax); scalebar(ax, fg, 30.5, -22.6, end_ax=0.965)
    hs = [Patch(fc=cols[0], label="Slope over 5°"),
          Patch(fc=cols[1], label="Water or wetland"),
          Patch(fc=cols[2], label="Built-up (+500 m)"),
          Patch(fc=cols[3], label="Protected area (+500 m)")]
    legend_br(ax, hs, "Excluded from analysis")
    source(fig, ax, "Source: Copernicus GLO-30 slope; ESA WorldCover 2021; JRC Global Surface Water; WDPA (May 2025). "
           "Cells failing any constraint are removed before the weighted overlay. " + OSM + " WGS 84.")
    save(fig, "map4_constraints")


# ---- map 5: suitability with validation sites --------------------------------
def map5():
    fig, ax, fg = frame3("Solar Farm Suitability Map")
    lift(ax)
    cls, ext = warp("suit_class", categorical=True)
    cls = np.where(cls == 0, np.nan, cls)
    pv, _ = warp("prov", categorical=True)
    show = np.where(pv == 1, np.where(np.isnan(cls), 0, cls), np.nan)
    cols = ["#9e9e9e"] + SCORE_COLS
    cmap = ListedColormap(cols); norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5], cmap.N)
    im = ax.imshow(np.ma.masked_invalid(show), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax))
    # transmission lines
    pl = gpd.read_file("data/power_lines.geojson").set_crs(4326, allow_override=True)
    pl.plot(ax=ax, color="#3a3a3a", lw=0.45, alpha=0.55, zorder=7)
    borders(ax); towns(ax, byo=True); scalebar(ax, fg, 30.5, -22.6, end_ax=0.965)
    res = json.load(open("out/results.json"))
    for name, lat, lon in SITES:
        ax.plot(lon, lat, "*", ms=13, mfc="#ffd700", mec="black", mew=0.9, zorder=40)
    names = {"Blanket Mine (12 MW)": (-0.42, 0.10), "Gwanda Timber Farm (100 MW)": (0.07, -0.16),
             "ZPC-Intratrek Gwanda (100 MW)": (0.07, 0.08), "Nottingham Estate (4.5 MW)": (0.07, 0.07),
             "Falcon College (1 MW)": (0.07, 0.07), "Mashaba Mini-Grid (99 kW)": (0.07, 0.07)}
    for name, lat, lon in SITES:
        dx, dy = names[name]
        ax.text(lon + dx, lat + dy, name, fontsize=7.5, zorder=40, fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    tot = sum(res["classes"].values())
    labs = ["Excluded"] + [f"{n}  ({100 * res['classes'][n] / tot:.0f})"
                           for n in ["Unsuitable", "Low", "Moderate", "High", "Very high"]]
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=l) for c, l in zip(cols, labs)]
    hs += [Line2D([], [], color="#3a3a3a", lw=0.6, alpha=0.7, label="Transmission line"),
           Line2D([], [], marker="*", ls="none", ms=12, mfc="#ffd700", mec="black", label="Existing / planned plant")]
    legend_br(ax, hs, "Suitability (% of analysable area)", fs=9.5, sp=0.5)
    source(fig, ax, "Source: AHP weighted overlay of six criteria (CR = 0.023), 250 m grid; constraints removed. "
           "Plants from OSM and ZERA licence records. " + OSM + " WGS 84.")
    save(fig, "map5_suitability")


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5"]):
        globals()[f]()
