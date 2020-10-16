import zipfile
import os

if not os.path.exists("C:\\utgtools\\redist"):
    os.makedirs("C:\\utgtools\\redist")

red_rez_zip = zipfile.ZipFile(os.path.join("C:\\utgtools\\redist", 'RedistributableRez.zip'), 'w', zipfile.ZIP_STORED)

core_folder = "C:\\utgtools\\core\\"
zip_root_folder = os.path.basename(core_folder)
for root, dirs, files in os.walk(core_folder):
    for file in files:
        file_path = os.path.join(root, file)
        parent_path = os.path.relpath(file_path, core_folder)
        arcname = os.path.join(zip_root_folder, parent_path)
        red_rez_zip.write(file_path, arcname)
red_rez_zip.close()
