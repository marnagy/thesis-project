import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

import math
from argparse import ArgumentParser, Namespace

out_format = 'png'

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir_path", type=str, help="Path of directory containing solutions (.wh files) .", required=True)
    parser.add_argument("-m", "--mode", type=str, help="[time, distance]", required=True)

    args = parser.parse_args(None)

    if args.mode not in ['time', 'distance']:
        raise Exception('Invalid mode {}'.format(args.mode))
    return args

def double(text: str) -> float:
    #print('Converting {}...'.format(text))
    return float(text.replace(',', '.')) if type(text) == str else text

def convert(x):
    print("doing: {}".format(x))
    return double(x) if ',' in x else int(x)

def main():
    args = get_args()
    mode = args.mode
    df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(
            args.dir_path, 'result_*_{}.csv'.format(mode)
        ) ) ], ignore_index=True)


    df['gen'] = df['gen'].apply(int)
    df['std'] = df['std'].apply(double)
    df['avg'] = df['avg'].apply(double)
    df['min'] = df['min'].apply(double)
    df['max'] = df['max'].apply(double)

    ax = sns.lineplot(x='gen', y='min', data=df, color='r')
    ax = sns.lineplot(x='gen', y='avg', data=df, ax=ax, color='g')
    ax = sns.lineplot(x='gen', y='max', data=df, ax=ax, color='b')

    ax.legend(['Min', 'Avg', 'Max'])
    ax.set_xlabel('Generations')
    ax.set_ylabel('Time (seconds)' if mode == 'time' else 'Distance (meters)')

    out_file_name = os.path.join(args.dir_path, 'progress_plot')

    plt.show()
    #plt.savefig( '{}.{}'.format( out_file_name, out_format ) )

if __name__ == "__main__":
    main()