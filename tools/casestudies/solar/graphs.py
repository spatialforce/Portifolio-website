"""Plain Excel-style charts for case study 7 (AHP solar suitability)."""
import json, os
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("out", exist_ok=True)
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"

res = json.load(open("out/results.json"))


def base(w=8.5, h=4.2, xgrid=False):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="x" if xgrid else "y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax


def sign(fig):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")


# Figure 1: AHP weights against published studies
CRIT = ["GHI", "Distance to grid", "Slope", "Distance to roads", "Land cover", "Distance to settlements"]
LIT = {  # criterion -> list of (study, weight); solar resource proxies marked in the report text
    "GHI": [("Al Garni & Awasthi 2017", 0.322), ("Doorga et al. 2019", 0.401), ("Mutume 2023", 0.555)],
    "Distance to grid": [("Noorollahi et al. 2016", 0.112), ("Sánchez-Lozano et al. 2013", 0.415)],
    "Slope": [("Al Garni & Awasthi 2017", 0.163)],
}
fig, ax = base(10, 4.6)
x = np.arange(len(CRIT))
ax.bar(x, [res["weights"][c] for c in CRIT], color=BLUE, width=0.4, label="This study", zorder=3)
seen = set()
for i, c in enumerate(CRIT):
    for study, wv in LIT.get(c, []):
        lab = "Weight in a published study" if "lit" not in seen else None; seen.add("lit")
        ax.plot(i + 0.26, wv, "D", ms=6, mfc=ORANGE, mec="#9c4a0e", mew=0.7, zorder=4, label=lab)
        short = study.replace(" et al.", "").replace(" & Awasthi", "")
        ax.text(i + 0.31, wv, short, va="center", ha="left", fontsize=6.8, color="#555555", zorder=4)
for i, c in enumerate(CRIT):
    ax.text(i, res["weights"][c] + 0.012, f"{res['weights'][c]:.3f}", ha="center", fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels([c.replace("Distance to ", "Distance to\n") for c in CRIT], fontsize=8.5)
ax.set_ylabel("AHP weight"); ax.set_ylim(0, 0.62)
ax.legend(frameon=False, loc="upper right", fontsize=8.5)
ax.set_title(f"Criterion weights (consistency ratio {res['CR']:.3f})", fontsize=10, loc="left")
sign(fig); fig.tight_layout(); fig.savefig("out/fig1_weights.png"); plt.close(fig)

# Figure 2: suitability class areas
fig, ax = base(7.5, 4.0)
names = ["Unsuitable", "Low", "Moderate", "High", "Very high"]
vals = [res["classes"][n] for n in names]
cols = ["#d73027", "#fdae61", "#ffffbf", "#a6d96a", "#1a9850"]
ax.bar(names, vals, color=cols, width=0.6, edgecolor="#777777", lw=0.5)
tot = sum(vals)
for i, v in enumerate(vals):
    ax.text(i, v + tot * 0.012, f"{v:,.0f} km²\n({100 * v / tot:.1f}%)".replace(",", " "), ha="center", fontsize=8.5)
ax.set_ylabel("Analysable area (km²)"); ax.set_ylim(0, max(vals) * 1.22)
sign(fig); fig.tight_layout(); fig.savefig("out/fig2_classes.png"); plt.close(fig)

# Figure 3: sensitivity tornado (+-20 % per criterion weight, change in High + Very high area)
fig, ax = base(8.5, 4.2, xgrid=True)
ax.axvline(0, color="#7f7f7f", lw=0.8, zorder=2)
ys = np.arange(len(CRIT))[::-1]
up = [res["sensitivity"][f"{c} +20%"]["change_pct"] for c in CRIT]
dn = [res["sensitivity"][f"{c} -20%"]["change_pct"] for c in CRIT]
ax.barh(ys + 0.18, up, height=0.34, color=BLUE, label="Weight +20%")
ax.barh(ys - 0.18, dn, height=0.34, color=ORANGE, label="Weight −20%")
for y, u, d in zip(ys, up, dn):
    ax.text(u + (0.25 if u >= 0 else -0.25), y + 0.18, f"{u:+.1f}%", va="center",
            ha="left" if u >= 0 else "right", fontsize=8)
    ax.text(d + (0.25 if d >= 0 else -0.25), y - 0.18, f"{d:+.1f}%", va="center",
            ha="left" if d >= 0 else "right", fontsize=8)
ax.set_yticks(ys); ax.set_yticklabels(CRIT, fontsize=9)
ax.tick_params(axis="y", length=0)
ax.set_xlabel("Change in High and Very high area (%)")
lim = max(map(abs, up + dn)) * 1.35
ax.set_xlim(-lim, lim)
ax.legend(frameon=False, loc="lower right", fontsize=8.5)
sign(fig); fig.tight_layout(); fig.savefig("out/fig3_sensitivity.png"); plt.close(fig)

# Figure 4: High + Very high area by district
d = {k: v for k, v in res["districts"].items()
     if v["high_plus_km2"] is not None and "Urban" not in k and k not in ("Beitbridge", "Plumtree", "Gwanda Urban")}
order = sorted(d, key=lambda k: -d[k]["high_plus_km2"])
fig, ax = base(8.0, 4.0)
vals = [d[k]["high_plus_km2"] for k in order]
ax.bar([k.replace(" Rural", "") for k in order], vals, color=BLUE, width=0.6)
for i, v in enumerate(vals):
    ax.text(i, v + max(vals) * 0.015, f"{v:,.0f}".replace(",", " "), ha="center", fontsize=8.5)
ax.set_ylabel("High and Very high area (km²)"); ax.set_xlabel("District"); ax.set_ylim(0, max(vals) * 1.15)
sign(fig); fig.tight_layout(); fig.savefig("out/fig4_districts.png"); plt.close(fig)

print("graphs done")
