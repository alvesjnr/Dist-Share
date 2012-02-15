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

class CreateCopyError(Exception):
    """Something wrong when copying"""
    message="Something wrong when copying"

def get_folder_tree(root):
    
    root_name = root.split('/')[-1]
    return ({root_name : get_folder_child(root,root)},{'meta':{'root_path':root}})


def get_folder_child(name,root):
    
    folders_in_root = filter(lambda x : os.path.isdir(os.path.join(root,x)), os.listdir(root))
    
    here = {}
    
    for folder in folders_in_root:
        here.update({folder:get_folder_child(folder, path.join(root,folder))})

    return here


def get_modules_tree(root):

    root_name = root.split('/')[-1]
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


def add_license(root, text):

    files = os.listdir(root)

    for f in files:
        file_path = os.path.join(root,f)

        if os.path.isdir(file_path):
            add_license(file_path, text)
        else:
            _,ext = os.path.splitext(f)
            if ext in extensions:
                license = process_license(text, ext)

                with open(file_path, "r+") as f:
                    firstline = f.readline()
                    if DO_NOT_ADD_LICENSE_MARKER in firstline.upper():
                        old = f.read()
                        f.close()
                        with open(file_path, 'w') as f:
                            f.write(old)
                        continue    #avoid any problems of reusing the f var
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

def get_leaves(nodes, separator='/'):
    leaves = []
    
    while nodes:
        node = nodes.pop(0)
        if filter(lambda x : x.startswith(node+separator), nodes):
            continue
        leaves.append(node)
    
    return leaves
