from project import Project
origin = '/tmp/dist_project'
destin = '/tmp/blah'
import os
os.mkdir(destin)
p = Project(origin)
p.set_copy_location(destin)
p.create_new_copy()
p.avoid_file('/tmp/dist_project/extending/src')
p.update_copy([])
p.unavoid_file('/tmp/dist_project/extending/src')
p.update_copy([])

