# Batch-export the predictor + comparison stack to an EE asset (interactive medians time out).
import sys, ee
sys.argv = ["x", "__none__"]
exec(open("fetch_pred.py").read().split("for n in (sys.argv")[0])
names = list(L)
stk = ee.Image.cat([L[n].toFloat().rename(n) for n in names])
aid = "projects/directed-sun-490915-m4/assets/hwange_stack"
t = ee.batch.Export.image.toAsset(stk, description="hwange_stack", assetId=aid, crs="EPSG:32735",
    crsTransform=[R, 0, x0, 0, -R, y1], dimensions=f"{W}x{H}", maxPixels=1e10)
t.start(); print(t.id, names)
