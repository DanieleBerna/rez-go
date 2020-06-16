import os
import subprocess
import re
import zipfile
name = "blender"
_VERSION_ENV_KEY = "BLENDER_RESOLVED_BUILD_VERSION"
@early()
def version():
    """
    This function actually does the entire extraction of the package etc..
    :return: the version string
    """
    # If we've already run this, then don't run it again
    blender_ver = os.getenv(_VERSION_ENV_KEY)
    blender_ver = "2.83"
    if blender_ver:
        return blender_ver
    print("Calculating Blender version from zip")
    this_dir = os.getcwd() # Rez execs this file so there's no reference to this directory at this time.
    package_dir = os.path.join(this_dir, "windows64")
    payload_dir = os.path.join(package_dir, 'payload')
    
    # Make sure the necessary directories exist
    for path in (payload_dir, package_dir):
        if not os.path.exists(path):
            raise IOError("Failed to find: {}".format(path))
    # Make sure the blender zip file exists
    payloads = [p for p in os.listdir(payload_dir) if p.lower() == "blender.zip"]
    if not payloads:
        raise IOError("Failed to find Blender.zip payload")
    archive = zipfile.ZipFile(os.path.join(payload_dir, payloads[0]))
    info_plist = archive.read(os.path.join('Blender.app', 'Contents', 'Info.plist'))
    match = re.search("<string>(.*), Blender Foundation</string>", info_plist)
    ver = match.groups()[0].replace(' ', '.').replace('-', '.')
    # Add a suffix if provided
    import sys
    if '--suffix' in sys.argv:
        idx = sys.argv.index('--suffix')
        ver += ".{}".format(sys.argv[idx+1])
    
    # Cache this value in the environment variables so we don't run this all over again unnecesarily 
    os.environ[_VERSION_ENV_KEY] = ver
    return ver
def commands():
    #print(system.platform)
    #if system.platform == 'osx':
    env.PATH.append("{root}/blender")
        #env.BLENDER_BOOTSTRAP.set("{root}/osx/bootstrap.py")
build_command = "py {root}/build.py"