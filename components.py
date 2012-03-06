
class Board(object):
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
            if not tkMessageBox.askokcancel('Log not yet saved', 'Log file is not yet saved.\nDo you want to quit anyway?', parent=self.root):
                return
        self.root.destroy()


if __name__=='__main__':

    import Tkinter as tk

    root = tk.Tk()
    app = Board(root)
    root.mainloop()

