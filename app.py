#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox
import pickle

from tree import CheckboxTree
from components import ModificationList, EditableOptionMenu, Board
from project import Project
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
        self.license_board = LicenseBoard(self.license_frame,change_callback=self.update_license,update_license_event=self.update_license_event)
        self.license_board.pack(anchor='w')
        self.license_frame.pack(anchor='w',side=tk.LEFT)

        #status frame
        self.status_board = StatusBoard(Master=self.status_frame,update_callback=self.update_project, width=602, height=2, bd=0, relief=tk.SUNKEN)
        self.status_board.pack(side=tk.LEFT, fill=tk.X)
        self.status_frame.pack(side=tk.LEFT)

        #packing frames
        self.copy_manager_frame.pack(anchor='w')
        self.project_frame.pack()
        self.bottom_frame.pack()
        self.main_frame.pack()

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
    
    def new_copy(self,event=None):
        new_copy_window = tk.Toplevel(self.root)
        new_copy_widget = NewCopy(new_copy_window,self.callback_new_copy)
        new_copy_widget.pack()
        new_copy_window.transient(self.root)

    def callback_new_copy(self,path,name):
        self.app_project.project.add_new_copy(path=path,name=name)
        self.copy_manager_menu.insert_option(0,name)
        self.copy_manager_var.set(name)
        self.app_project.locked_copy = True
        self.app_project.project.set_current_copy(copy_name=name)
        self.tree.set_all_items()
        self.app_project.name = self.app_project.project.copies_manager.current_copy.copy_name
        self.license_board.fill('')
        self.app_project.update_avoided_files()

    def load_project(self, event=None):

        if self.app_project and not self.check_for_saving():
            return

        filename = tkFileDialog.askopenfile(defaultextension=".dist", parent=self.root)
        if filename:
            self.app_project = AppProject(dumped_app_project=filename.read())
            self.app_project.project.update_project()
            self.tree.fill(self.app_project.project.project_items)
            self.copymenu.entryconfigure('Add new',state=tk.NORMAL)
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

        #FIXME: refresh is not working!
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
            self.app_project.project.copies_manager.current_copy.remove_change(i,to_remove[i])
        for i in to_add:
            self.app_project.project.copies_manager.current_copy.add_change(i,to_add[i])
        self.app_project.saved = False

    def change_to_copy(self,name=''):
        """ This method binds the event of changing copy by the dropdown menu
        """ 
        if not self.force_create_copy():
            return

        self.listbox.reset_list()
        if not name:
            name = self.copy_manager_var.get()
        if name == '-':
            self.tree.set_all_items()
            self.app_project.name = '-'
            self.license_board.fill('')
        else:
            self.app_project.project.set_current_copy(copy_name=name)
            self.tree.set_all_items()
            unselected_items = self.app_project.project.copies_manager.current_copy.avoided_files
            self.tree.set_unchecked_items(unselected_items)
            self.app_project.name = self.app_project.project.copies_manager.current_copy.copy_name

            renamed_files = self.app_project.project.copies_manager.current_copy.change_profile
            if renamed_files:
                self.listbox.fill(renamed_files)

            self.license_board.fill(self.app_project.project.copies_manager.current_copy.license)

    def update_license(self,event=None):
        if self.force_save():
            if self.app_project.name != '-':
                self.app_project.project.copies_manager.current_copy.license = self.license_board.get_license()

    def update_project(self,event=None):
        if not self.force_save():
            return
        self.app_project.project.update_project()
        self.tree.reset_tree()
        self.tree.fill(self.app_project.project.project_items)
        self.tree.set_unchecked_items(self.app_project.project.copies_manager.current_copy.avoided_files)
        if not self.force_create_copy():
            return
        self.app_project.project.update_copies()
        update_message = format_log_message(self.app_project.project.update_log)
        if update_message:
            Board.show_message(self.root,update_message)

    def refresh_copy(self,event=None):
        avoided_files = self.app_project.avoided_files[self.copy_manager_var.get()]
        self.app_project.project.copies_manager.current_copy.avoided_files = avoided_files
        self.tree.set_all_items()
        self.tree.set_unchecked_items(avoided_files)

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

    def update_license_event(self):
        """ Forces rewriting license in all files of the copy
        """
        if self.force_save():
            self.app_project.project.copies_manager.current_copy.update_license()

    def check_for_saving(self):
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
        self.avoided_files = {}
        self.update_avoided_files()

    def dumps(self):
        obj = {'project':self.project.dumps(),
               'path':self.path
               }
        return pickle.dumps(obj)

    def update_avoided_files(self):
        self.avoided_files = {}
        for copy in self.project.copies_manager.copies:
            self.avoided_files[copy.copy_name] = copy.avoided_files


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

    def __init__(self,Master=None, callback=None, **kw):
        apply(tk.Frame.__init__,(self,Master),kw)
        self.callback = callback
        self.root = Master
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
        self.okay = tk.Button(self.__Frame4,text='Create Copy')
        self.okay.pack(side='left')
        self.okay.bind('<ButtonRelease-1>',self.event_okay)
        self.cancel = tk.Button(self.__Frame4,text='Cancel')
        self.cancel.pack(side='left')
        self.cancel.bind('<ButtonRelease-1>',self.event_cancel)
        self.__Frame1 = tk.Frame(self)
        self.__Frame1.pack(side='top')
        self.warning_text = tk.Text(self.__Frame1)
        self.warning_text.pack(side='top')

        #REMOVE remove it after tests
        self.name_entry.insert(0,'copy')
        self.path_entry.insert(0,'/tmp/copy')

    def event_cancel(self,Event=None):
        pass

    def event_load_path(self,Event=None):
        pass

    def event_okay(self,Event=None):
        name = self.name_entry.get()
        path = self.path_entry.get()
        if not self._check_copy_path(path):
            tkMessageBox.showwarning('','Make sure that you have selected a valid path')
        elif not self._check_copy_name(name):
            tkMessageBox.showwarning('','Invalid copy name')
        else:
            self.callback(path,name)
            self.root.destroy()
    
    def _check_copy_name(self,name):
        #TODO
        if name:
            return True

    def _check_copy_path(self,path):
        #TODO
        if path:
            return True 


class LicenseBoard(tk.Frame):

    def __init__(self,Master=None, change_callback=None,update_license_event=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        self.change_callback = change_callback
        tk.Label(self,text='License:').pack(anchor='w')
        self.__Frame2 = tk.Frame(self)
        self.__Frame2.pack(side='top',anchor='w')
        self.__Text1 = tk.Text(self.__Frame2,width=100)
        self.license_scroll = tk.Scrollbar(self.__Frame2)
        self.__Text1 = tk.Text(self.__Frame2,
                                   height=10)
        self.__Text1.config(yscrollcommand=self.license_scroll.set)
        self.license_scroll.config(command=self.__Text1.yview)
        self.license_scroll.pack(side=tk.RIGHT,
                                  fill=tk.Y)
        self.__Text1.bind('<KeyRelease>',self.change_callback)
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
        self.__Button2 = tk.Button(self.__Frame3,anchor='w',justify='left'
            ,text='Update License', command=update_license_event)
        self.__Button2.pack(side='left',anchor='w')

    def load_license_event(self,event=None):
        fileobj = tkFileDialog.askopenfile()

        if fileobj:
            self.__Text1.delete(1.0,tk.END)
            self.__Text1.insert(tk.END,fileobj.read())
            self.label_var.set(fileobj.name)
            self.change_callback()

    def fill(self,text):
        if isinstance(text,basestring):
            self.__Text1.delete(1.0,tk.END)
            self.__Text1.insert(tk.END,text)
            self.label_var.set('')
            self.change_callback()

    def get_license(self):
        return self.__Text1.get(1.0,tk.END)


class StatusBoard(tk.Frame):

    def __init__(self,Master=None,update_callback=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        self.__Frame2 = tk.Frame(self)
        self.__Frame2.pack(side='top')
        self.__Label1 = tk.Label(self.__Frame2,anchor='w',text='URL:')
        self.__Label1.pack(side='left')
        self.svn_var = tk.StringVar()
        self.svn_label = tk.Label(self.__Frame2,anchor='w'
            ,textvariable=self.svn_var)
        self.svn_label.pack(side='left')
        self.__Frame1 = tk.Frame(self)
        self.__Frame1.pack(side='top')
        self.__Label3 = tk.Label(self.__Frame1,anchor='w',text='Local Copy:')
        self.__Label3.pack(side='left')
        self.path_var = tk.StringVar()
        self.path_label = tk.Label(self.__Frame1,anchor='w'
            ,textvariable=self.path_var)
        self.path_label.pack(side='left')
        self.__Frame4 = tk.Frame(self)
        self.__Frame4.pack(side='top')
        self.__Label5 = tk.Label(self.__Frame4,anchor='w',text='Current Copy:')
        self.__Label5.pack(side='left')
        self.copy_path_var = tk.StringVar()
        self.copy_path = tk.Label(self.__Frame4,anchor='w'
            ,textvariable=self.copy_path_var)
        self.copy_path.pack(side='left')
        self.__Frame3 = tk.Frame(self)
        self.__Frame3.pack(side='top')
        self.__Button1 = tk.Button(self.__Frame3,text='Update Project',command=update_callback)
        self.__Button1.pack(side='bottom')            


def main():
    WINDOW_TITLE = 'Dist Share'
    root = Tix.Tk()
    root.wm_title('Untitled Project - '+WINDOW_TITLE)
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
