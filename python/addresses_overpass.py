from overpy import Overpass
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--amount", default=50, type=int, help="Amount of shops to get.")

args = parser.parse_args(None)

api = Overpass()

query_str = '''area[name="Praha"];
node[shop="supermarket"](area);
out;'''

result = api.query(query_str)

nodes_lat_lon = list(map(lambda x: (float(x.lat), float(x.lon)), result.nodes))

if len(nodes_lat_lon) >= args.amount:
    print(args.amount)
    for node in random.choices(nodes_lat_lon, k=args.amount):
        print("{};{}".format(node[0],node[1]))
else:
    print(len(nodes_lat_lon))
    for node in nodes_lat_lon:
        print("{};{}".format(node[0],node[1]))
