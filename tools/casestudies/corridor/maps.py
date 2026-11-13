"""Maps and graphs for the Hwange to Chizarira elephant corridor case study. Analysis runs on a 100 m UTM 35S grid;
maps are drawn in geographic coordinates (WGS 84) after resampling to 0.001 degrees. Output: out/*.png"""
import os, sys, json
import numpy as np, pandas as pd, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from rasterio.warp import reproject, Resampling
from affine import Affine
from pyproj import Transformer
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; FG = "#222222"
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
EXT = (25.95, 29.15, -19.05, -17.35); ASPECT = 1 / np.cos(np.radians(18.2))
G = json.load(open("raw/grid.json")); TR = Affine(G["res"], 0, G["x0"], 0, -G["res"], G["y1"])
GR = 0.001; GW, GH = round((EXT[1] - EXT[0]) / GR), round((EXT[3] - EXT[2]) / GR); GT = Affine(GR, 0, EXT[0], 0, -GR, EXT[3])
Z = np.load("data/rasters.npz"); SM = json.load(open("data/summary.json")); PROF = pd.read_csv("data/profile.csv")
TO_G = Transformer.from_crs(32735, 4326, always_xy=True)
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
world = gpd.read_file(f"zip://{NE}").cx[24:31, -20:-16]
lakes = gpd.read_file("zip://../../corridors/raw/ne_10m_lakes.zip").cx[25:30, -19.5:-16]
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326)
zwe1 = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(4326)
dist = gpd.read_file("../population/raw/bnd/zwe_admin2.shp").to_crs(4326).cx[EXT[0]:EXT[1], EXT[2]:EXT[3]]
pa = gpd.read_file("../baobab/raw/wdpa.geojson").to_crs(4326).cx[EXT[0]:EXT[1], EXT[2]:EXT[3]]
NP = pa[pa.DESIG_ENG.eq("National Park")]; SA = pa[pa.DESIG_ENG.isin(["Safari Area", "State Forest"])]
WMA = pa[pa.DESIG_ENG.eq("Wildlife Management Area")]
roads = gpd.read_file("raw/osm_roads.gpkg").to_crs(4326); rivers = gpd.read_file("raw/osm_rivers.gpkg").to_crs(4326)
main_rd = roads[roads.kind.str.replace("_link", "").isin(["motorway", "trunk", "primary"])]
minor_rd = roads[~roads.index.isin(main_rd.index)]
big_riv = rivers[rivers.name.fillna("").str.contains("Gwayi|Shangani|Lutope|Mbumbusi|Sengwa|Lubu|Busi|Mlibizi|Deka|Sebungwe|Mzola|Kana|Bubi", regex=True)]
lcp = gpd.read_file("data/lcp.gpkg").to_crs(4326); pinch = gpd.read_file("data/pinch.gpkg").to_crs(4326)
TOWNS = [("Hwange", 26.50, -18.355), ("Dete", 26.86, -18.62), ("Binga", 27.34, -17.62), ("Lupane", 27.77, -18.93),
         ("Siabuwa", 28.13, -17.46), ("Gokwe", 28.95, -18.22)]


def geo(a, how=Resampling.nearest):
    d = np.full((GH, GW), np.nan, "float32")
    reproject(a.astype("float32"), d, src_transform=TR, src_crs="EPSG:32735", dst_transform=GT, dst_crs="EPSG:4326", resampling=how, dst_nodata=np.nan)
    return d


M = geo(Z["M"].astype("uint8")) > 0.5
GEXT = (EXT[0], EXT[1], EXT[2], EXT[3])


def hillshade():
    dem = rasterio.open("raw/dem.tif").read(1).astype(float)
    hs = LightSource(azdeg=315, altdeg=40).hillshade(dem, vert_exag=4, dx=G["res"], dy=G["res"])
    return geo(dem, Resampling.bilinear), geo(hs, Resampling.bilinear)


def axes_setup(ax, fs=9, face="#e6e6e6", tc=FG):
    ax.set_facecolor(face); ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(ASPECT)
    xs = [26, 26.5, 27, 27.5, 28, 28.5, 29]; ys = [-19, -18.5, -18, -17.5]
    ax.set_xticks(xs); ax.set_yticks(ys)
    ax.set_xticklabels([f"{x:g}°E" for x in xs], fontsize=fs); ax.set_yticklabels([f"{-y:g}°S" for y in ys], fontsize=fs, rotation=90, va="center")
    ax.tick_params(length=2)
    for sp in ax.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)


def north(ax, ty, size=1.0, c=FG):
    yt = EXT[2] + ty * (EXT[3] - EXT[2]); x = EXT[0] + 0.12
    ax.annotate("", xy=(x, yt), xytext=(x, yt - 0.17 * size), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=c, lw=1.2), zorder=70)
    ax.text(x, yt - 0.185 * size, "N", ha="center", va="top", fontsize=10 * size, fontweight="bold", color=c, zorder=70)


def header(fig, ax, title, fs=13, h=0.052, gap=0.008):
    """Small framed title strip directly above the map frame, same width as the map."""
    ax.apply_aspect(); p = ax.get_position()
    hx = fig.add_axes([p.x0, p.y1 + gap, p.width, h]); hx.set_xticks([]); hx.set_yticks([]); hx.set_facecolor("white")
    for sp in hx.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)
    hx.text(0.5, 0.5, title, ha="center", va="center", fontsize=fs, fontweight="bold", color=FG)
    return hx


def frame(title, face="#e6e6e6", tc=FG, size=(12.4, 7.6)):
    fig = plt.figure(figsize=size, dpi=200); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.05, 0.08, 0.93, 0.82]); axes_setup(ax, face=face)
    header(fig, ax, title)
    north(ax, 0.94, c=tc)
    return fig, ax


def legend_in(ax, handles, title, fs=9.5, face="white", tc=FG, ncol=1):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=(0.993, 0.05), fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=tc, facecolor=face, framealpha=1, borderpad=0.7, alignment="left", ncol=ncol,
                    handlelength=2.0, handleheight=1.1, labelspacing=0.55, labelcolor=tc, columnspacing=1.2)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.get_title().set_color(tc); leg.set_zorder(90)
    ax.text(0.993, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#777777" if face != "white" else "#555555", zorder=90)
    return leg


def scalebar(ax, c=FG, y=None, x0=None, L_km=50, fs=7.5):
    km = 111.32 * np.cos(np.radians(18.2)); L = L_km / km
    y = EXT[2] + 0.05 if y is None else y; x0 = EXT[0] + 0.08 if x0 is None else x0
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y), L / 4, 0.022, fc=c if i % 2 == 0 else "none", ec=c, lw=0.6, zorder=70))
    for v, x in [(0, x0), (L_km // 2, x0 + L / 2), (L_km, x0 + L)]:
        ax.text(x, y + 0.035, f"{v}", ha="center", va="bottom", fontsize=fs, color=c, zorder=70)
    ax.text(x0 + L + 0.03, y + 0.011, "km", fontsize=fs, va="center", color=c, zorder=70)


def source(ax, text, y=-0.075):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.5, ha="left", va="top")


def save(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def outside(ax, fc="#e6e6e6", ec="#ffffff"):
    world.plot(ax=ax, fc=fc, ec=ec, lw=0.6, zorder=1)


def water(ax, fc="#a9c8e0"):
    lakes.plot(ax=ax, fc=fc, ec="none", zorder=6)


def border(ax, c="#111111"):
    zwe.boundary.plot(ax=ax, color=c, lw=1.0, zorder=8)


def towns(ax, skip=(), tc="#111111", halo=HALO, mfc="white"):
    for n, x, y in TOWNS:
        if n in skip: continue
        ax.plot(x, y, "o", ms=4, mfc=mfc, mec="black", mew=0.8, zorder=30)
        ax.text(x + 0.025, y + 0.02, n, fontsize=8, color=tc, zorder=30, path_effects=halo)


def park_labels(ax, c="#1d3d1d", halo=HALO, extra=True):
    L = [("HWANGE\nNATIONAL PARK", 26.45, -18.85, 9), ("CHIZARIRA\nNATIONAL PARK", 27.93, -17.78, 9)]
    if extra: L += [("Chete SA", 27.95, -17.42, 7.5), ("Chirisa SA", 28.42, -17.88, 7.5), ("Matetsi SA", 26.12, -18.12, 7.5),
                    ("Deka SA", 26.72, -18.1, 7.5), ("Sijarira SF", 27.62, -17.86, 7.5)]
    for t, x, y, fs in L:
        ax.text(x, y, t, fontsize=fs, ha="center", va="center", color=c, fontweight="bold" if fs > 8 else "normal", zorder=31, path_effects=halo)


def img(ax, rgba, z=2):
    ax.imshow(rgba, extent=GEXT, zorder=z, interpolation="nearest")


def classed(arr, colours, mask):
    rgba = np.zeros(arr.shape + (4,))
    for v, c in colours.items():
        m = (arr == v) & mask; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    return rgba


ELEV = [(0, 700, "#7fae6a", "< 700"), (700, 850, "#b9cc8a", "700 – 850"), (850, 1000, "#e6dca0", "850 – 1 000"),
        (1000, 1150, "#d2a86e", "1 000 – 1 150"), (1150, 9999, "#a5703f", "> 1 150")]


def locator(ax, box=(0.835, 0.68, 0.155, 0.27)):
    la = ax.inset_axes(list(box)); la.set_zorder(85); la.set_facecolor("white")
    zwe1.plot(ax=la, fc="#e3e3e3", ec="white", lw=0.4)
    la.add_patch(Rectangle((EXT[0], EXT[2]), EXT[1] - EXT[0], EXT[3] - EXT[2], fc="#a5703f", alpha=0.35, ec="#7a2e0e", lw=1.1))
    zwe.boundary.plot(ax=la, color=FG, lw=0.6)
    la.set_xlim(24.6, 33.7); la.set_ylim(-22.6, -14.1); la.set_aspect(1 / np.cos(np.radians(19))); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(FG); sp.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.87), 1, 0.13, transform=la.transAxes, fc="white", ec=FG, lw=0.6, zorder=5))
    la.text(0.5, 0.935, "Zimbabwe", transform=la.transAxes, ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=6)


def map1():
    dem, hs = hillshade()
    fig, ax = frame("Study Area Map"); outside(ax)
    rgba = np.zeros((GH, GW, 4))
    for lo, hi, c, _ in ELEV:
        m = (dem >= lo) & (dem < hi) & M; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    rgba[..., :3] *= (0.62 + 0.38 * np.nan_to_num(hs, nan=1))[..., None]
    img(ax, rgba); water(ax)
    SA.plot(ax=ax, fc="none", ec="#2e6b2e", lw=0.8, hatch="////", zorder=10)
    NP.plot(ax=ax, fc="#f5c518", alpha=0.55, ec="none", zorder=10); NP.boundary.plot(ax=ax, color="#7a5a00", lw=1.4, zorder=11)
    big_riv.plot(ax=ax, color="#3d7fb8", lw=0.7, zorder=12); main_rd.plot(ax=ax, color="#7a2e0e", lw=1.1, zorder=13)
    border(ax); towns(ax); park_labels(ax, c="#111111")
    for n, x, y in [("ZAMBIA", 26.55, -17.42)]:
        ax.text(x, y, n, fontsize=8, color="#555555", style="italic", ha="center", zorder=31)
    locator(ax)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in ELEV]
    h += [Patch(fc="#f5c518", alpha=0.65, ec="#7a5a00", lw=1.2, label="National parks"),
          Patch(fc="none", ec="#2e6b2e", hatch="////", label="Safari area or forest"),
          Line2D([], [], color="#3d7fb8", lw=1, label="Rivers"), Line2D([], [], color="#7a2e0e", lw=1.3, label="Main roads")]
    legend_in(ax, h, "Elevation (m)", ncol=2); scalebar(ax)
    source(ax, "Source: Copernicus DEM GLO-30; protected areas WDPA (UNEP-WCMC & IUCN); roads, rivers and towns OpenStreetMap; boundaries OCHA COD-AB; Natural Earth. Geographic coordinates, WGS 84.")
    save(fig, "map1_study_area")


LC = {10: ("#2f6b2f", "Tree cover"), 20: ("#a9b85a", "Shrubland"), 30: ("#e8d98a", "Grassland"), 40: ("#e08a3c", "Cropland"),
      50: ("#c0282d", "Built-up"), 60: ("#c9bfb2", "Bare ground"), 80: ("#5a8fc7", "Open water"), 90: ("#4fb3a9", "Wetland")}


def map2():
    _, hs = hillshade(); lc = geo(rasterio.open("raw/lc.tif").read(1))
    fig, ax = frame("Land Cover Map"); outside(ax)
    g = 0.7 + 0.3 * np.nan_to_num(hs, nan=1)
    rgba = classed(lc, {k: v[0] for k, v in LC.items()}, M); rgba[..., :3] *= (0.55 + 0.45 * g)[..., None]
    img(ax, rgba); water(ax, "#5a8fc7")
    NP.boundary.plot(ax=ax, color="black", lw=1.3, zorder=11); border(ax)
    towns(ax); park_labels(ax, c="black", extra=False)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=n) for c, n in LC.values()]
    h += [Patch(fc="none", ec="black", lw=1.3, label="National parks")]
    legend_in(ax, h, "Land cover (2021)"); scalebar(ax)
    source(ax, "Source: ESA WorldCover 10 m v200 (2021), resampled to 100 m. Geographic coordinates, WGS 84.")
    save(fig, "map2_land_cover")


RES5 = [("#1a9850", "1"), ("#a6d96a", "5 – 15"), ("#fee08b", "20 – 40"), ("#f46d43", "50 – 80"), ("#a50026", "100")]


def bin5(a):
    return np.digitize(a, [1.5, 17, 45, 90])


def map3():
    W = SM["ahp"]["weights"]
    P = [("f_pop", "(a) Population Density", W["pop"]), ("f_lc", "(b) Land Cover", W["lc"]),
         ("f_road", "(c) Distance to Roads", W["road"]), ("f_wat", "(d) Distance to Water", W["wat"]), ("f_slp", "(e) Slope", W["slp"])]
    fig = plt.figure(figsize=(16.5, 7.6), dpi=200)
    cols = {i: c for i, (c, _) in enumerate(RES5)}
    pw, ph = 0.305, 0.34; Y = [0.49, 0.055]
    for i, (k, t, w) in enumerate(P):
        r, c = divmod(i, 3)
        ax = fig.add_axes([0.03 + c * 0.325, Y[r], pw, ph]); axes_setup(ax, fs=7.5)
        outside(ax); a = geo(Z[k].astype(float)); img(ax, classed(bin5(a), cols, M & np.isfinite(a))); water(ax); border(ax)
        NP.boundary.plot(ax=ax, color="black", lw=0.8, zorder=11)
        header(fig, ax, f"{t} (weight {w:.2f})", fs=10.5, h=0.045, gap=0.006)
        yt = EXT[2] + 0.9 * (EXT[3] - EXT[2]); x = EXT[0] + 0.1
        ax.annotate("", xy=(x, yt + 0.05), xytext=(x, yt - 0.12), arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.5", color=FG, lw=1), zorder=70)
        ax.text(x, yt - 0.13, "N", ha="center", va="top", fontsize=8, fontweight="bold", zorder=70)
        scalebar(ax, fs=6.5)
        ax.text(0.99, 0.015, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="#555555", zorder=90)
    ht = fig.add_axes([0.03, 0.935, 0.955, 0.05]); ht.set_xticks([]); ht.set_yticks([])
    for sp in ht.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)
    ht.text(0.5, 0.5, "Resistance Factors Map", ha="center", va="center", fontsize=13.5, fontweight="bold")
    lx = fig.add_axes([0.03 + 2 * 0.325, Y[1], pw, ph]); lx.axis("off")
    lx.legend(handles=[Patch(fc=c, ec="#777777", lw=0.3, label=l) for c, l in RES5], title="Resistance (1 – 100)", loc="center",
              fontsize=10.5, title_fontsize=11, frameon=True, fancybox=False, edgecolor=FG, borderpad=1, labelspacing=0.8, handlelength=2.4,
              alignment="left").get_title().set_fontweight("bold")
    fig.text(0.03, 0.0, "Source: WorldPop 2020 (constrained, UN adjusted); ESA WorldCover 2021; OpenStreetMap roads and rivers; Copernicus DEM GLO-30. "
             "Geographic coordinates, WGS 84.", fontsize=8.5)
    save(fig, "map3_factors")


COST4 = [(0, 10, "#fff5d6", "< 10"), (10, 25, "#fdbf6f", "10 – 25"), (25, 50, "#e0592b", "25 – 50"), (50, 101, "#7f1d0e", "> 50")]


def map4():
    cost = geo(np.where(Z["M"], Z["cost"], np.nan), Resampling.bilinear)
    fig, ax = frame("Resistance Surface Map"); outside(ax, fc="#bdbdbd")
    rgba = np.zeros((GH, GW, 4))
    for lo, hi, c, _ in COST4:
        m = (cost >= lo) & (cost < hi) & M; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    img(ax, rgba); water(ax, "#7d8fa3"); border(ax)
    NP.boundary.plot(ax=ax, color="#1a1a1a", lw=1.4, zorder=11)
    towns(ax); park_labels(ax, c="#111111", extra=False)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in COST4]
    h += [Patch(fc="#7d8fa3", label="Lake Kariba"),
          Patch(fc="none", ec="#1a1a1a", lw=1.4, label="National parks")]
    legend_in(ax, h, "Resistance (1 – 100)"); scalebar(ax)
    source(ax, "Source: weighted overlay of five resistance factors (AHP); this study. Geographic coordinates, WGS 84.")
    save(fig, "map4_resistance")


COR = {3: ("#0b6e4f", "≤ 5"), 2: ("#5dbb8a", "5 – 10"), 1: ("#c7ead2", "10 – 20")}


def map5():
    _, hs = hillshade(); cls = geo(Z["cls"])
    fig, ax = frame("Least-Cost Corridor Map", face="#f3f1ec"); outside(ax, fc="#f3f1ec", ec="#cfcfcf")
    g = 0.86 + 0.14 * np.nan_to_num(hs, nan=1); base = np.dstack([g * 0.97, g * 0.96, g * 0.93, M.astype(float)]); img(ax, base)
    img(ax, classed(cls, {k: v[0] for k, v in COR.items()}, M), z=3); water(ax); border(ax)
    NP.plot(ax=ax, fc="#8c8c8c", alpha=0.45, ec="none", zorder=9); NP.boundary.plot(ax=ax, color="#333333", lw=1.1, zorder=10)
    main_rd.plot(ax=ax, color="#555555", lw=0.8, zorder=12)
    lcp.plot(ax=ax, color="white", lw=4.2, zorder=20); lcp.plot(ax=ax, color="#111111", lw=1.9, zorder=21)
    (x0, y0), (x1, y1) = lcp.geometry[0].coords[0], lcp.geometry[0].coords[-1]
    for x, y, t, dx, ha, dy, va in [(x0, y0, "Leaves Hwange", -0.04, "right", -0.035, "top"), (x1, y1, "Enters Chizarira", -0.02, "right", 0.04, "bottom")]:
        ax.plot(x, y, "o", ms=6, mfc="white", mec="#111111", mew=1.3, zorder=22)
        ax.text(x + dx, y + dy, t, fontsize=8.5, ha=ha, va=va, fontweight="bold", zorder=23, path_effects=HALO)
    towns(ax); park_labels(ax, c="#222222", extra=False)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for c, l in COR.values()]
    h += [Line2D([], [], color="#111111", lw=2.2, label="Least-cost path"),
          Patch(fc="#8c8c8c", alpha=0.6, ec="#333333", label="National parks"), Line2D([], [], color="#555555", lw=0.9, label="Main roads")]
    legend_in(ax, h, "Corridor (% above least cost)", face="white"); scalebar(ax)
    source(ax, "Source: cost-weighted distance on the resistance surface; this study. Geographic coordinates, WGS 84.")
    save(fig, "map5_corridor")


def map6():
    BG = "#14161c"; TC = "#e8e8e8"; dk = [pe.withStroke(linewidth=2.2, foreground=BG)]
    dens = geo(Z["dens"], Resampling.bilinear); core = geo((Z["cls"] >= 2).astype("uint8")) > 0.5
    fig, ax = frame("Corridor Pressures Map", face=BG, tc=TC); outside(ax, fc="#20232b", ec="#3a3d46")
    land = np.dstack([np.full((GH, GW), 0.13), np.full((GH, GW), 0.14), np.full((GH, GW), 0.17), M.astype(float)]); img(ax, land)
    PC = [(2, 10, "#6b2459"), (10, 25, "#c2414f"), (25, 1e9, "#f39a4e")]
    glow = np.zeros((GH, GW, 4))
    for lo, hi, c in PC:
        m = M & (dens >= lo) & (dens < hi); glow[m, :3] = mpl.colors.to_rgb(c); glow[m, 3] = 0.9
    img(ax, glow, z=3)
    water(ax, "#26364a")
    ax.contourf(np.linspace(EXT[0], EXT[1], GW), np.linspace(EXT[3], EXT[2], GH), core.astype(float), levels=[0.5, 1.5], colors=["#3fd0a0"], alpha=0.45, zorder=4)
    ax.contour(np.linspace(EXT[0], EXT[1], GW), np.linspace(EXT[3], EXT[2], GH), core.astype(float), levels=[0.5], colors=["#3fd0a0"], linewidths=1.3, zorder=5)
    zwe.boundary.plot(ax=ax, color="#9a9a9a", lw=0.8, zorder=8)
    NP.boundary.plot(ax=ax, color="#d0d0d0", lw=1.1, zorder=10)
    minor_rd.plot(ax=ax, color="#bfc6d6", lw=0.45, alpha=0.8, zorder=12); main_rd.plot(ax=ax, color="#ffffff", lw=1.2, zorder=13)
    lcp.plot(ax=ax, color="#7fe6ff", lw=1.6, zorder=20)
    px, py = pinch.geometry[0].x, pinch.geometry[0].y
    ax.plot(px, py, "*", ms=15, mfc="white", mec=BG, mew=0.8, zorder=24)
    ax.text(px + 0.05, py + 0.04, f"Narrowest point ({SM['pinch']['width_km']:g} km)", fontsize=8.5, color="white", fontweight="bold", zorder=24, path_effects=dk)
    towns(ax, tc=TC, halo=dk, mfc=BG); park_labels(ax, c="#d8d8d8", halo=dk, extra=False)
    h = [Patch(fc=c, label=l) for (*_, c), l in zip(PC, ["2 – 10", "10 – 25", "> 25"])] + [
         Line2D([], [], color="#ffffff", lw=1.3, label="Main roads"), Line2D([], [], color="#bfc6d6", lw=0.7, label="Other roads"),
         Patch(fc="#3fd0a0", alpha=0.6, ec="#3fd0a0", lw=1.3, label="Corridor"), Line2D([], [], color="#7fe6ff", lw=1.6, label="Least-cost path"),
         Line2D([], [], ls="", marker="*", ms=11, mfc="white", mec=BG, label="Narrowest point")]
    legend_in(ax, h, "Population (people/km²)", face="#1d2028", tc=TC); scalebar(ax, c=TC)
    source(ax, "Source: WorldPop 2020 (constrained); OpenStreetMap roads; corridor from this study. Geographic coordinates, WGS 84.")
    save(fig, "map6_pressures")


def chart(title, ylab, xlab=None, size=(7.2, 4.4)):
    fig, ax = plt.subplots(figsize=size, dpi=200)
    ax.text(0.5, 1.05, title, transform=ax.transAxes, ha="center", fontsize=12.5, fontweight="bold")
    ax.set_ylabel(ylab, fontsize=10.5); ax.tick_params(labelsize=10)
    if xlab: ax.set_xlabel(xlab, fontsize=10.5)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
    return fig, ax


def done(fig, ax, name, y=-0.16):
    ax.text(1, y, AUTHOR, transform=ax.transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig(f"out/{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved", name)


def fig1():
    d = SM["lcp"]["lc_km"]; k = sorted(d, key=lambda x: -d[x])
    fig, ax = chart("Land Cover Along the Least-Cost Path", "Length of path (km)")
    ax.bar(k, [d[x] for x in k], width=0.5, color=[{v[1]: v[0] for v in LC.values()}.get(x, "#888") for x in k])
    for i, x in enumerate(k): ax.text(i, d[x] + 1.5, f"{d[x]:g} km", ha="center", fontsize=10.5)
    ax.set_ylim(0, 100); done(fig, ax, "fig1_path_cover")


def fig2():
    s = PROF.cost.rolling(15, center=True, min_periods=1).mean()
    fig, ax = chart("Resistance Along the Least-Cost Path", "Cost per cell (1 to 100)", "Distance from Hwange National Park (km)", size=(8.4, 4.2))
    ax.plot(PROF.km, s, color="#0b6e4f", lw=2)
    med = SM["cost"]["median"]; ax.axhline(med, color="#7f1d0e", lw=1.2)
    ax.text(PROF.km.max(), med + 0.6, f"Median for the whole area, {med:g}", ha="right", va="bottom", fontsize=9.5, color="#7f1d0e")
    pk = SM["pinch"]["km_along"]; ax.plot(pk, s[(PROF.km - pk).abs().idxmin()], "o", ms=7, mfc="white", mec="#111111", mew=1.2)
    ax.text(pk + 2.5, s[(PROF.km - pk).abs().idxmin()], "Narrowest point", ha="left", va="center", fontsize=9.5)
    ax.set_xlim(0, PROF.km.max()); ax.set_ylim(0, max(25, med + 5)); done(fig, ax, "fig2_path_profile", y=-0.2)


def fig3():
    S = SM["sens"]; k = list(S)
    lab = [x.replace(" (base)", "\n(base)").replace("Land cover first", "Land cover\nfirst").replace("People only doubled", "People\ndoubled")
           .replace("Equal weights", "Equal\nweights").replace("Without water", "Without\nwater") for x in k]
    v = [S[x]["within2km_pct"] for x in k]
    fig, ax = chart("Agreement With the Base Path", "Path within 2 km of the base path (%)", size=(7.6, 4.4))
    ax.bar(lab, v, width=0.5, color=["#0b6e4f"] + ["#5dbb8a"] * (len(k) - 1))
    for i, x in enumerate(k): ax.text(i, v[i] + 1.5, f"{v[i]:g} %\n{S[x]['len_km']:g} km", ha="center", fontsize=9.5)
    ax.set_ylim(0, 125); ax.set_yticks(range(0, 101, 20)); done(fig, ax, "fig3_sensitivity", y=-0.22)


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "map6", "fig1", "fig2", "fig3"]): globals()[n]()
