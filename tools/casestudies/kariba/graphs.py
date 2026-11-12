"""Plain Excel-style charts for the Lake Kariba study (legends above the plot, no in-image titles)."""
import json
import numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/stats.json")); MOL, MRL = 475.5, 488.5
LEG = dict(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)


def style(ax, axis="y"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)


def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)


# Figure 1: monthly lake level with the operating range
M = pd.read_csv("out/monthly.csv", parse_dates=["t"]).set_index("t").h
fig, ax = plt.subplots(figsize=(8.0, 3.6)); style(ax)
ax.plot(M.index, M.values, color=BLUE, lw=1.2, label="Monthly mean level")
ax.axhline(MRL, color=GREY, lw=1.0, ls=(0, (1, 0)), label="Maximum regulated level (488.5 m)")
ax.axhline(MOL, color=ORANGE, lw=1.2, label="Minimum operating level (475.5 m)")
ax.set_ylabel("Level (m above sea level)"); ax.set_ylim(474, 490); ax.set_xlim(pd.Timestamp("2000-01-01"), pd.Timestamp("2026-01-01"))
ax.legend(ncol=3, **LEG)
save(fig, "fig1_level")

# Figure 2: annual minimum and maximum level
yr = sorted(int(y) for y in S["annual"]); mn = [S["annual"][str(y)]["min"] for y in yr]; mx = [S["annual"][str(y)]["max"] for y in yr]
fig, ax = plt.subplots(figsize=(8.0, 3.6)); style(ax); x = np.arange(len(yr)); wd = 0.38
ax.bar(x - wd / 2, np.array(mx) - 470, wd, bottom=470, color=BLUE, label="Annual maximum")
ax.bar(x + wd / 2, np.array(mn) - 470, wd, bottom=470, color=ORANGE, label="Annual minimum")
ax.axhline(MOL, color="#404040", lw=0.9, label="Minimum operating level")
ax.set_xticks(x[::2]); ax.set_xticklabels([str(y) for y in yr][::2]); ax.set_ylim(472, 490); ax.set_ylabel("Level (m above sea level)")
ax.legend(ncol=3, **LEG)
save(fig, "fig2_annual")

# Figure 3: lake area against level with the fitted line
P = pd.read_csv("out/pairs.csv"); C = S["coef"]
fig, ax = plt.subplots(figsize=(8.0, 3.8)); style(ax, "both")
for s, col, lab in (("high", BLUE, "High season (April to June)"), ("low", ORANGE, "Low season (October to December)")):
    q = P[P.season == s]; ax.scatter(q.h, q.area_km2, s=18, color=col, label=lab, zorder=3)
hh = np.linspace(475, 489, 50); ax.plot(hh, np.polyval(C, hh), color="#404040", lw=1.0, label=f"Fitted line (R² {S['r2_lin']:.3f})")
ax.set_xlabel("Level (m above sea level)"); ax.set_ylabel("Lake area (km²)"); ax.set_xlim(475, 489)
ax.legend(ncol=3, **LEG)
save(fig, "fig3_area_level")

# Figure 4: live storage curve with the operator's checks
T = S["table"]; hh = np.arange(MOL, MRL + 0.01, 0.05)
A = lambda h: np.polyval(C, h); V = np.concatenate([[0], np.cumsum((A(hh[1:]) + A(hh[:-1])) / 2 * 0.05 / 1000)])
fig, ax = plt.subplots(figsize=(8.0, 3.8)); style(ax, "both")
ax.plot(hh, V, color=BLUE, lw=1.6, label="Live storage from the area curve")
ck = [c for c in S["checks"] if c["zra_live"] is not None]
ax.scatter([c["level"] for c in ck], [c["zra_live"] for c in ck], s=40, marker="D", color=ORANGE, zorder=4, label="Operator's reported storage")
pc = [c for c in S["checks"] if c["zra_live"] is None]
ax.scatter([c["level"] for c in pc], [c["zra_pct"] / 100 * S["live_km3"] for c in pc], s=40, marker="o", fc="white", ec=ORANGE, lw=1.2, zorder=4,
           label="Operator's reported % full")
ax.set_xlabel("Level (m above sea level)"); ax.set_ylabel("Live storage (km³)"); ax.set_xlim(MOL, MRL); ax.set_ylim(0, 70)
ax.legend(ncol=3, **LEG)
save(fig, "fig4_storage")
