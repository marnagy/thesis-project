import osmnx as ox
from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    """Get arguments from CLI.

    :return: Needed arguments
    :rtype: Namespace
    """
    parser = ArgumentParser()
    parser.add_argument("-p", "--place", type=str, help="Name of place to get map of. (Check compatibility on https://www.openstreetmap.org/)", required=True)
    parser.add_argument("-o", "--out_file", default="", type=str, help="Output file name.")

    args = parser.parse_args(None)
    return args

def download_map(place_name: str, out_filename: str):
    """Download map to current directory.

    :param place_name: Name of place to get map of
    :type place_name: str
    """
    print("Downloading...")
    graph = ox.graph_from_place(place_name, network_type='drive')

    print("Adding speed to edges...")
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)

    print("Saving...")
    ox.save_graphml(graph, filepath="{}.graphml".format(out_filename) )
    print("Graph saved.")

def main():
    args = get_args()
    download_map(
        args.place, 
        args.out_file if args.out_file != '' else '{}_map'.format(
            args.place.lower()
            )
        )


if __name__ == "__main__":
    main()