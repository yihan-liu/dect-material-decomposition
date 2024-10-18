# app.py

import ttkbootstrap as ttk
from controller import HUController

def main():
    style = ttk.Style('cosmo')
    root = style.master
    root.title('HU Processor')
    root.geometry('1200x800')
    controller = HUController(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()