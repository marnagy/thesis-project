### Project demo

1 warehouse 1 truck demo -> https://youtu.be/c6Ys4W7HJ9w

### addresses.py

Used for getting addresses of random shops in Prague

### chromedriver.exe

Necessary driver for selenium used in addresses.py

### main-deap.py

Main GA algorithm using DEAP module

### main.py

Main custom program of GA

### tsp.py

GA using deap library and generating tsp-progress.png and tsp-solution.png images

## To Do:

- [x] Implement GA solving TSP

# Main GA
## Goal
Find the best location for a Warehouse

- individual is array of double representing coordinates of the warehouse
- uses tournament selection
- crossover is custom: choose random point for square that has in opposite corners the parents
- mutation is change one of the coordinates to random coordinate
- each generation is mixed with the next one and the next generation is N best solutions
- evaluation of an individual is another GA for 1_000 generations

# Evaluating GA
## Goal
Find Hammilton walk, find order of points for the lowest price
[in this case, price means distance]

- possible improvement of first generation: start with some TSP approximation(explanation: by starting with better candidates, we reduce time needed, thus speeding up the main GA)
- individual is array of integers where integer is the index of a point in dictionary of points
- uses tournament selection
- crossover is TwoPointCrossover
- mutation is an exchange of 2 points
- each generation is mixed with the next one and the next generation is N best solutions
- evaluation is sum of distances from warehouse through points and back to warehouse

## Update 11.10.2020
### Inside Evaluating GA:
Instead of starting with random permutation, start with 2-aprox. of TSP(Double-tree alg.)
According to my testing, it performs better in terms of speed and accuracy