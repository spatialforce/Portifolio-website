"""Plain Excel-style charts for the Chimanimani flood susceptibility study (legends above the plot)."""
import json
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/overlay.json"))
LEG = dict(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
def style(ax, axis="y"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)

# Figure 1: AHP weights
NM = {"driver": "Distance to river", "slope": "Slope", "elev": "Elevation", "twi": "Wetness index", "rain": "Annual rainfall",
      "dd": "Drainage density", "lulc": "Land cover", "clay": "Soil clay"}
k = list(S["weights"]); v = [S["weights"][x] * 100 for x in k]
fig, ax = plt.subplots(figsize=(8.0, 3.6)); style(ax, "x")
ax.barh(range(len(k))[::-1], v, color=BLUE, height=0.6)
for i, x in enumerate(v): ax.text(x + 0.5, len(k) - 1 - i, f"{x:.1f} %", va="center", fontsize=8)
ax.set_yticks(range(len(k))[::-1]); ax.set_yticklabels([NM[x] for x in k]); ax.set_xlabel("Weight (%)"); ax.set_xlim(0, 36)
save(fig, "fig1_weights")

# Figure 2: share of area, buildings and people in each class
C = S["classes"]; x = np.arange(5); wd = 0.27
fig, ax = plt.subplots(figsize=(8.0, 3.8)); style(ax)
for j, (vals, col, lab) in enumerate([([c["pct"] for c in C], BLUE, "Share of district area"),
                                      ([c["bld"] / S["bld_total"] * 100 for c in C], ORANGE, "Share of buildings"),
                                      ([c["pop"] / S["pop_total"] * 100 for c in C], GREY, "Share of people")]):
    b = ax.bar(x + (j - 1) * wd, vals, wd, color=col, label=lab)
    ax.bar_label(b, fmt="%.1f", fontsize=7, padding=1)
ax.set_xticks(x); ax.set_xticklabels(["Very low", "Low", "Moderate", "High", "Very high"]); ax.set_ylabel("Per cent"); ax.set_ylim(0, 45)
ax.legend(ncol=3, **LEG)
save(fig, "fig2_classes")
