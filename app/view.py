# view.py

import threading

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from tkinter import ttk as tk
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class HUApp(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller  # HUController
        self.pack(fill=BOTH, expand=YES)
        self.create_widgets()
        
    def create_widgets(self):
        # Row 0: start scan index
        self.start_scan_label = ttk.Label(self, text='Start Scan Index:')
        self.start_scan_entry = ttk.Entry(self)
        self.start_scan_entry.insert(0, '1')
        
        self.start_scan_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.start_scan_entry.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        
        # Row 1: end scan index
        self.end_scan_label = ttk.Label(self, text='End Scan Index:')
        self.end_scan_entry = ttk.Entry(self)
        self.end_scan_entry.insert(0, '250')
        
        self.end_scan_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.end_scan_entry.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        # Row 2: Index of Scan to Show
        self.index_label = ttk.Label(self, text='Index of Scan to Show:')
        self.index_entry = ttk.Entry(self)
        self.index_entry.insert(0, "200")

        self.index_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.index_entry.grid(row=2, column=1, sticky=W, padx=5, pady=5)
        
        # Row 3: Trim (left, top, right, bottom)
        self.trim_label = ttk.Label(self, text='Trim (left top right bottom)')
        self.trim_entries = []
        for i in range(4):
            entry = ttk.Entry(self, width=5)
            self.trim_entries.append(entry)
            entry.grid(row=3, column=1 + i, sticky=W, padx=2, pady=5)
        self.trim_label.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        
        # Row 4: Low Post directory
        self.low_post_label = ttk.Label(self, text='80KV Post Directory:')
        self.low_post_entry = ttk.Entry(self, width=50)
        self.low_post_button = ttk.Button(self, text='Browse', command=self.browse_low_post_dir)
        
        self.low_post_label.grid(row=4, column=0, sticky=W, padx=5, pady=5)
        self.low_post_entry.grid(row=4, column=1, columnspan=3, sticky=W, padx=5, pady=5)
        self.low_post_button.grid(row=4, column=4, sticky=W, padx=5, pady=5)
        
        # Row 5: High Post directory
        self.high_post_label = ttk.Label(self, text='140KV Post Directory:')
        self.high_post_entry = ttk.Entry(self, width=50)
        self.high_post_button = ttk.Button(self, text='Browse', command=self.browse_high_post_dir)
        
        self.high_post_label.grid(row=5, column=0, sticky=W, padx=5, pady=5)
        self.high_post_entry.grid(row=5, column=1, columnspan=3, sticky=W, padx=5, pady=5)
        self.high_post_button.grid(row=5, column=4, sticky=W, padx=5, pady=5)
        
        # Row 6: Low Pre directory
        self.low_pre_label = ttk.Label(self, text='80KV Pre Directory:')
        self.low_pre_entry = ttk.Entry(self, width=50)
        self.low_pre_button = ttk.Button(self, text='Browse', command=self.browse_low_pre_dir)
        
        self.low_pre_label.grid(row=6, column=0, sticky=W, padx=5, pady=5)
        self.low_pre_entry.grid(row=6, column=1, columnspan=3, sticky=W, padx=5, pady=5)
        self.low_pre_button.grid(row=6, column=4, sticky=W, padx=5, pady=5)
        
        # Row 7: High Pre directory
        self.high_pre_label = ttk.Label(self, text='140KV Pre Directory:')
        self.high_pre_entry = ttk.Entry(self, width=50)
        self.high_pre_button = ttk.Button(self, text='Browse', command=self.browse_high_pre_dir)
        
        self.high_pre_label.grid(row=7, column=0, sticky=W, padx=5, pady=5)
        self.high_pre_entry.grid(row=7, column=1, columnspan=3, sticky=W, padx=5, pady=5)
        self.high_pre_button.grid(row=7, column=4, sticky=W, padx=5, pady=5)
        
        # Row 8: Enable image registration (Checkbox)
        self.register_var = BooleanVar()
        self.register_check = ttk.Checkbutton(self, text='Enable Registration', variable=self.register_var)
        self.register_check.grid(row=8, column=0, sticky=W, padx=5, pady=5)
        
        # Row 9: Batch name
        self.batch_name_label = ttk.Label(self, text='Batch Name:')
        self.batch_name_entry = ttk.Entry(self)
        self.batch_name_label.grid(row=9, column=0, sticky=W, padx=5, pady=5)
        self.batch_name_entry.grid(row=9, column=1, sticky=W, padx=5, pady=5)
        
        # Row 10: Process Button
        self.process_button = ttk.Button(self, text='Process', command=self.start_processing)
        self.process_button.grid(row=10, column=0, padx=5, pady=20)
        
    # Browse methods
    def browse_low_post_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.low_post_entry.delete(0, END)
            self.low_post_entry.insert(0, dir_name)
    
    def browse_high_post_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.high_post_entry.delete(0, END)
            self.high_post_entry.insert(0, dir_name)
    
    def browse_low_pre_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.low_pre_entry.delete(0, END)
            self.low_pre_entry.insert(0, dir_name)
    
    def browse_high_pre_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.high_pre_entry.delete(0, END)
            self.high_pre_entry.insert(0, dir_name)
            
    # Processes
    def start_processing(self):
        # Run processing in a separate thread to keep GUI responsive
        threading.Thread(target=self.controller.process_data).start()
        
    def get_input_values(self):
        # Get input values
        start_scan = int(self.start_scan_entry.get())
        end_scan = int(self.end_scan_entry.get())
        index = int(self.index_entry.get())
        
        # Get trim values
        trim_values = []
        for entry in self.trim_entries:
            value = entry.get()
            if value:
                trim_values.append(int(value))
        if len(trim_values) == 4:
            trim = trim_values
        else:
            trim = None
            
        low_post_dir = self.low_post_entry.get()
        high_post_dir = self.high_post_entry.get()
        low_pre_dir = self.low_pre_entry.get()
        high_pre_dir = self.high_pre_entry.get()
        enable_register = self.register_var.get()
        batch_name = self.batch_name_entry.get()
        
        return {
            'start_scan': start_scan,
            'end_scan': end_scan,
            'index': index,
            'trim': trim,
            'low_post_dir': low_post_dir,
            'high_post_dir': high_post_dir,
            'low_pre_dir': low_pre_dir,
            'high_pre_dir': high_pre_dir,
            'enable_register': enable_register,
            'batch_name': batch_name
        }
        
    def display_images(self, image_pair, mask_pair):
        # Create a new window to display images
        image_window = Toplevel(self)
        image_window.title('Images')
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(8, 8))
        
        # Show images
        axes[0, 0].imshow(image_pair[0], cmap='gray', vmin=-200, vmax=100)
        axes[0, 0].set_title('Low Post Scan')

        axes[0, 1].imshow(image_pair[1], cmap='gray', vmin=-200, vmax=100)
        axes[0, 1].set_title('High Post Scan')

        axes[1, 0].imshow(mask_pair[0], cmap='gray', vmin=0, vmax=1)
        axes[1, 0].set_title('Brown Mask')

        axes[1, 1].imshow(mask_pair[1], cmap='gray', vmin=0, vmax=1)
        axes[1, 1].set_title('White Mask')
        
        # Remove axes ticks
        for ax in axes.flat:
            ax.axis('off')
            
        plt.tight_layout()
        
        # Create a canvas and add the figure to it
        canvas = FigureCanvasTkAgg(fig, master=image_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
        # Close the figure to prevent memory leaks
        plt.close(fig)
        
    def show_error(self, message):
        messagebox.showerror('Error', message)
        
    def show_info(self, message):
        messagebox.showinfo('Info', message)