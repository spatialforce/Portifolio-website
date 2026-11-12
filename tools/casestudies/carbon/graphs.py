"""Plain Excel-style charts for the Hwange GEDI carbon case study."""
import json, os
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, pandas as pd
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/stats.json"))

def base(w=8.5, h=4.2, xgrid=False):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="x" if xgrid else "y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax
def sign(fig): fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")

# Figure 1: observed vs predicted (spatial block CV)
cv = pd.read_csv("out/cv.csv"); c = S["cv"]
fig, ax = base(6.2, 5.6); ax.grid(axis="both", color="#d9d9d9", lw=0.6)
smp = cv.sample(5000, random_state=1)                      # plain scatter of a random 5 000 cells
ax.scatter(smp.obs, smp.pred, s=6, color=BLUE, alpha=0.35, lw=0, label="Cells (random 5 000 of 211 509)")
edges = np.arange(0, 85, 5); mid = (edges[:-1] + edges[1:]) / 2
bm = [cv.pred[(cv.obs >= lo) & (cv.obs < hi)].mean() for lo, hi in zip(edges[:-1], edges[1:])]
ax.plot(mid, bm, color=ORANGE, lw=1.6, marker="o", ms=4, label="Mean prediction per 5 Mg/ha class")
ax.plot([0, 80], [0, 80], color="#404040", lw=1.0, label="1:1 line")
ax.set_xlim(0, 80); ax.set_ylim(0, 80); ax.set_aspect("equal")
ax.set_xlabel("GEDI cell mean AGBD (Mg/ha)"); ax.set_ylabel("Predicted AGBD in held-out blocks (Mg/ha)")
ax.text(3, 77, f"R² = {c['r2']:.2f}\nRMSE = {c['rmse']:.1f} Mg/ha ({c['rmse_pct']:.0f}%)\nBias = {c['bias']:+.2f} Mg/ha\n"
        f"n = {len(cv):,} cells".replace(",", " "), va="top", fontsize=8.5, bbox=dict(fc="white", ec="#bfbfbf", lw=0.5))
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, fontsize=8)
sign(fig); fig.tight_layout(); fig.savefig("out/fig1_cv.png"); plt.close(fig)

# Figure 2: mean AGBD by land cover, this study vs ESA CCI, with field reference
cls = [k for k in S["classes"] if k["share"] > 1]
fig, ax = base(8.0, 4.2)
x = np.arange(len(cls) + 1); w = 0.36
mine = [k["agbd"] for k in cls] + [S["totals"]["agbd_mean"]]; cci = [k["cci"] for k in cls] + [S["totals"]["cci_mean"]]
ax.bar(x - w / 2, mine, w, color=BLUE, label="This study (GEDI + Random Forest)", zorder=3)
ax.bar(x + w / 2, cci, w, color=GREY, label="ESA CCI Biomass v5 (2020)", zorder=3)
for i in range(len(x)):
    ax.text(x[i] - w / 2, mine[i] + 0.6, f"{mine[i]:.1f}", ha="center", fontsize=8.5)
    ax.text(x[i] + w / 2, cci[i] + 0.6, f"{cci[i]:.1f}", ha="center", fontsize=8.5)
ax.axhline(29.44, color=ORANGE, lw=1.1, ls="--", zorder=4)
ax.text(len(x) - 0.55, 30.2, "Baikiaea woodland field plots, NW Zimbabwe (GIZ 2015): 29.4", ha="right", fontsize=7.8, color="#9c4a0e")
ax.set_xticks(x); ax.set_xticklabels([f"{k['name']}\n({k['share']:.0f}% of park)" for k in cls] + ["Whole park"], fontsize=8.5)
ax.set_ylabel("Mean AGBD (Mg/ha)"); ax.set_ylim(0, 42); ax.legend(frameon=False, loc="upper right", fontsize=8.5, ncol=2)
sign(fig); fig.tight_layout(); fig.savefig("out/fig2_classes.png"); plt.close(fig)

# Figure 3: predictor importance
NM = {"s1_VV": "Sentinel-1 VV (dry)", "s1_VH": "Sentinel-1 VH (dry)", "elev": "Elevation", "slope": "Slope",
      "dry_NDVI": "NDVI (dry)", "wet_NDVI": "NDVI (wet)"}
nm = lambda k: NM.get(k, k.replace("dry_", "").replace("wet_", "") + (" (dry)" if k.startswith("dry") else " (wet)"))
imp = list(S["importance"].items())[::-1]
fig, ax = base(7.0, 4.6, xgrid=True)
cols = [ORANGE if k.startswith("s1") else (GREY if k in ("elev", "slope") else BLUE) for k, _ in imp]
ax.barh([nm(k) for k, _ in imp], [100 * v for _, v in imp], color=cols, height=0.62, zorder=3)
for i, (_, v) in enumerate(imp): ax.text(100 * v + 0.4, i, f"{100 * v:.1f}", va="center", fontsize=8)
ax.set_xlabel("Share of Random Forest impurity reduction (%)"); ax.set_xlim(0, 36); ax.tick_params(axis="y", labelsize=8.5)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc=ORANGE, label="Radar (Sentinel-1)"), Patch(fc=BLUE, label="Optical (Sentinel-2)"), Patch(fc=GREY, label="Terrain (GLO-30)")],
          frameon=False, loc="lower right", fontsize=8.5)
sign(fig); fig.tight_layout(); fig.savefig("out/fig3_importance.png"); plt.close(fig)
print("charts ok")
