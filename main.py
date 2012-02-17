import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox

import os
import shutil
import pickle 

import tree

from dist_creator import *
import tests_runner

root_path = "~"
default_target_path = '~'
DIST_FILE_VERSION = 'v0'

class App(object):

    origin_path = ''
    
    def __init__(self,root):

        
        self.root = root

        self.tree_view = None
        self.changed = False

        #Project issues
        self.project_name = None
        self.project_file_path = None #path of the file .dist

        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Project", command=self.load_project)
        self.filemenu.add_command(label="Save Project", command=self.save_project)
        self.filemenu.add_command(label="Save Project As ...", command=self.save_project_as)
        self.filemenu.add_command(label="New Project", command=self.new_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="Project", menu=self.filemenu)
        self.root.config(menu=self.menubar)
                
        self.main_frame = tk.Frame(self.root)
        
        self.main_label = tk.Label(self.main_frame, text="Select the modules for your distribution:")
        
        self.checkbuttons_frame = tk.Frame(self.root)
        
        self.packages_frame = tk.Frame(self.main_frame,height=400, width=600 )
        
        self.license_label = tk.Label(self.main_frame, text="License:")

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
                                     text="Load",
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
    
    def change_function(self):
        self.changed = True

    def set_packages(self, packages_list):
        
        if self.tree_view:
            self.tree_view.forget()
    
        self.tree_view = tree.CheckboxTree(self.packages_frame, 
                                          items=packages_list,
                                          height=400,
                                          width=600,
                                          change_function=self.change_function)
    
    def event_find_packages(self):
        self.changed = True
        origin_path = tkFileDialog.askdirectory(parent=self.root,
                                                initialdir=root_path,
                                                title='Please select source directory')
        if origin_path:
            self.origin_path = origin_path
            packages = get_folder_tree(self.origin_path)[0]
            self.set_packages(packages)
        
    
    def event_refresh(self):
        self.changed = True
        for package in self.packages_variables.values():
            package['var'].set(1)
    
    def event_next(self):

        if not self.origin_path:
            return
        
        folders_to_copy = self.tree_view.get_checked_items()

        license = self.license_box.get(1.0, tk.END)
        
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
            
        copy = process_folders_copy(self.origin_path, self.target_path, folders_to_copy, license)

        if copy:
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
    

    def check_changes_to_continue(self):
        """ 
        Check if the project has unsaved changes.
        Return True to continue action or False to abort
        """
        if self.changed:
            save = tkMessageBox.askyesnocancel('New Project', 'This project have unsaved modifications. Do you want to save it before continue?')
        
        if save is None:
            return False
        elif save:
            self.save_project()
            tkMessageBox.showinfo('Project Saved', 'Your project was saved')
        
        return True


    def new_project(self):

        if self.check_changes_to_continue():

            if self.tree_view:
                self.tree_view.forget()
            self.tree_view = None
            self.project_name = None
            self.project_file_path = None

    def save_project(self):
        
        if not self.project_name:
            self.save_project_as()
            return
        
        self.changed = False

        project_struct = {'dist_file_version':DIST_FILE_VERSION,
                          'name':self.project_name,
                          'origin_path':self.origin_path,
                          'unchecked_items':self.tree_view.get_checked_items(mode='off')}

        open_file = open(self.project_file_path, 'w')
        pickle.dump(project_struct, open_file)
        open_file.close()
        

    def load_project(self):

        if not self.check_changes_to_continue():
            return

        open_file = tkFileDialog.askopenfilename( defaultextension=".dist", parent=self.root)

        if not open_file:
            return
        
        self.project_file_path = open_file
        open_file = open(self.project_file_path, 'r')
        project_struct = pickle.loads(open_file.read())

        if project_struct['dist_file_version'] != DIST_FILE_VERSION:
            tkMessageBox.showerror('Invalid File', 'This project file is no longer supported')
            return

        self.project_name = project_struct['name']
        self.origin_path = project_struct['origin_path']
        
        packages = get_folder_tree(self.origin_path)[0]
        self.set_packages(packages)
        self.tree_view.set_unchecked_items(items=project_struct['unchecked_items'])

        open_file.close()
        
    
    def save_project_as(self):
        open_file = tkFileDialog.asksaveasfile(mode='w', defaultextension=".dist", parent=self.root)

        if not open_file:
            return

        self.changed = False
        self.project_file_path = open_file.name
        self.project_name = self.project_file_path.split(os.sep)[-1]

        project_struct = {'dist_file_version':DIST_FILE_VERSION,
                          'name':self.project_name,
                          'origin_path':self.origin_path,
                          'unchecked_items':self.tree_view.get_checked_items(mode='off')}
        
        pickle.dump(project_struct, open_file)

        open_file.close()


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

