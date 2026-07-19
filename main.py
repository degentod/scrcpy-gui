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

# STYLE: iTunes & 3uTools Modern Light Edition
LIGHT_THEME_STYLE = """
    QWidget {
        background-color: transparent;
        color: #333333;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    }
    QWidget #MainBackground {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F2F2F7);
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        border: none;
        background: #E5E5EA;
        width: 8px;
        height: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background: #C7C7CC;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
        background: #8E8E93;
    }
    QTabWidget::panel {
        border: 1px solid #D1D1D6;
        background: #FFFFFF;
        border-radius: 6px;
    }
    QTabBar::tab {
        background: #E5E5EA;
        border: 1px solid #D1D1D6;
        padding: 6px 14px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        margin-right: 2px;
        color: #555555;
    }
    QTabBar::tab:selected {
        background: #FFFFFF;
        border-bottom-color: #FFFFFF;
        color: #007AFF;
        font-weight: bold;
    }
    QComboBox, QLineEdit, QListWidget {
        background-color: #FFFFFF;
        border: 1px solid #C7C7CC;
        border-radius: 5px;
        padding: 5px 10px;
        color: #333333;
        font-size: 13px;
    }
    QComboBox:hover, QLineEdit:hover {
        border: 1px solid #007AFF;
    }
    QComboBox::drop-down {
        border: none;
    }
    QListWidget::item {
        padding: 4px;
        color: #333333;
    }
    QListWidget::item:hover {
        background-color: #E5E5EA;
        border-radius: 4px;
    }
    QListWidget::item:selected {
        background-color: #007AFF;
        color: #FFFFFF;
        border-radius: 4px;
    }
    QLabel {
        color: #1C1C1E;
        font-size: 13px;
    }
"""

DEVICE_CARD_STYLE = """
    QFrame #DeviceCard {
        background-color: #FFFFFF;
        border: 3px solid #8E44AD;
        border-radius: 8px;
    }
    QWidget #VideoFrame {
        background-color: #F8F9FA;
        border-radius: 5px;
    }
"""

class PasscodeUnlockDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle(f"🔑 Unlock Engine - Perangkat: {device_id}")
        self.resize(460, 320)
        self.setStyleSheet(LIGHT_THEME_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_title = QLabel("🔓 Passcode Bypass / Screen Unlocker", self)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(
            "Pilih metode pemulihan atau simulasi input kunci di bawah ini.\n"
            "Pastikan perangkat merespons ADB dengan benar.", self
        )
        lbl_desc.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(lbl_desc)
        
        self.method_combo = QComboBox(self)
        self.method_combo.addItems([
            "Metode 1: Kirim KeyEvent Swipe Up / Wake",
            "Metode 2: Dismiss Keyguard (Standar ADB)",
            "Metode 3: Force Clear Lock Settings (Membutuhkan Root)",
            "Metode 4: Bypass via Factory Reset (Recovery Mode)"
        ])
        layout.addWidget(self.method_combo)
        
        self.pin_input = QLineEdit(self)
        self.pin_input.setPlaceholderText("Masukkan PIN teks opsional (Jika ingin dikirimkan otomatis)")
        layout.addWidget(self.pin_input)
        
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setStyleSheet("QPushButton { background: #E5E5EA; border-radius: 5px; padding: 8px 20px; font-weight: 600; }")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_exec = QPushButton("⚡ Jalankan Unlock", self)
        self.btn_exec.setStyleSheet("QPushButton { background: #007AFF; color: white; border-radius: 5px; padding: 8px 20px; font-weight: bold; } QPushButton:hover { background: #0056B3; }")
        self.btn_exec.clicked.connect(self.execute_unlock)
        btn_layout.addWidget(self.btn_exec)
        
        layout.addLayout(btn_layout)
        
    def execute_unlock(self):
        method_idx = self.method_combo.currentIndex()
        pin_text = self.pin_input.text().strip()
        
        try:
            if method_idx == 0:
                subprocess.run(["adb", "-s", self.device_id, "shell", "input", "keyevent", "KEYCODE_WAKE"], check=True)
                time.sleep(0.3)
                subprocess.run(["adb", "-s", self.device_id, "shell", "input", "swipe", "300", "1000", "300", "300"], check=True)
                if pin_text:
                    time.sleep(0.5)
                    subprocess.run(["adb", "-s", self.device_id, "shell", "input", "text", pin_text], check=True)
                    subprocess.run(["adb", "-s", self.device_id, "shell", "input", "keyevent", "66"], check=True)
                QMessageBox.information(self, "Sukses", "Perintah KeyEvent Buka Kunci berhasil dikirim.")
                
            elif method_idx == 1:
                subprocess.run(["adb", "-s", self.device_id, "shell", "wm", "dismiss-keyguard"], check=True)
                QMessageBox.information(self, "Sukses", "Instruksi Dismiss Keyguard selesai dieksekusi.")
                
            elif method_idx == 2:
                cmd = ["adb", "-s", self.device_id, "shell", "su", "-c", "rm", "/data/system/password.key", "&&", "rm", "/data/system/gesture.key"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if "not found" in res.stderr or "Permission denied" in res.stderr:
                    QMessageBox.warning(self, "Gagal", "Sistem menolak akses. Perangkat Anda belum di-root atau izin SU ditolak.")
                else:
                    QMessageBox.information(self, "Sukses", "Perintah penghapusan runtime kunci sistem telah dikirim.")
                    
            elif method_idx == 3:
                reply = QMessageBox.question(self, "Konfirmasi Kritis", "Metode ini akan memaksa HP masuk ke mode Pemulihan (Recovery) untuk Wipe Data. Lanjutkan?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    subprocess.run(["adb", "-s", self.device_id, "reboot", "recovery"], check=True)
                    QMessageBox.information(self, "Info", "Perangkat sedang melakukan restart ke Recovery Mode.")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Kesalahan", f"Gagal mengeksekusi operasi bypass:\n{e}")

class AppManagerDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle(f"3uTools Style - App Manager ({device_id})")
        self.resize(550, 650)
        self.setStyleSheet(LIGHT_THEME_STYLE)
        
        self.raw_user_apps = []
        self.raw_system_apps = []
        
        layout = QVBoxLayout(self)
        lbl_info = QLabel(f"📦 Application Manager: {device_id}", self)
        lbl_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #8E44AD; margin-bottom: 5px;")
        layout.addWidget(lbl_info)
        
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Cari / Filter nama package aplikasi di sini...")
        self.search_bar.textChanged.connect(self.filter_packages)
        layout.addWidget(self.search_bar)
        
        self.tabs = QTabWidget(self)
        self.list_user = QListWidget()
        self.list_system = QListWidget()
        
        self.tabs.addTab(self.list_user, "User Installed Apps")
        self.tabs.addTab(self.list_system, "System / Bloatware Apps")
        layout.addWidget(self.tabs)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Refresh List", self)
        self.btn_refresh.setStyleSheet("QPushButton { background: #FFFFFF; border: 1px solid #C7C7CC; padding: 8px 15px; border-radius: 5px; font-weight: 600; } QPushButton:hover { background: #F2F2F7; }")
        self.btn_refresh.clicked.connect(self.load_packages)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_uninstall = QPushButton("🗑️ Uninstall Selected App", self)
        self.btn_uninstall.setStyleSheet("QPushButton { background: #FF3B30; color: #FFFFFF; padding: 8px 15px; border-radius: 5px; font-weight: bold; border: none; } QPushButton:hover { background: #E03B30; }")
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
        reply = QMessageBox.question(self, "Konfirmasi", f"Apakah Anda yakin ingin menghapus aplikasi ini?\n\n{package_name}", QMessageBox.Yes | QMessageBox.No)
        
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
        
        self.card_grid = QGridLayout(self)
        self.card_grid.setContentsMargins(1, 1, 1, 1)
        self.card_grid.setSpacing(0)
        
        self.video_frame = QWidget(self)
        self.video_frame.setObjectName("VideoFrame")
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
        self.device_ids = device_ids[:20]
        self.processes = []
        self.cards = []
        
        self.current_page = 0
        self.items_per_page = 4
        
        self.config_res = "1680"
        self.config_fps = "Auto"
        
        # Variabel Status Fitur Baru
        self.auto_off_screen = False  # Status Awal: Fitur Mati Layar Nonaktif
        self.audio_muted = False      # Status Awal: Audio Aktif (Unmute)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("3uTools Suite Wall Terminal - 1680p Resolution Edition")
        self.resize(1440, 940)
        self.setStyleSheet(LIGHT_THEME_STYLE)
        
        bg_widget = QWidget(self)
        bg_widget.setObjectName("MainBackground")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(bg_widget)
        
        content_layout = QVBoxLayout(bg_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)
        
        # --- TOP CONTROL BAR ---
        header_frame = QFrame(self)
        header_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(10)
        
        title_label = QLabel("iDevice Multi-Control Tool", self)
        title_label.setStyleSheet("font-size: 17px; font-weight: 700; color: #1C1C1E;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # --- TOMBOL AUDIO MUTE/UNMUTE ---
        self.btn_audio_toggle = QPushButton("🔊 Audio: Unmute", self)
        self.btn_audio_toggle.setStyleSheet("QPushButton { background: #E5E5EA; border: 1px solid #C7C7CC; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
        self.btn_audio_toggle.clicked.connect(self.toggle_audio_setting)
        header_layout.addWidget(self.btn_audio_toggle)

        # --- TOMBOL FITUR OTOMATIS LAYAR MATI/HIDUP ---
        self.btn_screen_toggle = QPushButton("📱 Auto-Off Layar: OFF", self)
        self.btn_screen_toggle.setStyleSheet("QPushButton { background: #E5E5EA; border: 1px solid #C7C7CC; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
        self.btn_screen_toggle.clicked.connect(self.toggle_screen_setting)
        header_layout.addWidget(self.btn_screen_toggle)
        
        header_layout.addSpacing(10)
        
        header_layout.addWidget(QLabel("Target Device:", self))
        self.combo_all_connected = QComboBox(self)
        if self.device_ids:
            self.combo_all_connected.addItems(self.device_ids)
        else:
            self.combo_all_connected.addItem("No Device Connected")
        header_layout.addWidget(self.combo_all_connected)
        
        if self.device_ids:
            self.btn_unlock_screen = QPushButton("🔑 Unlock Passcode", self)
            self.btn_unlock_screen.setStyleSheet("QPushButton { background: #FFFFFF; border: 1px solid #007AFF; color: #007AFF; padding: 5px 12px; border-radius: 5px; font-weight: 600; } QPushButton:hover { background: #007AFF; color: #FFFFFF; }")
            self.btn_unlock_screen.clicked.connect(self.open_passcode_unlocker)
            header_layout.addWidget(self.btn_unlock_screen)

            self.btn_top_apps = QPushButton("⚙️ Manage Apps", self)
            self.btn_top_apps.setStyleSheet("QPushButton { background: #FFFFFF; border: 1px solid #8E44AD; color: #8E44AD; padding: 5px 12px; border-radius: 5px; font-weight: 600; } QPushButton:hover { background: #8E44AD; color: #FFFFFF; }")
            self.btn_top_apps.clicked.connect(self.open_selected_app_manager)
            header_layout.addWidget(self.btn_top_apps)
            
        header_layout.addSpacing(5)
        
        self.btn_prev = QPushButton("◀️ Prev", self)
        self.btn_prev.setStyleSheet("QPushButton { background: #FFFFFF; border: 1px solid #C7C7CC; padding: 5px 10px; border-radius: 5px; } QPushButton:hover { background: #E5E5EA; }")
        self.btn_prev.clicked.connect(self.prev_page)
        header_layout.addWidget(self.btn_prev)
        
        self.lbl_page_indicator = QLabel("Page 1 / 1", self)
        self.lbl_page_indicator.setAlignment(Qt.AlignCenter)
        self.lbl_page_indicator.setStyleSheet("font-weight: bold; color: #8E44AD; min-width: 60px;")
        header_layout.addWidget(self.lbl_page_indicator)
        
        self.btn_next = QPushButton("Next ▶️", self)
        self.btn_next.setStyleSheet("QPushButton { background: #FFFFFF; border: 1px solid #C7C7CC; padding: 5px 10px; border-radius: 5px; } QPushButton:hover { background: #E5E5EA; }")
        self.btn_next.clicked.connect(self.next_page)
        header_layout.addWidget(self.btn_next)
        
        header_layout.addSpacing(5)
        
        header_layout.addWidget(QLabel("Res:", self))
        self.combo_res = QComboBox(self)
        self.combo_res.addItems(["1680", "Auto", "1080", "720", "480"])
        self.combo_res.currentIndexChanged.connect(self.update_settings_and_restart)
        header_layout.addWidget(self.combo_res)
        
        self.btn_sideload = QPushButton("📥 Batch Install APK", self)
        self.btn_sideload.setStyleSheet("QPushButton { background: #007AFF; color: #FFFFFF; padding: 6px 14px; border-radius: 5px; font-weight: 600; border: none; } QPushButton:hover { background: #0056B3; }")
        self.btn_sideload.clicked.connect(self.mass_sideload_apk)
        header_layout.addWidget(self.btn_sideload)
        
        content_layout.addWidget(header_frame)
        
        if not self.device_ids:
            no_device_lbl = QLabel("⚠️ Tidak Ada Perangkat Terdeteksi.\n\nHubungkan ponsel dengan kabel USB dan pastikan USB Debugging aktif.", self)
            no_device_lbl.setAlignment(Qt.AlignCenter)
            no_device_lbl.setStyleSheet("font-size: 14px; color: #FF3B30; background: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 8px; padding: 60px;")
            content_layout.addWidget(no_device_lbl, 1)
            return

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setContentsMargins(0, 5, 0, 5)
        self.grid_layout.setSpacing(12)
        
        self.scroll_area.setWidget(self.container_widget)
        content_layout.addWidget(self.scroll_area, 1)
        
        self.update_page_ui()

    # --- LOGIKA HANDLER AUDIO MUTE/UNMUTE ---
    def toggle_audio_setting(self):
        self.audio_muted = not self.audio_muted
        if self.audio_muted:
            self.btn_audio_toggle.setText("🔇 Audio: Mute")
            self.btn_audio_toggle.setStyleSheet("QPushButton { background: #FF3B30; color: white; border: 1px solid #FF3B30; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
        else:
            self.btn_audio_toggle.setText("🔊 Audio: Unmute")
            self.btn_audio_toggle.setStyleSheet("QPushButton { background: #E5E5EA; border: 1px solid #C7C7CC; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
        self.update_page_ui()

    # --- LOGIKA HANDLER OTOMATIS MATI/HIDUP LAYAR ---
    def toggle_screen_setting(self):
        self.auto_off_screen = not self.auto_off_screen
        if self.auto_off_screen:
            self.btn_screen_toggle.setText("📱 Auto-Off Layar: ON")
            self.btn_screen_toggle.setStyleSheet("QPushButton { background: #34C759; color: white; border: 1px solid #34C759; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
        else:
            self.btn_screen_toggle.setText("📱 Auto-Off Layar: OFF")
            self.btn_screen_toggle.setStyleSheet("QPushButton { background: #E5E5EA; border: 1px solid #C7C7CC; padding: 5px 12px; border-radius: 5px; font-weight: 600; }")
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
        if target_device and target_device != "No Device Connected":
            dialog = AppManagerDialog(target_device, self)
            dialog.exec_()

    def open_passcode_unlocker(self):
        target_device = self.combo_all_connected.currentText()
        if target_device and target_device != "No Device Connected":
            dialog = PasscodeUnlockDialog(target_device, self)
            dialog.exec_()

    def update_page_ui(self):
        # Saat dimatikan/diganti halamannya, scrcpy akan di-terminate. 
        # Secara otomatis, jika argumen --turn-screen-off dipakai, scrcpy akan membangunkan layar HP kembali saat terputus.
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
        
        self.lbl_page_indicator.setText(f"{self.current_page + 1} / {self.total_pages()}")
        
        cols = 2
        for index, dev_id in enumerate(page_devices):
            row = index // cols
            col = index % cols
            
            card = DeviceCard(dev_id, self.container_widget)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            
            self.launch_scrcpy_process(dev_id, card)

    def update_settings_and_restart(self):
        self.config_res = self.combo_res.currentText()
        self.update_page_ui()

    def launch_scrcpy_process(self, device_id, card):
        unique_title = f"scrcpy_{device_id}"
        cmd = ["scrcpy", "-s", device_id, "--window-title", unique_title]
        
        # Implementasi Kondisi Suara (Mute / Unmute)
        if self.audio_muted:
            cmd.append("--no-audio")
        
        # Implementasi Fitur Layar Otomatis (Matikan Layar saat Terkoneksi)
        if self.auto_off_screen:
            cmd.append("--turn-screen-off")
            cmd.append("--stay-awake")
        
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Installation File (APK)", "", "Android Package (*.apk)")
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
                
        msg = f"🚀 Batch Installation Complete!\n\nSuccessfully Installed: {success_count} Devices."
        if fail_devices:
            msg += f"\nFailed Devices: {', '.join(fail_devices)}"
        QMessageBox.information(self, "Installation Status", msg)

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