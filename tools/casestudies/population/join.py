"""Join prelim 2022 (ZimStat) with citypopulation.de 2002/2012/2022-final by district; write districts.gpkg."""
import json, pandas as pd, geopandas as gpd
CP = {"Harare Urban": "Harare Urban", "Ruwa Local Board": "Ruwa", "Uzumba Maramba Pfungwe": "Uzumba-Maramba-Pfungwe",
      "Chinhoyi Urban": "Chinhoyi", "Kadoma": "Kadoma Urban", "Beitbridge": "Beitbridge Urban", "Gwanda": "Gwanda Rural",
      "Mangwe": "Mangwe Rural", "Plumtree": "Mangwe Urban", "Gokwe Centre": "Gokwe Urban"}
d = pd.DataFrame(json.load(open("districts2022.json")))
c = pd.read_csv("data/citypop_districts.csv").set_index("district")
d["cp"] = d.district.map(lambda n: CP.get(n, n))
miss = set(d.cp) - set(c.index); print("missing in citypop:", miss)
d = d.join(c[["pop2002", "pop2012", "pop2022"]].rename(columns={"pop2022": "final2022"}), on="cp")
d["diff"] = d.final2022 - d.pop2022
print("sum 2012", d.pop2012.sum(), "(official 13061239)  sum 2002", d.pop2002.sum(), " final2022", d.final2022.sum())
print("max |prelim-final|", d["diff"].abs().max(), d.loc[d["diff"].abs().idxmax(), "district"])
b = gpd.read_file("raw/bnd/zwe_admin2.shp")[["adm2_pcode", "geometry"]]
g = b.merge(d, left_on="adm2_pcode", right_on="pcode")
g["area_km2"] = g.to_crs("ESRI:102022").area / 1e6   # Africa Albers equal area
g["dens2022"] = g.pop2022 / g.area_km2
g["growth"] = 100 * ((g.pop2022 / g.pop2012) ** (1 / 10) - 1)
print("area total", round(g.area_km2.sum()))
g.drop(columns=["cp"]).to_file("data/districts.gpkg", driver="GPKG")
print(g.sort_values("growth")[["district", "pop2012", "pop2022", "growth", "dens2022"]].round(2).to_string())
