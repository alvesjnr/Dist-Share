from dist_creator import *
import filecmp
import os
import shutil
import git

FOLDER_SEPARATOR = os.sep

def split_path(full_filename):
    return (FOLDER_SEPARATOR.join(full_filename.split(FOLDER_SEPARATOR)[:-1]),
            full_filename.split(FOLDER_SEPARATOR)[-1])


class Project(object):

    def __init__(self,source_path, license=None):

        self.items = get_files(source_path)
        self.source_path = source_path
        self.change_profile = {}
        self.avoided_files = []
        self.license = license

    def unavoid_file(self, full_filename):
        files_to_unavoid = []
        for item in self.avoided_files:
            if item.startswith(full_filename):
                files_to_unavoid.append(item)

        for item in files_to_unavoid:
            self.avoided_files.remove(item)

    def avoid_file(self, full_filename):
        if not full_filename in self.avoided_files:
            self.avoided_files.append(full_filename)
        for item in self.items:
            if item.startswith(full_filename) and item not in self.avoided_files:
                self.avoided_files.append(item)

    def add_change(self, full_filename, new_name):
        change_profile = {full_filename:new_name}
        self.change_profile.update(change_profile)

    def set_copy_location(self,path):
        self.copy_location = path
        _,self.project_name = split_path(path)

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
                if self.license:
                    add_license(copy_target,self.license)

        self.repo = git.Repo.init(self.source_path)
        # add files to repo
        # self.repo.commit('First commit of the project %s' % self.project_name)

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

    def update_copy(self, changed_files):
        """ Update copy using svn wrapper.
            It allows the code to scan just through modifyied files
        """
        updated_items = get_files(self.source_path)
        removed_items = [item for item in self.items if item not in updated_items]
        self.items = updated_items

        for item in self.avoided_files:
            self.remove_file(item)

        for item in self.items:
            if not os.path.exists(self.get_copy_path(item)) and item not in self.avoided_files:
                self.copy_new_file(item)

        for item in changed_files:
            self.update_file(item)

    def remove_file(self,origin_file_path):
        """ get the origen file path and remove this file from copy
        """
        filepath = self.get_copy_path(origin_file_path)
        if os.path.exists(filepath):
            if os.path.isfile(filepath):
                os.remove(filepath)
            else:
                shutil.rmtree(filepath)

    def get_copy_path(self,origin_path):
        """ get the origin file path and return its copy equivalent
        """
        if origin_path in self.change_profile:
            copy_name = self.get_new_filename(origin_path)
        else:
            copy_name = origin_path
        relative_file_path = self.get_relative_path(copy_name)

        if relative_file_path.startswith(FOLDER_SEPARATOR):
            relative_file_path = relative_file_path.replace(FOLDER_SEPARATOR,'',1)

        return os.path.join(self.copy_location,relative_file_path)

    def copy_new_file(self,filename):
        copy_name = self.get_copy_path(filename)
        path,name = split_path(copy_name)
        if os.path.isdir(filename):
            if not os.path.exists(copy_name):
                os.makedirs(copy_name)
        else:
            if not os.path.exists(path):
                os.makedirs(path)
            shutil.copy2(filename,copy_name)
            if self.license:
                add_license(copy_name,self.license)

    def update_file(self,filename):
        """ use it to update a file that already exists!!!
        """
        copy_name = self.get_copy_name(filename)
        os.remove(copy_name)
        os.shutil.copy2(filename,copy_name)
        if self.license:
            add_license(copy_name,self.license)
