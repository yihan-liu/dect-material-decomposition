import os
import argparse

import numpy as np

from utils import get_scan_paths
from hu_utils import load_hu

parser = argparse.ArgumentParser()
parser.add_argument('batch_path', type=str,
                    help='Path for a batch of scan slices.')
parser.add_argument('-r', '--root_dir', type=str,
                    default='Images', help='Root directory for the scan slices.')
parser.add_argument('-n', '--num_scan', type=int,
                    default=500, help='Number of scan slices to load.')
parser.add_argument('-s', '--first_scan', type=int,
                    default=0, help='Index of the first scan from which to load the rest of the scans.')
parser.add_argument('-l', '--last_scan', help='Index of the last scan.')
# parser.add_argument('-o', '--offset')  # TODO
parser.add_argument('-t', '--trim', nargs=4, type=int,
                    default=None, help='Range of the scan of interest, used for removing unwanted part of the scan.')

args = parser.parse_args()
batch_path = args.batch_path
root_dir = args.root_dir
num_scan = args.num_scan
first_scan = args.first_scan
last_scan = args.last_scan
# offset = args.offset
trim = args.trim

low_post_maps = []
high_post_maps = []
# low_pre_maps = []
# high_pre_maps = []

if last_scan is not None:
    assert last_scan == first_scan + num_scan
    idx_list = np.arange(first_scan, last_scan + 0.5, 1).astype(int)
else:
    idx_list = np.arange(first_scan, first_scan + num_scan + 0.5, 1).astype(int)

for idx in idx_list:
    # NOTE: Pre-xenon samples are not needed for now
    path_low_post = get_scan_paths(os.path.join(root_dir, batch_path), 'POST_LOW')[idx]
    path_high_post = get_scan_paths(os.path.join(root_dir, batch_path), 'POST_HIGH')[idx]
    # path_low_pre = get_scan_paths(os.path.join(root_dir, batch_path), 'PRE_LOW')[idx]
    # path_high_pre = get_scan_paths(os.path.join(root_dir, batch_path), 'PRE_HIGH')[idx]
    
    low_post_hu = load_hu(path_low_post, trim)
    high_post_hu = load_hu(path_high_post, trim)
    # low_pre_hu = load_hu(path_low_pre, trim)
    # high_pre_hu = load_hu(path_high_pre, trim)
    
    low_post_maps.append(low_post_hu)
    high_post_maps.append(high_post_hu)
    # low_pre_maps.append(low_pre_hu)
    # high_pre_maps.append(high_pre_hu)
    
low_post_maps = np.array(low_post_maps)
high_post_maps = np.array(high_post_maps)
# low_pre_maps = np.array(low_pre_maps)
# high_pre_maps = np.array(high_pre_maps)

np.save(os.path.join('images_np', batch_path + '-LOW') + '.npy', low_post_maps)
np.save(os.path.join('images_np', batch_path + '-HIGH') + '.npy', high_post_maps)