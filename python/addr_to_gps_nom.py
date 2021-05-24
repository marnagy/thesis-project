from geopy.geocoders import Nominatim
from sys import stdin

adresses = list(filter(lambda x: len(x) > 0, stdin.readlines()))

nom = Nominatim(user_agent="test_app")
coordinates = list(
    map(
        lambda x: (x.latitude, x.longitude),
        map(
            nom.geocode, adresses
            )
        )
    )

for code in coordinates:
    print("{};{}".format(code[0], code[1]))