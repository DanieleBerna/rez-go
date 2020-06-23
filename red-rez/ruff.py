import os
install_folder = "T:\\"
_UGCORE_DIR = "ugcore"
test_rez_file = open(os.path.join(install_folder, _UGCORE_DIR,"test_rez.bat"), "w+")
test_rez_file.write(f"IF \"%REZ_CONFIG_FILE%\"==\"\" SET REZ_CONFIG_FILE={os.path.join(install_folder, _UGCORE_DIR, 'rez','rezconfig.py')}\n"
                    f"{os.path.join(install_folder, _UGCORE_DIR, 'rez', 'Scripts', 'rez','rez-env')} python --"
                    f" {os.path.join(install_folder, _UGCORE_DIR, 'rez', 'Scripts', 'rez','rez-context')}"
                    f"\npause")
