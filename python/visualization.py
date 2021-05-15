import os
import sys
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from typing import List
from argparse import ArgumentParser, Namespace
from data import Warehouse, Point
#from collections import List

# print("Loading map data...")
# ox.config(use_cache=True)
# graph = ox.graph_from_xml("prague_map.osm")
# print("Adding speeds to edges...")
# graph = ox.add_edge_speeds(graph)
# graph = ox.add_edge_travel_times(graph)

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

# def validate(filename: str) -> bool:
#     '''[summary]

#     :param filename: [description]
#     :type filename: str
#     :return: [description]
#     :rtype: bool
#     '''
#     return len(filename) > 0 and re.match("^result_[0-9]+\.txt$", filename) is not None

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-m", "--map_path", type=str, help="Path of directory containing solutions (.wh files) .", required=True)
    parser.add_argument("-f", "--file_path", default="", type=str, help="Path of directory containing solutions (.wh files) .")
    parser.add_argument("-e", "--extension", default="pdf", type=str, help="Extension of the output file/files.")

    args = parser.parse_args(None)

    return args

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
    fitness_time = None
    fitness_distance = None
    routes = None
    for line in lines:
        if is_fitness_time and (not is_fitness_distance) and (not is_point) and (not is_route):
            fitness_time = double(line)
            is_fitness_time = False
            is_fitness_distance = True
            is_point = False
            continue
            
        if is_fitness_distance and (not is_fitness_time) and (not is_point) and (not is_route):
            fitness_distance = double(line)
            is_fitness_distance = False
            is_point = False
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

def create_json(warehouses):
    '''Returns json of warehouses.

    :param warehouses: List of Warehouse objects
    :type warehouses: List[Warehouse]
    '''
    return {
        'chromosome': list(map(lambda x: x.json(), warehouses))
    }

def get_node(point) -> int:
    '''Retrieve closes node on map to the given point.

    :param point: Point to find the closest map node to
    :type point: Point
    '''
    node = ox.get_nearest_node(graph, point=(point.lat, point.lon))
    return node

def get_route(point1, point2, weight: str) -> List[int]:
    node1 = get_node(point1)
    node2 = get_node(point2)
    route = ox.shortest_path(graph, node1, node2,
                weight=weight)
    return route

plot_colors = ['b', 'g', 'r', 'c', 'y']
wh_color = 'm'

def save_routes(warehouses: List[Warehouse], filename: str, out_ext: str):
    '''Saves visualization of solution to given output file name with specified extension.

    :param warehouses: Loaded warehouses
    :type warehouses: List[Warehouse]
    :param filename: Output file path
    :type filename: str
    '''
    global counter
    counter = 0
    routes_dict = {
        'routes': None,
        'colors': None
    }
    orig_dir = os.sep.join( filename.split(os.sep)[:-1] )
    filename = filename.split(os.sep)[-1]
    #wh_points = []
    for wh in warehouses:
        #print("Routes amount: {}".format( len(wh.routes) ))
        if wh.routes is None:
            continue
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
    figure_filename = "{}_map.{}".format(filename.split('.')[0], out_ext)
    print("Creating plot from {} ...".format(filename))
    res_file_path = os.path.join(orig_dir, RESULTS_DIR_NAME, figure_filename)

    for wh in warehouses:
        if wh.routes is None:
            continue
        routes_dict['routes'].append( [get_node(wh.point)] )
        routes_dict['colors'].append( wh_color )
    
    print("Saving to {}".format(res_file_path))

    fig, ax = ox.plot_graph_routes(
        graph,
        figsize=(100, 100),
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

def main():
    global graph
    '''Main method.

        Expects at least one argument: Path to file with solution.
    '''
    args = get_args()
    #print("Args: {}".format(args))
    map_file_path = args.map_path

    print("Loading map data...")
    ox.config(use_cache=True)
    graph = ox.load_graphml(map_file_path)
    print("Adding speed data to roads...")
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    print()

    if args.file_path == "":
        lines = sys.stdin.readlines()
        input_lines = list(map(lambda x: x[:-1], lines))
        filter_f = lambda x: x.endswith('.wh') and os.path.exists(x)
        input_lines = list(filter(filter_f, input_lines))
        if len(input_lines) == 0:
            raise Exception("Invalid input. It does not contain ")
        #print("Input_lines: {}".format(input_lines))
        for wh_file_name in input_lines:
            # wh_file_name = input_lines[i]
            # if wh_file_name.endswith('.wh') and os.path.exists(wh_file_name):
                # out_file_name = args.out_file
                # out_split = out_file_name.split('.')
                # out_file_name = "{}_{}.{}".format( '.'.join(out_split[-1]), i, out_split[-1] )
            try:
                print("Loading from file {}".format(wh_file_name))
                warehouses = load_warehouses(wh_file_name)
                save_routes(warehouses, wh_file_name, args.extension)
            except nx.NetworkXNoPath:
                print("Illegal solution: No path to node found.")
            finally:
                print()
            #os.system("python {} -m {} -f {}".format(__file__, map_file_path, wh_file_name))
    else:
        try:
            filename = args.file_path
            #for filename in files:
            if not (filename.endswith('.wh') and os.path.exists(filename)):
                print("Illegal file path.")
                return
            print("Loading from file {}".format(filename))
            warehouses = load_warehouses(filename)
            save_routes(warehouses, filename, args.extension)
        except nx.NetworkXNoPath:
            print("Illegal solution: No path to node found.")
        finally:
            print()

if __name__ == "__main__":
    main()