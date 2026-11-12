import json, numpy as np, geopandas as gpd, rasterio, pandas as pd
from scipy.ndimage import distance_transform_edt
g = json.load(open("data/grid.json")); x0, y0, x1, y1 = g["bounds"]; R = g["res"]
rd = lambda n: rasterio.open(f"rast/{n}.tif").read(1)
pop, lab = rd("pop2022").astype("float64"), rd("district")
d = gpd.read_file("data/districts.gpkg"); s = gpd.read_file("data/sites.gpkg")
L = {k: rd(f"los_{k}") > 0 for k in ["gsm10", "gsm15", "gsm20", "umts5", "umts10", "umts15"]}
B = {k: rd(f"buf_{k}") > 0 for k in L}
P = lab > 0; T = pop[P].sum()
seed = np.ones(pop.shape, bool)
for xx, yy in zip(s.x, s.y): seed[int((y1 - yy) // R), int((xx - x0) // R)] = False
dist = distance_transform_edt(seed) * R / 1000
base2, base3 = L["gsm15"], L["umts10"]; anyc = base2 | base3; unc = P & ~anyc
rows = []
for i, r in d.iterrows():
    m = lab == i + 1; p = pop[m].sum()
    rows.append(dict(district=r.district, pop=round(p), sites=int(s.within(r.geometry).sum()),
        g2=100 * pop[m & base2].sum() / p, g3=100 * pop[m & base3].sum() / p, any=100 * pop[m & anyc].sum() / p,
        buf2=100 * pop[m & B["gsm15"]].sum() / p, buf3=100 * pop[m & B["umts10"]].sum() / p,
        unc=round(pop[m & ~anyc].sum()), area_unc=100 * (m & ~anyc).sum() / m.sum(),
        dist_unc=float(np.average(dist[m & ~anyc], weights=pop[m & ~anyc] + 1e-9)) if (m & ~anyc).any() else 0))
t = pd.DataFrame(rows); print(t.round(1).to_string())
pc = lambda a: 100 * pop[P & a].sum() / T; ar = lambda a: 100 * (P & a).sum() / P.sum()
tot = dict(pop=T, g2=pc(base2), g3=pc(base3), any=pc(anyc), buf2=pc(B["gsm15"]), buf3=pc(B["umts10"]),
           buf_any=pc(B["gsm15"] | B["umts10"]), unc=pop[unc].sum(), area_g2=ar(base2), area_g3=ar(base3), area_any=ar(anyc),
           sites_prov=int(s.inprov.sum()), sites_grid=len(s), sites_gsm=int(s[s.inprov].gsm.sum()), sites_umts=int(s[s.inprov].umts.sum()),
           sites_both=int((s[s.inprov].gsm & s[s.inprov].umts).sum()))
rural = np.isin(lab, [i + 1 for i, r in d.iterrows() if "Urban" not in r.district])
tot["unc_rural_share"] = 100 * pop[unc & rural].sum() / pop[unc].sum()
tot["rural_any"] = 100 * pop[rural & anyc].sum() / pop[rural].sum()
w = pop[unc]; dd = dist[unc]
tot["unc_dist_med"] = float(np.interp(0.5, np.cumsum(w[np.argsort(dd)]) / w.sum(), np.sort(dd)))
tot["unc_dist_bands"] = {b: 100 * w[(dd >= a) & (dd < c)].sum() / w.sum() for b, a, c in [("<10", 0, 10), ("10-15", 10, 15), ("15-20", 15, 20), ("20-30", 20, 30), (">30", 30, 999)]}
sens = {k: dict(los=pc(L[k]), buf=pc(B[k]), area_los=ar(L[k])) for k in L}
# multi-site overlap for base 2G
c2 = rd("los_gsm15"); tot["g2_multi"] = 100 * pop[P & (c2 >= 2)].sum() / T
print(json.dumps(tot, indent=1)); print(json.dumps(sens, indent=1))
t.to_csv("out/districts.csv", index=False); json.dump(dict(tot=tot, sens=sens, districts=rows), open("out/stats.json", "w"), indent=1)
with rasterio.open("rast/dist.tif", "w", **{**rasterio.open("rast/pop2022.tif").profile}) as o: o.write(dist.astype("float32"), 1)
