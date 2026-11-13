"""Maps and graphs for the baobab habitat suitability case study. Simple maps for a general reader.
Run from this folder with PROJ_LIB set to rasterio's proj_data. Output: out/*.png"""
import os, sys, json
import numpy as np, rasterio, geopandas as gpd, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from affine import Affine
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"; LK = "../../corridors/raw/ne_10m_lakes.zip"
world = gpd.read_file(f"zip://{NE}").cx[20:38, -26:-12]
africa = gpd.read_file(f"zip://{NE}").cx[5:60, -40:10]
lakes = gpd.read_file(f"zip://{LK}").cx[25:33.2, -22.6:-15.4]
prov = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(4326)
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326)
pa = gpd.read_file("data/pa.gpkg")
SADC = ["AGO", "BWA", "COM", "COD", "SWZ", "LSO", "MDG", "MWI", "MUS", "MOZ", "NAM", "SYC", "ZAF", "TZA", "ZMB", "ZWE"]
AUTHOR = "© Kudzanai Chakavarika"
TOWNS = [("Harare", 31.052, -17.829), ("Bulawayo", 28.583, -20.150), ("Mutare", 32.670, -18.970), ("Gweru", 29.817, -19.450),
         ("Masvingo", 30.833, -20.074), ("Chinhoyi", 30.199, -17.367), ("Hwange", 26.500, -18.364), ("Victoria Falls", 25.840, -17.932),
         ("Beitbridge", 30.000, -22.217), ("Kariba", 28.800, -16.517), ("Gwanda", 29.000, -20.940), ("Chiredzi", 31.667, -21.050)]
PROV_OFF = {"Midlands": (0.1, -0.6), "Masvingo": (-0.5, -0.45)}
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
ASPECT = 1 / np.cos(np.radians(19))
EXT = (24.6, 36.0, -22.95, -14.95)
Z = np.load("data/stack.npz"); M = Z["mask"]; TR = Affine(*Z["transform"]); H, W = M.shape
GEXT = (TR.c, TR.c + W * TR.a, TR.f + H * TR.e, TR.f)
S = np.load("data/suit.npy"); C = np.load("data/classes.npy")
SM = json.load(open("data/summary.json")); MD = json.load(open("data/model.json"))
REC = pd.read_csv("data/records.csv"); RAW = pd.read_csv("raw/gbif_ZW.csv")
GREENS = ["#ececec", "#c7e9c0", "#74c476", "#1f7a3a"]
CLASSES = ["Not suitable", "Low", "Moderate", "High"]
FG = "#222222"


def axes_setup(ax, step=1, fs=9.5):
    ax.set_facecolor("#e0e0e0"); ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(ASPECT)
    xs = range(26, 36, step); ys = range(-22, -15, step)
    ax.set_xticks(list(xs)); ax.set_yticks(list(ys))
    ax.set_xticklabels([f"{x}°E" for x in xs], fontsize=fs)
    ax.set_yticklabels([f"{-y}°S" for y in ys], fontsize=fs, rotation=90, va="center")  # vertical, reading down the axis
    ax.tick_params(length=2)
    for sp in ax.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)


def north(ax, ty, size=1.0):
    yt = EXT[2] + ty * (EXT[3] - EXT[2]); x = EXT[0] + 0.35
    ax.annotate("", xy=(x, yt), xytext=(x, yt - 0.5 * size), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=FG, lw=1.2), zorder=20)
    ax.text(x, yt - 0.55 * size, "N", ha="center", va="top", fontsize=10 * size, fontweight="bold", color=FG, zorder=20)


def frame(title, size=(11.6, 8.8)):
    fig = plt.figure(figsize=size, dpi=220); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.06, 0.08, 0.92, 0.9]); axes_setup(ax)
    ax.text(0.5, 0.965, title, transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color=FG, zorder=50,
            path_effects=[pe.withStroke(linewidth=3, foreground="#e0e0e0")])
    north(ax, 0.965)
    return fig, ax


def legend_in(ax, handles, title, fs=10.5):
    """Framed legend inside the map, bottom-right corner; © just under it."""
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=(0.992, 0.045), fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=FG, framealpha=1, borderpad=0.8, alignment="left",
                    handlelength=2.2, handleheight=1.3, labelspacing=0.75)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.set_zorder(60)
    ax.text(0.992, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=60)
    return leg


def colorbar_in(fig, ax, norm, cmap, title, box=(0.835, 0.045, 0.157, 0.36), fs=10.5):
    """Colour bar in a framed white box inside the map, bottom-right corner."""
    ax.add_patch(Rectangle(box[:2], box[2], box[3], transform=ax.transAxes, fc="white", ec=FG, lw=0.6, zorder=55))
    ax.text(box[0] + box[2] / 2, box[1] + box[3] - 0.028, title, transform=ax.transAxes, ha="center", va="center", fontsize=fs, fontweight="bold", zorder=56)
    ca = ax.inset_axes([box[0] + box[2] * 0.3, box[1] + 0.03, box[2] * 0.13, box[3] - 0.1]); ca.set_zorder(57)
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ca); ca.tick_params(labelsize=fs - 1); cb.outline.set_linewidth(0.5)
    ax.text(0.992, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=60)
    return box[0]


def scalebar(ax, x_right_axes, y=-22.75, fs=7.5):
    """200 km bar in the bottom-left corner (legend sits bottom right)."""
    km = 111.32 * np.cos(np.radians(22)); L = 200 / km
    x0 = EXT[0] + 0.3
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y), L / 4, 0.07, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=20))
    for v, x in [(0, x0), (100, x0 + L / 2), (200, x0 + L)]:
        ax.text(x, y + 0.12, f"{v}", ha="center", va="bottom", fontsize=fs, zorder=20)
    ax.text(x0 + L + 0.08, y + 0.03, "km", fontsize=fs, va="center", zorder=20)


def leg_left(fig, ax, leg):
    fig.canvas.draw(); bb = leg.get_window_extent().transformed(ax.transAxes.inverted()); return bb.x0


def source(ax, text, y=-0.06):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7, ha="left", va="top")


def base(ax, fc="#e0e0e0"):
    world.plot(ax=ax, fc=fc, ec="#ffffff", lw=0.7, zorder=1)


def overlay(ax, towns=True, provlabels=False, tc="#111111"):
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=6)
    prov.boundary.plot(ax=ax, color="#666666", lw=0.5, zorder=7)
    zwe.boundary.plot(ax=ax, color="#111111", lw=1.0, zorder=8)
    for n, x, y in ([] if not towns else TOWNS):
        big = n in ("Harare", "Bulawayo")
        ax.plot(x, y, "s" if big else "o", ms=5 if big else 3.5, mfc="white", mec="black", mew=0.8, zorder=9)
        ax.text(x + 0.08, y + 0.05, n, fontsize=8.5 if big else 7.5, fontweight="bold" if big else "normal", color=tc, zorder=9, path_effects=HALO)
    if provlabels:
        for _, r in prov.iterrows():
            if r.adm1_name in ("Harare", "Bulawayo"): continue
            c = r.geometry.representative_point(); dx, dy = PROV_OFF.get(r.adm1_name, (0, -0.25))
            ax.text(c.x + dx, c.y + dy, r.adm1_name.upper(), fontsize=7, color="#333333", ha="center", style="italic", zorder=9, path_effects=HALO)
    for n, x, y in [("ZAMBIA", 27.0, -16.0), ("MOZAMBIQUE", 34.4, -18.2), ("BOTSWANA", 26.2, -20.9), ("SOUTH AFRICA", 29.6, -22.75)]:
        ax.text(x, y, n, fontsize=7.5, color="#666666", ha="center", style="italic", zorder=9)


def locator(ax, zc, box=(0.80, 0.60, 0.192, 0.37)):
    """SADC locator inside the map, top-right corner (Map 1 only)."""
    la = ax.inset_axes(list(box)); la.set_zorder(58); la.set_facecolor("white")
    africa.plot(ax=la, fc="#f0f0f0", ec="white", lw=0.3)
    africa[africa.ADM0_A3.isin(SADC)].plot(ax=la, fc="#cfcfcf", ec="white", lw=0.3)
    africa[africa.ADM0_A3 == "ZWE"].plot(ax=la, fc=zc, ec="none")
    la.set_xlim(9, 52); la.set_ylim(-36, 6); la.set_aspect(1 / np.cos(np.radians(15)), adjustable="datalim"); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(FG); sp.set_linewidth(0.6)
    la.text(0.5, 0.93, "SADC", transform=la.transAxes, ha="center", va="center", fontsize=10.5, fontweight="bold", zorder=7)


def save(fig, name):
    """Inner frame is the map edge; an outer frame is drawn round the whole layout (coordinates and source inside it)."""
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def dem():
    with rasterio.open("raw/dem500.tif") as s: z = s.read(1).astype(float); b = s.bounds
    dx = (b.right - b.left) / z.shape[1] * 111320 * np.cos(np.radians(19)); dy = (b.top - b.bottom) / z.shape[0] * 111320
    hs = LightSource(azdeg=315, altdeg=40).hillshade(z, vert_exag=6, dx=dx, dy=dy)
    from rasterio.features import geometry_mask
    inside = geometry_mask(zwe.geometry, out_shape=z.shape, transform=rasterio.open("raw/dem500.tif").transform, invert=True)
    return z, hs, inside, (b.left, b.right, b.bottom, b.top)


def grid_img(ax, rgb, z=2):
    ax.imshow(rgb, extent=GEXT, zorder=z, interpolation="nearest")


def map1():
    z, hs, inside, ext = dem()
    fig, ax = frame("Study Area Map"); base(ax)
    cmap = ListedColormap(plt.get_cmap("terrain")(np.linspace(0.22, 0.95, 256))); norm = mpl.colors.Normalize(100, 2500)
    rgb = cmap(norm(z))[..., :3] * (0.6 + 0.4 * hs[..., None])
    ax.imshow(np.dstack([rgb, inside.astype(float)]), extent=ext, zorder=2, interpolation="bilinear")
    overlay(ax, provlabels=True)
    x0 = colorbar_in(fig, ax, norm, cmap, "Elevation (m)")
    locator(ax, "#8a5a2b"); scalebar(ax, x0)
    source(ax, "Source: SRTM 1 arc-second DEM (NASA), resampled to 15 arc-seconds; boundaries OCHA COD-AB; Natural Earth. Geographic coordinates, WGS 84.")
    save(fig, "map1_study_area")


def map2():
    z, hs, inside, ext = dem()
    fig, ax = frame("Baobab Records Map"); base(ax)
    g = 0.78 + 0.2 * hs; ax.imshow(np.dstack([g, g, g, inside.astype(float)]), extent=ext, zorder=2, interpolation="bilinear")
    overlay(ax, tc="#333333")
    used = set(REC.key); rest = RAW[~RAW.key.isin(used)]
    ax.scatter(rest.decimalLongitude, rest.decimalLatitude, s=10, fc="none", ec="#1f7a3a", lw=0.6, zorder=10)
    ax.scatter(REC.decimalLongitude, REC.decimalLatitude, s=26, fc="#1f7a3a", ec="white", lw=0.6, zorder=11)
    h = [Line2D([], [], ls="", marker="o", ms=7, mfc="#1f7a3a", mec="white", label=f"Records used ({len(REC)})"),
         Line2D([], [], ls="", marker="o", ms=5, mfc="none", mec="#1f7a3a", label=f"Records removed ({len(RAW) - len(REC)})"),
         Line2D([], [], color="#111111", lw=1, label="National boundary"), Line2D([], [], color="#666666", lw=0.6, label="Province boundary")]
    leg = legend_in(ax, h, "Baobab records"); scalebar(ax, leg_left(fig, ax, leg))
    source(ax, "Source: GBIF.org occurrence download for Adansonia digitata L. in Zimbabwe (535 records); one record kept per 10 km. Geographic coordinates, WGS 84.")
    save(fig, "map2_records")


def map3():
    V = [("bio11", "(a) Winter Temperature", "°C", "YlOrRd", (12, 23)),
         ("bio12", "(b) Annual Rainfall", "mm", "Blues", (300, 1300)),
         ("bio15", "(c) Rainfall Seasonality", "%", "Purples", (80, 130))]
    fig = plt.figure(figsize=(16.2, 4.6), dpi=220)
    for i, (v, t, lab, cm, lim) in enumerate(V):
        ax = fig.add_axes([0.02 + i * 0.33, 0.1, 0.31, 0.88]); axes_setup(ax, step=2, fs=8.5)
        base(ax); a = np.ma.masked_where(~M, Z[v])
        im = ax.imshow(a, extent=GEXT, cmap=cm, vmin=lim[0], vmax=lim[1], zorder=2, interpolation="nearest")
        lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=6); zwe.boundary.plot(ax=ax, color="#111111", lw=0.9, zorder=8)
        prov.boundary.plot(ax=ax, color="#666666", lw=0.35, zorder=7)
        ax.text(0.5, 0.94, t, transform=ax.transAxes, ha="center", va="center", fontsize=12, fontweight="bold", zorder=50)
        north(ax, 0.94, 0.8)
        box = (0.8, 0.045, 0.185, 0.5)
        ax.add_patch(Rectangle(box[:2], box[2], box[3], transform=ax.transAxes, fc="white", ec=FG, lw=0.6, zorder=55))
        ax.text(box[0] + box[2] / 2, box[1] + box[3] - 0.04, lab, transform=ax.transAxes, ha="center", va="center", fontsize=10, fontweight="bold", zorder=56)
        ca = ax.inset_axes([box[0] + 0.035, box[1] + 0.04, 0.03, box[3] - 0.13]); ca.set_zorder(57)
        cb = fig.colorbar(im, cax=ca); ca.tick_params(labelsize=8.5); cb.outline.set_linewidth(0.5)
        km = 111.32 * np.cos(np.radians(22)); L = 200 / km; x1 = EXT[0] + box[0] * (EXT[1] - EXT[0]) - 0.4; x0, y0 = x1 - L, -22.7
        for k in range(2): ax.add_patch(Rectangle((x0 + k * L / 2, y0), L / 2, 0.09, fc=FG if k == 0 else "white", ec=FG, lw=0.6, zorder=20))
        ax.text(x0, y0 + 0.15, "0", ha="center", fontsize=7.5); ax.text(x0 + L, y0 + 0.15, "200 km", ha="center", fontsize=7.5)
        ax.text(0.985, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="#555555", zorder=60)
    fig.text(0.02, 0.0, "Source: CHELSA V2.1 climatologies 1981–2010 (Karger et al., 2017), 30 arc-seconds. Geographic coordinates, WGS 84.", fontsize=8, va="top")
    save(fig, "map3_climate")


def map4():
    fig, ax = frame("Habitat Suitability Map"); base(ax)
    rgb = np.ones((H, W, 4)); rgb[..., 3] = 0
    for k, c in enumerate(GREENS):
        m = C == k; rgb[m, :3] = mpl.colors.to_rgb(c); rgb[m, 3] = 1
    grid_img(ax, rgb); overlay(ax)
    br = ["< 0.2", "0.2 – 0.4", "0.4 – 0.6", "≥ 0.6"]
    h = [Patch(fc=GREENS[k], ec="#777777", lw=0.4, label=f"{CLASSES[k]} ({br[k]})") for k in range(3, -1, -1)]
    h += [Patch(fc="#a9c8e0", ec="none", label="Lake"), Line2D([], [], color="#666666", lw=0.6, label="Province boundary")]
    leg = legend_in(ax, h, "Suitability (0 – 1)"); scalebar(ax, leg_left(fig, ax, leg))
    source(ax, "Source: MaxEnt model of 145 GBIF baobab records on CHELSA V2.1 climate (1981–2010), 30 arc-seconds. Geographic coordinates, WGS 84.")
    save(fig, "map4_suitability")


def map5():
    from rasterio.features import rasterize
    PM = rasterize(pa.geometry, (H, W), transform=TR, fill=0, default_value=1).astype(bool) & M
    fig, ax = frame("Suitable Habitat and Protected Areas Map"); base(ax)
    rgb = np.ones((H, W, 4)); rgb[..., 3] = 0; suit = C >= 2
    for m, c in [(M, "#f2f2f2"), (M & PM & ~suit, "#d9d9d9"), (suit & ~PM, "#e8a33d"), (suit & PM, "#1f7a3a")]:
        rgb[m, :3] = mpl.colors.to_rgb(c); rgb[m, 3] = 1
    grid_img(ax, rgb)
    pa.boundary.plot(ax=ax, color="#333333", lw=0.4, zorder=5)
    overlay(ax, towns=False)
    for n, x, y in [("Gonarezhou NP", 31.75, -21.75), ("Save\nConservancy", 32.15, -20.45), ("Mana Pools NP", 29.55, -15.75),
                    ("Chewore SA", 30.25, -15.95), ("Hwange NP", 26.45, -19.15), ("Matusadona NP", 28.55, -16.85), ("Hurungwe SA", 29.25, -16.4)]:
        ax.text(x, y, n, fontsize=8, fontweight="bold", ha="center", va="center", zorder=12, path_effects=HALO)
    h = [Patch(fc="#1f7a3a", label=f"Suitable, protected ({SM['suit_in_pa_pct']} %)"),
         Patch(fc="#e8a33d", label=f"Suitable, unprotected ({round(100 - SM['suit_in_pa_pct'], 1)} %)"),
         Patch(fc="#d9d9d9", ec="#333333", lw=0.4, label="Protected, not suitable"),
         Patch(fc="#f2f2f2", ec="#999999", lw=0.4, label="Low or not suitable"),
         Patch(fc="#a9c8e0", label="Lake")]
    leg = legend_in(ax, h, "Suitable habitat"); scalebar(ax, leg_left(fig, ax, leg))
    source(ax, "Source: habitat suitability from this study; protected areas WDPA (UNEP-WCMC & IUCN). NP national park, SA safari area. Geographic coordinates, WGS 84.")
    save(fig, "map5_protected")


def fig1():
    nm = {"bio11": "Winter temperature", "bio15": "Rainfall seasonality", "bio12": "Annual rainfall"}
    imp = sorted(MD["importance"].items(), key=lambda x: -x[1])
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=220)
    ax.bar([nm[k] for k, _ in imp], [v for _, v in imp], width=0.5, color="#1f7a3a")
    for i, (_, v) in enumerate(imp): ax.text(i, v + 1.2, f"{v} %", ha="center", fontsize=10.5)
    ax.set_ylabel("Share of model importance (%)", fontsize=10.5); ax.set_ylim(0, 85); ax.tick_params(labelsize=10)
    ax.text(0.5, 1.04, "Importance of Each Climate Factor", transform=ax.transAxes, ha="center", fontsize=12.5, fontweight="bold")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
    ax.text(1, -0.16, AUTHOR, transform=ax.transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig("out/fig1_importance.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved fig1")


def fig2():
    g, p = MD["resp"]["bio11"]
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=220)
    ax.plot(g, p, color="#1f7a3a", lw=2)
    for lo, hi, c, t in [(0, 0.2, "#ececec", "Not suitable"), (0.6, 1.05, "#d8eed3", "High")]:
        ax.axhspan(lo, hi, color=c, zorder=0); ax.text(g[0] + 0.15, (lo + min(hi, 1)) / 2, t, va="center", fontsize=9.5, color="#444444")
    q = SM["rec"]["bio11"]; ax.axvline(q[1], color="#777777", lw=1, ls="--"); ax.text(q[1] + 0.15, 0.08, f"Median at records\n{q[1]} °C", fontsize=9, color="#444444")
    ax.set_xlabel("Mean temperature of the coldest three months (°C)", fontsize=10.5); ax.set_ylabel("Habitat suitability (0 to 1)", fontsize=10.5)
    ax.set_ylim(0, 1.05); ax.set_xlim(g[0], g[-1]); ax.tick_params(labelsize=10)
    ax.text(0.5, 1.04, "Suitability and Winter Temperature", transform=ax.transAxes, ha="center", fontsize=12.5, fontweight="bold")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.text(1, -0.2, AUTHOR, transform=ax.transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig("out/fig2_response.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved fig2")


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "fig1", "fig2"]): globals()[n]()
