import subprocess
import os

def is_svn_repo(path):
    #TODO: imporove those heuristic. It is too much weak!
    return os.path.isdir(os.path.join(path, '.svn'))

def get_svn_committers(path):
    command = """svn log %s -q | awk -F '|' '/^r/ {sub("^ ", "", $2); sub(" $", "", $2); print $2" = "$2" <"$2">"}' | sort -u"""
    command = command % path
    import pdb; pdb.set_trace()
    subprocess.call(command)