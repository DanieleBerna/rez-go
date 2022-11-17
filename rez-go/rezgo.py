# -*- coding: utf-8 -*-

"""
rezgo (Let's go Rez!) is a python tool used to quickly setup 'rez' (https://github.com/AcademySoftwareFoundation/rez)
on a Windows machine with no other prerequisites.
A portable Python (WinPython) is used to install rez, so it will be hardwired to that python, no matter how
many python version a user can have.
When installing it's possible to remap installation folder to a previously agreed unit to make the toolset fully portable.
"""

import os
import sys
import re
import argparse
import zipfile
import winreg
import requests

from shutil import rmtree
from subprocess import run

_TOOLSET_NAME = "utgtools"  # name for the whole studio toolset. It will be reflected everywhere
_CORE_DIR = "core"  # folder containing the base scripts and functionalities
_DEFAULT_INSTALL_FOLDER = r"C:/"
_DEFAULT_MAP_UNIT = "T"  # stands for Tools
_REMAP_REGISTRY_VALUE_NAME = "Map_"+_TOOLSET_NAME+"_unit"
_SERVER_NAME = "foofa"
_DEFAULT_REMOTE_FOLDER = "\\\\" + _SERVER_NAME + "\\" + _TOOLSET_NAME + "\\.rez\\packages"
_LAUNCHERS_DIR = "launchers"
_PAYLOAD_DIR = "payload"
_PORTABLE_PYTHON_ZIP = "winpython_395.zip"  # zipped archive of WinPython portable interpreter
_REZ_ZIP = "rez.zip"  # zipped archive of Rez (cloned from https://github.com/AcademySoftwareFoundation/rez )


def set_env_variable(name, value):
    """
    Simple function to quick set an environment variable for the user and making it immediately available
    """
    os.environ[name.upper()] = value
    run(["setx.exe", name.upper(), value])
    print(f"\n{name.upper()} env var set\n")
    return True


def create_python_package_file(interpreter_folder, version):
    """
    Create a package.py file used to rez-build an embedded interpreter
    :param interpreter_folder: folder of the python.exe file
    :param version: Python (and package) version
    """
    try:
        package_build_file = open(os.path.join(interpreter_folder, "package.py"), "w+")
        package_build_file.write(f"import os\n\nname = 'python'\nversion = '{version}'\nbuild_command = '{{root}}/python {{root}}/rezbuild.py {{install}}'\n\n"
                                 f"def commands():\n\t"
                                 f"if not env.PYTHON_NOOP:\n\t\t"
                                 f"env.PATH.append('{{root}}')\n\t\t"
                                 f"env.PYTHONPATH.append('{{root}}')\n")
        package_build_file.close()
    except IOError as e:
        print(f"Error while writing package.py file for Python interpreter\n{e}")
        return False
    return True


def create_python_rezbuild_file(interpreter_folder):
    """
    Create a rezbuild.py file used to rez-build an embedded interpreter
    :param interpreter_folder: folder of the python.exe file
    """
    try:
        rezbuild_file = open(os.path.join(interpreter_folder, "rezbuild.py"), "w+")
        rezbuild_file.write(f"import os\n"
                                 f"import sys\n"
                                 f"import logging\n"
                                 f"from distutils.dir_util import copy_tree\n"
                                 f"logging.basicConfig(level=logging.INFO)\n"
                                 f"log = logging.getLogger()\n\n\n"
                                 f"def build(source_path, build_path, install_path, targets):\n\t"
                                 f"print(source_path)\n\t"
                                 f"print(build_path)\n\t"
                                 f"print(install_path)\n\t"
                                 f"logging.info('Prepare build...')\n\t"
                                 f"if 'install' not in (targets or []):\n\t\t"
                                 f"return\n\t"
                                 f"logging.info('Copy files to install target path...')\n\t"
                                 f"# Copy files to repository\n\t"
                                 f"copy_tree(source_path, install_path)\n\n\n"
                                 f"if __name__ == '__main__':\n\t"
                                 f"build(source_path=os.environ['REZ_BUILD_SOURCE_PATH'],\n\t"
                                 f"      build_path=os.environ['REZ_BUILD_PATH'],\n\t"
                                 f"      install_path=os.environ['REZ_BUILD_INSTALL_PATH'],\n\t"
                                 f"      targets=sys.argv[1:])\n")
        rezbuild_file.close()
    except IOError as e:
        print(f"Error while writing rezbuild.py file for Python interpreter\n{e}")
        return False
    return True


def setup_folder_structure(install_folder, remote_folder=None, unit=None):
    """
    Create all needed folders and optionally remap local folder to a new unit
    """
    install_folder = os.path.join(install_folder, _TOOLSET_NAME)  #
    if not os.path.exists(install_folder):
        os.makedirs(install_folder)

    if remote_folder is not None:
        if not os.path.exists(remote_folder):
            try:
                os.makedirs(remote_folder)
            except IOError:
                print(f"An error has occurred while creating remote folder {remote_folder}")
                exit()

    if unit is not None and re.fullmatch("[a-z]", unit.lower()) and not os.path.exists(unit.upper()+":\\"):
        try:
            remap_to = unit.upper()
            run(["subst", (remap_to.upper() + ":"),
                 install_folder])  # Immediately remap the folder for the current session
            print(f"{install_folder} is remapped to {remap_to} unit")

            if True:
                try:
                    # Add a registry key for remapping the folder at Windows startup
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                         winreg.KEY_ALL_ACCESS)

                    try:  # If it exists, remove a previously set key value
                        winreg.DeleteValue(key, _REMAP_REGISTRY_VALUE_NAME)
                    except:
                        pass

                    winreg.SetValueEx(key, _REMAP_REGISTRY_VALUE_NAME, 0, winreg.REG_SZ,
                                      f"subst {remap_to.upper()}: {install_folder}")
                    winreg.CloseKey(key)
                except WindowsError:
                    print("An error has occurred while setting SUBST key registry")
                    exit()

            install_folder = remap_to + ":\\"
        except:
            print(f"An error has occurred while remapping {install_folder} to {remap_to} unit")
            exit()

    return install_folder, remote_folder


def setup_rezconfig(local_packages_folder, release_packages_path):
    """
    Write a rezconfig.py file for packages folder settings and create an env var to let rez reading it
    """

    rez_config_filename = os.path.join((os.path.split(local_packages_folder)[0]), "rezconfig.py")

    try:
        rez_config_file = open(os.path.join(rez_config_filename), "w+")
        rez_config_file.write(f"# The package search path. Rez uses this to find packages. A package with the\n"
                              f"# same name and version in an earlier path takes precedence.\n"
                              f"packages_path = [\n\tr\"{local_packages_folder}\",\n\tr\"{release_packages_path}\"]\n")
        rez_config_file.write(f"#REZ_LOCAL_PACKAGES_PATH\n"
                              f"# The path that Rez will locally install packages to when rez-build is used\n"
                              f"local_packages_path = r\"{local_packages_folder}\"\n")
        if release_packages_path is not None:
            rez_config_file.write(f"#REZ_RELEASE_PACKAGES_PATH\n"
                                  f"# The path that Rez will deploy packages to when rez-release is used. For\n"
                                  f"# production use, you will probably want to change this to a site-wide location.\n"
                                  f"release_packages_path = r\"{release_packages_path}\"")
            os.environ["REZ_RELEASE_PACKAGES_PATH"] = release_packages_path

    except IOError:
        print(f"An error has occurred while creating rezconfig.py")
        exit()

    set_env_variable("REZ_CONFIG_FILE", rez_config_filename)
    # Add the packages paths to current env
    os.environ["REZ_LOCAL_PACKAGES_PATH"] = local_packages_folder

    return rez_config_filename


def add_rez_to_path(rez_bin_folder):
    """
    Add bin folder of an installed rez to user's Path env var
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0,
                             winreg.KEY_ALL_ACCESS)
        val, type = winreg.QueryValueEx(key, "Path")
        if (val.replace("\\", "/")).find(rez_bin_folder.replace("\\", '/')) is -1:
            val = val + ";" + rez_bin_folder
            winreg.SetValueEx(key, "Path", type, winreg.REG_EXPAND_SZ, val)
        winreg.CloseKey(key)
    except WindowsError:
        pass


def rezbuild_machine_packages(rez_bin_folder, python_interpreter_folder):
    """
    Build some essential rez packages for the user's machine
    """
    # rez-build WinPython package. This will be the default Python package used by rez
    os.chdir(python_interpreter_folder)
    create_python_package_file(python_interpreter_folder, "3.9.5")
    create_python_rezbuild_file(python_interpreter_folder)
    run([os.path.join(rez_bin_folder, "rez-build"), "-i"])

    # rez-bind some packages
    run([os.path.join(rez_bin_folder, "rez-bind"), "platform"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "arch"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "os"])


def install_portable_python(core_folder):
    """
    Unpack portable WinPython to the core folder
    """
    print("Extracting Python...")
    try:
        with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), _PAYLOAD_DIR, _PORTABLE_PYTHON_ZIP), 'r') as zip_ref:
            zip_ref.extractall(core_folder)
    except Exception as e:
        print(f"Error while unpacking Python interpreter in {core_folder}:  {e.strerror}")
        exit()
    return True


def download_rez_release(download_to_filepath, latest=True):
    """
    Download official release from rez GitHub
    default is latest release
    """
    url = "https://api.github.com/repos/AcademySoftwareFoundation/rez/releases/latest"
    try:
        response = requests.get(url)
        version = response.json()["name"]
        print(f"Downloading rez version: {version}")
        download_url = response.json()["zipball_url"]
        response = requests.get(download_url)
        open(f"./{download_to_filepath}", "wb").write(response.content)
        return download_to_filepath
    except Exception as e:
        print(e)
        return None


def deploy_rez(install_folder, remote_folder, write_rezconfig, add_to_path=False, download=True):
    """
    Perform a rez installation on a machine.
    """

    # Search python interpreter
    python_folder = os.path.join(install_folder, "python")  # installed python needed for rez setup
    if not os.path.exists(python_folder):  # if toolset python is not present, install it
        print(f"Python interpreter not found in {install_folder}: install it before deploying rez")
        exit()

    rez_zip_filepath = os.path.join(os.path.dirname(sys.argv[0]), _PAYLOAD_DIR, _REZ_ZIP)
    # Download latest rez from AcademySoftwareFoundation GitHub
    if download:
        rez_zip_filepath = download_rez_release(rez_zip_filepath)

    # Unpack rez
    temp_rez_folder = (os.path.join(install_folder, "temp_rez"))
    print(f"TEMP REZ FOLDER: {temp_rez_folder}")
    rez_zip_root_folder = "rez-master"
    print("Extracting rez source...")

    with zipfile.ZipFile(rez_zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(temp_rez_folder)
        rez_zip_root_folder = [info.filename for info in zip_ref.infolist() if info.is_dir()][0].split("/")[0]

    # Run rez install.py using WinPython, to permanently link rez to this interpreter
    print("Running rez install.py...")
    rez_folder = os.path.join(install_folder, "rez")
    print(f"TEMP REZ FOLDER: {temp_rez_folder}")
    print(f"ROOT REZ FOLDER: {rez_zip_root_folder}")
    print(f"SETUP PY FOLDER: {os.path.join(temp_rez_folder, rez_zip_root_folder)}")
    run([os.path.join(python_folder, "python.exe"), os.path.join(temp_rez_folder, rez_zip_root_folder, "install.py"), "-v", rez_folder])

    rez_bin_folder = os.path.join(rez_folder, "Scripts", "rez")

    # Add installed rez to user's Path env var
    if add_to_path:
        add_rez_to_path(rez_bin_folder)

    # Write rezconfig.py file
    if write_rezconfig:
        setup_rezconfig(os.path.join(rez_folder, 'packages'), remote_folder)

    # rez-build WinPython package (default Python package used by rez) and bind machine packages (platform,arch,os)
    rezbuild_machine_packages(rez_bin_folder, python_folder)

    # Remove temp folder
    try:
        rmtree(temp_rez_folder)
    except OSError as e:
        print(f"Error while removing {temp_rez_folder}:  {e.strerror}")

    # Create of a simple batch file for testing purpose inside install_folder
    launchers_dir_fullpath = os.path.join(install_folder, _LAUNCHERS_DIR)

    if not os.path.exists(launchers_dir_fullpath):
        os.makedirs(launchers_dir_fullpath)
    test_rez_file = open(os.path.join(launchers_dir_fullpath, "test_rez.bat"), "w+")
    """test_rez_file.write(#f"IF \"%REZ_CONFIG_FILE%\"==\"\" SET REZ_CONFIG_FILE={os.path.join(install_folder, _CORE_DIR, 'rez','rezconfig.py')}\n"
                        f"{os.path.join(install_folder, _CORE_DIR, 'rez', 'Scripts', 'rez','rez-env')} python --"
                        f" {os.path.join(install_folder, _CORE_DIR, 'rez', 'Scripts', 'rez','rez-context')}"
                        f"\npause")"""
    test_rez_file.write("rez-env python -- rez-context\npause")
    test_rez_file.close()

    return install_folder


def install_toolset(install_folder, remote_folder=None, remap_unit=None, add_to_path=False, download_rez=False):
    print(f"Creating a new {_TOOLSET_NAME} toolset in {install_folder}\n")
    if remap_unit is not None:
        print(f"Local folder will be remapped to {remap_unit.upper()} unit\n")
    if remote_folder is None:
        remote_folder = _DEFAULT_REMOTE_FOLDER
    print(f"Remote rez packages folder: {remote_folder}")

    """Setup all needed folders"""
    install_folder, release_packages_path = setup_folder_structure(install_folder, remote_folder, remap_unit)
    core_folder = os.path.join(install_folder, _CORE_DIR)
    python_folder = os.path.join(core_folder, "python")

    """Unpack portable WinPython"""
    if not os.path.exists(python_folder):  # if toolset python is not present, install it
        os.makedirs(python_folder)
        install_portable_python(core_folder)

    deploy_rez(core_folder, remote_folder, True, add_to_path, download_rez)
    # utgtools_folder = install_rez(args.local_folder, args.unit, args.release_folder, args.add_to_path)
    set_env_variable(_TOOLSET_NAME, install_folder)
    print(f"Success - Rez is now ready in: {core_folder}")


def zip_utgtools(utgtools_folder):
    # Zip installed rez, ready for redistributing

    if not os.path.exists(os.path.join(utgtools_folder, "redist")):
        os.makedirs(os.path.join(utgtools_folder, "redist"))

    red_rez_zip = zipfile.ZipFile(os.path.join(utgtools_folder, "redist",'RedistributableRez.zip'), 'w', zipfile.ZIP_STORED)

    core_folder = os.path.join(utgtools_folder, _CORE_DIR)
    zip_root_folder = os.path.basename(core_folder)
    for root, dirs, files in os.walk(core_folder):
        for file in files:
            file_path = os.path.join(root, file)
            parent_path = os.path.relpath(file_path, core_folder)
            arcname = os.path.join(zip_root_folder, parent_path)
            red_rez_zip.write(file_path, arcname)
    red_rez_zip.close()


def parse_arguments():
    parser = argparse.ArgumentParser(prog="rezgo")

    subparsers = parser.add_subparsers(help='Modes', dest='mode', required=True)
    parser_install = subparsers.add_parser('install', help='Create a new rez setup in the local folder')
    parser_update = subparsers.add_parser('update', help='Update installed rez')
    parser_pack = subparsers.add_parser('pack', help='Pack the existing rez given the local folder in a zip file')

    parser_install.add_argument("local_folder", type=str, help="rez local folder")

    parser_install.add_argument("-r", "--release", action="store", type=str, dest="release_folder",
                                help="Set a remote folder as release_packages_path")

    parser_install.add_argument("-m", "--map", action="store", type=str, dest="unit",
                    help="Map the local folder to another disk unit during the install process")

    parser_install.add_argument("-p", "--path", action="store_true", dest="add_to_path",
                    help="Add rez to user Path environment variable")

    parser_install.add_argument("-d", "--download", action="store_true", dest="download_rez",
                                help="Download latest rez from GitHub")

    parser_update.add_argument("-d", "--download", action="store_true", dest="download_rez",
                                help="Download latest rez from GitHub")

    args = parser.parse_args()

    if args.mode == "install":  # This is for a full installation from scratch
        install_toolset(args.local_folder, args.release_folder, args.unit, args.add_to_path, args.download_rez)

    # UPDATE IS WIP
    if args.mode == "update":  # This updates rez
        toolset_folder = os.getcwd(_TOOLSET_NAME)
        if toolset_folder:
            print(f"Toolset installation detected in {toolset_folder}")
            # Remove rez folder
            try:
                print(f"Deleting installed rez...")
                rmtree(os.path.join(toolset_folder, _CORE_DIR, "rez"))
            except OSError as e:
                print(f"Error while removing old rez:  {e.strerror}")
        # deploy_rez(os.path.join(_TOOLSET_NAME, _CORE_DIR), remote_folder, True, False, download_rez)

    if args.mode == "pack":
        print(f"Pack stuff contained in {args.local_folder}")

    if args.mode == "deploy":
        print(f"Unpack zip content to {args.local_folder} and map to {args.unit}")


if __name__ == "__main__":
    print(f"REZ GO! - Quick Rez installer\n")
    parse_arguments()


