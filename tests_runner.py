# -*- coding: utf-8 -*-

import subprocess
from StringIO import StringIO
import traceback    
import sys
import os
import unittest
import pkgutil
import imp
import time

TESTSUITE_PACKAGE_NAME = "testsuite"

def is_a_testfile(f):
    #TODO: heuristic to decide which file is a test must be imporved!
    return 'test' in f and f.endswith('py')

def list_tests_from_directory(root, test_files=[]):
    """ List all tests *.py file. *.pyc files are NOT listed """
    files = os.listdir(root)

    for f in files:
        if os.path.isdir(os.path.join(root,f)):
            #I'm passing a reference of my list, so the new files will be just appended to the list
            list_tests_from_directory(os.path.join(root,f), test_files)
        else:
            if is_a_testfile(f):    
                test_files.append(os.path.join(root,f))
    
    return test_files


def run_tests(test_files):
    
    filename = '/tmp/dist_share%s' % time.time()
    with open(filename, 'w') as stdio:
        for f in test_files:
            try:
                stdio.flush()
                stdio.write('Processing test file %s\n' % f)        
                stdio.flush()
                subprocess.call('python ' + f, stderr=stdio, shell=True)
                stdio.flush()
                stdio.write('End of file %s\n\n' % f)
            except Exception, e:
                traceback.print_exc()
    with open(filename, 'r') as stdio:
        return stdio.read()
