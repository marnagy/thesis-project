from geopy.geocoders import Nominatim
from geopy import distance
from random import random, randint, shuffle
import math

population = 50
elite_num = 5
new_random = 5
mutation_prob = 0.001
distances = {}

class Chromosome:
    warehouse = None
    truck_routes = []
    _value = None

    def __init__(self, warehousePoint, stopPointsList):
        self.warehouse = warehousePoint
        self.truck_routes = stopPointsList
    
    def trucks_needed(self):
        return len(self.truck_routes)

    def evaluate(self):
        if self._value is not None:
            return self._value
        else:
            result = 0
            for truck_route in self.truck_routes:
                if len(truck_route) > 0:
                    for i in range( len(truck_route) ):
                        if i == 0:
                            result += GetDistance(self.warehouse, truck_route[i])
                        result += GetDistance(truck_route[i-1], truck_route[i])
                    result += GetDistance(truck_route[-1], self.warehouse)
            _value = result
            return result
        

def RandomChromosome(min_x, min_y, diff_x, diff_y, points, trucks_amount):
    resPoint = []
    for _ in range(trucks_amount):
        resPoint.append( [] )
    
    for point in points:
        resPoint[randint(0, trucks_amount - 1)].append(point)

    return Chromosome(
        ( min_x + diff_x*random(),
         min_y + diff_y*random()),
         resPoint
    )

def Generate_Chromosome(solutions):
    parent1 = ChooseParent(solutions)
    parent2 = ChooseParent(solutions)
    child1 = CrossOver(parent1, parent2)
    if random() <= mutation_prob:
        return Mutate(child1)
    return child1

def GetDistance(point1, point2):
    if str((point1, point2)) in distances:
        return distances[str((point1, point2))]
    elif str((point2, point1)) in distances:
        return distances[str((point2, point1))]
    else:
        dist = distance.distance(point1, point2).km
        distances[str((point1, point2))] = dist
        return dist

def ChooseParent(solutions):
    best_value = solutions[0].evaluate()
    random_index = randint(0, len(solutions) - 1 )
    while not best_value * random() <= solutions[random_index].evaluate():
        random_index = randint(0, len(solutions) - 1 )
    return solutions[random_index]

def CrossOver(parent1, parent2):
    warehouseAvg = ( (parent1.warehouse[0] + parent2.warehouse[0])/2, (parent1.warehouse[1] + parent2.warehouse[1])/2 )
    truck_routes = parent1.truck_routes.copy()
    # shuffle(truck_routes)

    # TO-DO: choose half random indices, sort and add in order
    resStopPoints = [ route[:math.floor(len(route)/2)] for route in truck_routes ]
    for route in parent2.truck_routes:
        unlisted_points = []
        for point in route:
            if not Contains(resStopPoints, point):
                unlisted_points.append( point )
        truck_index = randint(1, len(resStopPoints) ) - 1
        for point in unlisted_points:
            resStopPoints[truck_index].append( point )
    return Chromosome(warehouseAvg, resStopPoints)

def Contains(truck_routes, point):
    for route in truck_routes:
        if point in route:
            return True
    return False

def Mutate(solution):
    trucks_amount = len(solution.truck_routes)
    truck1 = randint(1, trucks_amount) - 1
    truck1_point = randint(1, len(solution.truck_routes[truck1])) - 1

    while True:
        truck2 = randint(1, trucks_amount) - 1
        truck2_point = randint(1, len(solution.truck_routes[truck2])) - 1

        if truck1 != truck2 or truck1_point != truck2_point:
            break
    solution.truck_routes[truck1][truck1_point], solution.truck_routes[truck2][truck2_point] = solution.truck_routes[truck2][truck2_point], solution.truck_routes[truck1][truck1_point]
    return solution
    

# first program: Best place to put warehouse if we have only one truck (modified TSP)
def Main():
    global population, new_random, elite_num
    adresses = []
    coordinates = []
    try:
        while True:
            line = input()
            if line == "":
                continue
            adresses.append(line)
    except EOFError:
        pass
    nom         = Nominatim(user_agent="test_app")
    #print("Getting locations...")
    geocodes    = [     nom.geocode(x)          for x in adresses ]
    #print("Loaded all locations.")
    coordinates = [ (x.latitude, x.longitude)   for x in geocodes ]

    with open("coordinates.txt","w") as f:
        for coords in coordinates:
            print(str(coords[0]) + "," + str(coords[1]),file=f)
    
    #print("Coordinates stored.")

    x_coords    = [ x[0] for x in coordinates ]
    max_x       = max( x_coords )
    min_x       = min( x_coords )
    diff_x      = max_x - min_x
    y_coords    = [ x[1] for x in coordinates ]
    max_y       = max( y_coords )
    min_y       = min( y_coords )
    diff_y      = max_y - min_y

    N = 1_500

    solutions = []
    # init first generation
    for _ in range(population):
        solutions.append( RandomChromosome(min_x, min_y, diff_x, diff_y, coordinates, 1 ) )

    solutions.sort( key=lambda chromosome: chromosome.evaluate() )
    next_solutions = []
    genNum = 1
    while genNum <= N :
        print( "Gen {0} -> {1}".format( genNum, solutions[0].evaluate() ) )
        # add elite
        next_solutions = solutions[:elite_num]
        # add new random
        for _ in range(new_random):
            next_solutions.append( RandomChromosome(min_x, min_y,
                diff_x, diff_y, coordinates, 1) )
        # generate from parents
        for _ in range(population - elite_num - new_random):
            next_solutions.append( Generate_Chromosome(solutions) )

        # sort solutions
        next_solutions.sort( key=lambda chromosome: chromosome.evaluate() )

        solutions = next_solutions
        next_solutions = []
        genNum += 1

    best_chromosome = solutions[0]
    print()
    print("Best solution found:")
    print("Total value: {}".format(best_chromosome.evaluate()) )
    print("Warehouse point: {}".format(best_chromosome.warehouse) )
    i = 1
    for route in best_chromosome.truck_routes:
        print("Truck {}:".format(i))
        for point in route:
            print(point)
        i += 1

if __name__ == "__main__":
    Main()