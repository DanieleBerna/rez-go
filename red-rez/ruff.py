from urllib import request
from shutil import copyfile
from subprocess import call, run
import os
import re
import zipfile

blender_zip_path = r"T:\blender\windows64\payload\blender.zip"
archive = zipfile.ZipFile(blender_zip_path)
print(archive.namelist()[0].split("-")[1])

