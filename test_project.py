from project import Project, CopiesManager, Copy
from dist_creator import get_files
import unittest
import filecmp
import os

ORIGIN_PROJECT = '/tmp/dist_project'


def compare_tree(left,right):
    """ compare two different files tree """

    on_left = [f.replace(left,'',1) for f in get_files(left)]
    on_right = [f.replace(right,'',1) for f in get_files(right)]

    just_on_right = [f for f in on_right if f not in on_left and '/.git/' not in f]
    just_on_left = [f for f in on_left if f not in on_right and '/.git/' not in f]

    return {'just_on_right':just_on_right, 'just_on_left':just_on_left}


class CopyTest(unittest.TestCase):

    def setUp(self):
        os.system('rm -rf /tmp/blah')
        os.system('mkdir /tmp/blah')
        os.system('rm -rf /tmp/dist_project')
        os.system('cp -r ~/Projects/dist_project /tmp/dist_project')

    def test_create_new_copy(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['just_on_left'] or diff['just_on_right'])

    def test_create_new_copy_avoiding_file(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')

        p.avoided_files.append(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['just_on_left'] == ['/extending/setup.py'])

    def test_create_new_copy_modifying_file_name(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['just_on_left']==['/extending/setup.py'] and 
                        diff['just_on_right']==['/extending/Setup.py'])

    def test_add_and_remove_file(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        p.avoid_file(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['just_on_left']==['/extending/setup.py'])
        p.unavoid_file(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['just_on_left'] or diff['just_on_right'])

    def test_modify_file_content(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        os.system('echo "hola" > /tmp/dist_project/extending/setup.py')
        p.update_copy(['/tmp/dist_project/extending/setup.py'])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['just_on_left'] or diff['just_on_right'])
        with open('/tmp/dist_project/extending/setup.py') as f:
            file_content = f.read()
            self.assertTrue(file_content=='hola\n')

    def test_modify_file_name_twice(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['just_on_left']==['/extending/setup.py'] and 
                        diff['just_on_right']==['/extending/Setup.py'])
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'SETUP.py')
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['just_on_left']==['/extending/setup.py'] and 
                        diff['just_on_right']==['/extending/SETUP.py'])


if __name__ == '__main__':
    unittest.main()

