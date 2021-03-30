# if __name__ != "__main__":
#     print("This file should NOT be used as module.")
#     exit()

#print("Loading modules...")
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from typing import List
from datetime import datetime
from math import sqrt
import osmnx as ox
import os
import sys

# custom datatypes
from visualization import Point, Warehouse


#print("Adding API paths...")

class HelloWorld(Resource):
    """Hello world docstring"""
    def get(self):
        """Method used for testing

            :return: {'Hello': 'world!'}
        """
        return {'Hello': 'world!'}

def get_eukl_distance(point1, point2):
    '''Simple euklidian distance in 2D plain.

        :type point1: tuple of length 2 containing 2 numerical values
        :type point2: tuple of length 2 containing 2 numerical values
        :return: distance
        :rtype: float
    '''    
    return sqrt( (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

def get_node_distance(point1, point2):
    '''
        Get distance of 2 point on map.

        :type point1: tuple of length 2 containing 2 numerical values
        :type point2: tuple of length 2 containing 2 numerical values
        :return: distance
        :rtype: float
    '''
    node1 = get_node( Point(point1[0], point1[1]) )
    node2 = get_node( Point(point2[0], point2[1]) )
    path = ox.shortest_path(graph, node1, node2)
    return ox.utils_graph.get_route_edge_attributes(graph, path, 'length')

def get_node(point):
    '''
        Get map node closest to the given coordinates.

        :param point: geographical point
        :type point: Point
        :return: node ID
        :rtype: integer
    '''
    node = ox.get_nearest_node(graph, point=(point.lat, point.lon))
    return node

def get_route(point1, point2, weight: str):
    '''
        Get best route depending on `weight` attribute.

        :param point1: geographical point
        :type point1: Point
        :param point2: geographical point
        :type point2: Point
        :param weight: key attribute of edge
        :type weight: string
        :return: best route in aspect to `weight` attribute
        :rtype: list of integers
    '''
    node1 = get_node(point1)
    node2 = get_node(point2)
    route = ox.shortest_path(graph, node1, node2,
                weight=weight)
    return route

class Distance(Resource):
    '''
        Get distance on map from url arguments.
    '''
    def get(self, start_lat: float, start_lon: float, dest_lat: float, dest_lon: float):
        '''Function for HTTP method GET.

        :param start_lat: latitude value for starting point
        :type start_lat: float
        :param start_lon: longitude value for starting point
        :type start_lon: float
        :param dest_lat: latitude value for destination point
        :type dest_lat: float
        :param dest_lon: longitude value for destination point
        :type dest_lon: float
        :return: distance
        :rtype: JSON
        '''
        start_node = get_node( Point(start_lat, start_lon) )
        dest_node = get_node( Point(dest_lat, dest_lon) )
        node_path = ox.shortest_path(graph, start_node, dest_node,
            weight='length')
        distances = ox.utils_graph.get_route_edge_attributes(graph, node_path,
            attribute='length')
        distance = sum(distances)        
        return {
            'meters_distance': distance
        }

class TravelTime(Resource):
    '''
        Get travel time on map from url arguments.
    '''
    def get(self, start_lat: float, start_lon: float, dest_lat: float, dest_lon: float):
        '''Function for HTTP method GET.

        :param start_lat: latitude value for starting point
        :type start_lat: float
        :param start_lon: longitude value for starting point
        :type start_lon: float
        :param dest_lat: latitude value for destination point
        :type dest_lat: float
        :param dest_lon: longitude value for destination point
        :type dest_lon: float
        :return: travel time
        :rtype: JSON
        '''
        start_node = get_node( Point(start_lat, start_lon) )
        dest_node = get_node( Point(dest_lat, dest_lon) )
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

if __name__ == '__main__':
    args = sys.argv[1:]
    map_filename = args[0]

    print("Loading map data...")
    ox.config(use_cache=True)
    graph = ox.graph_from_xml(map_filename)
    print("Adding speeds to edges...")
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)

    app = Flask(__name__)
    api = Api(app)

    # Add endpoints
    api.add_resource(HelloWorld, '/')
    #api.add_resource(DateTime, '/datetime')
    api.add_resource(Distance, '/shortest/<float:start_lat>:<float:start_lon>;<float:dest_lat>:<float:dest_lon>')
    api.add_resource(TravelTime, '/traveltime/<float:start_lat>:<float:start_lon>;<float:dest_lat>:<float:dest_lon>')
    #api.add_resource(Path, '/path')
    #api.add_resource(FinalGraph, '/graph')

    app.run(host='0.0.0.0', port=5_000, debug=True, threaded=True)
    #app.run(port=5_000, debug=True)