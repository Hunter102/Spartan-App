@echo off

echo Cleaning...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
pyinstaller --onefile --windowed SpartanGroupBuilder.py

echo Creating zip...
powershell Compress-Archive dist\SpartanGroupBuilder.exe release.zip -Force

echo Git add...
git add .

echo Git commit...
git commit -m "Release Build"

echo Git push...
git push

echo Done.
pause