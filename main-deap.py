import array
import random
import math
import os
from PIL import Image

import numpy
from matplotlib import pyplot as plt

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

random.seed(64)

POINTS_NUM = 15
paths = {}

points = {}
for i in range(POINTS_NUM):
	points[i] = (random.randint(0, 50), random.randint(0, 50))

#print("Points -> {}".format(points))

def GetDistance(point1, point2):
	return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

distance_map = [ [ GetDistance(points[p1], points[p2]) for p2 in points] for p1 in points]

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='f', fitness=creator.FitnessMin)

toolbox = base.Toolbox()

creator.create("TSPIndividual", array.array, typecode='i', fitness=creator.FitnessMin)

def evalFunc(individual):
	wh_x, wh_y = individual[0], individual[1]

	toolbox = base.Toolbox()

# Attribute generator
	toolbox.register("TSPindices", random.sample, range(POINTS_NUM), POINTS_NUM)

	# Structure initializers
	toolbox.register("TSPindividual", tools.initIterate, creator.TSPIndividual, toolbox.TSPindices)
	toolbox.register("TSPpopulation", tools.initRepeat, list, toolbox.TSPindividual)

	def evalTSP(TSPIndividual):
		#distance = distance_map[TSPIndividual[-1]][TSPIndividual[0]]
		#for gene1, gene2 in zip(individual[0:-1], individual[1:]):
		distance = 0
		for gene1, gene2 in zip(TSPIndividual[0:], TSPIndividual[1:]):
			distance += distance_map[gene1][gene2]
		distance += GetDistance((wh_x, wh_y), points[TSPIndividual[0]])
		distance += GetDistance((wh_x, wh_y), points[TSPIndividual[-1]])
		return distance,

	toolbox.register("mate", tools.cxPartialyMatched)
	toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("evaluate", evalTSP)

	NGEN = 100 # amount of generations
	MU = 20 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 40 # number of new children for each generation
	CXPB = 0.7 # probability of mating
	MUTPB = 0.2 # mutation probability

	pop = toolbox.TSPpopulation(n=MU)

	hof = tools.HallOfFame(1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	stats.register("max", numpy.max)
	
	# pop, logbook = algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats=stats, 
	# 					halloffame=hof, verbose=False)
	
	pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
						stats=stats, halloffame=hof, verbose=False)
	
	# pop, logbook = algorithms.eaMuCommaLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 	stats = stats, halloffame=hof, verbose=False)

	paths[str(individual)] = [ x for x in hof[0] ]
	return evalTSP(hof[0])

# Attribute generator
attributes = [ points[x][0] for x in points ] + [ points[x][1] for x in points ]
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
	return individual,

toolbox.register("evaluate", evalFunc)
toolbox.register("mate", mateWarehouse)
#toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
#toolbox.register("mutate", tools.mutUniformInt, low=low, up=up, indpb=0.05)
toolbox.register("mutate", mutateWarehouse)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():

	NGEN = 10 # amount of generations
	MU = 50 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 80 # number of new children for each generation
	CXPB = 0.7 # probability of mating
	MUTPB = 0.3 # mutation probability
	
	pop = toolbox.population(n=50)
	hof = tools.HallOfFame(1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	stats.register("max", numpy.max)
	
	# pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, 
	#                                stats=stats, halloffame=hof, verbose=True)

	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
						stats=stats, halloffame=hof, verbose=True)
	
	return pop, log, hof

def GenerateProgressFigure(gen_vals, best_vals, avg_vals, worst_vals):
	plt.plot(gen_vals, best_vals)
	plt.plot(gen_vals, avg_vals)
	plt.plot(gen_vals, worst_vals)
	plt.legend(["Best", "Average", "Worst"])
	plt.xlabel("Generation")
	plt.ylabel("Distance")
	#plt.show()
	plt.savefig("master-progress.png")
	plt.clf()

def GenerateBestPath(wh_point, path):
	ordered_points = [wh_point] + [ points[x] for x in path]
	distance = sum([ GetDistance(p1, p2) for p1, p2 in zip(ordered_points[-1:], ordered_points[0:]) ])
	# img_names = []
	# for point in ordered_points:
	# 	other_points = [ x for x in ordered_points if x != point ]
	# 	plt.scatter([ x[0] for x in other_points ], [ x[1] for x in other_points ], color="g", marker="o")
	# 	plt.scatter([wh_point[0]], [wh_point[1]], color="r", marker="o")
	# 	#plt.title( "Generation {}".format(i) )
	# 	plt.title("Distance: {}".format(distance))
	# 	name = "{}_{}.png".format(i, ordered_points.index(point))
	# 	img_names.append(name)
	# 	plt.savefig(name)
	# 	plt.clf()
	
	# frames = [ Image.open(img) for img in img_names ]

	# frames[0].save( "tsp-solution.gif", format="GIF",
	# 	append_images=frames[1:], save_all=True,
	# 	duration=500, loop=0 )
	
	# for file_name in img_names:
	# 	os.remove(file_name)

	#pairs = zip(ordered_points[-1:], ordered_points[0:])
	pairs = [ (ordered_points[i-1], ordered_points[i]) for i in range(len(ordered_points)) ]
	#print("Pairs -> {}".format(pairs))
	for pair in pairs:
		plt.plot( [ x[0] for x in pair ], [ x[1] for x in pair ], color="g")
	plt.scatter([ x[0] for x in ordered_points if x != wh_point ], [ x[1] for x in ordered_points if x != wh_point ], color="g", marker="o")
	plt.scatter([wh_point[0]], [wh_point[1]], color="r", marker="o")
	plt.title("Distance: {}".format(distance))
	plt.savefig("master-solution.png")
	plt.clf()

if __name__ == "__main__":
	_, logbook, hof = main()

	print("Generating progress figure...")
	gen_vals   = [ x["gen"] for x in logbook ]
	best_vals  = [ x["min"] for x in logbook ]
	avg_vals   = [ x["avg"] for x in logbook ]
	worst_vals = [ x["max"] for x in logbook ]
	GenerateProgressFigure(gen_vals, best_vals, avg_vals, worst_vals)

	best = hof[0]
	wh_x, wh_y = best[0], best[1]
	path = paths[str(best)]
	GenerateBestPath((wh_x, wh_y), path)
