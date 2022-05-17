import pandas as pd
import pickle
import matplotlib.pyplot as plt
from datetime import datetime
import typing
import numpy as np
from matplotlib.gridspec import GridSpec
import argparse


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

    parser.add_argument('--figname',
                        '-n',
                        dest='figname',
                        required=True,
                        help='what to save the multi figure as')

    parser.add_argument('--outputdir',
                        '-o',
                        dest='outputdir',
                        help='Directory to save figures in')

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
# outdir = 'WeekEndScorePlots'
# figname = 'week_end_scores.png'
# df = pickle.load(open(pickle_path, 'rb'))
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
print(mondays)

# get the average for each week broken up by weekdays and weekends
weekend_scores = {}
sec_per_day = 24 * 60 * 60
sec_in_5_days = sec_per_day * 5
week_avgs = {}
for i, mon in enumerate(mondays):
    if i == len(mondays) - 1:
        continue
    weekday_cols = [x for x in cols_in_range if
                    to_unix_time(x.split('_')[2]) >= mon and to_unix_time(x.split('_')[2]) <= mondays[
                        i] + sec_in_5_days]
    weekend_cols = [x for x in cols_in_range if
                    mondays[i] + sec_in_5_days >= mon and to_unix_time(x.split('_')[2]) <= mondays[i + 1]]
    weekday_avgs = df[weekday_cols].sum(axis=1) / len(weekday_cols)
    weekend_avgs = df[weekend_cols].sum(axis=1) / len(weekend_cols)
    weekend_scores[unix_to_date(mon)] = np.log2(weekday_avgs / weekend_avgs)
    week_cols = [x for x in cols_in_range if
                 to_unix_time(x.split('_')[2]) >= mon and to_unix_time(x.split('_')[2]) <= mondays[i + 1]]
    week_avgs[unix_to_date(mon)] = df[week_cols].sum(axis=1) / len(week_cols)

ws_df = pd.DataFrame(weekend_scores)
ws_df['positions'] = df['positions']
ws_df.to_csv(export_data, index=False)

for i, col in enumerate(ws_df.columns):
    if col in ['positions', 'ids', 'polygons']:
        continue
    fig, ax = plt.subplots()
    fig.set_size_inches(4, 4, forward=True)
    plt.axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    # plot it using the first week average as the baseline
    ax.scatter(week_avgs[unix_to_date(mondays[0])],
               ws_df[col], 2, c='blue', label='Slip score', alpha=.3)
    clear_ax(ax)
    ax.set_ylabel('Weekend score', fontsize=6)
    ax.set_xlabel('Baseline', fontsize=6)
    # ax.set_ylim((-5,5))
    ax.set_xscale('log')

    plt.title(col, fontsize=6)
    plt.savefig(outdir + col.replace(' ', '') + '.png')
    # plt.show()
    plt.clf()

# do the plots but in a single multipanel plot
# how large of a square does it need?
plt_cols = [x for x in ws_df.columns if x not in ['positions', 'ids', 'polygons']]
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
    print([x_cor, y_cor])
    axes[x_cor][y_cor].axhline(y=0.0, color='r', linestyle='-', alpha=.5)
    # plot it using the first week average as the baseline
    axes[x_cor][y_cor].scatter(week_avgs[unix_to_date(mondays[0])],
                               ws_df[col], 2, c='blue', label='Slip score', alpha=.3)
    clear_ax(axes[x_cor][y_cor])
    axes[x_cor][y_cor].set_ylabel('Weekend score', fontsize=6)
    axes[x_cor][y_cor].set_xlabel('Baseline', fontsize=6)
    axes[x_cor][y_cor].set_xscale('log')

    axes[x_cor][y_cor].set_title(col, fontsize=6)
plt.savefig(figname)
# plt.show()
plt.clf()
"""

Poland Example
python weekend_score.py -i poland_animation.pickle -s 2022-01-01 -e 2022-03-28 -o WeekEndScorePlots --figname poland_week_end_score.png --export_data poland_weekend.csv
"""
