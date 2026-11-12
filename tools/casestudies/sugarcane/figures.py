"""Figures for the sugarcane case study: three maps (no study-area map, by design) and three Excel-style charts.
Maps are on the 20 m UTM 36S grid of the stacks, background is the 7-year mean NDVI in grey."""
import os, json
import numpy as np, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Polygon
from matplotlib.lines import Line2D
from pyproj import Transformer

mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
AUTHOR = "© Kudzanai Chakavarika"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
BLUE, ORANGE, GREY, GREEN = "#4472C4", "#ED7D31", "#A5A5A5", "#70AD47"
YEARS = list(range(2019, 2026))
ST = json.load(open("out/stats.json")); RAIN = json.load(open("data/rain_monthly.json"))
seg = np.load("out/seg.npy"); H, W = seg.shape
G = gpd.read_file("out/fields.gpkg")
X0, Y0, RES = 326320.0, 7685140.0, 20.0
EXT = (X0, X0 + W * RES, Y0 - H * RES, Y0)
FROM = Transformer.from_crs(32736, 4326, always_xy=True); TO = Transformer.from_crs(4326, 32736, always_xy=True)
sp = lambda v: f"{v:,.0f}".replace(",", " ")

if not os.path.exists("out/bg.npy"):
    a = np.load("rast/ndvi_stack.npz")["a"]
    np.save("out/bg.npy", np.nanmean(a.astype("float32"), 0).astype("float32")); del a
BG = np.load("out/bg.npy"); BG[~np.isfinite(BG)] = np.nanmedian(BG)  # a few edge pixels have no clear month

# per-field values painted back onto the grid (field id k is G row with fid k)
fid = G["fid"].to_numpy() if "fid" in G else np.arange(1, len(G) + 1)
def paint(vals):
    lut = np.full(seg.max() + 1, np.nan, "float32"); lut[fid] = vals; return lut[seg]


# ---------------- map helpers ----------------
# Layout: title above the frame, map in the frame, and a framed panel under the map holding the legend,
# scale bar, compass rose, source and author, so nothing sits on the fields.
WD, MX, MW = 10.0, 0.07, 0.86              # figure width (in), map left and width (fractions)
T_H, GAP, P_H, PAD = 0.5, 0.38, 1.2, 0.08  # title band, gap for tick labels, panel height, bottom pad (in)


def ticks(ax, ext, sx=0.1, sy=0.05):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0, _ = FROM.transform(ext[0], ym); lo1, _ = FROM.transform(ext[1], ym); _, la0 = FROM.transform(xm, ext[2]); _, la1 = FROM.transform(xm, ext[3])
    lons = np.arange(np.ceil(lo0 / sx) * sx, lo1, sx); lats = np.arange(np.ceil(la0 / sy) * sy, la1, sy)
    ax.set_xticks([TO.transform(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.2f}°E" for l in lons])
    ax.set_yticks([TO.transform(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.2f}°S" for l in lats])
    ax.tick_params(length=2.5, labelsize=7.5, top=True, right=True, labeltop=False, labelright=False)


def narrow(ax, x, y, r):
    fig = ax.figure; fig.canvas.draw(); bb = ax.get_window_extent(); k = bb.height / bb.width
    for ang, rr in [(a_, r) for a_ in (0, 90, 180, 270)] + [(a_, r * 0.5) for a_ in (45, 135, 225, 315)]:
        t = np.radians(ang); tip = (x + rr * np.sin(t) * k, y + rr * np.cos(t)); w = rr * 0.2
        for side, fc in ((-1, "#222222"), (1, "white")):
            sa = t + side * np.radians(45); sv = (x + w * np.sin(sa) * k, y + w * np.cos(sa))
            ax.add_patch(Polygon([(x, y), tip, sv], closed=True, fc=fc, ec="#222222", lw=0.7, transform=ax.transAxes, zorder=70 if rr == r else 69))
    ax.add_patch(mpl.patches.Ellipse((x, y), 2 * r * 0.62 * k, 2 * r * 0.62, fc="none", ec="#222222", lw=0.7, transform=ax.transAxes, zorder=68))
    ax.text(x, y + r + 0.02, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=11, fontweight="bold", zorder=70)


def scalebar(axp, ext, km, x0=0.56, y=0.42):
    # the panel has the same width as the map, so a map distance is the same fraction of the panel width
    L = km * 1000 / (ext[1] - ext[0]); t = 0.10
    axp.plot([x0, x0 + L], [y, y], color="#222222", lw=1.3, solid_capstyle="butt", transform=axp.transAxes)
    for i in range(5):
        xx = x0 + i * L / 4; axp.plot([xx, xx], [y, y + (t if i in (0, 2, 4) else t * 0.55)], color="#222222", lw=1.1, transform=axp.transAxes)
    for v, xx in [(0, x0), (km / 2, x0 + L / 2), (km, x0 + L)]:
        axp.text(xx, y + t * 1.4, f"{v:g}", ha="center", va="bottom", fontsize=8.5, transform=axp.transAxes)
    axp.text(x0 + L + 0.012, y, "km", fontsize=8.5, va="center", transform=axp.transAxes)


def frame(title, ext=EXT):
    mh = WD * MW * (ext[3] - ext[2]) / (ext[1] - ext[0]); hh = T_H + mh + GAP + P_H + PAD
    fig = plt.figure(figsize=(WD, hh), dpi=200)
    ax = fig.add_axes([MX, (PAD + P_H + GAP) / hh, MW, mh / hh])
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1); ticks(ax, ext)
    for s_ in ax.spines.values(): s_.set_visible(True); s_.set_color("#222222"); s_.set_linewidth(0.7)
    ax.imshow(np.clip(BG, 0.1, 0.85), cmap="Greys_r", vmin=-0.4, vmax=1.3, extent=EXT, interpolation="nearest", zorder=1)
    fig.text(0.5, (hh - T_H / 2) / hh, title, ha="center", va="center", fontsize=13, fontweight="bold")
    axp = fig.add_axes([MX, PAD / hh, MW, P_H / hh]); axp.set_xticks([]); axp.set_yticks([])
    for s_ in axp.spines.values(): s_.set_visible(True); s_.set_color("#222222"); s_.set_linewidth(0.7)
    narrow(axp, 0.93, 0.47, 0.27)
    axp.text(0.995, 0.04, AUTHOR, transform=axp.transAxes, ha="right", va="bottom", fontsize=7, color="#444444")
    axp.text(0.008, 0.05, "Data: Copernicus Sentinel-2 L2A, monthly medians at 20 m. UTM zone 36S.", transform=axp.transAxes,
             ha="left", va="bottom", fontsize=7, color="#444444")
    return fig, ax, axp


def legend_p(axp, handles, title, ncol=3):
    leg = axp.legend(handles=handles, title=title, loc="upper left", bbox_to_anchor=(0.008, 0.97), ncol=ncol, fontsize=8.5,
                     title_fontsize=9, frameon=False, alignment="left", handlelength=2.0, handleheight=1.2,
                     labelspacing=0.55, columnspacing=1.4, borderaxespad=0.3)
    leg.get_title().set_fontweight("bold")


def finish(fig, ax, axp, name, ext=EXT, km=10):
    scalebar(axp, ext, km); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15); plt.close(fig); print("saved", name)


def classes(ax, grid, bounds, cols):
    cm = ListedColormap(cols); nm = BoundaryNorm(bounds, cm.N)
    ax.imshow(np.ma.masked_invalid(grid), cmap=cm, norm=nm, extent=EXT, interpolation="nearest", zorder=5)


def outlines(ax, lw=0.25, col="#333333"):
    G.boundary.plot(ax=ax, lw=lw, color=col, zorder=6)


EDGE = Line2D([], [], color="#333333", lw=0.8, label="Field boundary")
OTHER = Patch(fc="#b5b5b5", ec="#555555", lw=0.4, label="Other land (grey shade = mean NDVI)")

# ---------------- map 1: cane fields ----------------
fig, ax, axp = frame("Sugarcane Fields Map (2019–2025)")
ax.imshow(np.ma.masked_equal(seg > 0, 0), cmap=ListedColormap(["#2E7D32"]), extent=EXT, interpolation="nearest", zorder=5)
legend_p(axp, [Patch(fc="#2E7D32", ec="#555555", lw=0.4, label="Sugarcane field (≥ 5 ha)"), OTHER], "Land class", ncol=1)
finish(fig, ax, axp, "map1_fields")

# ---------------- map 2: field vigour ----------------
B2 = [0, 0.76, 0.78, 0.80, 0.82, 1]; C2 = ["#d7301f", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"]
L2 = ["< 0.76", "0.76 – 0.78", "0.78 – 0.80", "0.80 – 0.82", "> 0.82"]
fig, ax, axp = frame("Mean Peak NDVI By Field Map (2019–2025)")
classes(ax, paint(G["pk_mean"].to_numpy()), B2, C2); outlines(ax, 0.15)
legend_p(axp, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(C2, L2)], "Mean peak NDVI per field (unitless)", ncol=3)
finish(fig, ax, axp, "map2_vigour")

# ---------------- map 3: fields repeatedly in the bottom tenth ----------------
B4 = [-0.5, 0.5, 2.5, 4.5, 7.5]; C4 = ["#e8e8e8", "#fdd49e", "#fc8d59", "#b30000"]
L4 = ["0", "1 – 2", "3 – 4", "≥ 5"]
wn = G["weak_n"].to_numpy()
fig, ax, axp = frame("Persistently Weak Fields Map (2019–2025)")
classes(ax, paint(wn.astype("float32")), B4, C4); outlines(ax, 0.15)
for gx, gy in zip(G[wn >= 5].centroid.x, G[wn >= 5].centroid.y):
    ax.add_patch(mpl.patches.Circle((gx, gy), 650, fc="none", ec="#b30000", lw=1.4, zorder=8))
cnt = [(wn == 0).sum(), ((wn >= 1) & (wn <= 2)).sum(), ((wn >= 3) & (wn <= 4)).sum(), (wn >= 5).sum()]
ring = Line2D([], [], ls="none", marker="o", ms=10, mfc="none", mec="#b30000", mew=1.4, label="Persistently weak field (≥ 5 years)")
legend_p(axp, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(C4, L4)] + [ring],
         "Years in the lowest 10 % of fields (of 7)", ncol=3)
finish(fig, ax, axp, "map3_weak")


# ---------------- charts ----------------
LEG = dict(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
def style(ax, axis="y"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
def save(fig, name):
    fig.text(0.99, 0.01, AUTHOR, ha="right", va="bottom", fontsize=7, color="#777777"); fig.tight_layout()
    fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)

# Figure 1: 84 months of NDVI and NDMI over the cane fields (top) and monthly rainfall (bottom), sharing the time axis
nd_ = sum((ST["annual"][str(y)]["estate_ndvi"] for y in YEARS), []); nm_ = sum((ST["annual"][str(y)]["estate_ndmi"] for y in YEARS), [])
rn = [RAIN.get(f"{y}-{m:02d}", np.nan) for y in YEARS for m in range(1, 13)]; x = np.arange(84)
fig, (ax, a2) = plt.subplots(2, 1, figsize=(9.6, 4.8), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0.08))
style(ax); style(a2)
ax.plot(x, nd_, color=GREEN, lw=1.6, label="NDVI (greenness)"); ax.plot(x, nm_, color=BLUE, lw=1.6, label="NDMI (moisture)")
ax.set_ylim(0, 0.9); ax.set_ylabel("Index value"); ax.legend(ncol=2, **LEG)
a2.bar(x, rn, 0.8, color="#5B9BD5"); a2.set_ylim(0, 300); a2.set_yticks([0, 100, 200, 300]); a2.set_ylabel("Rainfall (mm)")
a2.set_xticks(np.arange(0, 84, 12)); a2.set_xticklabels([f"Jan {y}" for y in YEARS]); a2.set_xlim(-1, 84)
fig.align_ylabels([ax, a2])
save(fig, "fig1_series")

# Figure 2: harvested area by month, mean of seven years with the lowest and highest year
hm = np.array([ST["annual"][str(y)]["harvest_month_hist_ha"] for y in YEARS]); mu = hm.mean(0)
fig, ax = plt.subplots(figsize=(8.6, 3.7)); style(ax); x = np.arange(12)
ax.bar(x, mu, 0.62, color=BLUE, yerr=[mu - hm.min(0), hm.max(0) - mu], error_kw=dict(lw=0.7, capsize=2.5, ecolor="#404040"),
       label="Mean harvested area, 2019 to 2025 (whiskers: lowest and highest year)")
for i in x: ax.text(i, hm.max(0)[i] + 45, sp(mu[i]), ha="center", fontsize=7.5)
ax.set_xticks(x); ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.set_ylabel("Hectares"); ax.set_ylim(0, 3000); ax.legend(**LEG)
save(fig, "fig2_harvest")

# Figure 3: dry-season moisture and peak greenness by year, labelled with the rainfall of the season before
seas = {y: sum(RAIN[f"{y - 1 if m >= 7 else y}-{m:02d}"] for m in list(range(7, 13)) + list(range(1, 7))) for y in YEARS}
dn = [ST["annual"][str(y)]["dry_ndmi"] for y in YEARS]; pk = [ST["annual"][str(y)]["peak_ndvi"] for y in YEARS]
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.7)); x = np.arange(7); lab = [f"{y}\n{seas[y]:.0f} mm" for y in YEARS]
for ax, v, col, yl, lim, nm in ((axs[0], pk, GREEN, "Peak NDVI", (0.7, 0.82), "Peak greenness of the cane"),
                                 (axs[1], dn, BLUE, "Dry-season NDMI (Aug to Oct)", (0.15, 0.25), "Moisture in the dry season")):
    style(ax); ax.bar(x, v, 0.6, color=col, label=nm)
    for i in x: ax.text(i, v[i] + (lim[1] - lim[0]) * 0.015, f"{v[i]:.3f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=7.5); ax.set_ylim(*lim); ax.set_ylabel(yl); ax.legend(**LEG)
save(fig, "fig3_years")

r_pk = np.corrcoef([seas[y] for y in YEARS], pk)[0, 1]; r_dn = np.corrcoef([seas[y] for y in YEARS], dn)[0, 1]
yr = np.arange(7); slope = np.polyfit(yr, dn, 1)[0]
json.dump({"season_rain": seas, "r_rain_peak": r_pk, "r_rain_drynd": r_dn, "dry_ndmi_slope_per_year": slope,
           "harvest_mean_ha": mu.tolist(), "harvest_may_nov_share": float(mu[4:11].sum() / mu.sum()),
           "weak_counts": [int(c) for c in cnt], "vigour_counts": [int((np.digitize(G.pk_mean, B2[1:-1]) == i).sum()) for i in range(5)]}, open("out/fig_stats.json", "w"), indent=1)
print(open("out/fig_stats.json").read())
