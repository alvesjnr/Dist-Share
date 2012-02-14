import Tkinter as tk
import Tix

class CheckboxTree(object):
    def __init__(self, root, items={}):
        self.root = root
        self.make_list(items)

    def make_list(self, items):
        self.cl = Tix.CheckList(self.root, browsecmd=self.selectItem)
        self.cl.pack()
        
        if items:
            self.add_items(items)

        # self.cl.hlist.add("CL1", text="checklist1")
        # self.cl.hlist.add("CL1.Item1", text="subitem1")
        # self.cl.hlist.add("CL2", text="checklist2")
        # self.cl.hlist.add("CL2.Item1", text="subitem1")
        # self.cl.setstatus("CL2", "on")
        # self.cl.setstatus("CL2.Item1", "on")
        # self.cl.setstatus("CL1", "off")
        # self.cl.setstatus("CL1.Item1", "off")
        # self.cl.autosetmode()
    
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
        print item, self.cl.getstatus(item)

items = {'one':{'A':{},
                'B':{},
                },
         'two':{'has_more':{'1':{},
                            '2':{}
                            },
                 'blah':{},
                },
        }

def main():
    root = Tix.Tk()
    view = CheckboxTree(root, items)
    root.update()
    root.mainloop()

if __name__ == '__main__':
    main()
