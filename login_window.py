import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect

class LoginWindow(QMainWindow):
    login_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Liste des mots de passe valides
        self.valid_passwords = ["wassrami1234", "tarhou1234", "madhad1234"]
        self.init_ui()
        
    def init_ui(self):
        # Configuration de la fenêtre
        self.setWindowTitle("CPI TOOL V 3 - Login")
        self.setFixedSize(615, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Couleur de fond noir
        self.setStyleSheet("background-color: #000000;")
        
        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Widget vidéo (partie supérieure)
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(615, 400)  # Hauteur de la vidéo
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #000000;
                border: none;
            }
        """)
        main_layout.addWidget(self.video_widget)
        
        # Configuration du lecteur vidéo
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Widget pour le formulaire de login (partie inférieure)
        login_widget = QWidget()
        login_widget.setFixedSize(615, 320)  # Espace restant
        login_layout = QVBoxLayout(login_widget)
        login_layout.setContentsMargins(50, 40, 50, 40)
        
        # Label "Password :" aligné à gauche
        password_label = QLabel("Password :")
        password_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        password_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        login_layout.addWidget(password_label)
        
        # Champ de mot de passe
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background-color: #2a2a2a;
            }
        """)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.returnPressed.connect(self.check_password)
        login_layout.addWidget(self.password_input)
        
        # Layout horizontal pour les boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton de connexion
        self.login_button = QPushButton("SE CONNECTER")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                border: none;
                border-radius: 8px;
                padding: 14px 20px;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
        """)
        self.login_button.clicked.connect(self.check_password)
        buttons_layout.addWidget(self.login_button)
        
        # Bouton Fermer
        self.close_button = QPushButton("FERMER")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                border: none;
                border-radius: 8px;
                padding: 14px 20px;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #ff3333;
            }
            QPushButton:pressed {
                background-color: #ff2222;
            }
        """)
        self.close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_button)
        
        # Ajouter le layout des boutons
        login_layout.addLayout(buttons_layout)
        
        # Message d'erreur (caché par défaut)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px;
            }
        """)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(self.error_label)
        
        # Espacement flexible
        login_layout.addStretch()
        
        main_layout.addWidget(login_widget)
        
        # Animation de fondu d'ouverture
        self.setWindowOpacity(0)
        self.fade_in()
        
        # Charger et jouer la vidéo
        self.load_video()
        
        # Centrer la fenêtre sur l'écran
        self.center_on_screen()
        
        # Focus sur le champ de mot de passe
        QTimer.singleShot(500, self.password_input.setFocus)
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def fade_in(self):
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.start()
        
    def load_video(self):
        # Chemin vers la vidéo
        video_path = r"C:\Users\faysa\Desktop\CPI TOOL V 3\login vid.mp4"
        
        if os.path.exists(video_path):
            video_url = QUrl.fromLocalFile(video_path)
            self.media_player.setSource(video_url)
            self.media_player.play()
            
            # Mettre en boucle la vidéo
            self.media_player.mediaStatusChanged.connect(self.restart_video)
        else:
            print(f"Vidéo non trouvée: {video_path}")
            
    def restart_video(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
            
    def check_password(self):
        password = self.password_input.text().strip()
        
        if password in self.valid_passwords:
            self.error_label.setText("")
            self.fade_out_and_close()
        else:
            self.error_label.setText("Mot de passe incorrect!")
            self.password_input.clear()
            self.password_input.setFocus()
            
            # Animation de secousse pour le champ
            self.shake_animation()
            
    def shake_animation(self):
        original_pos = self.password_input.pos()
        shake_distance = 10
        shake_duration = 100
        
        for i in range(6):
            direction = 1 if i % 2 == 0 else -1
            new_x = original_pos.x() + (shake_distance * direction)
            
            QTimer.singleShot(i * shake_duration, 
                           lambda x=new_x: self.password_input.move(x, original_pos.y()))
            
        QTimer.singleShot(6 * shake_duration, 
                       lambda: self.password_input.move(original_pos))
        
    def fade_out_and_close(self):
        # Contourner le problème de l'animation qui ne se termine pas
        QTimer.singleShot(100, self.on_login_success)  # Petit délai pour l'effet visuel
        
    def on_login_success(self):
        self.login_success.emit()
        # Ne pas fermer ici, laisser la fonction appelante gérer la fermeture
        
    def keyPressEvent(self, event):
        # Permettre de fermer avec ESC
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configuration du style global
    app.setStyle('Fusion')
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())
