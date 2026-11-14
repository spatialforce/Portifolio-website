"""Write covid_dashboard.twb (Tableau workbook) that reads data/*.csv. Run: python -I make_twb.py"""
import os
from xml.sax.saxutils import quoteattr as q, escape as esc

DATA = os.path.abspath("data").replace("\\", "/")
TYPES = {"string": ("129", "Count"), "real": ("5", "Sum"), "date": ("133", "Year")}
from make_twb_cols import CTRY, WEEK
DS = {"C": ("federated.covid_countries", "covid_countries", CTRY), "W": ("federated.covid_weekly", "covid_weekly", WEEK)}
CAPTION = {"total_cases": "Cases", "total_deaths": "Deaths", "new_cases": "Weekly cases", "new_deaths": "Weekly deaths",
           "deaths_per_million": "Deaths per million", "people_vaccinated_per_hundred": "Vaccinated (%)", "week": "Week",
           "country": "Country"}


def datasource(key):
    name, cap, cols = DS[key]; fn = cap + ".csv"; rel = f"[{cap}#csv]"
    rc = "".join(f"<column datatype='{t}' name='{c}' ordinal='{i}' />" for i, (c, t) in enumerate(cols))
    md = "".join(
        f"<metadata-record class='column'><remote-name>{c}</remote-name><remote-type>{TYPES[t][0]}</remote-type>"
        f"<local-name>[{c}]</local-name><parent-name>[{fn}]</parent-name><remote-alias>{c}</remote-alias>"
        f"<ordinal>{i}</ordinal><local-type>{t}</local-type><aggregation>{TYPES[t][1]}</aggregation>"
        f"<contains-null>true</contains-null></metadata-record>" for i, (c, t) in enumerate(cols))
    lc = "".join(column(c, t) for c, t in cols)
    return (f"<datasource caption='{cap}' inline='true' name='{name}' version='18.1'><connection class='federated'>"
            f"<named-connections><named-connection caption='{cap}' name='textscan.{cap}'>"
            f"<connection class='textscan' directory={q(DATA)} filename='{fn}' password='' server='' /></named-connection>"
            f"</named-connections><relation connection='textscan.{cap}' name='{fn}' table='{rel}' type='table'>"
            f"<columns character-set='UTF-8' header='yes' locale='en_GB' separator=','>{rc}</columns></relation>"
            f"<metadata-records>{md}</metadata-records></connection>{lc}{extract(cap, cols)}</datasource>")


def extract(cap, cols):
    md = "".join(
        f"<metadata-record class='column'><remote-name>{c}</remote-name><remote-type>{TYPES[t][0]}</remote-type>"
        f"<local-name>[{c}]</local-name><parent-name>[Extract]</parent-name><remote-alias>{c}</remote-alias>"
        f"<ordinal>{i}</ordinal><local-type>{t}</local-type><aggregation>{TYPES[t][1]}</aggregation>"
        f"<contains-null>true</contains-null></metadata-record>" for i, (c, t) in enumerate(cols))
    return (f"<extract count='-1' enabled='true' units='records'><connection access_mode='readonly' author-locale='en_GB' "
            f"class='hyper' dbname='Data/Extracts/{cap}.hyper' default-settings='yes' schema='Extract' sslmode='' "
            f"tablename='Extract' update-time='11/14/2026 9:00:00 AM' username='tableau'>"
            f"<relation name='Extract' table='[Extract].[Extract]' type='table' />"
            f"<metadata-records>{md}</metadata-records></connection></extract>")


FMT = {"total_cases": "n#,##0", "total_deaths": "n#,##0", "new_cases": "n#,##0", "new_deaths": "n#,##0",
       "deaths_per_million": "n#,##0", "people_vaccinated_per_hundred": "n#,##0"}


def column(c, t):
    cap = f" caption={q(CAPTION[c])}" if c in CAPTION else ""
    if t == "string":
        sr = " semantic-role='[Country].[ISO3166_2]'" if c == "country" else ""
        return f"<column{cap} datatype='string' name='[{c}]' role='dimension'{sr} type='nominal' />"
    if t == "date":
        return f"<column{cap} datatype='date' name='[{c}]' role='dimension' type='ordinal' />"
    fm = f" default-format='{FMT[c]}'" if c in FMT else ""
    return f"<column{cap} datatype='real'{fm} name='[{c}]' role='measure' type='quantitative' />"


def inst(c, kind):
    return {"dim": (f"[none:{c}:nk]", "None", "nominal"), "sum": (f"[sum:{c}:qk]", "Sum", "quantitative"),
            "date": (f"[none:{c}:qk]", "None", "quantitative")}[kind]


def worksheet(name, key, uses, rows="", cols="", mark="Automatic", enc="", filt="", sort="", geo=False, style="<style />", pane="", title=None):
    ds = DS[key][0]; types = dict(DS[key][2])
    deps = "".join(column(c, types[c]) for c in sorted({c for c, _ in uses}))
    deps += "".join(f"<column-instance column='[{c}]' derivation='{inst(c, k)[1]}' name='{inst(c, k)[0]}' pivot='key' "
                    f"type='{inst(c, k)[2]}' />" for c, k in uses)
    if geo:
        deps += ("<column caption='Latitude (generated)' datatype='real' name='[Latitude (generated)]' role='measure' type='quantitative' />"
                 "<column caption='Longitude (generated)' datatype='real' name='[Longitude (generated)]' role='measure' type='quantitative' />")
    lo = (f"<layout-options><title><formatted-text><run bold='true' fontcolor='#333333' fontsize='10'>{esc(title or name)}</run>"
          f"</formatted-text></title></layout-options>")
    return (f"<worksheet name={q(name)}>{lo}<table><view><datasources><datasource caption='{DS[key][1]}' name='{ds}' /></datasources>"
            + ("<mapsources><mapsource name='Tableau' /></mapsources>" if geo else "") +
            f"<datasource-dependencies datasource='{ds}'>{deps}</datasource-dependencies>{filt}{sort}"
            + (f"<slices><column>{filt.split(chr(39))[3]}</column></slices>" if filt else "") +
            f"<aggregation value='true' /></view>{style}<panes><pane><view><breakdown value='auto' /></view>"
            f"<mark class='{mark}' /><encodings>{enc}</encodings>{pane}</pane></panes>"
            f"<rows>{rows}</rows><cols>{cols}</cols></table></worksheet>")


def f(key, c, kind):
    return f"[{DS[key][0]}].{inst(c, kind)[0]}"


def member(key, c, val):
    return (f"<filter class='categorical' column='{f(key, c, 'dim')}'><groupfilter function='member' level='{inst(c, 'dim')[0]}' "
            f"member={q(chr(34) + val + chr(34))} user:ui-domain='database' user:ui-enumeration='inclusive' user:ui-marker='enumerate' /></filter>")


def sortdesc(key, dim, by):
    return f"<sort class='computed' column='{f(key, dim, 'dim')}' direction='DESC' using='{f(key, by, 'sum')}' />"


INK, MUTED, BG = "#1f2933", "#6b7280", "#eef0f3"
CASE, DEATH, VAX = "#3b6ea5", "#b4483a", "#2f8a72"


def rule(el, *fmts):
    return f"<style-rule element='{el}'>{''.join(fmts)}</style-rule>"


def fm(attr, val, **k):
    extra = "".join(f" {a.replace('_', '-')}={q(v)}" for a, v in k.items())
    return f"<format attr='{attr}'{extra} value={q(val)} />"


NOGRID = rule("gridline", fm("line-visibility", "off", scope="cols"), fm("line-visibility", "off", scope="rows"))
NOZERO = rule("zeroline", fm("line-visibility", "off", scope="cols"), fm("line-visibility", "off", scope="rows"))
QUIET = rule("table", fm("show-null-value-warning", "false"))


def markstyle(color, labels=False, alpha=None):
    r = [fm("mark-color", color)]
    if labels: r += [fm("mark-labels-show", "true"), fm("mark-labels-cull", "false")]
    if alpha is not None: r.append(fm("mark-transparency", str(alpha)))
    return f"<style>{rule('mark', *r)}</style>"


def kpi(c):
    return ("<style>" + rule("cell", fm("font-size", "22"), fm("font-weight", "bold"), fm("color", INK), fm("text-align", "center"),
                             fm("vertical-align", "center")) + QUIET + "</style>")


def barstyle(key, measure):
    ax = f(key, measure, "sum")
    return ("<style>" + rule("axis", fm("display", "false", **{"class": "0", "field": ax, "scope": "cols"})) +
            rule("worksheet", fm("display-field-labels", "false", scope="rows")) +
            rule("label", fm("font-size", "8", field=f(key, measure, "sum")), fm("color", MUTED, field=f(key, measure, "sum"))) +
            NOGRID + NOZERO + QUIET + "</style>")


def areastyle(key, measure):
    return ("<style>" + rule("axis", fm("title", "", **{"class": "0", "field": f(key, "week", "date"), "scope": "cols"}),
                             fm("title", "", **{"class": "0", "field": f(key, measure, "sum"), "scope": "rows"})) +
            rule("gridline", fm("line-visibility", "off", scope="cols")) + NOZERO + QUIET + "</style>")


MAPSTYLE = ("<style>" + QUIET +
            rule("map-layer", *[fm("enabled", "false", id=i) for i in
                                ("admin-0-label-1st-tier", "admin-0-label-2nd-tier", "admin-0-label-3rd-tier",
                                 "admin-0-label-4th-tier", "admin-0-label-5th-tier")]) +
            rule("map", fm("washout", "0.0"), fm("map-style", "light"), fm("wrap", "true")) +
            rule("mark", f"<encoding attr='color' field='{f('C', 'deaths_per_million', 'sum')}' type='custom-interpolated'>"
                         "<color-palette custom='true' name='' type='ordered-sequential'><color>#f6e3dd</color>"
                         "<color>#7f2418</color></color-palette></encoding>") + "</style>")

S = []
KPIS = [("Cases worldwide", "total_cases", None), ("Deaths worldwide", "total_deaths", None),
        ("Cases in Zimbabwe", "total_cases", "Zimbabwe"), ("Deaths in Zimbabwe", "total_deaths", "Zimbabwe")]
for nm, c, ctry in KPIS:
    uses = [(c, "sum")] + ([("country", "dim")] if ctry else [])
    S.append(worksheet(nm, "C", uses, mark="Text", enc=f"<text column='{f('C', c, 'sum')}' />", style=kpi(c),
                       filt=member("C", "country", ctry) if ctry else ""))
MAPN = "COVID-19 deaths per million people"
S.append(worksheet(MAPN, "C",
                   [("country", "dim"), ("deaths_per_million", "sum"), ("total_cases", "sum"), ("total_deaths", "sum")],
                   rows=f"[{DS['C'][0]}].[Latitude (generated)]", cols=f"[{DS['C'][0]}].[Longitude (generated)]",
                   mark="Multipolygon", geo=True, style=MAPSTYLE,
                   title="Deaths per million people (darker is higher)",
                   enc=(f"<color column='{f('C', 'deaths_per_million', 'sum')}' /><lod column='{f('C', 'country', 'dim')}' />"
                        f"<tooltip column='{f('C', 'total_cases', 'sum')}' /><tooltip column='{f('C', 'total_deaths', 'sum')}' />"),
                   pane="<style>" + rule("mark", fm("has-stroke", "true"), fm("stroke-color", "#ffffff")) + "</style>"))
for nm, c, col in [("SADC deaths per million people", "deaths_per_million", DEATH),
                   ("SADC vaccinated, 1+ dose (%)", "people_vaccinated_per_hundred", VAX)]:
    S.append(worksheet(nm, "C", [("country", "dim"), (c, "sum"), ("sadc", "dim")],
                       rows=f("C", "country", "dim"), cols=f("C", c, "sum"), mark="Bar", style=barstyle("C", c),
                       filt=member("C", "sadc", "SADC"), sort=sortdesc("C", "country", c), pane=markstyle(col, labels=True)))
for nm, c, col in [("Weekly cases worldwide", "new_cases", CASE), ("Weekly deaths worldwide", "new_deaths", DEATH)]:
    S.append(worksheet(nm, "W", [("week", "date"), (c, "sum")], rows=f("W", c, "sum"), cols=f("W", "week", "date"), mark="Area",
                       style=areastyle("W", c), pane=markstyle(col, alpha=200)))

NAMES = [k[0] for k in KPIS] + [MAPN, "SADC deaths per million people", "SADC vaccinated, 1+ dose (%)",
                                "Weekly cases worldwide", "Weekly deaths worldwide"]
# x, y, w, h in 1/100000 of the dashboard
BOX = [(0, 7500, 25000, 13000), (25000, 7500, 25000, 13000), (50000, 7500, 25000, 13000), (75000, 7500, 25000, 13000),
       (0, 20500, 50000, 44000), (50000, 20500, 25000, 44000), (75000, 20500, 25000, 44000),
       (0, 64500, 50000, 31500), (50000, 64500, 50000, 31500)]
DASH = "COVID-19 Dashboard"


def zstyle(bg="#ffffff", pad="10"):
    return ("<zone-style>" + fm("border-color", "#000000") + fm("border-style", "none") + fm("border-width", "0") +
            fm("margin", "4") + fm("padding", pad) + fm("background-color", bg) + "</zone-style>")


z = [f"<zone h='7500' id='2' type-v2='text' w='100000' x='0' y='0'><formatted-text>"
     f"<run bold='true' fontcolor='{INK}' fontsize='16'>COVID-19 Dashboard</run>"
     f"<run fontcolor='{MUTED}' fontsize='11'>   Cases, deaths and vaccination, 2020 to 2026</run></formatted-text>"
     f"{zstyle(BG, '6')}</zone>"]
z += [f"<zone h='{h}' id='{i + 3}' name={q(n)} w='{w}' x='{x}' y='{y}'>{zstyle()}</zone>"
      for i, (n, (x, y, w, h)) in enumerate(zip(NAMES, BOX))]
z.append(f"<zone h='4000' id='20' type-v2='text' w='100000' x='0' y='96000'><formatted-text><run fontcolor='{MUTED}' fontsize='8'>"
         "Source: Our World in Data COVID-19 data (WHO cases and deaths; vaccinations to 2023), CC BY 4.0. "
         f"Dashboard: Kudzanai Chakavarika.</run></formatted-text>{zstyle(BG, '2')}</zone>")
dash = (f"<dashboards><dashboard name={q(DASH)}><style /><size minheight='640' minwidth='1000' sizing-mode='range' />"
        f"<zones><zone h='100000' id='1' type-v2='layout-basic' w='100000' x='0' y='0'>{''.join(z)}"
        f"<zone-style>{fm('background-color', BG)}</zone-style></zone></zones>"
        f"</dashboard></dashboards>")

CARDS = ("<cards><edge name='left'><strip size='160'><card type='pages' /><card type='filters' /><card type='marks' /></strip></edge>"
         "<edge name='top'><strip size='2147483647'><card type='columns' /></strip><strip size='2147483647'><card type='rows' /></strip>"
         "<strip size='31'><card type='title' /></strip></edge></cards>")
win = "".join(f"<window class='worksheet' name={q(n)}>{CARDS}</window>" for n in NAMES)
VP = "".join(f"<viewpoint name={q(n)}><zoom type='entire-view' /></viewpoint>" for n in NAMES)
win += f"<window class='dashboard' maximized='true' name={q(DASH)}><viewpoints>{VP}</viewpoints><active id='-1' /><device-preview visible='false' /></window>"
xml = ("<?xml version='1.0' encoding='utf-8' ?>\n<workbook source-build='2026.3.0' source-platform='win' version='18.1' "
       "xmlns:user='http://www.tableausoftware.com/xml/user'><preferences /><datasources>"
       f"{datasource('C')}{datasource('W')}</datasources><mapsources><mapsource name='Tableau' /></mapsources>"
       f"<worksheets>{''.join(S)}</worksheets>{dash}<windows source-height='30'>{win}</windows></workbook>")
open("covid_dashboard.twb", "w", encoding="utf-8").write(xml)
from xml.dom.minidom import parse; parse("covid_dashboard.twb")
import zipfile
with zipfile.ZipFile("covid_dashboard.twbx", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("covid_dashboard.twb", "covid_dashboard.twb")
    for n in ("covid_countries", "covid_weekly"): zf.write(f"data/extracts/{n}.hyper", f"Data/Extracts/{n}.hyper")
print("ok", len(xml), os.path.getsize("covid_dashboard.twbx"))
