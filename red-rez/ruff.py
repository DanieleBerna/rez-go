def create_python_pakage_file(interpreter_filepath, version):
    package_build_file = open(interpreter_filepath, "w+")
    package_build_file.write(f"import os\n\nname = 'python'\nversion = '{version}'\nbuild_command = False\n\n@early()\n"
                             f"def _bin_path():\n\treturn os.getcwd()\n\ndef commands():\n\tglobal env\n\t"
                             f"env['PATH'].prepend('{{this._bin_path}}')")
    package_build_file.close()

create_python_pakage_file("prova.py", "3.7.4")


