import matplotlib.pyplot as plt
import os
import sys
import argparse
import numpy as np
import PIL
from PIL import Image
import sys
print(sys.argv)


def remove_borders_and_ticks(_ax: plt.Axes) -> None:
    """
    Remove all borders from the given matplotlib axes object
    param _ax: axes object
    """
    _ax.spines['top'].set_visible(False)
    _ax.spines['right'].set_visible(False)
    _ax.spines['bottom'].set_visible(False)
    _ax.spines['left'].set_visible(False)
    _ax.set_yticklabels([])
    _ax.set_xticklabels([])
    _ax.set_yticks([])
    _ax.set_xticks([])


def get_args():
    """
    Gather the command line parameters, returns a namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        dest='input1',
                        required=True,
                        help='directory 1')

    parser.add_argument('-o',
                        dest='output',
                        required=True,
                        help='output file name')

    parser.add_argument('--d1',
                        dest='d1',
                        required=True,
                        type=int,
                        help='dimension 1')

    parser.add_argument('--d2',
                        dest='d2',
                        required=True,
                        type=int,
                        help='dimension 1')

    return parser.parse_args()


args = get_args()

rows = [[] for i in range(args.d1)]
print(len(rows))
dir = args.input1
print(dir)
if dir[-1] != '/':
    dir += '/'

files = os.listdir(dir)
files.sort()
for i,f in enumerate(files):
    ri = int(i / args.d2)
    rows[ri].append(Image.open(dir+f))

odir = args.output
if odir[-1] != '/':
    odir += '/'

img_rows = []
for i,r in enumerate(rows):
    im = np.hstack([np.asarray(i) for i in r])
    img_rows.append(im)
    fig, ax = plt.subplots()
    remove_borders_and_ticks(ax)
    imgs_comb = Image.fromarray(im)
    plt.imshow(imgs_comb)
    print('{}{}.png'.format(args.output, str(i)))
    imgs_comb.save('{}{}.png'.format(odir, str(i)))
    # plt.show()
    plt.clf()
