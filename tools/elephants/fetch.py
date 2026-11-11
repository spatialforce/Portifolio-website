"""Download the Movebank Data Repository files, resuming when the connection drops.

    python fetch.py    # writes cache/
"""
import os
import sys
import time

import requests

H = {"User-Agent": "Mozilla/5.0"}
B = "https://datarepository.movebank.org/server/api/core/bitstreams/"
FILES = {
    # Tsalyuk et al. 2018, Etosha National Park, CC BY-NC 4.0
    "etosha.csv.zip": "b0eb0919-9265-40c5-953c-770abc223e08",
    "etosha_ref.csv": "a6b84691-a1e1-4cc5-a3d3-4bed21d6d670",
    "etosha_fence.zip": "52dd67d4-5788-4f48-a85e-48f559be66bb",
    "etosha_README.txt": "98567d0d-83d5-4503-8280-2071208bd0b4",
    # Thaker et al. 2019, Kruger National Park, CC0
    "kruger.csv": "10240da1-0a99-42bf-a34f-eff15883bbfb",
    "kruger_ref.csv": "715e38b3-1339-4f8c-a997-c27c219de4c9",
    "kruger_README.txt": "09bb9678-356b-4bff-a950-cfa9217fc240",
}
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")


def get(name, uid):
    path = os.path.join(CACHE, name)
    size = requests.get(B + uid, headers=H, timeout=60).json()["sizeBytes"]
    for _ in range(60):
        have = os.path.getsize(path) if os.path.exists(path) else 0
        if have >= size:
            print(name, size // 1024, "KB")
            return
        try:
            with requests.get(B + uid + "/content", headers={**H, "Range": f"bytes={have}-"}, stream=True, timeout=120) as r:
                with open(path, "ab" if r.status_code == 206 else "wb") as f:
                    for chunk in r.iter_content(1 << 16):
                        f.write(chunk)
        except Exception as e:
            print(" ", name, "dropped at", have // 1024, "KB:", type(e).__name__)
            time.sleep(3)
    sys.exit(f"{name}: gave up")


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    for n, u in FILES.items():
        get(n, u)
