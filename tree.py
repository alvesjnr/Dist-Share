import Tkinter as tk
import Tix

class CheckboxTree(object):
    def __init__(self, root, items={}, height=600, width=800):
        self.root = root
        self.height = height
        self.width = width
        self.make_list(items)
        self.all_items = self.cl.getselection()

    def make_list(self, items):
        self.cl = Tix.CheckList(self.root, browsecmd=self.selectItem, width=self.width, height=self.height)
        self.cl.pack(fill=Tix.BOTH)
        
        if items:
            self.add_items(items)
        self.cl.autosetmode()

        for name in self.cl.getselection():
            self.cl.close(name)
    
    def add_items(self, items, parent=''):

        for item in items:
            if parent:
                name = '%s.%s' % (parent,item)
            else:
                name = item
            self.cl.hlist.add(name, text=item)
            self.cl.setstatus(name, 'on')

            if items[item]:
                self.add_items(items[item], name)

    def selectItem(self, item):
        #do the propagation

        for i in self.all_items:
            if i.startswith(item):
                self.cl.setstatus(i, self.cl.getstatus(item))
    
    def forget(self):
        self.cl.forget()

    def get_checked_items(self):
        return self.cl.getselection()




if __name__ == '__main__':
    items = {'one':{'A':{},
                    'B':False,
                    },
             'two':{'has_more':{'1':None,
                                '2':{},  #Empty node can be either None or {} or [] or False ...
                                },
                     'blah':{},
                    },
            }
    root = Tix.Tk()
    frame = Tix.Frame(root)
    tree = CheckboxTree(frame, items)
    frame.pack(fill=Tix.BOTH)
    root.update()
    root.mainloop()

