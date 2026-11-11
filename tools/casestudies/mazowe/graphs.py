"""Plain Excel-style charts for case study 4 (Mazowe Valley)."""
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, pandas as pd, geopandas as gpd, os
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("out", exist_ok=True)
BLUE, ORANGE, GREY, GOLD = "#4472C4", "#ED7D31", "#A5A5A5", "#FFC000"
SEC = {"Upper (0–130 km)": (1, 13), "Middle (130–210 km)": (14, 21), "Lower (210–359 km)": (22, 36)}

def base(w=8.5, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax

def sign(fig):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")

def top_legend(ax, ncol):
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), ncol=ncol, fontsize=8, borderaxespad=0)

cor = gpd.read_file("data/reaches_corridor.gpkg").set_index("reach")
bg = gpd.read_file("data/reaches_background.gpkg"); bg["ha"] = bg.area / 1e4; bg = bg.groupby("reach").ha.sum()
a = pd.read_csv("data/bare_by_reach.csv", index_col=0); b = pd.read_csv("data/bare_background.csv", index_col=0)
W = ["2000", "2009", "2017", "2025"]

# Figure 1: bare share of each reach corridor, 2000 and 2025 windows
fig, ax = base(9.5, 4.2); x = np.arange(1, 37)
p0 = 100 * a["2000"] / cor.area_ha; p1 = 100 * a["2025"] / cor.area_ha
ax.bar(x - 0.2, p0.reindex(x), 0.4, color=GREY, label="2000 window (1998/99 to 2000/01)")
ax.bar(x + 0.2, p1.reindex(x), 0.4, color=ORANGE, label="2025 window (2023/24 to 2025/26)")
ax.set_xticks(x); ax.set_xticklabels([f"{(i - 1) * 10}" for i in x], fontsize=7.5)
ax.set_xlabel("Distance along the main stem from its western end (km, start of each 10 km reach)"); ax.set_ylabel("Bare ground (% of reach corridor)")
ax.set_xlim(0.3, 36.7)
top_legend(ax, 2); sign(fig); fig.tight_layout(); fig.savefig("out/fig1_reach_profile.png"); plt.close(fig)

# Figure 2: corridor against background by section and window
rows = []
for s, (r0, r1) in SEC.items():
    i = range(r0, r1 + 1)
    for w in W:
        rows.append({"section": s, "window": w, "corridor": 100 * a.loc[i, w].sum() / cor.loc[i, "area_ha"].sum(),
                     "background": 100 * b.loc[i, w].sum() / bg.loc[list(i)].sum()})
t = pd.DataFrame(rows); t.round(2).to_csv("data/section_table.csv", index=False); print(t.round(2).to_string(index=False))
fig, ax = base(9, 4.2); cols = ["#BDD7EE", "#9DC3E6", "#4472C4", "#1F3864"]
for k, s in enumerate(SEC):
    for j, w in enumerate(W):
        v = t[(t.section == s) & (t.window == w)].iloc[0]
        xc = k * 5 + j
        ax.bar(xc, v.corridor, 0.8, color=cols[j], label=f"{w} window" if k == 0 else None)
        ax.plot([xc - 0.4, xc + 0.4], [v.background] * 2, color="#000000", lw=1.4, label="Background band (1 to 5 km)" if k == 0 and j == 0 else None)
ax.set_xticks([k * 5 + 1.5 for k in range(3)]); ax.set_xticklabels(list(SEC)); ax.set_ylabel("Bare ground (% of area)")
top_legend(ax, 5); sign(fig); fig.tight_layout(); fig.savefig("out/fig2_sections.png"); plt.close(fig)

# Figure 3: turbidity by section, 2019 to 2025 (median of reach medians)
d = pd.read_csv("data/ndti_by_reach.csv"); d = d[d.px >= 20]
fig, ax = base(8, 4.0); out = {}
for (s, (r0, r1)), c in zip(SEC.items(), [BLUE, GOLD, ORANGE]):
    m = d[d.reach.between(r0, r1)].groupby("year").ndti.median(); out[s] = m
    ax.plot(m.index, m.values, marker="o", ms=4, color=c, lw=1.8, label=s)
ax.axhline(0, color="#7f7f7f", lw=0.8)
ax.set_xlabel("Year (April to July images)"); ax.set_ylabel("Median NDTI of water pixels"); ax.set_xticks(range(2019, 2026))
top_legend(ax, 3); sign(fig); fig.tight_layout(); fig.savefig("out/fig3_ndti.png"); plt.close(fig)
print(pd.DataFrame(out).round(3).to_string())
print("graphs done")
