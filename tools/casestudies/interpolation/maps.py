"""Maps and graphs for the rainfall interpolation comparison (1961-1990 station normals). Surfaces are on a 0.025 degree
grid (interp.py); maps are drawn in geographic coordinates, WGS 84. Output: out/*.png"""
import os, sys, json
import numpy as np, pandas as pd, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LightSource, ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; FG = "#222222"
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
EXT = (23.0, 35.3, -23.6, -14.55); ASPECT = 1 / np.cos(np.radians(19))
R = json.load(open("data/interp.json")); CK = json.load(open("data/check.json"))
P = pd.read_csv("data/points.csv"); L = pd.read_csv("data/loocv.csv"); V = pd.read_csv("data/vario.csv")
G = np.load("data/surfaces.npz"); MK = G["mask"]; RES = float(G["res"])
REXT = (float(G["x0"]), float(G["x0"]) + MK.shape[1] * RES, float(G["y1"]) - MK.shape[0] * RES, float(G["y1"]))
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
africa = gpd.read_file(f"zip://{NE}").cx[5:60, -40:10]; world = africa.cx[20:38, -26:-12]
lakes = gpd.read_file("zip://../../corridors/raw/ne_10m_lakes.zip").cx[22.5:36, -24:-14.5]
zwe = gpd.read_file("../population/raw/bnd/zwe_admin0.shp").to_crs(4326)
prov = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(4326)
SADC = ["AGO", "BWA", "COM", "COD", "SWZ", "LSO", "MDG", "MWI", "MUS", "MOZ", "NAM", "SYC", "ZAF", "TZA", "ZMB", "ZWE"]
CITIES = [("Harare", 31.052, -17.829), ("Bulawayo", 28.583, -20.150), ("Mutare", 32.670, -18.970), ("Gweru", 29.817, -19.450),
          ("Masvingo", 30.833, -20.074), ("Hwange", 26.500, -18.364), ("Beitbridge", 30.000, -22.217), ("Kariba", 28.800, -16.517)]
COUNTRIES = [("ZAMBIA", 26.9, -16.0), ("MOZAMBIQUE", 34.2, -17.6), ("BOTSWANA", 25.6, -21.7), ("SOUTH AFRICA", 29.4, -23.2)]
NAMES = {"idw": "Inverse Distance Weighting", "ok": "Ordinary Kriging", "uk": "Universal Kriging", "tps": "Thin-Plate Spline"}
SRC_ST = "Source: GHCN-Monthly v2 station precipitation (NOAA NCEI), 1961–1990 means; boundaries OCHA COD-AB; Natural Earth. Geographic coordinates, WGS 84."


def axes_setup(ax, fs=9, face="#ffffff"):
    ax.set_facecolor(face); ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(ASPECT)
    xs = [26, 28, 30, 32]; ys = [-22, -20, -18, -16]
    ax.set_xticks(xs); ax.set_yticks(ys)
    ax.set_xticklabels([f"{x:g}°E" for x in xs], fontsize=fs); ax.set_yticklabels([f"{-y:g}°S" for y in ys], fontsize=fs, rotation=90, va="center")
    ax.tick_params(length=2, top=True, right=True, labeltop=True, labelright=True)
    for t in ax.get_yticklabels(): t.set_rotation(90); t.set_va("center")
    for sp in ax.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)


def north(ax, ty=0.95, size=1.0):
    yt = EXT[2] + ty * (EXT[3] - EXT[2]); x = EXT[0] + 0.32
    ax.annotate("", xy=(x, yt), xytext=(x, yt - 0.5 * size), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=FG, lw=1.2), zorder=70)
    ax.text(x, yt - 0.55 * size, "N", ha="center", va="top", fontsize=10 * size, fontweight="bold", zorder=70)


def header(fig, ax, title, fs=14):
    """Title printed on the map itself, top centre, with a white halo; no separate title strip."""
    ax.text(0.5, 0.975, title, transform=ax.transAxes, ha="center", va="top", fontsize=fs, fontweight="bold", color=FG, zorder=95,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])


def frame(title, size=(11.4, 8.6)):
    fig = plt.figure(figsize=size, dpi=200); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.06, 0.08, 0.92, 0.9]); axes_setup(ax)
    header(fig, ax, title); north(ax)
    return fig, ax


def legend_in(ax, handles, title, fs=9.5, ncol=1, **kw):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=(0.993, 0.05), fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=FG, facecolor="white", framealpha=1, borderpad=0.7, alignment="left", ncol=ncol,
                    handlelength=2.0, handleheight=1.1, labelspacing=0.55, columnspacing=1.2, **kw)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.set_zorder(90)
    ax.text(0.993, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=90)
    return leg


def scalebar(ax, L_km=200, fs=7.5, y=None, x0=None):
    km = 111.32 * np.cos(np.radians(19)); L = L_km / km
    y = EXT[2] + 0.2 if y is None else y; x0 = EXT[0] + 0.25 if x0 is None else x0
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y), L / 4, 0.07, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=70))
    for v, x in [(0, x0), (L_km // 2, x0 + L / 2), (L_km, x0 + L)]:
        ax.text(x, y + 0.11, f"{v}", ha="center", va="bottom", fontsize=fs, zorder=70)
    ax.text(x0 + L + 0.08, y + 0.035, "km", fontsize=fs, va="center", zorder=70)


def source(ax, text, y=-0.06):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.5, ha="left", va="top")


def save(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def base(ax, fc="#ececec", towns=True, labels=True, prov_lw=0.45, fs=7.5):
    world.plot(ax=ax, fc=fc, ec="white", lw=0.6, zorder=1)
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=6)
    prov.boundary.plot(ax=ax, color="#555555", lw=prov_lw, zorder=7)
    zwe.boundary.plot(ax=ax, color="#111111", lw=1.0, zorder=8)
    if labels:
        for n, x, y in COUNTRIES: ax.text(x, y, n, fontsize=fs, color="#666666", style="italic", ha="center", zorder=9)
    if towns:
        for n, x, y in CITIES:
            ax.plot(x, y, "s", ms=4, mfc="white", mec="black", mew=0.8, zorder=30)
            ax.text(x + 0.09, y + 0.07, n, fontsize=fs + 0.5, zorder=30, path_effects=HALO)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])


def surface(ax, a, colors, bins, z=2):
    ax.imshow(np.ma.masked_invalid(a), extent=REXT, cmap=ListedColormap(colors), norm=BoundaryNorm(bins, len(colors)), zorder=z, interpolation="nearest")


def hillshade():
    with rasterio.open("../population/rast/dem.tif") as s:
        z = s.read(1).astype(float); b = s.bounds
    dx = (b.right - b.left) / z.shape[1] * 111320 * np.cos(np.radians(19)); dy = (b.top - b.bottom) / z.shape[0] * 111320
    hs = LightSource(azdeg=315, altdeg=40).hillshade(z, vert_exag=6, dx=dx, dy=dy)
    ext = (b.left, b.right, b.bottom, b.top)
    inside = geometry_mask(zwe.geometry, z.shape, from_bounds(b.left, b.bottom, b.right, b.top, z.shape[1], z.shape[0]), invert=True)
    return z, hs, ext, inside


def locator(ax, box=(0.845, 0.735, 0.145, 0.255)):
    la = ax.inset_axes(list(box)); la.set_zorder(85); la.set_facecolor("white")
    africa.plot(ax=la, fc="#f0f0f0", ec="white", lw=0.3)
    africa[africa.ADM0_A3.isin(SADC)].plot(ax=la, fc="#cfcfcf", ec="white", lw=0.3)
    africa[africa.ADM0_A3 == "ZWE"].plot(ax=la, fc="#8c2d04", ec="none")
    la.set_xlim(9, 52); la.set_ylim(-36, 6); la.set_aspect(1 / np.cos(np.radians(15)), adjustable="datalim"); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(FG); sp.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.87), 1, 0.13, transform=la.transAxes, fc="white", ec=FG, lw=0.6, zorder=5))
    la.text(0.5, 0.935, "SADC", transform=la.transAxes, ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=6)


ELEV = [(0, 600, "#6a9a58", "< 600"), (600, 900, "#b5c77a", "600 – 900"), (900, 1200, "#e9dc9b", "900 – 1 200"),
        (1200, 1500, "#d1a46a", "1 200 – 1 500"), (1500, 9999, "#9c6a43", "≥ 1 500")]


# 1 Study area: elevation with the rain gauges
def map1():
    z, hs, ext, inside = hillshade()
    fig, ax = frame("Study Area Map"); base(ax, towns=False)
    rgba = np.zeros(z.shape + (4,))
    for lo, hi, c, _ in ELEV:
        m = (z >= lo) & (z < hi) & inside; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    rgba[..., :3] *= (0.6 + 0.4 * hs)[..., None]
    ax.imshow(rgba, extent=ext, zorder=2, interpolation="bilinear")
    ax.plot(P.lon, P.lat, "^", ms=5.5, mfc="#1f4e9c", mec="white", mew=0.6, ls="none", zorder=25)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3])
    locator(ax)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in ELEV]
    h += [Line2D([], [], marker="^", ls="none", ms=6.5, mfc="#1f4e9c", mec="white", label="Rain gauges"),
          Line2D([], [], color="#555555", lw=0.6, label="Province boundaries")]
    legend_in(ax, h, "Elevation (m)"); scalebar(ax)
    source(ax, "Source: Copernicus DEM GLO-30 (500 m); rain gauges GHCN-Monthly v2 (NOAA NCEI); boundaries OCHA COD-AB; Natural Earth. WGS 84.")
    save(fig, "map1_study_area")


RAIN = [("#c8553d", "< 450"), ("#f2b45a", "450 – 650"), ("#f6edb0", "650 – 800"), ("#7fbf8e", "800 – 1 000"), ("#2a7a8c", "≥ 1 000")]
RB = [0, 450, 650, 800, 1000, 5000]


# 2 Four surfaces in the same classes
def map2():
    fig = plt.figure(figsize=(13.2, 11.2), dpi=200)
    pw, ph = 0.455, 0.43; X = [0.04, 0.525]; Y = [0.525, 0.07]
    for i, k in enumerate(("idw", "ok", "uk", "tps")):
        r, c = divmod(i, 2)
        ax = fig.add_axes([X[c], Y[r], pw, ph]); axes_setup(ax, fs=7.5)
        base(ax, towns=False, labels=False, prov_lw=0.35)
        surface(ax, G[k], [c_ for c_, _ in RAIN], RB)
        ax.plot(P.lon, P.lat, ".", ms=2.2, color="#111111", zorder=25)
        header(fig, ax, f"({'abcd'[i]}) {NAMES[k]}", fs=11.5)
        yt = EXT[2] + 0.93 * (EXT[3] - EXT[2]); x = EXT[0] + 0.3
        ax.annotate("", xy=(x, yt), xytext=(x, yt - 0.42), arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.5", color=FG, lw=1), zorder=70)
        ax.text(x, yt - 0.46, "N", ha="center", va="top", fontsize=8, fontweight="bold", zorder=70)
        scalebar(ax, fs=6.5)
        cv = R["cv"][k]; s = R["surface"][k]
        ax.text(0.985, 0.03, f"Mean {s['mean']:,.0f} mm\nRMSE {cv['rmse']:.0f} mm".replace(",", " "), transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8, zorder=80, bbox=dict(fc="white", ec=FG, lw=0.5, pad=3))
    fig.text(0.51, 0.975, "Mean Annual Rainfall by Interpolation Method, 1961–1990", ha="center", va="center", fontsize=13, fontweight="bold")
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for c, l in RAIN] + [Line2D([], [], marker=".", ls="none", ms=6, color="#111111", label="Rain gauges")]
    fig.legend(handles=h, title="Rainfall (mm per year)", loc="lower center", bbox_to_anchor=(0.51, 0.0), ncol=6, fontsize=9.5, title_fontsize=10,
               frameon=True, fancybox=False, edgecolor=FG).get_title().set_fontweight("bold")
    fig.text(0.98, 0.005, AUTHOR, ha="right", va="bottom", fontsize=7.5, color="#555555")
    save(fig, "map2_surfaces")


# 3 Leave-one-out errors of ordinary kriging at each gauge
def map3():
    fig, ax = frame("Cross-Validation Error Map"); base(ax, fc="#f2f2f2")
    zwe.plot(ax=ax, fc="#fafafa", ec="none", zorder=2)
    e = (L.ok - L.obs).values
    bins = [-1e9, -150, -50, 50, 150, 1e9]
    cols = ["#b2182b", "#ef8a62", "#e0e0e0", "#67a9cf", "#2166ac"]
    labs = ["< -150", "-150 – -50", "-50 – 50", "50 – 150", "≥ 150"]
    k = np.digitize(e, bins[1:-1]); size = 18 + 0.55 * np.minimum(np.abs(e), 400)
    ax.scatter(P.lon, P.lat, s=size, c=[cols[i] for i in k], ec="#333333", lw=0.5, zorder=25)
    out = R["outlier"]; i = int(L.obs.idxmax())
    ax.annotate(f"{out['name']}\nobserved {out['obs']:,.0f} mm\nestimated {out['ok']:,.0f} mm".replace(",", " "), (P.lon[i], P.lat[i]),
                xytext=(P.lon[i] + 0.7, P.lat[i] + 0.55), fontsize=8, arrowprops=dict(arrowstyle="-", color=FG, lw=0.7), zorder=40, path_effects=HALO)
    h = [Line2D([], [], marker="o", ls="none", ms=8, mfc=c, mec="#333333", label=l) for c, l in zip(cols, labs)]
    legend_in(ax, h, "Estimation error (mm)"); scalebar(ax)
    source(ax, "Ordinary kriging, each gauge left out in turn and estimated from the other 64. Symbol size grows with the error. " + SRC_ST.replace("Source: ", "Source: ").split("; boundaries")[0] + ".")
    save(fig, "map3_cv_errors")


# 4 Agreement between the four methods
def map4():
    fig, ax = frame("Method Agreement Map"); base(ax)
    cols = ["#e9f1e4", "#f3c77b", "#b5402c"]
    surface(ax, G["spread"], cols, [0, 50, 100, 5000])
    ax.plot(P.lon, P.lat, ".", ms=3, color="#111111", zorder=25)
    s = R["spread"]
    h = [Patch(fc=cols[0], ec="#777777", lw=0.3, label="< 50"),
         Patch(fc=cols[1], ec="#777777", lw=0.3, label="50 – 100"),
         Patch(fc=cols[2], ec="#777777", lw=0.3, label="≥ 100"),
         Line2D([], [], marker=".", ls="none", ms=6, color="#111111", label="Rain gauges")]
    legend_in(ax, h, "Spread of estimates (mm)"); scalebar(ax)
    source(ax, "Highest minus lowest of the four surfaces in each 0.025° cell. " + SRC_ST)
    save(fig, "map4_agreement")


# 5 Universal kriging standard error
def map5():
    fig, ax = frame("Estimation Uncertainty Map"); base(ax)
    se = G["uk_se"]; cols = ["#eef3f8", "#9ebcda", "#4d6fa8"]; bins = [0, 75, 100, 5000]
    surface(ax, se, cols, bins)
    ax.plot(P.lon, P.lat, ".", ms=3, color="#111111", zorder=25)
    v = se[MK]; area = np.cos(np.radians(np.meshgrid(np.zeros(MK.shape[1]), REXT[3] - (np.arange(MK.shape[0]) + 0.5) * RES)[1]))[MK]
    pct = [100 * area[(v >= a) & (v < b)].sum() / area.sum() for a, b in zip(bins[:-1], bins[1:])]
    labs = ["< 75", "75 – 100", "≥ 100"]
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for c, l in zip(cols, labs)]
    h += [Line2D([], [], marker=".", ls="none", ms=6, color="#111111", label="Rain gauges")]
    legend_in(ax, h, "Standard error (mm)"); scalebar(ax)
    source(ax, "Universal kriging with a linear trend; spherical model fitted to the trend residuals. " + SRC_ST)
    json.dump(dict(se_classes_pct=[round(p, 1) for p in pct]), open("data/map5.json", "w"))
    save(fig, "map5_uncertainty")


def chart(title, ylab, xlab=None, size=(7.2, 4.4)):
    fig, ax = plt.subplots(figsize=size, dpi=200)
    ax.text(0.5, 1.05, title, transform=ax.transAxes, ha="center", fontsize=12.5, fontweight="bold")
    ax.set_ylabel(ylab, fontsize=10.5); ax.tick_params(labelsize=10)
    if xlab: ax.set_xlabel(xlab, fontsize=10.5)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
    return fig, ax


def done(fig, ax, name, y=-0.18):
    ax.text(1, y, AUTHOR, transform=ax.transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig(f"out/{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved", name)


SPH = lambda h, c0, c, a: np.where(h < a, c0 + c * (1.5 * h / a - 0.5 * (h / a) ** 3), c0 + c)
EXPM = lambda h, c0, c, a: c0 + c * (1 - np.exp(-3 * h / a))


# Figure 1: semivariograms, raw values and trend residuals
def fig1():
    fig, ax = chart("Semivariograms of Mean Annual Rainfall", "Semivariance (thousand mm²)", "Distance between gauges (km)", size=(8.0, 4.6))
    hh = np.linspace(0, 400, 200)
    b = R["tuning"]["best"]; fo = R["vario"]["ok"][b["ok"]]; fu = R["vario"]["uk"][b["uk"]]
    f_ok = SPH if b["ok"] == "Spherical" else EXPM; f_uk = SPH if b["uk"] == "Spherical" else EXPM
    ax.plot(V.ok_lag_km, V.ok_gamma / 1e3, "o", ms=5, color="#8c2d04", label="Rainfall values")
    ax.plot(hh, f_ok(hh, fo["nugget"], fo["psill"], fo["range_km"]) / 1e3, color="#8c2d04", lw=1.6, label=f"{b['ok']} model, ordinary kriging")
    ax.plot(V.uk_lag_km, V.uk_gamma / 1e3, "s", ms=5, color="#2a7a8c", label="Residuals from the linear trend")
    ax.plot(hh, f_uk(hh, fu["nugget"], fu["psill"], fu["range_km"]) / 1e3, color="#2a7a8c", lw=1.6, ls="--", label=f"{b['uk']} model, universal kriging")
    ax.set_xlim(0, 400); ax.set_ylim(0, 50); ax.legend(fontsize=9, frameon=False, loc="upper left")
    done(fig, ax, "fig1_semivariogram")


# Figure 2: cross-validation errors by method
def fig2():
    k = ["idw", "ok", "uk", "tps"]; lab = ["IDW", "Ordinary\nkriging", "Universal\nkriging", "Thin-plate\nspline"]
    fig, ax = chart("Leave-One-Out Errors by Method", "Error (mm per year)", size=(7.6, 4.4))
    x = np.arange(4); w = 0.34
    for j, (m, c, n) in enumerate((("mae", "#f2b45a", "Mean absolute error"), ("rmse", "#2a7a8c", "Root mean square error"))):
        v = [R["cv"][q][m] for q in k]
        ax.bar(x + (j - 0.5) * w, v, w, color=c, label=n)
        for i, y in enumerate(v): ax.text(x[i] + (j - 0.5) * w, y + 2, f"{y:.0f}", ha="center", fontsize=9.5)
    ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylim(0, 150); ax.legend(fontsize=9, frameon=False, loc="upper left", ncol=2)
    done(fig, ax, "fig2_cv_errors", y=-0.22)


# Figure 3: observed against estimated, four methods
def fig3():
    fig, axs = plt.subplots(1, 4, figsize=(12.4, 3.6), dpi=200, sharey=True)
    for ax, k in zip(axs, ("idw", "ok", "uk", "tps")):
        ax.plot([300, 1700], [300, 1700], color="#999999", lw=0.8)
        ax.plot(L.obs, L[k], "o", ms=3.5, mfc="#2a7a8c", mec="white", mew=0.4)
        ax.set_xlim(300, 1700); ax.set_ylim(300, 1700); ax.set_aspect(1)
        ax.set_title(NAMES[k], fontsize=10.5, fontweight="bold"); ax.tick_params(labelsize=8.5)
        ax.text(0.04, 0.96, f"r = {R['cv'][k]['r']:.2f}\nRMSE {R['cv'][k]['rmse']:.0f} mm", transform=ax.transAxes, va="top", fontsize=8.5)
        ax.set_xlabel("Observed (mm)", fontsize=9)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    axs[0].set_ylabel("Estimated (mm)", fontsize=9)
    fig.suptitle("Observed and Estimated Rainfall at Each Gauge", fontsize=12.5, fontweight="bold", y=0.93)
    axs[-1].text(1, -0.3, AUTHOR, transform=axs[-1].transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig("out/fig3_observed_estimated.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved fig3")


# Figure 4: rainfall against elevation
def fig4():
    fig, ax = chart("Mean Annual Rainfall and Gauge Elevation", "Rainfall (mm per year)", "Elevation (m)", size=(7.2, 4.4))
    ax.plot(P.elev, P.p, "o", ms=5, mfc="#8c2d04", mec="white", mew=0.5)
    b = np.polyfit(P.elev, P.p, 1); xx = np.array([P.elev.min(), P.elev.max()])
    ax.plot(xx, np.polyval(b, xx), color=FG, lw=1.2)
    ax.text(0.03, 0.95, f"r = {R['stations']['r_elev']:.2f}; about {b[0] * 100:.0f} mm more for every 100 m", transform=ax.transAxes, va="top", fontsize=9.5)
    json.dump(dict(slope_per_100m=round(b[0] * 100, 1)), open("data/fig4.json", "w"))
    ax.set_ylim(0, 1800); done(fig, ax, "fig4_elevation")


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "fig1", "fig2", "fig3", "fig4"]): globals()[n]()
