"""Write authorship and data-source metadata (EXIF + XMP) into the site's map and chart images.

WebP files are edited at the RIFF chunk level, so the image data is copied byte for byte and
never re-encoded. PNG files get iTXt chunks, also without touching the pixels.
Rerun after adding new images:  python tools/provenance/tag_images.py
"""
import io, struct, sys
from pathlib import Path
from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parents[2] / "src" / "assets"
AUTHOR = "Kudzanai Chakavarika"
YEAR = "2026"
SOFTWARE = "Python (rasterio, geopandas, matplotlib), QGIS, Google Earth Engine"
SKIP = {"myself.webp", "profile_1.webp", "hero.webp", "storymap_mapping.webp", "storymap_wildlife.webp"}

CASE = {
    "population": "A Spatial Analysis of Population Distribution, Density and Growth in Zimbabwe Between the 2012 and 2022 Population Censuses",
    "rainfall-zimbabwe": "Rainfall Variability and Drought Patterns in Zimbabwe from the 1991/92 to 2024/25 Agricultural Seasons",
    "mazowe-valley": "Assessing the Impact of Gold Mining on River Siltation in the Mazowe Valley from 2000 to 2025",
    "gazetted-forests": "Mapping Encroachment and Land Loss in Seven Gazetted Forests of Matabeleland North, Zimbabwe (2024)",
    "solar-site-suitability": "Site Suitability Analysis for Utility-Scale Solar Farms in Matabeleland South Province of Zimbabwe Using the Analytic Hierarchy Process",
    "hwange-carbon": "Above-Ground Carbon Stock Estimation in Hwange National Park Using GEDI LiDAR and Random Forest Regression (2019 to 2023)",
    "hwange-air": "Nitrogen Dioxide and Sulphur Dioxide Pollution from the Hwange Thermal Power Station Expansion Using Sentinel-5P (2019 to 2025)",
    "kariba": "Area–Elevation–Storage Relationships and Water Level Decline at Lake Kariba (2000 to 2025)",
    "bulawayo-landfill": "Landfill Site Selection for Bulawayo Using GIS-Based Multi-Criteria Analysis",
}


def describe(p: Path) -> str:
    kind = "Chart" if p.stem.startswith("fig") else "Map"
    if p.parent.name in CASE:
        return (f"{kind} from the case study '{CASE[p.parent.name]}' by {AUTHOR}. Rendered by GIS software and "
                f"code from the measured open datasets cited in the case study. Not an AI-generated image.")
    return (f"{kind} by {AUTHOR}. Rendered by GIS software and code from measured open geospatial data. "
            f"Not an AI-generated image.")


def exif_bytes(desc: str) -> bytes:
    e = Image.Exif()
    e[0x010E] = desc                                   # ImageDescription
    e[0x013B] = AUTHOR                                 # Artist
    e[0x8298] = f"© {YEAR} {AUTHOR}"                   # Copyright
    e[0x0131] = SOFTWARE                               # Software
    e[0x0132] = f"{YEAR}:11:12 00:00:00"               # DateTime
    b = e.tobytes()
    return b[6:] if b.startswith(b"Exif\x00\x00") else b


def xmp_bytes(desc: str) -> bytes:
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xmp="http://ns.adobe.com/xap/1.0/"
 xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/" xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/"
 xmlns:xmpRights="http://ns.adobe.com/xap/1.0/rights/">
<dc:creator><rdf:Seq><rdf:li>{AUTHOR}</rdf:li></rdf:Seq></dc:creator>
<dc:rights><rdf:Alt><rdf:li xml:lang="x-default">© {YEAR} {AUTHOR}</rdf:li></rdf:Alt></dc:rights>
<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{esc(desc)}</rdf:li></rdf:Alt></dc:description>
<photoshop:Credit>{AUTHOR}</photoshop:Credit>
<xmp:CreatorTool>{esc(SOFTWARE)}</xmp:CreatorTool>
<xmpRights:Marked>True</xmpRights:Marked>
<Iptc4xmpExt:DigitalSourceType>http://cv.iptc.org/newscodes/digitalsourcetype/dataDrivenMedia</Iptc4xmpExt:DigitalSourceType>
</rdf:Description></rdf:RDF></x:xmpmeta>
<?xpacket end="w"?>""".encode("utf-8")


def chunk(tag: bytes, data: bytes) -> bytes:
    return tag + struct.pack("<I", len(data)) + data + (b"\x00" if len(data) % 2 else b"")


def tag_webp(p: Path, desc: str):
    raw = p.read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", p
    chunks, i = [], 12
    while i + 8 <= len(raw):
        t, n = raw[i:i + 4], struct.unpack("<I", raw[i + 4:i + 8])[0]
        chunks.append((t, raw[i + 8:i + 8 + n])); i += 8 + n + (n % 2)
    chunks = [(t, d) for t, d in chunks if t not in (b"EXIF", b"XMP ")]
    with Image.open(io.BytesIO(raw)) as im:
        w, h, alpha = im.width, im.height, "A" in im.mode
    if chunks[0][0] == b"VP8X":
        flags = chunks[0][1][0] | 0x08 | 0x04
        chunks[0] = (b"VP8X", bytes([flags]) + chunks[0][1][1:])
    else:
        flags = 0x08 | 0x04 | (0x10 if alpha and chunks[0][0] == b"VP8L" else 0)
        vp8x = bytes([flags, 0, 0, 0]) + (w - 1).to_bytes(3, "little") + (h - 1).to_bytes(3, "little")
        chunks.insert(0, (b"VP8X", vp8x))
    chunks += [(b"EXIF", exif_bytes(desc)), (b"XMP ", xmp_bytes(desc))]
    body = b"WEBP" + b"".join(chunk(t, d) for t, d in chunks)
    out = b"RIFF" + struct.pack("<I", len(body)) + body
    with Image.open(io.BytesIO(out)) as chk:                 # must still decode to identical pixels
        chk.load()
        with Image.open(io.BytesIO(raw)) as orig:
            assert chk.tobytes() == orig.tobytes(), p
    p.write_bytes(out)


def tag_png(p: Path, desc: str):
    with Image.open(p) as im:
        im.load()
        info = PngImagePlugin.PngInfo()
        for k, v in [("Title", p.stem), ("Author", AUTHOR), ("Description", desc),
                     ("Copyright", f"© {YEAR} {AUTHOR}"), ("Software", SOFTWARE)]:
            info.add_itxt(k, v)
        info.add_itxt("XML:com.adobe.xmp", xmp_bytes(desc).decode("utf-8"))
        buf = io.BytesIO(); im.save(buf, "PNG", pnginfo=info, optimize=True)
    p.write_bytes(buf.getvalue())


n = 0
for p in sorted(ROOT.rglob("*")):
    if p.name in SKIP or p.suffix.lower() not in (".webp", ".png"):
        continue
    d = describe(p)
    head = p.read_bytes()[:12]
    tag_webp(p, d) if head[:4] == b"RIFF" and head[8:12] == b"WEBP" else tag_png(p, d)
    n += 1
print(f"tagged {n} images", file=sys.stderr)
