
import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
from skimage.restoration import denoise_bilateral
from skimage.morphology import disk
from skimage.morphology import binary_dilation, binary_erosion
from skimage.morphology import remove_small_objects

from hu_utils import load_hu, write_decom
from utils import show_pair

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_scan', type=int,
                        default=250, help='Number of scan slices to load.')
    parser.add_argument('-i', '--index', type=int,
                        default=200, help='Index of scan show.')
    parser.add_argument('-t', '--trim', nargs=4, type=int,
                        default=None, help='Range of the scan of interest, used for removing unwanted part of the scan.')
    parser.add_argument('--low-dir', type=str,
                        default=None, help='Path to the 80KV scans.')
    parser.add_argument('--high-dir', type=str,
                        default=None, help='Path to the 140KV scans.')
    parser.add_argument('--batch-name', type=str,
                        default=None, help='Name of the batch.')


    args = parser.parse_args()
    num_scan = args.num_scan
    index = args.index
    trim = args.trim
    low_dir = args.low_dir
    high_dir = args.high_dir
    batch_name = args.batch_name 

    # root_dir = 'scans'
    # low_dir = os.path.join(root_dir, '80KV')
    # high_dir = os.path.join(root_dir, '140KV')
    low_list = [os.path.join(low_dir, f.upper()) for f in os.listdir(low_dir) if f.upper().endswith('.IMA')][:num_scan]
    high_list = [os.path.join(high_dir, f.upper()) for f in os.listdir(high_dir) if f.upper().endswith('.IMA')][:num_scan]

    low_post_maps = []
    high_post_maps = []
    brown_mask_maps = []
    white_mask_maps = []
    difference_maps = []

    for idx, (low_scan, high_scan) in enumerate(zip(low_list, high_list)):
        print(f'Processing image No.{idx + 1}...')
        low_post_hu = load_hu(low_scan, trim)
        high_post_hu = load_hu(high_scan, trim)

        # Bilateral filter
        low_post_hu = denoise_bilateral(low_post_hu, sigma_color=5, sigma_spatial=2)
        high_post_hu = denoise_bilateral(high_post_hu, sigma_color=5, sigma_spatial=2)

        # Generate brown fat mask
        brown_mask = np.ones_like(low_post_hu)
        brown_mask = np.logical_and(brown_mask, ((low_post_hu >= -130) & (low_post_hu <= 0)))
        brown_mask = np.logical_and(brown_mask, ((high_post_hu >= -130) & (high_post_hu <= 0)))
        brown_mask = np.logical_and(brown_mask, (high_post_hu - 30 < low_post_hu))
        brown_mask = binary_erosion(brown_mask, disk(2))
        brown_mask = remove_small_objects(brown_mask, 64)

        # Generate white fat mask
        white_mask = np.ones_like(low_post_hu)
        white_mask = np.logical_and(white_mask, ((low_post_hu >= -200) & (low_post_hu <= 0)))
        white_mask = np.logical_and(white_mask, ((high_post_hu >= -200) & (high_post_hu <= 0)))
        white_mask = np.logical_and(white_mask, (high_post_hu > low_post_hu))
        white_mask = binary_erosion(white_mask, disk(5))
        white_mask = remove_small_objects(white_mask, 32)

        difference = np.where(brown_mask, low_post_hu - high_post_hu, -100)

        low_post_maps.append(low_post_hu)
        high_post_maps.append(high_post_hu)
        brown_mask_maps.append(brown_mask)
        white_mask_maps.append(white_mask)
        difference_maps.append(difference)

    low_post_maps = np.array(low_post_maps)
    high_post_maps = np.array(high_post_maps)
    brown_mask_maps = np.array(brown_mask_maps)
    white_mask_maps = np.array(white_mask_maps)
    difference_maps = np.array(difference_maps)

    # write to npy
    np.savez(f'output\\{batch_name}.npz',
             low_post_maps=low_post_maps,
             high_post_maps=high_post_maps,
             brown_mask_maps=brown_mask_maps,
             white_mask_maps=white_mask_maps)

    # write to dcm
    write_decom(low_post_maps, 'output\\80KV.DCM', series_name='low')
    write_decom(high_post_maps, 'output\\140KV.DCM', series_name='high')
    write_decom(brown_mask_maps, 'output\\BROWN_MASK.DCM', series_name='brown_mask')
    write_decom(white_mask_maps, 'output\\WHITE_MASK.DCM', series_name='white_mask')
    write_decom(difference_maps, 'output\\DIFF_MAP.DCM', series_name='diff_map')

    # show the corresponding image
    show_pair((low_post_maps[index], high_post_maps[index]), (-200, 0), title='Post scans')
    show_pair((brown_mask_maps[index], white_mask_maps[index]), (0, 1), title='Masks')
    plt.show()

if __name__ == '__main__':
    main()