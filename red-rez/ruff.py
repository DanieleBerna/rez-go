import os
def create_python_pakage_file(interpreter_folder, version):
    """
    Create a package.py file used to rez-build an embedded interpreter
    :param interpreter_folder: folder of the python.exe file
    :param version: Python (and package) version
    """
    try:
        package_build_file = open(os.path.join(interpreter_folder, "package.py"), "w+")
        package_build_file.write(f"import os\n\nname = 'python'\nversion = '{version}'\nbuild_command = '{{this._bin_path}}/rezbuild.py {{install}}'\n\n@early()\n"
                                 f"def _bin_path():\n\treturn os.getcwd()\n\ndef commands():\n\tglobal env\n\t"
                                 f"env['PATH'].prepend('{{this._bin_path}}')")
        package_build_file.close()
    except IOError as e:
        print(f"Error while writing package.py file for Python interpreter\n{e}")
        return False
    return True


create_python_pakage_file("T:/ugcore/python","3.7.4")
