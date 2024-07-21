
powershell -Command "Invoke-WebRequest https://aka.ms/dotnet/8.0/preview/dotnet-runtime-win-x64.exe -OutFile dotnet.exe"
dotnet.exe /install /quiet /norestart
del dotnet.exe

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