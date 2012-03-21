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
SVN_MARKER = os.path.join(FOLDER_SEPARATOR,'.svn')
SPACE = '%20'


def split_path(full_filename):
    return (FOLDER_SEPARATOR.join(full_filename.split(FOLDER_SEPARATOR)[:-1]),
            full_filename.split(FOLDER_SEPARATOR)[-1])


class CreateCopyError(Exception):
    """Something wrong when copying"""
    message="Something wrong when copying"


def get_files(root,files=None):
    if files is None:
        files = []

    files_here = [os.path.join(root,filename) for filename in os.listdir(root)]

    files += files_here

    for f in files_here:
        if os.path.isdir(f) and not SVN_MARKER in f:
            files = get_files(f,files)

    return files


def add_license(filepath, text):

    _,ext = os.path.splitext(filepath)
    if ext in extensions:
        license = process_license(text, ext)
    else:
        return  # If the extension is not listed, we don't apply the license

    with open(filepath, "r+") as f:
        firstline = f.readline()
        if DO_NOT_ADD_LICENSE_MARKER in firstline.upper():
            old = f.read()
            f.close()
            with open(filepath, 'w') as f:
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


def normalize_items(items):
    """ This function gets a list os directories and add the initial path:
        input: ['/a/b/c', '/a/b/d', '/a/d/j']
        output: ['a', 'a/b', 'a/b/c', 'a/b/d', 'a/d/j']
    """
    if not items:
        return []

    first_entry = items[0].split(FOLDER_SEPARATOR)

    list_head = []
    for i in range(len(first_entry)):
        entry = FOLDER_SEPARATOR.join(first_entry[:i+1])
        if entry:
            if entry.startswith(FOLDER_SEPARATOR):
                entry = entry.replace(FOLDER_SEPARATOR,'',1)
            list_head.append(entry)

    list_tail = []
    for i in items[1:]:
        if i.startswith(FOLDER_SEPARATOR):
            i = i.replace(FOLDER_SEPARATOR,'',1)
            list_tail.append(i)

    return list_head + list_tail


def format_log_message(log):

    message = ''
    
    if log['A']: 
        message += "Added files:\n%s\n\n" % '\n    '.join(log['A'])
    if log['U']: 
        message += "Updated Files:\n%s\n\n" % '\n    '.join(log['U'])
    if log['D']: 
        message += "Removed Files:\n%s\n\n" % '\n    '.join(log['D'])

    return message
