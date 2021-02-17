if __name__ != "__main__":
    print("This file should NOT be used as module.")
    exit()

#print("Loading modules...")
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from typing import List
from datetime import datetime
from math import sqrt
import osmnx as ox

print("Loading map data...")
ox.config(use_cache=True, log_console=True)
graph = ox.graph_from_xml("prague_map.osm")
print("Adding speeds to edges...")
graph = ox.add_edge_speeds(graph)
graph = ox.add_edge_travel_times(graph)

app = Flask(__name__)
api = Api(app)
#print("Adding API paths...")

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class DateTime(Resource):
    def get(self):
        dt = datetime.now()
        dt_dict = {
            'time': {
                'hours': str(dt.hour),
                'minutes': str(dt.minute)
            },
            'date': {
                'day': str(dt.day),
                'month': str(dt.month),
                'year': str(dt.year)
            }
        }
        return dt_dict

def get_eukl_distance(point1, point2):
    return sqrt( (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

def get_node_distance(point1, point2):
    node1 = ox.get_nearest_node(graph, point=point1)
    node2 = ox.get_nearest_node(graph, point=point2)
    path = ox.shortest_path(graph, node1, node2)
    return ox.utils_graph.get_route_edge_attributes(graph, path, 'length')

class Distance(Resource):
    def get(self, start_lat: float, start_lon: float, dest_lat: float, dest_lon: float):
        start_node = ox.get_nearest_node(graph, point=(start_lat, start_lon))
        dest_node = ox.get_nearest_node(graph, point=(dest_lat, dest_lon))
        node_path = ox.shortest_path(graph, start_node, dest_node,
            weight='length')
        distances = ox.utils_graph.get_route_edge_attributes(graph, node_path,
            attribute='length')
        distance = sum(distances)        
        return {
            'meters_distance': distance
        }

class TravelTime(Resource):
    def get(self, start_lat: float, start_lon: float, dest_lat: float, dest_lon: float):
        start_node = ox.get_nearest_node(graph, point=(start_lat, start_lon))
        dest_node = ox.get_nearest_node(graph, point=(dest_lat, dest_lon))
        node_path = ox.shortest_path(graph, start_node, dest_node,
            weight='travel_time')
        times = ox.utils_graph.get_route_edge_attributes(graph, node_path,
            attribute='travel_time')
        time = sum(times)
        print("Time needed: {}".format(time) )
        return {
            'travel_time': time
        }

# path_put_args = reqparse.RequestParser()
# path_put_args.add_argument("points", type=list, help="Points of a cycle", required=True)

class Path(Resource):
    def post(self):
        #args = path_put_args.parse_args()
        args = request.get_json()
        points = args['points']
        #distances = [ get_eukl_distance(tuple(points[0]), tuple(points[1])) for points in zip(points[-1:], points[:]) ]
        distances = list(map(lambda x: get_eukl_distance(tuple(points[x]), tuple(points[x+1])), range(-1, len(points) - 1)))
        distance = sum(distances)
        return {
            'distance': distance
            #'distances': distances,
            #'received': points
        }
        # points = list(map(tuple, args['points']))
        # graph_nodes = list(map(lambda point: ox.get_nearest_node(graph, point=point), points))
        # paths = [ ox.shortest_path(graph, start_node, dest_node) for p1, p2 in zip(graph_nodes[-1:], graph_nodes) ]
        # distances = list(map(lambda path: ox.utils_graph.get_route_edge_attributes(graph, path, 'length'), paths))
        # distance = sum(distances)
        # return {
        #     'distance': distance
        # }

api.add_resource(HelloWorld, '/')
api.add_resource(DateTime, '/datetime')
api.add_resource(Distance, '/shortest/<float:start_lat>:<float:start_lon>;<float:dest_lat>:<float:dest_lon>')
api.add_resource(TravelTime, '/traveltime/<float:start_lat>:<float:start_lon>;<float:dest_lat>:<float:dest_lon>')
api.add_resource(Path, '/path')

if __name__ == '__main__':
    #app.run(port=5_000, debug=True, threaded=True)
    app.run(port=5_000, threaded=True)