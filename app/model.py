# model.py

import os
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

class HUProcessor():
    def __init__(self, start_scan=1, end_scan=250, index=200, trim=None,
                 low_post_dir=None, high_post_dir=None, low_pre_dir=None, high_pre_dir=None,
                 enable_register=False, batch_name=None):
        self.start_scan = start_scan
        self.end_scan = end_scan
        self.index = index
        self.trim = trim
        self.low_post_dir = low_post_dir
        self.high_post_dir = high_post_dir
        self.low_pre_dir = low_pre_dir
        self.high_pre_dir = high_pre_dir
        self.enable_register = enable_register
        self.batch_name = batch_name
        
        # Data placeholders
        self.low_pre_maps = None
        self.low_post_maps = None
        self.high_pre_maps = None
        self.high_post_maps = None
        self.brown_mask_maps = None
        self.white_mask_maps = None
        self.difference_maps = None
        
    def process(self):
        start_scan = self.start_scan
        end_scan = self.end_scan
        index = self.index
        trim = self.trim
        low_post_dir = self.low_post_dir
        high_post_dir = self.high_post_dir
        low_pre_dir = self.low_pre_dir
        high_pre_dir = self.high_pre_dir
        enable_register = self.enable_register
        batch_name = self.batch_name
        
        # Build file lists
        low_pre_list = sorted([os.path.join(low_pre_dir, f) for f in os.listdir(low_pre_dir) if f.upper().endswith('.IMA')])[start_scan - 1: end_scan]
        low_post_list = sorted([os.path.join(low_post_dir, f) for f in os.listdir(low_post_dir) if f.upper().endswith('.IMA')])[start_scan - 1: end_scan]
        high_pre_list = sorted([os.path.join(high_pre_dir, f) for f in os.listdir(high_pre_dir) if f.upper().endswith('.IMA')])[start_scan - 1: end_scan]
        high_post_list = sorted([os.path.join(high_post_dir, f) for f in os.listdir(high_post_dir) if f.upper().endswith('.IMA')])[start_scan - 1: end_scan]
        
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
            if enable_register:
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
            else:
                registered_high_pre_hu = high_pre_hu
                registered_low_pre_hu = low_pre_hu

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

        self.low_pre_maps = np.array(low_pre_maps)
        self.low_post_maps = np.array(low_post_maps)
        self.high_pre_maps = np.array(high_pre_maps)
        self.high_post_maps = np.array(high_post_maps)
        self.brown_mask_maps = np.array(brown_mask_maps)
        self.white_mask_maps = np.array(white_mask_maps)
        self.difference_maps = np.array(difference_maps)
        
        # Ensure output directory exists
        os.makedirs('..\\output', exist_ok=True)
        
        # Write to npz
        np.savez(f'output\\{batch_name}.npz',
                 low_pre_maps=self.low_pre_maps,
                 low_post_maps=self.low_post_maps,
                 high_pre_maps=self.high_pre_maps,
                 high_post_maps=self.high_post_maps,
                 brown_mask_maps=self.brown_mask_maps,
                 white_mask_maps=self.white_mask_maps)
        
         # Write to DICOM
        write_decom(self.low_pre_maps, 'output\\PRE_80KV.DCM', series_name='low')
        write_decom(self.low_post_maps, 'output\\POST_80KV.DCM', series_name='low')
        write_decom(self.high_pre_maps, 'output\\PRE_140KV.DCM', series_name='high')
        write_decom(self.high_post_maps, 'output\\POST_140KV.DCM', series_name='high')
        write_decom(self.brown_mask_maps, 'output\\BROWN_MASK.DCM', series_name='brown_mask')
        write_decom(self.white_mask_maps, 'output\\WHITE_MASK.DCM', series_name='white_mask')
        write_decom(self.difference_maps, 'output\\DIFF_MAP.DCM', series_name='diff_map')


    def get_image_pair(self):
        index = self.index - self.start_scan
        return (self.low_post_maps[index], self.high_post_maps[index])

    def get_mask_pair(self):
        index = self.index - self.start_scan
        return (self.brown_mask_maps[index], self.white_mask_maps[index])