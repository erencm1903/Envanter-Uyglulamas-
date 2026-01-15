from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
import sqlite3


class LoginPage(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('log-in_page.ui',self)

        self.giris_btn.clicked.connect(self.check_login)
        self.sifre_linedit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.hesap_olustur_btn.clicked.connect(self.register_user)

        # Veritabanı bağlantısı
        self.db_connection = sqlite3.connect("kayıt.db")
        self.cursor = self.db_connection.cursor()

        # Kullanıcılar tablosunu oluştur
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Kullanıcılar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        self.db_connection.commit()
    
    
    
    
    
    
    def check_login(self):
        """Giriş bilgilerini doğrular."""
        username = self.kullanici_adi_linedit.text()
        password = self.sifre_linedit.text()

        # Kullanıcıyı doğrula
        self.cursor.execute("SELECT * FROM Kullanıcılar WHERE username = ? AND password = ?", (username, password))
        user = self.cursor.fetchone()

        if user:
            self.accept()  # Giriş başarılı
        else:
            # Hata mesajı
            self.error_label.setText("!Hatalı kullanıcı adı veya şifre!")
            self.error_label.setStyleSheet("color: rgb(255, 0, 0); font-size: 20px")

    def register_user(self):
        """Yeni kullanıcı kaydı ekler."""
        username = self.kullanici_adi_linedit.text()
        password = self.sifre_linedit.text()

        if not username or not password:
            # Boş alanlar için uyarı
            self.error_label.setText("!Kullanıcı adı ve şifre boş olamaz!")
            self.error_label.setStyleSheet("color: rgb(255, 0, 0); font-size: 20px")
            return

        try:
            # Yeni kullanıcı ekle
            self.cursor.execute("INSERT INTO Kullanıcılar (username, password) VALUES (?, ?)", (username, password))
            self.db_connection.commit()

            # Başarı mesajı
            msg = QMessageBox()
            msg.setWindowTitle("Başarılı")
            msg.setText("Kayıt başarılı! Giriş yapabilirsiniz.")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        except sqlite3.IntegrityError:
            # Kullanıcı adı zaten mevcutsa hata
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText("Bu kullanıcı adı zaten kayıtlı!")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()    