"""Write data/extracts/*.hyper (Tableau extracts) from data/*.csv. Run: python -I make_hyper.py"""
import csv, datetime, os
from tableauhyperapi import (HyperProcess, Connection, Telemetry, CreateMode, TableDefinition, SqlType, Inserter, TableName,
                             Nullability, Date)
from make_twb_cols import CTRY, WEEK

os.makedirs("data/extracts", exist_ok=True)
ST = {"string": SqlType.text(), "real": SqlType.double(), "date": SqlType.date()}


def conv(v, t):
    if v == "": return None
    if t == "real": return float(v)
    if t == "date": d = datetime.date.fromisoformat(v[:10]); return Date(d.year, d.month, d.day)
    return v


with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
    for name, cols in [("covid_countries", CTRY), ("covid_weekly", WEEK)]:
        with Connection(hp.endpoint, f"data/extracts/{name}.hyper", CreateMode.CREATE_AND_REPLACE) as cn:
            cn.catalog.create_schema("Extract")
            td = TableDefinition(TableName("Extract", "Extract"),
                                 [TableDefinition.Column(c, ST[t], Nullability.NULLABLE) for c, t in cols])
            cn.catalog.create_table(td)
            rows = list(csv.DictReader(open(f"data/{name}.csv", encoding="utf-8")))
            with Inserter(cn, td) as ins:
                ins.add_rows([[conv(r[c], t) for c, t in cols] for r in rows]); ins.execute()
            print(name, cn.execute_scalar_query('SELECT COUNT(*) FROM "Extract"."Extract"'))
