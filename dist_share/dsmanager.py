
import sys
import pickle
import argparse

from project import Project


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dist_file", help="The Dist Share file")
    parser.add_argument("command", help="clone-copy, delete-copy, create-copy")
    parser.add_argument("-y","--copy_name", help="The name of your copy")
    parser.add_argument("-n","--clone_name", help="The name of the copy clone")
    return parser.parse_args()


def main():
    args = _parse_args()
    
    if args.command == 'clone_copy':
        copy_name = args.copy_name
        clone_name = args.clone_name

        if not copy_name or not clone_name:
            raise Exception("For command clone_copy you must provide both a copy name and a clone name.")

        clone_copy(args.dist_file, copy_name, clone_name)


def clone_copy(dist_file,copy_name,clone_name,license=None):

    with open(dist_file) as f:
        project_dict = pickle.loads(f.read())
    
    project = Project(dumped_project=project_dict['project'])
    project = project.clone_copy(copy_name,clone_name)
    project_dict['project'] = project.dumps()

    with open(dist_file,'w') as f:
        f.write(pickle.dumps(project_dict))


if __name__ == '__main__':
    main()
