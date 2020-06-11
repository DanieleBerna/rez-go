from urllib import request
from shutil import copyfile
from subprocess import call, run, Popen
from pathlib import Path
import os
import re
import zipfile
import fileinput

EMBEDDABLE_PYTHON_URL = "https://www.python.org/ftp/python/"  # URL for python releases download

print(f"Red Rez - Redistributable rez installer\n")

""" The pipeline uses an embedded light Python3 version to install and then run rez.
A valid Python version is here required.
Script defaults to 3.7.4 64bit version if nothing is provided."""

python_version = input("Python version (3.7.4): ") or "3.7.4"
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

install_folder = input("Install folder (User Home)): ") or "D:\\Works\\pipe"  # str(Path.home())

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

zip_filename = f"python-{python_version}-embed-{system}.zip"
if not os.path.exists(zip_filename):  # Download required embeddable python if not present in script folder
    download_url = f"{EMBEDDABLE_PYTHON_URL}{python_version}/{zip_filename}"
    print(f"Downloading embeddable Python from: {download_url}")
    try:
        with request.urlopen(download_url) as response, open(zip_filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except:
        print(f"An error has occurred while downloading {zip_filename}")
        exit()

with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    zip_ref.extractall(os.path.join(install_folder, "core", "python"))


""" python37._pth needs to be edited uncommenting the import site line"""
for line in fileinput.input(os.path.join(install_folder, "core", "python", "python37._pth"), inplace=1):
    print(line.replace("#import site", "import site").rstrip())

getpip_filename = os.path.join(install_folder, "core", "python", "get-pip.py")
if not os.path.exists("get-pip.py"):  # Download get-pip.py if not present in script folder
    download_url = "https://bootstrap.pypa.io/get-pip.py"
    print(f"Downloading get-pip.py from: {download_url}")
    try:
        with request.urlopen(download_url) as response, open("get-pip.py", 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except:
        print(f"An error has occurred while downloading {zip_filename}")
        exit()
try:
    copyfile("get-pip.py", getpip_filename)
except IOError as e:
    print(f"An error has occurred while copying {zip_filename}")
    print(e)
    exit()

embedded_python_folder = os.path.join(install_folder, "core", "python")

call(os.path.join(embedded_python_folder, "python.exe") + " " + os.path.join(embedded_python_folder, "get-pip.py --no-warn-script-location"))

call(os.path.join(embedded_python_folder, "Scripts", "pip") + " install bleeding-rez --no-warn-script-location")

if not os.path.exists(os.path.join(embedded_python_folder, "rez")):
    os.makedirs(os.path.join(embedded_python_folder, "rez"))

include_file = True

if include_file:
    rez_config_filename = os.path.join(embedded_python_folder, "rez", "rezconfig.py")
else:
    rez_config_filename = os.path.join(embedded_python_folder, "rez")

os.environ["REZ_CONFIG_FILE"] = rez_config_filename
run(["setx.exe", "REZ_CONFIG_FILE", rez_config_filename])
#run(["set.exe", "REZ_CONFIG_FILE=", rez_config_filename],shell=True)
print(f"\nREZ_CONFIG_FILE set to: {os.environ.get('REZ_CONFIG_FILE')}\n")

local_packages_folder = os.path.join(embedded_python_folder,'rez','packages').replace('\\','/')
remote_packages_folder = input("Release rez packages folder: ") or "D:\\Works\\pipe\\server"
release_packages_path = os.path.join(remote_packages_folder, "rez", "packages").replace('\\','/')

if include_file:
    rez_config_file = open(os.path.join(rez_config_filename), "w+")
else:
    rez_config_file = open(os.path.join(rez_config_filename, "rezconfig.py"), "w+")

print(f"LOCAL PACKAGE FOLDER: {local_packages_folder}")
print(f"RELEASE PACKAGE FOLDER: {release_packages_path}")
os.environ["REZ_LOCAL_PACKAGES_PATH"] = local_packages_folder
os.environ["REZ_RELEASE_PACKAGES_PATH"] = release_packages_path
rez_config_file.write(f"all_parent_variables = True\n")
rez_config_file.write(f"# The package search path. Rez uses this to find packages. A package with the\n# same name and version in an earlier path takes precedence.\npackages_path = [\"{local_packages_folder}\",\"{release_packages_path}\"]\n")
rez_config_file.write(f"#REZ_LOCAL_PACKAGES_PATH\n# The path that Rez will locally install packages to when rez-build is used\nlocal_packages_path = \"{local_packages_folder}\"\n")
rez_config_file.write(f"#REZ_RELEASE_PACKAGES_PATH\n# The path that Rez will deploy packages to when rez-release is used. For\n# production use, you will probably want to change this to a site-wide location.\nrelease_packages_path = \"{release_packages_path}\"")

if not os.path.exists(local_packages_folder):
    os.makedirs(local_packages_folder)
if not os.path.exists(release_packages_path):
    os.makedirs(release_packages_path)
# call(os.path.join(embedded_python_folder, "Scripts", "rez-bind --quickstart"))
#call(os.path.join(embedded_python_folder, "Scripts", "rez-config packages_path"))
env_variables = os.environ.copy()
print(f"Var from os.environ: {env_variables.get('REZ_CONFIG_FILE')}\n")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)
run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "--source-list"], shell=True, env=env_variables)
print("\nVar with ECHO after --source-list")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)
run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "packages_path"], shell=True, env=dict(env_variables, REZ_LOCAL_PACKAGES_PATH=local_packages_folder, REZ_RELEASE_PACKAGES_PATH=release_packages_path))
print("\nVar with ECHO after packages_path")
run(["echo", "%REZ_CONFIG_FILE%"], shell=True, env=env_variables)

run([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "packages_path"], shell=True, env=dict(env_variables, REZ_LOCAL_PACKAGES_PATH=local_packages_folder, REZ_RELEASE_PACKAGES_PATH=release_packages_path))
# Popen([os.path.join(embedded_python_folder, "Scripts", "rez-config"), "packages_path"], shell=True, env=env_variables).wait()
