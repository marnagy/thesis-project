import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-b", "--base", type=str, help="Directory of Base algorithm", required=True)
    parser.add_argument("-a", "--alg", type=str, help="Directory of algorithm to compare to the Base", required=True)
    parser.add_argument("-t", "--type", default="time", type=str, help="Options: [time, distance]. Default is time.")
    parser.add_argument("-f", "--format", default='pdf', type=str, help="Available format to save [any matplotlib compatible format]. Default is pdf.")
    parser.add_argument("-m", "--mode", default='show', type=str, help="Available modes [save, show]. Default is save.")

    args = parser.parse_args(None)

    if args.type not in ['time', 'distance']:
        raise Exception('Illegal type "{}"'.format(args.type))
    if args.format not in ['pdf', 'png']:
        raise Exception('Illegal format "{}"'.format(args.format))
    if args.mode not in ['save', 'show']:
        raise Exception('Illegal mode "{}"'.format(args.format))
    return args

def double(text) -> float:
    return float(text.replace(',', '.')) if type(text) == str else text

def main():
    args = get_args()

    print("'Base' = {}".format(args.base))
    print("'Alg' = {}".format(args.alg))
    print("'Type' = {}".format(args.type))
    print("'Format' = {}".format(args.format))

    print("Loading files...")
    base_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(args.base, 'result_*_{}.csv'.format(args.type)) ) ], ignore_index=True)
    alg_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(args.alg, 'result_*_{}.csv'.format(args.type)) ) ], ignore_index=True)

    # convert to correct type (due to using decimal comma, pandas sometimes misinterprets the type)
    base_df['gen'] = base_df['gen'].apply(int)
    base_df['std'] = base_df['std'].apply(double)
    base_df['avg'] = base_df['avg'].apply(double)
    base_df['min'] = base_df['min'].apply(double)
    base_df['max'] = base_df['max'].apply(double)

    alg_df['gen'] = alg_df['gen'].apply(int)
    alg_df['std'] = alg_df['std'].apply(double)
    alg_df['avg'] = alg_df['avg'].apply(double)
    alg_df['min'] = alg_df['min'].apply(double)
    alg_df['max'] = alg_df['max'].apply(double)

    print("Plotting...")
    ax = sns.lineplot(x='gen', y='min', data=base_df, color='r', ci='sd')
    ax = sns.lineplot(x='gen', y='avg', data=base_df, ax=ax, color='g', ci='sd')
    ax = sns.lineplot(x='gen', y='min', data=alg_df, ax=ax, color='b', ci='sd')
    ax = sns.lineplot(x='gen', y='avg', data=alg_df, ax=ax, color='y', ci='sd')

    legend = ['BaseMin', 'BaseAvg', 'AlgMin', 'AlgAvg']

    title = 'Base:{} Alg:{}'.format('distance-based', 'time-based')
    ax.legend(legend)
    ax.set_xlabel('Generations')
    ax.set_ylabel('Time (seconds)' if args.type == 'time' else 'Distance (meters)')
    ax.set_title(title)

    # make plot bigger
    plt.gcf().set_size_inches(12, 8)

    if args.mode == 'show':
        plt.show()
    elif args.mode == 'save':
        out_file_name = "{}-{}".format(args.base, args.alg)
        out_file_name = 'comparison-{}_{}.{}'.format(out_file_name, args.type, args.format)

        plt.savefig( out_file_name )
        print("Plot saved to {}".format( out_file_name ))

if __name__ == "__main__":
    main()