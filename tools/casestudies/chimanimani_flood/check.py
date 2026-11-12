"""Independent check of the AHP map against the RMCA (2025) mapped debris-rich flow zones (not used to build it).
ROC AUC of the FSI (flood cells vs all other district cells) and share of flood cells per class -> out/check.json."""
import json, numpy as np
S = np.load("rast/stack.npz"); m = S["mask"] == 1; fz = (S["inv"] == 3) & m
fsi, cls = np.load("rast/fsi.npy"), np.load("rast/fcls.npy")
pos, neg = fsi[fz], fsi[m & ~fz]
r = np.concatenate([pos, neg]).argsort().argsort() + 1.0  # ranks (ties negligible on a continuous index)
auc = (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
share = [round(float((cls[fz] == c).mean() * 100), 1) for c in range(1, 6)]
out = {"flood_km2": round(float(fz.sum() * 0.0009), 2), "auc": round(float(auc), 3), "flood_share_by_class": share}
json.dump(out, open("out/check.json", "w"), indent=1); print(out)
