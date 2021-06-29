from collections import defaultdict
from typing import List, Tuple
from argparse import ArgumentParser, Namespace
import requests
from tqdm import tqdm
import osmnx as ox

from data import Point, Warehouse

graph = None

def double(number: str) -> float:
    '''Convert string containing double with , to Python float object

    :param number: Text representation of float number
    :type number: str
    :return: converted number
    :rtype: float
    '''
    return float(number.replace(',', '.'))

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-f", "--file_path", type=str, help="Path to a .wh file containing solution.", required=True)
    parser.add_argument('-m', '--map_file', type=str, help='Path to graphml map file.', required=True)
    parser.add_argument("-t", "--type", default="time", type=str, help="Options: [time, distance]")

    args = parser.parse_args(None)

    if args.type not in ['time', 'distance']:
        raise Exception('Type needs to be [time, distance].')

    return args

def get_node(point):
    node = ox.get_nearest_node(graph, point=(point.lat, point.lon))
    return node

def get_value(p1: Point, p2: Point, weight: str) -> float:
    route = ox.shortest_path(graph, get_node(p1), get_node(p2), weight)
    res = sum( ox.utils_graph.get_route_edge_attributes(graph, route, weight) )
    return res

def recompute(whs: List[Warehouse], type: str) -> float:    
    weight = 'travel_time' if type == 'time' else 'length'
    result = 0
    for wh in whs:
        if wh.routes is None:
            continue
        for r in wh.routes:
            route = [wh.point] + r
            route_result = 0
            for i in range(-1, len(route) - 1):
                route_result += get_value(route[i], route[i+1], weight)

            if type == 'time':
                result = max(result, route_result)
            if type == 'distance':
                result += route_result
    
    return result


def load_warehouses(filename: str) -> Tuple[float, float, List[Warehouse]]:
    '''Loads warehouses from given file.

    :param filename: Path to file
    :type filename: str
    :return: Loaded Warehouses of solution
    :rtype: List[Warehouse]
    '''
    warehouses = []
    json_obj = {}
    lines = None
    with open(filename, mode="r") as in_file:
        lines = list(map(lambda x: x.strip(), in_file.readlines()))
    is_fitness_time = True
    is_fitness_distance = False
    is_point = False
    is_route = False

    wh_point = None
    fitness_time = 0
    fitness_distance = 0
    routes = None
    for line in lines:
        if is_fitness_time and (not is_fitness_distance) and (not is_point) and (not is_route):
            fitness_time = double(line)
            is_fitness_time = False
            is_fitness_distance = True
            #is_point = True
            continue
            
        if is_fitness_distance and (not is_fitness_time) and (not is_point) and (not is_route):
            fitness_distance = double(line)
            is_fitness_distance = False
            is_point = True
            continue
            
        if is_point and not is_route:
            lineParts = line.split(';')
            wh_point = Point( double(lineParts[0]), double(lineParts[1]) )
            is_point = False
            is_route = True
            continue

        if is_route and not is_point:
            if line == "###":
                wh = Warehouse(wh_point)
                #print("Routes:")
                for route in routes:
                    wh.add_route( route )
                wh.add_fitness(fitness_time, fitness_distance)
                routes = []
                fitness = None
                warehouses.append( wh )
                is_point = True
                is_route = False
                continue
            doubles = list(map(double, line.split(';'))) 
            points = [ Point(d1, d2) for d1, d2 in zip(doubles[::2], doubles[1::2]) ]
            if routes is None:
                routes = [ points ]
            else:
                routes.append(points)
    return (fitness_time, fitness_distance, warehouses)

def main():
    global graph
    args = get_args()
    graph = ox.load_graphml(args.map_file)
    time_fit, distance_fit, warehouses = load_warehouses(args.file_path)
    print('Computed: {}'.format( recompute(warehouses, args.type) ) )
    print('Saved: {}'.format( time_fit if args.type == 'time' else distance_fit ) )

if __name__ == '__main__':
    main()