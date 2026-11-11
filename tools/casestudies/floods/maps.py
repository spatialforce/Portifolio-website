"""Maps for case study 6: flood exposure in Muzarabani and the lower Save valley (Sentinel-1, 2016/17 to 2025/26).
Helpers copied from ../mazowe/maps.py. Run with PROJ_LIB set (see ../rainfall/.projlib): python -I maps.py [map1 ...]. Output out/*.png"""
import os, sys
import numpy as np, pandas as pd, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
import contextily as ctx
from rasterio.warp import reproject, Resampling, calculate_default_transform
from scipy import ndimage
from matplotlib.colors import LightSource, ListedColormap
from matplotlib.patches import Patch, Rectangle, Polygon
from matplotlib.lines import Line2D
mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
os.makedirs("out", exist_ok=True); os.makedirs("rast", exist_ok=True)
AUTHOR = "© Kudzanai Chakavarika"
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
TY = 0.955
HALO = [pe.withStroke(linewidth=2.4, foreground="white")]
RIV = "#1f5fa8"
NE = "../../corridors/raw/ne_10m_admin_0_countries.zip"
world = gpd.read_file(f"zip://{NE}").cx[29:35, -23:-14]
dist = gpd.read_file("../population/data/districts.gpkg").to_crs(4326)
A = gpd.read_file("data/aoi.gpkg").set_index("aoi")
AG = {k: gpd.GeoSeries([A.geometry[k]], crs=4326) for k in A.index}
HR = gpd.read_file("data/hydrorivers.gpkg")
OR = gpd.read_file("data/osm_rivers.gpkg")
PL = pd.read_csv("data/places.csv")
EXT = {"muz": (30.74, 31.56, -16.90, -15.94), "save": (31.70, 32.72, -21.60, -19.82)}
LAT = {"muz": -16.4, "save": -20.7}
ASP = {k: 1 / np.cos(np.radians(LAT[k])) for k in LAT}
NAMES = {"Muzarabani Township": "Muzarabani", "Chadereka Business Center- Muzarabani": "Chadereka", "Hoya Business Center- Muzarabani": "Hoya",
         "St Alberts": "St Alberts", "Mucumbura": "Mukumbura", "Birchenough Bridge": "Birchenough Bridge", "Tongogara Refugee Camp": "Tongogara camp",
         "Chibuwe": "Chibuwe", "Checheche": "Checheche", "Chipinge": "Chipinge", "Devure": "Devure", "Mutema": "Mutema"}


def save(fig, name):
    fig.savefig(f"out/{name}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved", name)


def narrow(ax, x, y, fg="#222222", bg="white", h=0.085, tr=None):
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74); tr = tr or ax.transAxes
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9, transform=tr, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.008, "N", transform=tr, ha="center", va="top", fontsize=11, fontweight="bold", color=fg, zorder=70,
            path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def ticks(ax, ext, step, fg="#222222", fs=8):
    xs = np.arange(np.ceil(ext[0] / step - 1e-9) * step, ext[1] + 1e-9, step); ys = np.arange(np.ceil(ext[2] / step - 1e-9) * step, ext[3] + 1e-9, step)
    ax.set_xticks(xs); ax.set_yticks(ys)
    d = 2 if step < 0.1 else 1 if step < 1 else 0
    ax.set_xticklabels([f"{x:.{d}f}°E" for x in xs], color=fg, fontsize=fs); ax.set_yticklabels([f"{-y:.{d}f}°S" for y in ys], color=fg, fontsize=fs)
    ax.tick_params(length=2, colors=fg)


def scalebar(ax, fg, x0, y0, km_total, lat, alt="white", th=None):
    L = km_total / (111.32 * np.cos(np.radians(lat)))
    th = th or (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.011
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, th, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (km_total / 2, x0 + L / 2), (km_total, x0 + L)]:
        ax.text(x, y0 + th * 1.8, f"{v:g}", ha="center", va="bottom", fontsize=7.5, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + L * 0.05, y0 + th / 2, "km", fontsize=7.5, color=fg, va="center", zorder=60, path_effects=halo)


def to4326(path, resampling=Resampling.nearest):
    with rasterio.open(path) as s:
        T, w, h = calculate_default_transform(s.crs, "EPSG:4326", s.width, s.height, *s.bounds)
        out = np.zeros((s.count, h, w), dtype=s.dtypes[0])
        for b in range(s.count):
            reproject(rasterio.band(s, b + 1), out[b], dst_transform=T, dst_crs="EPSG:4326", resampling=resampling)
    l, t = T.c, T.f
    return out, (l, l + w * T.a, t + h * T.e, t)


def inmask(G, shape, ext):
    from rasterio.features import geometry_mask
    import rasterio.transform as rt
    T = rt.from_bounds(ext[0], ext[2], ext[1], ext[3], shape[1], shape[0])
    return geometry_mask(G.geometry, out_shape=shape, transform=T, invert=True)


def rivers(ax, k, scale=1.0, zorder=6, color=RIV):
    r = HR[HR.aoi == k]
    for lo, hi, lw in [(0, 3000, 0.5), (3000, 15000, 0.9), (15000, 1e9, 1.7)]:
        s = r[(r.UPLAND_SKM >= lo) & (r.UPLAND_SKM < hi)]
        if len(s): s.plot(ax=ax, color=color, lw=lw * scale, zorder=zorder)


def places(ax, k, names, fs=7.6, dx=0.02, dy=0.015, special=None):
    special = special or {}
    for _, p in PL[PL.aoi == k].iterrows():
        n = NAMES.get(p["name"])
        if n is None or n not in names: continue
        ax.plot(p.lon, p.lat, "o", ms=3.6, mfc="white", mec="black", mew=0.8, zorder=30)
        ddx, ddy, ha = special.get(n, (dx, dy, "left"))
        ax.text(p.lon + ddx, p.lat + ddy, n, fontsize=fs, ha=ha, zorder=30, path_effects=HALO)


# 1 Study Area Map: two panels (Muzarabani, lower Save) of elevation tints over hillshade, side column with legend and province locator
ELEV = [(0, 400, "#d9ead3"), (400, 600, "#f3e7b5"), (600, 900, "#dfbf8a"), (900, 9999, "#b58b5d")]
def tint(k):
    z, e = to4326(f"data/dem_{k}.tif", Resampling.bilinear); z = z[0].astype(float)
    inside = inmask(AG[k], z.shape, e)
    dx = (e[1] - e[0]) / z.shape[1] * 111320 * np.cos(np.radians(LAT[k])); dy = (e[3] - e[2]) / z.shape[0] * 111320
    hs = LightSource(azdeg=315, altdeg=40).hillshade(z, vert_exag=4, dx=dx, dy=dy)
    rgb = np.zeros(z.shape + (3,))
    for lo, hi, c in ELEV:
        m = (z >= lo) & (z < hi); rgb[m] = mpl.colors.to_rgb(c)
    rgb = rgb * (0.55 + 0.45 * hs[..., None])
    share = {f"{lo}-{hi}": round(100 * ((z >= lo) & (z < hi) & inside).sum() / inside.sum(), 1) for lo, hi, _ in ELEV}
    print(k, "elevation share %", share, "median m", round(float(np.median(z[inside]))))
    return np.dstack([rgb, inside.astype(float)]), e


def map1():
    fg = "#222222"
    fig = plt.figure(figsize=(10.4, 6.6), dpi=220); fig.patch.set_facecolor("white")
    top, bot = 0.90, 0.075
    H = top - bot
    pos = {}
    hin = H * 6.6
    x = 0.055
    for k in ["muz", "save"]:
        e = EXT[k]; win = hin * (e[1] - e[0]) / ((e[3] - e[2]) * ASP[k]); w = win / 10.4
        pos[k] = [x, bot, w, H]; x += w + 0.06
    axes = {}
    for k, lab in [("muz", "Muzarabani District"), ("save", "Lower Save Valley")]:
        e = EXT[k]; ax = fig.add_axes(pos[k]); axes[k] = ax; ax.set_facecolor("#f4f4f4")
        world.plot(ax=ax, fc="#ececec", ec="white", lw=0.6, zorder=1)
        dist.plot(ax=ax, fc="#e2e2e2", ec="white", lw=0.6, zorder=1.2)
        img, ie = tint(k)
        ax.imshow(img, extent=ie, zorder=2, interpolation="bilinear")
        dist.boundary.plot(ax=ax, color="#8a8a8a", lw=0.5, zorder=3)
        gpd.GeoSeries([world[world.ADM0_A3 == "ZWE"].geometry.iloc[0]]).boundary.plot(ax=ax, color="#111111", lw=1.1, zorder=5)
        rivers(ax, k)
        AG[k].boundary.plot(ax=ax, color="#c0392b", lw=1.4, zorder=7)
        ax.set_xlim(e[0], e[1]); ax.set_ylim(e[2], e[3]); ax.set_aspect(ASP[k])
        ticks(ax, e, 0.25 if k == "muz" else 0.5, fg, 7.5); ax.grid(color="#bbbbbb", lw=0.3, zorder=0)
        for sp in ax.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
        ax.text(0.03, 0.975, lab, transform=ax.transAxes, fontsize=9.5, fontweight="bold", ha="left", va="top", zorder=70, bbox=dict(fc="white", ec=fg, lw=0.6, pad=3))
    a = axes["muz"]
    places(a, "muz", ["Muzarabani", "Chadereka", "Hoya", "St Alberts"])
    a.text(31.40, -15.985, "MOZAMBIQUE", fontsize=7, color="#777777", style="italic", ha="center", zorder=8)
    scalebar(a, fg, 30.74, -16.88, 20, LAT["muz"])
    a = axes["save"]
    places(a, "save", ["Birchenough Bridge", "Tongogara camp", "Chibuwe", "Checheche", "Chipinge"],
           special={"Chipinge": (-0.02, 0.025, "right"), "Birchenough Bridge": (0.02, 0.02, "left")})
    rs = OR[OR.name.str.contains("Save")]
    a.text(32.40, -20.98, "Save", fontsize=7.5, color=RIV, style="italic", fontweight="bold", rotation=-60, zorder=31, path_effects=HALO)
    a.text(31.93, -21.27, "Runde", fontsize=7.5, color=RIV, style="italic", fontweight="bold", rotation=-25, zorder=31, path_effects=HALO)
    a.text(32.62, -21.35, "MOZAMBIQUE", fontsize=7, color="#777777", style="italic", ha="center", rotation=90, zorder=8)
    scalebar(a, fg, 31.75, -21.54, 25, LAT["save"])
    # title strip and north arrow above the panels
    fig.text((pos["muz"][0] + pos["save"][0] + pos["save"][2]) / 2, 0.955, "Study Area Map", ha="center", va="center", fontsize=14, fontweight="bold")
    na = fig.add_axes([pos["muz"][0], 0.955 - 0.075, 0.03, 0.075]); na.axis("off"); na.set_xlim(0, 1); na.set_ylim(0, 1)
    narrow(na, 0.5, 1.0, fg, "white", h=0.62)
    import textwrap
    fig.text(pos["muz"][0], 0.025, textwrap.fill("Source: elevation Copernicus GLO-30; rivers HydroSHEDS (upstream area over 500 km² in Muzarabani and 1 000 km² in the Save valley); districts OCHA COD-AB; "
             "Natural Earth; places OpenStreetMap. Study areas: Muzarabani District, and the land within 10 km of the Save and lower Runde south of Birchenough Bridge. WGS 84.", 190),
             fontsize=6.6, ha="left", va="top")
    # side column: two equal boxes
    x0 = pos["save"][0] + pos["save"][2] + 0.035; w = 0.985 - x0; gap = 0.03; hh = (H - gap) / 2
    la = fig.add_axes([x0, bot + hh + gap, w, hh]); la.set_xticks([]); la.set_yticks([])
    for sp in la.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    hs = [Patch(fc=c, ec="#777777", lw=0.4, label=(f"Below {hi} m" if lo == 0 else f"Over {lo} m" if hi > 5000 else f"{lo} to {hi} m")) for lo, hi, c in ELEV]
    hs += [Line2D([], [], color="#c0392b", lw=1.6, label="Study area"), Line2D([], [], color=RIV, lw=1.6, label="River"),
           Line2D([], [], color="#8a8a8a", lw=0.8, label="District boundary"), Line2D([], [], color="#111111", lw=1.2, label="National boundary"),
           Line2D([], [], marker="o", ls="", ms=5, mfc="white", mec="black", label="Place")]
    leg = la.legend(handles=hs, title="Elevation and features", loc="upper left", fontsize=8.6, title_fontsize=9.5, frameon=False, borderaxespad=0.6,
                    alignment="left", handlelength=2.0, labelspacing=0.5)
    leg.get_title().set_fontweight("bold")
    lo = fig.add_axes([x0, bot, w, hh]); lo.set_facecolor("white")
    PV = ["Mashonaland Central", "Manicaland", "Masvingo"]
    pv = dist[dist.province.isin(PV)].dissolve("province")
    dist.dissolve("province").plot(ax=lo, fc="#f0f0f0", ec="white", lw=0.4)
    pv.plot(ax=lo, fc="#cfcfcf", ec="none")
    for k in AG: AG[k].plot(ax=lo, fc="#c0392b", ec="none")
    pv.boundary.plot(ax=lo, color="#333333", lw=0.6)
    zb = dist.total_bounds; cx = (zb[0] + zb[2]) / 2; bw = (zb[2] - zb[0]) * 1.12
    bb = lo.get_position(); r = (bb.height * 6.6) / (bb.width * 10.4)           # box height / width in inches
    bh = bw * r / (1 / np.cos(np.radians(19)))                                   # degrees of latitude that fill the box at true aspect
    y0 = zb[1] - (bh * 0.85 - (zb[3] - zb[1])) / 2                               # map in the lower 85 %, under the header strip
    lo.set_xlim(cx - bw / 2, cx + bw / 2); lo.set_ylim(y0, y0 + bh); lo.set_aspect("auto")
    lo.set_xticks([]); lo.set_yticks([])
    for sp in lo.spines.values(): sp.set_color(fg); sp.set_linewidth(0.6)
    lo.add_patch(Rectangle((0, 0.85), 1, 0.15, transform=lo.transAxes, fc="white", ec="none", zorder=5))
    lo.plot([0, 1], [0.85, 0.85], transform=lo.transAxes, color=fg, lw=0.6, zorder=6)
    lo.text(0.5, 0.925, "Study Provinces", transform=lo.transAxes, ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=7)
    save(fig, "map1_study_area")


if __name__ == "__main__":
    for f in (sys.argv[1:] or ["map1"]): globals()[f]()
