# red-rez

**red-rez (*red*istributable *rez*) is a script used to create a working rez system on a Windows machine regardless of any previously installed Python version.
The created folder can be copy-pasted on other machines too and, with a few hacks, work without issues or complex setup processes.**

## Introduction

At our studio we use different DCCs, but mostly 3dsmax, Blender and Unreal Engine 4.
Custom tools can spped up the development and improve our pipeline, but each software uses it's own Python version: managing packages and modules by hand is a pain.
So one day, suggested by some community members, I decided to solve this problem with *rez*.
When I tried to setup rez for the first time on the office Windows machine I encountered some issues, mostly due to some messy Python installation already present on the PC.
I wanted to install the tool on other machines but every person had his personal setup and manage every specific case by hand was quite tedious.

My goal was to have a quick script capable to do the job for me: install and configure rez without problems and find a way to quickly replicate the setup on other machines.
How to do that?

## Solution

### WinPython installed rez
rez needs python to run. But I can't control Python versions on users' PCs.
At first I used the official embeddable Python interpreter but I had some issues: it's not *really* portable after all.
So I decided to give [WinPython](https://sourceforge.net/projects/winpython/) a chance and bind my rez to it.
Since I need Python just for have rez working and resolve environments it's fine to use WinPython: once the env is resolved I can use other interpreters from we DCCs we use.

## Usage
redrez is a command line script: basic usage is:
`redrez [-h] {install,pack,deploy} ... local_folder`
where local_folder is the rez directory on user's machine.

At the moment only the *install* subcommand is working and tested.

`usage: redrez install [-h] [-m UNIT] [-r RELEASE_FOLDER] [-p]`

`optional arguments:
  -h, --help            show this help message and exit
  -m UNIT, --map UNIT   Map the local folder to another disk unit during the
                        install process
  -r RELEASE_FOLDER, --release RELEASE_FOLDER
                        Set a remote folder as release_packages_path
  -p, --path            Add rez to user Path environment variable`


### Setup breakdown
The rez setup performed by red-rez can be summarized as follows: 
- User must provide a *local install folder*, an unused (and agreed at studio level) *unit letter* and an agreed *remote folder*
- The local folder is created if not present and mapped to the unit letter provided using *subst* command: from now on the script always use the new unit for paths, instead of local folder
- A registry key is added to execute the *subst* command at every Windows startup
- WinPython is unzipped in the local folder
- rez is unzipped in a temp folder
- WinPython is used to setup rez
- rez bin path is added to user's Path env var
- A rezconfig.py file is written, with all needed packages paths inside (the local remapped one and the remote one)
- The REZ_CONFIG_FILE env var pointing to the rezconfig file is created
- WinPython interpreter is packaged for future Python usage
- Bind arc, os,platform and create *locally stored* packages
- Create a *launchers* folder and a testing .bat file that just resolve an environment with Python
- Delete all temp folders and files

### Redistribution
At this point it's possible to copy paste the folder containing all (rez,python,packages,launchers) to another machine. If the unit letter is mapped and the REZ_CONFIG_FILE env var points to the correct file, rez will be immediately working on that machine.


