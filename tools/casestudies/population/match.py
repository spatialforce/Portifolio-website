"""Attach admin2 pcode and province to parsed districts and compare with official provincial totals."""
import json, geopandas as gpd
PROV = {"Bulawayo": 665940, "Manicaland": 2037762, "Mashonaland Central": 1384891, "Mashonaland East": 1731181,
        "Mashonaland West": 1893578, "Matabeleland North": 827626, "Matabeleland South": 760345,
        "Midlands": 1811908, "Masvingo": 1638539, "Harare": 2427209}
ALIAS = {"Bulawayo": "Bulawayo", "Harare Urban": "Harare", "Muzarabani": "Centenary/ Muzarabani", "Ruwa Local Board": "Ruwa",
         "Kadoma": "Kadoma Urban", "Chinhoyi Urban": "Chinhoyi", "Shurugwi Urban": "Shurugwi Town", "Gokwe Centre": "Gokwe South Urban",
         "Beitbridge": "Beitbridge Urban", "Beitbridge Rural": "Beitbridge", "Hwange Rural": "Hwange", "Kariba Rural": "Kariba",
         "Chegutu Rural": "Chegutu", "Marondera Rural": "Marondera", "Mutare Rural": "Mutare", "Chipinge Rural": "Chipinge",
         "Bindura Rural": "Bindura", "Gweru Rural": "Gweru", "Kwekwe Rural": "Kwekwe", "Shurugwi Rural": "Shurugwi",
         "Zvishavane Rural": "Zvishavane", "Masvingo Rural": "Masvingo", "Chiredzi Rural": "Chiredzi"}
d = json.load(open("districts2022.json"))
b = gpd.read_file("raw/bnd/zwe_admin2.shp").set_index("adm2_name")
for x in d:
    n = ALIAS.get(x["district"], x["district"])
    if n not in b.index: print("NO MATCH", x["district"]); continue
    x["adm2"] = n; x["pcode"] = b.loc[n, "adm2_pcode"]; x["province"] = b.loc[n, "adm1_name"]
print("unmatched shapes:", set(b.index) - {x.get("adm2") for x in d})
for p, t in PROV.items():
    s = sum(x["pop2022"] for x in d if x.get("province") == p)
    print(f"{p:20s} {s:9d} {t:9d} {s-t:+d}")
json.dump(d, open("districts2022.json", "w"), indent=1)
