import sys
import pkgutil
import os
import shutil
from os import path
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
                    raise CreateCopyError(e.message)

def add_text(root, extensions, text):
    files = os.listdir(root)

    for f in files:
        file_path = os.path.join(root,f)
        if os.path.isdir(file_path):
            add_text(file_path, extensions, text)
        else:
            for ext in extensions:  #TODO it is not performatic!
                if f.endswith(ext):
                    with open(file_path, "r+") as f:
                         old = f.read() 
                         f.seek(0) 
                         f.write(text+"\n" + old) 
                    break


class CreateCopyError(Exception):
    """Problems to create copy"""
    def __init__(self,message):
        self.message = message

