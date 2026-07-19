# 📱 Android Device Wall (Murni Perangkat Asli)

Aplikasi berbasis **PyQt5** untuk memantau aktivitas multi-perangkat Android secara real-time dalam bentuk grid terstruktur (maksimal grid 5x10 untuk 50 perangkat). UI hanya akan memuat perangkat fisik asli yang terdeteksi oleh sistem ADB (tanpa dummy data).

## ⚡ Optimalisasi Kinerja (Tanpa GPU)
Parameter streaming `scrcpy` dikunci pada konfigurasi paling efisien agar ringan dijalankan menggunakan CPU Decoding:
* **Resolusi:** 360p (Sangat pas untuk ukuran grid kecil)
* **Framerate:** 12 FPS (Cukup mulus untuk keperluan monitoring massal)
* **Bitrate:** 300 Kbps (Mencegah kelebihan beban data pada USB Hub controller)
* **Fitur Tambahan:** Audio dan kontrol input dimatikan untuk menghemat resource core prosesor.

## 🛠️ Langkah Memulai

### 1. Download / Clone Proyek
```bash
git clone [https://github.com/USERNAME-ANDA/android-device-wall.git]](https://github.com/degentod/scrcpy-gui/tree/main)(https://github.com/USERNAME-ANDA/android-device-wall.git)
cd android-device-wall

### Jalankan Pemasangan Otomatis
Windows:
bash
install_deps.bat

### Linux / macOS: Buka terminal Anda di folder ini dan jalankan perintah:

Bash
chmod +x install_deps.sh
./install_deps.sh

### jalankan aplikasi
bash
python main.py
