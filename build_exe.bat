@echo off
title Android Device Wall Compiler
echo [+] Memastikan PyInstaller terpasang di Python Windows Store...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo.
python build_runner.py
pause