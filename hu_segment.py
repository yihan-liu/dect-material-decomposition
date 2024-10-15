
import os
import argparse

import numpy as np
import matplotlib.pyplot as plt
from skimage.restoration import denoise_bilateral
from skimage.morphology import disk
from skimage.morphology import binary_dilation, binary_erosion
from skimage.morphology import remove_small_objects
import SimpleITK as sitk

from hu_utils import load_hu, write_decom
from utils import show_pair
from hu_process import register_bspline

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-scan', type=int,
                        default=1, help='Index of scan slice to start loading.')
    parser.add_argument('-e', '--end-scan', type=int,
                        default=250, help='Index of scan slice to end loading.')
    parser.add_argument('-i', '--index', type=int,
                        default=200, help='Index of scan show.')
    parser.add_argument('-t', '--trim', nargs=4, type=int,
                        default=None, help='Range of the scan of interest, used for removing unwanted part of the scan.')
    parser.add_argument('--low-post-dir', type=str,
                        default=None, help='Path to the post-xenon 80KV scans.')
    parser.add_argument('--high-post-dir', type=str,
                        default=None, help='Path to the post-xenon 140KV scans.')
    parser.add_argument('--low-pre-dir', type=str,
                        default=None, help='Path to the pre-xenon 80KV scans.')
    parser.add_argument('--high-pre-dir', type=str,
                        default=None, help='Path to the pre-xenon 140KV scans.')
    parser.add_argument('--batch-name', type=str,
                        default=None, help='Name of the batch.')


    args = parser.parse_args()
    start_scan = args.start_scan
    end_scan = args.end_scan
    index = args.index
    trim = args.trim
    low_post_dir = args.low_post_dir
    high_post_dir = args.high_post_dir
    low_pre_dir = args.low_pre_dir  # TODO
    high_pre_dir = args.high_pre_dir  # TODO
    batch_name = args.batch_name 

    low_pre_list = [os.path.join(low_pre_dir, f.upper()) for f in os.listdir(low_pre_dir) if f.upper().endswith('.IMA')][start_scan - 1: end_scan - 1]
    low_post_list = [os.path.join(low_post_dir, f.upper()) for f in os.listdir(low_post_dir) if f.upper().endswith('.IMA')][start_scan - 1: end_scan - 1]
    high_pre_list = [os.path.join(high_pre_dir, f.upper()) for f in os.listdir(high_pre_dir) if f.upper().endswith('.IMA')][start_scan - 1: end_scan - 1]
    high_post_list = [os.path.join(high_post_dir, f.upper()) for f in os.listdir(high_post_dir) if f.upper().endswith('.IMA')][start_scan - 1: end_scan - 1]

    low_pre_maps = []  # registered, only for reference
    low_post_maps = []
    high_pre_maps = []  # registered, only for reference
    high_post_maps = []
    
    # The following maps are calculated from post maps
    brown_mask_maps = []
    white_mask_maps = []
    difference_maps = []

    for idx, (low_pre_path, low_post_path, high_pre_path, high_post_path) in enumerate(zip(low_pre_list, low_post_list, high_pre_list, high_post_list)):
        print(f'Processing image No.{idx + 1}...')
        low_pre_hu = load_hu(low_pre_path, trim)
        low_post_hu = load_hu(low_post_path, trim)
        high_pre_hu = load_hu(high_pre_path, trim)
        high_post_hu = load_hu(high_post_path, trim)

        # Registration
        _, registered_high_pre_hu, transform_mat = register_bspline(high_post_hu, high_pre_hu)
        low_pre_img = sitk.GetImageFromArray(low_pre_hu)
        low_post_img = sitk.GetImageFromArray(low_post_hu)
        registered_low_pre_img = sitk.Resample(
            low_pre_img, low_post_img,
            transform_mat,
            sitk.sitkLinear,
            0.0,
            low_pre_img.GetPixelID())
        registered_low_pre_hu = sitk.GetArrayFromImage(registered_low_pre_img)

        # Bilateral filter
        low_pre_hu = denoise_bilateral(registered_low_pre_hu, sigma_color=5, sigma_spatial=2)
        low_post_hu = denoise_bilateral(low_post_hu, sigma_color=5, sigma_spatial=2)
        high_pre_hu = denoise_bilateral(registered_high_pre_hu, sigma_color=5, sigma_spatial=2)
        high_post_hu = denoise_bilateral(high_post_hu, sigma_color=5, sigma_spatial=2)

        # Generate brown fat mask (calculated from post xenon scans)
        brown_mask = np.ones_like(low_post_hu)
        brown_mask = np.logical_and(brown_mask, ((low_post_hu >= -130) & (low_post_hu <= 0)))
        brown_mask = np.logical_and(brown_mask, ((high_post_hu >= -130) & (high_post_hu <= 0)))
        brown_mask = np.logical_and(brown_mask, (high_post_hu - 30 < low_post_hu))
        brown_mask = binary_erosion(brown_mask, disk(2))
        brown_mask = remove_small_objects(brown_mask, 64)

        # Generate white fat mask (calculated from post xenon scans)
        white_mask = np.ones_like(low_post_hu)
        white_mask = np.logical_and(white_mask, ((low_post_hu >= -200) & (low_post_hu <= 0)))
        white_mask = np.logical_and(white_mask, ((high_post_hu >= -200) & (high_post_hu <= 0)))
        white_mask = np.logical_and(white_mask, (high_post_hu > low_post_hu))
        white_mask = binary_erosion(white_mask, disk(5))
        white_mask = remove_small_objects(white_mask, 32)

        difference = np.where(brown_mask, low_post_hu - high_post_hu, -100)

        low_pre_maps.append(low_pre_hu)
        low_post_maps.append(low_post_hu)
        high_pre_maps.append(high_pre_hu)
        high_post_maps.append(high_post_hu)
        brown_mask_maps.append(brown_mask)
        white_mask_maps.append(white_mask)
        difference_maps.append(difference)

    low_pre_maps = np.array(low_pre_maps)
    low_post_maps = np.array(low_post_maps)
    high_pre_maps = np.array(high_pre_maps)
    high_post_maps = np.array(high_post_maps)
    brown_mask_maps = np.array(brown_mask_maps)
    white_mask_maps = np.array(white_mask_maps)
    difference_maps = np.array(difference_maps)

    # write to npy
    np.savez(f'output\\{batch_name}.npz',
             low_pre_maps=low_pre_maps,
             low_post_maps=low_post_maps,
             high_pre_maps=high_pre_maps,
             high_post_maps=high_post_maps,
             brown_mask_maps=brown_mask_maps,
             white_mask_maps=white_mask_maps)

    # write to dcm
    write_decom(low_pre_maps, 'output\\80KV.DCM', series_name='low')
    write_decom(low_post_maps, 'output\\80KV.DCM', series_name='low')
    write_decom(high_pre_maps, 'output\\140KV.DCM', series_name='high')
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
