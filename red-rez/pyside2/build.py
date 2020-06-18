import os
import sys
import shutil
from distutils.dir_util import copy_tree

print("Running build.py...")
root = os.path.dirname(__file__).replace("\\","/")
print(root)
print(sys.argv[1])
rezconfig_file = os.path.join(os.environ["REZ_CONFIG_FILE"],"rezconfig.py")
local_packages_dir = release_packages_dir = None
with open(rezconfig_file, 'r') as rezconfig:
    # Read all lines in the file one by one
    for line in rezconfig:
        if "local_packages_path =" in line:
            local_packages_dir = line.split(" = ")[1].strip("\n\"").replace("\\","/")
            print(local_packages_dir)
            
        if "release_packages_path =" in line:
            release_packages_dir = line.split(" = ")[1].strip("\n\"").replace("\\","/")
            print(release_packages_dir)

"""print("Copying package payload to %s.." % build_dir)
shutil.copytree(
    os.path.join(root, "payload"),
    os.path.join(build_dir, "pyside2")
)"""

if int(os.getenv("REZ_BUILD_INSTALL")):
    # This part is called with `rez build --install`
    print("Installing payload to %s..." % local_packages_dir)
    copy_tree(
        os.path.join(root, "payload"),
        os.path.join(local_packages_dir, "pyside2", sys.argv[1])
    )