#!/bin/bash
echo "==================================================="
echo "Menginstal Alat Sistem (Linux / macOS)"
echo "==================================================="

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[+] Sistem terdeteksi: Linux"
    sudo apt update
    sudo apt install -y scrcpy adb python3-pip
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[+] Sistem terdeteksi: macOS"
    if ! command -v brew &> /dev/null; then
        echo "[-] Error: Homebrew belum terinstal di Mac Anda. Silakan instal dari https://brew.sh"
        exit 1
    fi
    brew install scrcpy android-platform-tools
else
    echo "[-] OS tidak dikenali."
    exit 1
fi

echo "[+] Menginstal library PyQt5..."
pip3 install PyQt5

echo "==================================================="
echo "[SUKSES] Pemasangan selesai!"
echo "Silakan hubungkan perangkat Anda, lalu jalankan: python3 main.py"
echo "==================================================="