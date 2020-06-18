from urllib import request
from shutil import copyfile
from subprocess import call, run
import os
import re
import zipfile
import fileinput

_EMBEDDABLE_PYTHON_URL = "https://www.python.org/ftp/python/"  # URL for python releases download
_DEFAULT_PYTHON_VERSION = "3.7.4"
_DEFAULT_INSTALL_FOLDER = r"T:/"
_UGCORE_DIR = "ugcore"


def hack_rezconfig_file(filepath, local_packages_folder, release_packages_folder, restore=False):
    """
    Replace rez packages paths inside base rezconfig.py file with custom ones and restore original settings.
    This is just a temporary hack since for some reason bleeding-rez seems to ignore rezconfig.py override at first
    run.
    :param filepath: complete path and filename of the default and primary rezconfig.py file
    :param local_packages_folder: destination folder of local packages
    :param release_packages_folder: destination folder for released packages
    :param restore: boolean flag for resetting paths to default ~/packages folder
    :return:
    """
    try:
        if not restore:
            for line in fileinput.input(filepath, inplace=1):
                print(line.replace("~/packages", local_packages_folder).rstrip())

            for line in fileinput.input(filepath, inplace=1):
                print(line.replace("~/.rez/packages", release_packages_folder).rstrip())
        else:
            for line in fileinput.input(filepath, inplace=1):
                print(line.replace(local_packages_folder, "~/packages").rstrip())

            for line in fileinput.input(filepath, inplace=1):
                print(line.replace(release_packages_folder, "~/.rez/packages").rstrip())
    except IOError as e:
        print(f"Error while hacking rezconfig.py file\n{e}")
        return False
    return True


def create_python_pakage_file(interpreter_folder, version):
    """
    Create a package.py file used to re-bind an embedded interpreter
    :param interpreter_folder: folder of the python.exe file
    :param version: Python (and package) version
    """
    try:
        package_build_file = open(os.path.join(interpreter_folder, "package.py"), "w+")
        package_build_file.write(f"import os\n\nname = 'python'\nversion = '{version}'\nbuild_command = False\n\n@early()\n"
                                 f"def _bin_path():\n\treturn os.getcwd()\n\ndef commands():\n\tglobal env\n\t"
                                 f"env['PATH'].prepend('{{this._bin_path}}')")
        package_build_file.close()
    except IOError as e:
        print(f"Error while writing package.py file for Python interpreter\n{e}")
        return False
    return True


print(f"RED REZ - Redistributable rez installer\n")

""" The pipeline uses an embedded light Python3 version to install and then run rez.
A valid Python version is here required.
Script defaults to 3.7.4 64bit version if nothing is provided."""

python_version = input(f"Python version ({_DEFAULT_PYTHON_VERSION}): ") or _DEFAULT_PYTHON_VERSION
if re.match("3.[0-9].[0-9]", python_version) is None:
    print(f"{python_version} is not a valid Python version")
    exit()

system = input("OS architecture (64bit): ") or "64"
if system == "32":
    system = "win32"
elif system == "64":
    system = "amd64"
else:
    print(f"{system} is not a valid OS architecture")
    exit()

""" The pipeline requires all tools to be installed in a local folder that is then remapped to a previously agreed unit.
Script defaults to user's home directory if nothing is provided."""

install_folder = input("Install folder (T:/): ") or r"T:/"
if not os.path.exists(install_folder):
    print(f"Install folder {install_folder} doesn't exists")
    exit()

remap_to = input("Remap folder to a new unit (no)? ") or False
if remap_to:
    try:
        remap_to = remap_to.upper()
        call("subst " + remap_to.upper()+": "+install_folder)
        print(f"{install_folder} is remapped to {remap_to} unit")
        install_folder = remap_to+":\\"
    except:
        print(f"An error has occurred while remapping {install_folder} to {remap_to} unit")
        exit()

"""Embeddable Python download and unpacking."""
python_zip_filename = f"python-{python_version}-embed-{system}.zip"
if not os.path.exists(python_zip_filename):  # Download required embeddable python if not present in script folder
    download_url = f"{_EMBEDDABLE_PYTHON_URL}{python_version}/{python_zip_filename}"
    print(f"Downloading embeddable Python from: {download_url}")
    try:
        with request.urlopen(download_url) as response, open(python_zip_filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except:
        print(f"An error has occurred while downloading {python_zip_filename}")
        exit()
embedded_python_folder = os.path.join(install_folder, _UGCORE_DIR, "python")
with zipfile.ZipFile(python_zip_filename, 'r') as zip_ref:
    zip_ref.extractall(embedded_python_folder)
    zip_ref.close()

""" pythonXX._pth needs to be edited uncommenting the import site line"""
pythonXX = "python"+python_version.split(".")[0]+python_version.split(".")[1]
for line in fileinput.input(os.path.join(embedded_python_folder, pythonXX+"._pth"), inplace=1):
    print(line.replace("#import site", "import site").rstrip())

""" Pip needs to be added to the interpreter """
getpip_filename = os.path.join(embedded_python_folder, "get-pip.py")
if not os.path.exists("get-pip.py"):  # Download get-pip.py if not present in script folder
    download_url = "https://bootstrap.pypa.io/get-pip.py"
    print(f"Downloading get-pip.py from: {download_url}")
    try:
        with request.urlopen(download_url) as response, open("get-pip.py", 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except:
        print(f"An error has occurred while downloading get-pip.py")
        exit()
try:
    copyfile("get-pip.py", getpip_filename)
except IOError as e:
    print(f"An error has occurred while copying get-pip.py")
    print(e)
    exit()
call(os.path.join(embedded_python_folder, "python.exe") + " " + os.path.join(embedded_python_folder, "get-pip.py --no-warn-script-location"))

"""Download and install of bleeding-rex using pip"""
call(os.path.join(embedded_python_folder, "Scripts", "pip") + " install bleeding-rez --no-warn-script-location")

rez_folder = os.path.join(install_folder, _UGCORE_DIR, "rez")
if not os.path.exists(rez_folder):
    os.makedirs(rez_folder)

include_file = False
if include_file:
    rez_config_filename = os.path.join(rez_folder, "rezconfig.py")
else:
    rez_config_filename = rez_folder

os.environ["REZ_CONFIG_FILE"] = rez_config_filename
run(["setx.exe", "REZ_CONFIG_FILE", rez_config_filename])
print(f"\nREZ_CONFIG_FILE set to: {os.environ.get('REZ_CONFIG_FILE')}\n")

local_packages_folder = os.path.join(rez_folder,'packages').replace('\\','/')
release_packages_path = input("Release rez packages folder (\\\\ASH\Storage\.rez\packages): ") or r"\\ASH\Storage\.rez\packages"
release_packages_path = os.path.join(release_packages_path, "rez", "packages").replace('\\', '/')

if include_file:
    rez_config_file = open(os.path.join(rez_config_filename), "w+")
else:
    rez_config_file = open(os.path.join(rez_config_filename, "rezconfig.py"), "w+")

# print(f"LOCAL PACKAGE FOLDER: {local_packages_folder}")
# print(f"RELEASE PACKAGE FOLDER: {release_packages_path}")
#os.environ["REZ_LOCAL_PACKAGES_PATH"] = local_packages_folder
#os.environ["REZ_RELEASE_PACKAGES_PATH"] = release_packages_path
# rez_config_file.write(f"all_parent_variables = True\n")
rez_config_file.write(f"# The package search path. Rez uses this to find packages. A package with the\n# same name and version in an earlier path takes precedence.\npackages_path = [\n\t\"{local_packages_folder}\",\n\t\"{release_packages_path}\"]\n")
rez_config_file.write(f"#REZ_LOCAL_PACKAGES_PATH\n# The path that Rez will locally install packages to when rez-build is used\nlocal_packages_path = \"{local_packages_folder}\"\n")
rez_config_file.write(f"#REZ_RELEASE_PACKAGES_PATH\n# The path that Rez will deploy packages to when rez-release is used. For\n# production use, you will probably want to change this to a site-wide location.\nrelease_packages_path = \"{release_packages_path}\"")

""" Now a package must be setup for the downloaded python interpreter: a package.py is created for a rez-build """
create_python_pakage_file(embedded_python_folder, python_version)

""" HACK: direct edit of Lib/site-packages/rez/rezconfig.py file """
hack_rezconfig_file(os.path.join(embedded_python_folder, "Lib", "site-packages", "rez", "rezconfig.py"), local_packages_folder, release_packages_path)


"""if not os.path.exists(local_packages_folder):
    os.makedirs(local_packages_folder)
if not os.path.exists(release_packages_path):
    os.makedirs(release_packages_path)"""

env_variables = os.environ.copy()
os.chdir(embedded_python_folder)
# run(os.path.join(embedded_python_folder, "Scripts", "rez-bind --quickstart"), shell=True, env=env_variables)

run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "platform"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "arch"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "os"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-build"), "--install"])
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "rez"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "rezgui"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "setuptools"], shell=True, env=env_variables)
run([os.path.join("Scripts", "rez-bind"), "-i", local_packages_folder, "pip"], shell=True, env=env_variables)

#call(os.path.join(embedded_python_folder, "Scripts", "rez-config packages_path"))

"""print(f"Var from os.environ: {env_variables.get('REZ_CONFIG_FILE')}\n")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)
run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "--source-list"], shell=True, env=env_variables)
print("\nVar with ECHO after --source-list")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)
run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "packages_path"], shell=True, env=env_variables)
print("\nVar with ECHO after packages_path")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)

run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "packages_path"], shell=True, env=env_variables)"""

""" HACK: direct edit of Lib/site-packages/rez/rezconfig.py file: restore original file"""
hack_rezconfig_file(os.path.join(embedded_python_folder, "Lib", "site-packages", "rez", "rezconfig.py"), local_packages_folder, release_packages_path, restore=True)
