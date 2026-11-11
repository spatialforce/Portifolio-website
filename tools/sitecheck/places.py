"""Download business locations for one city from Overture Maps Places (CDLA Permissive 2.0),
which merges Meta and Microsoft listings and is far more complete than OpenStreetMap
for African cities. Only places Overture is reasonably confident in are kept.

    python places.py harare
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import duckdb  # noqa: E402

from config import CITIES  # noqa: E402

RELEASE = "2026-10-21.0"
# Overture category -> our category
WANT = {
    "pharmacy": "pharmacy", "drugstore": "pharmacy",
    "supermarket": "supermarket", "grocery_store": "supermarket",
    "bank": "bank", "atms": "atm", "atm": "atm",
    "gas_station": "fuel",
    "hospital": "clinic", "medical_center": "clinic", "doctor": "clinic", "health_and_medical": "clinic",
}
MIN_CONFIDENCE = 0.6


def main(city):
    w, s, e, n = CITIES[city]["bbox"]
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    cats = ",".join(f"'{c}'" for c in WANT)
    q = f"""
      SELECT names.primary AS name, categories.primary AS cat, confidence,
             bbox.xmin AS lon, bbox.ymin AS lat
      FROM read_parquet('s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*', hive_partitioning=1)
      WHERE bbox.xmin BETWEEN {w} AND {e} AND bbox.ymin BETWEEN {s} AND {n}
        AND categories.primary IN ({cats})
    """
    rows = con.execute(q).fetchall()
    out = [{"name": r[0] or "", "cat": WANT[r[1]], "src": r[1], "conf": round(r[2] or 0, 2), "lon": round(r[3], 6), "lat": round(r[4], 6)}
           for r in rows]
    path = os.path.join(HERE, "cache", city, "overture.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"), indent=0)
    for c in sorted(set(WANT.values())):
        allc = [p for p in out if p["cat"] == c]
        good = [p for p in allc if p["conf"] >= MIN_CONFIDENCE]
        print(f"{c:12s} {len(allc):5d} listed, {len(good):5d} with confidence >= {MIN_CONFIDENCE}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "harare")
