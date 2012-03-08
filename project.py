from dist_creator import *
import filecmp
import os

FOLDER_SEPARATOR = os.sep

def split_path(full_filename):
    return (FOLDER_SEPARATORfull_filename.split(FOLDER_SEPARATOR)[:-1], 
            full_filename.split(FOLDER_SEPARATOR)[-1])


class Project(object):

    def __init__(self,source_path):

        self.items = get_files(source_path)
        self.source_path = source_path
        self.change_profile = {} 

    def add_change(self, full_filename, new_name):

        change_profile = {full_filename:new_name}

        self.change_profile.update(change_profile)

    def set_copy_lacation(self,path):
        pass

    def create_new_copy(self):
        pass

    def update_copy(self):
        """ Update copy using svn wrapper.
            It allows the code to scan just through modifyied files
        """
        pass

    def hard_update_copy(self):
        """ Update copy scanning ALL files
            It takes a longer time to run
        """
        # filecmp.cmp can help here
        pass

