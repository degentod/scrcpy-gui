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

# STYLE: Cyberpunk Glassmorphism
GLASS_STYLE = """
    QWidget {
        background-color: transparent;
        color: #FFFFFF;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QWidget #MainBackground {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f111a, stop:1 #181a26);
    }
    QScrollArea {
        border: none;
        background-color: transparent;
    }
    QScrollBar:vertical {
        border: none;
        background: rgba(255, 255, 255, 0.02);
        width: 8px;
    }
    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    QTabWidget::panel {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.03);
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
        background: rgba(0, 163, 255, 0.2);
        border-color: rgba(0, 163, 255, 0.5);
    }
    QComboBox, QLineEdit, QListWidget {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 6px;
        color: #FFF;
    }
    QComboBox::drop-down { border: none; }
    QListWidget::item:hover { background-color: rgba(255, 255, 255, 0.08); }
    QListWidget::item:selected { background-color: rgba(0, 163, 255, 0.3); }
"""

DEVICE_CARD_STYLE = """
    QFrame #DeviceCard {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
    }
    QFrame #DeviceCard:hover {
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(0, 163, 255, 0.5);
    }
    QLabel #DeviceTitle {
        color: #E0E0E0;
        font-size: 11px;
        font-weight: 600;
        padding: 6px;
        background-color: rgba(0, 0, 0, 0.5);
        border-top-left-radius: 11px;
        border-top-right-radius: 11px;
    }
    QWidget #VideoFrame {
        background-color: #000000;
        border-bottom-left-radius: 11px;
        border-bottom-right-radius: 11px;
    }
"""

class AppManagerDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle(f"App Manager - Perangkat {device_id}")
        self.resize(500, 600)
        self.setStyleSheet(GLASS_STYLE)
        
        layout = QVBoxLayout(self)
        lbl_info = QLabel(f"📦 Manajemen Aplikasi: {device_id}", self)
        lbl_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3ff;")
        layout.addWidget(lbl_info)
        
        self.tabs = QTabWidget(self)
        self.list_user = QListWidget()
        self.list_system = QListWidget()
        
        self.tabs.addTab(self.list_user, "Aplikasi Pengguna (User)")
        self.tabs.addTab(self.list_system, "Aplikasi Bawaan (System/Bloatware)")
        layout.addWidget(self.tabs)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Muat Ulang", self)
        self.btn_refresh.setStyleSheet("background: rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2);")
        self.btn_refresh.clicked.connect(self.load_packages)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_uninstall = QPushButton("🗑️ Hapus Aplikasi", self)
        self.btn_uninstall.setStyleSheet("background: rgba(232, 17, 35, 0.3); color: #FF4D4D; padding: 8px; border-radius: 6px; border: 1px solid rgba(232,17,35,0.4); font-weight: bold;")
        self.btn_uninstall.clicked.connect(self.uninstall_selected)
        btn_layout.addWidget(self.btn_uninstall)
        
        layout.addLayout(btn_layout)
        self.load_packages()

    def load_packages(self):
        self.list_user.clear()
        self.list_system.clear()
        try:
            out_user = subprocess.check_output(["adb", "-s", self.device_id, "shell", "pm", "list", "packages", "-3"]).decode("utf-8")
            for line in out_user.strip().split("\n"):
                if line.startswith("package:"):
                    self.list_user.addItem(line.replace("package:", "").strip())
            
            out_sys = subprocess.check_output(["adb", "-s", self.device_id, "shell", "pm", "list", "packages", "-s"]).decode("utf-8")
            for line in out_sys.strip().split("\n"):
                if line.startswith("package:"):
                    self.list_system.addItem(line.replace("package:", "").strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membaca daftar aplikasi:\n{e}")

    def uninstall_selected(self):
        current_list = self.list_user if self.tabs.currentIndex() == 0 else self.list_system
        selected_item = current_list.currentItem()
        
        if not selected_item:
            QMessageBox.warning(self, "Peringatan", "Pilih aplikasi yang ingin dihapus terlebih dahulu!")
            return
            
        package_name = selected_item.text()
        reply = QMessageBox.question(self, "Konfirmasi Hapus", f"Apakah Anda yakin menghapus?\n\n{package_name}", QMessageBox.Yes | QMessageBox.No)
        
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
                QMessageBox.critical(self, "Error", f"Gagal menghapus aplikasi:\n{e}")

class DeviceCard(QFrame):
    def __init__(self, device_id, count, main_wall, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.main_wall = main_wall
        self.setObjectName("DeviceCard")
        self.setStyleSheet(DEVICE_CARD_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        title_layout = QHBoxLayout()
        self.lbl_title = QLabel(f"[{count}] {device_id[:10]}", self)
        self.lbl_title.setObjectName("DeviceTitle")
        title_layout.addWidget(self.lbl_title, 1)
        
        self.btn_manage = QPushButton("⚙️ Apps", self)
        self.btn_manage.setStyleSheet("QPushButton { font-size: 10px; background: rgba(0,163,255,0.2); border: 1px solid rgba(0,163,255,0.4); border-radius: 4px; padding: 2px 6px; color:#FFF;} QPushButton:hover { background: rgba(0,163,255,0.6); }")
        self.btn_manage.clicked.connect(self.open_app_manager)
        title_layout.addWidget(self.btn_manage)
        
        header_frame = QWidget()
        header_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border-top-left-radius: 11px; border-top-right-radius: 11px;")
        hf_layout = QHBoxLayout(header_frame)
        hf_layout.setContentsMargins(6, 4, 6, 4)
        hf_layout.addLayout(title_layout)
        layout.addWidget(header_frame)
        
        self.video_frame = QWidget(self)
        self.video_frame.setObjectName("VideoFrame")
        self.video_frame.setMinimumSize(QSize(135, 240))
        layout.addWidget(self.video_frame)
        
        self.embed_timer = QTimer(self)
        self.embed_timer.setInterval(250)
        self.embed_timer.timeout.connect(self.try_embed_window)
        self.scrcpy_title = f"scrcpy_{self.device_id}"

    def open_app_manager(self):
        dialog = AppManagerDialog(self.device_id, self)
        dialog.exec_()

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
        self.device_ids = device_ids[:10]
        self.processes = []
        self.cards = []
        
        self.config_res = "Auto"
        self.config_fps = "Auto"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cyber Glass Control Panel - Android Device Wall")
        self.resize(1280, 760)
        self.setStyleSheet(GLASS_STYLE)
        
        bg_widget = QWidget(self)
        bg_widget.setObjectName("MainBackground")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(bg_widget)
        
        content_layout = QVBoxLayout(bg_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Android Device Wall", self)
        title_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        header_layout.addWidget(QLabel("Resolusi:", self))
        self.combo_res = QComboBox(self)
        self.combo_res.addItems(["Auto", "1080", "720", "480", "360"])
        self.combo_res.currentIndexChanged.connect(self.update_settings_and_restart)
        header_layout.addWidget(self.combo_res)
        
        header_layout.addWidget(QLabel("FPS:", self))
        self.combo_fps = QComboBox(self)
        self.combo_fps.addItems(["Auto", "60", "30", "20", "12"])
        self.combo_fps.currentIndexChanged.connect(self.update_settings_and_restart)
        header_layout.addWidget(self.combo_fps)
        
        self.btn_sideload = QPushButton("📥 Sideload Massal (APK)", self)
        self.btn_sideload.setStyleSheet("QPushButton { background: rgba(0, 200, 83, 0.2); border: 1px solid #00C853; padding: 6px 14px; border-radius: 15px; font-weight: 600; } QPushButton:hover { background: #00C853; color: black; }")
        self.btn_sideload.clicked.connect(self.mass_sideload_apk)
        header_layout.addWidget(self.btn_sideload)
        
        stats_label = QLabel(f"Connected: {len(self.device_ids)}/10", self)
        stats_label.setStyleSheet("font-size: 13px; color: #00a3ff; font-weight: 600; background: rgba(0,163,255,0.08); padding: 5px 12px; border-radius: 15px; border: 1px solid rgba(0,163,255,0.2);")
        header_layout.addWidget(stats_label)
        content_layout.addLayout(header_layout)
        
        if not self.device_ids:
            no_device_lbl = QLabel("⚠️ Tidak Ada HP Fisik Terdeteksi!\n\nHubungkan ponsel dengan kabel data berkualitas, lalu nyalakan USB Debugging.", self)
            no_device_lbl.setAlignment(Qt.AlignCenter)
            no_device_lbl.setStyleSheet("font-size: 15px; color: #FF7373; font-weight: 600; line-height: 26px; background: rgba(255,77,77,0.04); border: 1px dashed rgba(255,77,77,0.2); border-radius: 14px; padding: 50px;")
            content_layout.addWidget(no_device_lbl, 1)
            return

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(14)
        
        self.start_all_streams()
        
        self.scroll_area.setWidget(self.container_widget)
        content_layout.addWidget(self.scroll_area)

    def start_all_streams(self):
        for proc in self.processes:
            proc.terminate()
        self.processes.clear()
        
        for card in self.cards:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        
        cols = 5
        for index, dev_id in enumerate(self.device_ids):
            row = index // cols
            col = index % cols
            
            card = DeviceCard(dev_id, index + 1, self, self.container_widget)
            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            
            self.launch_scrcpy_process(dev_id, card)

    def update_settings_and_restart(self):
        self.config_res = self.combo_res.currentText()
        self.config_fps = self.combo_fps.currentText()
        self.start_all_streams()

    def launch_scrcpy_process(self, device_id, card):
        unique_title = f"scrcpy_{device_id}"
        cmd = ["scrcpy", "-s", device_id, "--window-title", unique_title, "--no-audio"]
        
        # Jika bukan di Windows, scrcpy tidak bisa di-embed rapi di dalam layout PyQt.
        # Kita paksa scrcpy berjalan sebagai window borderless melayang terpisah di Linux/Mac.
        if not IS_WINDOWS:
            cmd.extend(["--window-x", "0", "--window-y", "0", "--always-on-top"])
        else:
            cmd.append("--no-control")
        
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Aplikasi Android (APK)", "", "Android Package (*.apk)")
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
                
        msg = f"🚀 Sideload Selesai!\n\nBerhasil Terinstal: {success_count} Perangkat."
        if fail_devices:
            msg += f"\nGagal di perangkat: {', '.join(fail_devices)}"
        QMessageBox.information(self, "Status Sideload APK", msg)

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