# ======== Select a directory:

import Tkinter as tk
import tkFileDialog, tkMessageBox
import os
import shutil

from dist_creator import get_flat_packages, create_copy, CreateCopyError

packages_disclaimer = """#Comment or remove the packages that you want to avoid in your distribution\n\n"""
root_path = "/home/antonio/Projects/LightPy"

class App(object):

    dirname = ''
    
    def __init__(self,root):
        
        self.root = root
                
        self.main_frame = tk.Frame(self.root)
        
        self.main_label = tk.Label(self.main_frame, text="Select the modules for your distribution:")
        
        self.packages_frame = tk.Frame(self.main_frame)
        self.packages_box = tk.Text(self.packages_frame,
                                   height=10)
        self.packages_scroll = tk.Scrollbar(self.packages_frame)
        self.packages_box.config(yscrollcommand=self.packages_scroll.set)
        self.packages_scroll.config(command=self.packages_box.yview)
        self.packages_box.pack(side=tk.LEFT)
        self.packages_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)
        
        self.license_label = tk.Label(self.main_frame, text="Place here your license:")

        self.license_frame = tk.Frame(self.main_frame)
        self.license_scroll = tk.Scrollbar(self.license_frame)
        self.license_box = tk.Text(self.license_frame,
                                   height=10)
        self.license_box.config(yscrollcommand=self.license_scroll.set)
        self.license_scroll.config(command=self.license_box.yview)
        self.license_box.pack(side=tk.LEFT)
        self.license_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        self.dist_name_frame = tk.Frame(self.main_frame)
        self.dist_name_label = tk.Label(self.dist_name_frame, text="Distribution name: ")
        self.dist_name_entry = tk.Entry(self.dist_name_frame)
        self.dist_name_entry.insert(0, "new_distribution_name")
        
        self.dist_name_label.pack(side=tk.LEFT)
        self.dist_name_entry.pack(side=tk.LEFT)        
                                   
        self.buttons_frame = tk.Frame(self.main_frame)
        
        self.button_find = tk.Button(self.buttons_frame, 
                                     text="Find",
                                     command=self.event_find_packages)
        self.button_refresh = tk.Button(self.buttons_frame,
                                        text="Refresh",
                                        command=self.event_refresh)
        self.button_next = tk.Button(self.buttons_frame,
                                     text="Create",
                                     command=self.event_next)        
        
        self.button_find.pack(side=tk.LEFT)
        self.button_refresh.pack(side=tk.LEFT)
        self.button_next.pack(side=tk.LEFT)
        
        self.main_label.pack(side=tk.TOP)
        self.packages_frame.pack(side=tk.TOP)
        self.license_label.pack(side=tk.TOP)
        self.license_frame.pack(side=tk.TOP)
        self.dist_name_frame.pack(side=tk.LEFT)
        self.buttons_frame.pack(side=tk.TOP)
        
        self.main_frame.pack()
    
    def set_packages(self, packages_list):
        self.packages_box.delete(1.0, tk.END)
        self.packages_box.insert(1.0, packages_disclaimer + '\n'.join(packages_list))
    
    def event_find_packages(self):
        dirname = tkFileDialog.askdirectory(parent=self.root,initialdir=root_path,title='Please select source directory')
        if dirname:
            self.dirname = dirname
            packages = get_flat_packages(self.dirname)
            self.set_packages(packages)
        
    def event_refresh(self):
        if self.dirname:
            packages = get_flat_packages(self.dirname)
            self.set_packages(packages)
    
    def event_next(self):
        original_packages = get_flat_packages(self.dirname)
        pre_processed_packages = self.packages_box.dump(1.0, tk.END)
        processed_packages = []
        for t, v, i in pre_processed_packages:
            v = v.strip()
            if v and t == 'text' and v[0] != '#':
                if v in original_packages:
                    processed_packages.append(v)
        
        if processed_packages:
            target_path = tkFileDialog.askdirectory(parent=self.root,initialdir='/tmp',title='Please select target directory')
            target_path = os.path.join(target_path, self.dist_name_entry.get())
            
            try:
                create_copy(self.dirname,target_path,processed_packages)
            except CreateCopyError:
                print 'meleca' 
                    
    
    
if __name__=='__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    




