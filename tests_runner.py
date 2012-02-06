import os

TESTSUITE_PACKAGE_NAME = "testsuite"

def list_tests_from_directory(root, test_files=[]):
    """ List all tests *.py file. *.pyc files are NOT listed """
    files = os.listdir(root)

    for f in files:
        if os.path.isdir(os.path.join(root,f)):
            #I'm passing a reference of my old list, so the new files will be just appended to the list
            list_tests_from_directory(os.path.join(root,f), test_files)
        else:
            #TODO: heuristic to decide which file is a test must be imporved!
            if 'test' in f and f.endswith('py'):                
                test_files.append(os.path.join(root,f))
    
    return test_files


if __name__=='__main__':
    from pprint import pprint as pp
    pp(list_tests_from_directory('/tmp/new_distribution_name'))