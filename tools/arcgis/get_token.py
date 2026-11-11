"""Get a one-hour ArcGIS Online token and save it to tools/arcgis/.token (kept out of git).

    python tools/arcgis/get_token.py

The password is typed here and sent only to arcgis.com. The token works only from this computer's
internet address and expires after an hour.
"""
import getpass
import json
import os
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

user = input("ArcGIS username [kudzanai0101]: ").strip() or "kudzanai0101"
password = getpass.getpass("ArcGIS password (hidden): ")
body = urllib.parse.urlencode({"username": user, "password": password, "client": "requestip",
                               "expiration": 60, "f": "json"}).encode()
with urllib.request.urlopen("https://www.arcgis.com/sharing/rest/generateToken", body, timeout=30) as r:
    res = json.load(r)
if "token" not in res:
    raise SystemExit("ArcGIS said: " + json.dumps(res.get("error", res)))
with open(os.path.join(HERE, ".token"), "w") as f:
    json.dump({"user": user, "token": res["token"], "expires": res["expires"]}, f)
print("Token saved. It expires in an hour.")
