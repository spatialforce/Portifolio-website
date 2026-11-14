"""Maps for the Harare walking access study (PostGIS and pgRouting results exported by export.sh).
UTM 36S (EPSG:32736) with degree ticks on all four sides; framed title strip above each map; outer frame round the page.
Run from this folder after analysis.py. Output: out/*.png"""
import os, json
import numpy as np, pandas as pd, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
from pyproj import Transformer
from shapely import wkt

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; FG = "#222222"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
TO = Transformer.from_crs(4326, 32736, always_xy=True); FROM = Transformer.from_crs(32736, 4326, always_xy=True)
ST = json.load(open("out/stats.json"))


def gdf(name):
    d = pd.read_csv(f"exp/{name}.csv"); return gpd.GeoDataFrame(d.drop(columns="wkt"), geometry=d.wkt.map(wkt.loads), crs=32736)


PROV = gdf("province"); WARD = gdf("ward"); ROAD = gdf("roads")
FAC = pd.read_csv("exp/fac.csv"); CELL = pd.read_csv("exp/cell.csv"); PLACE = pd.read_csv("exp/place.csv")
ZW = gpd.read_file("../population/raw/bnd/zwe_admin1.shp").to_crs(32736)
WARD["auth"] = WARD.name.str.replace(r" \d+$", "", regex=True)
AUTHS = WARD.assign(geometry=WARD.buffer(5)).dissolve("auth").reset_index(); AUTHS["geometry"] = AUTHS.buffer(-5)  # buffer closes slivers between simplified wards
x0, y0, x1, y1 = PROV.total_bounds; PX = 2500
HH = y1 - y0 + 2 * PX  # landscape frame: province on the left, legend and locator in the open space on the right
WW = 1.35 * HH; LM = 9000  # left margin so the province sits nearer the centre
EXT = (x0 - LM, x0 - LM + WW, y0 - PX, y1 + PX)
FACE = "#f1f1f1"

# ---- cell values on a 100 m UTM grid (nearest from the native WorldPop grid) -----------------
with rasterio.open("data/pop_harare.tif") as r:
    src_t, src_crs, shp = r.transform, r.crs, r.shape
col = np.floor((CELL.lon - src_t.c) / src_t.a).astype(int); row = np.floor((CELL.lat - src_t.f) / src_t.e).astype(int)
RES = 100; GT = from_origin(EXT[0], EXT[3], RES, RES); GW, GH = int((EXT[1] - EXT[0]) / RES), int((EXT[3] - EXT[2]) / RES)
GX = (EXT[0], EXT[0] + GW * RES, EXT[3] - GH * RES, EXT[3])


def grid(values):
    a = np.full(shp, np.nan, np.float32); a[row, col] = values
    o = np.full((GH, GW), np.nan, np.float32)
    reproject(a, o, src_transform=src_t, src_crs=src_crs, dst_transform=GT, dst_crs="EPSG:32736",
              resampling=Resampling.nearest, src_nodata=np.nan, dst_nodata=np.nan)
    return o


def u(lon, lat): return TO.transform(lon, lat)


def ticks(ax, ext, step=0.1, fs=8):
    xm, ym = (ext[0] + ext[1]) / 2, (ext[2] + ext[3]) / 2; lom, lam = FROM.transform(xm, ym)
    lo0, _ = FROM.transform(ext[0], ym); lo1, _ = FROM.transform(ext[1], ym); _, la0 = FROM.transform(xm, ext[2]); _, la1 = FROM.transform(xm, ext[3])
    lons = np.arange(np.ceil(lo0 / step - 1e-9) * step, lo1, step); lats = np.arange(np.ceil(la0 / step - 1e-9) * step, la1, step)
    ax.set_xticks([u(l, lam)[0] for l in lons]); ax.set_xticklabels([f"{l:.1f}°E" for l in lons], fontsize=fs)
    ax.set_yticks([u(lom, l)[1] for l in lats]); ax.set_yticklabels([f"{-l:.1f}°S" for l in lats], fontsize=fs)
    ax.tick_params(length=2.5, top=True, right=True, labeltop=True, labelright=True, colors=FG)
    ax.tick_params(axis="y", labelrotation=90)
    plt.setp(ax.yaxis.get_ticklabels(), va="center")


def header(fig, ax, title, fs=13, h=0.04, gap=0.006):
    """Framed title strip directly above the map frame (clear of the top coordinates), same width as the map."""
    ax.apply_aspect(); p = ax.get_position()
    fig.canvas.draw(); tb = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    hx = fig.add_axes([p.x0, max(p.y1, tb.y1) + gap, p.width, h]); hx.set_xticks([]); hx.set_yticks([]); hx.set_facecolor("white")
    for s_ in hx.spines.values(): s_.set_color(FG); s_.set_linewidth(0.8)
    hx.text(0.5, 0.5, title, ha="center", va="center", fontsize=fs, fontweight="bold", color=FG)
    return hx


def narrow(ax, x, y, h=0.07):
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0_ = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, FG), (w, "white")):
        ax.add_patch(Polygon([(x, y), (x + xs, y0_), notch], closed=True, fc=fc, ec=FG, lw=0.9, transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0_ - 0.006, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11, fontweight="bold", color=FG, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground="white")])


def scalebar(ax, ext, km, x=0.03, y=0.035, fs=8.5):
    L = km * 1000; xa = ext[0] + x * (ext[1] - ext[0]); ya = ext[2] + y * (ext[3] - ext[2]); t = (ext[3] - ext[2]) * 0.01
    for i in range(4):
        ax.add_patch(Rectangle((xa + i * L / 4, ya), L / 4, t, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=70))
    for v, xx in [(0, xa), (km / 2, xa + L / 2), (km, xa + L)]:
        ax.text(xx, ya + t * 1.6, f"{v:g}", ha="center", va="bottom", fontsize=fs, zorder=70, path_effects=HALO)
    ax.text(xa + L + (ext[1] - ext[0]) * 0.01, ya + t / 2, "km", fontsize=fs, va="center", zorder=70, path_effects=HALO)


def legend_in(ax, handles, title, fs=10, at=(0.985, 0.06)):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=at, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=FG, facecolor="white", framealpha=1, borderpad=0.7, alignment="left",
                    handlelength=2.0, handleheight=1.1, labelspacing=0.45)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.set_zorder(90)
    ax.text(at[0], 0.008, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=90)
    return leg


def source(ax, text, y=-0.05):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.5, ha="left", va="top", wrap=True)


def save(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def frame(title, wd=10.5, arrow=(0.965, 0.975)):
    asp = (EXT[1] - EXT[0]) / (EXT[3] - EXT[2])
    ht = wd * 0.86 / asp / 0.84
    fig = plt.figure(figsize=(wd, ht), dpi=200); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.07, 0.07, 0.86, 0.84]); ax.set_facecolor(FACE)
    ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(1); ticks(ax, EXT)
    for s_ in ax.spines.values(): s_.set_color(FG); s_.set_linewidth(0.8)
    header(fig, ax, title); narrow(ax, *arrow)
    return fig, ax


def outline(ax, lw=0.8, wards=True):
    if wards: WARD.boundary.plot(ax=ax, color="#cfcfcf", lw=0.3, zorder=6)
    AUTHS.boundary.plot(ax=ax, color="#9a9a9a", lw=0.5, zorder=7)
    PROV.boundary.plot(ax=ax, color="#555555", lw=0.8, zorder=8)


def roads(ax, lw=0.5, color="#5a5a5a"):
    ROAD[ROAD.highway.isin(["trunk", "primary"])].plot(ax=ax, color=color, lw=lw * 1.6, zorder=5)
    ROAD[ROAD.highway.isin(["secondary"])].plot(ax=ax, color=color, lw=lw, zorder=5)


def facs(ax, sc, ms=4.2):
    f = FAC[FAC.scen == sc]
    for k, m in (("Clinic", "o"), ("Hospital", "s")):
        g = f[f.kind == k]; ax.plot(g.x, g.y, m, ms=ms if k == "Clinic" else ms + 0.6, mfc="white" if k == "Clinic" else FG,
                                    mec=FG, mew=0.8, ls="none", zorder=30)


def fac_handles(ms=5):
    return [Line2D([], [], ls="none", marker="o", ms=ms, mfc="white", mec=FG, label="Clinics"),
            Line2D([], [], ls="none", marker="s", ms=ms, mfc=FG, mec=FG, label="Hospitals")]


LABELS = ["Harare", "Chitungwiza", "Epworth", "Mbare", "Highfield", "Glen View", "Budiriro", "Kuwadzana", "Dzivarasekwa",
          "Mabvuku", "Tafara", "Borrowdale", "Hatcliffe", "Waterfalls", "Mufakose", "Warren Park", "Caledonia", "Southlea Park",
          "Avondale", "Greendale", "Hopley", "Mount Pleasant"]


def places(ax, sel=None, fs=7.5):
    for _, p in PLACE.iterrows():
        if p["name"] not in (sel or LABELS): continue
        big = p["name"] in ("Harare", "Chitungwiza", "Epworth")
        ax.text(p.x, p.y, p["name"], fontsize=fs + (1.5 if big else 0), fontweight="bold" if big else "normal", ha="center", va="center",
                zorder=40, path_effects=HALO, style="normal" if big else "italic")


def locator(ax, box=(0.745, 0.64, 0.24, 0.33)):
    la = ax.inset_axes(list(box)); la.set_zorder(85); la.set_facecolor("white")
    ZW.plot(ax=la, fc="#e3e3e3", ec="white", lw=0.5); ZW[ZW.adm1_name == "Harare"].plot(ax=la, fc="#b30000", ec="#b30000", lw=1.5)
    bx0, by0, bx1, by1 = ZW.total_bounds; px, py = (bx1 - bx0) * 0.05, (by1 - by0) * 0.05
    la.set_xlim(bx0 - px, bx1 + px); la.set_ylim(by0 - py, by1 + py * 4.2); la.set_aspect(1, adjustable="datalim"); la.set_xticks([]); la.set_yticks([])
    for s_ in la.spines.values(): s_.set_color(FG); s_.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.85), 1, 0.15, transform=la.transAxes, fc="white", ec=FG, lw=0.6, zorder=5))
    la.text(0.5, 0.925, "Zimbabwe", transform=la.transAxes, ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=6)


def classes(arr, breaks, colours):
    rgba = np.zeros(arr.shape + (4,))
    for i, c in enumerate(colours):
        m = (arr >= breaks[i]) & (arr < breaks[i + 1]); rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    return rgba


# ---- map 1: study area ----------------------------------------------------------------------
AUTH_C = {"Harare": "#fbf3e4", "Harare Rural": "#e9eef7", "Chitungwiza": "#eaf4e6", "Epworth": "#f6e8ef"}


def map1():
    fig, ax = frame("Study Area and Health Facilities", arrow=(0.035, 0.975))
    for a, c in AUTH_C.items(): AUTHS[AUTHS.auth == a].plot(ax=ax, fc=c, ec="none", zorder=1)
    outline(ax); roads(ax, lw=0.45, color="#e2aaa8"); facs(ax, "B", ms=3.6)
    a = FAC[FAC.scen == "A"]; ax.plot(a.x, a.y, "D", ms=6.5, mfc="none", mec="#1f4e9c", mew=1.1, ls="none", zorder=31)
    places(ax, ["Harare", "Chitungwiza", "Epworth", "Mbare", "Borrowdale", "Hatcliffe", "Kuwadzana", "Budiriro", "Mabvuku", "Caledonia"])
    locator(ax)
    h = [Patch(fc=c, ec="#777777", lw=0.4, label=a) for a, c in AUTH_C.items()]
    h += [Line2D([], [], color="#e2aaa8", lw=1.0, label="Main roads")] + fac_handles(4.5)
    h += [Line2D([], [], ls="none", marker="D", ms=6, mfc="none", mec="#1f4e9c", mew=1.1, label="Listed public facilities"),
          Line2D([], [], color="#bdbdbd", lw=0.6, label="Wards")]
    legend_in(ax, h, "Local authority"); scalebar(ax, EXT, 10)
    source(ax, "Source: wards geoBoundaries (ADM3); roads and facilities OpenStreetMap (Geofabrik, 2026); public facilities Maina et al. (2019). UTM zone 36S (WGS 84).")
    save(fig, "map1_study_area")


# ---- maps 2 and 3: walking distance to the nearest facility ---------------------------------
DB = [0, 1000, 2000, 3000, 5000, 1e9]; DC = ["#1a9850", "#91cf60", "#fee08b", "#fc8d59", "#d73027"]
DN = ["< 1", "1 – 2", "2 – 3", "3 – 5", "> 5"]


def dist_map(sc, title, name, note):
    fig, ax = frame(title)
    ax.imshow(classes(grid(CELL[f"dist{sc.lower()}"].to_numpy()), DB, DC), extent=GX, zorder=2, interpolation="nearest")
    outline(ax); facs(ax, sc, ms=3.8 if sc == "B" else 5)
    places(ax, ["Harare", "Chitungwiza", "Epworth"], fs=8)
    h = [Patch(fc=c, ec="#777777", lw=0.4, label=l) for c, l in zip(DC, DN)] + fac_handles(4.5)
    legend_in(ax, h, "Walking distance (km)"); scalebar(ax, EXT, 10)
    source(ax, note)
    save(fig, name)


def map2():
    dist_map("B", "Walking Distance to the Nearest Mapped Facility", "map2_distance_all",
             f"Source: shortest walks on the OpenStreetMap network (pgRouting) from each populated 100 m cell (WorldPop 2025) to the nearest of {ST['scen']['B']['n_fac']} mapped clinics and hospitals. UTM zone 36S (WGS 84).")


def map3():
    dist_map("A", "Walking Distance to the Nearest Listed Public Facility", "map3_distance_public",
             "Source: as Map 2, with only the 27 public facilities of the master facility list (Maina et al., 2019) as destinations. UTM zone 36S (WGS 84).")


# ---- map 4: share of ward population beyond 2 km --------------------------------------------
WB = [0, 20, 40, 60, 80, 100.01]; WC = ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]
WN = ["< 20", "20 – 40", "40 – 60", "60 – 80", "> 80"]


def map4():
    fig, ax = frame("People More Than 2 km from a Facility, by Ward")
    w = WARD.merge(pd.DataFrame(ST["wards"])[["wid", "far_b"]], on="wid")
    for i, c in enumerate(WC):
        w[(w.far_b >= WB[i]) & (w.far_b < WB[i + 1])].plot(ax=ax, fc=c, ec="white", lw=0.3, zorder=2)
    outline(ax, wards=False); facs(ax, "B", ms=3.4)
    places(ax, ["Harare", "Chitungwiza", "Epworth"], fs=8)
    h = [Patch(fc=c, ec="#777777", lw=0.4, label=l) for c, l in zip(WC, WN)] + fac_handles(4.5)
    legend_in(ax, h, "People over 2 km away (%)"); scalebar(ax, EXT, 10)
    source(ax, "Source: this study; share of each ward's 2025 population whose shortest walk to a mapped clinic or hospital is longer than 2 km. UTM zone 36S (WGS 84).")
    save(fig, "map4_wards")


# ---- map 5: people per facility catchment ---------------------------------------------------
LB = [0, 10000, 20000, 40000, 80000, 1e9]; LC = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"]
LN = ["< 10 000", "10 000 – 20 000", "20 000 – 40 000", "40 000 – 80 000", "> 80 000"]


def map5():
    fig, ax = frame("People Served by Each Facility Catchment")
    load = {d["fid"]: d["pop"] for d in ST["scen"]["B"]["load"]}
    ax.imshow(classes(grid(CELL.fidb.map(load).to_numpy()), LB, LC), extent=GX, zorder=2, interpolation="nearest")
    # catchment edges: cells whose right or lower neighbour belongs to another facility
    fid = grid(CELL.fidb.to_numpy().astype(np.float32)); e = np.zeros(fid.shape, bool)
    e[:, :-1] |= (fid[:, :-1] != fid[:, 1:]) & ~np.isnan(fid[:, :-1]) & ~np.isnan(fid[:, 1:])
    e[:-1, :] |= (fid[:-1, :] != fid[1:, :]) & ~np.isnan(fid[:-1, :]) & ~np.isnan(fid[1:, :])
    ax.imshow(np.ma.masked_where(~e, e), extent=GX, cmap=ListedColormap(["#ffffff"]), zorder=3, interpolation="nearest", alpha=0.45)
    outline(ax, wards=False); facs(ax, "B", ms=3.4)
    places(ax, ["Harare", "Chitungwiza", "Epworth"], fs=8)
    h = [Patch(fc=c, ec="#777777", lw=0.4, label=l) for c, l in zip(LC, LN)] + fac_handles(4.5)
    legend_in(ax, h, "People in catchment"); scalebar(ax, EXT, 10)
    source(ax, "Source: this study; each populated cell is assigned to the facility it can reach by the shortest walk (network catchments, WorldPop 2025). UTM zone 36S (WGS 84).")
    save(fig, "map5_catchments")


# ---- map 6: five candidate clinic sites -----------------------------------------------------
def map6():
    fig, ax = frame("Candidate Sites for Five New Clinics")
    d = grid(CELL.distb.to_numpy())
    base = classes(d, DB, ["#e6e6e6", "#e6e6e6", "#a8a8a8", "#a8a8a8", "#a8a8a8"])
    ax.imshow(base, extent=GX, zorder=2, interpolation="nearest")
    cov = pd.read_csv("exp/cover.csv"); picks = ST["sites"]["picks"][:5]
    pc = ["#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
    done = set()
    for p, c in zip(picks, pc):
        cid = set(cov[cov.kid == p["kid"]].cid) - done; done |= cid
        g = grid(CELL.cid.isin(cid).astype(np.float32).to_numpy())
        ax.imshow(np.ma.masked_where(g != 1, g), extent=GX, cmap=ListedColormap([c]), zorder=3, interpolation="nearest", alpha=0.85)
    outline(ax, wards=False); facs(ax, "B", ms=3.4)
    for p, c in zip(picks, pc):
        ax.plot(p["x"], p["y"], "*", ms=15, mfc=c, mec=FG, mew=0.9, zorder=45)
        ax.text(p["x"] + 900, p["y"] + 500, str(p["step"]), fontsize=10, fontweight="bold", zorder=46, path_effects=HALO)
    places(ax, ["Harare", "Chitungwiza", "Epworth"], fs=8)
    h = [Line2D([], [], ls="none", marker="*", ms=11, mfc=c, mec=FG, label=f"{p['step']}  {p['near'].replace('St. ', 'St ')}") for p, c in zip(picks, pc)]
    h += [Patch(fc="#e6e6e6", ec="#777777", lw=0.4, label="Within 2 km"), Patch(fc="#a8a8a8", ec="#777777", lw=0.4, label="Over 2 km")] + fac_handles(4.5)
    legend_in(ax, h, "New clinic sites"); scalebar(ax, EXT, 10)
    source(ax, "Source: this study; greedy maximal coverage over 2 km walking catchments of candidate network nodes. Shaded areas are people newly brought within 2 km. UTM zone 36S (WGS 84).")
    save(fig, "map6_sites")


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "map6"]): globals()[f]()
