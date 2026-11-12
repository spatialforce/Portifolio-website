"""Maps for the Masvingo mobile coverage case study (layout rules as in the carbon and rainfall maps)."""
import os, json
import numpy as np, rasterio, geopandas as gpd, matplotlib as mpl, matplotlib.pyplot as plt, matplotlib.patheffects as pe
from rasterio.warp import reproject, calculate_default_transform, Resampling
from matplotlib.colors import LightSource, BoundaryNorm, ListedColormap, LogNorm
from matplotlib.patches import Patch, Rectangle, Polygon, PathPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path
from scipy import ndimage
from shapely.geometry import box

mpl.rcParams.update({"font.family": "Arial", "font.size": 9})
LAT = 20.75
ASPECT = 1 / np.cos(np.radians(LAT))
AUTHOR = "© Kudzanai Chakavarika"
B = "../population/raw/bnd/"
prov = gpd.read_file("data/masvingo.geojson").to_crs(4326)
PG = gpd.GeoSeries([prov.geometry.union_all()], crs=4326)
dist = gpd.read_file("data/districts.gpkg").to_crs(4326)
zwe_p = gpd.read_file(B + "zwe_admin1.shp").to_crs(4326); zwe = gpd.read_file(B + "zwe_admin0.shp").to_crs(4326)
world = gpd.read_file("zip://../../corridors/raw/ne_10m_admin_0_countries.zip").cx[24:36, -27:-14]
sites = gpd.read_file("data/sites.gpkg").to_crs(4326)
TOWNS = [("Masvingo", 30.834, -20.072), ("Chiredzi", 31.669, -21.045), ("Triangle", 31.450, -21.034),
         ("Gutu", 31.159, -19.642), ("Jerera", 31.447, -20.405), ("Chivi", 30.502, -20.311),
         ("Nyika", 31.603, -20.010), ("Neshuro", 30.646, -20.945)]
EX = (29.55, 32.62, -22.56, -18.92)
TY = 0.968
OSM = "Basemap © OpenStreetMap contributors (Humanitarian style)."
S = json.load(open("out/stats.json"))
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
_W = {}


def warp(name, categorical=False, src="rast", arr=None):
    k = (name, src)
    if k in _W: return _W[k]
    with rasterio.open(f"{src}/{name}.tif") as s:
        tr, w, h = calculate_default_transform(s.crs, "EPSG:4326", s.width, s.height, *s.bounds)
        d = np.full((h, w), np.nan, "float32")
        a = s.read(1).astype("float32") if arr is None else arr.astype("float32")
        reproject(a, d, src_transform=s.transform, src_crs=s.crs, dst_transform=tr, dst_crs="EPSG:4326", src_nodata=np.nan,
                  resampling=Resampling.nearest if categorical else Resampling.bilinear, dst_nodata=np.nan)
    _W[k] = (d, (tr.c, tr.c + tr.a * w, tr.f + tr.e * h, tr.f)); return _W[k]


def basemap(dark=False):
    key = "bd" if dark else "b"
    if key in _W: return _W[key]
    import contextily as ctx
    f = "rast/basemap_hot.npz"
    if not os.path.exists(f):
        img, ext = ctx.bounds2img(29.2, -22.9, 33.0, -18.6, zoom=9, source=ctx.providers.OpenStreetMap.HOT, ll=True)
        img, ext = ctx.warp_tiles(img, ext, t_crs="EPSG:4326")
        np.savez_compressed(f, img=img, ext=np.array(ext))
    d = np.load(f); img = d["img"][..., :3].astype(float)
    mx, mn_ = img.max(2), img.min(2)
    grey = ndimage.binary_dilation((mx - mn_ < 22) & (mx > 110) & (mx < 228), iterations=1)
    grey &= ~ndimage.binary_dilation(mx < 110, iterations=3)
    med = np.stack([ndimage.median_filter(img[..., c], size=9) for c in range(3)], 2)
    img = np.where(grey[..., None], med, img) / 255
    if dark:
        g = 1 - img.mean(2); img = np.stack([0.06 + 0.30 * g] * 3, 2)
    else:
        img = 0.72 * img + 0.28
    _W[key] = (np.clip(img, 0, 1), tuple(d["ext"])); return _W[key]


def narrow(ax, x, y, fg="#222222", bg="white", h=0.06):
    fig = ax.figure; bb = ax.get_position()
    w = h * 0.34 * (bb.height * fig.get_figheight()) / (bb.width * fig.get_figwidth())
    y0 = y - h; notch = (x, y - h * 0.74)
    for xs, fc in ((-w, fg), (w, bg)):
        ax.add_patch(Polygon([(x, y), (x + xs, y0), notch], closed=True, fc=fc, ec=fg, lw=0.9,
                             transform=ax.transAxes, zorder=70, joinstyle="miter"))
    ax.text(x, y0 - 0.006, "N", transform=ax.transAxes, ha="center", va="top", fontsize=11,
            fontweight="bold", color=fg, zorder=70, path_effects=[pe.withStroke(linewidth=3, foreground=bg)])


def scalebar(ax, fg, x0, y0, length=100, alt="white", fs=7.5):
    km = 111.32 * np.cos(np.radians(LAT)); L = length / km
    halo = [pe.withStroke(linewidth=2.5, foreground=alt)]
    for i in range(4):
        ax.add_patch(Rectangle((x0 + i * L / 4, y0), L / 4, 0.03, fc=fg if i % 2 == 0 else alt, ec=fg, lw=0.6, zorder=60))
    for v, x in [(0, x0), (length // 2, x0 + L / 2), (length, x0 + L)]:
        ax.text(x, y0 + 0.05, f"{v}", ha="center", va="bottom", fontsize=fs, color=fg, zorder=60, path_effects=halo)
    ax.text(x0 + L + 0.035, y0 + 0.015, "km", fontsize=fs, color=fg, va="center", zorder=60, path_effects=halo)


def check(ax, artist, name):
    """Legend must sit clear of the province (rule: nothing overlaps the study area)."""
    ax.figure.canvas.draw()
    bb = artist.get_window_extent().transformed(ax.transData.inverted())
    hit = box(bb.x0, bb.y0, bb.x1, bb.y1).intersection(PG.iloc[0]).area
    print(f"  {name}: legend overlap with province {hit:.4f} deg2")


def legend_bl(ax, handles, title, fg="#222222", fs=9.5, sp=0.5, face="white", name=""):
    leg = ax.legend(handles=handles, title=title, loc="lower left", bbox_to_anchor=(0.008, 0.012), fontsize=fs,
                    title_fontsize=fs + 0.5, frameon=True, fancybox=False, edgecolor=fg, facecolor=face,
                    framealpha=0.94, alignment="left", labelcolor=fg, borderpad=0.9, handlelength=2.2,
                    handleheight=1.2, labelspacing=sp)
    leg.get_frame().set_linewidth(0.6); leg.set_zorder(65); leg.get_title().set_fontweight("bold"); leg.get_title().set_color(fg)
    check(ax, leg, name); return leg


def colorbar_bl(fig, ax, sm, title, ticks, labels=None, fg="#222222", face=(1, 1, 1, 0.94), w=0.42, h=0.10, ext="neither", name=""):
    bx = ax.inset_axes([0.008, 0.012, w, h]); bx.set_xticks([]); bx.set_yticks([]); bx.set_zorder(65)
    bx.set_facecolor(face)
    for s in bx.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    bx.text(0.045, 0.84, title, transform=bx.transAxes, ha="left", va="top", fontsize=10, fontweight="bold", color=fg)
    ca = bx.inset_axes([0.07, 0.28, 0.86, 0.17])
    cb = fig.colorbar(sm, cax=ca, orientation="horizontal", ticks=ticks, extend=ext)
    if labels: cb.set_ticklabels(labels)
    ca.tick_params(labelsize=8.5, length=2, colors=fg); cb.outline.set_linewidth(0.5); cb.outline.set_edgecolor(fg)
    check(ax, bx, name)


def pclip(ax, g=PG):
    verts, codes = [], []
    for geom in g:
        for poly in getattr(geom, "geoms", [geom]):
            for ring in [poly.exterior, *poly.interiors]:
                xy = np.asarray(ring.coords); verts += list(xy)
                codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    p = PathPatch(Path(verts, codes), transform=ax.transData, fc="none", ec="none"); ax.add_patch(p); return p


def lift(ax, glow=False):
    if glow:
        for k, a in enumerate(np.linspace(0.10, 0.02, 7)):
            PG.buffer(0.006 * (k + 1)).plot(ax=ax, fc="#ffb347", ec="none", alpha=a, zorder=1.5)
        PG.plot(ax=ax, fc="#101010", ec="none", zorder=1.6)
    else:
        for k in range(1, 8):
            PG.translate(0.007 * k, -0.007 * k).plot(ax=ax, fc="black", ec="none", alpha=0.055, zorder=1.5)
        PG.plot(ax=ax, fc="white", ec="none", zorder=1.6)


def ticks(ax, ext, fg, step=0.5):
    xt = np.arange(np.ceil(ext[0] / step) * step, ext[1], step); yt = np.arange(np.ceil(ext[2] / step) * step, ext[3], step)
    ax.set_xticks(xt); ax.set_yticks(yt)
    ax.set_xticklabels([f"{x:g}°E" for x in xt], color=fg); ax.set_yticklabels([f"{-y:g}°S" for y in yt], color=fg)
    ax.tick_params(length=2, colors=fg, labelsize=8)


def frame(title, width=9.0, dark=False):
    h = width * 0.9 * (EX[3] - EX[2]) * ASPECT / (EX[1] - EX[0]) / 0.92
    fig = plt.figure(figsize=(width, h), dpi=220); ax = fig.add_axes([0.07, 0.05, 0.9, 0.92])
    fg = "#f0f0f0" if dark else "#222222"; bg = "#111111" if dark else "white"
    fig.patch.set_facecolor("white")
    img, bext = basemap(dark); ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3]); ax.set_aspect(ASPECT); ticks(ax, EX, "#222222")
    for s in ax.spines.values(): s.set_color("#222222"); s.set_linewidth(0.7)
    halo = [pe.withStroke(linewidth=4, foreground=bg)]
    ax.text(0.5, TY, title, transform=ax.transAxes, ha="center", va="center", fontsize=15, fontweight="bold",
            color=fg, zorder=70, path_effects=halo)
    narrow(ax, 0.955, TY + 0.016, fg, bg)
    ax.text(0.992, 0.008, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=fg, zorder=70, path_effects=halo)
    return fig, ax, fg


def towns(ax, fs=8, dark=False, names=None):
    c, h = ("white", "#111111") if dark else ("black", "white")
    for n, x, y in TOWNS:
        if names and n not in names: continue
        ax.plot(x, y, "o", ms=3.6, mfc=h, mec=c, mew=0.8, zorder=30)
        dx, ha = (-0.03, "right") if n == "Triangle" else (0.03, "left")
        ax.text(x + dx, y + 0.02, n, fontsize=fs, ha=ha, color=c, zorder=30, path_effects=[pe.withStroke(linewidth=2.2, foreground=h)])


def outline(ax, dark=False):
    dist.boundary.plot(ax=ax, color="#9a9a9a" if dark else "#6f6f6f", lw=0.55, zorder=5)
    PG.boundary.plot(ax=ax, color="#dddddd" if dark else "#111111", lw=1.0, zorder=6)


def finish(fig, ax, text, name):
    ax.set_xlim(EX[0], EX[1]); ax.set_ylim(EX[2], EX[3])
    ax.text(0, -0.035, text, transform=ax.transAxes, fontsize=6.8, color="#222222", ha="left", va="top", wrap=True)
    fig.savefig(f"out/{name}.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig); print("saved", name)


def hillshade(exag=3):
    e, ext = warp("dem")
    dx = (ext[1] - ext[0]) / e.shape[1] * 111320 * np.cos(np.radians(LAT)); dy = (ext[3] - ext[2]) / e.shape[0] * 111320
    hs = LightSource(315, 40).hillshade(np.nan_to_num(e, nan=np.nanmean(e)), vert_exag=exag, dx=dx, dy=dy)
    return e, hs, ext


# ---- map 1: study area ----------------------------------------------------------
def map1():
    e, hs, eext = hillshade(4)
    E1 = (29.62, 32.55, -22.5, -19.05)
    fig = plt.figure(figsize=(10.4, 6.6), dpi=220); ax = fig.add_axes([0.04, 0.07, 0.56, 0.88])
    fg = "#222222"; fig.patch.set_facecolor("white"); ax.set_facecolor("#f4f4f4")
    ax.set_xlim(E1[0], E1[1]); ax.set_ylim(E1[2], E1[3]); ax.set_aspect(ASPECT, anchor="W"); ticks(ax, E1, fg)
    for s in ax.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    fig.canvas.draw()
    ax.text(0.5, TY, "Study Area Map", transform=ax.transAxes, ha="center", va="center", fontsize=14,
            fontweight="bold", color=fg, zorder=50, path_effects=HALO)
    narrow(ax, 0.93, TY + 0.016, fg, h=0.07)
    ax.text(0.99, 0.008, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#777777", zorder=50)
    world.plot(ax=ax, fc="#e8e8e8", ec="#ffffff", lw=0.6, zorder=1)
    zwe.plot(ax=ax, fc="#f0ede8", ec="none", zorder=1.2)
    zwe_p.boundary.plot(ax=ax, color="#b9b0a4", lw=0.6, zorder=1.3)
    im = ax.imshow(0.35 + 0.6 * hs, extent=eext, cmap="gray", vmin=0, vmax=1, zorder=2, interpolation="bilinear")
    im.set_clip_path(pclip(ax))
    ax.set_xlim(E1[0], E1[1]); ax.set_ylim(E1[2], E1[3])
    zwe.boundary.plot(ax=ax, color="#8c6d4f", lw=1.6, zorder=7)
    outline(ax); towns(ax, fs=7.5)
    LAB = {"Bikita": (31.73, -20.22), "Chiredzi Rural": (31.55, -21.62), "Chivi": (30.35, -20.62), "Gutu": (31.0, -19.42),
           "Masvingo Rural": (30.95, -20.45), "Mwenezi": (30.42, -21.55), "Zaka": (31.62, -20.62)}
    for n, (x, y) in LAB.items():
        ax.text(x, y, n.upper(), fontsize=6.3, ha="center", style="italic", zorder=8, path_effects=[pe.withStroke(linewidth=1.6, foreground="white")])
    ax.text(32.46, -22.05, "MOZAMBIQUE", fontsize=7, color="#777777", ha="center", style="italic", rotation=90, zorder=15)
    ax.text(30.6, -22.42, "SOUTH AFRICA", fontsize=7, color="#777777", ha="center", style="italic", zorder=15)
    hs_ = [Line2D([], [], marker="o", ls="none", ms=4.5, mfc="white", mec="black", label="Town"),
           Line2D([], [], color="#111111", lw=1.0, label="Province boundary"),
           Line2D([], [], color="#6f6f6f", lw=0.6, label="District boundary"),
           Line2D([], [], color="#8c6d4f", lw=1.6, label="International boundary"),
           Patch(fc="#e8e8e8", ec="#999999", lw=0.4, label="Neighbouring country")]
    p = ax.get_position(); x = p.x1 + 0.03; h = (p.y1 - p.y0 - 0.03) / 2; w = 0.985 - x
    la = fig.add_axes([x, p.y0 + h + 0.03, w, h]); la.set_xticks([]); la.set_yticks([])
    for s in la.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    leg = la.legend(handles=hs_, title="Legend", loc="upper left", fontsize=10.5, title_fontsize=11, frameon=False,
                    borderaxespad=0.8, alignment="left", handlelength=2.4, handleheight=1.4, labelspacing=0.75)
    leg.get_title().set_fontweight("bold")
    lc = fig.add_axes([x, p.y0, w, h]); lc.set_facecolor("white")
    world.plot(ax=lc, fc="#f0f0f0", ec="#ffffff", lw=0.3); zwe.plot(ax=lc, fc="#d9d9d9", ec="none")
    PG.plot(ax=lc, fc="#4d4d4d", ec="none"); zwe_p.boundary.plot(ax=lc, color="#ffffff", lw=0.5)
    lc.set_xlim(24.8, 34.2); lc.set_ylim(-23.2, -14.6); lc.set_aspect(ASPECT, adjustable="datalim"); lc.set_xticks([]); lc.set_yticks([])
    for s in lc.spines.values(): s.set_color(fg); s.set_linewidth(0.6)
    lc.add_patch(Rectangle((0, 0.87), 1, 0.13, transform=lc.transAxes, fc="white", ec="none", zorder=5))
    lc.plot([0, 1], [0.87, 0.87], transform=lc.transAxes, color=fg, lw=0.6, zorder=6)
    lc.text(0.5, 0.935, "ZIMBABWE", transform=lc.transAxes, ha="center", va="center", fontsize=11, fontweight="bold", zorder=7)
    lc.legend(handles=[Patch(fc="#4d4d4d", label="Masvingo Province"), Patch(fc="#d9d9d9", label="Other provinces")],
              loc="lower right", fontsize=7.5, frameon=False, handlelength=1.4)
    scalebar(ax, fg, 29.75, -22.30, 100, fs=7)
    ax.text(0, -0.05, "Source: boundaries OCHA COD-AB (ZIMSTAT); Copernicus GLO-30 DEM hillshade (90 m); towns OpenStreetMap; "
            "Natural Earth. WGS 84.", transform=ax.transAxes, fontsize=6.5, ha="left", va="top")
    fig.savefig("out/map1_study_area.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved map1_study_area")


# ---- map 2: recorded sites over relief -------------------------------------------------
def map2():
    fig, ax, fg = frame("Recorded Econet Sites By Technology Map (2025 to 2026)")
    lift(ax)
    e, hs, ext = hillshade(3)
    rgb = mpl.cm.gist_earth(mpl.colors.Normalize(150, 1500)(np.nan_to_num(e, nan=400)) * 0.75 + 0.2)[..., :3]
    shade = rgb * (0.55 + 0.45 * hs[..., None])
    im = ax.imshow(shade, extent=ext, zorder=2, interpolation="bilinear"); im.set_clip_path(pclip(ax))
    outline(ax)
    s = sites[sites.inprov.astype(bool)]
    kinds = [("2G only", (s.gsm == 1) & (s.umts == 0), "#ffffff", "o"), ("3G only", (s.gsm == 0) & (s.umts == 1), "#e8452c", "o"),
             ("2G and 3G", (s.gsm == 1) & (s.umts == 1), "#1d1d8f", "s")]
    hd = []
    for lab, m, c, mk in kinds:
        ax.scatter(s[m].geometry.x, s[m].geometry.y, s=11 if mk == "o" else 12, c=c, marker=mk, ec="#111111", lw=0.45, zorder=20)
        hd.append(Line2D([], [], marker=mk, ls="none", ms=5.5, mfc=c, mec="#111111", mew=0.6, label=f"{lab} ({int(m.sum())})"))
    towns(ax, fs=8)
    hd += [Patch(fc=mpl.cm.gist_earth(0.25), label="Low ground (about 200 m)"), Patch(fc=mpl.cm.gist_earth(0.8), label="High ground (about 1 500 m)")]
    legend_bl(ax, hd, "Recorded site (cells merged within 500 m)", name="map2")
    scalebar(ax, fg, 31.55, -22.50, 100)
    t = S["tot"]
    finish(fig, ax, f"Source: OpenCelliD cell export for Zimbabwe (MCC 648), Econet and NetOne cells, last updated 2025 to 2026; {t['sites_prov']} sites "
           "inside the province after merging cells by complete linkage (500 m). Positions are crowd-sourced estimates. "
           "Relief from Copernicus GLO-30 (90 m). No LTE cell is recorded inside the province. " + OSM + " WGS 84.", "map2_sites")


# ---- map 3: number of visible 2G sites -------------------------------------------------------
def map3():
    fig, ax, fg = frame("2G Line Of Sight Coverage Map (2026)")
    lift(ax)
    a, ext = warp("los_gsm15", categorical=True)
    bounds = [-0.5, 0.5, 1.5, 2.5, 4.5, 255]; cols = ["#ffffff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]
    cmap = ListedColormap(cols); norm = BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cmap, norm=norm, zorder=2, interpolation="nearest")
    im.set_clip_path(pclip(ax)); outline(ax); towns(ax)
    lab = ["None (no 2G site in view)", "1 site", "2 sites", "3 to 4 sites", "5 or more sites"]
    legend_bl(ax, [Patch(fc=c, ec="#555555", lw=0.4, label=l) for c, l in zip(cols, lab)], "2G sites in line of sight", name="map3")
    scalebar(ax, fg, 31.55, -22.50, 100)
    finish(fig, ax, "Source: GDAL viewshed from each recorded 2G site (30 m mast, 1.5 m handset, 4/3 earth radio refraction) "
           "on Copernicus GLO-30 (90 m), limited to 15 km. Sites within 30 km outside the province are included. " + OSM + " WGS 84.", "map3_los2g")


# ---- map 4: small multiples, line of sight vs terrain shadow ---------------------------------------
def map4():
    pan = [("2G (15 km)", "gsm15"), ("3G (10 km)", "umts10"), ("2G or 3G", None)]
    los = {k: warp(f"los_{k}", True)[0] > 0 for k in ["gsm15", "umts10"]}
    buf = {k: warp(f"buf_{k}", True)[0] > 0 for k in ["gsm15", "umts10"]}
    _, ext = warp("los_gsm15", True)
    cols = ["#1a9850", "#fdae61", "#ffffff"]
    E = (29.68, 32.50, -22.48, -19.10)
    pw = 4.6; ph = pw * (E[3] - E[2]) * ASPECT / (E[1] - E[0]); top = 0.55
    fig = plt.figure(figsize=(2 * pw, 2 * ph + top), dpi=220); fig.patch.set_facecolor("white")
    H = 2 * ph + top
    fig.text(0.5, 1 - top / 2 / H, "Line Of Sight And Terrain Shadow Map (2026)", ha="center", va="center", fontsize=15, fontweight="bold")
    img, bext = basemap()
    for i in range(4):
        r, c = divmod(i, 2)
        ax = fig.add_axes([c * 0.5, (1 - r) * ph / H, 0.5, ph / H]); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color("#222222"); s.set_linewidth(0.7)
        ax.imshow(img, extent=bext, zorder=0, interpolation="bilinear")
        ax.set_xlim(E[0], E[1]); ax.set_ylim(E[2], E[3]); ax.set_aspect("auto")
        if i == 3:
            ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, fc="white", ec="none", alpha=0.85, zorder=1))
            narrow(ax, 0.5, 0.93, h=0.11)
            leg = ax.legend(handles=[Patch(fc=c_, ec="#555555", lw=0.4, label=l) for c_, l in
                                     zip(cols, ["In range and in line of sight", "In range but hidden by terrain", "Beyond the assumed range"])],
                            title="Coverage class", loc="center", bbox_to_anchor=(0.5, 0.52), fontsize=10, title_fontsize=10.5,
                            frameon=True, fancybox=False, edgecolor="#222222", alignment="left", borderpad=0.9,
                            handlelength=2.2, handleheight=1.2, labelspacing=0.6)
            leg.get_frame().set_linewidth(0.6); leg.get_title().set_fontweight("bold")
            scalebar(ax, "#222222", E[0] + 0.32 * (E[1] - E[0]), E[2] + 0.17 * (E[3] - E[2]), 100)
            ax.text(0.98, 0.015, AUTHOR, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color="#222222", zorder=70)
            continue
        name, k = pan[i]
        lift(ax)
        if k: L, Bf = los[k], buf[k]
        else: L, Bf = los["gsm15"] | los["umts10"], buf["gsm15"] | buf["umts10"]
        cls = np.where(L, 0, np.where(Bf, 1, 2)).astype("float32")
        im = ax.imshow(cls, extent=ext, cmap=ListedColormap(cols), norm=BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3), zorder=2, interpolation="nearest")
        im.set_clip_path(pclip(ax)); outline(ax)
        ax.set_xlim(E[0], E[1]); ax.set_ylim(E[2], E[3])
        ax.text(0.03, 0.965, name, transform=ax.transAxes, ha="left", va="top", fontsize=12, fontweight="bold", zorder=70, path_effects=HALO)
    fig.text(0.0, -0.01, "Source: GDAL viewshed from each recorded site on Copernicus GLO-30 (90 m), 30 m mast, 1.5 m handset; assumed ranges 15 km (2G) "
             "and 10 km (3G). Orange is ground that a distance-only buffer would count as covered. " + OSM + " WGS 84.",
             fontsize=6.8, ha="left", va="top")
    fig.savefig("out/map4_shadow.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("saved map4_shadow")


# ---- map 5: people outside line of sight, dark glow -------------------------------------------
def map5():
    with rasterio.open("rast/pop2022.tif") as r: pop = r.read(1).astype("float64")
    los = (rasterio.open("rast/los_gsm15.tif").read(1) > 0) | (rasterio.open("rast/los_umts10.tif").read(1) > 0)
    lab = rasterio.open("rast/district.tif").read(1)
    u = np.where(los | (lab == 0), 0, pop)
    k = 11                                                     # about 1 km (11 x 90 m)
    H_, W_ = (u.shape[0] // k) * k, (u.shape[1] // k) * k
    agg = u[:H_, :W_].reshape(H_ // k, k, W_ // k, k).sum((1, 3)) / (k * 0.09) ** 2   # people per km2
    up = np.repeat(np.repeat(agg, k, 0), k, 1); full = np.zeros_like(u); full[:H_, :W_] = up
    full[lab == 0] = np.nan; full[full <= 0.5] = np.nan
    a, ext = warp("pop2022", src="rast", arr=full)
    fig, ax, fg = frame("Population Outside Line Of Sight Map (2022)", dark=True)
    lift(ax, glow=True)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("glow", ["#3b0f3f", "#8c1d5a", "#e0453a", "#fca636", "#fff4b0"])
    norm = LogNorm(1, 300)
    glow = ndimage.gaussian_filter(np.nan_to_num(np.log10(np.clip(a, 1, None))), 4)
    gi = ax.imshow(np.ma.masked_less(glow, 0.15), extent=ext, cmap=cmap, vmin=0, vmax=3.2, alpha=0.45, zorder=2, interpolation="bilinear")
    gi.set_clip_path(pclip(ax))
    im = ax.imshow(np.ma.masked_invalid(a), extent=ext, cmap=cmap, norm=norm, zorder=3, interpolation="nearest")
    im.set_clip_path(pclip(ax)); outline(ax, dark=True); towns(ax, dark=True)
    colorbar_bl(fig, ax, mpl.cm.ScalarMappable(norm=norm, cmap=cmap), "People per km² without coverage", [1, 3, 10, 30, 100, 300],
                ["1", "3", "10", "30", "100", "300"], fg="#f0f0f0", face=(0.07, 0.07, 0.07, 0.94), ext="max", name="map5")
    scalebar(ax, "#f0f0f0", 31.55, -22.50, 100, alt="#111111")
    t = S["tot"]
    finish(fig, ax, f"Source: WorldPop 2020 constrained (100 m) rescaled to ZIMSTAT 2022 district totals, summed to 1 km cells, kept where no "
           f"recorded 2G (15 km) or 3G (10 km) site is in line of sight: {t['unc'] / 1e6:.2f} million people. Inverted " + OSM + " WGS 84.", "map5_uncovered")


if __name__ == "__main__":
    import sys
    for n in (sys.argv[1:] or ["1", "2", "3", "4", "5"]): globals()[f"map{n}"]()
