#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tix
import Tkinter as tk
import tkFileDialog, tkMessageBox

from tree import CheckboxTree
from components import RenameFile, ModificationList


class App(object):
    
    def __init__(self,root):

        self.root = root

        #Frames definitions
        self.main_frame = tk.Frame(self.root, width=600, height=600)
        self.copy_frame = tk.Frame(self.main_frame)
        self.license_frame = tk.Frame(self.main_frame)

        #adding menubar
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)

        #File menu
        self.filemenu.add_command(label="Open Project", command=None)
        self.filemenu.add_command(label="Save Project", command=None)
        self.filemenu.add_command(label="Save Project As ...", command=None)
        self.filemenu.add_command(label="New Project", command=None)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)

        #Copy menu
        self.copymenu = tk.Menu(self.menubar, tearoff=0)
        self.copymenu.add_command(label="Add new",command=None)

        #Tools menu
        self.toolsmenu = tk.Menu(self.menubar, tearoff=0)
        self.toolsmenu.add_command(label="Diff", command=None)
        self.toolsmenu.add_command(label="Tests", command=None)
                
        #packing menu
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Copy", menu=self.copymenu)
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        self.root.config(menu=self.menubar)

        #packing frames
        self.copy_frame.pack()
        self.license_frame.pack()
        self.main_frame.pack()


def main():
    WINDOW_TITLE = 'Dist Share'
    root = Tix.Tk()
    root.wm_title('Untitled Project - '+WINDOW_TITLE)
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
