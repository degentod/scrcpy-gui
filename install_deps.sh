#!/bin/bash
echo "==================================================="
echo "Menginstal Dependensi Sistem Linux / macOS"
echo "==================================================="
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y scrcpy adb python3-pip python3-pyqt5
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install scrcpy android-platform-tools
fi
pip3 install PyQt5
echo "==================================================="
echo "[SUKSES] Semua dependensi selesai dipasang!"
echo "==================================================="