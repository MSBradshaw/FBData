import pickle
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime
import numpy as np
import pandas as pd
import argparse


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

    parser.add_argument('--pickle',
                        '-i',
                        dest='pickle',
                        required=True,
                        help='pickled pandas dataframe')

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

    parser.add_argument('--outdir2',
                        dest='outdir2',
                        default=None,
                        help='name of dir to save z-score figures to')

    parser.add_argument('--borders',
                        '-b',
                        dest='borders',
                        default=None,
                        help=
                        'tsv file with name, type, lat, long of border crossings (or any other point to be plotted')

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

df = pickle.load(open(args.pickle, 'rb'))
outdir = args.outdir
outdir2 = args.outdir2
country = args.country

# cities = pd.read_csv('cities.txt', sep='\t')
# borders = pd.read_csv('border_crossings.tsv', sep='\t', comment='#')
# roads = gpd.read_file('europe-road.geojson')
# df = pickle.load(open('poland_animation.pickle', 'rb'))

if outdir[-1] != '/':
    outdir += '/'

if outdir2[-1] != '/':
    outdir2 += '/'

if cities is not None:
    gdf = gpd.GeoDataFrame( cities, geometry=gpd.points_from_xy(cities.Lon, cities.Lat))
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

# average by day
def average_day_data(_df: pd.DataFrame):
    _dates = set([x.split('_')[2] for x in _df.columns if 'z_score' in x])
    print(_dates)
    _non_date_cols = [x for x in _df.columns if 'z_score' not in x]
    _non_date_cols_df = _df[_non_date_cols]
    _day_data = {}
    for date in _dates:
        _cols = [c for c in _df.columns if date in c]
        print(date)
        print(_cols)
        _sub = _df[_cols]
        _day_data[date] = []
        for i in range(_sub.shape[0]):
            vals = [x for x in _sub.iloc[i, :]]
            avg = sum(vals) / len(vals)
            _day_data[date].append(avg)
    _day_data_df = pd.DataFrame(_day_data)
    return pd.concat([_non_date_cols_df, _day_data_df], axis=1), _day_data_df.max().max()


def calc_change(_df: pd.DataFrame):
    # find out if the date is a weekday or weekend
    day_or_end_mapping = {}
    pre_war_weekdays = []
    pre_war_weekends = []
    for col in _df.columns[5:]:
        datetime_object = datetime.strptime(col, '%Y-%m-%d')
        # skip post-war start values
        if datetime_object.weekday() >= 5:
            # weekend
            day_or_end_mapping[col] = 'weekend'
            if datetime_object > datetime.strptime('2022-02-24', '%Y-%m-%d'):
                continue
            pre_war_weekends.append(col)
        else:
            day_or_end_mapping[col] = 'weekday'
            if datetime_object > datetime.strptime('2022-02-24', '%Y-%m-%d'):
                continue
            pre_war_weekdays.append(col)
    # calculate the averages and std for pre-war time
    tile_weekend_base = {}
    tile_weekday_base = {}
    tile_weekend_base_std = {}
    tile_weekday_base_std = {}
    for i in range(_df.shape[0]):
        # week days
        _sub = _df[pre_war_weekdays]
        day_vals = list(_sub.iloc[i, :])
        day_mean = sum(day_vals) / len(day_vals)
        tile_weekday_base[_df.iloc[i, 0]] = day_mean
        tile_weekday_base_std[_df.iloc[i, 0]] = np.array(day_vals).std()
        # week end
        _sub_end = _df[pre_war_weekends]
        end_vals = list(_sub_end.iloc[i, :])
        end_mean = sum(end_vals) / len(end_vals)
        tile_weekend_base[_df.iloc[i, 0]] = end_mean
        tile_weekend_base_std[_df.iloc[i, 0]] = np.array(end_vals).std()
    # create a z-score dataframe
    z_score_data = {}
    for j in range(5, _df.shape[1]):
        date = _df.columns[j]
        z_score_data[date] = []
        for i in range(_df.shape[0]):
            if day_or_end_mapping[date] == 'weekend':
                std = tile_weekend_base_std[_df.iloc[i, 0]]
                mean = tile_weekend_base[_df.iloc[i, 0]]
            else:
                std = tile_weekday_base_std[_df.iloc[i, 0]]
                mean = tile_weekday_base[_df.iloc[i, 0]]
            z_score_data[date].append((_df.iloc[i, j] - mean) / std)
    z_score_df = pd.DataFrame(z_score_data)
    non_date_df = _df.iloc[:, :5]
    z_score_df = z_score_df.fillna(0)
    print(z_score_df.shape)
    print(non_date_df.shape)
    return pd.concat([non_date_df, z_score_df], axis=1), z_score_df.max().max(), z_score_df.min().min()


avg_df, c_max = average_day_data(df)
z_score_avg_df, z_max, z_min = calc_change(avg_df)
avg_df.to_csv('avg_df.csv')
for col in [x for x in avg_df.columns[5:]]:
    fig, ax = plt.subplots(figsize=(8, 6))
    # print(countries.columns)
    countries.columns = [x.lower() for x in countries.columns]
    countries[countries["name"] == country].plot(color="lightgrey", ax=ax)
    avg_df.plot(x="lon", y="lat", kind="scatter",
                c=col, colormap="YlOrRd", vmax=int(c_max),
                title='{} {}'.format(country, col),
                ax=ax)
    # plt.clim(0, c_max)
    if country == 'Boulder':
        x_lim = [40.075242, 39.957985]
        y_lim = [-105.154538, -105.300506]
        # y_lim = (avg_df['lon'].max(), avg_df['lon'].min())
        # x_lim = (avg_df['lat'].max(), avg_df['lat'].min())
        ax.set_ylim(x_lim)
        ax.set_xlim(y_lim)
    plt.savefig('{}{}.png'.format(outdir, col))
    # plt.show()
    plt.clf()

for col in [x for x in z_score_avg_df.columns[5:]]:
    datetime_object = datetime.strptime(col, '%Y-%m-%d')
    # skip post-war start values
    day_type = 'Weekday'
    if datetime_object.weekday() >= 5:
        day_type = 'Saturday / Sunday'
    fig, ax = plt.subplots(figsize=(8, 6))
    countries[countries["name"] == country].plot(color="lightgrey", ax=ax, linewidth=1)
    z_score_avg_df.plot(x="lon", y="lat", kind="scatter",
                        c=col, colormap="bwr", vmax=30, vmin=-30,
                        title='{} {} {}'.format(country, col, day_type),
                        ax=ax, s=3)
    if cities is not None:
        for idx, dat in cities.iterrows():
            # print(dat.city, dat.lng, dat.lat)
            ax.scatter(dat.Lon, dat.Lat, s=1, color='black')
            ax.annotate(dat.City, (dat.Lon, dat.Lat), size=6)

    if borders is not None:
        for idx, dat in borders.iterrows():
            # print(dat.city, dat.lng, dat.lat)
            ax.scatter(dat.long, dat.lat, s=2, color='black')
            # ax.annotate(dat.City, (dat.Lon, dat.Lat), size=6)
    if roads is not None:
        roads.plot(ax=ax, alpha=0.3, linewidth=1, color='lightgrey')
    remove_ticks(ax)
    remove_borders(ax)
    ax.set_ylabel('')
    ax.set_xlabel('')
    # plt.clim(0, c_max)
    plt.savefig('{}{}.png'.format(outdir2, col))
    # plt.show()
    plt.clf()

"""
-i 
poland_animation.pickle
--country
Poland
--cities
cities.txt
--roads
europe-road.geojson
--outdir
Figs
--outdir2
ZScoreFigs
--borders
border_crossings.tsv
"""