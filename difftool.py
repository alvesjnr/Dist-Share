# -*- coding: utf-8 -*-

import Tkinter as tk
import tkMessageBox
import tkFileDialog

import os

def get_files_tree(root, level=0, stack_on_level={}, show_hidden=False, output=None, fl_root=None):
    if output is None: output = []

    if level==0:
        output.append(root)
        fl_root = root.split(os.sep)[-1]

    files = os.listdir(root)
    stack_on_level[level] = True
    for f in files:
        line_output = ''
        if not show_hidden and f.startswith('.'):
            continue
        for i in range(level):
            if i != level:
                if stack_on_level[i]:
                    line_output += '│ '
                else:
                    line_output += '  '

        filename = os.path.join(root,f)
        filename = filename.split(fl_root)
        if len(filename) > 1:
            filename = fl_root.join(filename[1:])
        else:
            filename = '.'

        if f==files[-1]:
            output.append((filename,line_output+'└─ '+f))
            stack_on_level[level] = False
        else:
            output.append((filename,line_output+'├─ '+f))
        
        if os.path.isdir(os.path.join(root,f)):
            get_files_tree(os.path.join(root,f),level=level+1, stack_on_level=stack_on_level, show_hidden=False, output=output, fl_root=fl_root)
    
    if level==0:
        return output

def get_removed_lines(original,copy):
    for number,line in enumerate(original):
        if line not in copy:
            yield number


class DiffBoard(object):
    def __init__(self, root):
        
        self.root = root
        
        self.labels_frame = tk.Frame(self.root)

        self.label_original = tk.Frame(self.labels_frame)
        self.label_copy = tk.Frame(self.labels_frame)

        tk.Label(self.label_original, text='Original Project').pack()
        tk.Label(self.label_copy, text='Copy').pack()
        self.label_original.pack(side=tk.LEFT)
        self.label_copy.pack(side=tk.LEFT)

        self.text_frame = tk.Frame(self.root )
        self.text_board_l = tk.Listbox(self.text_frame, height=40, width=50 )
        self.text_board_r = tk.Listbox(self.text_frame, height=40, width=50 )
        self.text_scroll_l = tk.Scrollbar(self.text_frame)
        self.text_scroll_r = tk.Scrollbar(self.text_frame)
        
        self.text_board_l.config(yscrollcommand=self.text_scroll_l.set)
        self.text_scroll_l.config(command=self.text_board_l.yview)
        self.text_board_r.config(yscrollcommand=self.text_scroll_r.set)
        self.text_scroll_r.config(command=self.text_board_r.yview)
        self.text_board_l.pack(side=tk.LEFT)
        self.text_scroll_l.pack(side=tk.LEFT,
                                  fill=tk.Y)
        self.text_board_r.pack(side=tk.LEFT)
        self.text_scroll_r.pack(side=tk.LEFT,
                                  fill=tk.Y)
        
        self.buttons_frame = tk.Frame(self.root)
        self.button_quit = tk.Button(self.buttons_frame,
                                     text="Quit",
                                     command=self.event_quit,
                                     width=8)
        self.button_quit.pack(side=tk.LEFT)

        self.labels_frame.pack()
        self.text_frame.pack()
        self.buttons_frame.pack()
    
    def fill_board(self, board, text):
        if board=='r':
            for number,line in enumerate(text):
                self.text_board_r.insert(number, line)
                self.text_board_r.itemconfig(number, bg='#00b2ee')
        elif board=='l':
            for number,line in enumerate(text):
                self.text_board_l.insert(number, line)
                self.text_board_l.itemconfig(number, bg='#00b2ee')
    
    def event_quit(self):
        self.root.destroy()
    
    def set_removed_colors(self, removed):
        for i in removed:
            self.text_board_l.itemconfig(i, bg='#EE3B3B')
    
    def set_diff_board(self, original=None, copy=None):
        original = original or tkFileDialog.askdirectory() 
        if not original:
            self.event_quit()
            return

        copy = copy or tkFileDialog.askdirectory()
        if not copy:
            self.event_quit()
            return
        
        original = get_files_tree(original)
        copy = get_files_tree(copy) #FIXME: why should I have to pass output if it is defined on function signature?
        removed_lines = get_removed_lines([t[0] for t in original],[t[0] for t in copy])

        self.fill_board('l',(t[1] for t in original))
        self.fill_board('r',(t[1] for t in copy))
        self.set_removed_colors(removed_lines)


if __name__=='__main__':
    
    root = tk.Tk()
    app = DiffBoard(root)
    app.set_diff_board('/home/antonio/Projects/dist_project', '/tmp/catapulta/dist_project')
    root.mainloop()

