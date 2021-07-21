import os
import sys
from types import TracebackType
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from typing import List, Tuple
from argparse import ArgumentParser, Namespace

RESULTS_DIR_NAME = "result_visualization"
counter = 0
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
    parser.add_argument("-m", "--map_path", type=str, help="Path of directory containing solutions (.wh files) .", required=True)
    parser.add_argument("-f", "--file_path", default="", type=str, help="Path of directory containing solutions (.wh files) .")

    args = parser.parse_args(None)

    return args

def create_json(warehouses):
    '''Returns json of warehouses.

    :param warehouses: List of Warehouse objects
    :type warehouses: List[Warehouse]
    '''
    return {
        'chromosome': list(map(lambda x: x.json(), warehouses))
    }

def get_node(point: Tuple[float, float]) -> int:
    '''Retrieve closes node on map to the given point.

    :param point: Point to find the closest map node to
    :type point: Point
    '''
    node = ox.get_nearest_node(graph, point=point)
    return node

def get_route(point1: Tuple[float, float], point2: Tuple[float, float], weight: str) -> List[int]:
    node1 = get_node(point1)
    node2 = get_node(point2)
    route = ox.shortest_path(graph, node1, node2, weight=weight)
    return route

def parse_coords(line: str) -> Tuple[float, float]:
    parts = line.split(';')
    assert len(parts) == 2
    return tuple(map(lambda x: double(x), parts))

def load_coordinates(filepath: str) -> List[Tuple[float, float]]:
    with open(filepath, 'r') as f:
        # remove '\n' character at the end of the lines
        lines = list(map(lambda x: x.strip(), f.readlines()))

    return list(
        map(
            parse_coords,
            lines
        )
    )

def check_reachability(coords: List[Tuple[float, float]]) -> Tuple[bool, Tuple[float, float]]:
    success = True
    problem_point = None

    for point1, point2 in [ (coords[i], coords[i+1]) for i in range(-1, len(coords) - 1)]:
        try:
            _ = get_route(point1, point2, 'length')
        except nx.NetworkXNoPath:
            success = False
            problem_point = point2
            break
    return success, problem_point

def main():
    global graph
    args = get_args()
    map_file_path = args.map_path

    filename = args.file_path
    print("Loading from file {}".format(filename))
    coordinates = load_coordinates(filename)

    print("Loading map data...")
    graph = ox.load_graphml(map_file_path)

    success, problem_point = check_reachability(coordinates)
    if success:
        print('All points are reachable')
    else:
        print('NOT all points are reachable')
        print('Problem point: {}'.format(problem_point))

if __name__ == "__main__":
    main()