"""Plain Excel-style charts for the Shurugwi study (no in-image titles). Writes out/fig*.png."""
import json
import numpy as np, matplotlib as mpl, matplotlib.pyplot as plt, geopandas as gpd
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE = "#4472C4", "#ED7D31"; S = json.load(open("out/stats.json")); G = json.load(open("out/grisk.json"))
def style(ax, axis="x"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#555555")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)
fs = lambda v, d=1: f"{v:,.{d}f}".replace(",", " ")

# Figure 1: area of each soil loss class
lab = ["Very low\n(< 2)", "Low\n(2 – 5)", "Moderate\n(5 – 10)", "High\n(10 – 20)", "Very high\n(> 20)"]
col = ["#ffffd4", "#fed98e", "#fe9929", "#d95f0e", "#7f2704"]; a = [c["km2"] for c in S["classes"]]
fig, ax = plt.subplots(figsize=(6.2, 3.6)); style(ax, "y")
bars = ax.bar(lab, a, color=col, edgecolor="#7f7f7f", lw=0.5, width=0.6)
for b_, c in zip(bars, S["classes"]): ax.text(b_.get_x() + b_.get_width() / 2, b_.get_height(), f"{fs(c['km2'])}\n({c['pct']:.1f} %)", ha="center", va="bottom", fontsize=8)
ax.set_ylabel("Area (km²)"); ax.set_xlabel("Soil loss class (t/ha/yr)"); ax.set_ylim(0, max(a) * 1.25)
save(fig, "fig1_classes")

# Figure 2: mean soil loss and high gully risk share by land cover (two panels)
L = [r for r in S["landcover"] if r["lc"] != "Built-up"]; gd = G["landcover"]; gd["Bare or sparse"] = gd.get("Bare or sparse"); L = [r for r in L if r["lc"] in gd]
L.sort(key=lambda r: r["mean"]); nm = [r["lc"] for r in L]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.0), sharey=True)
for ax, vals, c, xl, d in ((a1, [r["mean"] for r in L], BLUE, "Mean soil loss (t/ha/yr)", 1), (a2, [gd[n] for n in nm], ORANGE, "Land at high gully risk (%)", 1)):
    style(ax); bars = ax.barh(nm, vals, color=c, height=0.6)
    for b_ in bars: ax.text(b_.get_width(), b_.get_y() + b_.get_height() / 2, " " + fs(b_.get_width(), d), va="center", fontsize=8)
    ax.set_xlabel(xl); ax.set_xlim(0, max(vals) * 1.22)
a1.text(-0.02, 1.04, "(a)", transform=a1.transAxes, fontweight="bold"); a2.text(-0.02, 1.04, "(b)", transform=a2.transAxes, fontweight="bold")
save(fig, "fig2_landcover")

# Figure 3: wards, mean soil loss against high gully risk share
w = gpd.read_file("out/wards.gpkg")
fig, ax = plt.subplots(figsize=(6.2, 3.9)); style(ax, "both")
ax.scatter(w["ghi"], w["mean"], s=26, color=BLUE, edgecolor="white", lw=0.6, zorder=3)
for x, y, n in zip(w["ghi"], w["mean"], w["ward"]): ax.annotate("T" if n == "Town" else n, (x, y), xytext=(4, 3), textcoords="offset points", fontsize=7.5)
r = np.corrcoef(w["ghi"], w["mean"])[0, 1]; rr = np.corrcoef(w[w.ward != "Town"]["ghi"], w[w.ward != "Town"]["mean"])[0, 1]
print("r all", round(r, 2), "r rural", round(rr, 2))
ax.set_xlabel("Land at high gully risk (%)"); ax.set_ylabel("Mean soil loss (t/ha/yr)")
save(fig, "fig3_wards")
