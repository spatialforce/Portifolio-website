"""Download all GBIF records of Adansonia digitata with coordinates in Zimbabwe and a buffer region. Writes raw/gbif_*.csv."""
import json, urllib.request, csv, sys
def get(country):
    out, off = [], 0
    while True:
        u = f"https://api.gbif.org/v1/occurrence/search?taxonKey=5406695&country={country}&hasCoordinate=true&hasGeospatialIssue=false&occurrenceStatus=PRESENT&limit=300&offset={off}"
        d = json.load(urllib.request.urlopen(u)); out += d["results"]; off += 300
        if d["endOfRecords"]: break
    return out
F = ["key", "datasetName", "basisOfRecord", "year", "decimalLongitude", "decimalLatitude", "coordinateUncertaintyInMeters", "stateProvince", "locality", "institutionCode", "issues"]
for c in sys.argv[1:] or ["ZW"]:
    r = get(c)
    with open(f"raw/gbif_{c}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(F)
        for o in r: w.writerow([("|".join(o.get(k, [])) if k == "issues" else o.get(k, "")) for k in F])
    print(c, len(r))
