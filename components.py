#!/usr/bin/python
import Tkinter as tk
import Tix
import ttk
from functions import *
import tkFileDialog, tkMessageBox

from tree import CheckboxTree

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
        modification_entry = self.listbox.selection_get()
        original_name, new_name = self._split_text(modification_entry)
        
        modify_window = tk.Toplevel(self.root)
        modify_widget = EditModification(modify_window,modification_entry,self.edit_entry_callback)

    def edit_entry_callback(self,change_descriptor,new_name):
        if change_descriptor == self.listbox.get('active'):
            self.listbox.delete('active')
            original_name,_ = self._split_text(change_descriptor)
            self.listbox.insert(0,"%s -> %s" % (original_name,new_name))
        

    def add_entry_window(self):
        """ Calls the AddModification window passing the function _add_item
            to insert a new entry
        """
        add_entry_window = tk.Toplevel(self.root)
        add_entry_widget = AddModification(path='/tmp',callback=self._add_item,root=add_entry_window)
        add_entry_window.transient(self.root)

    def remove_entry(self):
        if len(self.listbox.curselection()):
            index = int(self.listbox.curselection()[0])
            self.listbox.delete(index, index)

    def fill(self,items):
        for item in items:
            self._add_item(item,items[item])

    def _add_item(self,original_name,new_name):
        self.listbox.insert(0,"%s -> %s" % (original_name,new_name))

    def get_modification_list(self):

        return dict(self._split_text(item) for item in self.listbox.get(0,tk.END))

    def _split_text(self,item):
            return item.split(' -> ')


class AddModification(object):

    def __init__(self,root,path,callback):

        self.root = root
        self.callback = callback

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
        filepath = tkFileDialog.askopenfilename()

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

