from project import Project, CopiesManager, Copy
import unittest
import filecmp
import os

ORIGIN_PROJECT = '/home/antonio/Projects/dist_project'

class ProjectTest(unittest.TestCase):

    def setUp(self):
        os.system('rm -rf /tmp/blah')
        os.system('mkdir /tmp/blah')

    def test_create_new_copy(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        #p.create_new_copy()
        cmp = filecmp.dircmp(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(cmp.left_only or cmp.right_only)

    def test_create_new_copy_avoiding_file(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')

        p.avoided_files.append(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        #p.create_new_copy()
        cmp = filecmp.dircmp(ORIGIN_PROJECT,'/tmp/blah')
        print cmp.left_only
        print cmp.right_only
        self.assertTrue(cmp.left_only == [])

    def test_create_new_copy_modifying_file_name(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')

        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.create_new_copy()


if __name__ == '__main__':
    unittest.main()

