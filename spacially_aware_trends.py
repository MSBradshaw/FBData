import pickle
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime
import numpy as np
import pandas as pd
import argparse
import re
import sys
import geopy.distance

print(sys.argv)
title_size = 8
axis_size = 6
tick_label_size = 4
week_day_alpha = 0.1
weekend_alpha = 0.3


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

    parser.add_argument('--input',
                        '-i',
                        dest='input',
                        required=True,
                        help='csv with the columns that contains dates in YYYY-MM-DD format in the column names, non-date columns ignored')

    parser.add_argument('--out',
                        '-o',
                        dest='out',
                        default=None,
                        help='what to name the output file')

    parser.add_argument('--locs',
                        dest='locs',
                        default=None,
                        help='tsv file with columns, [name, lat long], only tiles within a certain distance of these points will be plotted')

    parser.add_argument('--distance',
                        dest='distance',
                        default=None,
                        type=float,
                        help='distance threshold in Km for tiles to be plotted. A tile must be within X km of a loc to be plotted')

    parser.add_argument('--pmax',
                        dest='pmax',
                        default=None,
                        type=float,
                        help='print all tile locations with a hotspot score above this value')

    parser.add_argument('--pmin',
                        dest='pmin',
                        default=None,
                        type=float,
                        help='print all tile locations with a hotspot score below this value')

    parser.add_argument('--highlight',
                        dest='highlight',
                        default=None,
                        help='list of lat long coordinates to highlight, needs to be the exact same as the lat lon in the input file')

    parser.add_argument('--title',
                        dest='title',
                        default='',
                        help='What to use as the title of the plot')

    return parser.parse_args()


def calc_distance(_a, _b):
    """

    :param _a: lat and long coordinates
    :param _b: lat and long coordinates
    :return: distance in km of points a and b
    """
    return geopy.distance.distance(_a, _b).km


def is_in_range(_a,_locs,_distance):
    """

    :param _a: lat and long coordinates
    :param _locs: list of lat and long coordinates
    :param _distance: distance threshold in km that _a must be from any _loc
    :return:
    """
    for _b in _locs:
        _d = calc_distance(_a, _b)
        if _d <= _distance:
            return True
    return False

def string_pos_to_list(_string):
    """

    :param _string: coordinates stored in a string formatted like [42.000, -150.0000]
    :return:
    """
    _string = _string.replace(' ','').replace('[','').replace(']','')
    return [float(x) for x in _string.split(',')]

args = get_args()

df = pd.read_csv(args.input)

# rename the columns to just be dates
df.columns = [re.match('\d\d\d\d-\d\d-\d\d', x).group() if re.match('\d\d\d\d-\d\d-\d\d', x) else x for x in df.columns]
cols_to_plot = [x for x in df.columns if re.match('\d\d\d\d-\d\d-\d\d', x)]
# sort the cols to make sure they are in the correct order
cols_to_plot.sort()

locs = pd.read_csv(args.locs, sep='\t')
locs.columns = ['Name', 'Lat', 'Long']
locs_list = [[r["Lat"], r['Long']] for i, r in locs.iterrows()]

highlights = []
if args.highlight is not None:
    highlights = [line.strip() for line in open(args.highlight,'r')]
# cal distance between all tiles and these locs
df['in_range'] = [is_in_range(string_pos_to_list(x), locs_list, args.distance) for x in df['positions']]
sub = df[df['in_range']]
sub = sub[cols_to_plot]
sub.to_csv('trend_sub.cache.csv',index=False)
print(sum(df['in_range']))

fig, ax = plt.subplots()
maxes = {}
maxes_map = {}
for i, col in enumerate(cols_to_plot):
    l = list(df[col])
    lmax = max(l)
    max_index = l.index(lmax)
    # print(df.iloc[i, :])
    pos = df.iloc[i, :]['positions']
    if pos in maxes:
        maxes[pos] += 1
    else:
        maxes[pos] = 1
    maxes_map[pos] = max_index

for key in maxes.keys():
    if maxes[key] > 1:
        print(key, str(maxes[key]))

for i, row in sub.iterrows():
    color = 'grey'
    if df['positions'][i] in highlights:
        color = 'red'
    # if none are na, plot the row
    if not row.isna().any():
        ax.plot(row, color=color, alpha=.1)

remove_borders(ax)
if len(cols_to_plot) > 13:
    tick_labs = [x if i % 7 == 0 else '' for i, x in enumerate(cols_to_plot)]
    ax.set_xticks(list(range(len(cols_to_plot))))
    ax.set_xticklabels(tick_labs)

if 'poland' in args.input and 'hot' in args.input:
    ax.axvline(x=cols_to_plot.index('2022-02-24'), color='red', linestyle='--', alpha=.5)

ax.axhline(y=0.0, color='black', linestyle='--', alpha=.5)

plt.xticks(rotation=90)
plt.title(args.title)
plt.tight_layout()
plt.savefig(args.out)
plt.clf()

if args.pmax is not None:
    print('Maxes')
    for i, r in sub.iterrows():
        if r.isna().any():
            continue
        if sum([x > args.pmax for x in r]) > 0:
            print(df['positions'][i])

if args.pmin is not None:
    print('Mins')
    for i, r in sub.iterrows():
        if r.isna().any():
            continue
        if sum([x < args.pmin for x in r]) > 0:
            print(df['positions'][i])