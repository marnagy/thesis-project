import requests
from pprint import pprint
import json

#body = {"coordinates":[[8.681495,49.41461],[8.686507,49.41943]]}
coordinates = []
with open("gps_coords.txt", "r") as gpsf:
    amount = int(gpsf.readline().strip('\n'))
    for _ in range(amount):
        coordinates.append( list(map(float, gpsf.readline().split(';'))) )
body = {"coordinates":coordinates,
    "instructions":"false",
    "geometry":"false"
    }

headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': '5b3ce3597851110001cf624838b03c85b4e9460d81ac362a626348ba',
    'Content-Type': 'application/json; charset=utf-8'
}
call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car', json=body, headers=headers)

print(call.status_code, call.reason)
pprint(call.text)
json_obj = json.loads(call.text)
print(json_obj["routes"][0]["summary"]["distance"])
