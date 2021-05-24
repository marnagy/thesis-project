import requests
import json
import os
from sys import stdin

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
}
ors_key = None
assert "ors_key.txt" in os.listdir()
with open("ors_key.txt", "r") as kf:
	ors_key = kf.readline()

def get_coords(addr: str):
    resp = requests.get('https://api.openrouteservice.org/geocode/search?api_key={}&text={}'.format(ors_key, addr), headers=headers)
    assert resp.status_code == 200
    json_obj = json.loads(resp.text)
    return json_obj["features"][0]["geometry"]["coordinates"]

adresses = list(filter(lambda x: len(x) > 0, stdin.readlines()))

coordinates = [ get_coords(addr) for addr in adresses ]

for coord in coordinates:
    print( "{};{}".format(coord[1], coord[0]) )
