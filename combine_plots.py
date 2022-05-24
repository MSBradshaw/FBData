import matplotlib.pyplot as plt
import os
import sys
import argparse
import numpy as np
import PIL
from PIL import Image
import sys
print(sys.argv)
"""

"""


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

    parser.add_argument('-a',
                        dest='input1',
                        required=True,
                        help='directory 1')

    parser.add_argument('-b',
                        dest='input2',
                        required=True,
                        help='directory 2')

    parser.add_argument('-o',
                        dest='output',
                        required=True,
                        help='output directory')

    parser.add_argument('-n',
                        dest='number',
                        required=True,
                        default=3,
                        type=int,
                        help='number of plot to put in one figure, -1 means all in one')

    return parser.parse_args()


args = get_args()
dir1 = args.input1
dir2 = args.input2
outdir = args.output

if dir1[-1] != '/':
    dir1 += '/'
if dir2[-1] != '/':
    dir2 += '/'
if outdir[-1] != '/':
    outdir += '/'

# get a list of file names that are found in both dirs
files = {}
for file in os.listdir(dir1):
    files[file] = 1
for file in os.listdir(dir2):
    if file in files:
        files[file] += 1
    else:
        files[file] = 1
print(files)
num_in_both = 0
files_in_both = []
for file in files.keys():
    if files[file] > 1:
        files_in_both.append(file)
        num_in_both += 1
print(files_in_both)
list_im = ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']
rows = []
tmp_files = []
for file in files_in_both:
    f1 = dir1 + file
    f2 = dir2 + file
    imgs = [Image.open(i) for i in [f1, f2]]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    # imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))

    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save('del.tmp_fig.' + file)
    tmp_files.append('del.tmp_fig.' + file)
    rows.append(imgs_comb)
    fig, ax = plt.subplots()
    plt.imshow(imgs_comb)
    remove_borders_and_ticks(ax)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    cs = []
    for i in range(0, len(lst), n):
        cs.append(lst[i:i + n])
    return cs

tmp_files.sort()
print(tmp_files)
for i, chunk in enumerate(chunks(tmp_files, args.number)):
    print(chunk)
    tmp_imgs = [Image.open(i) for i in chunk]
    # imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in tmp_imgs ) )
    imgs_comb = np.vstack((np.asarray(i) for i in tmp_imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    fig, ax = plt.subplots()
    plt.imshow(imgs_comb)
    remove_borders_and_ticks(ax)
    imgs_comb.save('{}{}.png'.format(outdir, '.'.join([x.replace('del.tmp_fig.', '').replace('.png', '') for x in chunk])))
    # plt.show()
    plt.clf()
