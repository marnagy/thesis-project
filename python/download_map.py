import osmnx as ox
from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    """Get arguments from CLI.

    :return: Needed arguments
    :rtype: Namespace
    """
    parser = ArgumentParser()
    parser.add_argument("-p", "--place", default="Prague", type=str, help="Name of place to get map of.")
    parser.add_argument("-o", "--out_file", default="prague_map", type=str, help="Output file name.")

    args = parser.parse_args(None)
    return args

def download_map(place_name: str, out_filename: str):
    """Download map to current directory.

    :param place_name: Name of place to get map of
    :type place_name: str
    """
    print("Downloading...")
    graph = ox.graph_from_place(place_name,
        network_type='drive'
        #simplify=False,
        #clean_periphery=True,
        )
    print("Adding speed to edges...")
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    print("Saving...")
    #ox.save_graph_geopackage(graph, filepath='prague_map.gpkg', directed=True)
    ox.save_graphml(graph, filepath="{}.graphml".format(out_filename) )
    #ox.save_graph_xml(graph, filepath='prague_map.osm')
    print("Graph saved.")

if __name__ == "__main__":
    args = get_args()
    download_map(args.place, args.out_file)