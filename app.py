#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox

from tree import CheckboxTree
from components import ModificationList, EditableOptionMenu
from project import Project


class App(object):
    
    def __init__(self,root):

        self.root = root

        #Frames definitions
        self.main_frame = tk.Frame(self.root, width=600, height=600)
        self.project_frame = tk.Frame(self.main_frame)
        self.license_frame = tk.Frame(self.main_frame)

        #adding menubar
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)

        #File menu
        self.filemenu.add_command(label="Open Project", command=None)
        self.filemenu.add_command(label="Save Project", command=None)
        self.filemenu.add_command(label="Save Project As ...", command=None)
        self.filemenu.add_command(label="New Project", command=self.new_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)

        #Copy menu
        self.copymenu = tk.Menu(self.menubar, tearoff=0)
        self.copymenu.add_command(label="Add new",command=self.new_copy)

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
                                                    command=None)
        self.copy_manager_update_button = tk.Button(self.copy_manager_frame, text='Update Copy')
        self.copy_manager_update_project_button = tk.Button(self.copy_manager_frame, text='Update Project')
        self.copy_manager_label.pack(side=tk.LEFT)
        self.copy_manager_menu.pack(side=tk.LEFT)
        self.copy_manager_update_button.pack(side=tk.LEFT)
        tk.Frame(self.copy_manager_frame, width=102, height=2, bd=0, relief=tk.SUNKEN).pack(fill=tk.X, padx=25, pady=5, side=tk.LEFT) #separator
        self.copy_manager_update_project_button.pack(side=tk.LEFT)

        #project frame contains both tree and rename list
        self.project_frame_tree = tk.Frame(self.project_frame)
        self.project_frame_list = tk.Frame(self.project_frame)
        self.listbox = ModificationList(self.project_frame_list,self)
        self.tree = CheckboxTree(self.project_frame_tree,self)
        self.project_frame_tree.pack(side=tk.LEFT)
        self.project_frame_list.pack(side=tk.LEFT)

        #packing frames
        self.copy_manager_frame.pack(anchor='w')
        self.project_frame.pack()
        self.license_frame.pack()
        self.main_frame.pack()

    def new_project(self,event=None):
        new_project_window = tk.Toplevel(self.root)
        new_project_widget = NewProject(new_project_window)
        new_project_widget.pack()
        new_project_window.transient(self.root)
    
    def new_copy(self,event=None):
        new_copy_window = tk.Toplevel(self.root)
        new_copy_widget = NewProject(new_copy_window)
        new_copy_widget.pack()
        new_copy_window.transient(self.root)


class NewProject(tk.Frame):

    def __init__(self,Master=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side='top')
        self.__Label1 = tk.Label(self.top_frame,text='URL:')
        self.__Label1.pack(side='left')
        self.url_entry = tk.Entry(self.top_frame)
        self.url_entry.pack(side='left')
        self.check_url = tk.Button(self.top_frame,text='Check')
        self.check_url.pack(side='left')
        self.check_url.bind('<ButtonRelease-1>',self.check_url_event)
        self.middle_frame = tk.Frame(self)
        self.middle_frame.pack(side='top')
        self.__Label2 = tk.Label(self.middle_frame,text='Copy Location')
        self.__Label2.pack(side='left')
        self.pth_entry = tk.Entry(self.middle_frame)
        self.pth_entry.pack(side='left')
        self.load_path = tk.Button(self.middle_frame,text='Open')
        self.load_path.pack(side='left')
        self.load_path.bind('<ButtonRelease-1>',self.load_path_event)
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(side='top')
        self.okay = tk.Button(self.buttons_frame,text='Create Project')
        self.okay.pack(side='left')
        self.okay.bind('<ButtonRelease-1>',self.okay)
        self.cancel = tk.Button(self.buttons_frame,text='Cancel')
        self.cancel.pack(side='left')
        self.cancel.bind('<ButtonRelease-1>',self.cancel)
        self.warning_frame = tk.Frame(self)
        self.warning_frame.pack(side='top')
        self.warning_text = tk.Text(self.warning_frame)
        self.warning_text.pack(side='top')

    def cancel(self,Event=None):
        pass

    def check_url_event(self,Event=None):
        pass

    def load_path_event(self,Event=None):
        pass

    def okay(self,Event=None):
        pass


class NewCopy(tk.Frame):

    def __init__(self,Master=None,**kw):
        apply(Frame.__init__,(self,Master),kw)
        self.__Frame3 = tk.Frame(self)
        self.__Frame3.pack(side='top')
        self.__Label2 = tk.Label(self.__Frame3,text='Copy Name:')
        self.__Label2.pack(side='left')
        self.name_entry = tk.Entry(self.__Frame3)
        self.name_entry.pack(side='left')
        self.__Frame2 = tk.Frame(self)
        self.__Frame2.pack(side='top')
        self.__Label1 = tk.Label(self.__Frame2,text='Copy Location:')
        self.__Label1.pack(side='left')
        self.path_entry = tk.Entry(self.__Frame2)
        self.path_entry.pack(side='left')
        self.load_path_button = tk.Button(self.__Frame2,text='Load')
        self.load_path_button.pack(side='left')
        self.load_path_button.bind('<ButtonRelease-1>',self.event_load_path)
        self.__Frame4 = tk.Frame(self)
        self.__Frame4.pack(side='top')
        self.okay = Button(self.__Frame4,text='Create Copy')
        self.okay.pack(side='left')
        self.okay.bind('<ButtonRelease-1>',self.okay)
        self.cancel = tk.Button(self.__Frame4,text='Cancel')
        self.cancel.pack(side='left')
        self.cancel.bind('<ButtonRelease-1>',self.cancel)
        self.__Frame1 = tk.Frame(self)
        self.__Frame1.pack(side='top')
        self.warning_text = tk.Text(self.__Frame1)
        self.warning_text.pack(side='top')

    def cancel(self,Event=None):
        pass

    def event_load_path(self,Event=None):
        pass

    def okay(self,Event=None):
        pass


def main():
    WINDOW_TITLE = 'Dist Share'
    root = Tix.Tk()
    root.wm_title('Untitled Project - '+WINDOW_TITLE)
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
