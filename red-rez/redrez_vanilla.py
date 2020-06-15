from urllib import request
from shutil import copyfile
from subprocess import call, run, Popen
from pathlib import Path
import os
import re
import zipfile
import fileinput
import sys

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

with zipfile.ZipFile(os.path.join(install_folder, "core", "python", "python37.zip"), 'r') as zip_ref:
    pyzip_folder = os.path.join(install_folder, "core", "python", "python37zip")
    zip_ref.extractall(pyzip_folder)
    zip_ref.close()
    os.remove(os.path.join(install_folder, "core", "python", "python37.zip"))
    os.rename(pyzip_folder, os.path.join(install_folder, "core", "python", "python37.zip"))

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

#  call(os.path.join(embedded_python_folder, "Scripts", "pip") + " install bleeding-rez --no-warn-script-location") NO MORE BLEEDING REZ

""" TRY WITH VANILLA REZ """
with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), "rez.zip"), 'r') as zip_ref:
    zip_ref.extractall(os.path.join(install_folder, "core", "rez-install"))
run([os.path.join(embedded_python_folder, "python.exe"), os.path.join(install_folder, "core", "rez-install", "rez", "install.py"), "-v", os.path.join(install_folder, "core", "rez")])

