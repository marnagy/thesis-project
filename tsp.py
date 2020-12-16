import random
import array

import numpy
from math import sqrt

from matplotlib import pyplot as plt
from os import remove
from PIL import Image

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

ITEMS_NUMBER = 20

random.seed(128)

items = {}

for i in range(ITEMS_NUMBER):
	items[i] = (random.uniform(0, 50), random.uniform(0, 50))
#print(items)

distance_map = [ [ sqrt((items[i][0] - items[j][0])**2 + (items[i][1] - items[j][1])**2) for j in range(ITEMS_NUMBER) ] for i in range(ITEMS_NUMBER) ]
tour_size = ITEMS_NUMBER

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("indices", random.sample, range(tour_size), tour_size)

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalTSP(individual):
	distance = distance_map[individual[-1]][individual[0]]
	for gene1, gene2 in zip(individual[0:-1], individual[1:]):
		distance += distance_map[gene1][gene2]
	return distance,

toolbox.register("mate", tools.cxPartialyMatched)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evalTSP)

def main():
	#random.seed(169)

	NGEN = 1_000 # amount of generations
	MU = 100 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 150 # number of new children for each generation
	CXPB = 0.15 # probability of mating
	MUTPB = 0.8 # mutation probability

	pop = toolbox.population(n=MU)

	hof = tools.HallOfFame(1)
	stats = tools.Statistics(lambda ind: ind.fitness.values)
	stats.register("avg", numpy.mean)
	#stats.register("std", numpy.std)
	stats.register("min", numpy.min)
	#stats.register("max", numpy.max)
	
	# pop, logbook = algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats=stats, 
	# 					halloffame=hof, verbose=False)
	
	# pop, logbook = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 					stats=stats, halloffame=hof, verbose=False)
	
	pop, logbook = algorithms.eaMuCommaLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
		stats = stats, halloffame=hof, verbose=True)
	
	return pop, logbook, stats, hof

def GenerateProgressFigure(gen_vals, best_vals, avg_vals, worst_vals):
	plt.plot(gen_vals, best_vals)
	plt.plot(gen_vals, avg_vals)
	#plt.plot(gen_vals, worst_vals)
	#plt.legend(["Best", "Average", "Worst"])
	plt.legend(["Best", "Average"])
	plt.xlabel("Generation")
	plt.ylabel("Distance")
	plt.savefig("tsp-progress.png")
	plt.clf()

def GenerateBestGif(individual, distance):
	best_value = 2**30
	generated_pic_names = []
	ordered_points = [ items[x] for x in individual ]
	for point in ordered_points:
		other_points = [ x for x in ordered_points if x != point ]
		plt.scatter([ x[0] for x in other_points ], [ x[1] for x in other_points ], color="g", marker="o")
		plt.scatter([point[0]], [point[1]], color="r", marker="x")
		#plt.title( "Generation {}".format(i) )
		plt.title("Distance: {}".format(distance))
		name = "{}_{}.png".format(i, ordered_points.index(point))
		generated_pic_names.append(name)
		plt.savefig(name)
		plt.clf()
	
	frames = [ Image.open(img) for img in generated_pic_names ]

	frames[0].save( "tsp-solution.gif", format="GIF",
		append_images=frames[1:], save_all=True,
		duration=500, loop=0 )
	
	for file_name in generated_pic_names:
		remove(file_name)

def GenerateBestPng(individual, distance):
	ordered_points = [ items[x] for x in individual ]
	pairs = [ (ordered_points[i-1],ordered_points[i]) for i in range(len(ordered_points)) ]
	for pair in pairs:
		plt.plot( [ x[0] for x in pair ], [ x[1] for x in pair ], color="g", marker="o")
	plt.title("Best solution")
	plt.savefig("tsp-solution.png")
	plt.clf()

if __name__ == "__main__":
	pop, logbook, stats, hof = main()

	print("Generating progress figure...")
	gen_vals   = [ x["gen"] for x in logbook ]
	best_vals  = [ x["min"] for x in logbook ]
	avg_vals   = [ x["avg"] for x in logbook ]
	#worst_vals = [ x["max"] for x in logbook ]
	GenerateProgressFigure(gen_vals, best_vals, avg_vals, None)

	best = hof.items[0]
	best_dist = evalTSP(best)[0]
	# print("Generating gif of best solution...")
	# GenerateBestGif(best, best_dist)
	print("Generating image of best solution...")
	GenerateBestPng(best, best_dist)
	print("Best distance: {}".format( best_dist ) )