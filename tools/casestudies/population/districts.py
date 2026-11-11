"""Parse 2022 census preliminary district totals from prelim.txt (pdftotext -layout).
Columns in the text are shuffled, so the district total is taken as the largest number in each district block
(the total is always >= any ward, male or female figure). Provinces come from the admin2 names."""
import re, sys, json
txt = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
a = txt.rindex("4. Population Distribution by District"); b = txt.rindex("5. Number of Households")
lines = txt[a:b].splitlines()
hdr = re.compile(r"^\s*([A-Z][A-Za-z' -]+?)(?:\s+\(UMP\))?\s+(?:District\b|(?=Male\b))")
blocks, cur = [], None
for ln in lines:
    m = hdr.match(ln)
    if m:
        rest = ln[m.end():]  # numbers on a header line spill over from the previous district
        if cur: cur[1] += [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+|\d+", rest)]
        cur = [m.group(1).strip(), []]; blocks.append(cur); continue
    if cur: cur[1] += [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+|\d+", ln)]
out = [{"district": n, "pop2022": max(v) if v else 0} for n, v in blocks]
json.dump(out, open(sys.argv[2], "w"), indent=1)
for o in out: print(o["district"], o["pop2022"], sep="=", end=" | ")
print("\n", len(out), sum(o["pop2022"] for o in out))
