# Download each band of the exported asset into rast/<name>.tif (tiled, via dl() from fetch_pred.py).
import sys, ee
exec(open("fetch_pred.py").read().split("for n in (sys.argv")[0])
stk = ee.Image("projects/directed-sun-490915-m4/assets/hwange_stack")
for n in L:
    dl(stk.select(n).toByte() if n == "worldcover" else stk.select(n), n, n=2)
