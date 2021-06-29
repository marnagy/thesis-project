from geopy.geocoders import Nominatim
from sys import stdin
from tqdm import tqdm

addresses = list(filter(lambda x: len(x) > 0, stdin.readlines()))

nom = Nominatim(user_agent="test_app")
coordinates = list()
for addr in tqdm(addresses, ascii=True):
    geopoint = nom.geocode(addr)
    coordinates.append( (geopoint.latitude, geopoint.longitude) )

for code in coordinates:
    print("{};{}".format(code[0], code[1]))