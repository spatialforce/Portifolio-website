"""Flood extent and exposure per season and per ward, from the Sentinel-1 season rasters.
A 30 m cell counts as flooded in a season if it was flooded on at least one acquisition date (normal water excluded).
Outputs
  data/season.csv   aoi, season, flood_km2, people, buildings, crop_km2, built_km2, dates (acquisition dates in season)
  data/ward.csv     aoi, ward pcode, name, district, area_km2, people (2025), seasons_flooded mean, people exposed per season and mean, buildings mean
  rast/freq_<aoi>.tif  number of seasons flooded (0..10)
Run: python -I analysis.py (PROJ_LIB set as ../rainfall/.projlib)"""
import os, numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
os.makedirs("rast", exist_ok=True)
SEASONS = list(range(2016, 2026))
A = gpd.read_file("data/aoi.gpkg").set_index("aoi")
W = gpd.read_file("../population/raw/bnd/zwe_admin3.shp").to_crs(32736)
ts = {k: pd.read_csv(f"data/ts_{k}.csv") for k in A.index}
S, WR = [], []
for k in A.index:
    with rasterio.open(f"data/normal_{k}.tif") as s:
        normal = s.read(1) == 1; prof = s.profile; T, shp = s.transform, s.shape
    aoi = rasterize([A.to_crs(32736).geometry[k]], out_shape=shp, transform=T).astype(bool)
    with rasterio.open(f"data/lc_{k}.tif") as s: lc = s.read(1); assert s.shape == shp
    # population 100 m -> people per 30 m cell (area-weighted)
    with rasterio.open(f"data/pop_{k}.tif") as s:
        pop = np.zeros(shp, "float32")
        reproject(s.read(1).astype("float32"), pop, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=prof["crs"], resampling=Resampling.average)
        pop *= (30 * 30) / (s.transform.a * -s.transform.e)
    pop *= aoi
    b = pd.read_csv(f"data/bld_{k}.csv")
    bx, by = gpd.points_from_xy(b.lon, b.lat, crs=4326).to_crs(32736).x, gpd.points_from_xy(b.lon, b.lat, crs=4326).to_crs(32736).y
    r, c = rasterio.transform.rowcol(T, bx, by); r, c = np.array(r), np.array(c)
    ok = (r >= 0) & (r < shp[0]) & (c >= 0) & (c < shp[1]); r, c = r[ok], c[ok]
    bin_ = aoi[r, c]; r, c = r[bin_], c[bin_]
    w = W[W.intersects(A.to_crs(32736).geometry[k])].copy()
    w["id"] = range(1, len(w) + 1)
    wid = rasterize(zip(w.geometry, w.id), out_shape=shp, transform=T) * aoi
    freq = np.zeros(shp, "uint8"); wp = {}
    for y in SEASONS:
        with rasterio.open(f"data/fl_{k}_{y}.tif") as s: f = (s.read(1) >= 1) & ~normal & aoi
        freq += f
        S.append(dict(aoi=k, season=f"{y}/{str(y + 1)[2:]}", flood_km2=round(f.sum() * 9e-4, 1), people=round(float(pop[f].sum())),
                      buildings=int(f[r, c].sum()), crop_km2=round((f & (lc == 40)).sum() * 9e-4, 1), built_km2=round((f & (lc == 50)).sum() * 9e-4, 2),
                      dates=int(ts[k].date.str[:7].between(f"{y}-11", f"{y + 1}-04").sum())))
        wp[y] = np.bincount(wid[f], weights=pop[f], minlength=len(w) + 1)
    p = prof.copy(); p.update(dtype="uint8", count=1, nodata=255)
    with rasterio.open(f"rast/freq_{k}.tif", "w", **p) as d: d.write(np.where(aoi, freq, 255).astype("uint8"), 1)
    area = np.bincount(wid.ravel(), minlength=len(w) + 1) * 9e-4
    ppl = np.bincount(wid.ravel(), weights=pop.ravel(), minlength=len(w) + 1)
    ever = np.bincount(wid[freq >= 1], minlength=len(w) + 1) * 9e-4
    for _, x in w.iterrows():
        i = x.id
        row = dict(aoi=k, pcode=x.adm3_pcode, ward=x.adm3_name, district=x.adm2_name, area_km2=round(area[i], 1), people=round(ppl[i]), ever_km2=round(ever[i], 1))
        for y in SEASONS: row[f"p{y}"] = round(wp[y][i])
        row["p_mean"] = round(np.mean([wp[y][i] for y in SEASONS])); row["p_max"] = round(max(wp[y][i] for y in SEASONS))
        WR.append(row)
    print(k, "AOI km2", round(aoi.sum() * 9e-4), "people 2025", round(float(pop.sum())), "buildings", len(r), "ever flooded km2", round((freq >= 1).sum() * 9e-4, 1),
          "flooded 5+ seasons km2", round((freq >= 5).sum() * 9e-4, 1), "normal water km2", round((normal & aoi).sum() * 9e-4, 1))
pd.DataFrame(S).to_csv("data/season.csv", index=False); pd.DataFrame(WR).to_csv("data/ward.csv", index=False)
print(pd.DataFrame(S).to_string(index=False))
