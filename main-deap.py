import array
import random
from math import sqrt
from PIL import Image
import sys

import numpy
from matplotlib import pyplot as plt

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# custom lib
import min_span_tree

#random.seed(64)

POINTS_NUM = 10
#paths = {}

points = []
for i in range(POINTS_NUM):
	points.append( (random.randint(0, 50), random.randint(0, 50)) )

# create nodes
first_nodes = [ min_span_tree.Node(p[0], p[1], str(p)) for p in points ]
# add neighbours
for n in first_nodes:
	for n2 in first_nodes:
		if n2 != n:
			n.add_neighbour(n2)

def Index_node_in_points(node, points):
	for i in range(len(points)):
		if node.X == points[i][0] and node.Y == points[i][1]:
			return i
	return -1

route = [ Index_node_in_points(node, points) for
		node in min_span_tree.TSP_aproximate(first_nodes) ]

def GetDistance(point1, point2):
	return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

distance_map = [ [ GetDistance(p1, p2) for p2 in points] for p1 in points]

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='f', fitness=creator.FitnessMin)

toolbox = base.Toolbox()

creator.create("TSPIndividual", array.array, typecode='i', fitness=creator.FitnessMin)

def shuffle_TSP(route):
	start_index = random.randint(-len(route) + 1, 0)
	return [ route[i] for i in range(start_index,len(route) + start_index) ]

def no_shuffle_TSP(route):
	return route

def evalFunc(individual):
	wh_x, wh_y = individual[0], individual[1]

	toolbox = base.Toolbox()

	# if already calculated, DON'T calculate again
	try:
		if not individual.is_mutated:
			return individual.path
	except AttributeError:
		pass

# Attribute generator
	# toolbox.register("TSPindices", random.sample, range(POINTS_NUM), POINTS_NUM)
	toolbox.register("TSPindices", shuffle_TSP, route)	

	# Structure initializers
	toolbox.register("TSPindividual", tools.initIterate, creator.TSPIndividual, toolbox.TSPindices)
	toolbox.register("TSPpopulation", tools.initRepeat, list, toolbox.TSPindividual)

	def evalTSP(TSPIndividual):
		distance = 0
		for pair in [ (TSPIndividual[i-1], TSPIndividual[i]) for i in range(1, len(TSPIndividual)) ]:
			gene1 = pair[0]
			gene2 = pair[1]
			distance += distance_map[gene1][gene2]
		distance += GetDistance((wh_x, wh_y), points[TSPIndividual[0]])
		distance += GetDistance((wh_x, wh_y), points[TSPIndividual[-1]])
		return distance,

	toolbox.register("mate", tools.cxPartialyMatched)
	toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("evaluate", evalTSP)

	NGEN = POINTS_NUM * 10 # amount of generations
	MU = 20 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 30 # number of new children for each generation
	CXPB = 0.7 # probability of mating
	MUTPB = 0.3 # mutation probability

	pop = toolbox.TSPpopulation(n=MU)

	hof = tools.HallOfFame(1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	#stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	#stats.register("max", numpy.max)
	
	# pop, logbook = algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats=stats, 
	# 					halloffame=hof, verbose=False)

	_, _ = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
						stats=stats, halloffame=hof, verbose=False)
	
	# pop, logbook = algorithms.eaMuCommaLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 	stats = stats, halloffame=hof, verbose=False)

	individual.path = [ x for x in hof[0] ]
	individual.is_mutated = False
	return evalTSP(hof[0])

# Attribute generator
attributes = [ x[0] for x in points ] + [ x[1] for x in points ]
low, up = min(attributes), max(attributes)
toolbox.register("point_attr", random.uniform, low, up)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.point_attr, 2)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def mateWarehouse(ind1, ind2):
	child1 = creator.Individual()
	child1.append(ind1[0] + (ind2[0] - ind1[0])*random.random())
	child1.append(ind1[1] + (ind2[1] - ind1[1])*random.random())
	child2 = creator.Individual()
	child2.append(ind2[0] + (ind1[0] - ind2[0])*random.random())
	child2.append(ind2[1] + (ind1[1] - ind2[1])*random.random())
	return ( child1, child2 )

def mutateWarehouse(individual):
	index = random.randint(0,1)
	individual[index] = toolbox.point_attr()
	individual.is_mutated = True
	return individual,

toolbox.register("evaluate", evalFunc)
toolbox.register("mate", mateWarehouse)
#toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
#toolbox.register("mutate", tools.mutUniformInt, low=low, up=up, indpb=0.05)
toolbox.register("mutate", mutateWarehouse)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():

	NGEN = 50 # amount of generations
	MU = 100 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 150 # number of new children for each generation
	CXPB = 0.7 # probability of mating
	MUTPB = 0.3 # mutation probability
	
	pop = toolbox.population(n=MU)
	hof = tools.HallOfFame(1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	#stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	#stats.register("max", numpy.max)
	
	# pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, 
	#                                stats=stats, halloffame=hof, verbose=True)

	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
						stats=stats, halloffame=hof, verbose=True)
	
	return pop, log, hof

def GenerateProgressFigure(gen_vals, best_vals, avg_vals):
	plt.plot(gen_vals, best_vals)
	plt.plot(gen_vals, avg_vals)
	#plt.plot(gen_vals, worst_vals)
	plt.legend(["Best", "Average"])
	plt.xlabel("Generation")
	plt.ylabel("Distance")
	#plt.show()
	plt.title("Progress")
	plt.savefig("master-progress-aprox.png")
	plt.clf()

def GenerateBestPath(wh_point, path):
	ordered_points = [wh_point] + [ points[x] for x in path]
	distance = sum([ GetDistance(p1, p2) for p1, p2 in [ (ordered_points[i-1], ordered_points[i]) for i in range(len(ordered_points))] ])

	#pairs = zip(ordered_points[-1:], ordered_points[0:])
	pairs = [ (ordered_points[i-1], ordered_points[i]) for i in range(len(ordered_points)) ]
	#print("Pairs -> {}".format(pairs))
	for pair in pairs:
		plt.plot( [ x[0] for x in pair ], [ x[1] for x in pair ], color="g")
	plt.scatter( [ x[0] for x in ordered_points if x != wh_point ], [ x[1] for x in ordered_points if x != wh_point ], color="g", marker="o")
	plt.scatter([wh_point[0]], [wh_point[1]], color="r", marker="o")
	plt.title("Distance: {}".format(distance))
	plt.savefig("master-solution-aprox.png")
	plt.clf()

if __name__ == "__main__":
	#pool  = concurrent.futures.ThreadPoolExecutor()
	_, logbook, hof = main()

	print("Generating progress figure...")
	gen_vals   = [ x["gen"] for x in logbook ]
	best_vals  = [ x["min"] for x in logbook ]
	avg_vals   = [ x["avg"] for x in logbook ]
	GenerateProgressFigure(gen_vals, best_vals, avg_vals)

	best = hof[0]
	wh_x, wh_y = best[0], best[1]
	path = best.path
	GenerateBestPath((wh_x, wh_y), path)
	print("Best position for warehouse is {}".format( (wh_x, wh_y) ))