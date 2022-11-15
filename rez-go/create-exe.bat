pyinstaller --onefile rezgo.py

copy .\dist\rezgo.exe .\
@echo off
(
  echo set /p "installfolder=Enter installation folder: "
  echo .\rezgo.exe install %%installfolder%% -d -p
  echo copy .\blender_city20.bat %%installfolder%%\utgtools\core\launchers\blender_city20.bat
  echo copy .\blender.bat %%installfolder%%\utgtools\core\launchers\blender.bat
) > setup.bat

echo rez-env blender-3.3 city20_texturingtool blender_ug_exporter -- blender.exe --app-template city20 --python-use-system-env --python %%%%REZ_BLENDER_BOOTSCRIPT%%%% > blender_city20.bat
echo rez-env blender-3.3 -- blender.exe --python-use-system-env --python %%%%REZ_BLENDER_BOOTSCRIPT%%%% > blender.bat

tar.exe acvf rezgo.zip payload rezgo.exe setup.bat blender_city20.bat blender.bat
del .\rezgo.exe
del .\setup.bat
del .\blender_city20.bat
del .\blender.bat




