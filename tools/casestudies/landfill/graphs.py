"""Plain Excel-style charts for the Bulawayo landfill study (no in-image titles). Writes out/fig*.png."""
import json
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
R = json.load(open("out/results.json")); C = json.load(open("out/constraints.json"))


def style(ax, axis="x"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)


def labels(ax, bars, fmt, horiz=True):
    for b in bars:
        if horiz: ax.text(b.get_width(), b.get_y() + b.get_height() / 2, " " + fmt(b.get_width()), va="center", fontsize=8)
        else: ax.text(b.get_x() + b.get_width() / 2, b.get_height(), fmt(b.get_height()), ha="center", va="bottom", fontsize=8)


def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)


# Figure 1: AHP weights
W = R["weights"]; n = list(W)[::-1]
fig, ax = plt.subplots(figsize=(8.0, 3.2)); style(ax)
bars = ax.barh(n, [W[k] for k in n], color=BLUE, height=0.6); labels(ax, bars, lambda v: f"{v:.3f}")
ax.set_xlabel("Weight"); ax.set_xlim(0, 0.36)
save(fig, "fig2_weights")

# Figure 2: area of each suitability class on open land
lab = ["Very low", "Low", "Moderate", "High", "Very high"]; col = ["#d7191c", "#fdae61", "#ffffbf", "#a6d96a", "#1a9641"]
a = [R["class_km2"][str(i)] for i in range(1, 6)]
fig, ax = plt.subplots(figsize=(8.0, 3.2)); style(ax, "y")
bars = ax.bar(lab, a, color=col, edgecolor="#7f7f7f", lw=0.5, width=0.6); labels(ax, bars, lambda v: f"{v:.1f}", horiz=False)
ax.set_ylabel("Area (km²)"); ax.set_ylim(0, 300)
save(fig, "fig3_classes")
