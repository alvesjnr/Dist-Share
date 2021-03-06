from project import Project, CopiesManager, Copy, DupllicatedCopyNameException
from functions import get_files
import unittest
import filecmp
import os
import pickle
import StringIO

ORIGIN_PROJECT = '/tmp/dist_project'


def compare_tree(left,right):
    """ compare two different files tree """

    on_left = [f.replace(left,'',1) for f in get_files(left)]
    on_right = [f.replace(right,'',1) for f in get_files(right)]

    right_only = [f for f in on_right if f not in on_left and '.git' not in f and '.svn' not in f and 'COPY.info' not in f]
    left_only = [f for f in on_left if f not in on_right and '.git' not in f and '.svn' not in f and 'COPY.info' not in f]

    return {'right_only':right_only, 'left_only':left_only}


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
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_create_new_copy_avoiding_file(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')

        p.avoided_files.append(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only'] == ['/extending/setup.py'])

    def test_create_new_copy_modifying_file_name(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'] and 
                        diff['right_only']==['/extending/Setup.py'])

    def test_add_and_remove_file(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        p.avoid_file(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'])
        p.unavoid_file(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_modify_file_content(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        os.system('echo "hola" > /tmp/dist_project/extending/setup.py')
        p.update_copy(['/tmp/dist_project/extending/setup.py'])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        with open('/tmp/dist_project/extending/setup.py') as f:
            file_content = f.read()
            self.assertTrue(file_content=='hola\n')

    def test_modify_file_name_twice(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'] and 
                        diff['right_only']==['/extending/Setup.py'])
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'SETUP.py')
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'] and 
                        diff['right_only']==['/extending/SETUP.py'])

    def test_modify_file_name_several_times(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        p.create_new_copy()
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'Setup.py')
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['right_only'] == ['/extending/Setup.py'] and diff['left_only'] == ['/extending/setup.py'])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'] and 
                        diff['right_only']==['/extending/Setup.py'])
        p.add_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'),'SETUP.py')
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertTrue(diff['left_only']==['/extending/setup.py'] and 
                        diff['right_only']==['/extending/SETUP.py'])
        p.remove_change(os.path.join(ORIGIN_PROJECT,'extending/setup.py'))
        p.update_copy([])
        diff = compare_tree(ORIGIN_PROJECT,'/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_adding_license(self):
        p = Copy(ORIGIN_PROJECT)
        p.set_copy_location('/tmp/blah')
        license = "this is a test license"
        p.license = license
        p.create_new_copy()
        with open('/tmp/blah/example/setup.py') as f:
            file_content = f.readline()
            self.assertTrue(license in file_content)


class ProjectTest(unittest.TestCase):

    def setUp(self):
        if os.path.exists('/tmp/test_place'):
            os.system('rm -rf /tmp/test_place')
        if os.path.exists('/tmp/blah'):
            os.system('rm -rf /tmp/blah')
        if os.path.exists('/tmp/blah2'):
            os.system('rm -rf /tmp/blah2')
        try:
            os.system('rm -rf /tmp/workspace/svnrepo/temp')
        except: pass
        try:
            os.system('svn rm /tmp/workspace/svnrepo/temp')
        except: pass
        try:
            os.system('svn commit /tmp/workspace/svnrepo -m "removing"')
        except: pass

    def test_create_new_project(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        diff = compare_tree('/tmp/workspace/svnrepo','/tmp/test_place')        
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_create_one_copy(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_update_copy(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        os.system('date > /tmp/workspace/svnrepo/nha.c')
        os.system('date +%N >> /tmp/workspace/svnrepo/nha.c')
        os.system('svn commit /tmp/workspace/svnrepo/nha.c -m "changing things in repo"')
        self.assertFalse(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        p.update_project()
        p.update_copies()
        self.assertTrue(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))

    def test_update_copy_removing_file(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.update_project()
        p.update_copies()
        p.avoid_files(['/tmp/test_place/nha.c'])
        p.update_project()
        p.update_copies()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])

    def test_removing_file_from_svn_repository(self):
        os.system('echo "blahblahblah" > /tmp/workspace/svnrepo/temp')
        os.system('svn add /tmp/workspace/svnrepo/temp')
        os.system('svn commit /tmp/workspace/svnrepo/temp -m "adding in repo"')
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.update_project()
        p.update_copies()
        diff = compare_tree('/tmp/workspace/svnrepo','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        os.system('rm /tmp/workspace/svnrepo/temp')
        os.system('svn rm /tmp/workspace/svnrepo/temp')
        os.system('svn commit /tmp/workspace/svnrepo -m "removing in repo"')
        p.update_project()
        diff = compare_tree('/tmp/workspace/svnrepo','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_managing_two_copies(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.add_new_copy('/tmp/blah2')
        p.avoid_files(['/tmp/test_place/nha.c'])
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])

    def test_two_copies_with_same_name(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah',name='copy')
        p.create_current_copy()
        self.assertRaises(DupllicatedCopyNameException,p.add_new_copy,*('/tmp/blah2','copy'))
        p.add_new_copy('/tmp/blah2','copy2')
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertFalse(diff['left_only'] or diff['right_only'])

    def test_updating_two_copies(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.add_new_copy('/tmp/blah2')
        p.avoid_files(['/tmp/test_place/nuca'])
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nuca','/nuca/suco'] and diff['right_only'] == [])
        os.system('date > /tmp/workspace/svnrepo/nha.c')
        os.system('date +%N >> /tmp/workspace/svnrepo/nha.c')
        os.system('svn commit /tmp/workspace/svnrepo/nha.c -m "changing things in repo"')
        self.assertFalse(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        self.assertFalse(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah2/nha.c'))
        p.update_project()
        p.update_copies()
        self.assertTrue(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        self.assertTrue(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah2/nha.c'))

    def test_updating_file_that_is_not_on_copy(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.add_new_copy('/tmp/blah2')
        p.avoid_files(['/tmp/test_place/nha.c'])
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])
        os.system('date > /tmp/workspace/svnrepo/nha.c')
        os.system('date +%N >> /tmp/workspace/svnrepo/nha.c')
        os.system('svn commit /tmp/workspace/svnrepo/nha.c -m "changing things in repo"')
        self.assertFalse(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        p.update_project()
        p.update_copies()
        self.assertTrue(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])

    def test_renaming_file_with_svn_move(self):
        p = Project(path='/tmp/test_place', url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        os.system('svn mv /tmp/workspace/svnrepo/nha.c /tmp/workspace/svnrepo/nha_2.c')
        os.system('svn commit /tmp/workspace/svnrepo -m "changing name"')
        p.update_project()
        p.update_copies()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertTrue(diff['left_only'] == ['/nha_2.c'] and diff['right_only'] == [])
        os.system('svn mv /tmp/workspace/svnrepo/nha_2.c /tmp/workspace/svnrepo/nha.c')
        os.system('svn commit /tmp/workspace/svnrepo -m "restoring old name"')
        p.update_project()
        p.update_copies()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])

    def test_persist_project(self):
        p = Project(path='/tmp/test_place',url='svn://alvesjnr@localhost/tmp/svnrepo')
        p.add_new_copy('/tmp/blah')
        p.create_current_copy()
        p.add_new_copy('/tmp/blah2')
        p.avoid_files(['/tmp/test_place/nha.c'])
        p.create_current_copy()
        diff = compare_tree('/tmp/test_place','/tmp/blah')
        self.assertFalse(diff['left_only'] or diff['right_only'])
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])
        os.system('date > /tmp/workspace/svnrepo/nha.c')
        os.system('date +%N >> /tmp/workspace/svnrepo/nha.c')
        os.system('svn commit /tmp/workspace/svnrepo/nha.c -m "changing things in repo"')
        self.assertFalse(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))

        dumped_project = p.dumps()
        del(p)
        p = Project(dumped_project=dumped_project)

        p.update_project()
        p.update_copies()
        self.assertTrue(filecmp.cmp('/tmp/workspace/svnrepo/nha.c','/tmp/blah/nha.c'))
        diff = compare_tree('/tmp/test_place','/tmp/blah2')
        self.assertTrue(diff['left_only'] == ['/nha.c'] and diff['right_only'] == [])

if __name__ == '__main__':
    unittest.main()

