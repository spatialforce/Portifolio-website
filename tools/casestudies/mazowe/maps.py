"""Five maps for case study 4: bare ground and turbidity along the Mazowe River corridor.
Layout rules and helpers follow ../rainfall/maps.py. Run with PROJ_LIB set (see ../rainfall/.projlib). Output: out/*.png"""
import os, json
import numpy as np, pandas as pd, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
import contextily as ctx
from rasterio.warp import reproject, Resampling, calculate_default_transform
from scipy import ndimage
from matplotlib.colors import LightSource, ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True); os.makedirs("rast", exist_ok=True)
ASPECT = 1 / np.cos(np.radians(17.1))
AUTHOR = "© Kudzanai Chakavarika"
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
TY = 0.955
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
SADC = ["AGO", "BWA", "COM", "COD", "SWZ", "LSO", "MDG", "MWI", "MUS", "MOZ", "NAM", "SYC", "ZAF", "TZA", "ZMB", "ZWE"]
africa = gpd.read_file(f"zip://{NE}").cx[5:60, -40:10]
world = gpd.read_file(f"zip://{NE}").cx[29:35, -19:-15]
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(4326)
STUDY = ["Mazowe", "Bindura Rural", "Bindura Urban", "Shamva", "Uzumba Maramba Pfungwe", "Mudzi"]
sd = dist[dist.district.isin(STUDY)]
SG = gpd.GeoSeries([sd.geometry.union_all()], crs=4326)
river = gpd.read_file("data/mainstem.gpkg").to_crs(4326)
rl = gpd.read_file("data/reaches_line.gpkg")
cor = gpd.read_file("data/reaches_corridor.gpkg").to_crs(4326)
TOWNS = [("Harare", 31.052, -17.829), ("Mazowe", 30.973, -17.507), ("Bindura", 31.330, -17.299), ("Shamva", 31.579, -17.313),
         ("Mutoko", 32.226, -17.405), ("Mount Darwin", 31.584, -16.772), ("Kotwa", 32.670, -16.991)]
EX = (30.55, 33.25, -18.30, -16.25)
HB = (31.47, 31.792, -17.306, -17.166)        # Shamva hotspot, reaches 14 to 17
HALO = [pe.withStroke(linewidth=2.4, foreground="white")]
RIV = "#1f5fa8"
ZB = (31.605, 31.765, -17.290, -17.180)       # most affected stretch inside the hotspot (92% of its 2025 bare ground)


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved", name)


_BM = {}
def basemap(key, bounds, zoom, dark=False):
    """Humanitarian OSM tiles warped to WGS 84, grey dashed admin lines stripped, faded (or inverted grey when dark)."""
    k = (key, dark)
    if k in _BM: return _BM[k]
    f = f"rast/bm_{key}.npz"
    if not os.path.exists(f):
        for attempt in range(8):
            try:
                img, ext = ctx.bounds2img(*bounds, zoom=zoom, source=ctx.providers.OpenStreetMap.HOT, ll=True, n_connections=2); break
            except Exception:
                import time; time.sleep(4)
                print("tile retry", attempt)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:4326")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn < 22) & (mx > 110) & (mx < 228), iterations=1)
    grey &= ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255
    if dark:
        g = 1 - img.mean(axis=2, keepdims=True); img = np.repeat(0.05 + 0.32 * g, 3, axis=2)
    else:
        img = 0.72 * img + 0.28
    _BM[k] = (np.clip(img, 0, 1), tuple(d["ext"]))
    return _BM[k]


def narrow(ax, x, y, fg="#222222", bg="white", h=0.085):
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9, transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def ticks(ax, ext, step, fg):
    xs = np.arange(np.ceil(ext[0] / step) * step, ext[1] + 1e-9, step); ys = np.arange(np.ceil(ext[2] / step) * step, ext[3] + 1e-9, step)
    ax.set_xticks(xs); ax.set_yticks(ys)
    d = 2 if step < 0.1 else 1 if step < 1 else 0
    ax.set_xticklabels([f"{x:.{d}f}°E" for x in xs], color=fg); ax.set_yticklabels([f"{-y:.{d}f}°S" for y in ys], color=fg)
    ax.tick_params(length=2, colors=fg)


def frame3(title, ext, bm, width=11.0, dark=False, step=0.5):
    h = width * 0.92 * (ext[3] - ext[2]) * ASPECT / (ext[1] - ext[0]) / 0.9
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0.055, 0.075, 0.92, 0.9])
    fg = "#e6e6e6" if dark else "#222222"; bg = "#0b0b0b" if dark else "white"
    fig.patch.set_facecolor(bg)
    img, bext = basemap(*bm, dark=dark)
    ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(ASPECT)
    ticks(ax, ext, step, fg)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.7)
    halo = [pe.withStroke(linewidth=4, foreground=bg)]
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=15, fontweight="bold", color=fg, zorder=70, path_effects=halo)
    narrow(ax, 0.035, TY, fg, bg)
    ax.text(0.992, 0.01, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg, zorder=70, path_effects=halo)
    return fig, ax, fg


def lift(ax, g=SG, d=0.006, dark=False):
    if dark:
        g.boundary.plot(ax=ax, color="#9fd3ff", lw=0.9, zorder=6, path_effects=[pe.withStroke(linewidth=6, foreground="#9fd3ff", alpha=0.18)])
        return
    for k in range(1, 8):
        g.translate(d * k, -d * k).plot(ax=ax, fc="black", ec="none", alpha=0.055, zorder=1.5)
    g.plot(ax=ax, fc="white", ec="none", zorder=1.6)


def legend_br(ax, handles, title, fg="#222222", bg="white", fs=10.5, **kw):
    leg = ax.legend(handles=handles, title=title, loc="lower right", bbox_to_anchor=(0.992, 0.045), fontsize=fs, title_fontsize=11,
                    frameon=True, fancybox=False, edgecolor=fg, facecolor=bg, framealpha=0.94, alignment="left", labelcolor=fg,
                    **{"borderpad": 0.9, "handlelength": 2.4, "handleheight": 1.4, "labelspacing": 0.75, **kw})
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65)
    leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)
    return leg


def scalebar(ax, fg, x0, y0, km_total=50, lat=-17.2, alt="white", th=0.012):
    L = km_total / (111.32 * np.cos(np.radians(lat)))
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, th, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (km_total / 2, x0 + L / 2), (km_total, x0 + L)]:
        ax.text(x, y0 + th * 1.8, f"{v:g}", ha="center", va="bottom", fontsize=7.5, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + L * 0.04, y0 + th / 2, "km", fontsize=7.5, color=fg, va="center", zorder=60, path_effects=halo)


def towns(ax, color="black", halo="white", names=None, fs=7.8):
    for n, x, y in TOWNS:
        if names and n not in names: continue
        ax.plot(x, y, "o", ms=3.6, mfc=halo, mec=color, mew=0.8, zorder=30)
        ax.text(x + 0.025, y + 0.02, n, fontsize=fs, color=color, zorder=30, path_effects=[pe.withStroke(linewidth=2.2, foreground=halo)])


def source(ax, text, fg="#222222", ext=EX):
    ax.set_aspect(ASPECT); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    import textwrap
    ax.text(0, -0.05, textwrap.fill(text, 205), transform=ax.transAxes, fontsize=6.8, color=fg, ha="left", va="top", linespacing=1.3)


def mids():
    """Midpoint of every reach in WGS 84, with its reach number."""
    p = rl.copy(); p["geometry"] = rl.geometry.interpolate(0.5, normalized=True)
    return p.to_crs(4326)


def to4326(path):
    with rasterio.open(path) as s:
        T, w, h = calculate_default_transform(s.crs, "EPSG:4326", s.width, s.height, *s.bounds)
        out = np.zeros((s.count, h, w), dtype=s.dtypes[0])
        for b in range(s.count):
            reproject(rasterio.band(s, b + 1), out[b], dst_transform=T, dst_crs="EPSG:4326", resampling=Resampling.nearest)
    l, t = T.c, T.f
    return out, (l, l + w * T.a, t + h * T.e, t)


def hotcor():
    """Corridor of reaches 14 to 17 as one smooth outline (removes slivers left where reaches meet)."""
    g = cor[cor.reach.between(14, 17)].to_crs(32736).geometry.union_all().buffer(60).buffer(-60).buffer(-180).buffer(180)
    return gpd.GeoSeries([g], crs=32736).to_crs(4326)


def inmask(G, shape, ext):
    from rasterio.features import geometry_mask
    import rasterio.transform as rt
    T = rt.from_bounds(ext[0], ext[2], ext[1], ext[3], shape[1], shape[0])
    return geometry_mask(G.geometry, out_shape=shape, transform=T, invert=True).astype(int)


# 1 Study area: grey hillshade of the six districts, river with distance marks, side column with legend and province locator
def map1():
    with rasterio.open("../population/rast/dem.tif") as s:
        z = s.read(1).astype(float); b = s.bounds
    ext = (b.left, b.right, b.bottom, b.top)
    ls = LightSource(azdeg=315, altdeg=40)
    dx = (b.right - b.left) / z.shape[1] * 111320 * np.cos(np.radians(17)); dy = (b.top - b.bottom) / z.shape[0] * 111320
    hs = ls.hillshade(z, vert_exag=8, dx=dx, dy=dy)
    from rasterio.features import geometry_mask
    T = rasterio.transform.from_bounds(b.left, b.bottom, b.right, b.top, z.shape[1], z.shape[0])
    inside = geometry_mask(SG.geometry, out_shape=z.shape, transform=T, invert=True)
    fig = plt.figure(figsize=(10.0, 6.4), dpi=220); ax = fig.add_axes([0.045, 0.08, 0.70, 0.86]); fg = "#222222"
    fig.patch.set_facecolor("white"); ax.set_facecolor("#f4f4f4")
    world.plot(ax=ax, fc="#e6e6e6", ec="white", lw=0.6, zorder=1)
    dist.plot(ax=ax, fc="#ececec", ec="white", lw=0.6, zorder=1.2)
    g = np.where(inside, 0.40 + 0.55 * hs, np.nan)
    ax.imshow(np.ma.masked_invalid(g), extent=ext, cmap="gray", vmin=0, vmax=1, zorder=2, interpolation="bilinear")
    sd.boundary.plot(ax=ax, color="#3a3a3a", lw=1.1, zorder=4)
    river.plot(ax=ax, color=RIV, lw=2.0, zorder=6, path_effects=[pe.withStroke(linewidth=3.6, foreground="white")])
    m = river.to_crs(32736).geometry.iloc[0]
    for k in range(0, 351, 50):
        p = gpd.GeoSeries([m.interpolate(k * 1000)], crs=32736).to_crs(4326).iloc[0]
        ax.plot(p.x, p.y, "s", ms=4.2, mfc="white", mec=RIV, mew=1.0, zorder=7)
        up = k in (100, 150)   # below these marks sit Bindura and Shamva
        ax.text(p.x, p.y + (0.045 if up else -0.045), f"{k} km", fontsize=7, color=RIV, ha="center", va="bottom" if up else "top", zorder=7,
                path_effects=HALO, fontweight="bold")
    for n, x, y in TOWNS:
        ax.plot(x, y, "o", ms=3.8, mfc="white", mec="black", mew=0.8, zorder=8)
        ax.text(x + 0.03, y + 0.025, n, fontsize=8, zorder=8, path_effects=HALO)
    lab = {"Mazowe": (30.78, -17.30), "Bindura Rural": (31.27, -16.95), "Shamva": (31.72, -17.05), "Uzumba Maramba Pfungwe": (32.05, -17.05),
           "Mudzi": (32.62, -17.20)}
    for n, (x, y) in lab.items():
        ax.text(x, y, n.upper() if n != "Uzumba Maramba Pfungwe" else "UZUMBA MARAMBA\nPFUNGWE", fontsize=6.8, color="#444444", ha="center",
                style="italic", zorder=8, path_effects=HALO, linespacing=1.1)
    ax.text(33.12, -17.55, "MOZAMBIQUE", fontsize=7.5, color="#777777", style="italic", ha="center", rotation=90, zorder=8)
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3]); ax.set_aspect(ASPECT, anchor="W")
    ticks(ax, EX, 0.5, fg); ax.grid(color="#bbbbbb", lw=0.3)
    for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    ax.text(0.5, TY, "Study Area Map", transform=ax.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color=fg, zorder=50,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])
    narrow(ax, 0.035, TY, fg, "white", h=0.11)
    scalebar(ax, fg, 30.62, -18.24, 50)
    ax.text(0.99, 0.012, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#444444", zorder=50, path_effects=HALO)
    ax.text(0, -0.065, "Source: river OpenStreetMap relation 2638607; districts OCHA COD-AB; relief SRTM; Natural Earth. Distance marks along the main stem from its "
            "western end. WGS 84.", transform=ax.transAxes, fontsize=6.8, ha="left", va="top")
    # side column: two equal boxes
    fig.canvas.draw(); p = ax.get_position(); x = p.x1 + 0.025; gap = 0.03; hh = (p.y1 - p.y0 - gap) / 2; w = 0.985 - x
    la = fig.add_axes([x, p.y0 + hh + gap, w, hh]); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    hsl = [Line2D([], [], color=RIV, lw=2.2, label="Mazowe River"), Line2D([], [], marker="s", ls="", ms=5, mfc="white", mec=RIV, label="Distance mark"),
           Line2D([], [], marker="o", ls="", ms=5, mfc="white", mec="black", label="Town"), Line2D([], [], color="#3a3a3a", lw=1.2, label="District boundary"),
           Patch(fc="#9a9a9a", ec="none", label="Study districts")]
    leg = la.legend(handles=hsl, title="Legend", loc="upper left", fontsize=9.5, title_fontsize=10.5, frameon=False, borderaxespad=0.7,
                    alignment="left", handlelength=2.2, labelspacing=0.55)
    leg.get_title().set_fontweight("bold")
    lo = fig.add_axes([x, p.y0, w, hh]); lo.set_facecolor("white")
    pv = dist[dist.province.isin(["Mashonaland Central", "Mashonaland East"])].dissolve("province")
    dist.plot(ax=lo, fc="#f0f0f0", ec="white", lw=0.3)
    pv.plot(ax=lo, fc="#cfcfcf", ec="none")
    sd.plot(ax=lo, fc=RIV, ec="white", lw=0.3)
    pv.boundary.plot(ax=lo, color="#333333", lw=0.8)
    for n, (x, y) in {"MASHONALAND\nCENTRAL": (31.05, -16.45), "MASHONALAND\nEAST": (31.75, -18.35)}.items():
        lo.text(x, y, n, fontsize=7, ha="center", va="center", color="#222222", linespacing=1.1, path_effects=[pe.withStroke(linewidth=2, foreground="#cfcfcf")])
    bx = pv.total_bounds; cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2; hy = (bx[3] - bx[1]) / 2 * 1.08
    lo.set_xlim(cx - 1, cx + 1); lo.set_ylim(cy - hy * 1.16, cy + hy * 1.50); lo.set_aspect(ASPECT, adjustable="datalim"); lo.set_xticks([]); lo.set_yticks([])
    for sp in lo.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    lo.add_patch(Rectangle((0, 0.86), 1, 0.14, transform=lo.transAxes, fc="white", ec="none", zorder=5))
    lo.plot([0, 1], [0.86, 0.86], transform=lo.transAxes, color=fg, lw=0.6, zorder=6)
    lo.text(0.5, 0.93, "Mashonaland Central And East", transform=lo.transAxes, ha="center", va="center", fontsize=10.5, fontweight="bold", zorder=7)
    save(fig, "map1_study_area")


# 2 Graduated symbols: share of each reach corridor that is bare (2024 to 2026 window)
def map2():
    a = pd.read_csv("data/bare_by_reach.csv", index_col=0)
    c = cor.set_index("reach"); pct = 100 * a["2025"] / c.area_ha
    pt = mids().set_index("reach"); pt["pct"] = pct
    fig, ax, fg = frame3("Bare Ground Along The Mazowe River Map (2025)", EX, ("region2", (30.3, -18.55, 33.5, -16.0), 10))
    lift(ax)
    sd.boundary.plot(ax=ax, color="#8a8a8a", lw=0.6, zorder=3)
    river.plot(ax=ax, color=RIV, lw=1.4, zorder=4)
    size = lambda v: 10 + 21 * v
    cols = ["#fee391", "#fe9929", "#cc4c02", "#662506"]; bins = [0, 2, 4, 6, 100]
    k = np.digitize(pt.pct, bins[1:-1])
    ax.scatter(pt.geometry.x, pt.geometry.y, s=size(pt.pct), c=[cols[i] for i in k], ec="#3a2a1a", lw=0.6, zorder=6)
    towns(ax)
    scalebar(ax, fg, 30.62, -18.24, 50)
    labs = ["Under 2", "2 to 4", "4 to 6", "Over 6"]; rep = [1, 3, 5, 8]
    n = [int((k == i).sum()) for i in range(4)]
    hs = [Line2D([], [], marker="o", ls="", ms=np.sqrt(size(r)), mfc=c_, mec="#3a2a1a", mew=0.6, label=f"{l}  ({m} reaches)")
          for c_, l, r, m in zip(cols, labs, rep, n)]
    hs.append(Line2D([], [], color=RIV, lw=1.6, label="Mazowe River"))
    legend_br(ax, hs, "Bare ground (% of 1 km corridor)", handleheight=1.9)
    source(ax, "Source: Landsat 8 and 9 Collection 2 Level 2, wet seasons (November to April) 2023/24 to 2025/26; median NDVI below 0.3, water and built-up land "
           "excluded (ESA WorldCover 2021). One symbol per 10 km reach. Boundaries OCHA COD-AB. " + OSM + " WGS 84.")
    save(fig, "map2_bare_2025")
    return pct


SITES = [("A", 31.6397, -17.2789), ("B", 31.7081, -17.2230), ("C", 31.7505, -17.2048)]   # 4.5 km windows with the most newly bare ground
def sitebox(lon, lat, wkm=5.4, hkm=4.2):
    dx = wkm / 2 / (111.32 * np.cos(np.radians(lat))); dy = hkm / 2 / 110.6
    return (lon - dx, lon + dx, lat - dy, lat + dy)


def sitekm(lon, lat):
    """Distance along the river (km from the start of the main stem) of the point nearest the site centre."""
    ln = river.to_crs(32736).geometry.union_all()
    p = gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(32736).iloc[0]
    return ln.project(p) / 1000


def legend_cell(k, fg, title, items, km, frac, top=0.94, box_h=0.60):
    """Spare cell of a small-multiple grid: framed legend, north arrow and scale bar under it."""
    k.set_xlim(0, 1); k.set_ylim(0, 1); k.set_xticks([]); k.set_yticks([])
    for sp in k.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
    k.add_patch(Rectangle((0.05, top - box_h), 0.90, box_h, fc="white", ec=fg, lw=0.6))
    k.text(0.08, top - 0.05, title, ha="left", va="top", fontsize=12, fontweight="bold")
    step = (box_h - 0.16) / len(items)
    for j, (kind, c_, l) in enumerate(items):
        cy = top - 0.16 - step * (j + 0.5)
        if kind is Patch: k.add_patch(Rectangle((0.09, cy - 0.032), 0.07, 0.064, fc=c_, ec="#777777", lw=0.5))
        else: k.plot([0.09, 0.16], [cy, cy], color=c_, lw=1.8, path_effects=[pe.withStroke(linewidth=3.2, foreground="#555555")] if c_ == "white" else None)
        k.text(0.19, cy, l, ha="left", va="center", fontsize=11)
    narrow(k, 0.10, 0.25, fg, "white", h=0.13)
    x0, y0 = 0.34, 0.12
    for j in range(4):
        k.add_patch(Rectangle((x0 + j * frac / 4, y0), frac / 4, 0.035, fc=fg if j % 2 == 0 else "white", ec=fg, lw=0.6))
    for v, x in [(0, x0), (km / 2, x0 + frac / 2), (km, x0 + frac)]:
        k.text(x, y0 + 0.05, f"{v:g}", ha="center", va="bottom", fontsize=8.5)
    k.text(x0 + frac + 0.02, y0 + 0.017, "km", fontsize=8.5, va="center")
    k.text(0.97, 0.025, AUTHOR, ha="right", va="bottom", fontsize=7.5)


def grid(n_cols, n_rows, ext, title, W=13.0, TS=0.62):
    cw = W / n_cols; ch = cw * (ext[3] - ext[2]) * ASPECT / (ext[1] - ext[0]); H = n_rows * ch + TS; fh = ch / H
    fig = plt.figure(figsize=(W, H), dpi=220); fig.patch.set_facecolor("white")
    pos = [[c / n_cols, (n_rows - 1 - r) * fh, 1 / n_cols, fh] for r in range(n_rows) for c in range(n_cols)]
    fig.text(0.5, 1 - (TS / 2) / H, title, ha="center", va="center", fontsize=16, fontweight="bold")
    return fig, pos


def panel(fig, p, ext, label, fg="#222222"):
    a = fig.add_axes(p); a.set_aspect(ASPECT); a.set_xlim(ext[0], ext[1]); a.set_ylim(ext[2], ext[3]); a.set_xticks([]); a.set_yticks([])
    for sp in a.spines.values(): sp.set_color(fg); sp.set_linewidth(0.8)
    a.text(0.02, 0.95, label, transform=a.transAxes, fontsize=12, fontweight="bold", ha="left", va="top", zorder=70, bbox=dict(fc="white", ec=fg, lw=0.6, pad=3.5))
    return a


# 3 Small multiples: the most changed site in four windows, bare ground over the wet-season Landsat image of each window
def map3():
    n, lon, lat = SITES[0]; e = sitebox(lon, lat); HG = hotcor(); fg = "#222222"; BARE = "#ff3b00"
    print("site A river km", round(sitekm(lon, lat)))
    fig, pos = grid(3, 2, e, "Bare Ground Maps Shamva Reach Site A (2000–2025)")
    for i, y in enumerate([2000, 2009, 2017, 2025]):
        a = panel(fig, pos[i], e, f"Bare ground ({y})")
        im, iext = to4326(f"data/hot_l_rgb_{y}.tif"); a.imshow(np.moveaxis(im, 0, -1), extent=iext, zorder=1, interpolation="bilinear")
        m, mext = to4326(f"data/hot_bare_{y}.tif")
        a.imshow(np.ma.masked_equal(m[0] * inmask(HG, m[0].shape, mext), 0), extent=mext, cmap=ListedColormap([BARE]), vmin=0, vmax=1, zorder=3, interpolation="nearest")
        HG.boundary.plot(ax=a, color="white", lw=1.1, zorder=4); river.plot(ax=a, color="#7fd0ff", lw=1.1, zorder=4)
    a = panel(fig, pos[4], e, "Satellite image (2025)")
    rgb, rext = to4326("data/hot_rgb_2025.tif"); a.imshow(np.moveaxis(rgb, 0, -1), extent=rext, zorder=1, interpolation="bilinear")
    HG.boundary.plot(ax=a, color="white", lw=1.1, zorder=4)
    wk = (e[1] - e[0]) * 111.32 * np.cos(np.radians(lat))
    legend_cell(fig.add_axes(pos[5]), fg, "Legend", [(Patch, BARE, "Bare ground"), (Line2D, "#7fd0ff", "Mazowe River"), (Line2D, "white", "1 km corridor")], 2, 2 / wk)
    fig.text(0, -0.008, "Source: Landsat 5, 7, 8 and 9 Collection 2 Level 2, wet-season median true colour and NDVI below 0.3 in three-season windows centred on each year; "
             "Sentinel-2 L2A dry-season median June to September 2025 (satellite image). River OpenStreetMap. WGS 84.", fontsize=7.5, ha="left", va="top")
    save(fig, "map3_hotspot_years")


# 4 Change classes at the three most changed sites, 2000 window against 2025 window, over a grey 2025 image
def map4():
    a, ext = to4326("data/hot_bare_2000.tif"); b, _ = to4326("data/hot_bare_2025.tif")
    a, b = a[0], b[0]
    cls = np.zeros(a.shape); cls[(a == 1) & (b == 1)] = 1; cls[(a == 0) & (b == 1)] = 2; cls[(a == 1) & (b == 0)] = 3
    HG = hotcor(); fg = "#222222"
    rgb, rext = to4326("data/hot_rgb_2025.tif")
    g = np.moveaxis(rgb, 0, -1)[..., :3].astype(float).mean(axis=2) / 255; g = 0.45 + 0.55 * np.clip(g * 1.6, 0, 1)
    cols = ["#6b6b6b", "#e31a1c", "#1a9641"]
    e0 = sitebox(*SITES[0][1:])
    fig, pos = grid(2, 2, e0, "Bare Ground Change Maps Shamva Reach Sites (2000–2025)", W=11.0)
    for i, (n, lon, lat) in enumerate(SITES):
        e = sitebox(lon, lat); print("site", n, "river km", round(sitekm(lon, lat)))
        p = panel(fig, pos[i], e, f"Site {n}")
        p.imshow(g, extent=rext, cmap="gray", vmin=0, vmax=1, zorder=1, interpolation="bilinear")
        p.imshow(np.ma.masked_equal(cls * inmask(HG, cls.shape, ext), 0), extent=ext, cmap=ListedColormap(cols), vmin=0.5, vmax=3.5, zorder=3, interpolation="nearest")
        HG.boundary.plot(ax=p, color="black", lw=1.0, zorder=4); river.plot(ax=p, color=RIV, lw=1.2, zorder=4)
    wk = (e0[1] - e0[0]) * 111.32 * np.cos(np.radians(SITES[0][2]))
    items = [(Patch, cols[1], "Newly bare"), (Patch, cols[2], "No longer bare"), (Patch, cols[0], "Bare in both windows"), (Line2D, RIV, "Mazowe River"), (Line2D, "black", "1 km corridor")]
    legend_cell(fig.add_axes(pos[3]), fg, "Change from 2000 to 2025", items, 2, 2 / wk, box_h=0.62)
    from rasterio.features import geometry_mask
    import rasterio.transform as rt
    T = rt.from_bounds(ext[0], ext[2], ext[1], ext[3], cls.shape[1], cls.shape[0])
    inside = geometry_mask(HG.geometry, out_shape=cls.shape, transform=T, invert=True)
    ha = [((cls == i) & inside).sum() * 0.09 for i in (1, 2, 3)]
    print("hotspot corridor ha stable/new/lost", [round(v) for v in ha], "(approx; reprojected pixels)")
    fig.text(0, -0.008, "Source: Landsat 5, 7, 8 and 9 Collection 2 Level 2; wet-season median NDVI below 0.3, three-season windows 1998/99 to 2000/01 and 2023/24 to 2025/26. "
             "Backdrop Sentinel-2 L2A June to September 2025 in grey. River OpenStreetMap. WGS 84.", fontsize=7.5, ha="left", va="top")
    save(fig, "map4_hotspot_change")
    return ha


# 5 Dark glow line map: river reaches coloured by turbidity (median NDTI 2021 to 2025)
def map5():
    d = pd.read_csv("data/ndti_by_reach.csv"); d = d[(d.year >= 2021) & (d.px >= 20)]
    t = d.groupby("reach").ndti.median()
    g = rl.to_crs(4326).set_index("reach"); g["ndti"] = t
    fig, ax, fg = frame3("River Turbidity Map (2021–2025)", EX, ("region2", (30.3, -18.55, 33.5, -16.0), 10), dark=True)
    SG.plot(ax=ax, fc="#0b0b0b", ec="none", zorder=1.6, alpha=0.75)
    sd.boundary.plot(ax=ax, color="#5a5a5a", lw=0.5, zorder=3)
    lift(ax, dark=True)
    bins = [-1, -0.15, 0, 0.1, 0.15, 1]
    cols = ["#2c7fb8", "#7fcdbb", "#fed976", "#fd8d3c", "#e31a1c"]
    labs = ["Below −0.15 (clear)", "−0.15 to 0", "0 to 0.10", "0.10 to 0.15", "Over 0.15 (turbid)"]
    river.plot(ax=ax, color="#555555", lw=1.2, zorder=4)
    for i, c_ in enumerate(cols):
        s = g[(g.ndti >= bins[i]) & (g.ndti < bins[i + 1])]
        if len(s): s.plot(ax=ax, color=c_, lw=3.2, zorder=5, path_effects=[pe.withStroke(linewidth=9, foreground=c_, alpha=0.25)])
    towns(ax, color="#f0f0f0", halo="#0b0b0b")
    scalebar(ax, fg, 30.62, -18.24, 50, alt="#0b0b0b")
    n = [int(((g.ndti >= bins[i]) & (g.ndti < bins[i + 1])).sum()) for i in range(5)]
    hs = [Line2D([], [], color=c_, lw=3.2, label=f"{l}  ({m})") for c_, l, m in zip(cols, labs, n)]
    hs.append(Line2D([], [], color="#555555", lw=1.4, label=f"Too few water pixels  ({int(g.ndti.isna().sum())})"))
    legend_br(ax, hs, "Turbidity index NDTI (reaches)", fg=fg, bg="#0b0b0b")
    source(ax, "Source: Sentinel-2 L2A, April to July 2021 to 2025; NDTI = (red − green) / (red + green) on scene-classified water pixels, median per 10 km reach "
           "(reaches with fewer than 20 water pixels in a year left out). Boundaries OCHA COD-AB. " + OSM + " WGS 84.", fg)
    save(fig, "map5_turbidity")


if __name__ == "__main__":
    import sys
    for f in (sys.argv[1:] or ["map1", "map2", "map3", "map4", "map5"]): globals()[f]()
