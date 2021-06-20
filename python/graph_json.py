from argparse import ArgumentParser, Namespace
import osmnx as ox
import json
import os

def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument('-m', '--map_file', type=str, help='Path to the graphml file containing the graph.')
    parser.add_argument('-p', '--place', type=str, help='Name of place to be downloaded by OSMnx.')

    args = parser.parse_args(None)
    return args

def main():
    args = get_args()

    if (not args.map_file) and (not args.place):
        print('Please, choose one of the methods.')
        exit(1)

    if args.map_file and args.place:
        print('Cannot load from file AND from internet (place).')
        print('Please, choose one of the methods.')
        exit(1)

    if args.map_file is not None:
        if not os.path.isfile(args.map_file):
            print(f'File {args.map_file} does not exist.')
            exit(1)
        
        #print('Loading...')
        graph = ox.load_graphml(args.map_file)
        #print('Creating json file...')
        ox_nodes = list(graph.nodes(data=True))
        ox_edges = list(graph.edges(keys=True, data=True))
        nodes = list(
            map(
                lambda x: {
                    'id': x[0],
                    'lat': x[1]['y'],
                    'lon': x[1]['x']
                },
                ox_nodes
            )
        )
        edges = list(
            map(
                lambda x: {
                    'start_node_id':x[0],
                    'dest_node_id': x[1],
                    'length': x[3]['length'],
                    'travel_time': x[3]['travel_time']
                },
                ox_edges
                )
        )
        json_dict = {
            'nodes': nodes,
            'edges': edges
        }

        print(json.dumps(json_dict, indent=4))

if __name__ == '__main__':
    main()