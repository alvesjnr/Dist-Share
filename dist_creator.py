import sys
import pkgutil
import os
import shutil
from os import path
import tkFileDialog, tkMessageBox

comments = {'.py':{'begin':'"""', 'end':'"""'},
            '.c':{'begin':'/*', 'end':'*/'},
            '.cpp':{'begin':'/*', 'end':'*/'},
            '.h':{'begin':'/*', 'end':'*/'},
            }

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

def add_license(root, extensions, text):
    files = os.listdir(root)

    for f in files:
        file_path = os.path.join(root,f)
        if os.path.isdir(file_path):
            add_license(file_path, extensions, text)
        else:
            _,ext = os.path.splitext(f)
            if ext in extensions:
                license = process_license(text, ext)
                with open(file_path, "r+") as f:
                     old = f.read() 
                     f.seek(0) 
                     f.write(license+"\n" + old) 
                break


def process_license(license, extension):

    if not license:
        return ''

    comment_begin = comments[extension]['begin']
    comment_end = comments[extension]['end']

    license = license.strip()
    if license.startswith(comment_begin) and license.endswith(comment_end):
        return license + '\n\n'
    else:
        return comment_begin + license + comment_end + "\n\n"


class CreateCopyError(Exception):
    """Problems to create copy"""
    def __init__(self,message):
        self.message = message

