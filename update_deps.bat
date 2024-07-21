
powershell -Command "Invoke-WebRequest https://download.visualstudio.microsoft.com/download/pr/d1adccfa-62de-4306-9410-178eafb4eeeb/48e3746867707de33ef01036f6afc2c6/dotnet-sdk-8.0.303-win-x64.exe -OutFile dotnetsdk.exe"
dotnetsdk.exe /install /quiet /norestart
del dotnetsdk.exe

powershell -Command "Invoke-WebRequest https://github.com/SanyaNya/AssetRipper/releases/download/1.0.18-r23/AssetRipper-Console-win-x64-1.0.18-r23.zip -OutFile package.zip"
rmdir /Q /S AssetRipper
mkdir AssetRipper
cd AssetRipper
tar -xvf ..\package.zip
cd ..
del package.zip

powershell -Command "Invoke-WebRequest https://github.com/FACS01-01/FACS_Utilities/releases/download/24.05.03/FACS.Utilities.24.05.03.zip -OutFile package.zip"
rmdir /Q /S FACS_Utilities
mkdir FACS_Utilities
cd FACS_Utilities
tar -xvf ..\package.zip
cd ..
del package.zip

rmdir /Q /S vrcrip
python -m venv vrcrip
call ./vrcrip/Scripts/activate.bat
pip install vrchatapi
call ./vrcrip/Scripts/deactivate.bat
echo.
echo ---------------DONE!-------------