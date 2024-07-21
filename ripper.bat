@echo off
if not exist "vrcrip" call update_deps.bat
call ./vrcrip/Scripts/activate.bat
python script.py %*
call ./vrcrip/Scripts/deactivate.bat
pause