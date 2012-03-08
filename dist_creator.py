# -*- coding: utf-8 -*-

import sys
import pkgutil
import os
import shutil
import tkFileDialog, tkMessageBox
from os import path


comments = {'.py':{'begin':'"""', 'end':'"""'},
            '.c':{'begin':'/*', 'end':'*/'},
            '.cpp':{'begin':'/*', 'end':'*/'},
            '.h':{'begin':'/*', 'end':'*/'},
            '.hpp':{'begin':'/*', 'end':'*/'},
            }

extensions = [key for key in comments]
DO_NOT_ADD_LICENSE_MARKER = 'DO NOT ADD LICENSE'
FOLDER_SEPARATOR = os.sep
SPACE = '%20'


class CreateCopyError(Exception):
    """Something wrong when copying"""
    message="Something wrong when copying"


def get_files(root,files=None):
    if files is None:
        files = []

    files_here = [os.path.join(root,filename) for filename in os.listdir(root)]

    files += files_here

    for f in files_here:
        if os.path.isdir(f):
            files = get_files(f,files)

    return files # [f.replace(' ',SPACE) for f in files]


def get_folder_tree(root):
    
    root_name = root.split(FOLDER_SEPARATOR)[-1]
    return ({root_name : get_folder_child(root,root)},{'meta':{'root_path':root}})


def get_folder_child(name,root):
    
    folders_in_root = filter(lambda x : os.path.isdir(os.path.join(root,x)), os.listdir(root))
    
    here = {}
    
    for folder in folders_in_root:
        here.update({folder:get_folder_child(folder, path.join(root,folder))})

    return here


def get_package_tree(root):

    root_name = root.split(FOLDER_SEPARATOR)[-1]
    return ({root_name : get_package_child(root,root)},{'meta':{'root_path':root}})


def get_package_child(name,root):

    modules_in_root = [_[1] for _ in pkgutil.iter_modules([root])]
    
    here = {}
    
    for package in modules_in_root:
        here.update({package:get_package_child(package, path.join(root,package))})

    return here


def get_flat_packages(root):

    return [module[1] for module in pkgutil.iter_modules([root])]
        

def create_copy(origin, destin, packages):
    #create a new directory with the name of the distribution
    try:
        os.mkdir(destin)
    except OSError as e:
        tkMessageBox.showwarning(message='This file already exists\nChoose a different name')
        raise CreateCopyError
    
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
                    raise e
            except shutil.Error as e:
                sys.stderr.write(str(e.message))


def add_license(filepath, text):

    _,ext = os.path.splitext(f)
    if ext in extensions:
        license = process_license(text, ext)
    else:
        return  # If the extension is not listed, we don't apply the license

    with open(filepath, "r+") as f:
        firstline = f.readline()
        if DO_NOT_ADD_LICENSE_MARKER in firstline.upper():
            old = f.read()
            f.close()
            with open(file_path, 'w') as f:
                f.write(old)
                return    #avoid any problems of reusing the f var
        else:
            f.seek(0)
            old = f.read()
            f.seek(0)
            try:
                f.write(license + old)
            except:
                #FIXME: seek for the correct encoding!
                f.write(old)


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
        

def process_copy(origin_path, target_path, packages, raw_license):

    if packages:
                
        try:
            create_copy(origin_path, target_path, packages)
        except CreateCopyError as e:
            sys.stderr.write(e.message)
            return False
        
        add_license(target_path, raw_license)

        return True
    
    return False


def process_folders_copy(origin_path, target_path, folders_to_copy, raw_license):

    if folders_to_copy:
                
        leaves = get_leaves(folders_to_copy)
        inter_nodes = get_leaves(folders_to_copy, mirror=True)
        copy_leaves(origin_path, target_path, leaves)
        copy_inter_nodes(origin_path, target_path, inter_nodes)
        
        add_license(target_path, raw_license)

        return True


def copy_leaves(origin_path, target_path, leaves):
    origin_location = FOLDER_SEPARATOR.join(origin_path.split(FOLDER_SEPARATOR)[:-1])
    for folder in leaves:
        copy_folder = folder.split(FOLDER_SEPARATOR)
        copy_folder = FOLDER_SEPARATOR.join(copy_folder[1:])

        shutil.copytree(os.path.join(origin_location,folder), os.path.join(target_path,copy_folder))


def copy_inter_nodes(origin_path, target_path, inter_nodes):
    origin_location = FOLDER_SEPARATOR.join(origin_path.split(FOLDER_SEPARATOR)[:-1])

    for node in inter_nodes:
        isfile = lambda f : os.path.isfile( os.path.join(os.path.join(origin_location,node) ,f))
        files = filter(isfile,os.listdir(os.path.join(origin_location,node)))
        
        copy_node = node.split(FOLDER_SEPARATOR)
        copy_node = FOLDER_SEPARATOR.join(copy_node[1:])
        
        for f in files:
            shutil.copy2(os.path.join(os.path.join(origin_location,node),f),os.path.join(target_path,copy_node))


def get_leaves(nodes, separator=FOLDER_SEPARATOR, mirror=False):

    leaves = []
    nodes = nodes[:]
    
    while nodes:
        node = nodes.pop(0)
        if not mirror ^ bool(filter(lambda x : x.startswith(node+separator), nodes)):
            leaves.append(node)
    
    return leaves
