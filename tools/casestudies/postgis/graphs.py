"""Plain Excel-style charts for the Harare walking access study (legends above the plot, no titles). Run after analysis.py."""
import json
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np
mpl.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#4472C4", "#ED7D31", "#A5A5A5"
S = json.load(open("out/stats.json")); A, B = S["scen"]["A"], S["scen"]["B"]
LEG = dict(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
NA = f"Listed public facilities only ({A['n_fac']})"; NB = f"All mapped clinics and hospitals ({B['n_fac']})"


def style(ax, axis="y"):
    ax.grid(axis=axis, color="#d9d9d9", lw=0.6); ax.set_axisbelow(True)
    for s in ("left", "bottom"): ax.spines[s].set_color("#7f7f7f"); ax.spines[s].set_linewidth(0.6)


def save(fig, name):
    fig.text(0.99, 0.01, "© Kudzanai Chakavarika", ha="right", va="bottom", fontsize=7, color="#777777")
    fig.tight_layout(); fig.savefig(f"out/{name}.png", dpi=200); plt.close(fig); print("saved", name)


# Figure 1: share of people in each walking distance band
x = np.arange(5); wd = 0.36
fig, ax = plt.subplots(figsize=(8.0, 3.8)); style(ax)
for j, (s, col, lab) in enumerate([(A, GREY, NA), (B, BLUE, NB)]):
    b = ax.bar(x + (j - 0.5) * wd, [v["pct"] for v in s["bands"]], wd, color=col, label=lab); ax.bar_label(b, fmt="%.1f", fontsize=7, padding=1)
ax.set_xticks(x); ax.set_xticklabels(["Under 1 km", "1 to 2 km", "2 to 3 km", "3 to 5 km", "Over 5 km"])
ax.set_ylabel("Share of people (%)"); ax.set_xlabel("Walking distance to the nearest facility"); ax.set_ylim(0, 50)
ax.legend(ncol=2, **LEG)
save(fig, "fig1_bands")

# Figure 2: cumulative share of people within a given walk
fig, ax = plt.subplots(figsize=(8.0, 3.8)); style(ax, "both")
for s, col, lab in [(A, GREY, NA), (B, BLUE, NB)]:
    ax.plot([c["km"] for c in s["cum"]], [c["pct"] for c in s["cum"]], color=col, lw=1.8, label=lab)
for k in (2, 5): ax.axvline(k, color="#7f7f7f", lw=0.8, ls="--")
ax.set_xlim(0, 12); ax.set_ylim(0, 100); ax.set_xticks(range(0, 13))
ax.set_xlabel("Walking distance (km)"); ax.set_ylabel("People within this distance (%)")
ax.legend(ncol=2, **LEG)
save(fig, "fig2_cumulative")

# Figure 3: people per facility catchment, all mapped facilities, largest first
ld = B["load"]; v = [d["pop"] / 1000 for d in ld]
fig, ax = plt.subplots(figsize=(8.0, 3.6)); style(ax)
ax.bar(range(len(v)), v, color=[ORANGE if d["kind"] == "Hospital" else BLUE for d in ld], width=0.8)
ax.axhline(B["load_median"] / 1000, color="#444444", lw=0.8, ls="--")
ax.text(len(v) - 1, B["load_median"] / 1000 + 3, f"Median {B['load_median'] / 1000:.1f} thousand", ha="right", fontsize=8)
ax.set_xlim(-1, len(v)); ax.set_xticks([]); ax.set_xlabel("Facilities, ranked by people in their walking catchment")
ax.set_ylabel("People (thousands)")
ax.legend(handles=[mpl.patches.Patch(color=BLUE, label="Clinics"), mpl.patches.Patch(color=ORANGE, label="Hospitals")], ncol=2, **LEG)
save(fig, "fig3_load")

# Figure 4: people newly within 2 km as new clinics are added one at a time
p = S["sites"]["picks"]
fig, ax = plt.subplots(figsize=(8.0, 3.6)); style(ax)
b = ax.bar([d["step"] for d in p], [d["gain"] / 1000 for d in p], color=BLUE, width=0.6, label="Added by this site")
ax.bar_label(b, fmt="%.1f", fontsize=7, padding=1)
ax.plot([d["step"] for d in p], [d["cum"] / 1000 for d in p], color=ORANGE, marker="o", ms=4, lw=1.6, label="Running total")
ax.set_xticks([d["step"] for d in p]); ax.set_xlabel("New clinic (order of choice)"); ax.set_ylabel("People brought within 2 km (thousands)")
ax.set_ylim(0, max(d["cum"] for d in p) / 1000 * 1.12)
ax.legend(ncol=2, **LEG)
save(fig, "fig4_sites")
