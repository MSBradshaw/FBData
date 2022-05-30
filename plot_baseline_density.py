import pandas as pd
import matplotlib.pyplot as plt
import sys
import argparse
import seaborn as sns

def get_args():
    """
    Gather the command line parameters, returns a namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--input',
                        '-i',
                        dest='input',
                        required=True,
                        help='csv file with a column labeled baseline')

    parser.add_argument('--out',
                        '-o',
                        dest='out',
                        default=None,
                        help='what to name the output file')

    return parser.parse_args()

def remove_borders(_ax: plt.Axes) -> None:
    """
    Remove all borders from the given matplotlib axes object
    param _ax: axes object
    """
    _ax.spines['top'].set_visible(False)
    _ax.spines['right'].set_visible(False)
    _ax.spines['bottom'].set_visible(False)
    _ax.spines['left'].set_visible(False)


args = get_args()

df = pd.read_csv(args.input)


# sns.distplot(df['baseline'], hist=True, kde=True,
#              bins=100, color = 'darkblue',
#              hist_kws={'edgecolor':'black'},
#              kde_kws={'linewidth': 4})

fig, ax = plt.subplots()
plt.hist(df['baseline'], bins=5000)
plt.yscale('log')
plt.xscale('log')
plt.xlim([1, 8200])
plt.xlabel('Tile Density')
plt.ylabel('Count')
remove_borders(ax)
plt.savefig(args.out)
