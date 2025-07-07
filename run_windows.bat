@echo off
echo GitHub Project Uploader - Windows Launcher
echo.
echo Checking Git installation...
python check_git.py
echo.
echo Installing dependencies...
pip install requests
echo.
echo Starting application...
python main.py
echo.
pause