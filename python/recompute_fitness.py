from typing import List
from argparse import ArgumentParser, Namespace
import requests

from data import Point, Warehouse

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
    parser.add_argument("-t", "--type", default="time", type=str, help="Options: [time, distance]")

    args = parser.parse_args(None)

    if args.type not in ['time', 'distance']:
        raise Exception('Type needs to be [time, distance].')

    return args

def get_value(url: str, ret_attr: str, p1: Point, p2: Point) -> float:
    resp = requests.get('{}/{}:{};{}:{}'.format(
        url,
        p1.lat, p1.lon, p2.lat, p2.lon
    ))
    return resp.json()[ret_attr]

def recompute(whs: List[Warehouse], type: str) -> float:
    url = 'http://localhost:5000'
    ret_attr = None

    if type == 'time':
        url = url + '/traveltime'
        ret_attr = 'travel_time'
    elif type == 'distance':
        url = url + '/shortest'
        ret_attr = 'meters_distance'
    
    result = 0
    for wh in whs:
        if wh.routes is None:
            continue
        for r in wh.routes:
            route = [wh.point] + r
            route_result = 0
            for i in range(-1, len(route) - 1):
                route_result += get_value(url, ret_attr, route[i], route[i+1])

            if type == 'time':
                result = max(result, route_result)
            if type == 'distance':
                result += route_result
    
    return result


def load_warehouses(filename: str) -> List[Warehouse]:
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
            #is_fitness_distance = True
            is_point = True
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
    return warehouses

def main():
    args = get_args()
    sol = load_warehouses(args.file_path)
    print(recompute(sol, args.type))

if __name__ == '__main__':
    main()