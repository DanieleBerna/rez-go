name = 'pyside2'
version = '5.15.0'
requires=["python"]
build_command = "py {root}/build.py "+version 

def commands():
	global env
	env['PYTHONPATH'].prepend('{root}')