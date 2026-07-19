import sys
import subprocess
import os
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QDialog, QComboBox, QLineEdit, QFileDialog, 
                             QListWidget, QListWidgetItem, QMessageBox, QTabWidget)
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import Qt, QSize, QTimer

# Deteksi OS untuk Window Embedding
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import win32gui
    import win32con

# STYLE: Cyberpunk Glassmorphism dengan Aksen Ungu Neon
GLASS_STYLE = """
    QWidget {
        background-color: transparent;
        color: #FFFFFF;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QWidget #MainBackground {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0b10, stop:1 #12131a);
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: rgba(255, 255, 255, 0.02);
        width: 8px;
        height: 8px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: rgba(157, 78, 221, 0.3);
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
        background: rgba(157, 78, 221, 0.6);
    }
    QTabWidget::panel {
        border: 1px solid rgba(157, 78, 221, 0.3);
        background: rgba(0, 0, 0, 0.4);
        border-radius: 8px;
    }
    QTabBar::tab {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 8px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
    }
    QTabBar::tab:selected {
        background: rgba(157, 78, 221, 0.2);
        border-color: rgba(157, 78, 221, 0.6);
    }
    QComboBox, QLineEdit, QListWidget {
        background-color: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 6px;
        padding: 6px 12px;
        color: #FFF;
        font-size: 13px;
    }
    QComboBox::drop-down { border: none; }
    QListWidget::item:hover { background-color: rgba(157, 78, 221, 0.15); }
    QListWidget::item:selected { background-color: rgba(157, 78, 221, 0.4); }
"""

DEVICE_CARD_STYLE = """
    QFrame #DeviceCard {
        background-color: #000000;
        border: 3px solid #9D4EDD;
        border-radius: 12px;
    }
    QWidget #VideoFrame {
        background-color: #000000;
        border-radius: 9px;
    }
"""

class AppManagerDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle(f"App Manager - {device_id}")
        self.resize(550, 650)
        self.setStyleSheet(GLASS_STYLE)
        
        self.raw_user_apps = []
        self.raw_system_apps = []
        
        layout = QVBoxLayout(self)
        lbl_info = QLabel(f"📦 Kelola Aplikasi: {device_id}", self)
        lbl_info.setStyleSheet("font-size: 15px; font-weight: bold; color: #9D4EDD; margin-bottom: 5px;")
        layout.addWidget(lbl_info)
        
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Cari nama package aplikasi di sini...")
        self.search_bar.textChanged.connect(self.filter_packages)
        layout.addWidget(self.search_bar)
        
        self.tabs = QTabWidget(self)
        self.list_user = QListWidget()
        self.list_system = QListWidget()
        
        self.tabs.addTab(self.list_user, "Aplikasi User")
        self.tabs.addTab(self.list_system, "Aplikasi System (Bloatware)")
        layout.addWidget(self.tabs)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Muat Ulang", self)
        self.btn_refresh.setStyleSheet("background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px; border: 1px solid rgba(157, 78, 221, 0.4); font-weight: 600;")
        self.btn_refresh.clicked.connect(self.load_packages)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_uninstall = QPushButton("🗑️ Hapus Aplikasi", self)
        self.btn_uninstall.setStyleSheet("background: rgba(232, 17, 35, 0.25); color: #FF4D4D; padding: 10px; border-radius: 6px; border: 1px solid rgba(232,17,35,0.4); font-weight: bold;")
        self.btn_uninstall.clicked.connect(self.uninstall_selected)
        btn_layout.addWidget(self.btn_uninstall)
        
        layout.addLayout(btn_layout)
        self.load_packages()

    def load_packages(self):
        self.list_user.clear()
        self.list_system.clear()
        self.raw_user_apps = []
        self.raw_system_apps = []
        self.search_bar.clear()
        
        try:
            out_user = subprocess.check_output(["adb", "-s", self.device_id, "shell", "pm", "list", "packages", "-3"]).decode("utf-8")
            for line in out_user.strip().split("\n"):
                if line.startswith("package:"):
                    pkg = line.replace("package:", "").strip()
                    self.raw_user_apps.append(pkg)
                    self.list_user.addItem(pkg)
            
            out_sys = subprocess.check_output(["adb", "-s", self.device_id, "shell", "pm", "list", "packages", "-s"]).decode("utf-8")
            for line in out_sys.strip().split("\n"):
                if line.startswith("package:"):
                    pkg = line.replace("package:", "").strip()
                    self.raw_system_apps.append(pkg)
                    self.list_system.addItem(pkg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membaca daftar aplikasi:\n{e}")

    def filter_packages(self, text):
        search_text = text.lower()
        self.list_user.clear()
        for pkg in self.raw_user_apps:
            if search_text in pkg.lower():
                self.list_user.addItem(pkg)
                
        self.list_system.clear()
        for pkg in self.raw_system_apps:
            if search_text in pkg.lower():
                self.list_system.addItem(pkg)

    def uninstall_selected(self):
        current_list = self.list_user if self.tabs.currentIndex() == 0 else self.list_system
        selected_item = current_list.currentItem()
        
        if not selected_item:
            QMessageBox.warning(self, "Peringatan", "Pilih aplikasi terlebih dahulu!")
            return
            
        package_name = selected_item.text()
        reply = QMessageBox.question(self, "Konfirmasi", f"Hapus package ini?\n\n{package_name}", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                if self.tabs.currentIndex() == 0:
                    cmd = ["adb", "-s", self.device_id, "uninstall", package_name]
                else:
                    cmd = ["adb", "-s", self.device_id, "shell", "pm", "uninstall", "-k", "--user", "0", package_name]
                
                output = subprocess.check_output(cmd).decode("utf-8")
                QMessageBox.information(self, "Sukses", f"Hasil:\n{output}")
                self.load_packages()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus:\n{e}")

class DeviceCard(QFrame):
    def __init__(self, device_id, main_wall, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.main_wall = main_wall
        self.setObjectName("DeviceCard")
        self.setStyleSheet(DEVICE_CARD_STYLE)
        
        # Fitur Baru: Grid dalam Grid (Sub-grid layout agar pas presisi di dalam bingkai ungu)
        self.card_grid = QGridLayout(self)
        self.card_grid.setContentsMargins(2, 2, 2, 2)
        self.card_grid.setSpacing(0)
        
        self.video_frame = QWidget(self)
        self.video_frame.setObjectName("VideoFrame")
        
        # Ukuran Layar disesuaikan penuh untuk resolusi kelas tinggi 1680p (skala 16:9 murni)
        self.video_frame.setMinimumSize(QSize(472, 840)) 
        
        self.card_grid.addWidget(self.video_frame, 0, 0)
        
        self.embed_timer = QTimer(self)
        self.embed_timer.setInterval(200)
        self.embed_timer.timeout.connect(self.try_embed_window)
        self.scrcpy_title = f"scrcpy_{self.device_id}"

    def start_embedding(self):
        self.embed_timer.start()

    def try_embed_window(self):
        if not IS_WINDOWS:
            self.embed_timer.stop()
            return

        hwnd = win32gui.FindWindow(None, self.scrcpy_title)
        if hwnd:
            self.embed_timer.stop()
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style = style & ~win32con.WS_POPUP & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            
            window = QWindow.fromWinId(hwnd)
            widget = QWidget.createWindowContainer(window, self.video_frame)
            widget.setGeometry(self.video_frame.rect())
            widget.show()
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

class GlassDeviceWall(QWidget):
    def __init__(self, device_ids):
        super().__init__()
        # Maksimal 20 Device terdeteksi simultan
        self.device_ids = device_ids[:20]
        self.processes = []
        self.cards = []
        
        # Konfigurasi Paginasi 4 perangkat per halaman (Layout grid 2x2)
        self.current_page = 0
        self.items_per_page = 4
        
        self.config_res = "1680" # Default diset langsung ke opsi rendering 1680p
        self.config_fps = "Auto"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Android Ultra Device Wall - 1680p Native Grid")
        self.resize(1400, 920)
        self.setStyleSheet(GLASS_STYLE)
        
        bg_widget = QWidget(self)
        bg_widget.setObjectName("MainBackground")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(bg_widget)
        
        content_layout = QVBoxLayout(bg_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # --- HEADER CONTROL BAR UTAMA ---
        header_layout = QHBoxLayout()
        title_label = QLabel("Android Mirror Wall", self)
        title_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Devices Connected:", self))
        self.combo_all_connected = QComboBox(self)
        if self.device_ids:
            self.combo_all_connected.addItems(self.device_ids)
        else:
            self.combo_all_connected.addItem("Tidak Ada HP Terdeteksi")
        header_layout.addWidget(self.combo_all_connected)
        
        # KONTROL HALAMAN (PAGINASI)
        self.btn_prev = QPushButton("⬅️ Prev Page", self)
        self.btn_prev.setStyleSheet("QPushButton { background: rgba(255,255,255,0.05); border: 1px solid #9D4EDD; padding: 6px 12px; border-radius: 6px; } QPushButton:hover { background: #9D4EDD; }")
        self.btn_prev.clicked.connect(self.prev_page)
        header_layout.addWidget(self.btn_prev)
        
        self.lbl_page_indicator = QLabel("Page 1 / 1", self)
        self.lbl_page_indicator.setStyleSheet("font-weight: bold; color: #9D4EDD; padding: 0px 5px;")
        header_layout.addWidget(self.lbl_page_indicator)
        
        self.btn_next = QPushButton("Next Page ➡️", self)
        self.btn_next.setStyleSheet("QPushButton { background: rgba(255,255,255,0.05); border: 1px solid #9D4EDD; padding: 6px 12px; border-radius: 6px; } QPushButton:hover { background: #9D4EDD; }")
        self.btn_next.clicked.connect(self.next_page)
        header_layout.addWidget(self.btn_next)
        
        header_layout.addSpacing(15)
        
        if self.device_ids:
            self.btn_top_apps = QPushButton("⚙️ Manage Apps", self)
            self.btn_top_apps.setStyleSheet("QPushButton { background: rgba(157, 78, 221, 0.2); border: 1px solid #9D4EDD; padding: 6px 14px; border-radius: 6px; font-weight: 600; } QPushButton:hover { background: #9D4EDD; color: black; }")
            self.btn_top_apps.clicked.connect(self.open_selected_app_manager)
            header_layout.addWidget(self.btn_top_apps)
        
        header_layout.addWidget(QLabel("Res:", self))
        self.combo_res = QComboBox(self)
        self.combo_res.addItems(["1680", "Auto", "1080", "720", "480"])
        self.combo_res.currentIndexChanged.connect(self.update_settings_and_restart)
        header_layout.addWidget(self.combo_res)
        
        self.btn_sideload = QPushButton("📥 Sideload Massal", self)
        self.btn_sideload.setStyleSheet("QPushButton { background: rgba(0, 200, 83, 0.15); border: 1px solid #00C853; padding: 6px 12px; border-radius: 6px; font-weight: 600; } QPushButton:hover { background: #00C853; color: black; }")
        self.btn_sideload.clicked.connect(self.mass_sideload_apk)
        header_layout.addWidget(self.btn_sideload)
        
        content_layout.addLayout(header_layout)
        
        if not self.device_ids:
            no_device_lbl = QLabel("⚠️ Tidak Ada HP Fisik Terdeteksi!\n\nHubungkan kabel USB data ke PC Anda, pastikan USB Debugging di HP aktif.", self)
            no_device_lbl.setAlignment(Qt.AlignCenter)
            no_device_lbl.setStyleSheet("font-size: 14px; color: #FF7373; background: rgba(255,77,77,0.04); border: 1px dashed #FF4D4D; border-radius: 10px; padding: 40px;")
            content_layout.addWidget(no_device_lbl, 1)
            return

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.container_widget)
        content_layout.addWidget(self.scroll_area, 1)
        
        self.update_page_ui()

    def total_pages(self):
        if not self.device_ids:
            return 1
        return (len(self.device_ids) + self.items_per_page - 1) // self.items_per_page

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_ui()

    def next_page(self):
        if self.current_page < self.total_pages() - 1:
            self.current_page += 1
            self.update_page_ui()

    def open_selected_app_manager(self):
        target_device = self.combo_all_connected.currentText()
        if target_device and target_device != "Tidak Ada HP Terdeteksi":
            dialog = AppManagerDialog(target_device, self)
            dialog.exec_()

    def update_page_ui(self):
        """Memperbarui grid utama halaman (Susunan grid murni 2x2 tanpa teks label)"""
        for proc in self.processes:
            proc.terminate()
        self.processes.clear()
        
        for card in self.cards:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.device_ids))
        page_devices = self.device_ids[start_idx:end_idx]
        
        self.lbl_page_indicator.setText(f"Page {self.current_page + 1} / {self.total_pages()}")
        
        cols = 2
        for index, dev_id in enumerate(page_devices):
            row = index // cols
            col = index % cols
            
            # Membuat Card murni tanpa widget label teks di atasnya
            card = DeviceCard(dev_id, self.container_widget)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            
            self.launch_scrcpy_process(dev_id, card)

    def update_settings_and_restart(self):
        self.config_res = self.combo_res.currentText()
        self.update_page_ui()

    def launch_scrcpy_process(self, device_id, card):
        unique_title = f"scrcpy_{device_id}"
        cmd = ["scrcpy", "-s", device_id, "--window-title", unique_title, "--no-audio"]
        
        if not IS_WINDOWS:
            cmd.extend(["--window-x", "0", "--window-y", "0", "--always-on-top"])
        
        if self.config_res != "Auto":
            cmd.extend(["-m", self.config_res])
        if self.config_fps != "Auto":
            cmd.extend(["--max-fps", self.config_fps])
            
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc)
            card.start_embedding()
        except FileNotFoundError:
            pass

    def mass_sideload_apk(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File APK", "", "Android Package (*.apk)")
        if not file_path:
            return
            
        success_count = 0
        fail_devices = []
        
        for dev_id in self.device_ids:
            try:
                res = subprocess.Popen(["adb", "-s", dev_id, "install", "-r", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                res.wait()
                if res.returncode == 0:
                    success_count += 1
                else:
                    fail_devices.append(dev_id)
            except Exception:
                fail_devices.append(dev_id)
                
        msg = f"🚀 Sideload APK Selesai!\n\nBerhasil Terinstal: {success_count} Perangkat."
        if fail_devices:
            msg += f"\nGagal di perangkat: {', '.join(fail_devices)}"
        QMessageBox.information(self, "Status Sideload", msg)

    def closeEvent(self, event):
        for proc in self.processes: 
            proc.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    device_list = []
    try:
        output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        for line in output.strip().split("\n")[1:]:
            if "device" in line and not line.startswith("*"):
                parts = line.split()
                if len(parts) > 0 and parts[1] == "device":
                    device_list.append(parts[0])
    except Exception as e:
        print(f"Error ADB: {e}")

    window = GlassDeviceWall(device_list)
    window.showMaximized()
    sys.exit(app.exec_())