debug = True

#import requests
import sys
import re
import json
from datetime import datetime
import osmnx as ox
import os
#from collections import List

print("Loading map data...")
ox.config(use_cache=True)
graph = ox.graph_from_xml("prague_map.osm")
print("Adding speeds to edges...")
graph = ox.add_edge_speeds(graph)
graph = ox.add_edge_travel_times(graph)

RESULTS_DIR_NAME = "result_photos"
counter = 0

class Point:
    lat = 0
    lon = 0

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
    
    def json(self):
        return {
            'lat': self.lat,
            'lon': self.lon
        }

    @staticmethod
    def from_json(point_json):
        #print("Loading Point from: {}".format(point_json))
        return Point(point_json['lat'], point_json['lon'])

    def __str__(self):
        return "Lat: {}, Lon: {}".format(self.lat, self.lon)

class Warehouse:
    point = None
    routes = None
    fitness = None

    def __init__(self, point: Point):
        self.point = point

    def json(self):
        return {
            'point': self.point.json(),
            'routes': [
                list(map(lambda x: x.json(), route)) for route in self.routes
            ]
        }
    
    def add_route(self, route):
        if self.routes is None:
            self.routes = [ route ]
        else:
            self.routes.append(route)
    
    def add_fitness(self, fitness):
        self.fitness = fitness

    @staticmethod
    def from_json(wh_json):
        #print("Loading JSON from: {}".format(wh_json))
        wh = Warehouse(Point.from_json(wh_json['point']))
        for route in wh_json['routes']:
            #print("Loading route from: {}".format(route))
            r = list(map(lambda x: Point.from_json(x), route))
            wh.add_route(r)
        return wh

    def __str__(self):
        res = """Warehouse:
        Point: {}
        Routes:\n""".format(self.point)
        for route in self.routes:
            r = "["
            for i in range(len(route)):
                point = route[i]
                if i > 0:
                    r += ", "
                r += str(point)
            r += "]"
            res += r + '\n'
        return res

def double(number: str) -> float:
    return float(number.replace(',', '.'))

def validate(filename: str) -> bool:
    return len(filename) > 0 and re.match("^result_[0-9]+\.txt$", filename) is not None

'''
    Loads warehouses from given files.
'''
def load_warehouses(filename):
    warehouses = []
    if True: # validate(filename):
        json_obj = {}
        lines = None
        with open(filename, mode="r") as in_file:
            lines = list(map(lambda x: x.strip(), in_file.readlines()))
        is_fitness = True
        is_point = False
        is_route = False

        wh_point = None
        fitness = None
        routes = None
        for line in lines:
            if is_fitness and (not is_point) and (not is_route):
                fitness = double(line)
                is_fitness = False
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
                    wh.add_fitness(fitness)
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

'''
    Returns json of warehouses.
'''
def create_json(warehouses) :
    return {
        'chromosome': list(map(lambda x: x.json(), warehouses))
    }

def get_and_save_photo(wh_json, filename: str):
    print("JSON to send: {}".format(wh_json))
    print("Getting file...")
    resp = requests.post(url="http://localhost:5000/graph", json=wh_json)
    dt = datetime.now()
    name = "result_{}_{}_{}.png".format(
        dt.second, dt.minute, dt.hour
    )
    with open(name, mode="xb") as out_file:
        out_file.write(resp.content)
    print("File saved as {}".format(name))

def get_node(point):
    node = ox.get_nearest_node(graph, point=(point.lat, point.lon))
    return node

def get_route(point1, point2, weight: str):
    node1 = get_node(point1)
    node2 = get_node(point2)
    route = ox.shortest_path(graph, node1, node2,
                weight=weight)
    return route

plot_colors = ['r', 'g', 'c', 'm', 'y']

def save_routes(warehouses, filename):
    global counter
    counter = 0
    routes_dict = {
        'routes': None,
        'colors': None
    }
    for wh in warehouses:
        #print("Routes amount: {}".format( len(wh.routes) ))
        for route in wh.routes:
        # for i in range(len(wh.routes)):
        #     #print("i: {}".format(i))
        #     route = wh.routes[i]
            points = [wh.point] + route
            for p1, p2 in [ (points[i], points[i+1]) for i in range(-1, len(points) - 1)]:
                graph_route = get_route(p1, p2, "traveltime")
                if routes_dict['routes'] is None:
                    routes_dict['routes'] = [ graph_route ]
                else:
                    routes_dict['routes'].append( graph_route )
                if routes_dict['colors'] is None:
                    routes_dict['colors'] = [ plot_colors[counter % len(plot_colors)] ]
                else:
                    routes_dict['colors'].append( plot_colors[counter % len(plot_colors)] )
            counter += 1
    #print("Amount of routes: {}".format(len(routes_dict['routes'])))
    figure_filename = "{}_map.png".format(filename.split('.')[0])
    print("Creating and saving plot from {} ...".format(filename))
    res_file_path = os.path.join(RESULTS_DIR_NAME, figure_filename)
    _, _ = ox.plot_graph_routes(
        graph,
        figsize=(150, 150),
        dpi=100,
        route_colors=routes_dict['colors'],
        routes=routes_dict['routes'],
        #route_linewidth=10,
        route_alpha=0.5,
        #node_size=30,
        edge_linewidth=1,
        # make route points more visible
        orig_dest_size=500,
        show=False,
        save=True,
        filepath=res_file_path
    )
    print("Routes saved to {}".format(res_file_path))

def save_warehouse_points(warehouses):
    pass

def main():
    args = sys.argv
    directory = args[1]
    # save original directory
    orig_dir = os.getcwd()
    if not os.path.isdir(directory):
        print("Given argument is NOT a directory.")
        return
    # move to the directory
    os.chdir(directory)
    try:
        files = os.listdir()
        if not os.path.exists(RESULTS_DIR_NAME):
            os.mkdir(RESULTS_DIR_NAME)
    except:
        return

    try:
        args = list(map(lambda x: os.path.join(directory, x), files))
        for filename in args:
            if not filename.endswith('.wh'):
                continue
            print("Loading from file {}".format(filename))
            warehouses = load_warehouses(filename)
            save_routes(warehouses, filename.split(os.sep)[-1])
            print()
    finally:
        os.chdir(orig_dir)

if __name__ == "__main__":
    main()