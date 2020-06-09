from urllib import request
from shutil import copyfile
from subprocess import call, run
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

install_folder = input("Install folder (User Home)): ") or "T:\\test"  # str(Path.home())

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
rez_config_filename = os.path.join(embedded_python_folder, "rez", "rezconfig.py")
os.environ["REZ_CONFIG_FILE"] = rez_config_filename
run(r'setx.exe REZ_CONFIG_FILE  ' + rez_config_filename)
rez_config_file = open(rez_config_filename, "w+")
#rez_config_file.write(f"""#REZ_LOCAL_PACKAGES_PATH\n# The path that Rez will locally install packages to when rez-build is used\nlocal_packages_path = "{os.path.join(embedded_python_folder,"rez","packages")}\n""")
rez_config_file.write(f"#REZ_LOCAL_PACKAGES_PATH\n# The path that Rez will locally install packages to when rez-build is used\nlocal_packages_path = \"{os.path.join(embedded_python_folder,'rez','packages')}\"\n")
remote_packages_folder = input("Release rez packages folder: ")
release_packages_path = os.path.join(remote_packages_folder, "rez", "packages")
rez_config_file.write(f"#REZ_RELEASE_PACKAGES_PATH\n# The path that Rez will deploy packages to when rez-release is used. For\n# production use, you will probably want to change this to a site-wide location.\nrelease_packages_path = \"{release_packages_path}\"")

call(os.path.join(embedded_python_folder, "Scripts", "rez-bind --quickstart"))