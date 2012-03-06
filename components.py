import Tkinter as tk
import ttk
import dist_creator as dc

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


class RenameFile(object):
    def __init__(self,root,file, modification_function, modified_name=''):

        self.root = root
        
        self.full_file_name = file
        self.original_name = self.full_file_name.split(SEPARATOR)[-1]
        
        self.filepath = SEPARATOR.join(self.full_file_name.split(SEPARATOR)[:-1]) + SEPARATOR
        
        if modified_name:
            self.new_filename = modified_name
            newpath_value = self.filepath + modified_name
        else:
            newpath_value = file
            self.new_filename = self.original_name
        
        self.full_file_name_label = tk.Label(self.root,text=file)
        self.new_name = tk.Entry(self.root)
        self.new_name.bind('<KeyRelease>',self.change_name)
        self.new_name.insert(0,self.new_filename)
        self.newpath_variable = tk.StringVar()
        self.newpath_variable.set(newpath_value)
        self.new_file_name_label = tk.Label(self.root,textvariable=self.newpath_variable)

        self.okay_cancel_frame = tk.Frame(self.root)
        tk.Button(self.okay_cancel_frame, text='OK', command=self.okay).pack(side=tk.LEFT)
        tk.Button(self.okay_cancel_frame, text='Cancel', command=self.close).pack(side=tk.LEFT)

        self.full_file_name_label.pack()
        self.new_name.pack()
        self.new_file_name_label.pack()
        self.okay_cancel_frame.pack()

        self.comunicate_modification = modification_function

    def change_name(self, event):
        self.new_filename = self.new_name.get()
        self.new_file_name = self.filepath + self.new_filename
        self.newpath_variable.set(self.new_file_name)

    def close(self):
        self.root.destroy()

    def okay(self):
        modification = {'path':self.filepath[:-1],
                        'old_name':self.original_name,
                        'new_name':self.new_filename}

        self.comunicate_modification(modification)
        self.close()


class TreeView(object):
    
    def __init__(self,root, items=[]):
        self.root = root

        self.tree_view = ttk.Treeview(self.root)
        self.add_items(items)
        self.tree_view.tag_bind('ttk', '<Double-Button-1>', self.item_clicked)
        self.tree_view.pack(side=tk.LEFT)

    def add_item(self,item):
        if SEPARATOR in item:
            folder = item.split(SEPARATOR)
            self.tree_view.insert(SEPARATOR.join(folder[:-1]), 'end', item, text=folder[-1],tags=('ttk','simple'))
        else:
            self.tree_view.insert('','end',item,text=item,tags=('ttk','simple'))

    def add_items(self,items):
        for item in items:
            self.add_item(item)

    def remove_item(self, item):
        pass

    def item_clicked(self, event):

        item_clicked = self.tree_view.focus()

        rename_window = tk.Toplevel(self.root)
        rename_widget = RenameFile(rename_window, item_clicked, self.modification_function)
        rename_window.transient(self.root)   

    def modification_function(self,modification):

        #FIXME: reset name when midifying
        new_name = modification['new_name']
        item_path = SEPARATOR.join([modification['path'],modification['old_name']])
        old_name = self.tree_view.item(item_path)['text']

        if old_name != new_name:
            self.tree_view.item(item_path, text="%s -> %s" % (old_name,new_name))


class ModificationList(object):

    def __init__(self, root):
        
        self.root = root
        self.modification_list = []

        self.frame = tk.Frame(self.root)
        self.listbox = tk.Listbox(self.frame)
        self.listbox.bind('<Double-Button-1>', self.edit_entry)
        self.listbox.pack()

        self.buttons_frame = tk.Frame(self.frame)
        tk.Button(self.buttons_frame, text='Edit', command=self.edit_entry).pack(side=tk.LEFT)
        tk.Button(self.buttons_frame, text='Remove', command=self.remove_entry).pack(side=tk.LEFT)

        self.buttons_frame.pack()
        self.frame.pack(side=tk.LEFT)

    def add_item(self,item):
        self.modification_list.insert(0,item)
        old_name = item['old_name']
        new_name = item['new_name']

        self.listbox.insert(0, "%s -> %s" % (old_name,new_name))

    def edit_entry(self, event=None):
        index = int(self.listbox.curselection()[0])
        modification_profile = self.modification_list[index]
        
        rename_window = tk.Toplevel(self.root)
        rename_widget = RenameFile(rename_window, SEPARATOR.join([modification_profile['path'], 
                                                                  modification_profile['old_name']]), 
                                   self.modification_function,
                                   modified_name=modification_profile['new_name'])

        rename_window.transient(self.root)

    def modification_function(self,profile):
        #FIXME!!!
        index = int(self.listbox.curselection()[0])

        self.listbox.delete(index)
        old_name = profile['old_name']
        new_name = profile['new_name']

        self.listbox.insert(0, "%s -> %s" % (old_name,new_name))
        # self.parent.modifying_name(profile)

    def remove_entry(self):
        index = int(self.listbox.curselection()[0])

        self.listbox.delete(index, index)
        profile = self.modification_list.pop(index)

        # self.parent.removing_rename(profile)


class App(object):

    def __init__(self, root, path):

        self.root = root

        items = dc.get_files(path)
        self.tree = CheckboxTree(self.root, items=items)
        self.tree_view = TreeView(self.root)
        self.modification_list =  ModificationList(self.root)



if __name__=='__main__':

    import Tix
    root = Tix.Tk()
    # app = TreeView(root, ['a', 'a/b', 'a/b/c', 'a/b/d', 'a/j'])
    app = App(root, '/home/antonio/Projects/dist_project')

    root.mainloop()

