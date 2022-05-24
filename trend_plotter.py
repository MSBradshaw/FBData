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

    parser.add_argument('--title',
                        dest='title',
                        default='',
                        help='What to use as the title of the plot')

    return parser.parse_args()


args = get_args()

df = pd.read_csv(args.input)

# rename the columns to just be dates
df.columns = [re.match('\d\d\d\d-\d\d-\d\d', x).group() if re.match('\d\d\d\d-\d\d-\d\d', x) else x for x in df.columns]
cols_to_plot = [x for x in df.columns if re.match('\d\d\d\d-\d\d-\d\d', x)]
# sort the cols to make sure they are in the correct order
cols_to_plot.sort()
sub = df[cols_to_plot]

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
    ax.plot(row, color='blue', alpha=.5)

remove_borders(ax)
if len(cols_to_plot) > 13:
    tick_labs = [x if i % 7 == 0 else '' for i, x in enumerate(cols_to_plot)]
    ax.set_xticks(list(range(len(cols_to_plot))))
    ax.set_xticklabels(tick_labs)
plt.xticks(rotation=90)
plt.title(args.title)
plt.tight_layout()
plt.savefig(args.out)
plt.clf()
print(cols_to_plot)
# for key in maxes.keys():
#     fig, ax = plt.subplots()
#     max_i = maxes_map[key]
#     for i, row in sub.iterrows():
#         color = 'blue'
#         if max_i == i:
#             color = 'red'
#         ax.plot(row, color=color, alpha=.5)
#     remove_borders(ax)
#     if len(cols_to_plot) > 13:
#         tick_labs = [x if i % 7 == 0 else '' for i, x in enumerate(cols_to_plot)]
#         ax.set_xticks(list(range(len(cols_to_plot))))
#         ax.set_xticklabels(tick_labs)
#     plt.xticks(rotation=90)
#     plt.title(args.title)
#     plt.tight_layout()
#     plt.savefig('SpecificTrendPlots/{}.png'.format(key))
#     plt.clf()

poses = ['40.017097830719, -105.26275634766',
         '40.004475801858, -105.26824951172',
         '40.017097830719, -105.28472900391',
         '40.017097830719, -105.23529052734']

poses = ['40.017097830719, -105.23529052734']

low_poses = ['40.038129358358, -105.27923583984',
             '40.033923571574, -105.28472900391',
             '39.979224742356, -105.24078369141',
             '40.042334885757, -105.26275634766',
             '39.979224742356, -105.24627685547',
             '40.050745162371, -105.28472900391',
             '39.987642799428, -105.23529052734']

low_poses = ['39.979224742356, -105.24078369141']

fig, ax = plt.subplots()
for i, row in sub.iterrows():
    color = 'grey'
    this_pos = df.iloc[i, :]['positions']
    if this_pos in poses:
        color = 'red'
    elif this_pos in low_poses:
        color = 'blue'
    ax.plot(row, color=color, alpha=.3)
remove_borders(ax)
if len(cols_to_plot) > 13:
    tick_labs = [x if i % 7 == 0 else '' for i, x in enumerate(cols_to_plot)]
    ax.set_xticks(list(range(len(cols_to_plot))))
    ax.set_xticklabels(tick_labs)
    for i,date in enumerate(cols_to_plot):
        
        dow = get_day_of_week(date)
        x_offset =0.3
        if dow in ['Saturday', 'Sunday']:
            ax.axvspan(i-x_offset, i+x_offset, alpha=weekend_alpha, color='grey')
        else:
            ax.axvspan(i - x_offset, i + x_offset, alpha=week_day_alpha, color='grey')
ax.axhline(y=0.0, color='black', linestyle='--', alpha=.5)
plt.xticks(rotation=90)
plt.title(args.title)
plt.tight_layout()
plt.savefig('SpecificTrendPlots/all.png')
plt.clf()

# print out positions with > 6 hotspot scores
print('Maxes')
for i, row in sub.iterrows():
    if max(row) > 6:
        print(df.iloc[i, :]['positions'])

print('Mins')
for i, row in sub.iterrows():
    if min(row) < -10:
        print(df.iloc[i, :]['positions'])
