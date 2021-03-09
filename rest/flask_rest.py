if __name__ != "__main__":
    print("This file should NOT be used as module.")
    exit()

#print("Loading modules...")
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_restful import Resource, Api, reqparse
from typing import List
from datetime import datetime
from math import sqrt
import osmnx as ox
import os
from visualization import Point, Warehouse

print("Loading map data...")
ox.config(use_cache=True)
graph = ox.graph_from_xml("prague_map.osm")
print("Adding speeds to edges...")
graph = ox.add_edge_speeds(graph)
graph = ox.add_edge_travel_times(graph)

app = Flask(__name__)
api = Api(app)
#print("Adding API paths...")

class HelloWorld(Resource):
    def get(self):
        return {'Server': 'works!'}

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

def get_node(lat: int, lon: int):
    node = ox.get_nearest_node(graph, point=(lat, lon))
    return node

def get_node(point):
    node = ox.get_nearest_node(graph, point=(point.lat, point.lon))
    return node

def get_route(point1, point2, weight: str):
    node1 = get_node(point1)
    node2 = get_node(point2)
    route = ox.shortest_path(graph, node1, node2,
                weight=weight)
    return route

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
        try:
            node_path = ox.shortest_path(graph, start_node, dest_node,
                weight='travel_time')
            times = ox.utils_graph.get_route_edge_attributes(graph, node_path,
                attribute='travel_time')
            time = sum(times)
            #print("Time needed: {}".format(time) )
            return {
                'travel_time': time
            }
        except:
            return {
                'travel_time': 10_000
            }

class FinalGraph(Resource):
    def post(self):
        wh_chr_json = request.get_json()
        #print("Received JSON: {}".format(wh_chr_json))
        # load object from json
        warehouses_json = wh_chr_json['chromosome']
        warehouses = []
        #print("Received JSON: {}".format(warehouses_json))
        for wh_json in warehouses_json:
            warehouses.append( Warehouse.from_json(wh_json) )
        # print("Loaded warehouses:")
        # for wh in warehouses:
        #     print(wh)
        # get routes
        colors = ['r', 'g', 'c', 'm', 'y']
        routes = []
        for wh in warehouses:
            for i in range(len(wh.routes)):
                route = wh.routes[i]
                points = [wh.point] + route
                # print("Route points:")
                # for point in points:
                #     print(point)
                for p1, p2 in [ (points[i], points[i+1]) for i in range(-1, len(points) - 1)]:
                    #print("Getting route between: {} and {}".format(p1, p2))
                    routes.append( (get_route(p1, p2, weight='traveltime'), colors[i]) )
        print("Amount of routes: {}".format(len(routes)))
        # print("Routes:")
        # for route in routes:
        #     print(route)
        dt = datetime.now()
        filename = "figure_{}_{}_{}-{}_{}_{}.png".format(
            dt.second, dt.minute, dt.hour, dt.day, dt.month, dt.year
        )
        _, _ = ox.plot_graph_routes(
            graph,
            figsize=(150, 150),
            route_colors=list(map(lambda x: x[1], routes)),
            routes=list(map(lambda x: x[0], routes)),
            route_linewidth=5,
            route_alpha=0.5,
            node_size=5,
            edge_linewidth=1,
            dpi=100,
            show=False,
            save=True,
            filepath=os.path.join(os.getcwd(), filename)
        )
        # load data to list
        # with open(filename, "rb") as fig_file:
        #     data = list(fig_file.read())
        
        return send_from_directory('.', filename) #send_file(filename)

# path_put_args = reqparse.RequestParser()
# path_put_args.add_argument("points", type=list, help="Points of a cycle", required=True)

class Path(Resource):
    def post(self):
        #args = path_put_args.parse_args()
        args = request.get_json()
        points = args['points']
        #distances = [ get_eukl_distance(tuple(points[0]), tuple(points[1])) for points in zip(points[-1:], points[:]) ]
        distances = list(
            map(
                lambda x: get_eukl_distance(tuple(points[x]), tuple(points[x+1])),
                range(-1, len(points) - 1)
                )
            )
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
#api.add_resource(FinalGraph, '/graph')

if __name__ == '__main__':
    app.run(port=5_000, threaded=True)
    #app.run(port=5_000, debug=True)