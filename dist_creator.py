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
            '.hpp':{'begin':'/*', 'end':'*/'},
            }
extensions = [key for key in comments]
DO_NOT_ADD_LICENSE_MARKER = 'DO NOT ADD LICENSE'


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
        tkMessageBox.showwarning(message='This file already exists\nChoose a different name')
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
                    raise e


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
                            f.write(license+"\n" + old)
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


def process_packages(raw_packages, origin_path):
    
    original_packages = get_flat_packages(origin_path)
    processed_packages = []

    for i in raw_packages:
        i = i.strip()
        if i and i[0] != '#':
            if i in original_packages:
                processed_packages.append(i)

    return processed_packages
    
        
def process_copy(origin_path, target_path, packages, raw_license):

    processed_packages = process_packages(packages, origin_path)

    if processed_packages:
                
        try:
            create_copy(origin_path, target_path, processed_packages)
        except CreateCopyError as e:
            sys.stderr.write(e.message)
            tkMessageBox.showinfo(message='It was not possible to create the project copy')
            return False
        
        add_license(target_path, raw_license)

        return True

