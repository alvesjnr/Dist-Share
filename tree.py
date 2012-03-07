# -*- coding: utf-8 -*-

import Tkinter as tk
import Tix
import os

FOLDER_SEPARATOR = os.sep
SPACE = '%20'

class CheckboxTree(object):
    def __init__(self, root, items=[], height=400, width=600, change_function=None):
        self.odd = True
        self.root = root
        self.height = height
        self.width = width
        self.make_list(normalize_items(items))
        self.change_function = change_function
        self.all_items = self.cl.getselection()
        
    def make_list(self, items):
        self.cl = Tix.CheckList(self.root, 
                                browsecmd=self.selectItem,
                                command=self.selectItem,
                                width=self.width, 
                                height=self.height,)
        self.cl.hlist.configure(indicatorcmd=self.colapse,
                                selectforeground='black',
                                separator=FOLDER_SEPARATOR)
        self.cl.pack(fill=Tix.BOTH, side=tk.LEFT)
        
        for i in items:
            self.cl.hlist.add(i,text=i)
            self.cl.setstatus(i, 'on')
        
        self.cl.autosetmode()
        for name in self.cl.getselection():
            self.cl.close(name)
    
    def colapse(self,a):
        if self.odd:
            self.odd = False
            return
        self.odd=True

        mode = self.cl.getmode(a)

        if mode == 'close':
            self.cl.close(a)
        elif mode == 'open':
            self.cl.open(a)

    def selectItem(self, item):
        status = self.cl.getstatus(item)
        #do the top-bottom propagation
        for i in self.all_items:
            if i.startswith(item + FOLDER_SEPARATOR):
                self.cl.setstatus(i, status)
        
        #do the bottom-up propagation
        parent = FOLDER_SEPARATOR.join(item.split(FOLDER_SEPARATOR)[:-1])
        while status == 'on' and parent and self.cl.getstatus(parent) == 'off':
            self.cl.setstatus(parent, 'on')
            parent = FOLDER_SEPARATOR.join(parent.split(FOLDER_SEPARATOR)[:-1])
        
        if self.change_function:
            self.change_function()
    
    def forget(self):
        self.cl.forget()

    def get_checked_items(self, mode='on'):
        return self.cl.getselection(mode=mode)
    
    def set_unchecked_items(self, items):
        for item in items:
            self.cl.setstatus(item, 'off')
    
    def set_all_items(self):
        for item in self.all_items:
            self.cl.setstatus(item, 'on')


def normalize_items(items):
    """ This function gets a list os directories and add the initial path:
        input: ['/a/b/c', '/a/b/d', '/a/d/j']
        output: ['a', 'a/b', 'a/b/c', 'a/b/d', 'a/d/j']
    """
    if not items:
        return []

    first_entry = items[0].split(FOLDER_SEPARATOR)

    list_head = []
    for i in range(len(first_entry)):
        entry = FOLDER_SEPARATOR.join(first_entry[:i+1])
        if entry:
            if entry.startswith(FOLDER_SEPARATOR):
                entry = entry.replace(FOLDER_SEPARATOR,'',1)
            list_head.append(entry)

    list_tail = []
    for i in items[1:]:
        if i.startswith(FOLDER_SEPARATOR):
            i = i.replace(FOLDER_SEPARATOR,'',1)
            list_tail.append(i)

    return list_head + list_tail


if __name__ == '__main__':

    """just for test and exemplification"""
    import dist_creator as dc
    items = dc.get_files('/home/antonio/Projects/LightPy')

    root = Tix.Tk()
    frame = Tix.Frame(root, bg='white')
    tree = CheckboxTree(frame, items)
    frame.pack(fill=Tix.BOTH)
    root.update()
    root.mainloop()

