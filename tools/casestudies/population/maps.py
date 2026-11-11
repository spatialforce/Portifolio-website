"""Five maps for case study 1: population distribution, density and growth in Zimbabwe (2012 and 2022 censuses).
Run with PROJ_LIB set to rasterio's proj_data (see .projlib). Output: out/*.png"""
import os, zipfile
import numpy as np, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.colors import LightSource, BoundaryNorm, ListedColormap, LogNorm
from matplotlib.patches import Patch, Rectangle
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
ASPECT = 1 / np.cos(np.radians(19))
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
LK = "../../corridors/raw/ne_10m_lakes.zip"
world = gpd.read_file(f"zip://{NE}").cx[20:38, -26:-12]
lakes = gpd.read_file(f"zip://{LK}").cx[25:33.2, -22.6:-15.4]
prov = gpd.read_file("raw/bnd/zwe_admin1.shp")
dist = gpd.read_file("data/districts.gpkg")
zwe = gpd.read_file("raw/bnd/zwe_admin0.shp")
SADC = ["AGO", "BWA", "COM", "COD", "SWZ", "LSO", "MDG", "MWI", "MUS", "MOZ", "NAM", "SYC", "ZAF", "TZA", "ZMB", "ZWE"]
africa = gpd.read_file(f"zip://{NE}").cx[5:60, -40:10]
AUTHOR = "© Kudzanai Chakavarika"
CITIES = [("Harare", 31.052, -17.829), ("Bulawayo", 28.583, -20.150), ("Mutare", 32.670, -18.970), ("Gweru", 29.817, -19.450),
          ("Kwekwe", 29.815, -18.928), ("Masvingo", 30.833, -20.074), ("Kadoma", 29.915, -18.333), ("Chinhoyi", 30.199, -17.367),
          ("Hwange", 26.500, -18.364), ("Victoria Falls", 25.840, -17.932), ("Beitbridge", 30.000, -22.217),
          ("Kariba", 28.800, -16.517), ("Marondera", 31.551, -18.185), ("Bindura", 31.330, -17.302), ("Gwanda", 29.000, -20.940),
          ("Chiredzi", 31.667, -21.050), ("Chipinge", 32.623, -20.188), ("Zvishavane", 30.067, -20.333)]


# Layout: map frame on the left, a side column on the right for the legend (or colour bar) and the Harare
# enlargement, so nothing is drawn on top of the map. The title sits inside the map at the top centre.
EXT = (25.0, 33.2, -22.6, -14.85)
MAIN = [0.035, 0.07, 0.60, 0.88]
TY = 0.965          # vertical position of the title inside the map (axes fraction)
GAP = 0.03          # gap between the two equal boxes in the side column


def frame(title, dark=False, size=(11.6, 8.6), top=EXT[3]):
    fig = plt.figure(figsize=size, dpi=220); ax = fig.add_axes(MAIN)
    fg = "#dddddd" if dark else "#222222"; bg = "black" if dark else "white"
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg if dark else "#f4f4f4")
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], top); ax.set_aspect(ASPECT, anchor="W")
    ax.set_xticks(range(26, 34)); ax.set_yticks(range(-22, -14))
    ax.set_xticklabels([f"{x}°E" for x in range(26, 34)], color=fg); ax.set_yticklabels([f"{-y}°S" for y in range(-22, -14)], color=fg)
    ax.grid(color="#555555" if dark else "#bbbbbb", lw=0.3, ls=":"); ax.tick_params(length=2, colors=fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color=fg, zorder=50)
    # north arrow in the top-left corner, its tip level with the middle of the title
    yt = EXT[2] + TY * (top - EXT[2])
    ax.annotate("", xy=(25.3, yt), xytext=(25.3, yt - 0.5), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=fg, lw=1.2), zorder=20)
    ax.text(25.3, yt - 0.55, "N", ha="center", va="top", fontsize=10, fontweight="bold", color=fg, zorder=20)
    # attribution in the empty lower-right corner
    ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#999999" if dark else "#777777", zorder=50)
    return fig, ax, fg


def side(fig, ax):
    """Left edge of the side column, just right of the drawn map."""
    fig.canvas.draw(); p = ax.get_position()
    return p.x1 + 0.025, p.y0, p.y1


def boxes(fig, ax):
    """Two boxes of equal size in the side column: [upper, lower] as [x, y, w, h]."""
    x, y0, y1 = side(fig, ax); h = (y1 - y0 - GAP) / 2; w = 0.98 - x
    return [x, y0 + h + GAP, w, h], [x, y0, w, h]


def legend_side(fig, ax, handles, title, fg="#222222"):
    up, _ = boxes(fig, ax)
    la = fig.add_axes(up); la.set_xticks([]); la.set_yticks([]); la.set_facecolor("none")
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    leg = la.legend(handles=handles, title=title, loc="upper left", fontsize=10.5, title_fontsize=11, frameon=False,
                    borderaxespad=0.8, alignment="left", labelcolor=fg, handlelength=2.4, handleheight=1.5, labelspacing=0.9)
    leg.get_title().set_fontweight("bold")
    leg.get_title().set_color(fg)
    return la


def colorbar_side(fig, ax, sm, label, fg="#222222"):
    up, _ = boxes(fig, ax)
    h = up[3] * 0.86; yb = up[1] + (up[3] - h) / 2
    ca = fig.add_axes([up[0] + up[2] / 2 - 0.035, yb, 0.026, h])
    cb = fig.colorbar(sm, cax=ca); cb.set_label(label, color=fg, fontsize=10.5, fontweight="bold"); ca.tick_params(labelsize=9.5); cb.outline.set_edgecolor(fg); cb.outline.set_linewidth(0.5)
    ca.yaxis.set_tick_params(color=fg); plt.setp(ca.get_yticklabels(), color=fg)


def furniture(ax, fg, source):
    # scale bar and north arrow in the empty lower-left corner (Botswana), clear of Zimbabwe
    km = 111.32 * np.cos(np.radians(22)); L = 200 / km; x0, y0 = 25.3, -22.35
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.07, fc=fg if i % 2 == 0 else ("black" if fg != "#222222" else "white"), ec=fg, lw=0.6, zorder=20))
    for v, x in [(0, x0), (100, x0 + L / 2), (200, x0 + L)]:
        ax.text(x, y0 + 0.12, f"{v}", ha="center", va="bottom", fontsize=7, color=fg, zorder=20)
    ax.text(x0 + L + 0.08, y0 + 0.03, "km", fontsize=7, color=fg, va="center", zorder=20)
    ax.text(0, -0.055, source, transform=ax.transAxes, fontsize=6.5, color=fg, ha="left", va="top", wrap=True)


def neighbours(ax, fc="#e0e0e0", ec="#ffffff", lw=0.6):
    world.plot(ax=ax, fc=fc, ec=ec, lw=lw, zorder=1)


def labels_countries(ax, color="#888888"):
    for n, x, y in [("ZAMBIA", 27.6, -16.3), ("MOZAMBIQUE", 32.45, -16.0), ("BOTSWANA", 26.3, -20.9), ("SOUTH AFRICA", 30.8, -22.45)]:
        ax.text(x, y, n, fontsize=7, color=color, ha="center", style="italic", zorder=15)


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved", name)


def hillshade():
    with rasterio.open("rast/dem.tif") as s:
        z = s.read(1).astype(float); b = s.bounds
    ls = LightSource(azdeg=315, altdeg=40)
    dx = (b.right - b.left) / z.shape[1] * 111320 * np.cos(np.radians(19)); dy = (b.top - b.bottom) / z.shape[0] * 111320
    hs = ls.hillshade(z, vert_exag=6, dx=dx, dy=dy)
    return z, hs, (b.left, b.right, b.bottom, b.top)


def clip_mask(shape, extent, geoms):
    from rasterio.features import geometry_mask
    T = rasterio.transform.from_bounds(extent[0], extent[2], extent[1], extent[3], shape[1], shape[0])
    return geometry_mask(geoms, out_shape=shape, transform=T, invert=True)


# 1 Study area
def map1():
    z, hs, ext = hillshade()
    inside = clip_mask(z.shape, ext, zwe.geometry)
    fig, ax, fg = frame("Study Area Map")
    cmap = plt.get_cmap("gist_earth")
    norm = mpl.colors.Normalize(200, 2600)
    rgb = cmap(norm(z))[..., :3]
    ls = LightSource(azdeg=315, altdeg=40)
    shaded = ls.blend_overlay(rgb, hs[..., None]) if hasattr(ls, "blend_overlay") else rgb * (0.45 + 0.55 * hs[..., None])
    grey = np.full(shaded.shape, 0xe0 / 255)  # flat grey outside Zimbabwe, same as the frame background
    img = np.where(inside[..., None], shaded, grey)
    ax.imshow(img, extent=ext, zorder=0, interpolation="bilinear")
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_facecolor("#e0e0e0")
    lakes.plot(ax=ax, fc="#a9c8e0", ec="none", zorder=2)
    world.boundary.plot(ax=ax, color="#ffffff", lw=0.7, zorder=3)
    prov.boundary.plot(ax=ax, color="#333333", lw=0.5, ls="--", zorder=4)
    zwe.boundary.plot(ax=ax, color="#111111", lw=1.0, zorder=5)
    for n, x, y in CITIES:
        big = n in ("Harare", "Bulawayo")
        ax.plot(x, y, "s" if big else "o", ms=5 if big else 3, mfc="white", mec="black", mew=0.7, zorder=6)
        ax.text(x + 0.07, y + 0.05, n, fontsize=8 if big else 7, fontweight="bold" if big else "normal", zorder=6,
                path_effects=[mpl.patheffects.withStroke(linewidth=2, foreground="white")])
    for _, r in prov.iterrows():
        c = r.geometry.representative_point(); n = r.adm1_name
        if n in ("Harare", "Bulawayo"): continue
        ax.text(c.x, c.y - 0.25, n.upper(), fontsize=6.5, color="#333333", ha="center", zorder=6, style="italic",
                path_effects=[mpl.patheffects.withStroke(linewidth=1.5, foreground="white")])
    labels_countries(ax, "#555555")
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap); zc = cmap(0.45)
    colorbar_side(fig, ax, sm, "Elevation (m)")
    locator(fig, ax, zc=zc)
    furniture(ax, fg, "Source: Copernicus GLO-30 DEM (resampled to 500 m); boundaries OCHA COD-AB 2023; Natural Earth. Geographic coordinates, WGS 84.")
    save(fig, "map1_study_area")


# 2 Dark glow population
def map2():
    with rasterio.open("rast/pop2022_300m.tif") as s:
        p = s.read(1); b = s.bounds; res = s.res
    cell_km2 = (res[0] * 111.32 * np.cos(np.radians(19))) * (res[1] * 110.57)
    d = p / cell_km2
    d = np.ma.masked_less(d, 1)
    fig, ax, fg = frame("Population Density Map (2022)", dark=True)
    world.plot(ax=ax, fc="#0b0b0b", ec="#333333", lw=0.5, zorder=1)
    zwe.plot(ax=ax, fc="#111111", ec="none", zorder=1.5)
    norm = LogNorm(1, 10000)
    ax.imshow(d, extent=(b.left, b.right, b.bottom, b.top), cmap="inferno", norm=norm, zorder=2, interpolation="nearest")
    prov.boundary.plot(ax=ax, color="#444444", lw=0.35, zorder=3)
    zwe.boundary.plot(ax=ax, color="#888888", lw=0.6, zorder=3)
    for n, x, y in CITIES[:6] + [CITIES[8]]:
        ax.text(x + 0.1, y + 0.08, n, fontsize=7, color="#dddddd", zorder=6)
    colorbar_side(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap="inferno"), "People per km²", fg)
    locator(fig, ax, dark=True, zc=plt.get_cmap("inferno")(0.75))
    furniture(ax, fg, "Source: WorldPop 2020 constrained 100 m grid, rescaled to ZimStat 2022 census district totals (dasymetric); cells under 1 person per km² left black.")
    save(fig, "map2_density_grid")


def classed(fig, ax, col, bins, colors, labels, title_leg):
    cmap = ListedColormap(colors); norm = BoundaryNorm(bins, cmap.N)
    dist.plot(ax=ax, column=col, cmap=cmap, norm=norm, ec="#ffffff", lw=0.3, zorder=2)
    prov.boundary.plot(ax=ax, color="#222222", lw=0.6, zorder=3)
    counts = np.histogram(dist[col], bins=bins)[0]
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=f"{l}  ({n})") for c, l, n in zip(colors, labels, counts)]
    legend_side(fig, ax, hs, title_leg + "\n(number of districts)")
    return cmap, norm


def locator(fig, ax, dark=False, zc="#c0392b"):
    """Small map of SADC at the bottom of the side column, Zimbabwe highlighted."""
    _, lo = boxes(fig, ax)
    la = fig.add_axes(lo)
    sea, other, member, ec = ("#000000", "#1a1a1a", "#3a3a3a", "#000000") if dark else ("#ffffff", "#f0f0f0", "#cfcfcf", "#ffffff")
    la.set_facecolor(sea)
    africa.plot(ax=la, fc=other, ec=ec, lw=0.3)
    africa[africa.ADM0_A3.isin(SADC)].plot(ax=la, fc=member, ec=ec, lw=0.3)
    africa[africa.ADM0_A3 == "ZWE"].plot(ax=la, fc=mpl.colors.to_hex(zc), ec="none")
    la.set_xlim(9, 52); la.set_ylim(-36, 6); la.set_aspect(1 / np.cos(np.radians(15)), adjustable="datalim")
    la.set_xticks([]); la.set_yticks([])
    fg = "#dddddd" if dark else "#222222"
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    # header strip so the title never sits on the land
    la.add_patch(Rectangle((0, 0.88), 1, 0.12, transform=la.transAxes, fc=sea, ec="none", zorder=5))
    la.plot([0, 1], [0.88, 0.88], transform=la.transAxes, color=fg, lw=0.6, zorder=6)
    la.text(0.5, 0.94, "SADC", transform=la.transAxes, ha="center", va="center", fontsize=11, fontweight="bold", color=fg, zorder=7)


# 3 District density
def map3():
    fig, ax, fg = frame("Population Density By District Map (2022)")
    neighbours(ax)
    bins = [0, 15, 25, 50, 100, 500, 1500, 10000]
    cols = ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"]
    labs = ["Under 15", "15 to 25", "25 to 50", "50 to 100", "100 to 500", "500 to 1 500", "Over 1 500"]
    cmap, norm = classed(fig, ax, "dens2022", bins, cols, labs, "People per km²")
    labels_countries(ax)
    locator(fig, ax, zc=cols[-2])
    furniture(ax, fg, "Source: ZimStat 2022 Population and Housing Census, preliminary district totals; district areas computed in Africa Albers Equal Area from OCHA COD-AB boundaries.")
    save(fig, "map3_density_district")


# 4 Growth
def map4():
    fig, ax, fg = frame("Population Growth By District Map (2012–2022)")
    neighbours(ax)
    bins = [-5, 0, 0.5, 1, 1.5, 2, 3, 5, 20]
    cols = ["#4393c3", "#f7f7f7", "#fddbc7", "#f4a582", "#e7745b", "#d6604d", "#b2182b", "#67001f"]
    labs = ["Decline", "0 to 0.5", "0.5 to 1.0", "1.0 to 1.5", "1.5 to 2.0", "2.0 to 3.0", "3.0 to 5.0", "Over 5.0"]
    cmap, norm = classed(fig, ax, "growth", bins, cols, labs, "Growth (% per year)")
    labels_countries(ax)
    locator(fig, ax, zc=cols[-2])
    furniture(ax, fg, "Source: ZimStat 2012 and 2022 censuses (2012 district totals as compiled by citypopulation.de); exponential growth rate, 2012 district boundaries matched by name.")
    save(fig, "map4_growth")


# 5 Sex ratio
def map5():
    fig, ax, fg = frame("Sex Ratio By District Map (2022)")
    neighbours(ax)
    bins = [0, 86, 90, 94, 98, 102, 200]
    cols = ["#542788", "#8073ac", "#b2abd2", "#e5e1ef", "#f7f7f7", "#e08214"]
    labs = ["Under 86", "86 to 90", "90 to 94", "94 to 98", "98 to 102", "Over 102"]
    cmap, norm = classed(fig, ax, "sexratio", bins, cols, labs, "Males per 100 females")
    labels_countries(ax)
    locator(fig, ax, zc=cols[0])
    furniture(ax, fg, "Source: ZimStat 2022 Population and Housing Census, preliminary report, male and female totals by district. National ratio 92.")
    save(fig, "map5_sex_ratio")


if __name__ == "__main__":
    import matplotlib.patheffects  # noqa
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5"]): globals()[f]()
