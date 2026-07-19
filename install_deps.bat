@echo off
echo ===================================================
echo Menginstal Dependensi Sistem Windows
echo ===================================================
winget install Genymobile.scrcpy --silent
pip install PyQt5 pywin32
echo ===================================================
echo [SUKSES] Semua dependensi selesai dipasang!
echo ===================================================
pause