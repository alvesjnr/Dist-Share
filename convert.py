import subprocess
import time
import os

from StringIO import StringIO

def is_svn_repo(path):
    #TODO: improve those heuristic. It is too much weak!
    return os.path.isdir(os.path.join(path, '.svn'))

def get_svn_committers(path):
    command = """svn log %s -q | awk -F '|' '/^r/ {sub("^ ", "", $2); sub(" $", "", $2); print $2" = "$2" <"$2">"}' | sort -u"""
    command = command % path

    filename = '/tmp/dist_share%s' % time.time()
    with open(filename, 'w') as stdio:
        subprocess.call(command, shell=True, stdout=stdio, stderr=stdio)
    
    with open(filename, 'r') as stdio:
        output = stdio.read()
    
    os.system('rm %s' % filename)
    return output