"""Plain Excel-style charts for the Chivi soil loss study (no in-image titles). Writes out/fig*.png."""
import json
import matplotlib as mpl, matplotlib.pyplot as plt
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE = "#4472C4"; S = json.load(open("out/stats.json"))
def style(ax, axis="x"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)
fs = lambda v: f"{v:,.1f}".replace(",", " ")
# Figure 1: area of each soil loss class
lab = ["Very low\n(< 2)", "Low\n(2 to 5)", "Moderate\n(5 to 10)", "High\n(10 to 20)", "Very high\n(> 20)"]
col = ["#1a9641", "#a6d96a", "#ffffbf", "#fdae61", "#d7191c"]; a = [c["km2"] for c in S["classes"]]
fig, ax = plt.subplots(figsize=(8.0, 3.3)); style(ax, "y")
bars = ax.bar(lab, a, color=col, edgecolor="#7f7f7f", lw=0.5, width=0.6)
for b_, c in zip(bars, S["classes"]): ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height(), f"{fs(c['km2'])}\n({c['pct']:.1f} %)", ha="center", va="bottom", fontsize=8)
ax.set_ylabel("Area (km²)"); ax.set_xlabel("Soil loss class (t/ha/yr)"); ax.set_ylim(0, max(a) * 1.3)
save(fig, "fig1_classes")
# Figure 2: mean soil loss by land cover
L = sorted([r for r in S["landcover"] if r["lc"] != "Built-up"], key=lambda r: r["mean"])
fig, ax = plt.subplots(figsize=(8.0, 3.0)); style(ax)
bars = ax.barh([r["lc"] for r in L], [r["mean"] for r in L], color=BLUE, height=0.6)
for b_ in bars: ax.text(b_.get_width(), b_.get_y() + b_.get_height() / 2, " " + fs(b_.get_width()), va="center", fontsize=8)
ax.axvline(11.2, color="#c00000", lw=0.9, ls="--"); ax.text(11.2, len(L) - 0.45, " Upper tolerable limit (11.2)", color="#c00000", fontsize=8, va="bottom")
ax.set_xlabel("Mean soil loss (t/ha/yr)"); ax.set_xlim(0, max(r["mean"] for r in L) * 1.25)
save(fig, "fig2_landcover")
