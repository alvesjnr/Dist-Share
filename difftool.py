# -*- coding: utf-8 -*-

import os

def get_files_tree(root, level=0):
    
    files = os.listdir(root)

    for f in files:
        for i in range(level):
            if i != level:
                print '│   ',
        print '├── '+f
        
        if os.path.isdir(os.path.join(root,f)):
            get_files_tree(os.path.join(root,f),level=level+1)

if __name__=='__main__':
    get_files_tree('.')
