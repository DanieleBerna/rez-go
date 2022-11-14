pyinstaller --onefile rezgo.py

copy .\dist\rezgo.exe .\
@echo off
(
  echo set /p "installfolder=Enter installation folder: "
  echo .\rezgo.exe install %%installfolder%% -d
) > setup.bat

tar.exe acvf rezgo.zip payload rezgo.exe setup.bat
del .\rezgo.exe
del .\setup.bat




