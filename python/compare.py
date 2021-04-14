import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import sys

import math
from argparse import ArgumentParser, Namespace

out_format = 'png'

def get_args():
    args = sys.argv[1:]
    if len(args) == 2:
        if sum( os.path.exists(dir) and os.path.isdir(dir) for dir in args):
            return [args[0], args[1]]
        else: raise Exception("At least one of directories does not exist or is not a directory.")
    else:
        raise Exception("Illegal number of arguments. Expected 2, got {}".format( len(args) ))

def double(text: str) -> float:
    #print('Converting {}...'.format(text))
    return float(text.replace(',', '.')) if type(text) == str else text

def main():
    dirs = get_args()
    # print("Dires: {}".format(dirs))
    # files = glob.glob( os.path.join(dirs[1], 'result_*.csv') )
    # print("Files: {}".format(files) )
    #df = pd.read_csv(os.path.join(dirs[0], 'result_0.csv'), sep=';')
    print("Loading files...")
    base_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(dirs[0], 'result_*.csv') ) ], ignore_index=True)
    time_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(dirs[1], 'result_*.csv') ) ], ignore_index=True)


    base_df['gen'] = base_df['gen'].apply(int)
    base_df['std'] = base_df['std'].apply(double)
    base_df['avg'] = base_df['avg'].apply(double)
    base_df['min'] = base_df['min'].apply(double)
    base_df['max'] = base_df['max'].apply(double)

    time_df['gen'] = time_df['gen'].apply(int)
    time_df['std'] = time_df['std'].apply(double)
    time_df['avg'] = time_df['avg'].apply(double)
    time_df['min'] = time_df['min'].apply(double)
    time_df['max'] = time_df['max'].apply(double)

    print("Plotting...")
    ax = sns.lineplot(x='gen', y='min', data=base_df, color='r')
    ax = sns.lineplot(x='gen', y='avg', data=base_df, ax=ax, color='g')
    ax = sns.lineplot(x='gen', y='min', data=time_df, ax=ax, color='b')
    ax = sns.lineplot(x='gen', y='avg', data=time_df, ax=ax, color='y')

    ax.legend(['BaseMin', 'BaseAvg', 'AlgMin', 'AlgAvg'])
    ax.set_xlabel('Generations')
    ax.set_ylabel('Time (seconds)')

    #out_file_name = os.path.join(args.dir_path, 'progress_plot')

    plt.show()
    #plt.savefig( '{}.{}'.format( out_file_name, out_format ) )

if __name__ == "__main__":
    main()