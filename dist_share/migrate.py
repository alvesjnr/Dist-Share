
import git
import pysvn
import os
from project import *

EXEC_PATH = os.path.abspath('.')
PREVIOUS_PATH = None
PREVIOUS_ORIGINAL_PATH = None
CURRENT_ORIGINAL_PATH = os.path.join(EXEC_PATH, 'original')


def migrate_copy(copy):
    copy.copy_location = os.path.join(EXEC_PATH,copy.copy_name)
    os.mkdir(os.path.join(EXEC_PATH,copy.copy_name))
    copy.items = [f.replace(PREVIOUS_PATH,EXEC_PATH) for f in copy.items]
    copy.avoided_files = [f.replace(PREVIOUS_ORIGINAL_PATH,CURRENT_ORIGINAL_PATH) for f in copy.avoided_files]
    copy.removed_files = [f.replace(PREVIOUS_PATH,EXEC_PATH) for f in copy.removed_files]
    copy.source_path = CURRENT_ORIGINAL_PATH


def migrate_project(dumped_project):

    project = Project(dumped_project=dumped_project)
    os.mkdir(CURRENT_ORIGINAL_PATH)
    project.project_items = [f.replace(PREVIOUS_ORIGINAL_PATH,CURRENT_ORIGINAL_PATH) for f in project.project_items]
    project.path = CURRENT_ORIGINAL_PATH
    for copy in project.copies_manager.copies:
        migrate_copy(copy)
    return project


def get_login(realm, username, may_save):
    username = raw_input('username: ')
    password = raw_input('password: ')
    return bool(username and password), username, password, False


def clone_original(project):
    client = pysvn.Client()
    client.callback_get_login = get_login
    client.checkout(project.url,CURRENT_ORIGINAL_PATH)


def clone_copies(project):
    g = git.Git()
    for copy in project.copies_manager.copies:
        if copy.remote_url:
            g.clone(copy.remote, copy.copy_path)
        else:
            copy.create_new_copy()


if __name__=='__main__':
    
    global PREVIOUS_PATH
    global PREVIOUS_ORIGINAL_PATH

    project_file = pickle.load(open(sys.argv[1]))
    dumped_project = project_file['project']

    PREVIOUS_PATH = os.path.dirname(project_file['path'])
    PREVIOUS_ORIGINAL_PATH = os.path.join(PREVIOUS_PATH,'original')

    project = migrate_project(dumped_project)
    clone_original(project)
    clone_copies(project)

    dumped_project = project.dumps()

    pickle.dump({'path':os.path.join(EXEC_PATH, sys.argv[1]), 'project':dumped_project},open(sys.argv[1],'w'))
