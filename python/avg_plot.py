from argparse import ArgumentParser, Namespace
import os
import json
from typing import List, Dict
import matplotlib.pyplot as plt

def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument("-d", "--dir_path", type=str, help="Path of directory containing solutions (.wh files) .", required=True)

    args = parser.parse_args(None)

    return args

def load_log_files(log_files: List[str]) -> List[Dict[int, Dict[str, float]]]:
    jsons = []
    for lf in log_files:
        with open(lf, "r") as log_file:
            lines = log_file.readlines()
        log_file_json = {}

        for line in lines:
            json_dict = json.loads(line)
            temp_dict = {}
            temp_dict["std"] = json_dict["std"]
            temp_dict["min"] = json_dict["min"]
            temp_dict["avg"] = json_dict["avg"]
            temp_dict["max"] = json_dict["max"]
            log_file_json[json_dict["gen"]] = temp_dict

        jsons.append(log_file_json)
    return jsons

def main():
    args = get_args()

    #print("All files: {}".format(os.listdir(args.dir_path)))
    log_files = list(filter(lambda x: os.path.isfile( os.path.join(args.dir_path, x) ) and x.endswith(".log") , os.listdir(args.dir_path)))
    #print(log_files)
    log_files = list(map(lambda x: os.path.join(args.dir_path, x) , log_files))
    loaded_files = load_log_files(log_files)

    max_gen = max(loaded_files[0].keys())
    gens = list(range(max_gen + 1))
    runs = len(loaded_files)
    min_values = []
    avg_values = []
    max_values = []
    for gen in gens:
        mins = list(map(lambda x: x[gen]["min"], loaded_files))
        avg_min = sum(mins) / runs
        min_values.append(avg_min)

        avgs = list(map(lambda x: x[gen]["avg"], loaded_files))
        avg_avg = sum(avgs) / runs
        avg_values.append(avg_avg)

        maxs = list(map(lambda x: x[gen]["max"], loaded_files))
        avg_max = sum(maxs) / runs
        max_values.append(avg_max)
    
    plt.plot(gens, min_values)
    plt.plot(gens, avg_values)
    plt.plot(gens, max_values)
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.title("Average progress plot")
    plt.show()

if __name__ == "__main__":
    main()