"""Male and female 2022 totals per district from prelim.txt (section 4).
In each district block the total is the largest number; the male and female totals are the unique
pair that sums to it. The member printed further left (Male column) is male."""
import re, sys, json
txt = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
a = txt.rindex("4. Population Distribution by District"); b = txt.rindex("5. Number of Households")
hdr = re.compile(r"^\s*([A-Z][A-Za-z' -]+?)(?:\s+\(UMP\))?\s+(?:District\b|(?=Male\b))")
num = re.compile(r"\d{1,3}(?:,\d{3})+|\d+")
blocks, cur = [], None
for ln in txt[a:b].splitlines():
    m = hdr.match(ln); start = m.end() if m else 0
    found = [(int(x.group().replace(",", "")), x.start()) for x in num.finditer(ln, start)]
    if m:
        if cur: cur[1] += found
        cur = [m.group(1).strip(), []]; blocks.append(cur); continue
    if cur: cur[1] += found
out = []
for n, v in blocks:
    t = max(x for x, _ in v)
    for (x, cx) in v:
        for (y, cy) in v:
            if x + y == t and cx < cy and x != y:
                out.append({"district": n, "male": x, "female": y, "total": t}); break
        else: continue
        break
    else:
        out.append({"district": n, "male": None, "female": None, "total": t})
json.dump(out, open(sys.argv[2], "w"), indent=1)
ok = [o for o in out if o["male"]]
M = sum(o["male"] for o in ok); F = sum(o["female"] for o in ok)
print(len(out), len(ok), M, F, round(100 * M / F, 1))
for o in out: print(o["district"], o["male"], o["female"], o["male"] and round(100*o["male"]/o["female"],1))
