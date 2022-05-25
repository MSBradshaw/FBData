import pandas as pd
import pickle
import matplotlib.pyplot as plt
from datetime import datetime
import typing
import numpy as np
from matplotlib.gridspec import GridSpec
import argparse
import sys
print(sys.argv)


def get_args():
    """
    Gather the command line parameters, returns a namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--pickle',
                        '-i',
                        dest='pickle',
                        required=True,
                        help='pickled pandas dataframe')

    parser.add_argument('--baselinestart',
                        '-s',
                        dest='baselinestart',
                        required=True,
                        help='when to start the baseline data formatted like %Y-%m-%d e.g. 2022-02-14')

    parser.add_argument('--baselineend',
                        '-e',
                        dest='baselineend',
                        required=True,
                        help='when to end the baseline data formatted like %Y-%m-%d e.g. 2022-02-20')

    parser.add_argument('--outputdir',
                        '-o',
                        dest='outputdir',
                        help='Directory to save figures in')

    parser.add_argument('--figname',
                        '-n',
                        dest='figname',
                        required=True,
                        help='what to save the multi figure as')

    parser.add_argument('--export_data',
                        dest='export_data',
                        help='csv file to save computed data in')


    return parser.parse_args()


def to_unix_time(_date: str):
    """

    :param _date: date in format %Y-%m-%d e.g. 2022-02-14
    :return: float, unixtime stamp in seconds of given date
    """
    _datetime_object = datetime.strptime(_date, '%Y-%m-%d')
    return datetime.timestamp(_datetime_object)


def get_day_of_week(_date: str):
    """

    :param _date: date in format %Y-%m-%d e.g. 2022-02-14
    :return: string day of the week
    """
    _datetime_object = datetime.strptime(_date, '%Y-%m-%d')
    return _datetime_object.strftime('%A')


def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)

def unix_to_day_of_week(_current_time):
    return datetime.fromtimestamp(_current_time).strftime('%A')


def unix_to_date(_current_time):
    return datetime.fromtimestamp(_current_time).strftime('%Y-%m-%d')

# These are variables being hard coded in for testing, but will need to be parameterized
# pickle_path = 'poland_animation.pickle'
# start_date = '2022-01-24'
# end_date = '2022-03-10'
# outdir = 'HotSpotPlots'
# df = pickle.load(open(pickle_path, 'rb'))
# figname = 'week_end_scores.png'
# --------------------------------------------------------------------------------------

args = get_args()
pickle_path = args.pickle
start_date = args.baselinestart
end_date = args.baselineend
outdir = args.outputdir
figname = args.figname
df = pickle.load(open(pickle_path, 'rb'))
export_data = args.export_data

# make sure the dir ends with a /
if outdir[-1] != '/':
    outdir += '/'

start_date_unix = to_unix_time(start_date)
end_date_unix = to_unix_time(end_date)

column_to_unix_map = {x: to_unix_time(x.split('_')[2]) for x in df.columns if 'z_score' in x}

cols_in_range = [x for x in df.columns if x in column_to_unix_map and
                      start_date_unix <= column_to_unix_map[x] <= end_date_unix]

# get all weeks (mondays) in range
current_unix = start_date_unix
mondays = []
while current_unix < end_date_unix:
    current_unix += (60 * 60 * 24)
    if unix_to_day_of_week(current_unix) == 'Monday':
        mondays.append(current_unix)

# get the average for each week
week_avgs = {}
for i, mon in enumerate(mondays):
    if i == len(mondays) - 1:
        continue
    week_cols = [x for x in cols_in_range if to_unix_time(x.split('_')[2]) >= mon and to_unix_time(x.split('_')[2]) <= mondays[i+1]]

    week_avgs[unix_to_date(mon)] = df[week_cols].sum(axis=1) / len(week_cols)

# get the diff of the weeks and log_2 of that
diffs = {}
keys = list(week_avgs.keys())
for i, week in enumerate(keys):
    if i == len(keys) - 1:
        continue
    diffs[week + 'vs' + keys[i+1]] = list(np.log2(week_avgs[week] / week_avgs[keys[i+1]]))

slip_df = pd.DataFrame(diffs)
slip_df['positions'] = df['positions']
slip_df['baseline'] = week_avgs[unix_to_date(mondays[0])]
slip_df.to_csv(export_data, index=False)

for i,col in enumerate(slip_df.columns):
    if col in ['positions','ids','polygons']:
        continue
    my_dpi = 300
    fig, ax = plt.subplots(figsize=(800 / my_dpi, 600 / my_dpi), dpi=my_dpi)
    # fig.set_size_inches(4, 4, forward=True)

    plt.axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    # plot it using the first week average as the baseline
    ax.scatter(slip_df['baseline'],
               slip_df[col], 2, c='blue', label='Slip score', alpha=.3)
    clear_ax(ax)
    ax.set_ylabel('Slip score', fontsize=6)
    ax.set_xlabel('Baseline', fontsize=6)
    # ax.set_ylim((-5,5))
    xlim = ax.get_xlim()
    if (xlim[1] - xlim[0]) > 100:
        print('log')
        ax.set_xscale('log')
    else:
        print('not log', str(xlim) )

    plt.title(col, fontsize=6)
    plt.tight_layout()
    plt.savefig(outdir + col.replace(' ', '') + '.png', dpi=my_dpi)
    # plt.show()
    plt.clf()


# do the plots but in a single multipanel plot
# how large of a square does it need?
plt_cols = [x for x in slip_df.columns if x not in ['positions', 'ids', 'polygons']]
num_plots = len(plt_cols)
if num_plots % 2 == 1:
    num_plots += 1
dim1 = 1
dim2 = 1
while dim1 * dim2 < num_plots:
    if dim1 == dim2:
        dim1 += 1
    else:
        dim2 += 1

fig = plt.figure()
# fig, axes = plt.subplots(dim1, dim2, wspace=0.10, hspace=0.1)
gs1 = GridSpec(dim1, dim2, wspace=0.50, hspace=0.5)
axes = []
for i in range(dim1):
    axes.append([])
    for j in range(dim2):
        axes[i].append(fig.add_subplot(gs1[i, j]))

fig.set_size_inches(4 * dim1, 4 * dim2, forward=True)

if len(plt_cols) != num_plots:
    axes[-1][-1].set_visible(False)

for i, col in enumerate(plt_cols):
    x_cor = i % dim1
    y_cor = int(i / dim1)
    axes[x_cor][y_cor].axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    # plot it using the first week average as the baseline
    axes[x_cor][y_cor].scatter(slip_df['baseline'],
                               slip_df[col], 2, c='blue', label='Slip score', alpha=.3)
    clear_ax(axes[x_cor][y_cor])
    axes[x_cor][y_cor].set_ylabel('Weekend score', fontsize=6)
    axes[x_cor][y_cor].set_xlabel('Baseline', fontsize=6)
    axes[x_cor][y_cor].set_xscale('log')

    axes[x_cor][y_cor].set_title(col, fontsize=6)
plt.savefig(figname)
# plt.show()
plt.clf()

"""
Example parameters
-i
poland_animation.pickle
-s
2022-01-14
-e
2022-03-10
-o
SlipScorePlots
--figname
slip_score.png
--export_data
poland_slip.csv
"""