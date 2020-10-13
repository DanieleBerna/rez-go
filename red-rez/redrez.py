# -*- coding: utf-8 -*-

"""
redrez (Redistributable Rez) is a python module used to setup 'rez' (https://github.com/nerdvegas/rez) ona Windows machine.
The pipeline uses a portable Python (WinPython) to install and then run rez.
If the install is done in a previously agreed path between users, the whole installed folder can be moved between machines.
when installing to a local folder it's possible to remap it to a previously agreed unit to make the tool portable.
"""

import os
import sys
import zipfile
import winreg
from shutil import rmtree
from subprocess import run

_PORTABLE_PYTHON_ZIP = "resources/portable_python_374.zip"  # zipped archive of WinPython portable interpreter
_REZ_ZIP = "resources/rez.zip"  # zipped archive of Rez (cloned from https://github.com/nerdvegas/rez )
_DEFAULT_INSTALL_FOLDER = r"T:/"
_UGCORE_DIR = "ugcore"


def create_python_pakage_file(interpreter_folder, version):
    """
    Create a package.py file used to rez-build an embedded interpreter
    :param interpreter_folder: folder of the python.exe file
    :param version: Python (and package) version
    """
    try:
        package_build_file = open(os.path.join(interpreter_folder, "package.py"), "w+")
        package_build_file.write(f"import os\n\nname = 'python'\nversion = '{version}'\nbuild_command = '{{root}}/python {{root}}/rezbuild.py {{install}}'\n\n"
                                 f"def commands():\n\t"
                                 f"env.PATH.append('{{root}}')\n\t"
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
    :param version: Python (and package) version
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


def install_rez():
    """
    Perform a rez installation on a machine.
    Installation will include a portable WinPython that will be used for 'rez' setup.
    """

    install_folder = input("Install folder ("+_DEFAULT_INSTALL_FOLDER+"): ") or _DEFAULT_INSTALL_FOLDER  # Ask user for a local install folder
    remap_to = input("Remap folder to new unit (leave empty if no remapped is required): ") or False  # Ask user for an optional remap unit for the install folder

    if remap_to:
        try:
            remap_to = remap_to.upper()
            run(["subst", (remap_to.upper()+":"), install_folder])  # Immediately remap the folder for the current session
            print(f"{install_folder} is remapped to {remap_to} unit")

            try:
                # Add a registry key for remapping the folder at Windows startup
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "Map_T_unit", 0, winreg.REG_SZ, f"subst {remap_to.upper()}: {install_folder}")
                winreg.CloseKey(key)
            except WindowsError:
                print("An error has occurred while setting SUBST key registry")
                exit()

            install_folder = remap_to+":\\"
        except:
            print(f"An error has occurred while remapping {install_folder} to {remap_to} unit")
            exit()

    # Unpack portable WinPython
    print("Extracting portable Python...")
    with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), _PORTABLE_PYTHON_ZIP), 'r') as zip_ref:
        zip_ref.extractall(os.path.join(install_folder, _UGCORE_DIR))
    python_interpreter_folder = os.path.join(install_folder, _UGCORE_DIR, "python")

    # Unpack rez
    temp_rez_folder = (os.path.join(install_folder,  _UGCORE_DIR, "temp_rez"))
    print("Extracting rez source...")
    with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), _REZ_ZIP), 'r') as zip_ref:
        zip_ref.extractall(temp_rez_folder)
    rez_folder = os.path.join(install_folder, _UGCORE_DIR, "rez")

    # Run rez install.py using WinPython, to permanently link rez to this interpreter
    print("Running rez install.py...")
    run([os.path.join(python_interpreter_folder, "python.exe"), os.path.join(temp_rez_folder, "rez", "install.py"), "-v", os.path.join(install_folder, _UGCORE_DIR, "rez")])
    rez_bin_folder = os.path.join(rez_folder, "Scripts", "rez")

    # Add installed rez to user's Path env var
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

    # Write a rezconfig.py file for packages folder settings and create an env var to let rez reading it
    rez_config_filename = os.path.join(rez_folder, "rezconfig.py")
    os.environ["REZ_CONFIG_FILE"] = rez_config_filename
    run(["setx.exe", "REZ_CONFIG_FILE", rez_config_filename])
    print(f"\nREZ_CONFIG_FILE set to: {os.environ.get('REZ_CONFIG_FILE')}\n")

    local_packages_folder = os.path.join(rez_folder, 'packages')#.replace('\\','/')
    release_packages_path = input("Release rez packages folder (\\\\ASH\Storage\.rez\packages): ") or r"\\ASH\Storage\.rez\packages"

    rez_config_file = open(os.path.join(rez_config_filename), "w+")
    rez_config_file.write(f"# The package search path. Rez uses this to find packages. A package with the\n"
                          f"# same name and version in an earlier path takes precedence.\n"
                          f"packages_path = [\n\tr\"{local_packages_folder}\",\n\tr\"{release_packages_path}\"]\n")
    rez_config_file.write(f"#REZ_LOCAL_PACKAGES_PATH\n"
                          f"# The path that Rez will locally install packages to when rez-build is used\n"
                          f"local_packages_path = r\"{local_packages_folder}\"\n")
    rez_config_file.write(f"#REZ_RELEASE_PACKAGES_PATH\n"
                          f"# The path that Rez will deploy packages to when rez-release is used. For\n"
                          f"# production use, you will probably want to change this to a site-wide location.\n"
                          f"release_packages_path = r\"{release_packages_path}\"")

    # Add the packages paths to current env
    os.environ["REZ_LOCAL_PACKAGES_PATH"] = local_packages_folder
    os.environ["REZ_RELEASE_PACKAGES_PATH"] = release_packages_path

    # rez-build WinPython package. This will be the default Python package used by rez
    os.chdir(python_interpreter_folder)
    create_python_pakage_file(python_interpreter_folder, "3.7.4")
    create_python_rezbuild_file(python_interpreter_folder)
    run([os.path.join(rez_bin_folder, "rez-build"), "-i"])

    # rez-bind some packages
    run([os.path.join(rez_bin_folder, "rez-bind"), "platform"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "arch"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "os"])

    # Remove temp folder
    try:
        rmtree(temp_rez_folder)
    except OSError as e:
        print(f"Error while removing {temp_rez_folder}:  {e.strerror}")

    # Create of a simple batch file for testing purpose inside install_folder
    test_rez_file = open(os.path.join(install_folder, _UGCORE_DIR,"test_rez.bat"), "w+")
    test_rez_file.write(f"IF \"%REZ_CONFIG_FILE%\"==\"\" SET REZ_CONFIG_FILE={os.path.join(install_folder, _UGCORE_DIR, 'rez','rezconfig.py')}\n"
                        f"{os.path.join(install_folder, _UGCORE_DIR, 'rez', 'Scripts', 'rez','rez-env')} python --"
                        f" {os.path.join(install_folder, _UGCORE_DIR, 'rez', 'Scripts', 'rez','rez-context')}"
                        f"\npause")


if __name__ == "__main__":
    print(f"RED REZ - Redistributable Rez installer\n")
    install_rez()
