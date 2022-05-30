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


def to_unix_time(_date: str, _pattern: str = '%Y-%m-%d'):
    """

    :param _date: date in format %Y-%m-%d e.g. 2022-02-14
    :return: float, unixtime stamp in seconds of given date
    """
    _datetime_object = datetime.strptime(_date, _pattern)
    return datetime.timestamp(_datetime_object)


def get_day_of_week(_date: str):
    """

    :param _date: date in format %Y-%m-%d e.g. 2022-02-14
    :return: string day of the week
    """
    _datetime_object = datetime.strptime(_date, '%Y-%m-%d')
    return _datetime_object.strftime('%A')


def clear_ax(ax, top=False, bottom=False, left=False, right=False):
    ax.spines['top'].set_visible(top)
    ax.spines['bottom'].set_visible(bottom)
    ax.spines['left'].set_visible(left)
    ax.spines['right'].set_visible(right)
    # ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(True)
    ax.yaxis.set_tick_params(width=0.0, labelsize=4)
    ax.xaxis.set_tick_params(width=0.0, labelsize=4)


def unix_to_day_of_week(_current_time):
    return datetime.fromtimestamp(_current_time).strftime('%A')


def unix_to_date(_current_time):
    return datetime.fromtimestamp(_current_time).strftime('%Y-%m-%d')


def get_day_of_week(_date: str):
    """

    :param _date: date in format %Y-%m-%d e.g. 2022-02-14
    :return: string day of the week
    """
    _datetime_object = datetime.strptime(_date, '%Y-%m-%d')
    return _datetime_object.strftime('%A')


def remove_borders(_ax: plt.Axes) -> None:
    """
    Remove all borders from the given matplotlib axes object
    param _ax: axes object
    """
    _ax.spines['top'].set_visible(False)
    _ax.spines['right'].set_visible(False)
    _ax.spines['bottom'].set_visible(False)
    _ax.spines['left'].set_visible(False)


def remove_ticks(_ax: plt.Axes, remove_x: bool = True, remove_y: bool = True) -> None:
    """
    Remove tick marks from a matplotlib axes object
    param _ax: axes object
    param remove_x=True: If true remove the x ticks
    param remove_y=True: If true remove the y ticks
    """
    if remove_x:
        _ax.get_xaxis().set_ticks([])
    if remove_y:
        _ax.get_yaxis().set_ticks([])


def get_args():
    """
    Gather the command line parameters, returns a namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--cases',
                        dest='cases',
                        required=True,
                        help='tsv of new cases per day, col names are dates')

    parser.add_argument('--hotspot',
                        dest='hotspot',
                        required=True,
                        help='csv of hotspot scores')

    parser.add_argument('--slip',
                        dest='slip',
                        required=True,
                        help='csv of slip scores')

    parser.add_argument('--weekend',
                        dest='weekend',
                        required=True,
                        help='csv of weekend scores')

    parser.add_argument('--start',
                        '-s',
                        dest='start',
                        required=True,
                        help='when to start the baseline data formatted like %Y-%m-%d e.g. 2022-02-14')

    parser.add_argument('--end',
                        '-e',
                        dest='end',
                        required=True,
                        help='when to end the baseline data formatted like %Y-%m-%d e.g. 2022-02-20')

    parser.add_argument('--output',
                        '-o',
                        dest='output',
                        help='file to save figure in')

    return parser.parse_args()


def get_dates_in_range(_df: pd.DataFrame, _start: int, _end: int, _pattern='%Y-%m-%d'):
    """

    :param _df:
    :param _start:
    :param _end:
    :param _pattern:
    :return:
    """
    _cols_keep = [col for col in _df.columns if
                  to_unix_time(col, _pattern=_pattern) >= _start and to_unix_time(col, _pattern=_pattern) <= _end]
    return _df[_cols_keep]


def add_0_to_date(_date, _sep):
    return _sep.join(['0' + x if len(x) == 1 else x for x in _date.split(_sep)])


args = get_args()
cases = pd.read_csv(args.cases, sep='\t')
hotspot = pd.read_csv(args.hotspot)
slip = pd.read_csv(args.slip)
weekend = pd.read_csv(args.weekend)

hotspot.columns = [x.replace('_hot_spot', '') for x in hotspot.columns]
slip.columns = [x.split('vs')[0] for x in slip.columns]
cases.columns = [add_0_to_date(x, '/') for x in cases.columns]

hotspot = hotspot[[x for x in hotspot.columns if x not in ['positions', 'ids', 'polygons', 'baseline']]]
slip = slip[[x for x in slip.columns if x not in ['positions', 'ids', 'polygons', 'baseline']]]
weekend = weekend[[x for x in weekend.columns if x not in ['positions', 'ids', 'polygons', 'baseline']]]

start_date = args.start
end_date = args.end

unix_start = to_unix_time(start_date)
unix_end = to_unix_time(end_date)

# calc covid cases per day, not total
case_counts = list(cases.iloc[0,:])
case_counts = [0] + [ case_counts[i] - case_counts[i-1] for i in range(1,len(case_counts))]
cases.iloc[0, :] = case_counts

# get all the information for the dfs that is in the date range
cases = get_dates_in_range(cases, unix_start, unix_end, _pattern='%m/%d/%y')
hotspot = get_dates_in_range(hotspot, unix_start, unix_end, '%Y-%m-%d')
slip = get_dates_in_range(slip, unix_start, unix_end, '%Y-%m-%d')
weekend = get_dates_in_range(weekend, unix_start, unix_end, '%Y-%m-%d')

my_dpi = 300
fig, axes = plt.subplots(4, 1, figsize=(8, 6))

xs = [ to_unix_time(x, '%m/%d/%y') for x in cases.columns]
axes[0].plot(xs, cases.iloc[0, :], color='grey')
axes[0].set_xticks([])

dfs = [hotspot, slip, weekend]

for i, df in enumerate(dfs):
    xs = [to_unix_time(x, '%Y-%m-%d') for x in df.columns]
    for j, row in df.iterrows():
        axes[i+1].plot(xs, row, color='grey', alpha=.5)
    axes[i + 1].set_xticks([])
    axes[i + 1].axhline(y=0.0, color='r', linestyle='-', alpha=.5)

[clear_ax(x) for x in axes]
clear_ax(axes[-1], bottom=True)

[ax.tick_params(axis='both', which='major', labelsize=6) for ax in axes]
[ax.tick_params(axis='both', which='minor', labelsize=6) for ax in axes]


axes[-1].set_xticks([to_unix_time(x, '%Y-%m-%d') for x in hotspot.columns])
axes[-1].set_xticklabels([x if i % 7 == 0 and '2020-08-08' not in hotspot.columns[i] else ' ' for i,x in enumerate(hotspot.columns)], rotation = 45, size=6)

axes[0].set_ylabel('New COVID-19 cases', size=8)
axes[1].set_ylabel('Hotspot', size=8)
axes[2].set_ylabel('Slip', size=8)
axes[3].set_ylabel('Weekend', size=8)

plt.tight_layout()
plt.savefig(args.output, dpi=300)







"""
Plot the average absolute deviance from 0
"""


def calc_average_deviance_from_0(_df):
    res = {'avg_abs': [], 'dates': []}
    res_all = {'avg_abs': [], 'dates': []}
    for i, col in enumerate(_df.columns):
        res['dates'].append(col)
        col_vals = _df[col]
        col_vals = [abs(x) for x in col_vals]
        for x in col_vals:
            res_all['avg_abs'].append(x)
            res_all['dates'].append(i)
        res['avg_abs'].append(sum(col_vals) / len(col_vals))
    print(np.corrcoef(res_all['avg_abs'], res_all['dates']))
    return pd.DataFrame(res), pd.DataFrame(res_all)


mag_hotspot, mag_hotspot_all = calc_average_deviance_from_0(hotspot)
mag_slip, mag_slip_all = calc_average_deviance_from_0(slip)
mag_weekend, mag_weekend_all = calc_average_deviance_from_0(weekend)

my_dpi = 300
fig, axes = plt.subplots(4, 1, figsize=(8, 6))

case_xs = [ to_unix_time(x, '%m/%d/%y') for x in cases.columns]
axes[0].plot(case_xs, cases.iloc[0, :], color='grey', linewidth=1)
axes[0].set_xticks([])
print('cases cor',np.corrcoef(cases.iloc[0, :], case_xs))
cases.columns = case_xs

dfs = [mag_hotspot, mag_slip, mag_weekend]
dfs_all = [mag_hotspot_all, mag_slip_all, mag_weekend_all]
for i, df in enumerate(dfs):
    xs = [to_unix_time(x, '%Y-%m-%d') for x in df['dates']]
    common_xs = [x for x in xs if x in case_xs]
    df['unix_times'] = xs
    # xs_all = [to_unix_time(x, '%Y-%m-%d') for x in dfs_all[i]['dates']]
    axes[i+1].plot(xs, df['avg_abs'], color='grey', linewidth=1)
    print((np.corrcoef(df['avg_abs'],xs)))
    axes[i + 1].set_xticks([])

    cases_values = list(cases[common_xs].iloc[0, :])
    df_values = list(df[df['unix_times'].isin(common_xs)]['avg_abs'])
    print('Covid corr')
    print(np.corrcoef(cases_values, df_values))



[clear_ax(x) for x in axes]
clear_ax(axes[-1], bottom=True)

[ax.tick_params(axis='both', which='major', labelsize=6) for ax in axes]
[ax.tick_params(axis='both', which='minor', labelsize=6) for ax in axes]


axes[-1].set_xticks([to_unix_time(x, '%Y-%m-%d') for x in hotspot.columns])
axes[-1].set_xticklabels([x if i % 7 == 0 and '2020-08-08' not in hotspot.columns[i] else ' ' for i,x in enumerate(hotspot.columns)], rotation = 45, size=6)

axes[0].set_ylabel('New COVID-19 cases', size=8)
axes[1].set_ylabel('Hotspot\nAAV', size=8)
axes[2].set_ylabel('Slip\nAAV', size=8)
axes[3].set_ylabel('Weekend\nAAV', size=8)

plt.tight_layout()
plt.savefig('four_panel_magnitude.png', dpi=300)
