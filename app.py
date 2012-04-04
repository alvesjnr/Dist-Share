#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import shutil

import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox

import git

from tree import CheckboxTree
from components import *
from project import Project, DupllicatedCopyNameException
from functions import format_log_message


class App(object):
    
    def __init__(self,root):

        self.root = root
        self.app_project = None

        #Frames definitions
        self.main_frame = tk.Frame(self.root, width=600, height=600)
        self.project_frame = tk.Frame(self.main_frame)
        self.bottom_frame = tk.Frame(self.main_frame)
        self.license_frame = tk.Frame(self.bottom_frame)
        self.status_frame = tk.Frame(self.bottom_frame)

        #adding menubar
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)

        #File menu
        self.filemenu.add_command(label="Open Project", command=self.load_project)
        self.filemenu.add_command(label="Save Project", command=self.save_project)
        self.filemenu.add_command(label="Save Project As ...", command=self.save_project_as)
        self.filemenu.add_command(label="New Project", command=self.new_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.event_exit)

        #Copy menu
        self.copymenu = tk.Menu(self.menubar, tearoff=0)
        self.copymenu.add_command(label="Add new",command=self.new_copy, state=tk.DISABLED)
        self.copymenu.add_command(label="Configure",command=self.configure_copies, state=tk.DISABLED)

        #Tools menu
        self.toolsmenu = tk.Menu(self.menubar, tearoff=0)
        self.toolsmenu.add_command(label="Diff", command=None)
        self.toolsmenu.add_command(label="Tests", command=None)
                
        #packing menu
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Copy", menu=self.copymenu)
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        self.root.config(menu=self.menubar)

        #copy_manager frame
        self.copy_manager_frame = tk.Frame(self.main_frame)
        self.copy_manager_label = tk.Label(self.copy_manager_frame,text='Current copy:')
        self.copy_manager_var = tk.StringVar()
        self.copy_manager_var.set("-")
        self.copy_manager_menu = EditableOptionMenu(self.copy_manager_frame,
                                                    self.copy_manager_var, 
                                                    *('-'), 
                                                    command=self.change_to_copy)
        self.copy_manager_update_button = tk.Button(self.copy_manager_frame, text='Refresh', command=self.refresh_copy)
        self.copy_manager_update_project_button = tk.Button(self.copy_manager_frame, text='Update Project', command=self.update_project)
        self.copy_manager_push_copy_button = tk.Button(self.copy_manager_frame, text='Push Copy', command=self.push_copy)
        self.copy_manager_label.pack(side=tk.LEFT)
        self.copy_manager_menu.pack(side=tk.LEFT)
        self.copy_manager_update_button.pack(side=tk.LEFT)
        tk.Frame(self.copy_manager_frame, width=102, height=2, bd=0, relief=tk.SUNKEN).pack(fill=tk.X, padx=25, pady=5, side=tk.LEFT) #separator
        self.copy_manager_update_project_button.pack(side=tk.LEFT)
        self.copy_manager_push_copy_button.pack(side=tk.LEFT)

        #project frame contains both tree and rename list
        self.project_frame_tree = tk.Frame(self.project_frame)
        self.project_frame_list = tk.Frame(self.project_frame)
        self.listbox = ModificationList(self.project_frame_list,self)
        self.tree = CheckboxTree(self.project_frame_tree,self)
        self.project_frame_tree.pack(side=tk.LEFT)
        self.project_frame_list.pack(side=tk.LEFT)

        #License Board
        self.license_board = LicenseBoard(self.license_frame,change_callback=self.license_text_changed,update_license_event=self.update_license_event)
        self.license_board.pack(anchor='w')
        self.license_frame.pack(anchor='w',side=tk.LEFT)

        #packing frames
        self.copy_manager_frame.pack(anchor='w')
        self.project_frame.pack()
        self.bottom_frame.pack()
        self.main_frame.pack()

    def load_initial_project(self,filename):
        with open(filename) as dumped_app_project:
            self.app_project = AppProject(dumped_app_project=dumped_app_project.read())
            self.app_project.project.update_project()
            self.tree.fill(self.app_project.project.project_items)
            self.copymenu.entryconfigure('Add new',state=tk.NORMAL)
            self.copymenu.entryconfigure('Configure',state=tk.NORMAL)
            for copy in self.app_project.project.copies_manager.copies:
                self.copy_manager_menu.insert_option(0,copy.copy_name)
            self.app_project.project.copies_manager.current_copy = None

    def event_exit(self,event=None):
        if self.check_for_saving:
            self.root.quit()

    def new_project(self,event=None):
        if not self.check_for_saving():
            return
        new_project_window = tk.Toplevel(self.root)
        new_project_widget = NewProject(new_project_window,callback=self.callback_new_project)
        new_project_widget.pack()
        new_project_window.transient(self.root)

    def callback_new_project(self,project):
        self.app_project = AppProject(project)
        self.tree.fill(self.app_project.project.project_items)
        self.copymenu.entryconfigure('Add new',state=tk.NORMAL)
        self.copymenu.entryconfigure('Configure',state=tk.NORMAL)
    
    def new_copy(self,event=None,name=None,path=None):
        gc = git.config.GitConfigParser(os.path.expanduser('~/.gitconfig'))
        git_username = gc.get('user','name')
        git_useremail = gc.get('user','email')
        new_copy_window = tk.Toplevel(self.root)
        new_copy_widget = NewCopy(new_copy_window,self.callback_new_copy,git_username=git_username,git_useremail=git_useremail)
        #TODO: works fine, but this is not the correct place to do it!
        if name:
            new_copy_widget.name_entry.delete(0,tk.END)
            new_copy_widget.name_entry.insert(0,name)
        if path:
            new_copy_widget.path_entry.delete(0,tk.END)
            new_copy_widget.path_entry.insert(0,path)
        new_copy_widget.pack()
        new_copy_window.transient(self.root)

    def callback_new_copy(self,path,name,**kw):
        if not self.force_save():
            return
        git_username,git_useremail,remote_url = kw['git_username'],kw['git_useremail'],kw['remote_url']

        try:
            self.app_project.project.add_new_copy(path=path,name=name)
        except DupllicatedCopyNameException:
            tkMessageBox.showerror('Error','Already exists a copy named "%s". Please choose a different name to continue.' % name)
            self.new_copy(name=name,path=path)
            return

        if git_username and git_useremail:
            self.app_project.project.config_git_user_email(git_username,git_useremail)

        # fakes a hard copy
        current_copy = self.app_project.project.copies_manager.current_copy
        map(current_copy.avoid_file,current_copy.items)
        
        self.app_project.project.create_current_copy()

        if remote_url:
            current_copy.create_remote('origin',remote_url)

        map(current_copy.unavoid_file,current_copy.items)

        self.copy_manager_menu.insert_option(0,name)
        self.copy_manager_var.set(name)
        self.app_project.locked_copy = True
        self.app_project.project.set_current_copy(copy_name=name)
        self.tree.set_all_items()
        self.app_project.name = self.app_project.project.copies_manager.current_copy.copy_name
        self.license_board.erase()
        self.app_project.update_avoided_files()
        self.save_project()

    def load_project(self, event=None):

        if self.app_project:
            if not self.check_for_saving():
                return
            else:
                self.tree.reset_tree()
                self.app_project = None 

        filename = tkFileDialog.askopenfile(defaultextension=".dist", parent=self.root)
        if filename:
            self.app_project = AppProject(dumped_app_project=filename.read())
            self.app_project.project.update_project()
            self.tree.fill(self.app_project.project.project_items)
            self.copymenu.entryconfigure('Add new',state=tk.NORMAL)
            self.copymenu.entryconfigure('Configure',state=tk.NORMAL)
            for copy in self.app_project.project.copies_manager.copies:
                self.copy_manager_menu.insert_option(0,copy.copy_name)
    
    def save_project(self, event=None):

        if self.app_project:
            if not self.force_create_copy():
                return
            if self.app_project.path:
                with open(self.app_project.path,'w') as f:
                    f.write(self.app_project.dumps())
                self.app_project.saved = True
            else:
                self.save_project_as()
            self.app_project.update_avoided_files()

    def save_project_as(self):
        if not self.force_create_copy():
            return
        filename = tkFileDialog.asksaveasfile(mode='w', defaultextension=".dist", parent=self.root)

        if filename is None:
            return

        self.app_project.path = filename.name
        filename.write(self.app_project.dumps())
        filename.close()
        self.app_project.saved = True

    def change_callback(self):
        """ This method receives one signal from CheckboxTree informing that one change coulb have been happened
        """ 
        if self.app_project.name == '-':
            self.tree.set_all_items()
            tkMessageBox.showinfo('No current copy','You must select a copy before avoid a file')
            return

        self.app_project.saved = False
        unselected_items = self.tree.get_checked_items(mode='off')
        current_avoided = self.app_project.project.copies_manager.current_copy.avoided_files

        files_to_avoid = [item for item in unselected_items if item not in current_avoided]
        files_to_unavoid = [item for item in current_avoided if item not in unselected_items]

        for item in files_to_avoid:
            self.app_project.project.copies_manager.current_copy.avoid_file(item)
        for item in files_to_unavoid:
            self.app_project.project.copies_manager.current_copy.unavoid_file(item)

    def rename_file_callback(self):
        """ This method receives one signal from ModificationsList informing that one change happened
        """ 
        def get_modifications(old,new):
            remove = {}
            add = {}
            for i in new:
                if i in old:
                    if old[i] != new[i]:
                        remove[i] = old[i]
                        add[i] = new[i]
                else:
                    add[i] = new[i]

            for i in old:
                if i not in new:
                    remove[i] = old[i]
            
            return add,remove

        renamed_files = self.listbox.get_modification_list()
        current_change_profile = self.app_project.project.copies_manager.current_copy.change_profile

        to_add,to_remove = get_modifications(current_change_profile,renamed_files)
        for i in to_remove:
            self.app_project.project.copies_manager.current_copy.remove_change(i)
        for i in to_add:
            self.app_project.project.copies_manager.current_copy.add_change(i,to_add[i])
        self.app_project.saved = False

    def change_to_copy(self,name=''):
        """ This method binds the event of changing copy by the dropdown menu
        """ 
        
        if not self.force_create_copy():
            return
        
        if not self.force_save():
            self.copy_manager_var.set(self.app_project.project.copies_manager.current_copy.copy_name)
            return

        self.tree.reset_last_states()
        self.listbox.reset_list()
        if not name:
            name = self.copy_manager_var.get()
        if name == '-':
            self.tree.set_all_items()
            self.app_project.name = '-'
            self.license_board.erase()
        else:
            self.app_project.project.set_current_copy(copy_name=name)
            self.tree.set_all_items()
            unselected_items = self.app_project.project.copies_manager.current_copy.avoided_files
            self.tree.set_unchecked_items(unselected_items)
            self.tree.freeze_state()
            self.app_project.name = self.app_project.project.copies_manager.current_copy.copy_name

            renamed_files = self.app_project.project.copies_manager.current_copy.change_profile
            if renamed_files:
                self.listbox.fill(renamed_files)

            self.license_board.fill(self.app_project.project.copies_manager.current_copy.license)

    def update_license_event(self):
        """ Forces rewriting license in all files of the copy
        """
        if self.app_project.name != '-' and self.force_save():
            self.app_project.project.copies_manager.current_copy.license = self.license_board.get_license()
            self.save_project()
            self.app_project.project.copies_manager.current_copy.update_license()

    def license_text_changed(self,event=None):
        if self.app_project.name != '-':
            self.app_project.project.copies_manager.current_copy.license = self.license_board.get_license().strip()
            self.app_project.saved = False

    def update_project(self,event=None):

        if self.app_project.project.copies_manager.current_copy is None:
            return

        if not self.force_save():
            return

        self.app_project.project.update_project()
        self.tree.reset_tree()
        self.tree.fill(self.app_project.project.project_items)
        self.tree.set_unchecked_items(self.app_project.project.copies_manager.current_copy.avoided_files)

        if not self.force_create_copy():
            return

        self.app_project.project.update_copies()
        self.save_project()
        update_message = format_log_message(self.app_project.project.update_log)
        if update_message:
            Board.show_message(self.root,update_message)

    def push_copy(self,event=None):

        current_copy = self.app_project.project.copies_manager.current_copy

        if current_copy is None or not current_copy.remote_url:
            return

        copy_name = current_copy.copy_name
        branchs = current_copy.repo.git.branch()
        try:
            diff = current_copy.repo.git.diff('origin/master','master','--stat')
        except git.GitCommandError:
            diff = "First commit? Remote looks empty!"
        status = current_copy.repo.git.status()
        
        message = \
"""
Push copy: %s 

Remote repository at: %s

Brach:
%s

Status:
%s

Diff:
%s
""" % (copy_name,current_copy.remote_url,branchs,status,diff)

        PushBoard.show_board(self.root,message=message,callback=self.push_copy_callback,copy_name=copy_name)

    def push_copy_callback(self,copy_name):
        copy = self.app_project.project.get_copy_by_name(name=copy_name)

        if copy is None:
            tkMessageBox.showerror('Copy not found',"Copy '%s' not found!" % copy_name)
            return

        try:
            copy.repo.git.push('origin','master')
        except git.GitCommandError:
            tkMessageBox.showerror('Remote not found','It were not possible to push to remote repository. Remote not found!')
            sys.stderr.write("Warning: Remote not found\n")
            return

        tkMessageBox.showinfo('Copy pushed',"You have successfully pushed the copy '%s' to the remote repository." % copy_name)

    def refresh_copy(self,event=None):
        self.app_project.saved = True
        current_copy = self.app_project.project.copies_manager.current_copy
        copy_name = current_copy.copy_name

        if copy_name != self.copy_manager_var.get():
            raise Exception("Panic!")
            self.root.quit()

        avoided_files = self.app_project.avoided_files[copy_name]
        current_copy.avoided_files = avoided_files[:]
        self.tree.set_all_items()
        self.tree.set_unchecked_items(avoided_files)

        license = self.app_project.license[copy_name]
        self.license_board.erase()
        self.license_board.fill(license)
        current_copy.license = license

        change_profile = self.app_project.renamed_files[copy_name]
        current_copy.change_profile = change_profile.copy()
        self.listbox.reset_list()
        self.listbox.fill(change_profile)

    def force_create_copy(self):
        if self.app_project.locked_copy:
            if tkMessageBox.askyesno('Create current copy','This action will fisically creates the current copy. Do you want to proceed anyway?'):
                self.app_project.project.create_current_copy()
                self.app_project.locked_copy = False
                return True
            else:
                return False
        else:
            return True

    def check_for_saving(self):
        if self.app_project is None:
            return True
        if not self.app_project.saved:
            if tkMessageBox.askyesno('Save project?','This project has unsaved changes. Do you want to proceed and lost those changes?'):
                return True
            else:
                return False
        else:
            return True

    def force_save(self):
        if not self.app_project.saved:
            if tkMessageBox.askyesno('Save project?','This project has unsaved changes. You must save then before continue. Do you want to save and continue?'):
                self.save_project()
                return True
            else:
                return False
        else:
            return True

    def configure_copies(self,event=None):
        CopiesConfig.copies_config_window(self.root,self.app_project,callback_delete_copy=self.callback_delete_copy,callback_save=self.save_project)

    def callback_delete_copy(self,copy_name):

        if not self.force_save():
            return False

        if self.app_project.project.copies_manager.current_copy:
            if self.app_project.project.copies_manager.current_copy.copy_name == copy_name:
                self.change_to_copy('-')
        for copy in self.app_project.project.copies_manager.copies:
            if copy.copy_name == copy_name:
                shutil.rmtree(copy.copy_location)
                self.app_project.project.copies_manager.copies.remove(copy)
                self.copy_manager_menu.delete_option(copy_name)
        self.save_project()
        return True


class AppProject(object):
    """ AppProject is an object that represents an Project object inside the GUI
        This separations exists to keep Project and GUI totally unconnected
    """

    def __init__(self,project=None,dumped_app_project=None):
        if project:
            self.project = project
            self.saved = False
            self.path = ''
            self.name = '-'
            self.locked_copy = False    # A locked copy is a copy that have not been fisically copied yet
        elif dumped_app_project:
            obj = pickle.loads(dumped_app_project)
            self.path = obj['path']
            self.project = Project(dumped_project=obj['project'])
            self.saved = True
            self.name = '-'
            self.locked_copy = False
        else:
            raise BaseException("You must provide either a Project or a dumped AppProject object")
        self.update_avoided_files()

    def dumps(self):
        obj = {'project':self.project.dumps(),
               'path':self.path
               }
        return pickle.dumps(obj)

    def update_avoided_files(self):
        self.avoided_files = {}
        self.license = {}
        self.renamed_files = {}
        for copy in self.project.copies_manager.copies:
            self.avoided_files[copy.copy_name] = copy.avoided_files[:]
            self.renamed_files[copy.copy_name] = copy.change_profile.copy()
            self.license[copy.copy_name] = copy.license


def main(project=None):
    WINDOW_TITLE = 'Dist Share'
    root = Tix.Tk()
    root.wm_title('Untitled Project - '+WINDOW_TITLE)
    app = App(root)
    if project:
        app.load_initial_project(project)
    root.mainloop()


if __name__ == '__main__':
    project = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        project = sys.argv[1]

    main(project)
    