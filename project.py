from dist_creator import *

import os

FOLDER_SEPARATOR = os.sep

def split_path(full_filename):
    return (FOLDER_SEPARATORfull_filename.split(FOLDER_SEPARATOR)[:-1], 
            full_filename.split(FOLDER_SEPARATOR)[-1])


class Project(object):

    def __init__(self,source_path, items):


    	self.items = items
    	self.source_path = source_path
        self.change_profile = []

    def add_change(self, full_filename, new_name):

        path,original_name = split_path(full_filename)

        change_profile = {'original_name':original_name,
                          'path':path,
                          'new_name':new_name}
        self.change_profile.append(change_profile)

    def copy(self):
    	pass