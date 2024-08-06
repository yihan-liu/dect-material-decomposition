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

def region_growing(image, seed_point, threshold):
    rows, cols = image.shape
    segmented_image = np.zeros_like(image, dtype=bool)
    seed_value = image[seed_point]

    # Initialize the list of points to be checked with the seed point
    points_to_check = [seed_point]
    segmented_image[seed_point] = True

    while points_to_check:
        current_point = points_to_check.pop(0)
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_point = (current_point[0] + i, current_point[1] + j)
                if (0 <= neighbor_point[0] < rows and
                    0 <= neighbor_point[1] < cols and
                    not segmented_image[neighbor_point] and
                    abs(image[neighbor_point] - seed_value) < threshold):
                    segmented_image[neighbor_point] = True
                    points_to_check.append(neighbor_point)

    return segmented_image

def energy_correlation(reg_range, roi_values_pair):
    roi_low_values = roi_values_pair[0]
    roi_high_values = roi_values_pair[1]
    
    linear_regressor = LinearRegression()
    linear_regressor.fit(roi_low_values.reshape(-1, 1),
                         roi_high_values.reshape(-1, 1))
    
    x = np.arange(reg_range[0], reg_range[1], 1)
    y = linear_regressor.predict(x.reshape(-1, 1))
    
    slope = linear_regressor.coef_.item(0)
    intercept = linear_regressor.intercept_.item(0)
    
    return x, y, slope, intercept
