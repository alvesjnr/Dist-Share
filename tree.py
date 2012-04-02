# -*- coding: utf-8 -*-

import Tkinter as tk
import Tix
import os
import sys

from functions import *

FOLDER_SEPARATOR = os.sep
SPACE = '%20'
SVN_MARKER = os.path.join(FOLDER_SEPARATOR,'.svn')


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


class CheckboxTree(object):

    def __init__(self, root, parent, height=500, width=600):
        self.odd = True
        self.root = root
        self.height = height
        self.width = width
        self.parent = parent
        self.cl = Tix.CheckList(self.root, 
                                browsecmd=self.selectItem,
                                command=self.double_click,
                                width=self.width, 
                                height=self.height,)
        self.cl.hlist.configure(indicatorcmd=self.colapse,
                                selectforeground='black',
                                separator=FOLDER_SEPARATOR)
        self.cl.pack(fill=Tix.BOTH, side=tk.LEFT)

    def reset_tree(self):
        self.cl.destroy()
        self.cl = Tix.CheckList(self.root, 
                                browsecmd=self.selectItem,
                                command=self.double_click,
                                width=self.width, 
                                height=self.height,)
        self.cl.hlist.configure(indicatorcmd=self.colapse,
                                selectforeground='black',
                                separator=FOLDER_SEPARATOR)
        self.cl.pack(fill=Tix.BOTH, side=tk.LEFT)

    def fill(self,items):
        items = self._remove_space(items)
        self.make_list(normalize_items(items))
        self.all_items = self.cl.getselection()
        
    def make_list(self, items):
        
        for i in items:
            if not SVN_MARKER in i:
                text = i.split(FOLDER_SEPARATOR)[-1]
                text = text.replace(SPACE,' ')
                self.cl.hlist.add(i,text=text)
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

    def double_click(self,item):
        text = open(FOLDER_SEPARATOR+item.replace(SPACE,' ')).read()
        Board.show_message(self.root,text)
        self.selectItem(item)

    def selectItem(self, item):
        item = item.replace(' ',SPACE)
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
        
        self.parent.change_callback()
    
    def forget(self):
        self.cl.forget()

    def get_checked_items(self, mode='on'):
        checked_items = [os.path.join(FOLDER_SEPARATOR,item) for item in self.cl.getselection(mode=mode)]
        checked_items = self._add_space(checked_items)
        return checked_items
    
    def set_unchecked_items(self, items):
        items = self._remove_space(items)
        for item in items:
            if item.startswith(FOLDER_SEPARATOR):
                item = item.replace(FOLDER_SEPARATOR,'',1)
            try:
                self.cl.setstatus(item, 'off')
            except Tix.TclError as e:
                sys.stderr.write('Warning: %s\n' % str(e))
    
    def set_all_items(self):
        for item in self.all_items:
            self.cl.setstatus(item, 'on')

    @staticmethod
    def _remove_space(l):
        f = lambda x : x.replace(' ',SPACE)
        return map(f,l)

    @staticmethod
    def _add_space(l):
        f = lambda x : x.replace(SPACE,' ')
        return map(f,l)


if __name__ == '__main__':

    """just for test and exemplification"""
    import functions as dc
    items = dc.get_files('/home/antonio/Projects/LightPy')

    root = Tix.Tk()
    frame = Tix.Frame(root, bg='white')
    tree = CheckboxTree(frame, items)
    frame.pack(fill=Tix.BOTH)
    root.update()
    root.mainloop()

