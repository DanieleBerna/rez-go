# -*- coding: utf-8 -*-

"""
redrez (Redistributable Rez) is a python module used to setup 'rez' (https://github.com/nerdvegas/rez) ona Windows machine.
The pipeline uses a portable Python (WinPython) to install and then run rez.
If the install is done in a previously agreed path between users, the whole installed folder can be moved between machines.
when installing to a local folder it's possible to remap it to a previously agreed unit to make the tool portable.
"""

"""TEST"""
"""redrez.py -i local_folder -m map_unit -r release_folder"""
import os
import sys
import re
import argparse
import zipfile
import winreg

from shutil import rmtree
from subprocess import run

_TOOLSET_NAME = "utgtools"
_CORE_DIR = "core"
_DEFAULT_INSTALL_FOLDER = r"C:/"
_DEFAULT_MAP_UNIT = "T"
_REMAP_REGISTRY_VALUE_NAME = "Map_utgtools_unit"
_DEFAULT_RELEASE_FOLDER = r"C:/"+_TOOLSET_NAME
_LAUNCHERS_DIR = "launchers"

_PORTABLE_PYTHON_ZIP = "resources/portable_python_374.zip"  # zipped archive of WinPython portable interpreter
_REZ_ZIP = "resources/rez.zip"  # zipped archive of Rez (cloned from https://github.com/nerdvegas/rez )


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


def setup_folder_structure(local_folder, unit=None, release_folder=None):
    """
    Create all needed folders and optionally remap local folder to a new unit
    """
    install_folder = os.path.join(local_folder, _TOOLSET_NAME)  #
    if not os.path.exists(install_folder):
        os.makedirs(install_folder)

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

    if release_folder is not None:
        release_packages_folder = release_folder + r"\\" + r"\.rez\packages"
        if not os.path.exists(release_packages_folder):
            try:
                os.makedirs(release_packages_folder)
            except IOError:
                print(f"An error has occurred while creating remote folder {release_packages_folder}")
                exit()
    else:
        release_packages_folder = None

    return install_folder, release_packages_folder


def setup_rezconfig_file(local_packages_folder, release_packages_path):
    """
    Write a rezconfig.py file for packages folder settings and create an env var to let rez reading it
    """

    rez_config_filename = os.path.join((os.path.split(local_packages_folder)[0]), "rezconfig.py")
    os.environ["REZ_CONFIG_FILE"] = rez_config_filename
    run(["setx.exe", "REZ_CONFIG_FILE", rez_config_filename])
    print(f"\nREZ_CONFIG_FILE set to: {os.environ.get('REZ_CONFIG_FILE')}\n")

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

    # Add the packages paths to current env
    os.environ["REZ_LOCAL_PACKAGES_PATH"] = local_packages_folder

    return rez_config_filename


def add_rez_to_path(rez_bin_folder):
    """
    Add bin folder of an already installed rez to user's Path env var
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


def rez_build_machine_packages(rez_bin_folder, python_interpreter_folder):
    """
    Build some essential rez packages for the user's machine
    """
    # rez-build WinPython package. This will be the default Python package used by rez
    os.chdir(python_interpreter_folder)
    create_python_pakage_file(python_interpreter_folder, "3.7.4")
    create_python_rezbuild_file(python_interpreter_folder)
    run([os.path.join(rez_bin_folder, "rez-build"), "-i"])

    # rez-bind some packages
    run([os.path.join(rez_bin_folder, "rez-bind"), "platform"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "arch"])
    run([os.path.join(rez_bin_folder, "rez-bind"), "os"])


def install_rez(local_folder, unit, release_folder, add_to_path):
    """
    Perform a rez installation on a machine.
    Installation will include a portable WinPython that will be used for 'rez' setup.
    """

    install_folder, release_packages_path = setup_folder_structure(local_folder, unit, release_folder)  # Get install and release folders
    utgtools_folder = os.path.join(install_folder, _CORE_DIR)

    # Unpack portable WinPython
    print("Extracting portable Python...")
    with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), _PORTABLE_PYTHON_ZIP), 'r') as zip_ref:
        zip_ref.extractall(utgtools_folder)
    python_interpreter_folder = os.path.join(utgtools_folder, "python")

    # Unpack rez
    temp_rez_folder = (os.path.join(utgtools_folder, "temp_rez"))
    print("Extracting rez source...")
    with zipfile.ZipFile(os.path.join(os.path.dirname(sys.argv[0]), _REZ_ZIP), 'r') as zip_ref:
        zip_ref.extractall(temp_rez_folder)
    rez_folder = os.path.join(utgtools_folder, "rez")

    # Run rez install.py using WinPython, to permanently link rez to this interpreter
    print("Running rez install.py...")
    run([os.path.join(python_interpreter_folder, "python.exe"), os.path.join(temp_rez_folder, "rez", "install.py"), "-v", os.path.join(utgtools_folder, "rez")])

    rez_bin_folder = os.path.join(rez_folder, "Scripts", "rez")

    # Add installed rez to user's Path env var
    if add_to_path:
        add_rez_to_path(rez_bin_folder)

    # Write rezconfig.py file
    setup_rezconfig_file(os.path.join(rez_folder, 'packages'), release_packages_path)

    # rez-build WinPython package (default Python package used by rez) and bind machine packages (platform,arch,os)
    rez_build_machine_packages(rez_bin_folder, python_interpreter_folder)

    # Remove temp folder
    try:
        rmtree(temp_rez_folder)
    except OSError as e:
        print(f"Error while removing {temp_rez_folder}:  {e.strerror}")

    # Create of a simple batch file for testing purpose inside install_folder
    launchers_dir_fullpath = os.path.join(utgtools_folder, _LAUNCHERS_DIR)

    if not os.path.exists(launchers_dir_fullpath):
        os.makedirs(launchers_dir_fullpath)
    test_rez_file = open(os.path.join(launchers_dir_fullpath, "test_rez.bat"), "w+")
    """test_rez_file.write(#f"IF \"%REZ_CONFIG_FILE%\"==\"\" SET REZ_CONFIG_FILE={os.path.join(install_folder, _CORE_DIR, 'rez','rezconfig.py')}\n"
                        f"{os.path.join(install_folder, _CORE_DIR, 'rez', 'Scripts', 'rez','rez-env')} python --"
                        f" {os.path.join(install_folder, _CORE_DIR, 'rez', 'Scripts', 'rez','rez-context')}"
                        f"\npause")"""
    test_rez_file.write("rez-env python -- rez-context\npause")
    test_rez_file.close()

    os.environ["UTGTOOLS"] = utgtools_folder
    run(["setx.exe", "UTGTOOLS", utgtools_folder])
    print(f"\nUTGTOOLS env var set\n")

    installation_log_file = open(os.path.join(utgtools_folder, "installation_log.txt"), "w+")
    installation_log_file.write(f"local folder:{local_folder}\n"
                                f"map unit:{unit.lower()}\n"
                                f"install folder:{install_folder}\n"
                                f"release folder:{release_folder}")
    installation_log_file.close()

    return utgtools_folder


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
    parser = argparse.ArgumentParser(prog="redrez")

    subparsers = parser.add_subparsers(help='Modes', dest='mode', required=True)
    parser_install = subparsers.add_parser('install', help='Create a new rez setup in the local folder')
    parser_pack = subparsers.add_parser('pack', help='Pack the existing rez given the local folder in a zip file')
    parser_deploy = subparsers.add_parser('deploy', help='Unpack and deploy to the local folder a previously zipped rez')

    for p in (parser_install, parser_deploy):
        p.add_argument("-m", "--map", action="store", type=str, dest="unit",
                        help="Map the local folder to another disk unit during the install process")

        p.add_argument("-r", "--release", action="store", type=str, dest="release_folder",
                        help="Set a remote folder as release_packages_path")

        p.add_argument("-p", "--path", action="store_true", dest="add_to_path",
                       help="Add rez to user Path environment variable")

    parser.add_argument("local_folder", type=str,
                          help="rez local folder")

    args = parser.parse_args()

    if args.mode == "install":
        print(f"Creating a new rez setup:\n"
              f"Local folder: {args.local_folder}\n"
              f"Map unit: {args.unit}\n"
              f"Remote packages folder: {args.release_folder}")
        utgtools_folder = install_rez(args.local_folder, args.unit, args.release_folder, args.add_to_path)
        print(f"Success - Rez is now ready in: {utgtools_folder}")

    if args.mode == "pack":
        print(f"Pack stuff contained in {args.local_folder}")

    if args.mode == "deploy":
        print(f"Unpack zip content to {args.local_folder} and map to {args.unit}")


if __name__ == "__main__":
    print(f"RED REZ - Redistributable Rez installer\n")
    parse_arguments()

