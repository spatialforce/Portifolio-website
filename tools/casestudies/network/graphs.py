"""Plain Excel-style charts for the Masvingo mobile coverage case study (legends above the plot)."""
import json
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/stats.json"))
D = sorted(S["districts"], key=lambda r: -r["any"])


def base(w=8.5, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)
    return fig, ax


def sign(fig): fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
def top(ax, n=3): ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=n, fontsize=8.5)
def names(): return [r["district"].replace(" ", "\n") for r in D]


def bars(series, fname, ylab):
    fig, ax = base(); x = np.arange(len(D)); w = 0.8 / len(series)
    for i, (key, lab, col) in enumerate(series):
        v = [r[key] for r in D]; xx = x - 0.4 + w * (i + 0.5)
        ax.bar(xx, v, w, color=col, label=lab, zorder=3)
        for a, b in zip(xx, v): ax.text(a, b + 1, f"{b:.0f}", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(names(), fontsize=8.5); ax.set_ylim(0, 108); ax.set_ylabel(ylab)
    top(ax, len(series)); sign(fig); fig.tight_layout(); fig.savefig(f"out/{fname}.png"); plt.close(fig)


# Figure 1: share of people in line of sight of a 2G or 3G site, by district
bars([("g2", "2G in line of sight (15 km)", BLUE), ("g3", "3G in line of sight (10 km)", ORANGE)], "fig1_districts",
     "Population in line of sight (%)")
# Figure 2: distance buffer vs viewshed (2G, 15 km)
bars([("buf2", "Within 15 km of a 2G site (buffer)", GREY), ("g2", "In line of sight of a 2G site (viewshed)", BLUE)], "fig2_buffer",
     "Population covered (%)")

# Figure 3: range sensitivity, one panel per technology
sn = S["sens"]
fig, axs = plt.subplots(1, 2, figsize=(8.5, 3.9), dpi=200, sharey=True)
for ax, (tech, keys) in zip(axs, (("2G", ["gsm10", "gsm15", "gsm20"]), ("3G", ["umts5", "umts10", "umts15"]))):
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#7f7f7f"); ax.spines[sp].set_linewidth(0.6)
    km = [int(k.strip("gsmut")) for k in keys]
    for key, lab, col, mk in (("buf", "Distance buffer", GREY, "s"), ("los", "Line of sight", BLUE, "o")):
        v = [sn[k][key] for k in keys]
        ax.plot(km, v, color=col, lw=1.8, marker=mk, ms=4.5, label=lab)
        for x_, y_ in zip(km, v): ax.text(x_, y_ + (2.2 if key == "buf" else -5.2), f"{y_:.1f}", ha="center", fontsize=7.8)
    ax.set_xticks(km); ax.set_xlim(km[0] - 2, km[-1] + 2); ax.set_ylim(0, 85)
    ax.set_xlabel(f"Assumed {tech} range (km)")
axs[0].set_ylabel("Population of the province covered (%)")
axs[0].legend(frameon=False, loc="lower center", bbox_to_anchor=(1.05, 1.0), ncol=2, fontsize=8.5)
sign(fig); fig.tight_layout(); fig.savefig("out/fig3_sensitivity.png"); plt.close(fig)

# Figure 4: uncovered people by distance to the nearest recorded site
b = S["tot"]["unc_dist_bands"]; lab = ["Under 10", "10 to 15", "15 to 20", "20 to 30", "Over 30"]
v = [b[k] for k in ["<10", "10-15", "15-20", "20-30", ">30"]]; n = [x / 100 * S["tot"]["unc"] for x in v]
fig, ax = base(7.0, 3.8)
ax.bar(lab, v, 0.6, color=BLUE, zorder=3, label="Share of people outside line of sight")
for i, (a, c) in enumerate(zip(v, n)): ax.text(i, a + 0.6, f"{a:.1f}% ({c / 1000:.0f} 000)", ha="center", fontsize=8)
ax.set_ylim(0, 30); ax.set_ylabel("Share of uncovered population (%)"); ax.set_xlabel("Distance to the nearest recorded site (km)")
top(ax, 1); sign(fig); fig.tight_layout(); fig.savefig("out/fig4_distance.png"); plt.close(fig)
print("charts ok")
