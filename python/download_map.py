import osmnx as ox

print("Downloading...")
graph = ox.graph_from_place("Prague, Czech Republic",
    network_type='drive'
    #simplify=False,
    #clean_periphery=True,
    )
print("Adding speed to edges...")
graph = ox.add_edge_speeds(graph)
graph = ox.add_edge_travel_times(graph)
print("Saving...")
ox.save_graph_xml(graph, filepath='prague_map.osm')
print("Graph saved.")