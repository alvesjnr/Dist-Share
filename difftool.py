# -*- coding: utf-8 -*-

import os

def get_files_tree(root, level=0, stack_on_level={}, show_hidden=False, output=[]):
    
    if level==0:
        print root

    files = os.listdir(root)
    stack_on_level[level] = True
    for f in files:
        if not show_hidden and f.startswith('.'):
            continue
        for i in range(level):
            if i != level:
                if stack_on_level[i]:
                    output.append('│ ')
                else:
                    print output.append('  ')
        if f==files[-1]:
            output.append('└─ '+f)
            stack_on_level[level] = False
        else:
            output.append('├─ '+f)
        
        if os.path.isdir(os.path.join(root,f)):
            get_files_tree(os.path.join(root,f),level=level+1, stack_on_level=stack_on_level, output=output)
    return output

if __name__=='__main__':
    for i in get_files_tree('.', show_hidden=True):
        print i
