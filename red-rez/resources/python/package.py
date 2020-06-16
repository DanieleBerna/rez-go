import os

name = "python"
version = "3.7.4"
build_command = False

@early()
def _bin_path():
    return os.getcwd()
        
def commands():
    global env
    env["PATH"].prepend("{this._bin_path}")