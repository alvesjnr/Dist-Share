from dist_creator import *
import filecmp
import os
import shutil

FOLDER_SEPARATOR = os.sep

def split_path(full_filename):
    return (FOLDER_SEPARATOR.join(full_filename.split(FOLDER_SEPARATOR)[:-1]),
            full_filename.split(FOLDER_SEPARATOR)[-1])


class Project(object):

    def __init__(self,source_path):

        self.items = get_files(source_path)
        self.source_path = source_path
        self.change_profile = {} 
        self.avoided_files = []

    def avoid_file(self, full_filename):
        if not full_filename in self.avoided_files:
            self.avoided_files.append(full_filename)
        for item in self.items:
            if item.startswith(full_filename) and item not in self.avoided_files:
                self.avoided_files.append(item)

    def add_file(self, full_filename):
        if full_filename in self.avoided_files:
            self.avoided_files.remove(full_filename)
        for item in self.avoided_files:
            if item.startswith(full_filename):
                self.avoided_files.remove(item)

    def add_change(self, full_filename, new_name):
        change_profile = {full_filename:new_name}
        self.change_profile.update(change_profile)

    def set_copy_location(self,path):
        self.copy_location = path

    def create_new_copy(self):
        self.create_directories_struct()
        for item in self.items:
            if item in self.avoided_files:
                continue
            if os.path.isfile(item):
                if item in self.change_profile:
                    copy_name = self.get_new_filename(item)
                else:
                    copy_name = item
                relative_item_path = self.get_relative_path(copy_name)
                copy_target = os.path.join(self.copy_location,relative_item_path)

                shutil.copy2(item,copy_target)

    def create_directories_struct(self):
        for item in self.items:
            if os.path.isdir(item) and item not in self.avoided_files:
                if item in self.change_profile:
                    item = self.get_new_filename(item)
                relative_path = self.get_relative_path(item)
                copy_target = os.path.join(self.copy_location,relative_path)

                if not os.path.exists(copy_target):
                    os.mkdir(copy_target)

    def get_relative_path(self, path):
        """ Returns the relative path over the self.source_path
        """
        relative_item_path = path.replace(self.source_path,'',1)
        if relative_item_path.startswith(FOLDER_SEPARATOR):
            relative_item_path = relative_item_path.replace(FOLDER_SEPARATOR,'',1)

        return relative_item_path

    def get_new_filename(self,full_filename):
        if full_filename in self.change_profile:
            path,name = split_path(full_filename)
            new_name = self.change_profile[full_filename]
            return os.path.join(path,new_name)
        else:
            return full_filename

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

