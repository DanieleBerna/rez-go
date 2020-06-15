import fileinput
import os

for line in fileinput.input("rezconfig.py", inplace=1):
    print(line.replace("~/packages", "D:\Path\Locale").rstrip())

for line in fileinput.input("rezconfig.py", inplace=1):
    print(line.replace("~/.rez/packages", "D:\Path\Server").rstrip())