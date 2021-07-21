import sys
import os
from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir_path", type=str, help="Path of directory containing solutions (.wh files) .", required=True)
    parser.add_argument("-n", default=1, type=int, help="Get [n] filenames of best solutions.")
    parser.add_argument("-t", "--type", default="time", type=str, help="Options: [time, distance]. Default is time.")

    args = parser.parse_args(None)

    if args.n <= 0:
        raise Exception("n needs to be larger than 0.")
    if args.type not in ['time', 'distance']:
        raise Exception('Illegal type "{}"'.format(args.type))

    return args

def double(line: str) -> float:
    return float(line.replace(',', '.'))

def main():
    args = get_args()

    dir_path = args.dir_path
    if not os.path.exists(dir_path):
        sys.stderr.write("Given argument doesn't exist.\n")
        return
    
    if not os.path.isdir(dir_path):
        sys.stderr.write("Given argument is not a directory.\n")
        return
    
    files = os.listdir(dir_path)
    wh_files = list(filter(lambda x: x.endswith('.wh') , files))

    if len(wh_files) == 0:
        sys.stderr.write("Given directory does not contain any .wh files.\n")
        return
    
    sol_fitness_pairs = []

    for sol in wh_files:
        fitness_time = None
        fitness_distance = None
        with open( os.path.join(dir_path, sol), 'r' ) as sol_file:
            fitness_time = double(sol_file.readline())
            fitness_distance = double(sol_file.readline())
        sol_fitness_pairs.append( (sol, fitness_time, fitness_distance) )
    
    sort_index = 1 if args.type == 'time' else 2 # for distance
    sol_fitness_pairs.sort( key=lambda x: x[sort_index] )
    for i in range( min(args.n, len(sol_fitness_pairs)) ):
        print( os.path.join(dir_path, sol_fitness_pairs[i][0]) )

if __name__ == "__main__":
    main()
