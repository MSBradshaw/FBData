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

    parser.add_argument('--plottingbegin',
                        '-b',
                        dest='plottingbegin',
                        required=True,
                        help='when to begin plotting data from formatted like %Y-%m-%d e.g. 2022-02-21')

    parser.add_argument('--plottingfinish',
                        '-f',
                        dest='plottingfinish',
                        required=True,
                        help='when to finish plotting data from formatted like %Y-%m-%d e.g. 2022-03-09')


    parser.add_argument('--outputdir',
                        '-o',
                        dest='outputdir',
                        help='Directory to save figures in')

    parser.add_argument('--export_data',
                        dest='export_data',
                        help='csv file to save computed data in')

    parser.add_argument('--figname',
                        '-n',
                        dest='figname',
                        required=True,
                        help='what to save the multi figure as')

    parser.add_argument('--xrange',
                        dest='xrange',
                        nargs='+',
                        default=None,
                        help='two values separated by a space to use as x lim e.g. 0 10')

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


def get_three_day_average(_df: pd.DataFrame, _date: str, _col_date_mapping: typing.Dict) -> float:
    """
    Given a date, find the running 3 day average for that date
    :param _df:
    :param _date:
    :param _col_date_mapping:
    :return:
    """
    _second_per_day = 60 * 60 * 24
    # start of the window is 3 days before the given date
    _window_start = to_unix_time(_date) - (3 * _second_per_day)
    # end of the window is the end of the given date (the next day minus 1 second)
    _window_end = to_unix_time(_date) + _second_per_day - 1
    _cols_in_window = [x for x in _df.columns if x in _col_date_mapping and
                       _window_start <= _col_date_mapping[x] <= _window_end]
    avgs = [sum(_df.iloc[i, :][_cols_in_window]) / len(_cols_in_window) for i in range(_df.shape[0])]
    stds = [np.std(list(_df.iloc[i, :][_cols_in_window])) for i in range(_df.shape[0])]
    _data = {'positions': _df['positions'], _date + '_3_day_average': avgs, _date + '_3_day_std': stds}
    return pd.DataFrame(_data)


def clear_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)

# These are variables being hard coded in for testing, but will need to be parameterized
# pickle_path = 'poland_animation.pickle'
# starting_week_start_date = '2022-02-14'
# starting_week_end_date = '2022-02-20'
# plotting_begin = '2022-02-21'
# plotting_finish = '2022-03-10'
# outdir = 'HotSpotPlots'
# figname = 'hot_spot.png'
# --------------------------------------------------------------------------------------

args = get_args()
pickle_path = args.pickle
starting_week_start_date = args.baselinestart
starting_week_end_date = args.baselineend
plotting_begin = args.plottingbegin
plotting_finish = args.plottingfinish
outdir = args.outputdir
figname = args.figname
df = pickle.load(open(pickle_path, 'rb'))
export_data = args.export_data
xrange = args.xrange
if xrange is not None:
    xrange = [float(x) for x in xrange]

# make sure the dir ends with a /
if outdir[-1] != '/':
    outdir += '/'

starting_week_start_date_unix = to_unix_time(starting_week_start_date)
starting_week_end_date_unix = to_unix_time(starting_week_end_date)

column_to_unix_map = {x: to_unix_time(x.split('_')[2]) for x in df.columns if 'z_score' in x}

starting_week_cols = [x for x in df.columns if x in column_to_unix_map and
                      starting_week_start_date_unix <= column_to_unix_map[x] <= starting_week_end_date_unix]

# starting week 3 day averages mapped by day of the week
baseline_df = None
for x in starting_week_cols:
    tmp = get_three_day_average(df, x.split('_')[2], column_to_unix_map)
    if baseline_df is None:
        baseline_df = tmp
    else:
        baseline_df = baseline_df.merge(tmp, on='positions')

# check if there are two mondays in the columns. Remove the _x and _y cols
# add day of the week annotations to baseline_df
cols = [ get_day_of_week(x.split('_')[0]) + '_' + '_'.join(x.split('_')[1:]) if 'positions' != x else x for x in baseline_df.columns]
baseline_df.columns = cols
# keep only cols without the _x and _y
final_cols = [x for x in cols if '_x' not in x and '_y' not in x]
baseline_df = baseline_df[final_cols]

# for each date after the baseline week, calc the hot spot score
crisis_date_cols = [x for x in df.columns if x in column_to_unix_map and starting_week_end_date_unix < column_to_unix_map[x]]

hot_spot_scores = {'positions':df['positions'],'ids':df['ids'],'polygons':df['polygons']}
dates_seen = []
for i,col in enumerate(crisis_date_cols):
    col_date = col.split('_')[2]
    # skip dates that have already been seen
    if col_date in dates_seen:
        continue
    dates_seen.append(col_date)
    tmp = get_three_day_average(df, col_date, column_to_unix_map)
    day_of_week = get_day_of_week(col_date)
    # get the average col
    avg_col = day_of_week + '_3_day_average'
    std_col = day_of_week + '_3_day_std'
    # X - baseline avg
    tmp_hot_spot_scores = (tmp[col_date + '_3_day_average'] - baseline_df[avg_col]) / baseline_df[std_col]
    hot_spot_scores[col_date + '_hot_spot'] = tmp_hot_spot_scores

hot_spot_df = pd.DataFrame(hot_spot_scores)
hot_spot_df['positions'] = df['positions']
hot_spot_df.to_csv(export_data, index=False)

# plot it

for i,col in enumerate(hot_spot_df.columns):
    if col in ['positions','ids','polygons']:
        continue
    my_dpi = 300
    fig, ax = plt.subplots(figsize=(800 / my_dpi, 600 / my_dpi), dpi=my_dpi)
    # fig.set_size_inches(4, 4, forward=True)
    plt.axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    col_date = col.split('_')[0]
    day_of_week = get_day_of_week(col_date)
    ax.scatter(baseline_df[day_of_week + '_3_day_average'],
               hot_spot_df[col], 2, c='blue', label='Hotspot score', alpha=.3)
    clear_ax(ax)
    ax.set_ylabel('Hotspot', fontsize=6)
    ax.set_xlabel('Baseline', fontsize=6)
    xlim = ax.get_xlim()
    if xlim[1] / (xlim[0] + 1) > 100:
        ax.set_xscale('log')
    if xrange is not None:
        ax.set_xlim(xrange)
    ax.set_ylim((-5,5))
    plt.title(col_date, fontsize=6)
    # plt.savefig(outdir + col + '.png')
    plt.tight_layout()
    plt.savefig(outdir + col.replace(' ', '') + '.png', dpi=my_dpi)
    # plt.show()
    plt.clf()
quit()
# do the plots but in a single multipanel plot
# how large of a square does it need?
plt_cols = [x for x in hot_spot_df.columns if x not in ['positions', 'ids', 'polygons']]
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

for x in range(dim1):
    for y in range(dim2):
        axes[x][y].set_visible(False)

for i, col in enumerate(plt_cols):
    x_cor = i % dim1
    y_cor = int(i / dim1)
    axes[x_cor][y_cor].set_visible(True)
    axes[x_cor][y_cor].axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    # plot it using the first week average as the baseline
    axes[x_cor][y_cor].scatter(baseline_df[day_of_week + '_3_day_average'],
                               hot_spot_df[col], 2, c='blue', label='Slip score', alpha=.3)
    clear_ax(axes[x_cor][y_cor])
    axes[x_cor][y_cor].set_ylabel('Hotspot Score', fontsize=7)
    axes[x_cor][y_cor].set_xlabel('Baseline', fontsize=7)
    axes[x_cor][y_cor].set_xscale('log')
    axes[x_cor][y_cor].set_title(col, fontsize=8)
    if xrange is not None:
        axes[x_cor][y_cor].set_xlim(xrange)
plt.savefig(figname)
# plt.show()
plt.clf()
"""
Example parameters

python hot_spot_score.py -i poland_animation.pickle -s 2022-02-14 -e 2022-02-20 -b 2022-02-21 -f 2022-03-10 -o HotSpotPlots --figname poland_hotspot.png --export_data poland_hotspot.csv
"""