import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from argparse import ArgumentParser, Namespace

def get_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-n", "--name", type=str, help="Name of the mutation [routemut, whmut, pointwhmut]", required=True)
    parser.add_argument("-l", "--low", type=str, help="Directory of Base algorithm", required=True)
    parser.add_argument("-b", "--base", type=str, help="Directory of algorithm to compare to the Base", required=True)
    parser.add_argument("-h", "--high", type=str, help="Directory of algorithm to compare to the Base", required=True)
    parser.add_argument("-t", "--type", default="time", type=str, help="Options: [time, distance]. Default is time.")
    parser.add_argument("-f", "--format", default='pdf', type=str, help="Available format to save [any matplotlib compatible format]. Default is pdf.")
    parser.add_argument("-m", "--mode", default='show', type=str, help="Available modes [save, show]. Default is save.")

    args = parser.parse_args(None)
    if args.name not in ['routemut', 'whmut', 'pointwhmut']:
        raise Exception('Illegal name "{}". Please use one of [routemut, whmut, pointwhmut]'.format(args.name))
    if args.type not in ['time', 'distance']:
        raise Exception('Illegal type "{}". Please use one of [time, distance]'.format(args.type))
    if args.format not in ['pdf', 'png']:
        raise Exception('Illegal format "{}". Please use one of [pdf, png]'.format(args.format))
    if args.mode not in ['save', 'show']:
        raise Exception('Illegal mode "{}". Please use one of [save, show]'.format(args.format))
    return args

def double(text) -> float:
    return float(text.replace(',', '.')) if type(text) == str else text

def main():
    args = None
    try:
        args = get_args()
    except Exception as e:
        print(e)
        return

    print("'Base' = {}".format(args.base))
    print("'Alg' = {}".format(args.alg))
    if args.alg2 is not None:
        print("'Alg2' = {}".format(args.alg2))
    print("'Type' = {}".format(args.type))
    print("'Format' = {}".format(args.format))

    mut_name = args.name

    print("Loading files...")
    base_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(args.base, 'result_*_{}.csv'.format(args.type)) ) ], ignore_index=True)
    alg_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(args.alg, 'result_*_{}.csv'.format(args.type)) ) ], ignore_index=True)
    alg2_df = None
    if args.alg2 is not None:
        alg2_df = pd.concat( [pd.read_csv(f, sep=';') for f in glob.glob( os.path.join(args.alg2, 'result_*_{}.csv'.format(args.type)) ) ], ignore_index=True)

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

    if alg2_df is not None:
        alg2_df['gen'] = alg2_df['gen'].apply(int)
        alg2_df['std'] = alg2_df['std'].apply(double)
        alg2_df['avg'] = alg2_df['avg'].apply(double)
        alg2_df['min'] = alg2_df['min'].apply(double)
        alg2_df['max'] = alg2_df['max'].apply(double)

    print("Plotting min...")
    ax = sns.lineplot(x='gen', y='min', data=base_df, color='r', ci='sd')
    ax = sns.lineplot(x='gen', y='min', data=alg_df, ax=ax, color='b', ci='sd')
    if alg2_df is not None:
        ax = sns.lineplot(x='gen', y='min', data=alg2_df, ax=ax, color='m', ci='sd')

    legend = ['BaseMin', 'AlgMin']
    #legend = ['Base Min', 'Alg Min']

    title = 'Base: {}, Alg: {}, Alg2: {}'.format(
        0.3 if mut_name == 'pointwhmut' else 0.4,
        0.5 if mut_name == 'pointwhmut' else 0.6,
        0.7 if mut_name == 'pointwhmut' else 0.8)

    if alg2_df is not None:
        legend += ['Alg2Min']
    ax.legend(legend)
    ax.set_xlabel('Generations')
    ax.set_ylabel('Time (seconds)' if args.type == 'time' else 'Distance (meters)')
    ax.set_title(title)

    # make plot bigger
    plt.gcf().set_size_inches(12, 8)

    if args.mode == 'show':
        plt.show()
    elif args.mode == 'save':
        out_file_name = f'{mut_name}prob_min_' + ('0.3_0.5_0.7' if mut_name == 'pointwhmut' else '0.4_0.6_0.8' )
        out_file_name = 'comparison-{}_{}.{}'.format(out_file_name, args.type, args.format)

        plt.savefig( out_file_name )
        print("Plot saved to {}".format( out_file_name ))
        plt.clf()
    
    print("Plotting average...")
    ax = sns.lineplot(x='gen', y='avg', data=base_df, color='g', ci='sd')
    ax = sns.lineplot(x='gen', y='avg', data=alg_df, ax=ax, color='y', ci='sd')
    if alg2_df is not None:
        ax = sns.lineplot(x='gen', y='avg', data=alg2_df, ax=ax, color='k', ci='sd')

    legend = ['BaseAvg', 'AlgAvg']
    #legend = ['Base Min', 'Alg Min']

    title = 'Base: {}, Alg: {}, Alg2: {}'.format(
        0.3 if mut_name == 'pointwhmut' else 0.4,
        0.5 if mut_name == 'pointwhmut' else 0.6,
        0.7 if mut_name == 'pointwhmut' else 0.8)

    if alg2_df is not None:
        legend += ['Alg2Avg']
    ax.legend(legend)
    ax.set_xlabel('Generations')
    ax.set_ylabel('Time (seconds)' if args.type == 'time' else 'Distance (meters)')
    ax.set_title(title)

    # make plot bigger
    plt.gcf().set_size_inches(12, 8)

    if args.mode == 'show':
        plt.show()
    elif args.mode == 'save':
        out_file_name = f'{mut_name}prob_avg_' + ('0.3_0.5_0.7' if mut_name == 'pointwhmut' else '0.4_0.6_0.8' )
        out_file_name = 'comparison-{}_{}.{}'.format(out_file_name, args.type, args.format)

        plt.savefig( out_file_name )
        print("Plot saved to {}".format( out_file_name ))

if __name__ == "__main__":
    main()