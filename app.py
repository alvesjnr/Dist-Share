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
        self.filemenu.add_command(label="Open Project", command=None)
        self.filemenu.add_command(label="Save Project", command=None)
        self.filemenu.add_command(label="Save Project As ...", command=None)
        self.filemenu.add_command(label="New Project", command=self.new_project)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)

        #Copy menu
        self.copymenu = tk.Menu(self.menubar, tearoff=0)
        self.copymenu.add_command(label="Add new",command=self.new_copy, state=tk.DISABLED)

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
                                                    command=self.change_copy)
        self.copy_manager_update_button = tk.Button(self.copy_manager_frame, text='Update Copy')
        #self.copy_manager_update_project_button = tk.Button(self.copy_manager_frame, text='Update Project')
        self.copy_manager_label.pack(side=tk.LEFT)
        self.copy_manager_menu.pack(side=tk.LEFT)
        self.copy_manager_update_button.pack(side=tk.LEFT)
        tk.Frame(self.copy_manager_frame, width=102, height=2, bd=0, relief=tk.SUNKEN).pack(fill=tk.X, padx=25, pady=5, side=tk.LEFT) #separator
        #self.copy_manager_update_project_button.pack(side=tk.LEFT)

        #project frame contains both tree and rename list
        self.project_frame_tree = tk.Frame(self.project_frame)
        self.project_frame_list = tk.Frame(self.project_frame)
        self.listbox = ModificationList(self.project_frame_list,self)
        self.tree = CheckboxTree(self.project_frame_tree,self)
        self.project_frame_tree.pack(side=tk.LEFT)
        self.project_frame_list.pack(side=tk.LEFT)

        #License Board
        self.license_board = LicenseBoard(self.license_frame)
        self.license_board.pack(anchor='w')

        #packing frames
        self.copy_manager_frame.pack(anchor='w')
        self.project_frame.pack()
        self.license_frame.pack(anchor='w')
        self.bottom_frame.pack()
        self.main_frame.pack()

    def new_project(self,event=None):
        new_project_window = tk.Toplevel(self.root)
        new_project_widget = NewProject(new_project_window,callback=self.callback_new_project)
        new_project_widget.pack()
        new_project_window.transient(self.root)

    def callback_new_project(self,project):
        self.app_project = AppProject(project)
        self.tree.fill(self.app_project.project.project_items)
        self.copymenu.entryconfigure('Add new',state=tk.NORMAL)
    
    def new_copy(self,event=None):
        new_copy_window = tk.Toplevel(self.root)
        new_copy_widget = NewCopy(new_copy_window)
        new_copy_widget.pack()
        new_copy_window.transient(self.root)

    def callback_new_copy(self):
        pass

    def load_project(self, event=None):
        pass
    
    def save_project(self, event=None):
        pass

    def change_callback(self):
        """ This method receives one signal from CheckboxTree informing that one change coulb have been happened
        """ 
        if self.app_project.project.copies_manager.current_copy:
            #change things of the curent copy
            self.app_project.saved = False
        else:
            self.tree.set_all_items()
            tkMessageBox.showinfo('No current copy','You must select a copy before avoid a file')

    def change_copy(self,event=None):
        """ This method binds the event of changing copy by the dropdown menu
        """ 
        pass


class AppProject(object):
    """ AppProject is an object that represents an Project object inside the GUI
        This separations exists to keep Project and GUI totally unconnected
    """

    def __init__(self,project):
        self.project = project
        self.saved = False


class NewProject(tk.Frame):

    def __init__(self,Master=None,callback=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        self.root = Master
        self.callback = callback
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
        self.okay.bind('<ButtonRelease-1>',self.event_okay)
        self.cancel = tk.Button(self.buttons_frame,text='Cancel')
        self.cancel.pack(side='left')
        self.cancel.bind('<ButtonRelease-1>',self.event_cancel)
        self.warning_frame = tk.Frame(self)
        self.warning_frame.pack(side='top')
        self.warning_text = tk.Text(self.warning_frame)
        self.warning_text.pack(side='top')

        #REMOVE remove it after tests
        self.url_entry.insert(0,'svn://alvesjnr@localhost/tmp/svnrepo')
        self.pth_entry.insert(0,'/tmp/nuca')

    def event_cancel(self,Event=None):
        self.root.destroy()

    def check_url_event(self,Event=None):
        url = self.url_entry.get()
        if self._svn_url_okay(url):
            tkMessageBox.showinfo('','This is a valid svn repository')
        else:
            tkMessageBox.showwarning('Warn','This is not a valid SVN repository, or you dont have permission to check it out.')

    def load_path_event(self,Event=None):
        repository_path = tkFileDialog.askdirectory()
        if self._project_path_okay(repository_path):
            self.pth_entry.delete(0)
            self.pth_entry.insert(0,repository_path)

    def event_okay(self,Event=None):
        project_path = self.pth_entry.get()
        project_url = self.url_entry.get()

        if self._svn_url_okay(project_url) and self._project_path_okay(project_path):
            try:
                project = Project(path=project_path,url=project_url)
            except:
                tkMessageBox.showerror('Error','It was not possible to create a new project. \nPlease check svn URL and folder path.')
            else:
                self.callback(project)
                self.root.destroy()
        else:
            tkMessageBox.showerror('Error','It was not possible to create a new project. \nPlease check svn URL and folder path.')


    def _svn_url_okay(self,url):
        #TODO: check if url is valid and if url is a valid svn.
        #      also check for permissions to checkout this svn rrepository
        if url:
            return True

    def _project_path_okay(self,path):
        #TODO chack is path is valid, and if the user has permission to write on it
        if path:
            return True


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


class LicenseBoard(tk.Frame):

    def __init__(self,Master=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        tk.Label(self,text='License:').pack(anchor='w')
        self.__Frame2 = tk.Frame(self)
        self.__Frame2.pack(side='top',anchor='w')
        self.__Text1 = tk.Text(self.__Frame2,width=100)
        self.__Text1.pack(side='top',anchor='w')
        self.__Frame3 = tk.Frame(self)
        self.__Frame3.pack(side='top',anchor='w')
        self.label_var = tk.StringVar()
        self.label_var.set('')
        self.__Label1 = tk.Label(self.__Frame3,anchor='w',textvariable=self.label_var)
        self.__Label1.pack(side='left',anchor='w')
        self.__Button1 = tk.Button(self.__Frame3,anchor='w',justify='left'
            ,text='Load', command=self.load_license_event)
        self.__Button1.pack(side='left',anchor='w')

    def load_license_event(self,event=None):
        fileobj = tkFileDialog.askopenfile()

        if fileobj:
            self.__Text1.delete(1.0,tk.END)
            self.__Text1.insert(tk.END,fileobj.read())
            self.label_var.set(fileobj.name)
            

def main():
    WINDOW_TITLE = 'Dist Share'
    root = Tix.Tk()
    root.wm_title('Untitled Project - '+WINDOW_TITLE)
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
