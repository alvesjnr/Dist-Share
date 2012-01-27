import sys
import pkgutil
import os
import shutil
from os import path
from pprint import pprint
import tkFileDialog, tkMessageBox

def get_modules_tree(root):
    return {root : get_package_child(root,root)}
    

def get_package_child(name,root):

    modules_in_root = [_[1] for _ in pkgutil.iter_modules([root])]
    
    here = {}
    
    for package in modules_in_root:
        here.update({package:get_package_child(package, path.join(root,package))})

    return here


def get_flat_packages(root):

    return [_[1] for _ in pkgutil.iter_modules([root])]
    

class CreateCopyError(Exception):
    """Problems to create copy"""
    

def create_copy(origin, destin, packages):
    #create a new directory with the name of the distribution
    try:
        os.mkdir(destin)
    except OSError as e:
        tkMessageBox.showinfo(message='This file already exists\nChoose a different name')
        return
    
    original_packages = get_flat_packages(origin)
    avoided_packages = [p for p in original_packages if p not in packages]
    
    #list all files/directories in origin
    files = os.listdir(origin)
    
    for f in files:
        if f not in avoided_packages:
            try:
                shutil.copytree(os.path.join(origin,f), os.path.join(destin,f))
            except OSError as e:
                try:
                    shutil.copy2(os.path.join(origin,f), os.path.join(destin,f))
                except:
                    raise CreateCopyError



if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print '%s: missing root operand' % (sys.argv[0])
        print "Try '%s <package_root>'" % (sys.argv[0])
    else:
        pkg_root = sys.argv[1]
        if not path.isdir(pkg_root):
            raise ArgumentError
        else:
            pprint(get_modules_tree(pkg_root))
        
