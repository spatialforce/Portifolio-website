"""Add a faint brightness grain to map and chart images, like the sensor noise of a scan or photo.

Whites are lifted to about 252 so the grain is not clipped, then monochrome Gaussian noise of
SIGMA levels (out of 255) is added and the image is saved as lossy WebP at QUALITY.
After WebP compression about one level of grain remains; colours move by about 2 levels, which
cannot be seen. Files ending in .png are left alone (grain would triple their size).
Re-encoding drops metadata, so run tag_images.py afterwards.

Usage: python tools/provenance/grain.py SOURCE_DIR [file ...]
  SOURCE_DIR holds clean copies of src/assets, so grain is never applied twice.
"""
import io, sys, zlib
from pathlib import Path
import numpy as np
from PIL import Image

ASSETS = Path(__file__).resolve().parents[2] / "src" / "assets"
SKIP = {"myself.webp", "profile_1.webp", "hero.webp", "storymap_mapping.webp", "storymap_wildlife.webp"}
SIGMA, QUALITY = 2.0, 86


def grain(src: Path, dst: Path):
    with Image.open(src) as im:
        im.load()
        alpha = im.convert("RGBA").getchannel("A") if "A" in im.getbands() else None
        a = np.asarray(im.convert("RGB")).astype(np.float32)
    rng = np.random.default_rng(zlib.crc32(dst.name.encode()))
    a = a * (249 / 255) + 3 + rng.normal(0, SIGMA, a.shape[:2])[..., None]
    out = Image.fromarray(np.clip(np.rint(a), 0, 255).astype(np.uint8), "RGB")
    if alpha is not None:
        out.putalpha(alpha)
    buf = io.BytesIO()
    out.save(buf, "WEBP", quality=QUALITY, method=6)
    dst.write_bytes(buf.getvalue())
    return src.stat().st_size, len(buf.getvalue())


src_root = Path(sys.argv[1])
rels = [Path(f).resolve().relative_to(ASSETS) for f in sys.argv[2:]] or [
    p.relative_to(src_root) for p in sorted(src_root.rglob("*.webp")) if p.name not in SKIP]
t0 = t1 = 0
for rel in rels:
    b0, b1 = grain(src_root / rel, ASSETS / rel)
    t0 += b0; t1 += b1
    print(f"{str(rel):60s} {b0/1024:6.0f} KB -> {b1/1024:6.0f} KB")
print(f"{len(rels)} images, {t0/1048576:.1f} MB -> {t1/1048576:.1f} MB")
