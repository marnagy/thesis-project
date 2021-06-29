import requests
import json
import os
from sys import stdin
from tqdm import tqdm

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
}

ors_key_file = "ors_key.txt"
ors_key = None
if ors_key_file not in os.listdir():
    print(f'Missing file {ors_key_file} in current directory {os.getcwd()}')
    exit()

with open(ors_key_file, "r") as kf:
	ors_key = kf.readline()

def get_coords(addr: str):
    resp = requests.get('https://api.openrouteservice.org/geocode/search?api_key={}&text={}'.format(ors_key, addr), headers=headers)
    assert resp.status_code == 200
    json_obj = json.loads(resp.text)
    return json_obj["features"][0]["geometry"]["coordinates"]

addresses = list(filter(lambda x: len(x) > 0, stdin.readlines()))

coordinates = list()
for addr in tqdm(addresses, ascii=True):
    coordinates.append( get_coords(addr) )

for coord in coordinates:
    print( "{};{}".format(coord[1], coord[0]) )
