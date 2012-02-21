# -*- coding: utf-8 -*-

import os

def get_files_tree(root, level=0, stack_on_level={}, show_hidden=False, output=[]):
    
    if level==0:
        print root

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
        if f==files[-1]:
            output.append(line_output+'└─ '+f)
            stack_on_level[level] = False
        else:
            output.append(line_output+'├─ '+f)
        
        if os.path.isdir(os.path.join(root,f)):
            get_files_tree(os.path.join(root,f),level=level+1, stack_on_level=stack_on_level, output=output)
    return output

if __name__=='__main__':
    for i in get_files_tree('.', show_hidden=True):
        print i
