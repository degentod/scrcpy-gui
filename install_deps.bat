@echo off
echo ===================================================
echo Menginstal Alat Sistem: ADB, scrcpy, dan PyQt5
echo ===================================================

echo [+] Memastikan scrcpy dan ADB terinstal...
winget install Genymobile.scrcpy --silent

echo [+] Menginstal library PyQt5 untuk UI...
pip install PyQt5

echo ===================================================
echo [SUKSES] Semua dependensi telah diproses!
echo PERINGATAN: Tutup dan buka kembali terminal/CMD Anda agar sistem mendeteksi perubahan.
echo ===================================================
pause