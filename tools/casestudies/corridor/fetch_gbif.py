"""GBIF records of the African savanna elephant (Loxodonta africana) with coordinates inside the study box. Writes raw/gbif.csv.
Used only to check the resistance surface (are records in low-cost land?), not to build it."""
import json, urllib.request, csv
key = json.load(urllib.request.urlopen("https://api.gbif.org/v1/species/match?name=Loxodonta%20africana"))["usageKey"]
geo = "POLYGON((25.95 -19.05,29.15 -19.05,29.15 -17.35,25.95 -17.35,25.95 -19.05))".replace(" ", "%20").replace(",", "%2C")
out, off = [], 0
while True:
    u = (f"https://api.gbif.org/v1/occurrence/search?taxonKey={key}&geometry={geo}&hasCoordinate=true&hasGeospatialIssue=false"
         f"&occurrenceStatus=PRESENT&limit=300&offset={off}")
    d = json.load(urllib.request.urlopen(u)); out += d["results"]; off += 300
    if d["endOfRecords"]: break
F = ["key", "datasetName", "basisOfRecord", "year", "decimalLongitude", "decimalLatitude", "coordinateUncertaintyInMeters", "locality"]
with open("raw/gbif.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(F)
    for o in out: w.writerow([o.get(k, "") for k in F])
print("taxonKey", key, "records", len(out))
