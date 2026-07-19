import sys
import math
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect

class RainXLoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        # 1. Pengaturan Jendela (Frameless & Transparan)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 300)
        
        # 2. Layout Utama
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Layout untuk Logo (rain + X)
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(2)
        
        # 3. Komponen Teks "rain"
        self.lbl_rain = QLabel("rain")
        font_rain = QFont("Segoe UI", 48, QFont.Weight.Light)
        self.lbl_rain.setFont(font_rain)
        self.lbl_rain.setStyleSheet("color: #A0A0A5;") # Dark Charcoal text
        
        # 4. Komponen Simbol "X"
        self.lbl_x = QLabel("X")
        font_x = QFont("Segoe UI", 48, QFont.Weight.ExtraBold)
        self.lbl_x.setFont(font_x)
        self.lbl_x.setStyleSheet("color: #00E5FF;") # Electric Blue
        
        # Efek Pendaran (Glow) pada huruf X - Sekarang diimpor dengan benar dari QtWidgets
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(20)
        glow_effect.setColor(QColor("#00E5FF"))
        glow_effect.setOffset(0, 0)
        self.lbl_x.setGraphicsEffect(glow_effect)
        
        # Masukkan ke layout logo
        logo_layout.addWidget(self.lbl_rain)
        logo_layout.addWidget(self.lbl_x)
        
        # 5. Teks Indikator Loading
        self.lbl_loading = QLabel("LOADING ASSETS...")
        font_loading = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
        font_loading.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        self.lbl_loading.setFont(font_loading)
        self.lbl_loading.setStyleSheet("color: #55555A; margin-top: 20px;")
        self.lbl_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Masukkan semua ke layout utama
        main_layout.addLayout(logo_layout)
        main_layout.addWidget(self.lbl_loading)
        self.setLayout(main_layout)
        
        # 6. Setup Animasi Membesar (Scale/Font Size) pada Huruf X
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_x)
        self.anim_timer.start(20) # Update setiap 20ms untuk kehalusan gerakan
        
        self.time_counter = 0.0
        
        # 7. Timer Simulasi untuk Menutup Loading Screen (Selesai Memuat Software)
        # Layar akan otomatis menutup setelah 5 detik
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.finish_loading)
        self.close_timer.start(5000) 

    def animate_x(self):
        self.time_counter += 0.05
        
        # Menggunakan rumus Sinus agar animasi membesar & mengecil berulang secara mulus (loop)
        # Ukuran dasar font 48, membesar hingga kisaran ~60 (sekitar 125%)
        dynamic_size = int(48 + (math.sin(self.time_counter) + 1) * 6)
        
        font = self.lbl_x.font()
        font.setPointSize(dynamic_size)
        self.lbl_x.setFont(font)
        
    def finish_loading(self):
        self.anim_timer.stop()
        self.close_timer.stop()
        self.close()
        print("Software rainX Siap Digunakan!")
        # Di sini kamu bisa memanggil window utama aplikasimu nantinya

    # Membuat latar belakang jendela tetap bundar/custom matte black
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#121214"))) # Background Matte Black
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15) # Sudut rounded lembut

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    loading_screen = RainXLoadingScreen()
    # Posisikan di tengah layar monitor pengguna saat aplikasi dibuka
    loading_screen.show()
    
    sys.exit(app.exec())