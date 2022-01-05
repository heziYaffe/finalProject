import os


def create_dir_in_path(p, dir_name):
    # Directory
    directory = dir_name


    # Parent Directory path
    parent_dir = p

    # Path
    path = os.path.join(parent_dir, directory)

    # Create the directory if dosent exist
    if not os.path.exists(path):
        os.makedirs(path)
    print("Directory '% s' created" % directory)