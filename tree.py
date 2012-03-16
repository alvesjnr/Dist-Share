# -*- coding: utf-8 -*-

import Tkinter as tk
import Tix
import os

FOLDER_SEPARATOR = os.sep
SPACE = '%20'

class CheckboxTree(object):
    def __init__(self, root, parent, height=500, width=600):
        self.odd = True
        self.root = root
        self.height = height
        self.width = width
        self.parent = parent
        self.reset_tree()

    def reset_tree(self):
        self.cl = Tix.CheckList(self.root, 
                                browsecmd=self.selectItem,
                                command=self.selectItem,
                                width=self.width, 
                                height=self.height,)
        self.cl.hlist.configure(indicatorcmd=self.colapse,
                                selectforeground='black',
                                separator=FOLDER_SEPARATOR)
        self.cl.pack(fill=Tix.BOTH, side=tk.LEFT)

    def fill(self,items):
        self.make_list(normalize_items(items))
        self.change_function = change_function
        self.all_items = self.cl.getselection()
        
    def make_list(self, items):
        
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

