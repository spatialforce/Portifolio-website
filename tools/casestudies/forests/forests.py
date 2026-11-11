"""Case study: gazetted forests of Matabeleland North. Figures from the 2024 Forestry Commission maps (legend areas).
Map 1 study area (approximate forest centres read off each map's graticule), Figure 1 and 2. Output: out/*.png"""
import os, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe, numpy as np, geopandas as gpd
from matplotlib.patches import Rectangle
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
P = "../population/"
AUTHOR = "© Kudzanai Chakavarika"
# name: (forest/woodland ha, cultivation ha, other ha, lon, lat)
F = {"Gwaai": (127880.06, 16061.60, 322.80, 27.93, -19.26),
     "Bembesi": (47506.00, 7539.10, 0, 28.13, -19.36),
     "Lake Alice": (34765.40, 4235.60, 0, 28.25, -19.08),
     "Gwampa": (43579.82, 3420.18, 0, 28.68, -19.17),
     "Inseze Extension": (7885.11, 514.89, 0, 28.03, -19.81),
     "Chesa": (12915.00, 1199.83, 135.16, 28.19, -20.02),
     "Kavira": (28013.44, 186.56, 0, 26.98, -18.05)}
TOTAL = {"Gwaai": 144265, "Bembesi": 55100, "Lake Alice": 39000, "Gwampa": 47000, "Inseze Extension": 8400, "Chesa": 14250, "Kavira": 28200}

print(f"{'forest':18}{'total':>9}{'sum':>11}{'lost':>10}{'lost%':>7}")
lost = {}
for n, (f, c, o, *_) in F.items():
    lost[n] = c + (o if n == "Gwaai" else 0)   # Chesa plantation is a forest use, not loss
    print(f"{n:18}{TOTAL[n]:>9}{f + c + o:>11.2f}{lost[n]:>10.2f}{100 * lost[n] / TOTAL[n]:>7.2f}")
L = sum(lost.values()); T = sum(TOTAL.values())
print("total lost", round(L, 2), "of", T, round(100 * L / T, 2), "%; cultivation only", round(sum(v[1] for v in F.values()), 2))
for n in F: print(f"  share of all loss {n}: {100 * lost[n] / L:.1f}%")

# Map 1: study area
dist = gpd.read_file(P + "data/districts.gpkg"); prov = gpd.read_file(P + "raw/bnd/zwe_admin1.shp"); zwe = gpd.read_file(P + "raw/bnd/zwe_admin0.shp")
world = gpd.read_file("zip://../../corridors/raw/ne_10m_admin_0_countries.zip").cx[24:31, -21.5:-16.5]
lakes = gpd.read_file("zip://../../corridors/raw/ne_10m_lakes.zip").cx[25:30, -21:-16.5]
EXT = (24.95, 29.95, -20.85, -17.15)
fig = plt.figure(figsize=(10, 7.6), dpi=200); ax = fig.add_axes([0.06, 0.08, 0.9, 0.86])
ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(1 / np.cos(np.radians(19)))
ax.set_facecolor("#eeeeee")
world.plot(ax=ax, fc="#e3e3e3", ec="#ffffff", lw=0.8, zorder=1)
mnd = dist[dist.province == "Matabeleland North"]
zwe.plot(ax=ax, fc="#f7f7f7", ec="none", zorder=2)
mnd.plot(ax=ax, fc="#fbf6e9", ec="none", zorder=3)
lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=4)
mnd.boundary.plot(ax=ax, color="#888888", lw=0.5, ls="--", zorder=5)
prov.boundary.plot(ax=ax, color="#333333", lw=0.8, zorder=6); zwe.boundary.plot(ax=ax, color="#111111", lw=1.1, zorder=6)
for _, r in mnd.iterrows():
    if "Urban" in str(r.adm2) or "Victoria" in str(r.adm2): continue
    c = r.geometry.representative_point()
    ax.text(c.x, c.y + 0.14, str(r.adm2).replace(" Rural", "").upper(), fontsize=7, color="#666666", ha="center", style="italic", zorder=7)
for n, x, y in [("Bulawayo", 28.583, -20.150), ("Victoria Falls", 25.840, -17.932), ("Hwange", 26.500, -18.364), ("Lupane", 27.80, -18.93),
                ("Binga", 27.33, -17.62), ("Nkayi", 28.90, -19.00), ("Tsholotsho", 27.75, -19.77)]:
    dx = -0.05 if n == "Tsholotsho" else 0.05
    ax.plot(x, y, "s" if n == "Bulawayo" else "o", ms=4, mfc="white", mec="black", mew=0.7, zorder=8)
    ax.text(x + dx, y - 0.09, n, ha="right" if dx < 0 else "left", fontsize=7.5, zorder=8, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
CL = [(15000, 70, "0 – 15 000 ha"), (40000, 170, "15 001 – 40 000 ha"), (60000, 320, "40 001 – 60 000 ha"), (1e9, 620, "60 001 – 145 000 ha")]
size = lambda a: next(sz for lim, sz, _ in CL if a <= lim)
off = {"Gwaai": (-0.17, 0.0, "right"), "Bembesi": (0.1, -0.1, "left"), "Lake Alice": (0.08, 0.1, "left"), "Gwampa": (0.1, -0.08, "left"),
       "Inseze Extension": (0.07, 0.0, "left"), "Chesa": (-0.07, 0.0, "right"), "Kavira": (0.08, 0.0, "left")}
for n, v in F.items():
    ax.scatter(v[3], v[4], s=size(TOTAL[n]), c="#2e7d32", ec="#103b12", lw=0.7, alpha=0.85, zorder=9)
    dx, dy, ha = off[n]
    ax.text(v[3] + dx, v[4] + dy, n, ha=ha, va="center", fontsize=8.5, fontweight="bold", color="#103b12", zorder=10, path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
for n, x, y in [("ZAMBIA", 26.5, -17.62), ("BOTSWANA", 25.35, -18.5)]:
    ax.text(x, y, n, fontsize=7.5, color="#888888", style="italic", ha="center", zorder=7)
ax.set_xticks(np.arange(26, 30)); ax.set_yticks(np.arange(-20, -17))
ax.set_xticklabels([f"{x}°E" for x in range(26, 30)]); ax.set_yticklabels([f"{-y}°S" for y in range(-20, -17)])
ax.grid(color="#bbbbbb", lw=0.3, ls=":"); ax.tick_params(length=2)
ax.text(0.31, 0.965, "Study Area Map", transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", zorder=20,
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])
ax.annotate("", xy=(25.12, -17.21), xytext=(25.12, -17.41), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color="#222222", lw=1.2), zorder=20)
ax.text(25.12, -17.42, "N", ha="center", va="top", fontsize=10, fontweight="bold", zorder=20)
km = 111.32 * np.cos(np.radians(20)); Lb = 100 / km; x0, y0 = 28.42, -20.66
for i in range(4):
    ax.add_patch(Rectangle((x0 + i * Lb / 4, y0), Lb / 4, 0.04, fc="#222222" if i % 2 == 0 else "white", ec="#222222", lw=0.6, zorder=20))
for v, x in [(0, x0), (50, x0 + Lb / 2), (100, x0 + Lb)]:
    ax.text(x, y0 + 0.07, f"{v}", ha="center", fontsize=7, zorder=20)
ax.text(x0 + Lb + 0.05, y0 + 0.02, "km", fontsize=7, va="center", zorder=20)
h = [plt.scatter([], [], s=sz, c="#2e7d32", ec="#103b12", lw=0.7, alpha=0.85) for _, sz, _ in CL]
leg = ax.legend(h, [t for *_, t in CL], title="Gazetted forest (area)", loc="lower left", frameon=True, fontsize=8,
                title_fontsize=8.5, labelspacing=2.8, borderpad=1.8, handletextpad=2.0, facecolor="white", edgecolor="#999999")
leg.get_title().set_fontweight("bold"); leg.set_zorder(30)
ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#777777", zorder=50)
ax.text(0, -0.06, "Source: forest areas from Forestry Commission of Zimbabwe (2024); symbols at the approximate centre of each forest; "
        "boundaries OCHA COD-AB 2023; Natural Earth. WGS 84.", transform=ax.transAxes, fontsize=6.5, va="top")
fig.savefig("out/map1_study_area.png", dpi=200, bbox_inches="tight", pad_inches=0.2); plt.close(fig)

# Excel-style graphs
BLUE, ORANGE, GREY, GREEN = "#4472C4", "#ED7D31", "#A5A5A5", "#70AD47"
def base(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    ax.set_axisbelow(True); ax.grid(axis="x", color="#d9d9d9", lw=0.6); return fig, ax
def sign(fig): fig.text(0.99, 0.01, AUTHOR, ha="right", va="bottom", fontsize=7, color="#777777")
sp = lambda v: f"{v:,.0f}".replace(",", " ")

# Figure 1: share of each forest under woodland, cultivation and other land
order = sorted(F, key=lambda n: lost[n] / TOTAL[n])
fig, ax = base(8.5, 4.2); y = np.arange(len(order))
pf = np.array([100 * F[n][0] / TOTAL[n] for n in order]); pc = np.array([100 * F[n][1] / TOTAL[n] for n in order]); po = np.array([100 * F[n][2] / TOTAL[n] for n in order])
ax.barh(y, pf, 0.6, color=GREEN, label="Forest or woodland")
ax.barh(y, pc, 0.6, left=pf, color=ORANGE, label="Cultivation")
ax.barh(y, po, 0.6, left=pf + pc, color=GREY, label="Powerline (Gwaai) or plantation (Chesa)")
for i, n in enumerate(order): ax.text(100.4, i, f"{100 * lost[n] / TOTAL[n]:.1f}% lost", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(order); ax.set_xlim(80, 100); ax.set_xlabel("Share of gazetted area (%), axis starts at 80%")
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), ncol=3, fontsize=8, borderaxespad=0)
sign(fig); fig.tight_layout(); fig.savefig("out/fig1_share.png"); plt.close(fig)

# Figure 2: land lost in hectares
o2 = sorted(F, key=lambda n: lost[n])
fig, ax = base(8.5, 3.8); y = np.arange(len(o2))
ax.barh(y, [lost[n] for n in o2], 0.6, color=BLUE)
for i, n in enumerate(o2): ax.text(lost[n] + 200, i, f"{sp(lost[n])} ha", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels(o2); ax.set_xlim(0, 19000); ax.set_xlabel("Land lost (ha)")
ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: sp(v)))
sign(fig); fig.tight_layout(); fig.savefig("out/fig2_lost.png"); plt.close(fig)
print("done")
