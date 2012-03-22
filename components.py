#!/usr/bin/python
import Tkinter as tk
import Tix
import ttk
from functions import *
import tkFileDialog, tkMessageBox
from project import Project, NewProjectException
from tree import CheckboxTree
import pysvn

import os

SEPARATOR = os.sep


class Board(object):

    def __init__(self, root):
        
        self.root = root
        
        self.text_frame = tk.Frame(self.root )
        self.text_board = tk.Text(self.text_frame, height=40, width=100 )
        self.text_scroll = tk.Scrollbar(self.text_frame)
        
        self.text_board.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_board.yview)
        self.text_board.pack(side=tk.LEFT)
        self.text_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        self.buttons_frame = tk.Frame(self.root)

        self.button_quit = tk.Button(self.buttons_frame,
                                     text="Quit",
                                     command=self.event_quit,
                                     width=8)
        
        self.button_quit.pack(side=tk.LEFT)

        
        self.text_frame.pack()
        self.buttons_frame.pack()
    
    def fill_board(self, text):
        self.text_board.insert(1.0, text)
    
    def event_quit(self):
        self.root.destroy()

    @classmethod
    def show_message(cls,root,message):
        window = tk.Toplevel(root)
        widget = cls(window)
        widget.fill_board(message)
        window.transient(root)


class SaveQuitBoard(Board):
    def __init__(self,root):

        super(SaveQuitBoard,self).__init__(root)

        self.log_saved = False

        self.button_save = tk.Button(self.buttons_frame,
                                     text="Save",
                                     command=self.event_save,
                                     width=8)
        self.button_save.pack(side=tk.LEFT)

    def event_save(self):   
        fout = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt", parent=self.root)

        if fout:
            log = unicode(self.text_board.get(0.0,tk.END))
            fout.write(log)
            fout.close()
            self.log_saved = True 

    def event_quit(self):
        if not self.log_saved:
            if not tkMessageBox.askokcancel('File not yet saved', 'File is not yet saved.\nDo you want to quit anyway?', parent=self.root):
                return
        self.root.destroy()


class ModificationList(object):

    def __init__(self, root, parent):
        
        self.root = root
        self.parent = parent
        self.modification_list = []

        self.frame = tk.Frame(self.root)
        self.listbox = tk.Listbox(self.frame, width=50, height=30)
        self.listbox.bind('<Double-Button-1>', self.edit_entry)
        self.listbox.pack()

        self.buttons_frame = tk.Frame(self.frame)
        tk.Button(self.buttons_frame, text='Add', command=self.add_entry_window).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text='Edit', command=self.edit_entry).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text='Remove', command=self.remove_entry).pack(side=tk.LEFT)

        self.buttons_frame.pack()
        self.frame.pack(side=tk.LEFT,fill=tk.BOTH)

    def edit_entry(self, event=None):
        try:
            modification_entry = self.listbox.selection_get()
        except tk.TclError:
            # none selected item
            return
        
        original_name, new_name = self._split_text(modification_entry)
        modify_window = tk.Toplevel(self.root)
        modify_widget = EditModification(modify_window,modification_entry,self.edit_entry_callback)

    def edit_entry_callback(self,change_descriptor,new_name):
        if change_descriptor == self.listbox.get('active'):
            self.listbox.delete('active')
            original_name,_ = self._split_text(change_descriptor)
            self.listbox.insert(0,"%s -> %s" % (original_name,new_name))
            self.parent.rename_file_callback()

    def add_entry_window(self):
        """ Calls the AddModification window passing the function _add_item
            to insert a new entry
        """
        add_entry_window = tk.Toplevel(self.root)
        add_entry_widget = AddModification(path=self.parent.app_project.project.path,callback=self.add_item,root=add_entry_window)
        add_entry_window.transient(self.root)

    def remove_entry(self):
        if len(self.listbox.curselection()):
            index = int(self.listbox.curselection()[0])
            self.listbox.delete(index, index)
            self.parent.rename_file_callback()

    def fill(self,items):
        for item in items:
            self._add_item(item,items[item])

    def add_item(self,original_name,new_name):
        change_profile = self.parent.app_project.project.copies_manager.current_copy.change_profile
        if original_name in change_profile:
            if tkMessageBox.askyesno('Duplicated file','Already exists one change for this file. Do you want to overwrite the last change?'):
                old_name = "%s -> %s" % (original_name,change_profile[original_name])
                index = 0
                while self.listbox.get(index) != old_name:
                    index += 1
                    if not self.listbox.get(index):
                        sys.stderr.write('Warning: listbox entr %s not found\n' % old_name)
                        return
                self.listbox.delete(index)
        self._add_item(original_name,new_name)

    def _add_item(self,original_name,new_name):
        self.listbox.insert(0,"%s -> %s" % (original_name,new_name))
        self.parent.rename_file_callback()

    def get_modification_list(self):

        return dict(self._split_text(item) for item in self.listbox.get(0,tk.END))

    def _split_text(self,item):
            return item.split(' -> ')

    def reset_list(self):
        self.listbox.delete(0, tk.END)


class EditModification(object):

    def __init__(self,root,change_descriptor,callback):
        self.root = root
        self.change_descriptor = change_descriptor
        
        self.full_file_name, self.modified_name = self._split_text(change_descriptor)

        self.original_path, self.original_name = split_path(self.full_file_name)

        self.full_file_name_label = tk.Label(self.root,text=self.full_file_name)
        self.new_name = tk.Entry(self.root)
        self.new_name.bind('<KeyRelease>',self.change_name)
        self.new_name.insert(0,self.modified_name)
        self.newpath_variable = tk.StringVar()
        self.newpath_variable.set(os.path.join(self.original_path,self.modified_name))
        self.new_file_name_label = tk.Label(self.root,textvariable=self.newpath_variable)

        self.okay_cancel_frame = tk.Frame(self.root)
        tk.Button(self.okay_cancel_frame, text='OK', command=self.okay).pack(side=tk.LEFT)
        tk.Button(self.okay_cancel_frame, text='Cancel', command=self.close).pack(side=tk.LEFT)

        self.full_file_name_label.pack()
        self.new_name.pack()
        self.new_file_name_label.pack()
        self.okay_cancel_frame.pack()

        self.callback = callback
    
    def _split_text(self,item):
            return item.split(' -> ')

    def change_name(self, event):
        self.modified_name = self.new_name.get()
        new_file_name = os.path.join(self.original_path,self.modified_name)
        self.newpath_variable.set(new_file_name)

    def close(self):
        self.root.destroy()

    def okay(self):
        self.callback(self.change_descriptor,self.modified_name)
        self.close()


class AddModification(object):

    def __init__(self,root,path,callback):

        self.root = root
        self.callback = callback
        self.path = path

        self.frame = tk.Frame(self.root)
        self.frame_path = tk.Frame(self.frame)
        self.frame_newname = tk.Frame(self.frame)
        self.frame_label = tk.Frame(self.frame)
        self.frame_butons = tk.Frame(self.frame)

        self.label_path = tk.Label(self.frame_path, text="File:")
        self.text_path = tk.Entry(self.frame_path, width=50)
        self.button_load_file = tk.Button(self.frame_path, text="Load",command=self.load)
        self.label_path.pack(side=tk.LEFT)
        self.text_path.pack(side=tk.LEFT)
        self.button_load_file.pack(side=tk.LEFT)

        self.label_newname = tk.Label(self.frame_newname, text="New Name:")
        self.text_newname = tk.Entry(self.frame_newname, width=20)
        self.text_newname.bind('<KeyRelease>',self.change_name)
        self.label_newname.pack(side=tk.LEFT)
        self.text_newname.pack(side=tk.LEFT)

        self.newpath_variable = tk.StringVar()
        self.newpath_variable.set('')
        self.new_file_name_label = tk.Label(self.frame_label,textvariable=self.newpath_variable)
        self.new_file_name_label.pack()

        self.button_okay = tk.Button(self.frame_butons, text='Okay', command=self.okay)
        self.button_cancel = tk.Button(self.frame_butons, text='Cancel', command=self.cancel)
        self.button_okay.pack(side=tk.LEFT)
        self.button_cancel.pack(side=tk.LEFT)

        self.frame_path.pack()
        self.frame_newname.pack(anchor='w')
        self.frame_label.pack()
        self.frame_butons.pack()
        self.frame.pack()

    def load(self):
        filepath = tkFileDialog.askopenfilename(initialdir=self.path)

        if filepath:
            path,name = split_path(filepath)
            self.text_path.insert(0,filepath)
            self.text_newname.insert(0,name)
            self.newpath_variable.set(filepath)
            
            self.original_name = filepath
            self.path = path
            self.name = name

    def change_name(self,blah):
        self.name = self.text_newname.get()
        new_file_name = os.path.join(self.path,self.name)
        self.newpath_variable.set(new_file_name)

    def cancel(self):
        self.root.destroy()

    def okay(self):
        if hasattr(self,'original_name'):
            self.callback(self.original_name,self.name)
        self.cancel()


class EditableOptionMenu(tk.OptionMenu):
    """OptionMenu which allows editing of menu items
    """
    def __init__(self, master, variable, value, *values, **kwargs):
        """copy-paste-modified from Tkinter.OptionMenu, works the same way"""
        kw = {"borderwidth": 2, "textvariable": variable,
              "indicatoron": 1, "relief": tk.RAISED, "anchor": "c",
              "highlightthickness": 2}
        tk.Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = tk.Menu(self, name="menu", tearoff=0)
        self.menuname = menu._w
        # 'command' is the only supported keyword
        callback = kwargs.get('command')
        if kwargs.has_key('command'):
            del kwargs['command']
        if kwargs:
            raise TclError, 'unknown option -'+kwargs.keys()[0]
        menu.add_command(label=value,
                 command=tk._setit(variable, value, callback))
        for v in values:
            menu.add_command(label=v,
                     command=tk._setit(variable, v, callback))
        self["menu"] = menu
        
        self.menu=menu
        self.variable=variable
        self.callback=callback
        
    def insert_option(self, index, text):
        """Insert an option to the menu.
        Handling of index is the same as in Tkinter.Menu.insert_command()
        """
        self.menu.insert_command(index, label=text,
            command=tk._setit(self.variable, text, self.callback))

    def delete_option(self, index1, index2=None):
        """Delete options the same way as Tkinter.Menu.delete()"""
        self.menu.delete(index1, index2)

    def set_current_option(self,option):
        pass


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
        self.callback_get_login = None

        # #REMOVE remove it after tests
        # self.url_entry.insert(0,'')
        # self.pth_entry.insert(0,'/home/antonio/copies_of_project/original')

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

    def create_callback_get_login(self,param):
        def f(*x,**y):
            return True, param[0], param[1], True

        self.callback_get_login = f

    def event_okay(self,Event=None):
        project_path = self.pth_entry.get()
        project_url = self.url_entry.get()

        if self._svn_url_okay(project_url) and self._project_path_okay(project_path):
            try:
                project = Project(path=project_path,url=project_url,callback_get_login=self.callback_get_login)
                self.callback_get_login = None
            except NewProjectException:
                sys.stderr.write(e)
                tkMessageBox.showerror('Error','It was not possible to create a new project. \nPlease check svn URL and folder path.')
            except pysvn.ClientError:
                AskPassword.ask_password_window(self.root,self.create_callback_get_login)
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

    def __init__(self,Master=None, change_callback=None, update_license_event=None,**kw):

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

    def get_license(self):
        return self.__Text1.get(1.0,tk.END)

    def erase(self):
            self.__Text1.delete(1.0,tk.END)


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


class AskPassword(tk.Frame):

    def __init__(self,Master=None,callback=None,**kw):

        apply(tk.Frame.__init__,(self,Master),kw)
        self.root = Master
        self.callback = callback
        self.__Frame3 = tk.Frame(self)
        self.__Frame3.pack(side='top')
        self.__Label1 = tk.Label(self.__Frame3,text='Username:')
        self.__Label1.pack(side='left')
        self.username_entry = tk.Entry(self.__Frame3)
        self.username_entry.pack(side='left')
        self.__Frame2 = tk.Frame(self)
        self.__Frame2.pack(side='top')
        self.__Label2 = tk.Label(self.__Frame2,text='Password:')
        self.__Label2.pack(side='left')
        self.password_entry = tk.Entry(self.__Frame2,show='*')
        self.password_entry.pack(side='left')
        self.__Frame1 = tk.Frame(self)
        self.__Frame1.pack(side='top')
        self.okay_button = tk.Button(self.__Frame1,text='Okay')
        self.okay_button.pack(side='left')
        self.okay_button.bind('<ButtonRelease-1>',self.event_okay)
        self.cancel_button = tk.Button(self.__Frame1,text='Cancel')
        self.cancel_button.pack(side='left')
        self.cancel_button.bind('<ButtonRelease-1>',self.event_cancel)

    def event_cancel(self,Event=None):
        self.callback(None)
        self.root.destroy()

    def event_okay(self,Event=None):
        response = (self.username_entry.get(),self.password_entry.get())
        
        if not all(response):
            return

        self.callback(response)
        self.root.destroy()

    @classmethod
    def ask_password_window(cls,root,callback):
        window = tk.Toplevel(root)
        widget = cls(window,callback)
        widget.pack()
        window.transient(root)


if __name__ == '__main__':
    def print_it(event):
        print strvar.get()
    r = tk.Tk()
    strvar = tk.StringVar()
    test = ("none", "item1", "item2", "item3")
    strvar.set(test[0])
    om = EditableOptionMenu(r, strvar, *test, command=print_it)
    om.pack()
    om.insert_option(4, 'item4')
    om.delete_option(2)
    r.mainloop()

