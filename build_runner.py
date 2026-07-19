import os
import sys
import subprocess
import shutil

def run_build():
    print("====================================================")
    print("🚀 MEMULAI PROSES KOMPILASI ANDROID DEVICE WALL")
    print("====================================================")
    
    try:
        import PyInstaller
        print("[+] PyInstaller terdeteksi di sistem.")
    except ImportError:
        print("[*] PyInstaller belum terpasang. Menginstal sekarang...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"[*] Membersihkan folder lama: {folder}...")
            shutil.rmtree(folder)
            
    if os.path.exists("AndroidDeviceWall.spec"):
        os.remove("AndroidDeviceWall.spec")

    # MENGGUNAKAN HURUF KAPITAL "PyInstaller" YANG SESUAI DENGAN PANGGILAN MODULNYA
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name=AndroidDeviceWall",
        "main.py"
    ]
    
    print(f"\n[+] Mengeksekusi perintah kompilasi di sistem: {sys.platform.upper()}...")
    try:
        # Tanpa shell=True agar dieksekusi langsung oleh interpreter Python internal
        subprocess.check_call(cmd)
        print("\n====================================================")
        print("🎉 [SUKSES] APLIKASI BERHASIL DIKOMPILASI!")
        dist_path = os.path.abspath("dist")
        print(f"[+] Silakan cek hasilnya di folder: {dist_path}")
        if sys.platform == "win32":
            print("[+] File Terbuat: AndroidDeviceWall.exe")
        else:
            print("[+] File Terbuat: AndroidDeviceWall (Aplikasi Biner)")
        print("====================================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Gagal melakukan kompilasi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_build()