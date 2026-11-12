"""Plain Excel-style charts for the Hwange air quality case study (legends above the plot)."""
import json
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "mathtext.default": "regular"})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/stats.json"))
GAS = {"no2": "NO$_2$", "so2": "SO$_2$"}
UNIT = "µmol/m²"


def style(ax):
    ax.grid(axis="y", color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)


def sign(fig): fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
def save(fig, name): sign(fig); fig.tight_layout(); fig.savefig(f"out/{name}.png"); plt.close(fig)


# Figure 1: monthly source enhancement (zone minus background ring), Hwange vs Maamba, with Unit 7 and 8 dates
fig, axs = plt.subplots(2, 1, figsize=(8.5, 6.0), dpi=200, sharex=True)
for ax, g in zip(axs, ("no2", "so2")):
    style(ax); m = S[g]["monthly"]; x = np.arange(len(m["m"]))
    ax.axvspan(48 - 0.5, 59.5, color="#f2f2f2", zorder=0, label="2023 (commissioning year, excluded)")
    ax.axhline(0, color="#7f7f7f", lw=0.6)
    ax.plot(x, m["hwange"], color=ORANGE, lw=1.4, label="Hwange (15 km round the power station)")
    ax.plot(x, m["maamba"], color=BLUE, lw=1.2, label="Maamba control (15 km round the power station)")
    for i in (50, 53): ax.axvline(i, color="#404040", lw=0.7)
    if g == "no2":
        ax.text(49.3, 29, "Unit 7\nsynchronised", fontsize=7, va="top", ha="right", color="#404040")
        ax.text(53.7, 29, "Units 7 and 8\nat full load", fontsize=7, va="top", color="#404040")
    ax.set_ylabel(f"{GAS[g]} above background ({UNIT})")
    ax.set_xticks(np.arange(0, len(x), 12)); ax.set_xticklabels([s[:4] for s in m["m"][::12]])
    ax.set_xlim(-1, len(x))
axs[0].legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8)
save(fig, "fig1_monthly")

# Figure 2: annual mean enhancement at Hwange by year
fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.9), dpi=200)
yrs = [str(y) for y in range(2019, 2026)]
col = [BLUE] * 4 + [GREY] + [ORANGE] * 2
for ax, g in zip(axs, ("no2", "so2")):
    style(ax); v = [S[g]["hwange"]["annual"][y] for y in yrs]
    ax.bar(yrs, v, 0.7, color=col, zorder=3)
    for i, b in enumerate(v): ax.text(i, b + max(v) * 0.015, f"{b:.1f}", ha="center", fontsize=7.5)
    ax.set_ylim(0, max(v) * 1.15); ax.set_ylabel(f"{GAS[g]} above background ({UNIT})")
    ax.tick_params(axis="x", labelsize=8)
h = [mpl.patches.Patch(color=c) for c in (BLUE, GREY, ORANGE)]
fig.legend(h, ["Before Units 7 and 8 (2019 to 2022)", "Commissioning (2023)", "After (2024 to 2025)"], frameon=False,
           loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8.5)
sign(fig); fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig("out/fig2_annual.png"); plt.close(fig)

# Figure 3: seasonal cycle of Hwange NO2 enhancement (before and after) and fire activity within 80 km
m = S["no2"]["monthly"]; mm = np.array([int(s[5:]) for s in m["m"]]); yy = np.array([int(s[:4]) for s in m["m"]])
e = np.array(m["hwange"], float)
pre = [np.nanmean(e[(mm == k) & (yy <= 2022)]) for k in range(1, 13)]
post = [np.nanmean(e[(mm == k) & (yy >= 2024)]) for k in range(1, 13)]
fig, ax = plt.subplots(figsize=(8.5, 4.0), dpi=200); style(ax)
mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ax2 = ax.twinx(); ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color("#7f7f7f"); ax2.spines["right"].set_linewidth(0.6)
ax2.bar(mon, S["fire_clim"], 0.6, color="#e6e6e6", zorder=1, label="Fire pixels within 80 km (monthly mean, right axis)")
ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
ax.plot(mon, pre, color=BLUE, lw=1.8, marker="o", ms=4, label="Hwange NO$_2$ enhancement, 2019 to 2022")
ax.plot(mon, post, color=ORANGE, lw=1.8, marker="o", ms=4, label="Hwange NO$_2$ enhancement, 2024 to 2025")
ax.set_ylabel(f"NO$_2$ above background ({UNIT})"); ax2.set_ylabel("Fire pixels (count)")
ax.set_ylim(0, max(post) * 1.2)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8)
save(fig, "fig3_season")

# Figure 4: people living where the NO2 column is 1.5 and 2 times the background
x = S["exposure"]; lab = ["Above 1.5 × background", "Above 2 × background"]; k = ["x1.5", "x2"]
fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=200); style(ax); xx = np.arange(2)
for i, (p, c, t) in enumerate((("pre", BLUE, "2019 to 2022"), ("post", ORANGE, "2024 to 2025"))):
    v = [x[p][q] for q in k]; xs = xx - 0.18 + 0.36 * i
    ax.bar(xs, v, 0.36, color=c, label=t, zorder=3)
    for a, b in zip(xs, v): ax.text(a, b + 500, f"{b:,.0f}".replace(",", " "), ha="center", fontsize=8)
ax.set_xticks(xx); ax.set_xticklabels(lab); ax.set_ylabel("People (WorldPop 2020)"); ax.set_ylim(0, 45000)
ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5)
save(fig, "fig4_exposure")
print("charts ok")
