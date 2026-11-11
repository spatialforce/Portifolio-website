"""Plain Excel-style charts for case study 1."""
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, os
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
os.makedirs("out", exist_ok=True)
BLUE, ORANGE = "#4472C4", "#ED7D31"

def base(w=7.5, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax

def sign(fig):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")

# Figure 1: census totals
yrs = [1982, 1992, 2002, 2012, 2022]; pop = [7608432, 10412548, 11631657, 13061239, 15178979]
fig, ax = base()
ax.bar([str(y) for y in yrs], [p / 1e6 for p in pop], color=BLUE, width=0.55)
for i, p in enumerate(pop): ax.text(i, p / 1e6 + 0.2, f"{p/1e6:.2f}", ha="center", fontsize=8)
ax.set_ylabel("Population (millions)"); ax.set_xlabel("Census year"); ax.set_ylim(0, 17)
sign(fig); fig.tight_layout(); fig.savefig("out/fig1_census_totals.png"); plt.close(fig)

# Figure 2: provinces 2012 vs 2022
P = ["Bulawayo", "Manicaland", "Mash. Central", "Mash. East", "Mash. West", "Mat. North", "Mat. South", "Midlands", "Masvingo", "Harare"]
p12 = [653337, 1752698, 1152520, 1344955, 1501656, 749017, 683893, 1614941, 1485090, 2123132]
p22 = [665940, 2037762, 1384891, 1731181, 1893578, 827626, 760345, 1811908, 1638539, 2427209]
o = np.argsort(p22)[::-1]; x = np.arange(len(P))
fig, ax = base(8.5, 4.4)
ax.bar(x - 0.2, [p12[i] / 1e6 for i in o], 0.4, color=BLUE, label="2012")
ax.bar(x + 0.2, [p22[i] / 1e6 for i in o], 0.4, color=ORANGE, label="2022")
ax.set_xticks(x); ax.set_xticklabels([P[i] for i in o], rotation=30, ha="right")
ax.set_ylabel("Population (millions)"); ax.set_ylim(0, 2.75); ax.legend(frameon=False, loc="upper right", ncol=2)
sign(fig); fig.tight_layout(); fig.savefig("out/fig2_provinces.png"); plt.close(fig)

print("graphs done")
