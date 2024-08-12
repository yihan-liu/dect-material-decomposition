
import argparse

import numpy as np
from skimage.exposure import histogram
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cmap import Colormap

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('batch_name', type=str,
                        help='Name of the batch to get statistics from.')
    parser.add_argument('idx', type=int,
                        help='Show the histogram and box plot of the specified scan.')
    
    args = parser.parse_args()
    batch_name = args.batch_name
    idx = args.idx
    
    arrays = np.load(f'output\\{batch_name}.npz')
    low_post_maps = arrays['low_post_maps']
    high_post_maps = arrays['high_post_maps']
    brown_mask_maps = arrays['brown_mask_maps']
    white_mask_maps = arrays['white_mask_maps']

    sample_low_post = low_post_maps[idx]
    sample_high_post = high_post_maps[idx]
    sample_brown_mask = brown_mask_maps[idx]
    sample_white_mask = white_mask_maps[idx]

    # Histogram
    hist_low_post, bin_centers_low_post = histogram(sample_low_post, 1024)
    hist_high_post, bin_centers_high_post = histogram(sample_high_post, 1024)

    plt.figure(figsize=(8, 8))

    plt.plot(bin_centers_low_post, hist_low_post, label='80KV Post-Xenon')
    plt.plot(bin_centers_high_post, hist_high_post + 2000, label='140KV Post-Xenon')
    plt.xlim(-250, 400)
    plt.ylim(0, 4000)

    plt.xlabel('HU value')
    plt.ylabel('Count')
    plt.legend()
    plt.show()

    # Statistics
    brown_size = len(sample_low_post[sample_brown_mask])
    white_size = len(sample_low_post[sample_white_mask])

    data = np.vstack((np.pad(sample_low_post[sample_brown_mask], (0, white_size - brown_size), constant_values=np.nan),
                      sample_low_post[sample_white_mask],
                      np.pad(sample_high_post[sample_brown_mask], (0, white_size - brown_size), constant_values=np.nan),
                      sample_high_post[sample_white_mask])).T
    data = np.ma.masked_invalid(data)

    plt.figure(figsize=(8, 8))

    positions = []
    for i in range(2):
        positions.append(i * 3 + 1)
        positions.append(i * 3 + 2)

    boxprops_brown = dict(linestyle='-', linewidth=1.5, color='saddlebrown')
    boxprops_yellow = dict(linestyle='-', linewidth=1.5, color='palegoldenrod')
    medianprops = dict(linestyle='-', linewidth=2, color='black')
    flierprops_brown = dict(marker='o', markerfacecolor='saddlebrown', markersize=5, linestyle='none')
    flierprops_yellow = dict(marker='o', markerfacecolor='palegoldenrod', markersize=5, linestyle='none')

    # Creating the box plots
    for i in range(4):
        boxprops = boxprops_brown if i % 2 == 0 else boxprops_yellow
        flierprops = flierprops_brown if i % 2 == 0 else flierprops_yellow
        plt.boxplot(data[:, i].compressed(), positions=[positions[i]], patch_artist=False, notch=True, vert=1, widths=0.6, 
                    boxprops=boxprops, medianprops=medianprops, flierprops=flierprops)
    plt.xticks([1.5, 4.5, 7.5, 10.5], ['XE 80KV', 'XE 140KV'])
    plt.ylabel('Voxel HU value')

    # Adding legend
    brown_patch = plt.Line2D([], [], color='saddlebrown', marker='o', linestyle='None', markersize=5, label='Brown adipose tissue')
    yellow_patch = plt.Line2D([], [], color='palegoldenrod', marker='o', linestyle='None', markersize=5, label='White adipose tissue')
    plt.legend(handles=[brown_patch, yellow_patch], loc='upper right')

    plt.show()