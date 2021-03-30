#import osmnx as ox
import os
import sys
import json
import matplotlib.pyplot as plt
from argparse import ArgumentParser, Namespace

std_tag = 'std'
min_tag = 'min'
average_tag = 'avg'
max_tag = 'max'

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", default="", type=str, help="Path of directory containing solutions (.wh files) .")
    parser.add_argument("-o", "--out_file", type=str, help="Path of directory containing solutions (.wh files) .", required=True)

    args = parser.parse_args(None)

    return args

def main():
    args = get_args()

    if args.file == "":
        lines = sys.stdin.readlines()
        input_lines = list(map(lambda x: x[:-1], lines))
        print("Input_lines: {}".format(input_lines))
        for i in range(len(input_lines)):
            wh_file_name = input_lines[i]
            if wh_file_name.endswith('.wh'):
                out_file_name = args.out_file
                out_split = out_file_name.split('.')
                out_file_name = "{}_{}.{}".format( '.'.join(out_split[-1]), i, out_split[-1] )
                os.system("python {} -f {} -o {}".format(__file__, wh_file_name, out_file_name))
    else:
        logs_file_name = args.file
        out_file_name = args.out_file
        #for i in range(len(logs_filenames)):
        #for logs_file_name in logs_filenames:
        # logs_file_name = logs_filenames[i]
        # out_file_name = out_filenames[i]
        # clear figure
        plt.clf()

        jsons = {}
        lines = None

        with open(logs_file_name, 'r') as log:
            lines = log.readlines()

        for line in lines:
            temp_json = json.loads(line)
            gen_num = temp_json['gen']
            temp_dict = {}
            temp_dict[std_tag] = temp_json[std_tag]
            temp_dict[min_tag] = temp_json[min_tag]
            temp_dict[average_tag] = temp_json[average_tag]
            temp_dict[max_tag] = temp_json[max_tag]
            jsons[gen_num] = temp_dict

        gens = list(jsons.keys())
        #std_values = list(map(lambda gen_num: jsons[gen_num][std_tag], gens))
        min_values = list(map(lambda gen_num: jsons[gen_num][min_tag], gens))
        avg_values = list(map(lambda gen_num: jsons[gen_num][average_tag], gens))
        max_values = list(map(lambda gen_num: jsons[gen_num][max_tag], gens))
        
        plt.plot(gens, min_values, color='red')
        plt.plot(gens, avg_values, color='orange')
        plt.plot(gens, max_values, color='green')
        # plt.fill_between(gens, min_values, max_values,
        #     color='#00005588', alpha=0.5)
        plt.ylabel('Time needed (seconds)')
        plt.xlabel('Generations')
        plt.savefig(out_file_name)

if __name__ == "__main__":
    main()