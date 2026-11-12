"""Maps for the Hwange Power Station NO2 and SO2 case study (Sentinel-5P, 2019 to 2025)."""
import os, json
import numpy as np, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from scipy import ndimage
from shapely.geometry import Point

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
LAT = 18.4; ASPECT = 1 / np.cos(np.radians(LAT))
AUTHOR = "© Kudzanai Chakavarika"; OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
B = "../population/raw/bnd/"
zwe = gpd.read_file(B + "zwe_admin0.shp").to_crs(4326)
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(4326)
world = gpd.read_file("zip://../../corridors/raw/ne_10m_admin_0_countries.zip").cx[10:45, -36:-4]
S = json.load(open("out/stats.json"))
HPS, MAA = (26.4706, -18.3833), (27.18594, -17.352722)
EX = (25.55, 27.45, -18.92, -17.95)                 # zoom on Hwange for maps 2 to 5
TY = 0.955; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
TOWNS = [("Hwange", 26.4918, -18.3646, (-0.075, 0.018)), ("Dete", 26.8630, -18.6207, (0.02, 0.015)),
         ("Lukosi", 26.5580, -18.3480, (0.02, 0.0)), ("Cross Dete", 26.8960, -18.4940, (0.02, 0.015))]
with rasterio.open("rast/no2_post.tif") as r: GEXT = (r.bounds.left, r.bounds.right, r.bounds.bottom, r.bounds.top)
rd = lambda n: rasterio.open(f"rast/{n}.tif").read(1)


def circle(xy, km, crs=32735):
    return gpd.GeoSeries([Point(xy)], crs=4326).to_crs(crs).buffer(km * 1000, 128).to_crs(4326)


def basemap(ext, f):
    import contextily as ctx
    if not os.path.exists(f):
        img, e = ctx.bounds2img(ext[0] - .05, ext[2] - .05, ext[1] + .05, ext[3] + .05, zoom=11, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, e = ctx.warp_tiles(img, e, t_crs="EPSG:4326"); np.savez_compressed(f, img=img, ext=np.array(e))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1) & ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    return np.clip(0.72 * np.where(grey[..., None], med, img) / 255 + 0.28, 0, 1), tuple(d["ext"])


def narrow(ax, x=0.075, y=0.86, r=0.055):
    """Compass rose north arrow: four main points and four short ones, each split dark and light, N above."""
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, "#222222"), (1, "white")):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec="#222222", lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec="#222222", lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.008, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=12, fontweight="bold", zorder=70, path_effects=HALO)


def scalebar(ax, ext, length=20, x=0.035, y=0.06, fg="#222222"):
    """Line scale bar with ticks, bottom left."""
    km = 111.32 * np.cos(np.radians(LAT)); L = length / km
    x0 = ext[0] + x * (ext[1] - ext[0]); y0 = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.014
    ax.plot([x0, x0 + L], [y0, y0], color=fg, lw=1.3, zorder=60, solid_capstyle="butt", path_effects=[pe.withStroke(linewidth=3.5, foreground="white")])
    for i in range(5):
        xx = x0 + i * L / 4; hh = t if i in (0, 2, 4) else t * 0.55
        ax.plot([xx, xx], [y0, y0 + hh], color=fg, lw=1.1, zorder=60, path_effects=[pe.withStroke(linewidth=3, foreground="white")])
    for v, xx in [(0, x0), (length / 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(xx, y0 + t * 1.5, f"{v:g}", ha="center", va="bottom", fontsize=8.5, zorder=60, path_effects=HALO)
    ax.text(x0 + L + L * 0.07, y0, "km", fontsize=8.5, va="center", zorder=60, path_effects=HALO)


def scale_next(ax, ext, length=20):
    """Put the scale bar at the bottom, just left of the legend or colour box."""
    fig = ax.figure; fig.canvas.draw(); leg = ax.get_legend()
    x1 = leg.get_window_extent().transformed(ax.transAxes.inverted()).x0 if leg else ax._cbx0
    Lf = length / (111.32 * np.cos(np.radians(LAT))) / (ext[1] - ext[0])
    scalebar(ax, ext, length, x=x1 - 0.13 - Lf, y=0.045)


def ticks(ax, ext, step):
    xt = np.arange(np.ceil(ext[0] / step) * step, ext[1], step); yt = np.arange(np.ceil(ext[2] / step) * step, ext[3], step)
    ax.set_xticks(xt); ax.set_yticks(yt); ax.set_xticklabels([f"{x:g}°E" for x in xt]); ax.set_yticklabels([f"{-y:g}°S" for y in yt])
    ax.tick_params(length=2.5, labelsize=8.5, top=True, right=True, labeltop=True, labelright=True)


def legend_br(ax, handles, title, fs=7.5, sp=0.35, left=False):
    leg = ax.legend(handles=handles, title=title, loc="lower left" if left else "lower right", bbox_to_anchor=(0.008, 0.012) if left else (0.992, 0.012), fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor="#222222", facecolor="white", framealpha=0.94, alignment="left",
                    borderpad=0.6, handlelength=1.8, handleheight=1.0, labelspacing=sp)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold")


def colorbar_br(fig, ax, sm, title, tk, w=0.40, h=0.15, ext="neither"):
    ax._cbx0 = 0.992 - w; box = ax.inset_axes([0.992 - w, 0.012, w, h]); box.set_xticks([]); box.set_yticks([]); box.set_zorder(65); box.set_facecolor((1, 1, 1, 0.94))
    for s in box.spines.values(): s.set_color("#222222"); s.set_linewidth(0.6)
    box.text(0.05, 0.84, title, transform=box.transAxes, ha="left", va="top", fontsize=8, fontweight="bold")
    ca = box.inset_axes([0.08, 0.28, 0.84, 0.17]); cb = fig.colorbar(sm, cax=ca, orientation="horizontal", ticks=tk, extend=ext)
    ca.tick_params(labelsize=7.5, length=2); cb.outline.set_linewidth(0.5)


def frame(title, width=7.6):
    h = width * (EX[3] - EX[2]) * ASPECT / (EX[1] - EX[0])
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0, 0, 1, 1])
    img, be = basemap(EX, "rast/basemap_hot3.npz"); ax.imshow(img, extent=be, zorder=0, interpolation="bilinear")
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3]); ax.set_aspect(ASPECT); ticks(ax, EX, 0.25)
    for s in ax.spines.values(): s.set_color("#222222"); s.set_linewidth(0.7)
    ax.text(0.5, 0.965, title, transform=ax.transAxes, ha="center", va="center", fontsize=12.5, fontweight="bold", zorder=70,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])
    narrow(ax)
    ax.text(0.012, 0.012, AUTHOR, transform=ax.transAxes, ha="left", va="bottom", fontsize=7, color="#555555", zorder=70, path_effects=HALO)
    return fig, ax


def marks(ax, fs=7):
    ax.plot(*HPS, marker="s", ms=6, mfc="#111111", mec="white", mew=1.0, zorder=40)
    ax.text(HPS[0] - 0.02, HPS[1] - 0.03, "Hwange Power\nStation", fontsize=fs + 0.5, ha="right", va="top", fontweight="bold", zorder=40, path_effects=HALO)
    for n, x, y, (dx, dy) in TOWNS:
        ax.plot(x, y, "o", ms=3.6, mfc="white", mec="black", mew=0.8, zorder=30)
        ax.text(x + dx, y + dy, n, fontsize=fs, zorder=30, path_effects=HALO)
    world.boundary.plot(ax=ax, color="#8c6d4f", lw=0.9, alpha=0.45, zorder=7)
    dist.boundary.plot(ax=ax, color="#777777", lw=0.5, zorder=6)


def finish(fig, ax, text, name):
    scale_next(ax, EX)
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3])
    ax.text(0, -0.065, text, transform=ax.transAxes, fontsize=6.5, ha="left", va="top", wrap=True)
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig); print("saved", name)


def grid_xy(a):
    return (np.linspace(GEXT[0] + .005, GEXT[1] - .005, a.shape[1]), np.linspace(GEXT[3] - .005, GEXT[2] + .005, a.shape[0]))


def sp(v): return f"{v:,.0f}".replace(",", " ")


SRC = "Source: Sentinel-5P TROPOMI offline L3 (Copernicus, via Google Earth Engine), all overpasses averaged on a 0.01° grid. "


# ---- map 1: study area (flat style, zones) ---------------------------------------------
def map1():
    W = 7.6; fig = plt.figure(figsize=(W, W * (EX[3] - EX[2]) * ASPECT / (EX[1] - EX[0])), dpi=220); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("#e6e6e6"); ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3]); ax.set_aspect(ASPECT); ticks(ax, EX, 0.25)
    ax.grid(color="#cfcfcf", lw=0.3)
    for s_ in ax.spines.values(): s_.set_color("#222222"); s_.set_linewidth(0.7)
    world.plot(ax=ax, fc="#e6e6e6", ec="none", zorder=1); zwe.plot(ax=ax, fc="#f6f3ee", ec="none", zorder=1.2)
    pass
    circle(HPS, 15).plot(ax=ax, fc="#f3b183", ec="#c0504d", lw=1.0, alpha=0.8, zorder=4)
    dist.boundary.plot(ax=ax, color="#8a8a8a", lw=0.6, zorder=5); world.boundary.plot(ax=ax, color="#8c6d4f", lw=0.9, alpha=0.45, zorder=6)
    for n, x, y in (("Hwange Rural District", 26.30, -18.72), ("Hwange Urban", 26.555, -18.255), ):
        ax.text(x, y, n, fontsize=8.5, color="#6b6b6b", style="italic", ha="center", zorder=7, path_effects=HALO)
    for n, x_, y_ in (("ZAMBIA", 26.88, -17.985), ("BOTSWANA", 25.66, -18.8)):
        ax.text(x_, y_, n, fontsize=8, color="#666666", style="italic", ha="center", va="center", zorder=7)
    ax.plot(*HPS, "s", ms=8, mfc="#111111", mec="white", zorder=9)
    ax.text(HPS[0] - 0.03, HPS[1] - 0.025, "Hwange Power Station", ha="right", va="top", fontsize=7.5, fontweight="bold", zorder=9, path_effects=HALO)
    for n, x, y, (dx, dy) in TOWNS:
        ax.plot(x, y, "o", ms=4.2, mfc="white", mec="black", mew=0.9, zorder=8); ax.text(x + dx, y + dy, n, fontsize=7.5, zorder=8, path_effects=HALO)
    ax.text(0.5, 0.965, "Study Area Map", transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", zorder=50, path_effects=HALO)
    narrow(ax)
    ax.text(0.988, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="#555555", zorder=50, path_effects=HALO)
    hs_ = [Line2D([], [], marker="s", ls="none", ms=6.5, mfc="#111111", mec="white", label="Hwange Power Station"),
           Patch(fc="#f3b183", ec="#c0504d", label="15 km round the station"),
           Patch(fc="#f6f3ee", ec="#999999", label="Zimbabwe"),
           Line2D([], [], marker="o", ls="none", ms=4.5, mfc="white", mec="black", label="Town"),
           Line2D([], [], color="#8a8a8a", lw=0.7, label="District boundary"),
           ]
    legend_br(ax, hs_, "Legend", left=True)
    Lf = 20 / (111.32 * np.cos(np.radians(LAT))) / (EX[1] - EX[0]); scalebar(ax, EX, 20, x=0.97 - Lf, y=0.06)
    lc = ax.inset_axes([0.735, 0.70, 0.255, 0.29]); lc.set_facecolor("#dfe9f3"); lc.set_zorder(66)
    world.plot(ax=lc, fc="#f0f0f0", ec="#bbbbbb", lw=0.3)
    world[world.ADMIN.isin(["Zimbabwe", "Zambia"])].plot(ax=lc, fc="#cfcfcf", ec="#888888", lw=0.4)
    lc.add_patch(Rectangle((EX[0], EX[2]), EX[1] - EX[0], EX[3] - EX[2], fc="none", ec="#c00000", lw=1.4, zorder=5))
    lc.plot(*MAA, "^", ms=5, mfc="#4472c4", mec="#222222", mew=0.5, zorder=6)
    lc.text(MAA[0] + 0.5, MAA[1] + 0.3, "Maamba (control)", fontsize=6, ha="left", va="bottom", zorder=6)
    lc.set_xlim(21, 34); lc.set_ylim(-23, -8); lc.set_aspect(ASPECT, adjustable="datalim"); lc.set_xticks([]); lc.set_yticks([])
    for s_ in lc.spines.values(): s_.set_linewidth(0.7); s_.set_color("#222222")
    for n, x_, y_ in (("ZAMBIA", 26.5, -13.0), ("ZIMBABWE", 30.0, -20.2)): lc.text(x_, y_, n, fontsize=6.5, fontweight="bold", ha="center", zorder=6)
    ax.text(0, -0.065, "Source: power station site OpenStreetMap; Maamba site Global Energy Monitor; boundaries OCHA COD-AB 2023 and Natural Earth. "
            "The red box in the inset is the study area. WGS 84.", transform=ax.transAxes, fontsize=6.5, ha="left", va="top", wrap=True)
    fig.savefig("out/map1_study_area.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig); print("saved map1")


# ---- map 2: NO2 after Units 7 and 8 (continuous, translucent over OSM) ----------------------
def map2():
    fig, ax = frame("Nitrogen Dioxide Column Map (2024 to 2025)")
    a = ndimage.gaussian_filter(rd("no2_post"), 1.0); norm = mpl.colors.Normalize(10, 50); cmap = plt.get_cmap("YlOrRd")
    ax.imshow(a, extent=GEXT, cmap=cmap, norm=norm, alpha=0.72, zorder=2, interpolation="bilinear")
    marks(ax)
    colorbar_br(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap), "Tropospheric NO$_2$ (µmol/m²)", [10, 20, 30, 40, 50], ext="both")
    finish(fig, ax, SRC + f"Mean of January 2024 to December 2025, after Units 7 and 8 entered service. Background ring mean {S['no2']['bg']['post']:.1f} µmol/m². "
           "Light smoothing (σ = 1 cell). " + OSM + " WGS 84.", "map2_no2_post")


# ---- map 3: NO2 change (classed, diverging, cells) ----------------------------------------
def map3():
    fig, ax = frame("Change in Nitrogen Dioxide Map (2019–2022 to 2024–2025)")
    d = rd("no2_post") - rd("no2_pre") - (S["no2"]["bg"]["post"] - S["no2"]["bg"]["pre"])
    bounds = [-30, -2, 0, 2, 5, 10, 15, 20, 60]; cols = ["#4f8fc0", "#c6dbef", "#fff5eb", "#fdd0a2", "#fdae6b", "#f16913", "#c4410a", "#7f2704"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bounds, cmap.N)
    ax.imshow(d, extent=GEXT, cmap=cmap, norm=norm, alpha=0.85, zorder=2, interpolation="nearest")
    marks(ax)
    lab = ["< −2", "−2 – 0", "0 – 2", "2 – 5", "5 – 10", "10 – 15", "15 – 20", "> 20"]
    legend_br(ax, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(cols, lab)][::-1], "NO$_2$ change (µmol/m²)")
    finish(fig, ax, SRC + "Mean of 2024 to 2025 minus mean of 2019 to 2022 in each 0.01° cell, less the change in the background ring "
           f"({S['no2']['bg']['post'] - S['no2']['bg']['pre']:+.1f} µmol/m²) so that regional drift is removed. " + OSM + " WGS 84.", "map3_no2_change")


# ---- map 4: SO2 (filled contours) ---------------------------------------------------------
def map4():
    fig, ax = frame("Sulphur Dioxide Column Map (2024 to 2025)")
    au = [t for t in ax.texts if t.get_text() == AUTHOR][0]; au.set_position((0.988, 0.985)); au.set_ha("right"); au.set_va("top")
    a = ndimage.gaussian_filter(rd("so2_post"), 2.5); xs, ys = grid_xy(a)
    lv = [-1000, 50, 75, 100, 125, 150, 200, 1000]; cols = ["#ffffff00", "#e5e0f0", "#c3b5da", "#9d85c0", "#7a57a6", "#59308d", "#3a0f6e"]
    ax.contourf(xs, ys, a, levels=lv, colors=cols, alpha=0.8, zorder=2)
    ax.contour(xs, ys, a, levels=lv[1:-1], colors="#3a0f6e", linewidths=0.35, zorder=2.1)
    marks(ax)
    lab = ["< 50", "50 – 75", "75 – 100", "100 – 125", "125 – 150", "150 – 200", "> 200"]
    legend_br(ax, [Patch(fc=c if i else "white", ec="#555555", lw=0.4, label=l) for i, (c, l) in enumerate(zip(cols, lab))][::-1], "SO$_2$ column (µmol/m²)")
    finish(fig, ax, SRC + "SO$_2$ total column, mean of 2024 to 2025, smoothed (σ = 2.5 cells) because single SO$_2$ retrievals are noisy. "
           f"Background ring mean {S['so2']['bg']['post']:.1f} µmol/m². " + OSM + " WGS 84.", "map4_so2_post")


# ---- map 5: people inside the enhanced zone (dot map) ----------------------------------------
def map5():
    global EX
    EX = (25.85, 27.15, -18.79, -18.12)
    fig, ax = frame("Population Exposure Map (2024 to 2025)")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fc="white", ec="none", alpha=0.45, zorder=0.5))
    a = rd("no2_post"); bg = S["no2"]["bg"]["post"]; pop = rd("wpc2020"); xs, ys = grid_xy(a)
    X, Y = np.meshgrid(xs, ys)
    ax.contourf(xs, ys, a, levels=[bg * 1.5, bg * 2, 1e3], colors=["#fde0c5", "#f6a77a"], alpha=0.75, zorder=2)
    ax.contour(xs, ys, a, levels=[bg * 1.5, bg * 2], colors=["#d9824d", "#b23c17"], linewidths=[0.8, 1.1], zorder=2.1)
    k = pop >= 20; cls = np.where(a > 2 * bg, 2, np.where(a > 1.5 * bg, 1, 0))[k]
    cc = np.array(["#9a9a9a", "#e46c0a", "#7f1d06"])[cls]
    ax.scatter(X[k], Y[k], s=np.clip(pop[k] / 35, 1.2, 55), c=cc, ec="white", lw=0.3, zorder=20)
    marks(ax)
    e = S["exposure"]["post"]
    hi, mid = bg * 2, bg * 1.5
    hs_ = [Patch(fc="#f6a77a", ec="#b23c17", label=f"> {hi:.0f}"), Patch(fc="#fde0c5", ec="#d9824d", label=f"{mid:.0f} – {hi:.0f}"),
           Line2D([], [], marker="o", ls="none", ms=5.5, mfc="#7f1d06", mec="white", label=f"People (NO$_2$ > {hi:.0f})"),
           Line2D([], [], marker="o", ls="none", ms=5.5, mfc="#e46c0a", mec="white", label=f"People (NO$_2$ {mid:.0f} – {hi:.0f})"),
           Line2D([], [], marker="o", ls="none", ms=5.5, mfc="#9a9a9a", mec="white", label=f"People (NO$_2$ ≤ {mid:.0f})")]
    legend_br(ax, hs_, "NO$_2$ column (µmol/m²)")
    t = (f"Source: Sentinel-5P NO$_2$ mean of 2024 to 2025; high is 1.5 to 2 times and very high more than 2 times the background mean ({bg:.1f} µmol/m²); "
         f"WorldPop 2020 constrained population (Zimbabwe only) summed to 0.01° cells, dot area proportional to people, cells under 20 people not drawn. "
         + sp(e['x2']) + " people in the very high area and " + sp(e['x1.5']) + " in the high and very high areas together. ")
    finish(fig, ax, t + OSM + " WGS 84.", "map5_exposure")


if __name__ == "__main__":
    import sys
    for n in (sys.argv[1:] or ["1", "2", "3", "4", "5"]): globals()[f"map{n}"]()
