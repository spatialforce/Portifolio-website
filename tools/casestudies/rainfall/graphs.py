"""Plain Excel-style charts for case study 2."""
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, pandas as pd, os
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("out", exist_ok=True)
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"

def base(w=8.5, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax

def sign(fig):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")

# Figure 1: national seasonal totals with the 1991-2020 normal and the 75 % line
d = pd.read_csv("data/national_series.csv"); nm = (d.mm / d.pct * 100).mean()
fig, ax = base(9, 4.4); x = np.arange(len(d))
ax.bar(x, d.mm, color=[ORANGE if p < 75 else BLUE for p in d.pct], width=0.7)
ax.axhline(nm, color="#000000", lw=1, label=f"Normal 1991–2020 ({nm:.0f} mm)")
ax.axhline(0.75 * nm, color="#000000", lw=1, ls="--", label=f"75% of normal ({0.75*nm:.0f} mm)")
ax.set_xticks(x); ax.set_xticklabels(d.season, rotation=90, fontsize=7.5)
ax.set_ylabel("October to April rainfall (mm)"); ax.set_xlabel("Season"); ax.set_ylim(0, 1050); ax.set_xlim(-0.7, len(d) - 0.3)
from matplotlib.patches import Patch
h, l = ax.get_legend_handles_labels()
ax.legend(h + [Patch(fc=BLUE), Patch(fc=ORANGE)], l + ["Season total", "Below 75% of normal"], frameon=False, loc="lower left", bbox_to_anchor=(0, 1.01), ncol=4, fontsize=8, borderaxespad=0)
sign(fig); fig.tight_layout(); fig.savefig("out/fig1_national_series.png"); plt.close(fig)

# Figure 2: monthly climatology, July to June
mm = [163.3, 127.1, 75.1, 23.1, 4.7, 3.4, 1.5, 1.7, 4.1, 19.9, 72.0, 149.5]
o = [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5]; mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
fig, ax = base(7.5, 4.0)
ax.bar([mon[i] for i in o], [mm[i] for i in o], color=BLUE, width=0.6)
for k, i in enumerate(o): ax.text(k, mm[i] + 2.5, f"{mm[i]:.1f}", ha="center", fontsize=8)
ax.set_ylabel("Mean rainfall (mm)"); ax.set_xlabel("Month"); ax.set_ylim(0, 185)
sign(fig); fig.tight_layout(); fig.savefig("out/fig2_monthly.png"); plt.close(fig)
print("graphs done")
