import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox
import os
import shutil

import tree

from dist_creator import *
import tests_runner

root_path = "~"
default_target_path = '~'

class App(object):

    origin_path = ''
    
    def __init__(self,root):
        
        self.root = root

        self.tree_view = None
                
        self.main_frame = tk.Frame(self.root)
        
        self.main_label = tk.Label(self.main_frame, text="Select the modules for your distribution:")
        
        self.checkbuttons_frame = tk.Frame(self.root)
        
        self.packages_frame = tk.Frame(self.main_frame,height=400, width=600 )
        self.packages_scroll = tk.Scrollbar(self.checkbuttons_frame)
        
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
                                     text="Open",
                                     command=self.event_find_packages,
                                     width=8)
        self.button_refresh = tk.Button(self.buttons_frame,
                                        text="Refresh",
                                        command=self.event_refresh,
                                        width=8)
        self.button_next = tk.Button(self.buttons_frame,
                                     text="Create",
                                     command=self.event_next,
                                     width=8)
        
        self.button_find.pack(side=tk.LEFT)
        self.button_refresh.pack(side=tk.LEFT)
        self.button_next.pack(side=tk.LEFT)
        
        self.main_label.pack(side=tk.TOP, anchor='w')
        self.packages_frame.pack(side=tk.TOP, anchor='w')
        self.license_label.pack(side=tk.TOP, anchor='w')
        self.license_frame.pack(side=tk.TOP)
        self.dist_name_frame.pack(side=tk.LEFT)
        self.buttons_frame.pack(side=tk.TOP)
        
        self.main_frame.pack()
    

    def set_packages(self, packages_list):
        
        if self.tree_view:
            self.tree_view.forget()
    
        self.tree_view = tree.CheckboxTree(self.packages_frame, 
                                          items=packages_list,
                                          height=400,
                                          width=600)
    
    def event_find_packages(self):
        origin_path = tkFileDialog.askdirectory(parent=self.root,
                                                initialdir=root_path,
                                                title='Please select source directory')
        if origin_path:
            self.origin_path = origin_path
            packages = get_folder_tree(self.origin_path)[0]
            self.set_packages(packages)
        
    
    def event_refresh(self):
        for package in self.packages_variables.values():
            package['var'].set(1)
    
    def event_next(self):

        if not self.origin_path:
            return
        
        blah = self.tree_view.get_checked_items()
        import pdb; pdb.set_trace()

        license = self.license_box.get(1.0, tk.END)
        raw_packages = [package['button']['text'] for package in self.packages_variables.values() if package['var'].get()]

        if not license.strip():
            if not tkMessageBox.askokcancel('License','No license found. Do you want to proceed anyway?'):
                return
            else:
                license = ''

        self.target_path = tkFileDialog.askdirectory(parent=self.root,
                                                     initialdir=default_target_path,
                                                     title='Please select target directory')
        
        if self.target_path:
            self.target_path = os.path.join(self.target_path, self.dist_name_entry.get())
            
        if process_copy(self.origin_path, self.target_path, raw_packages, license):
            do_tests = tkMessageBox.askyesno(message='Copy finished\nDo you want to scan for tests?')
            if do_tests:
                self.do_tests()
        
    def do_tests(self):

        test_files = tests_runner.list_tests_from_directory(self.target_path)        
        output_log = tests_runner.run_tests(test_files)

        log_window = tk.Toplevel(self.root)
        log_board = LogBoard(log_window)
        log_board.fill_board(output_log)
        log_window.transient(self.root)
        log_window.grab_set()
        self.root.wait_window()


class LogBoard(object):
    def __init__(self, root):
        
        self.root = root
        self.log_saved = False
        
        self.text_frame = tk.Frame(self.root )
        self.text_board = tk.Text(self.text_frame, height=40, width=100 )
        self.text_scroll = tk.Scrollbar(self.text_frame)
        
        self.text_board.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_board.yview)
        self.text_board.pack(side=tk.LEFT)
        self.text_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        self.buttons_frame = tk.Frame(self.root)
        self.button_save = tk.Button(self.buttons_frame,
                                     text="Save",
                                     command=self.event_save_log,
                                     width=8)
        self.button_quit = tk.Button(self.buttons_frame,
                                     text="Quit",
                                     command=self.event_quit,
                                     width=8)
        self.button_save.pack(side=tk.LEFT)
        self.button_quit.pack(side=tk.LEFT)

        
        self.text_frame.pack()
        self.buttons_frame.pack()
    
    def fill_board(self, text):
        self.text_board.insert(1.0, text)

    def event_save_log(self):
        fout = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt", parent=self.root)

        if fout:
            log = unicode(self.text_board.get(0.0,tk.END))
            fout.write(log)
            fout.close()
            self.log_saved = True 
    
    def event_quit(self):
        if not self.log_saved:
            if not tkMessageBox.askokcancel('Log not yet saved', 'Log file is not yet saved.\nDo you want to quit anyway?', parent=self.root):
                return
        self.root.destroy()
        
    
if __name__=='__main__':
    root = Tix.Tk()
    app = App(root)
    root.mainloop()

