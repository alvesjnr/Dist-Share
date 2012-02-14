

import Tkinter as tk
import tkFileDialog, tkMessageBox
import os
import shutil

from dist_creator import *
import tests_runner
import convert


root_path = "~"
default_target_path = '~'
committers_head = """#Edit commiters names and e-mails\n#Example: \n#aturing = aturing <aturing>\n#becames:\n#aturing = Alan Turing <alan@turing.org>"""

class App(object):

    origin_path = ''
    
    def __init__(self,root):
        
        self.root = root
        self.packages_variables = {}

        #Main Frame
        self.main_frame = tk.Frame(self.root)
        
        #Menu
        self.menubar = tk.Menu(self.root)        
        self.menu_tools = tk.Menu(self.menubar, tearoff=0)
        self.menu_tools_convert = tk.Menu(self.menu_tools)
        self.menu_tools_convert.add_command(label='svn -> git', command=self.svn2git)
        self.menu_tools_convert.add_command(label='svn -> mercurial')
        self.menu_tools.add_cascade(label='Convert', menu=self.menu_tools_convert)
        self.menubar.add_cascade(label='Tools', menu=self.menu_tools)
        
        #Packages Selection
        self.main_label = tk.Label(self.main_frame, text="Select the modules for your distribution:")
        
        self.checkbuttons_frame = tk.Frame(self.root)
        
        self.packages_frame = tk.Frame(self.main_frame)
        self.packages_scroll = tk.Scrollbar(self.checkbuttons_frame)
        
        #License adding
        self.license_label = tk.Label(self.main_frame, text="Place here your license:")

        self.license_frame = tk.Frame(self.main_frame)
        self.license_scroll = tk.Scrollbar(self.license_frame)
        self.license_box = tk.Text(self.license_frame,
                                   height=10)
        self.license_box.config(yscrollcommand=self.license_scroll.set)
        self.license_scroll.config(command=self.license_box.yview)
        self.license_box.pack(side=tk.LEFT)
        self.license_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        #Convert frame
        self.convert_frame = tk.Frame(self.main_frame)
        self.convert_checkbox_frame = tk.Frame(self.convert_frame)
        self.convert_radiobox_frame = tk.Frame(self.convert_frame)

        self.convert_to = tk.StringVar()

        self.convert_radio_label = tk.Label(self.convert_radiobox_frame, text='Convet to:')
        self.convert_radio_do_not_convert = tk.Radiobutton(self.convert_radiobox_frame, text="Do not convert", variable=self.convert_to, value='dnc')
        self.convert_radio_git = tk.Radiobutton(self.convert_radiobox_frame, text="Git", variable=self.convert_to, value='git')
        self.convert_radio_hg = tk.Radiobutton(self.convert_radiobox_frame, text="Mercurial", variable=self.convert_to, value='hg')
        self.convert_radio_do_not_convert.select()
        
        self.convert_radio_label.pack(anchor='w')
        self.convert_radio_do_not_convert.pack(anchor='w')
        self.convert_radio_git.pack(anchor='w')
        self.convert_radio_hg.pack(anchor='w')
        
        self.convert_radiobox_frame.pack(anchor='w')

        #Setting distribution name
        self.dist_name_frame = tk.Frame(self.main_frame)
        self.dist_name_label = tk.Label(self.dist_name_frame, text="Distribution name: ")
        self.dist_name_entry = tk.Entry(self.dist_name_frame)
        self.dist_name_entry.insert(0, "new_distribution_name")
        
        self.dist_name_label.pack(side=tk.LEFT)
        self.dist_name_entry.pack(side=tk.LEFT)        
                                   
        self.buttons_frame = tk.Frame(self.main_frame)
        
        self.button_find = tk.Button(self.buttons_frame, 
                                     text="Open",
                                     command=self.event_find_packages,
                                     width=8)
        self.button_refresh = tk.Button(self.buttons_frame,
                                        text="Refresh",
                                        command=self.event_refresh,
                                        width=8)
        self.button_next = tk.Button(self.buttons_frame,
                                     text="Create",
                                     command=self.event_next,
                                     width=8)
        
        self.button_find.pack(side=tk.LEFT)
        self.button_refresh.pack(side=tk.LEFT)
        self.button_next.pack(side=tk.LEFT)
        
        #Packing stuff
        self.main_label.pack(side=tk.TOP, anchor='w')
        self.packages_frame.pack(side=tk.TOP, anchor='w')
        self.license_label.pack(side=tk.TOP, anchor='w')
        self.license_frame.pack(side=tk.TOP, anchor='w')
        self.convert_frame.pack(side=tk.TOP, anchor='w')
        self.dist_name_frame.pack(side=tk.LEFT)
        self.buttons_frame.pack(side=tk.TOP)
        
        self.main_frame.pack()
        self.root.config(menu=self.menubar)
    

    def set_packages(self, packages_list):
        if self.packages_variables:
            for package in self.packages_variables.values():
                package['button'].pack_forget()

        self.packages_variables = {}
        for package in packages_list:
            var = tk.IntVar()
            c = tk.Checkbutton(self.packages_frame, text=package, variable=var, anchor='w',)
            var.set(1)
            self.packages_variables.update( {package: {'var': var, 'button':c}}  ) 
            c.pack(anchor='w')

    
    def event_find_packages(self):
        origin_path = tkFileDialog.askdirectory(parent=self.root,
                                                initialdir=root_path,
                                                title='Please select source directory')
        if origin_path:
            self.origin_path = origin_path
            packages = get_flat_packages(self.origin_path)
            self.set_packages(packages)
        
    
    def event_refresh(self):
        for package in self.packages_variables.values():
            package['var'].set(1)
    
    def event_next(self):

        if not self.origin_path:
            return

        license = self.license_box.get(1.0, tk.END)
        raw_packages = [package['button']['text'] for package in self.packages_variables.values() if package['var'].get()]

        if not license.strip():
            if not tkMessageBox.askokcancel('License','No license found. Do you want to proceed anyway?'):
                return
            else:
                license = ''

        self.target_path = tkFileDialog.askdirectory(parent=self.root,
                                                     initialdir=default_target_path,
                                                     title='Please select target directory')
        
        if self.target_path:
            self.target_path = os.path.join(self.target_path, self.dist_name_entry.get())
            
        if process_copy(self.origin_path, self.target_path, raw_packages, license):
            do_tests = tkMessageBox.askyesno(message='Copy finished\nDo you want to scan for tests?')
            if do_tests:
                self.do_tests()
        
    def do_tests(self):

        test_files = tests_runner.list_tests_from_directory(self.target_path)        
        output_log = tests_runner.run_tests(test_files)

        log_window = tk.Toplevel(self.root)
        log_board = LogBoard(log_window)
        log_board.fill_board(output_log)
        log_window.transient(self.root)
        log_window.grab_set()
        self.root.wait_window()
    
    def svn2git(self):
        
        is_svn_repo = False

        while not is_svn_repo:
            origin_path = tkFileDialog.askdirectory(parent=self.root,
                                                    initialdir=default_target_path,
                                                    title='Please select repository to convert')
            
            if not origin_path: #just check if cancel was pressed
                return
            
            is_svn_repo = convert.is_svn_repo(origin_path)
            if not is_svn_repo:
                tkMessageBox.showwarning(message="This is not a valid svn repository")
        
        svn_committers = convert.get_svn_committers(origin_path)

        
        svn_commiters = committers_head + '\n\n' + svn_committers

        committers_window = tk.Toplevel(self.root)
        commiters_board = CommitersBoard(committers_window)
        commiters_board.fill_board(svn_commiters)
        committers_window.transient(self.root)
        committers_window.grab_set()
        self.root.wait_window()

        import pdb; pdb.set_trace()
        target_path = tkFileDialog.askdirectory(parent=self.root,
                                                initialdir=default_target_path,
                                                title='Please select where you want to place your git repository')
        
        if not target_path:
            return
        

        if convert.svn2git(origin_path, target_path):
            tkMessageBox.showinfo(message="This is not a valid svn repository")
        else:
            tkMessageBox.showerror(message="This is not a valid svn repository")
        

class LogBoard(object):
    def __init__(self, root):
        
        self.root = root
        self.log_saved = False
        
        self.text_frame = tk.Frame(self.root )
        self.text_board = tk.Text(self.text_frame, height=40, width=100 )
        self.text_scroll = tk.Scrollbar(self.text_frame)
        
        self.text_board.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_board.yview)
        self.text_board.pack(side=tk.LEFT)
        self.text_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        self.buttons_frame = tk.Frame(self.root)
        self.button_save = tk.Button(self.buttons_frame,
                                     text="Save",
                                     command=self.event_save_log,
                                     width=8)
        self.button_quit = tk.Button(self.buttons_frame,
                                     text="Quit",
                                     command=self.event_quit,
                                     width=8)
        self.button_save.pack(side=tk.LEFT)
        self.button_quit.pack(side=tk.LEFT)

        
        self.text_frame.pack()
        self.buttons_frame.pack()
    
    def fill_board(self, text):
        self.text_board.insert(1.0, text)

    def event_save_log(self):
        fout = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt", parent=self.root)

        if fout:
            log = unicode(self.text_board.get(0.0,tk.END))
            fout.write(log)
            fout.close()
            self.log_saved = True 
    
    def event_quit(self):
        if not self.log_saved:
            if not tkMessageBox.askokcancel('Log not yet saved', 'Log file is not yet saved.\nDo you want to quit anyway?', parent=self.root):
                return
        self.root.destroy()

class CommitersBoard(object):
    def __init__(self, root):
        
        self.root = root
        self.log_saved = False
        
        self.text_frame = tk.Frame(self.root )
        self.text_board = tk.Text(self.text_frame, height=40, width=100 )
        self.text_scroll = tk.Scrollbar(self.text_frame)
        
        self.text_board.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.config(command=self.text_board.yview)
        self.text_board.pack(side=tk.LEFT)
        self.text_scroll.pack(side=tk.LEFT,
                                  fill=tk.Y)

        self.buttons_frame = tk.Frame(self.root)
        self.button_cancel = tk.Button(self.buttons_frame,
                                     text="Cancel",
                                     command=self.event_cancel,
                                     width=8)
        self.button_continue = tk.Button(self.buttons_frame,
                                     text="Continue",
                                     command=self.event_continue,
                                     width=8)
        self.button_cancel.pack(side=tk.LEFT)
        self.button_continue.pack(side=tk.LEFT)

        
        self.text_frame.pack()
        self.buttons_frame.pack()
    
    def fill_board(self, text):
        self.text_board.insert(1.0, text)
    
    def get_valid_board(self):
        text = self.text_board.get(0.0, tk.END).split('\n')
        output = '\n'.join([line.strip() for line in text if not line.strip().startswith('#')])
        return output

    def event_continue(self):
        if not tkMessageBox.askyesno('Continue', 'Continue convertion?', parent=self.root):
            return
        
        self.root.svn_commiters = self.get_valid_board()
        self.root.destroy()
    
    def event_cancel(self):
        if not tkMessageBox.askokcancel('Cancel', 'Cancel repository convertion?', parent=self.root):
            return
        self.root.destroy()


    
if __name__=='__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

