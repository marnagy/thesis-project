import OSMParser as osmp
import random
import overpy
from pprint import pprint
import lzma
import pickle
import requests

api = overpy.Overpass()

with open("gps_coords.txt", "r") as f:
    amount = int(f.readline())
    coordinates = [None] * amount
    for i in range(amount):
        coordinates[i] = list(map(float, f.readline().split(';')))
    
for c in coordinates:
    c.reverse()

#print(coordinates)

left = min(map(lambda x: x[0], coordinates))
right = max(map(lambda x: x[0], coordinates))
top = max(map(lambda x: x[1], coordinates))
bottom = min(map(lambda x: x[1], coordinates))

nums = [left, bottom, right, top]
print("Nums: {}".format(nums))

query_str = '''area[name="Praha"];
    way(area)[highway][name];
    out;'''

# query_str = '''<osm-script output="json">
#         <query type="way">
#         <has-kv k="highway" v="motorway"/>
#         <bbox-query ({0},{1},{2},{3})/>
#         </query>
#     <print mode="body"/>
#     <recurse type="down"/>
#     <print mode="skeleton"/>
#     </osm-script>'''.format(left,
#         bottom, right, top)
print("Getting result...")
print(query_str)
result = api.query(query_str)
print("Result received")