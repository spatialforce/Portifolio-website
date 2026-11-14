"""Clean OWID COVID-19 data into two Tableau tables. Run: python -I prep.py"""
import pandas as pd
SADC = set("AGO BWA COM COD SWZ LSO MDG MWI MUS MOZ NAM SYC ZAF TZA ZMB ZWE".split())
d = pd.read_csv("dl/owid.csv", low_memory=False, parse_dates=["date"])
d = d[d.code.notna() & ~d.code.astype(str).str.startswith("OWID")].copy()
d["sadc"] = d.code.isin(SADC).map({True: "SADC", False: "Other"})
d["week"] = d.date - pd.to_timedelta(d.date.dt.weekday, unit="D")
keys = ["country", "code", "continent", "sadc", "population"]
w = d.groupby(keys + ["week"], dropna=False).agg(
    new_cases=("new_cases", "sum"), new_deaths=("new_deaths", "sum"),
    total_cases=("total_cases", "max"), total_deaths=("total_deaths", "max"),
    vaccinated_pct=("people_vaccinated_per_hundred", "max"),
    fully_vaccinated_pct=("people_fully_vaccinated_per_hundred", "max")).reset_index()
w["cases_per_million"] = w.new_cases / w.population * 1e6
w["deaths_per_million"] = w.new_deaths / w.population * 1e6
w = w[w.week >= "2019-12-30"].round(2)
w.to_csv("data/covid_weekly.csv", index=False, date_format="%Y-%m-%d")
last = lambda c: d.dropna(subset=[c]).sort_values("date").groupby("code")[c].last()
c = d.groupby("code")[keys].first()
for k in ["total_cases", "total_deaths", "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred",
          "median_age", "gdp_per_capita", "hospital_beds_per_thousand", "human_development_index"]:
    c[k] = last(k)
c["cases_per_million"] = c.total_cases / c.population * 1e6
c["deaths_per_million"] = c.total_deaths / c.population * 1e6
c["case_fatality_pct"] = c.total_deaths / c.total_cases * 100
c = c.reset_index(drop=True).round(2)
c.to_csv("data/covid_countries.csv", index=False)
print("weekly", w.shape, w.week.min().date(), w.week.max().date()); print("countries", c.shape)
print(c[c.code == "ZWE"].T.to_string())
print("world cases, deaths", int(c.total_cases.sum()), int(c.total_deaths.sum()))
