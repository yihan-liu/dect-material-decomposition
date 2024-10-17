# controller.py

import threading

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from model import HUProcessor
from view import HUApp

class HUController():
    def __init__(self, root):
        self.root = root
        self.app = HUApp(root, self)
        self.processor = None
        
    def process_data(self):
        # Get inputs from the view
        inputs = self.app.get_input_values()
        
        if not inputs['batch_name']:
            self.app.show_error('Please enter a batch name.')
            return
        
        # Create processor instance
        self.processor = HUProcessor(
            start_scan=inputs['start_scan'],
            end_scan=inputs['end_scan'],
            index=inputs['index'],
            trim=inputs['trim'],
            low_post_dir=inputs['low_post_dir'],
            high_post_dir=inputs['high_post_dir'],
            low_pre_dir=inputs['low_pre_dir'],
            high_pre_dir=inputs['high_pre_dir'],
            enable_register=inputs['enable_register'],
            batch_name=inputs['batch_name']
        )
        
        self.run()
        # Run processing in a background thread to avoid blocking the GUI
        # threading.Thread(target=self.run)
            
        
    def run(self):
        try:
            # Call the process method
            self.processor.process()
            
            # After processing, schedule image display on the main thread
            # self.root.after(0, self.display_images)
        except Exception as e:
            self.app.show_error(str(e))
            # self.root.after(0, self.app.show_error, str(e))
    
    def display_images(self):
        # Get the images after processing
        image_pair = self.processor.get_image_pair()
        mask_pair = self.processor.get_mask_pair()
        
        # Call the view to display images
        self.app.display_images(image_pair, mask_pair)
        self.app.show_info('Processing completed.')