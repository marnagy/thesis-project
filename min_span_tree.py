import random
from math import sqrt
from pprint import pprint

POINTS_AMOUNT = 5
RANGE = 20

#random.seed(64)

def is_in_points(x: int, y: int, points):
    for point in points:
        if point[0] == x and point[1] == y:
            return True
    return False

# points = []
# for i in range(POINTS_AMOUNT):
#     x = random.randint(0, RANGE)
#     y = random.randint(0, RANGE)
#     while is_in_points(x, y, points):
#         x = random.randint(0, RANGE)
#         y = random.randint(0, RANGE)
#     points.append( (x, y) )
# print("points:")
# pprint(points)

class Node(object):
    X = None
    Y = None
    Name = ""
    neighbours = None
    def __init__(self, x: int, y: int, name: str):
        self.X = x
        self.Y = y
        self.Name = name
    
    def add_neighbour(self, node):
        if self.neighbours is None:
            self.neighbours = set()
            self.neighbours.add(node)
        else:
            self.neighbours.add(node)
    
    def __eq__(self, other):
        return str(self) == str(other)
    
    def __hash__(self):
        return self.X * self.Y + hash(self.Name)
    
    def __str__(self):
        return "Name={}, X={}, Y={}".format(self.Name, self.X, self.Y)

def euklidian_distance(n1: Node, n2: Node):
    return sqrt((n1.X - n2.X)**2 + (n1.Y - n2.Y)**2)

def find_min_span_tree(distance_func, root: Node):
    tree_root = Node(root.X, root.Y, root.Name)
    seen_nodes = set()
    seen_nodes.add( tree_root )
    considering_points = set()
    values = {}
    closest_point = {}
    for neighbour in root.neighbours:
        considering_points.add(neighbour)
        values[neighbour] = distance_func(root, neighbour)
        closest_point[neighbour] = tree_root
    
    while len(considering_points) > 0:
        min_value = None
        min_node = None
        for point in considering_points:
            if min_value is None:
                min_value = values[point]
                min_node = point
            else:
                if values[point] < min_value:
                    min_value = values[point]
                    min_node = point

        min_node_new = Node(min_node.X, min_node.Y, min_node.Name)
        parent = closest_point[min_node]
        parent.add_neighbour( min_node_new )
        min_node_new.add_neighbour( parent )
        seen_nodes.add(min_node_new)
        del parent

        for neighbour in min_node.neighbours:
            if neighbour not in seen_nodes:
                if neighbour not in considering_points:
                    considering_points.add(neighbour)
                    values[neighbour] = distance_func(min_node, neighbour)
                    closest_point[neighbour] = min_node_new
                elif distance_func(min_node_new, neighbour) < values[neighbour]:
                    values[neighbour] = distance_func(min_node_new, neighbour)
                    closest_point[neighbour] = min_node_new

        considering_points.remove(min_node)
        del values[min_node]
        del closest_point[min_node]
    return list(seen_nodes)

def TSP_aproximate(nodes):
    route = []
    first_node = nodes[random.randint(0, len(nodes) - 1)]
    seen_nodes = set()
    stack = []
    # for node in nodes:
    #     if node.neighbours is not None and len(node.neighbours) == 1:
    #         first_node = node
    #         break
    stack.append(first_node)
    seen_nodes.add(first_node)

    while len(stack) > 0:
        node = stack[-1]
        stack.remove(node)
        route.append(node)

        if node.neighbours is not None:
            for neighbour in node.neighbours:
                if neighbour not in seen_nodes:
                    stack.append(neighbour)
                    seen_nodes.add(neighbour)
    return route

def main():
    # create full graph
    nodes = [ Node(point[0], point[1], str(point)) for point in points]
    for n in nodes:
        n.neighbours = [ n2 for n2 in nodes if n2 != n ]
    # choose one node
    root = nodes[0]
    # find 
    new_nodes = find_min_span_tree(euklidian_distance, root)
    tsp_aprox = TSP_aproximate(new_nodes)
    for node in tsp_aprox:
        print(node)

if __name__ == "__main__":
    main()