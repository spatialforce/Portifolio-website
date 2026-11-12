# AHP pairwise matrix, weights (principal eigenvector), consistency ratio.
# Judgements follow the literature consensus for utility-scale PV siting:
# GHI strongest (Al Garni & Awasthi 2017; Doorga et al. 2019; Mutume 2023),
# grid distance second (Noorollahi et al. 2016; Sanchez-Lozano et al. 2013),
# then slope, roads, land cover, settlements.
import numpy as np

CRITERIA = ["GHI", "Distance to grid", "Slope", "Distance to roads",
            "Land cover", "Distance to settlements"]

# Saaty 1-9 scale, row relative to column.
#        GHI  GRID SLOPE ROAD  LC   SETT
A = np.array([
    [1,   3,   4,    5,   5,   7],    # GHI
    [1/3, 1,   2,    3,   3,   5],    # grid
    [1/4, 1/2, 1,    2,   2,   4],    # slope
    [1/5, 1/3, 1/2,  1,   1,   3],    # roads
    [1/5, 1/3, 1/2,  1,   1,   3],    # land cover
    [1/7, 1/5, 1/4,  1/3, 1/3, 1],    # settlements
])

RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}

def weights_cr(M):
    vals, vecs = np.linalg.eig(M)
    k = np.argmax(vals.real)
    w = np.abs(vecs[:, k].real)
    w = w / w.sum()
    lam = vals[k].real
    n = M.shape[0]
    CI = (lam - n) / (n - 1)
    return w, lam, CI, CI / RI[n]

if __name__ == "__main__":
    w, lam, CI, CR = weights_cr(A)
    for c, x in zip(CRITERIA, w):
        print(f"{c:26s} {x:.3f}")
    print(f"lambda_max {lam:.3f}  CI {CI:.4f}  CR {CR:.4f}")
