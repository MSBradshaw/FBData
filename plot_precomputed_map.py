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
                        help='csv with an index, position (lat, long) column and data columns named with dates in format YYYY-MM-DD')

    parser.add_argument('--country',
                        '-p',
                        dest='country',
                        required=True,
                        help='name of country to be plotted, should be spelled an capitalized exactly '
                             'like it appears in geopandas naturalearth_lowres')

    parser.add_argument('--cities',
                        '-c',
                        dest='cities',
                        default=None,
                        help='tsv file with city name lat long')

    parser.add_argument('--roads',
                        '-r',
                        dest='roads',
                        default=None,
                        help='geojson file of roads to be plotted')

    parser.add_argument('--outdir',
                        '-o',
                        dest='outdir',
                        default=None,
                        help='name of dir to save figures to')

    parser.add_argument('--borders',
                        '-b',
                        dest='borders',
                        default=None,
                        help=
                        'tsv file with name, type, lat, long of border crossings (or any other point to be plotted')

    parser.add_argument('--colormap',
                        dest='colormap',
                        default='bwr',
                        help='matplotlib color map to use')

    parser.add_argument('--colorscale',
                        dest='colorscale',
                        nargs='+',
                        default=None,
                        help='two values separated by a space to use as color lim e.g. -10 10')

    return parser.parse_args()

args = get_args()

if args.cities is not None:
    cities = pd.read_csv(args.cities, sep='\t')
else:
    cities = None

if args.borders is not None:
    borders = pd.read_csv(args.borders, sep='\t', comment='#')
else:
    borders = None

if args.roads is not None:
    roads = gpd.read_file(args.roads)
else:
    roads = None

df = pd.read_csv(args.input, sep=',')
outdir = args.outdir
country = args.country
cmap = args.colormap
color_scale = args.colorscale
if color_scale is not None:
    color_scale = [float(x) for x in color_scale]

# cities = pd.read_csv('cities.txt', sep='\t')
# borders = pd.read_csv('border_crossings.tsv', sep='\t', comment='#')
# roads = gpd.read_file('europe-road.geojson')
# df = pickle.load(open('poland_animation.pickle', 'rb'))

if outdir[-1] != '/':
    outdir += '/'

if cities is not None:
    gdf = gpd.GeoDataFrame(cities, geometry=gpd.points_from_xy(cities.Lon, cities.Lat))
else:
    gdf = None
# load the data
df['lat'] = [float(x.split(',')[0]) for x in df['positions']]
df['lon'] = [float(x.split(',')[1]) for x in df['positions']]

# load the proper country data, global or US
if country != 'Boulder':
    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
else:
    countries = gpd.read_file('Counties/cb_2018_us_county_500k.shp')

countries.columns = [x.lower() for x in countries.columns]

# if the column is a date in format YYYY-MM-DD plot it
print(df.columns)
for col in [x for x in df.columns if len(re.findall('\d\d\d\d-\d\d-\d\d',x)) > 0]:
    print(col)
    my_dpi = 300
    fig, ax = plt.subplots(figsize=(800 / my_dpi, 600 / my_dpi), dpi=my_dpi)
    scatter_size = 3
    color = 'lightgrey'
    if country == 'Boulder':
        scatter_size = 10
        color = 'black'
    countries[countries["name"] == country].plot(color="lightgrey", ax=ax, linewidth=1)
    df.plot(x="lon", y="lat", kind="scatter",
                        c=col, colormap=cmap,
                        vmax=max(color_scale), vmin=min(color_scale),
                        ax=ax, s=scatter_size)
    if 'z_score' in col:
        col = col.split('_')[2] + ' ' + col.split('_')[3]
    ax.set_title('{} {}'.format(country, col), size=title_size)
    cax = fig.get_axes()[1]
    # and we can modify it, i.e.:
    cax.set_ylabel('')
    cax.tick_params(labelsize=tick_label_size)
    if cities is not None:
        for idx, dat in cities.iterrows():
            ax.scatter(dat.Lon, dat.Lat, s=1, color='black')
            ax.annotate(dat.City, (dat.Lon, dat.Lat), size=tick_label_size)

    if borders is not None:
        for idx, dat in borders.iterrows():
            ax.scatter(dat.long, dat.lat, s=scatter_size, color='black')
            # ax.annotate(dat.City, (dat.Lon, dat.Lat), size=6)
    if roads is not None:
        roads.plot(ax=ax, alpha=0.3, linewidth=1, color=color)
    if country == 'Boulder':
        pass
        x_lim = [39.957985, 40.075242]
        y_lim = [-105.300506, -105.154538]
        ax.set_ylim(x_lim)
        ax.set_xlim(y_lim)
    remove_ticks(ax)
    remove_borders(ax)
    ax.set_ylabel('')
    ax.set_xlabel('')
    # plt.clim(0, c_max)
    plt.tight_layout()
    plt.savefig('{}{}.png'.format(outdir, col.replace(' ', '_')), dpi=my_dpi)
    # plt.show()
    plt.clf()

"""
Poland Example HotSpot

python plot_precomputed_map.py -i poland_hot_spot_df.csv --country Poland --outdir PolandZScoreFigsHotStop --colorscale -10 10 --cities cities.txt --roads europe-road.geojson --borders border_crossings.tsv

Colorado example

python plot_precomputed_map.py -i covid_hotspot.csv --country Boulder --outdir CovidZScoreFigsHotStop --colorscale -10 10 --cities co_cities.txt --roads boulder_roads.geojson

"""