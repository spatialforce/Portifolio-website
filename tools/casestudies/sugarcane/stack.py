# Mosaic the monthly tiles into one stack per index: out arrays float32 (month, row, col), NaN where no clear data.
import glob, numpy as np, rasterio
from rasterio.merge import merge
MONTHS = [(y, m) for y in range(2019, 2026) for m in range(1, 13)]
def load(ix):
    arr = None
    for k, (y, m) in enumerate(MONTHS):
        srcs = [rasterio.open(f"rast/{ix}_{y}{m:02d}_{t}.tif") for t in (0, 1)]
        a, tr = merge(srcs, nodata=0); a = a[0].astype("float32")
        if arr is None:
            arr = np.full((len(MONTHS),) + a.shape, np.nan, "float32"); prof = srcs[0].profile; prof.update(transform=tr, width=a.shape[1], height=a.shape[0], count=1)
        a[a == 0] = np.nan; arr[k] = (a - 100) / 100
        for s in srcs: s.close()
    return arr, prof
if __name__ == "__main__":
    for ix in ("ndvi", "ndmi"):
        a, prof = load(ix)
        np.savez_compressed(f"rast/{ix}_stack.npz", a=a.astype("float16"), transform=np.array(prof["transform"])[:6], crs=str(prof["crs"]))
        print(ix, a.shape, "clear share by month (first 12):", np.round(np.isfinite(a).mean(axis=(1, 2))[:12], 2))
