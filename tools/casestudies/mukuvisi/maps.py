"""Maps and graphs for the Mukuvisi catchment runoff study. Analysis grid: 30 m UTM 36S; maps drawn in geographic
coordinates (WGS 84) after resampling to 0.0003 degrees. Output: out/*.png"""
import os, sys, json
import numpy as np, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LightSource
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from rasterio.warp import reproject, Resampling
from affine import Affine
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"; FG = "#222222"; HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
EXT = (30.862, 31.292, -17.975, -17.764); LAT0 = -17.87; ASPECT = 1 / np.cos(np.radians(LAT0))
G = json.load(open("raw/grid.json")); TR = Affine(G["res"], 0, G["x0"], 0, -G["res"], G["y1"])
GR = 0.0003; GW, GH = round((EXT[1] - EXT[0]) / GR), round((EXT[3] - EXT[2]) / GR); GT = Affine(GR, 0, EXT[0], 0, -GR, EXT[3])
Z = np.load("data/grid.npz"); C = np.load("data/cn.npz")
catch = gpd.read_file("data/catchment.gpkg").to_crs(4326); sub = gpd.read_file("data/subcatch.gpkg").to_crs(4326)
streams = gpd.read_file("data/streams.gpkg").to_crs(4326); ms = gpd.read_file("data/mainstem.gpkg").to_crs(4326)
roads = gpd.read_file("raw/osm_roads.gpkg").to_crs(4326); main_rd = roads[roads.kind.str.replace("_link", "").isin(["motorway", "trunk", "primary"])]
rivers = gpd.read_file("raw/osm_rivers.gpkg").to_crs(4326)
dams = gpd.read_file("raw/osm_dams.gpkg").to_crs(4326); dams = dams[dams.geometry.type == "Polygon"]
BND = "../population/raw/bnd"
prov = gpd.read_file(f"{BND}/zwe_admin1.shp").to_crs(4326); har = prov[prov.adm1_name == "Harare"]
dist = gpd.read_file(f"{BND}/zwe_admin2.shp").to_crs(4326); hd = dist[dist.adm1_name == "Harare"]
NAMES = {1: "Greendale", 2: "Upper Mukuvisi", 3: "Eastlea–Highlands", 4: "Hatfield", 5: "City Centre", 6: "Glen Norah",
         7: "Waterfalls–Mbare", 8: "Glen View"}
_pl = gpd.read_file("raw/osm_places.gpkg")
SHOW = ["Mbare", "Highfield", "Glen View", "Glen Norah", "Waterfalls", "Hatfield", "Msasa", "Mabvuku", "Greendale", "Eastlea", "Epworth", "Braeside"]
PLACES = [(n, float(_pl[_pl.name == n].geometry.x.iloc[0]), float(_pl[_pl.name == n].geometry.y.iloc[0])) for n in SHOW if (_pl.name == n).any()]
PLACES += [("City Centre", 31.047, -17.829)]


def geo(a, how=Resampling.nearest):
    d = np.full((GH, GW), np.nan, "float32")
    reproject(a.astype("float32"), d, src_transform=TR, src_crs="EPSG:32736", dst_transform=GT, dst_crs="EPSG:4326", resampling=how, dst_nodata=np.nan)
    return d


M = geo(Z["catch"].astype("uint8")) > 0.5


def hillshade():
    dem = Z["dem"].astype(float)
    hs = LightSource(azdeg=315, altdeg=40).hillshade(dem, vert_exag=6, dx=G["res"], dy=G["res"])
    return geo(dem, Resampling.bilinear), geo(hs, Resampling.bilinear)


def axes_setup(ax, fs=9, face="#e6e6e6"):
    ax.set_facecolor(face); ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(ASPECT)
    xs = [30.9, 31.0, 31.1, 31.2]; ys = [-17.95, -17.9, -17.85, -17.8]
    ax.set_xticks(xs); ax.set_yticks(ys)
    ax.set_xticklabels([f"{x:.1f}°E" for x in xs], fontsize=fs)
    ax.set_yticklabels([f"{-y:.2f}°S" for y in ys], fontsize=fs, rotation=90, va="center")
    ax.tick_params(length=2)
    for sp in ax.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)


def north(ax, c=FG):
    x = EXT[0] + 0.014; yt = EXT[3] - 0.012
    ax.annotate("", xy=(x, yt), xytext=(x, yt - 0.02), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=c, lw=1.2), zorder=70)
    ax.text(x, yt - 0.022, "N", ha="center", va="top", fontsize=10, fontweight="bold", color=c, zorder=70)


def header(fig, ax, title, fs=13, h=0.052, gap=0.008):
    ax.apply_aspect(); p = ax.get_position()
    hx = fig.add_axes([p.x0, p.y1 + gap, p.width, h]); hx.set_xticks([]); hx.set_yticks([]); hx.set_facecolor("white")
    for sp in hx.spines.values(): sp.set_color(FG); sp.set_linewidth(0.8)
    hx.text(0.5, 0.5, title, ha="center", va="center", fontsize=fs, fontweight="bold", color=FG)


def frame(title, face="#e6e6e6", size=(12.4, 7.6)):
    fig = plt.figure(figsize=size, dpi=200); fig.patch.set_facecolor("white")
    ax = fig.add_axes([0.05, 0.08, 0.93, 0.82]); axes_setup(ax, face=face); header(fig, ax, title); north(ax)
    return fig, ax


def legend_in(ax, handles, title, fs=9.5, ncol=1, loc=(0.993, 0.05)):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=loc, fontsize=fs, title_fontsize=fs + 0.5,
                    frameon=True, fancybox=False, edgecolor=FG, facecolor="white", framealpha=1, borderpad=0.7, alignment="left", ncol=ncol,
                    handlelength=2.0, handleheight=1.1, labelspacing=0.55, columnspacing=1.2)
    leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold"); leg.set_zorder(90)
    ax.text(loc[0], 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#555555", zorder=90)


def scalebar(ax, L_km=5, fs=7.5):
    km = 111.32 * np.cos(np.radians(LAT0)); L = L_km / km; y = EXT[2] + 0.007; x0 = EXT[0] + 0.01
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y), L / 4, 0.0028, fc=FG if i % 2 == 0 else "white", ec=FG, lw=0.6, zorder=70))
    for v, x in [(0, x0), (L_km / 2, x0 + L / 2), (L_km, x0 + L)]:
        ax.text(x, y + 0.0045, f"{v:g}", ha="center", va="bottom", fontsize=fs, zorder=70, path_effects=HALO)
    ax.text(x0 + L + 0.004, y + 0.0014, "km", fontsize=fs, va="center", zorder=70, path_effects=HALO)


def source(ax, text, y=-0.075):
    ax.text(0, y, text, transform=ax.transAxes, fontsize=7.5, ha="left", va="top")


def save(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); bb = fig.get_tightbbox(r)
    W_, H_ = fig.get_size_inches(); p = 0.12
    fig.add_artist(Rectangle(((bb.x0 - p) / W_, (bb.y0 - p) / H_), (bb.width + 2 * p) / W_, (bb.height + 2 * p) / H_,
                             transform=fig.transFigure, fc="none", ec=FG, lw=1.2, clip_on=False))
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.08); plt.close(fig); print("saved", name)


def img(ax, rgba, z=2): ax.imshow(rgba, extent=EXT, zorder=z, interpolation="nearest")


def shade(rgba, hs, k=0.4):
    rgba[..., :3] *= ((1 - k) + k * np.nan_to_num(hs, nan=1))[..., None]; return rgba


def grey_hs(hs, mask, base=0.86):
    rgba = np.zeros((GH, GW, 4)); g = base * (0.75 + 0.25 * np.nan_to_num(hs, nan=1))
    rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = g; rgba[..., 3] = (~mask) & ~np.isnan(hs); return rgba


def classes(a, bins, mask):
    rgba = np.zeros((GH, GW, 4))
    for lo, hi, c, _ in bins:
        m = (a >= lo) & (a < hi) & mask; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    return rgba


def outline(ax, c="#111111", lw=1.4): catch.boundary.plot(ax=ax, color=c, lw=lw, zorder=20)


def places(ax, which=None, fs=8):
    for n, x, y in PLACES:
        if which and n not in which: continue
        ax.plot(x, y, "o", ms=3.5, mfc="white", mec="black", mew=0.7, zorder=30)
        ax.text(x + 0.003, y + 0.002, n, fontsize=fs, zorder=30, path_effects=HALO)


def locator(ax, box=(0.83, 0.6, 0.16, 0.38)):
    la = ax.inset_axes(list(box)); la.set_zorder(85); la.set_facecolor("white")
    hd.plot(ax=la, fc="#e3e3e3", ec="white", lw=0.6); har.boundary.plot(ax=la, color=FG, lw=0.6)
    catch.plot(ax=la, fc="#2f6fa8", ec="#123a5e", lw=0.6, alpha=0.8)
    b = har.total_bounds; px = (b[2] - b[0]) * 0.08
    la.set_xlim(b[0] - px, b[2] + px); la.set_ylim(b[1] - px, b[3] + px * 3.2); la.set_aspect(ASPECT); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(FG); sp.set_linewidth(0.6)
    la.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=la.transAxes, fc="white", ec=FG, lw=0.6, zorder=5))
    la.text(0.5, 0.93, "Harare Province", transform=la.transAxes, ha="center", va="center", fontsize=9, fontweight="bold", zorder=6)


ELEV = [(0, 1400, "#6f9e5d", "< 1 400"), (1400, 1450, "#a9c47f", "1 400 – 1 450"), (1450, 1500, "#e3d89a", "1 450 – 1 500"),
        (1500, 1550, "#d4a66b", "1 500 – 1 550"), (1550, 9999, "#a46b3c", "> 1 550")]


def map1():
    dem, hs = hillshade(); fig, ax = frame("Study Area Map")
    img(ax, grey_hs(hs, M)); img(ax, shade(classes(dem, ELEV, M), hs, 0.45), 3)
    dams.plot(ax=ax, fc="#9cc3e4", ec="none", zorder=8)
    rivers[rivers.kind == "river"].plot(ax=ax, color="#3d7fb8", lw=0.9, zorder=12); main_rd.plot(ax=ax, color="#7a2e0e", lw=1.0, zorder=13)
    outline(ax); places(ax); locator(ax)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in ELEV]
    h += [Line2D([], [], color="#111111", lw=1.4, label="Catchment boundary"), Line2D([], [], color="#3d7fb8", lw=1, label="Rivers"),
          Line2D([], [], color="#7a2e0e", lw=1.1, label="Main roads"), Patch(fc="#9cc3e4", label="Dams")]
    legend_in(ax, h, "Elevation (m)", ncol=2); scalebar(ax)
    source(ax, "Source: Copernicus DEM GLO-30; rivers, roads, dams and suburbs OpenStreetMap; boundaries OCHA COD-AB. Geographic coordinates, WGS 84.")
    save(fig, "map1_study_area")


SUBC = {1: "#8dd3c7", 2: "#ffffb3", 3: "#bebada", 4: "#fb8072", 5: "#80b1d3", 6: "#fdb462", 7: "#b3de69", 8: "#fccde5"}
SW = {1: 0.5, 2: 1.0, 3: 1.8, 4: 2.6}


def map2():
    _, hs = hillshade(); fig, ax = frame("Drainage Network and Sub-Catchments Map", face="white")
    lab = geo(Z["lab"].astype("float32")); rgba = np.zeros((GH, GW, 4))
    for i, c in SUBC.items():
        m = lab == i; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    img(ax, grey_hs(hs, M, 0.93)); img(ax, shade(rgba, hs, 0.3), 3)
    sub.boundary.plot(ax=ax, color="#555555", lw=0.6, zorder=10)
    for k in sorted(streams.order.astype(int)):
        streams[streams.order.astype(int) == k].plot(ax=ax, color="#1f5fa0", lw=SW.get(k, 2.6), zorder=12)
    outline(ax)
    o = ms.geometry.iloc[0].coords[0]; ax.plot(*o, "s", ms=6, mfc="#c0282d", mec="black", mew=0.7, zorder=40)
    ax.text(o[0] + 0.003, o[1] - 0.006, "Outlet", fontsize=8, zorder=40, path_effects=HALO)
    for _, s in sub.iterrows():
        p = s.geometry.representative_point()
        ax.text(p.x, p.y, str(int(s.id)), fontsize=11, fontweight="bold", ha="center", va="center", zorder=35, path_effects=HALO)
    h = [Patch(fc=SUBC[i], ec="#555555", lw=0.5, label=f"{i}  {NAMES[i]}") for i in SUBC]
    h += [Line2D([], [], color="#1f5fa0", lw=SW[k], label=f"Order {k} streams") for k in sorted(set(streams.order.astype(int)))]
    h += [Line2D([], [], marker="s", ls="", ms=6, mfc="#c0282d", mec="black", label="Outlet")]
    legend_in(ax, h, "Sub-catchments", ncol=2); scalebar(ax)
    source(ax, "Source: derived from Copernicus DEM GLO-30 (D8 flow direction, streams draining 1 km² or more, Strahler order). Geographic coordinates, WGS 84.")
    save(fig, "map2_drainage")


LC = {10: ("#2f6b2f", "Tree cover"), 20: ("#a9b85a", "Shrubland"), 30: ("#e8d98a", "Grassland"), 40: ("#e08a3c", "Cropland"),
      50: ("#c0282d", "Built-up"), 60: ("#c9bfb2", "Bare ground"), 80: ("#5a8fc7", "Open water"), 90: ("#4fb3a9", "Wetland")}


def map3():
    _, hs = hillshade(); lc = geo(C["lc"].astype("float32")); fig, ax = frame("Land Cover Map")
    rgba = np.zeros((GH, GW, 4))
    for k, (c, _) in LC.items():
        m = (lc == k) & M; rgba[m, :3] = mpl.colors.to_rgb(c); rgba[m, 3] = 1
    img(ax, grey_hs(hs, M)); img(ax, shade(rgba, hs, 0.25), 3); outline(ax); ms.plot(ax=ax, color="#123a5e", lw=1.1, zorder=15)
    places(ax, ["City Centre", "Mbare", "Hatfield", "Mabvuku", "Glen View"])
    present = set(np.unique(C["lc"][Z["catch"]]).tolist())
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for k, (c, l) in LC.items() if k in present]
    h += [Line2D([], [], color="#123a5e", lw=1.1, label="Mukuvisi River")]
    legend_in(ax, h, "Land cover", ncol=2); scalebar(ax)
    source(ax, "Source: ESA WorldCover 2021 v200 (10 m, resampled to 30 m by majority). Geographic coordinates, WGS 84.")
    save(fig, "map3_landcover")


CLAY = [(0, 20, "#f3e6c4", "< 20"), (20, 25, "#e2c08a", "20 – 25"), (25, 30, "#c98f55", "25 – 30"), (30, 35, "#a3602f", "30 – 35"),
        (35, 999, "#6e3a17", "> 35")]


def map4():
    _, hs = hillshade(); cl = geo(C["clay"].astype("float32"), Resampling.bilinear); fig, ax = frame("Soil Clay Content Map", face="#f2f2f2")
    img(ax, grey_hs(hs, M, 0.95)); img(ax, shade(classes(cl, CLAY, M), hs, 0.2), 3); outline(ax)
    sub.boundary.plot(ax=ax, color="#ffffff", lw=0.7, zorder=10); ms.plot(ax=ax, color="#1f5fa0", lw=1.1, zorder=15)
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in CLAY]
    h += [Line2D([], [], color="#1f5fa0", lw=1.1, label="Mukuvisi River"), Line2D([], [], color="#bbbbbb", lw=1.2, label="Sub-catchment boundaries")]
    legend_in(ax, h, "Clay content, 0–30 cm (%)", ncol=2); scalebar(ax)
    source(ax, "Source: iSDAsoil (Hengl et al., 2021), 30 m, depth-weighted 0–30 cm. Geographic coordinates, WGS 84.")
    save(fig, "map4_soil")


CNB = [(0, 70, "#1a9850", "< 70"), (70, 77, "#91cf60", "70 – 77"), (77, 82, "#fee08b", "77 – 82"), (82, 87, "#fc8d59", "82 – 87"),
       (87, 101, "#d73027", "≥ 87")]


def map5():
    _, hs = hillshade(); cn = geo(C["cn"].astype("float32")); fig, ax = frame("Curve Number Map")
    img(ax, grey_hs(hs, M)); img(ax, shade(classes(cn, CNB, M), hs, 0.2), 3); outline(ax)
    sub.boundary.plot(ax=ax, color="#333333", lw=0.6, zorder=10)
    places(ax, ["City Centre", "Mbare", "Hatfield", "Mabvuku", "Glen View", "Greendale"])
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in CNB]
    h += [Line2D([], [], color="#333333", lw=0.8, label="Sub-catchment boundaries")]
    legend_in(ax, h, "Curve number", ncol=2); scalebar(ax)
    source(ax, "Source: ESA WorldCover 2021 and iSDAsoil soil groups joined to USDA TR-55 curve numbers, average moisture (AMC II). Geographic coordinates, WGS 84.")
    save(fig, "map5_cn")


RUN = [(0, 20, "#fff3b0", "Low (< 20)"), (20, 30, "#f4a259", "Moderate (20 – 30)"), (30, 999, "#b5391f", "High (≥ 30)")]


def map6():
    _, hs = hillshade(); q = geo(np.load("data/qmap.npz")["q10"].astype("float32")); fig, ax = frame("10-Year Storm Runoff Map")
    img(ax, grey_hs(hs, M)); img(ax, shade(classes(q, RUN, M), hs, 0.2), 3); outline(ax)
    sub.boundary.plot(ax=ax, color="#333333", lw=0.6, zorder=10); ms.plot(ax=ax, color="#1f5fa0", lw=1.2, zorder=15)
    places(ax, ["City Centre", "Mbare", "Hatfield", "Mabvuku", "Glen View", "Glen Norah", "Greendale"])
    h = [Patch(fc=c, ec="#777777", lw=0.3, label=l) for *_, c, l in RUN]
    h += [Line2D([], [], color="#1f5fa0", lw=1.2, label="Mukuvisi River"), Line2D([], [], color="#333333", lw=0.8, label="Sub-catchment boundaries")]
    legend_in(ax, h, "Runoff depth (mm)"); scalebar(ax)
    source(ax, "Source: this study. SCS curve number runoff from a 60 mm, 24-hour storm (10-year return period), average moisture. Geographic coordinates, WGS 84.")
    save(fig, "map6_runoff")


def chart(title, ylab, xlab=None, size=(7.2, 4.4)):
    fig, ax = plt.subplots(figsize=size, dpi=200)
    ax.text(0.5, 1.05, title, transform=ax.transAxes, ha="center", fontsize=12.5, fontweight="bold")
    ax.set_ylabel(ylab, fontsize=10.5); ax.tick_params(labelsize=10)
    if xlab: ax.set_xlabel(xlab, fontsize=10.5)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
    return fig, ax


def done(fig, ax, name, y=-0.16):
    ax.text(1, y, AUTHOR, transform=ax.transAxes, ha="right", fontsize=7.5, color="#777777")
    fig.savefig(f"out/{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.15, facecolor="white"); plt.close(fig); print("saved", name)


J = json.load(open("data/runoff.json", encoding="utf-8"))


def fig1():
    am = np.sort(np.array(J["rain"]["am"]))[::-1]; n = len(am); T = (n + 0.12) / (np.arange(1, n + 1) - 0.44)
    fig, ax = chart("Design Storms for the Mukuvisi Catchment", "24-hour rainfall (mm)", "Return period (years)")
    ax.set_xscale("log"); ax.scatter(T, am, s=16, color="#555555", zorder=3, label="Wettest day of each season, 1981/82 to 2024/25")
    tt = np.geomspace(1.05, 100, 80); m, sd = am.mean(), am.std(ddof=1)
    K = -np.sqrt(6) / np.pi * (0.5772 + np.log(np.log(tt / (tt - 1))))
    ax.plot(tt, m + K * sd, color="#1f5fa0", lw=1.6, label="Gumbel fit")
    for t, p in J["rain"]["PT"].items():
        if t in ("2", "10", "100"): ax.plot(float(t), p, "o", ms=5, color="#1f5fa0", zorder=4); ax.text(float(t) * 1.08, p - 5, f"{p:.0f} mm", ha="left", fontsize=9.5, color="#1f5fa0")
    ax.set_xticks([1, 2, 5, 10, 25, 50, 100]); ax.set_xticklabels(["1", "2", "5", "10", "25", "50", "100"]); ax.set_ylim(0, 100)
    ax.legend(frameon=False, fontsize=9, loc="upper left"); done(fig, ax, "fig1_design_storms")


def fig2():
    fig, ax = chart("Flood Hydrographs at the Catchment Outlet", "Discharge (m³/s)", "Time from the start of the storm (hours)")
    for k, c in (("hydro100", "#b5391f"), ("hydro10", "#f4a259"), ("hydro2", "#1f5fa0")):
        h = np.array(J[k]); t = np.arange(len(h)) * 0.25; ax.plot(t, h, color=c, lw=1.6, label=f"{k[5:]}-year storm, peak {h.max():.0f} m³/s")
    ax.set_xlim(0, 54); ax.set_ylim(0, 280); ax.legend(frameon=False, fontsize=9.5); done(fig, ax, "fig2_hydrographs")


def fig3():
    S = J["sub"]; ids = sorted(S, key=lambda i: S[i]["C10"])
    fig, ax = chart("Runoff and Built-Up Land by Sub-Catchment", "", size=(7.6, 4.4))
    y = [S[i]["C10"] for i in ids]
    ax.barh([f"{i} {NAMES[int(i)]}" for i in ids], y, height=0.55, color=[SUBC[int(i)] for i in ids], ec="#555555", lw=0.5)
    for k, i in enumerate(ids): ax.text(y[k] + 0.008, k, f"{y[k]:.2f}  ({S[i]['built']:.0f} % built-up)", va="center", fontsize=9.5)
    ax.set_xlim(0, 0.75); ax.grid(axis="y", visible=False); ax.grid(axis="x", color="#e5e5e5", lw=0.6)
    ax.set_xlabel("Runoff coefficient, 10-year storm", fontsize=10.5); done(fig, ax, "fig3_subcatchments")


if __name__ == "__main__":
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5", "map6", "fig1", "fig2", "fig3"]): globals()[f]()
