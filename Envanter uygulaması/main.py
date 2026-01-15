from ast import Index
import enum
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from panel import *
from login import LoginPage
from panel import Ui_MainWindow


#Arayüz işlemleri

uygulama = QApplication(sys.argv)
login_page = LoginPage()
if login_page.exec_() == QDialog.Accepted:
    pencere = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(pencere)
    pencere.show()

    #Veri Tabanı işlemleri

    import sqlite3

    baglanti = sqlite3.connect('kayıt.db')
    islem = baglanti.cursor()
    baglanti.commit()

    table = islem.execute('Create table if not exists Envanter(Urun_Kodu varchar(10),Urun_Adı varchar(50),Marka varchar(50),Stok_Adet integer,Urun_Turu varchar(50),Fiyat varchar(50),Tarih varchar(20))')
    baglanti.commit()
    ui.tableWidget.setHorizontalHeaderLabels(('Ürün Kodu','Ürün Adı','Marka','Stok Adedi','Ürün Türü','Birim Fiyat','Giriş Tarihi'))

    #Fonksiyonlar

    def clear():
        for widget in pencere.findChildren(QLineEdit):
            widget.clear()
        
        for widget in pencere.findChildren(QComboBox):
            widget.setCurrentIndex(-1)  


    def urun_ekle():
        urun_kodu = ui.urun_kodu_line.text()
        urun_adı = ui.urun_adi_line.text()
        marka = ui.marka_line.text()
        stok_adet = ui.stok_adet_line.text()
        urun_turu = ui.urun_tur_combx.currentText()
        birim_fiyat = ui.fiyat_line.text()
        giriş_tarihi = ui.tarih_line.text()

        try:
            ekle = 'insert into Envanter(Urun_Kodu,Urun_Adı,Marka,Stok_Adet,Urun_Turu,Fiyat,Tarih) values (?,?,?,?,?,?,?)'
            islem.execute(ekle,(urun_kodu,urun_adı,marka,stok_adet,urun_turu,birim_fiyat,giriş_tarihi))
            baglanti.commit()
            ui.statusbar.showMessage('Ürün Ekleme Başarılı....',3000)
            kayıt_listele()
            clear()

        except:
            ui.statusbar.showMessage('Ürün Ekleme Başarısız!!!',3000)

    def kayıt_listele():
        ui.tableWidget.clear()
        ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ui.tableWidget.setHorizontalHeaderLabels(('Ürün Kodu','Ürün Adı','Marka','Stok Adedi','Ürün Türü','Birim Fiyat','Giriş Tarihi'))
        sorgu = 'select * from Envanter'
        islem.execute(sorgu)

        for indexSatır,kayıtNumarası in enumerate(islem):
            for IndexSutun,kayıtSutun in enumerate(kayıtNumarası):
                ui.tableWidget.setItem(indexSatır,IndexSutun,QTableWidgetItem(str(kayıtSutun)))
        clear()

    def kayıt_sil():
        sil_mesajı = QMessageBox.question(pencere,'Silme Onayı','Silme İşlemini Onaylıyormusunuz ?')
        QMessageBox.Yes |QMessageBox.No

        if sil_mesajı == QMessageBox.Yes:
            secilen_kayıt = ui.tableWidget.selectedItems()
            silinecek_kayıt = secilen_kayıt[0].text()

            sorgu = 'delete from Envanter where Urun_Kodu = ?'

            try:
                islem.execute(sorgu,(silinecek_kayıt,))
                baglanti.commit()
                ui.statusbar.showMessage('Kayıt Silme İşlemi Başarılı....',3000)
                kayıt_listele()
                clear()
            except:
                ui.statusbar.showMessage('Kayıt Silme İşlemi Başarısız....',3000)

        else:
            ui.statusbar.showMessage('Kayıt Silme İşlemi İptal Edildi....',3000)
            clear()
                
    def filitre():
        listelenecek_kolon = ui.fltr_combx.currentText()
        listelenecek_line = ui.filitre_line.text()

        sorgu = f'select * from Envanter where {listelenecek_kolon} = ?'
        islem.execute(sorgu,(listelenecek_line,))
        ui.tableWidget.clear()
        ui.tableWidget.setHorizontalHeaderLabels(('Ürün Kodu','Ürün Adı','Marka','Stok Adedi','Ürün Türü','Birim Fiyat','Giriş Tarihi'))
        for indexSatır,kayıtNumarası in enumerate(islem):
            for IndexSutun,kayıtSutun in enumerate(kayıtNumarası):
                ui.tableWidget.setItem(indexSatır,IndexSutun,QTableWidgetItem(str(kayıtSutun)))
        clear()


    def update():
        new_price = ui.fiyat_line.text()  
        new_stock = ui.stok_adet_line.text()  
        secilen_kayıt = ui.tableWidget.selectedItems()  
        if not secilen_kayıt:
            ui.statusbar.showMessage('Lütfen Bir Ürün Seçiniz....',3000)  
            return

        güncellenecek_kayıt = secilen_kayıt[0].text()  
        try:
            islem.execute(
                "UPDATE Envanter SET Stok_Adet = ?, Fiyat = ? WHERE Urun_Kodu = ?", 
                (new_stock, new_price, güncellenecek_kayıt)
            )
            kayıt_listele()  
            clear() 
        except sqlite3.Error as e:
            ui.statusbar.showMessage('Silme İşleminde Bir Hata Oluştu',e,3000)

    def sipariş_oluştur():
        urun_kodu = ui.siparis_urun_kodu_lnedit.text()
        satış_miktarı = ui.siparis_miktar_lnedit.text()

        if not urun_kodu or not satış_miktarı:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText("Lütfen Ürün Kodu ve Satış Miktarı Giriniz!")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        try:
            satış_miktarı = int(satış_miktarı)
            güncel_stok = islem.execute('SELECT Stok_Adet FROM Envanter WHERE Urun_Kodu = ?', (urun_kodu,))
            stok_sonuc = güncel_stok.fetchone()

            if stok_sonuc is None:
                msg = QMessageBox()
                msg.setWindowTitle("Hata")
                msg.setText("Ürün Kodu Bulunamadı!")
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            mevcut_stok = int(stok_sonuc[0])

            if mevcut_stok < satış_miktarı:
                msg = QMessageBox()
                msg.setWindowTitle("Hata")
                msg.setText("Yeterli Stok Yok!")
                msg.setIcon(QMessageBox.Warning)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                yeni_stok = mevcut_stok - satış_miktarı
                islem.execute('UPDATE Envanter SET Stok_Adet = ? WHERE Urun_Kodu = ?', (yeni_stok, urun_kodu))
                baglanti.commit()
                kayıt_listele()

                msg = QMessageBox()
                msg.setWindowTitle("Başarılı")
                msg.setText(f"Sipariş Başarıyla Oluşturuldu. Toplam Sipariş Miktarı = {satış_miktarı}")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        except ValueError:
            msg = QMessageBox()
            msg.setWindowTitle("Hata")
            msg.setText("Satış Miktarı Geçerli Bir Sayı Olmalıdır!")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


        






    #Butonlar

    ui.ekle_btn.clicked.connect(urun_ekle)
    ui.sil_btn.clicked.connect(kayıt_sil)
    ui.filitre_btn.clicked.connect(filitre)
    ui.yenile_btn.clicked.connect(kayıt_listele)
    ui.gnclle_btn.clicked.connect(update)
    ui.siparis_btn.clicked.connect(sipariş_oluştur)
































    kayıt_listele()
    sys.exit(uygulama.exec_())


    