from geopy.geocoders import Nominatim
from geopy import distance
from random import random, randint, shuffle
import math
from matplotlib import pyplot as plt

population = 50
elite_num = 2
new_random = 5
mutation_prob = 0.005
distances = {}
truck_value = 5
distance_value = 1

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
            result = truck_value * len(self.truck_routes)
            distance = 0
            for truck_route in self.truck_routes:
                if len(truck_route) > 0:
                    distance += GetDistance(self.warehouse, truck_route[i])
                    for i in range(len(truck_route) - 1 ):
                        distance += GetDistance(truck_route[i], truck_route[i+1])
                    distance += GetDistance(truck_route[-1], self.warehouse)
            result += distance * distance_value
            self._value = result
            return result
        

def RandomChromosome(min_x, min_y, diff_x, diff_y, points, trucks_amount):
    resPoint = []
    for _ in range(trucks_amount):
        resPoint.append( [] )
    
    for point in points:
        resPoint[randint(0, trucks_amount - 1)].append(point)
    
    if [] in resPoint: 
        return RandomChromosome(min_x, min_y, diff_x, diff_y, points, trucks_amount)

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
    warehouse_x = parent1.warehouse[0] + random() * (parent1.warehouse[0] - parent2.warehouse[0])
    warehouse_y = parent1.warehouse[1] + random() * (parent1.warehouse[1] - parent2.warehouse[1])
    warehouseAvg = ( warehouse_x, warehouse_y )

    truck_routes = parent1.truck_routes.copy()
    indices = []
    for route in truck_routes:
        temp = [ x for x in range( len(route) ) ]
        shuffle(temp)
        indices.append( sorted( temp[:randint(0, len(route) )] ) )

    resStopPoints = []
    for i in range(len(indices)):
        temp_route = []
        for index in indices[i]:
            temp_route.append( truck_routes[i][index] )
        resStopPoints.append( temp_route )

    for route in parent2.truck_routes:
        unlisted_points = []
        for point in route:
            if not Contains(resStopPoints, point):
                unlisted_points.append( point )
        truck_index = randint(1, len(resStopPoints) ) - 1
        for point in unlisted_points:
            resStopPoints[truck_index].append( point )
    if [] in resStopPoints:
        return CrossOver(parent1, parent2)
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
    print("Getting locations...")
    geocodes    = [     nom.geocode(x)          for x in adresses ]
    print("Loaded all locations.")
    print( "Geocodes -> " + str(geocodes) )
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

    N = 500

    solutions = []
    # init first generation
    for _ in range(population):
        solutions.append( RandomChromosome(min_x, min_y, diff_x, diff_y, coordinates, 3 ) )

    solutions.sort( key=lambda chromosome: chromosome.evaluate() )
    next_solutions = []    
    genNum = 1
    best_values = [ solutions[0].evaluate() ]
    avg_values = [ sum( [x.evaluate() for x in solutions] ) / len(solutions) ]
    worst_values = [ solutions[len(solutions) - 1].evaluate() ]

    best_value = solutions[0].evaluate()
    print( "Gen {0} -> {1}".format( genNum, best_value ) )
    while genNum < N :
        
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

        best_values.append( solutions[0].evaluate() )
        avg_values.append( sum( [x.evaluate() for x in solutions] ) / len(solutions) )
        worst_values.append( solutions[len(solutions) - 1].evaluate() )

        genNum += 1

        if best_value > solutions[0].evaluate():
            best_value = solutions[0].evaluate()
            print( "Gen {0} -> {1}".format( genNum, best_value ) )


    best_chromosome = solutions[0]
    print()
    print("Best solution found:")
    print("Total needed distance (km): {}".format(best_chromosome.evaluate()) )
    print("Warehouse geopoint: {}".format(best_chromosome.warehouse) )
    i = 1
    for route in best_chromosome.truck_routes:
        print("Truck {} delivery points:".format(i))
        for point in route:
            print(point)
        i += 1
    generations = [x for x in range(N)]
    plt.plot( generations, best_values )
    plt.plot( generations, avg_values )
    plt.plot( generations, worst_values )
    plt.xlabel("Generation")
    plt.ylabel("Distance needed")
    plt.legend(["Best", "Average", "Worst"])
    plt.show()

if __name__ == "__main__":
    Main()