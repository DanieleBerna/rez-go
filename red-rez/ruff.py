import os
_DEFAULT_INSTALL_FOLDER = r"T:/"
_UGCORE_DIR = "ugcore"
import shutil
import zipfile

if os.path.exists(os.path.join(_DEFAULT_INSTALL_FOLDER, _UGCORE_DIR, "python")) and os.path.exists(os.path.join(_DEFAULT_INSTALL_FOLDER, _UGCORE_DIR, "rez")):
    print("ugcore presente sul pc")
    #os.chdir(os.path.join(_DEFAULT_INSTALL_FOLDER, _UGCORE_DIR))

    """zf = zipfile.ZipFile('ugcore.zip', mode='w')
    try:
        zf.write(os.path.join(_DEFAULT_INSTALL_FOLDER, _UGCORE_DIR, "python"))
    finally:
        zf.close()"""

    for dirname, subdirs, files in os.walk(os.path.join(_DEFAULT_INSTALL_FOLDER, _UGCORE_DIR)):
        redistributable_folders = []
        if 'exclude directory' in subdirs:
            subdirs.remove('exclude directory')
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

