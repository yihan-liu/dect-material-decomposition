import os
import re

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

from sklearn.linear_model import LinearRegression

def get_scan_paths(base_dir, group_code):
    group_mapping = {
        "POST_HIGH": re.compile(r'POST.*140KV'),
        "POST_LOW": re.compile(r'POST.*80KV'),
        "PRE_HIGH": re.compile(r'PRE.*140KV'),
        "PRE_LOW": re.compile(r'PRE.*80KV')
    }
    
    if group_code not in group_mapping:
        raise ValueError("Invalid group code provided.")
    pattern = group_mapping[group_code]
    scan_paths = []
    
    for root, dirs, files in os.walk(base_dir):
        for folder in dirs:
            if pattern.search(folder):
                folder_path = os.path.join(root, folder)
                for file in os.listdir(folder_path):
                    if file.endswith(".IMA"):
                        scan_paths.append(os.path.join(folder_path, file))
    
    return scan_paths

def show_pair(img_pair, color_range):
    ''' Show a pair of two images.
    '''
    img1 = img_pair[0]
    img2 = img_pair[1]
    
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    im1 = axes[0].imshow(img1, cmap='gray', vmin=color_range[0], vmax=color_range[1])
    im2 = axes[1].imshow(img2, cmap='gray', vmin=color_range[0], vmax=color_range[1])
    
    divider = make_axes_locatable(axes[0])
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im1, cax=cax, orientation='vertical')
    divider = make_axes_locatable(axes[1])
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im2, cax=cax, orientation='vertical')
