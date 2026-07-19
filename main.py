import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QSize

MODERN_STYLE = """
    QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Arial, sans-serif; }
    QScrollArea { border: none; background-color: #121212; }
    QScrollBar:vertical { border: none; background: #1E1E1E; width: 10px; }
    QScrollBar::handle:vertical { background: #333333; min-height: 20px; border-radius: 5px; }
    QScrollBar::handle:vertical:hover { background: #4F4F4F; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""

DEVICE_CARD_STYLE = """
    QFrame #DeviceCard { background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 8px; }
    QFrame #DeviceCard:hover { border: 1px solid #0078D4; background-color: #252525; }
    QLabel #DeviceTitle { color: #FFFFFF; font-size: 11px; font-weight: 600; padding: 4px; background-color: #2D2D2D; border-top-left-radius: 7px; border-top-right-radius: 7px; }
    QWidget #VideoFrame { background-color: #000000; border-bottom-left-radius: 7px; border-bottom-right-radius: 7px; }
"""

class DeviceCard(QFrame):
    def __init__(self, device_id, count, parent=None):
        super().__init__(parent)
        self.setObjectName("DeviceCard")
        self.setStyleSheet(DEVICE_CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.lbl_title = QLabel(f"[{count}] 📱 {device_id}", self)
        self.lbl_title.setObjectName("DeviceTitle")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_title)
        
        self.video_frame = QWidget(self)
        self.video_frame.setObjectName("VideoFrame")
        self.video_frame.setMinimumSize(QSize(108, 192)) 
        layout.addWidget(self.video_frame)

class ModernDeviceWall(QWidget):
    def __init__(self, device_ids):
        super().__init__()
        self.device_ids = device_ids
        self.processes = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Control Panel - Android Device Wall")
        self.resize(1440, 900)
        self.setStyleSheet(MODERN_STYLE)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header Panel
        header_layout = QHBoxLayout()
        title_label = QLabel("Android Device Wall", self)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        stats_label = QLabel(f"Connected Devices: {len(self.device_ids)}", self)
        stats_label.setStyleSheet("font-size: 14px; color: #0078D4; font-weight: bold; padding-right: 10px;")
        header_layout.addWidget(stats_label)
        
        btn_close = QPushButton("Close All", self)
        btn_close.setStyleSheet("QPushButton { background-color: #A80000; color: white; border: none; padding: 8px 16px; font-weight: bold; border-radius: 4px; } QPushButton:hover { background-color: #E81123; }")
        btn_close.clicked.connect(self.close)
        header_layout.addWidget(btn_close)
        main_layout.addLayout(header_layout)
        
        # Layar Peringatan Jika Tidak Ada HP Colok
        if not self.device_ids:
            no_device_lbl = QLabel("⚠️ Tidak Ada Perangkat Terdeteksi!\n\nPastikan HP sudah dicolok menggunakan kabel data berkualitas,\ndan fitur 'USB Debugging' di Opsi Pengembang sudah aktif.", self)
            no_device_lbl.setAlignment(Qt.AlignCenter)
            no_device_lbl.setStyleSheet("font-size: 16px; color: #FF4D4D; font-weight: bold; line-height: 25px;")
            main_layout.addWidget(no_device_lbl, 1)
            self.setLayout(main_layout)
            return

        # Grid Perangkat Asli
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        container_widget = QWidget()
        grid_layout = QGridLayout(container_widget)
        grid_layout.setContentsMargins(5, 5, 5, 5)
        grid_layout.setSpacing(12)
        
        cols = 10 
        for index, dev_id in enumerate(self.device_ids):
            row = index // cols
            col = index % cols
            
            card = DeviceCard(dev_id, index + 1, container_widget)
            grid_layout.addWidget(card, row, col)
            self.start_scrcpy(dev_id, card.video_frame)
            
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def start_scrcpy(self, device_id, target_widget):
        unique_title = f"scrcpy_{device_id}"
        # Konfigurasi optimal tanpa GPU untuk kestabilan multi-device
        cmd = [
            "scrcpy", 
            "-s", device_id, 
            "-m", "360", 
            "-b", "300k", 
            "--max-fps", "12", 
            "--no-audio", 
            "--no-control", 
            "--window-title", unique_title
        ]
        
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes.append(proc)
        except FileNotFoundError:
            target_widget.setStyleSheet("background-color: #2D1A1A; border-radius: 7px;")
            lbl_err = QLabel("scrcpy\nMissing", target_widget)
            lbl_err.setAlignment(Qt.AlignCenter)
            lbl_err.setStyleSheet("color: #FF4D4D; font-size: 10px; font-weight: bold;")
            err_layout = QVBoxLayout(target_widget)
            err_layout.addWidget(lbl_err)

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
        print(f"Error mendeteksi perangkat ADB: {e}")

    device_list = device_list[:50] # Batasi maks 50 perangkat (grid 5x10)
    
    window = ModernDeviceWall(device_list)
    window.showMaximized()
    sys.exit(app.exec_())