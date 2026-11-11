"""Species photos: the lead image of each species' Wikipedia article, saved as a small webp,
with the author and licence from Wikimedia Commons so the credit can be shown."""
import io
import json
import os
import re
import urllib.parse
import urllib.error
import urllib.request

from PIL import Image

from species import SPECIES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "public", "webmaps", "migration", "photos")
UA = {"User-Agent": "migration-atlas-build/1.0 (portfolio map)"}


def get(url):
    import time
    for attempt in range(6):
        time.sleep(1.5)
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("rate limited: " + url)


def strip(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    cpath = os.path.join(OUT, "credits.json")
    credits = json.load(open(cpath)) if os.path.exists(cpath) else {}
    for s in SPECIES:
        if s["slug"] in credits and os.path.exists(os.path.join(OUT, s["slug"] + ".webp")):
            continue
        summ = json.loads(get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{s['wiki']}"))
        orig = summ.get("originalimage", {}).get("source")
        if not orig:
            print("no image", s["slug"]); continue
        parts = urllib.parse.urlparse(orig).path.split("/")
        fname = urllib.parse.unquote(parts[-2] if "thumb" in parts else parts[-1])
        q = urllib.parse.urlencode({"action": "query", "titles": "File:" + fname, "prop": "imageinfo",
                                    "iiprop": "extmetadata|url", "iiurlwidth": 480, "format": "json"})
        page = {}
        for host in ("commons.wikimedia.org", "en.wikipedia.org"):
            page = next(iter(json.loads(get(f"https://{host}/w/api.php?" + q))["query"]["pages"].values()))
            if "imageinfo" in page:
                break
        if "imageinfo" not in page:
            print("no imageinfo", s["slug"], ascii(fname)); continue
        info = page["imageinfo"][0]
        meta = info.get("extmetadata", {})
        img = Image.open(io.BytesIO(get(info.get("thumburl") or orig))).convert("RGB")
        img.thumbnail((480, 480))
        img.save(os.path.join(OUT, s["slug"] + ".webp"), "WEBP", quality=80)
        credits[s["slug"]] = {
            "author": strip(meta.get("Artist", {}).get("value", "Unknown"))[:80],
            "license": strip(meta.get("LicenseShortName", {}).get("value", "")),
            "url": info.get("descriptionurl", ""),
        }
        print(s["slug"], ascii(credits[s["slug"]]))
        json.dump(credits, open(cpath, "w"), indent=1)


if __name__ == "__main__":
    main()
