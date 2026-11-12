# AHP weights for landfill siting (Saaty 1980). Surface water and settlements carry
# the most weight, as in Sener et al. (2006) and later GIS landfill studies.
import numpy as np
CRITERIA = ["Distance from settlements", "Distance from surface water", "Soil clay", "Slope", "Distance to roads", "Land cover"]
A = np.array([
    [1,   1,   3,   3,   4,   5],
    [1,   1,   3,   3,   4,   5],
    [1/3, 1/3, 1,   1,   2,   3],
    [1/3, 1/3, 1,   1,   2,   3],
    [1/4, 1/4, 1/2, 1/2, 1,   2],
    [1/5, 1/5, 1/3, 1/3, 1/2, 1]])
RI = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}
def weights_cr(M):
    v, V = np.linalg.eig(M); k = np.argmax(v.real); w = np.abs(V[:, k].real); w /= w.sum()
    lam = v[k].real; n = len(M); CI = (lam - n) / (n - 1); return w, lam, CI, CI / RI[n]
if __name__ == "__main__":
    w, lam, CI, CR = weights_cr(A)
    for c, x in zip(CRITERIA, w): print(f"{c:30s} {x:.3f}")
    print(f"lambda {lam:.3f} CI {CI:.4f} CR {CR:.4f}")
