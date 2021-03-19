import array
import random
from math import sqrt
from PIL import Image
from sys import argv
import multiprocessing
import time
import os
from requests import post
#from concurrent.futures import ThreadPoolExecutor
from geopy import distance
import json
import requests
from pprint import pprint

import numpy as np
from matplotlib import pyplot as plt

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import functools

# custom lib
import min_span_tree

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--seed", default=64, type=int, help="Random seed")
parser.add_argument("--cores", default=multiprocessing.cpu_count()//2,
	type=int, help="Core count for multi processing")
parser.add_argument("--runs", default=5, type=int, help="Amount of runs")
parser.add_argument("--points_file", default="gps_coords.txt",
	type=str, help="Name of file containing gps coordinates of points")

args = parser.parse_args([] if "__file__" not in globals() else None)

#random.seed(args.seed)

use_osmnx_fastapi = False
use_osmnx_flask = True
use_geopy = False

# check use_ params
assert int(use_geopy) + int(use_osmnx_flask) + int(use_osmnx_fastapi) <= 1

use_multiproc = True

debug = True
WH_AMOUNT = 1

# debug
POINTS_NUM = 4
POINTS_RANGE = 30
wh_x, wh_y = 0, 0

points = []
if debug:
	for i in range(POINTS_NUM):
		points.append( (random.randint(0, POINTS_RANGE), random.randint(0, POINTS_RANGE)) )
else:
	with open(args.points_file, "r") as gps_file:
		POINTS_NUM = int(gps_file.readline())
		for i in range(POINTS_NUM):
			line = tuple( float(part) for part in gps_file.readline().split(';') )
			assert len(line) == 2
			points.append((line[0], line[1]))

@functools.lru_cache(maxsize=None)
def GetDistance(point1, point2):
	return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 )

# distance_map = [ [ GetDistance(p1, p2) for p2 in points] for p1 in points]

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
# creator.create("Individual", array.array, typecode='f', fitness=creator.FitnessMin,
# 				path=None)
creator.create("Individual", list, fitness=creator.FitnessMin,
				path=None)

toolbox = base.Toolbox()

creator.create("TSP_Individual", list, fitness=creator.FitnessMin)

def shuffle_TSP(route):
	start_index = random.randint(-len(route) + 1, 0)
	res = [ route[i] for i in range(start_index,len(route) + start_index) ]
	print(res)
	return res

def no_shuffle_TSP(route):
	return route

def random_shuffle(points):
	points2 = points[:]
	random.shuffle(points2)
	return points2

def custom_pmx(p1, p2):
	point1 = random.randrange(1, len(p1))
	point2 = random.randrange(1, len(p1))
	start = min(point1, point2)
	end = max(point1, point2)

	# swap the middle parts
	o1mid = p2[start:end]
	o2mid = p1[start:end]

	o1 = creator.TSP_Individual()
	o2 = creator.TSP_Individual()

	for index in range(len(p1)):
		val1 = p2[index]
		if start <= index < end:
			o1.append(o1mid[index - start])
		else:
			while val1 in o1mid:
				val1 = p2[p1.index(val1)]
			else:
				o1.append(p2[index])
		val2 = p1[index]
		if start <= index < end:
			o2.append(o2mid[index - start])
		else:
			while val2 in o2mid:
				val2 = p1[p2.index(val2)]
			else:
				o2.append(p1[index])
	#print("TSP children created")
	return ( o1, o2 )

def evalTSP(TSPIndividual):
	#wh_x, wh_y = TSPIndividual[0], TSPIndividual[1]
	distance = 0
	# if use_osmnx_flask:
	# 	#data = [ list(point) for point in TSPIndividual ]
	# 	resp = requests.post("http://localhost:5000/path", json={
	# 		'points': [ [x[0], x[1]] for x in TSPIndividual ]
	# 	})
	# 	json_obj = resp.json()
	# 	#print(json_obj)
	# 	distance = json_obj['distance']
	# else:
	#for point1, point2 in zip(TSPIndividual[-1:], TSPIndividual):
	for point1, point2 in zip(TSPIndividual[-1:], TSPIndividual):
		#print(gene1, gene2)
		# if gene1 == len(points):
		# 	point1 = (wh_x, wh_y)
		# else:
		# 	point1 = points[gene1]
		# if gene2 == len(points):
		# 	point2 = (wh_x, wh_y)
		# else:
		# 	point2 = points[gene2]
		# #print(point1, point2)
		distance += GetDistance(tsp_points[point1], tsp_points[point2])
	return distance,

def evalFunc(individual, NGEN = 500, save_path = False):
	global tsp_points
	wh_x, wh_y = individual[0][0], individual[0][1]
	toolbox = base.Toolbox()

	tsp_points = [(wh_x, wh_y)] + points

	# Attribute generator
	toolbox.register("TSP_Points", random.sample, range(len(points) + 1), len(points) + 1)
	#toolbox.register("TSPindices", shuffle_TSP, route)

	# Structure initializers
	toolbox.register("TSP_Individual", tools.initIterate, creator.TSP_Individual, toolbox.TSP_Points)
	toolbox.register("TSPpopulation", tools.initRepeat, list, toolbox.TSP_Individual)

	#toolbox.register("mate", tools.cxOrdered)
	toolbox.register("mate", tools.cxPartialyMatched)
	#toolbox.register("mate", custom_pmx)
	toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("evaluate", evalTSP)

	MU = 10 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 20 # number of new children for each generation
	CXPB = 0.25 # probability of mating
	MUTPB = 0.7 # mutation probability

	pop = toolbox.TSPpopulation(n=MU)

	hof = tools.HallOfFame(1)
	#stats = tools.Statistics(lambda ind: ind.fitness.values)
	#stats.register("max", numpy.max)
	#stats.register("avg", np.mean)
	#stats.register("std", numpy.std)
	#stats.register("min", np.min)

	# pop, logbook = algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, stats=stats,
	# 					halloffame=hof, verbose=False)

	# _, _ = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 					halloffame=hof, verbose=False)

	_, _ = algorithms.eaMuCommaLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
						halloffame=hof, verbose=False)

	if save_path:
		individual.path = [ tsp_points[x] for x in hof[0] ]
	value = hof[0].fitness.getValues()[0]
	#value, = evalTSP(hof[0])
	return value,

# Attribute generator
x_attributes = [ x[0] for x in points ] # + [ x[1] for x in points ]
x_low, x_up = min(x_attributes), max(x_attributes)
y_attributes = [ x[1] for x in points ]
y_low, y_up = min(y_attributes), max(y_attributes)
def create_warehouse(x_low, x_high, y_low, y_high):
	return ( random.uniform(x_low, x_high), random.uniform(y_low, y_high))

toolbox.register("point_attr", create_warehouse, x_low=x_low, x_high=x_up,
				y_low=y_low, y_high=y_up)
# attributes = [ x[0] for x in points ] + [ x[1] for x in points ]
# low, up = min(attributes), max(attributes)
#toolbox.register("point_attr", random.uniform, low, up)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.point_attr, WH_AMOUNT)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def mateWarehouse(ind1, ind2):
	# update to new type of warehouse
	child1 = creator.Individual()
	child2 = creator.Individual()
	for i in range(WH_AMOUNT):
		rand1 = random.random()
		rand2 = random.random()
		child1.append( (rand1*ind1[i][0] + (1-rand1)*ind2[i][0], rand2*ind1[i][1] + (1-rand2)*ind2[i][1]) )
		child2.append( (rand1*ind2[i][0] + (1-rand1)*ind1[i][0], rand2*ind2[i][1] + (1-rand2)*ind1[i][1]) )
	# child2.append(ind2[0] + (ind1[0] - ind2[0])*random.random())
	# child2.append(ind2[1] + (ind1[1] - ind2[1])*random.random())
	return ( child1, child2 )

def mutateWarehouse(individual):
	rand_step = np.random.normal(size=len(individual)*2)
	for i in range(len(individual)):
		rand_step = np.random.normal(size=2)
		individual[i] = ( individual[i][0] + 0.001 * rand_step[0], individual[i][1] + 0.001 * rand_step[1] )
	return individual,

toolbox.register("evaluate", evalFunc)
toolbox.register("mate", mateWarehouse)
toolbox.register("mutate", mutateWarehouse)
toolbox.register("select", tools.selRoulette)
#toolbox.register("select", tools.selTournament, tournsize=3)

def main_ga(pool):

	NGEN = 30 # amount of generations
	MU = 10 # amount of individuals to select from each generation (possible parents)
	LAMBDA = 20 # number of new children for each generation
	CXPB = 0.8 # probability of mating
	MUTPB = 0.1 # mutation probability

	if pool is not None:
		toolbox.register("map", pool.map)

	pop = toolbox.population(n=MU)
	hof = tools.HallOfFame(1)
	stats = tools.Statistics( lambda ind: ind.fitness.values )
	stats.register("std", np.std )
	stats.register("max", np.max )
	stats.register("avg", np.mean)
	stats.register("min", np.min )

	pop, log = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN,
								   stats=stats, halloffame=hof, verbose=True)

	# pop, log = algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 								stats=stats, halloffame=hof, verbose=True)

	# pop, log = algorithms.eaMuCommaLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN,
	# 								stats=stats, halloffame=hof, verbose=True)

	return pop, log, hof

def GenerateProgressFigure(gen_vals, best_vals, avg_vals, run_num):
	plt.plot(gen_vals, best_vals)
	plt.plot(gen_vals, avg_vals)
	#plt.plot(gen_vals, worst_vals)
	plt.legend(["Best", "Average"])
	plt.xlabel("Generation")
	plt.ylabel("Distance")
	#plt.show()
	plt.title("Progress")
	if use_osmnx_flask or use_osmnx_fastapi:
		plt.savefig("osmnx-progress-{}.png".format(run_num))
	elif use_geopy:
		plt.savefig("geo-progress-{}.png".format(run_num))
	else:
		plt.savefig("progress-{}.png".format(run_num))
	plt.clf()

def GenerateBestPath(wh_point, path, run_num):
	ordered_points = [ points[x] if x < len(points) else wh_point for x in path]
	distance = sum([ GetDistance(p1, p2) for p1, p2 in [ (ordered_points[i-1], ordered_points[i]) for i in range(len(ordered_points))] ])

	#pairs = zip(ordered_points[-1:], ordered_points[0:])
	pairs = [ (ordered_points[i-1], ordered_points[i]) for i in range(len(ordered_points)) ]
	#print("Pairs -> {}".format(pairs))
	for pair in pairs:
		plt.plot( [ x[0] for x in pair ], [ x[1] for x in pair ], color="g")
	plt.scatter( [ x[0] for x in ordered_points if x != wh_point ], [ x[1] for x in ordered_points if x != wh_point ], color="g", marker="o")
	plt.scatter([wh_point[0]], [wh_point[1]], color="r", marker="o")
	plt.title("Distance: {}".format(distance))
	if use_osmnx_flask or use_osmnx_fastapi:
		plt.savefig("osmnx-solution-{}.png".format(run_num))
	elif use_geopy:
		plt.savefig("geo-solution-{}.png".format(run_num))
	else:
		plt.savefig("solution-{}.png".format(run_num))
	plt.clf()

if __name__ == "__main__":
	args = parser.parse_args([] if "__file__" not in globals() else None)

	pool = None
	if use_multiproc:
		print("Running on {} CPU cores.".format(args.cores))
		pool = multiprocessing.Pool(processes=args.cores)
	
	best_value = None
	best_run = None
	for i in range(args.runs):
		print("{}. run in progress...".format(i+1))
		if use_multiproc:
			_, logbook, hof = main_ga(pool)
		else:
			_, logbook, hof = main_ga(None)

		print("Generating progress figure...")
		gen_vals   = [ x["gen"] for x in logbook ]
		best_vals  = [ x["min"] for x in logbook ]
		avg_vals   = [ x["avg"] for x in logbook ]
		GenerateProgressFigure(gen_vals, best_vals, avg_vals, i+1)

		best = hof[0]
		print(best)
		#wh_x, wh_y = best[0][0], best[0][1]
		wh_x, wh_y = None, None
		print("Generating path for the best warehouse placement...")
		evalFunc(best, NGEN=1_000, save_path=True)
		print("Done")
		path = best.path
		GenerateBestPath(best[0], path, i+1)
		print("Best position for warehouse: {}".format( best[0] ))
		value = best.fitness.getValues()[0]
		print("Best value: {}".format(value))
		print()
		if best_value is None or best_value > value:
			best_value = value
			best_run = i+1

	print("Best value: {} from {}. run".format(best_value, best_run))
	if use_multiproc:
		pool.close()
