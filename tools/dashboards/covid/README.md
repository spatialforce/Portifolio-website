# COVID-19 Dashboard (Tableau Public)

Data: Our World in Data COVID-19 compact file (WHO case and death counts; vaccinations to end of 2023), CC BY 4.0.
Refresh: download https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv to dl/owid.csv, then `python -I prep.py`.

## Tables (data/)
- covid_weekly.csv: one row per country per week (Monday). new_cases, new_deaths, per million, running totals, vaccinated %.
- covid_countries.csv: one row per country, latest totals, per million, case fatality %, vaccinated %, context fields.
- sadc = "SADC" for the 16 member states, else "Other". 237 countries; world 779.2 M cases, 7.11 M deaths.

## Build in Tableau Public
1. Connect > Text file > covid_countries.csv; add covid_weekly.csv as a second source (Data > New Data Source).
2. Set `code` geographic role: Country/Region > ISO 3166-1 alpha-3.
3. Sheets:
   - KPIs: SUM(total_cases), SUM(total_deaths), AVG(people_vaccinated_per_hundred) (countries table).
   - Map: code on Detail, deaths_per_million as colour (sequential), tooltip with country and totals.
   - Weekly cases: week (exact week) on Columns, SUM(new_cases) on Rows, bars.
   - Weekly deaths: same with new_deaths.
   - Top 10: country by deaths_per_million, filtered top 10.
   - Vaccination: people_vaccinated_per_hundred bars for SADC countries.
4. Filters: continent, sadc, country (apply to all sheets using related sources).
5. Dashboard 1200 x 800, publish (File > Save to Tableau Public), copy the embed link.

## Packaged workbook for Tableau Public

Tableau Public only accepts extracts. `python make_hyper.py` writes data/extracts/*.hyper (needs `pip install --user tableauhyperapi`, so run it without `-I`), then `python make_twb.py` writes covid_dashboard.twb and covid_dashboard.twbx (workbook plus extracts). Open the .twbx in Tableau Public 2025.1 and use File > Save to Tableau Public As.
