import os
from distutils.dir_util import copy_tree

rezconfig_file = os.path.join(os.environ["REZ_CONFIG_FILE"])

# Open the file in read only mode
build_dir = install_dir = None
with open(rezconfig_file, 'r') as rezconfig:
    # Read all lines in the file one by one
    for line in rezconfig:
        # For each line, check if line contains the string
        if "local_packages_path =" in line:
            build_dir = line.split(" = ")[1]
        if "release_packages_path =" in line:
            install_dir = line.split(" = ")[1]


