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

