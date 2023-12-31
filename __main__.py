from database_toko import arus_stok, update_toko
from kas_masuk import debit
from PyQt5 import QtGui, QtCore, Qt
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QUrl, QObject,QStringListModel, Qt
from PyQt5.QtQuick   import QQuickView
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QGroupBox
from PyQt5.QtCore import QAbstractListModel, QVariant, Qt
from PyQt5.QtWidgets import QApplication
from database_toko import get_id
from cek_stok import stok_habis
from open_value_excel import get_duit
import database_toko as dt
from sent_data import publish
from git_toko import pull_debit, push_debit_1, push_debit_2
from utang import hutangToko
from stat import ChartStat
import sys
cek = 'TWS1000'
#inisiasi quit button
quitbtn = 0
minibtn = 0
text = "wildan"
arus_stok = arus_stok()
data_toko = dt.update_toko()
class ListModel(QAbstractListModel):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return str(self._data[index.row()])

        return QVariant()
    
class Aplikasi(QQuickView):
    txtpush = ""
    Hutang = ""
    showHutang = pyqtSignal(str)
    git_push = pyqtSignal(str)
    stat = pyqtSignal(list)
    Quit = pyqtSignal(str)
    Mini = pyqtSignal(str)
    idprdk = pyqtSignal(str)
    nama = pyqtSignal(str)
    stok = pyqtSignal(str)
    hrgdus = pyqtSignal(str)
    jualdus = pyqtSignal(str)
    jualpcs = pyqtSignal(str)
    etalaseproduk = pyqtSignal(str)
    # list_id = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setSource(QUrl('main.qml'))
        self.rootContext().setContextProperty('Aplikasi',self)
        self.setGeometry(100, 100, 1000, 800)
        self.setTitle("Toko Plastik Solusa")
        self.show()
        vista = self.rootObject()
        self.Hutang = hutangToko().nominalHutang()
        self.stat.connect(vista.nameMonth)
        self.nama.connect(vista.namaproduk)
        self.stok.connect(vista.produk1)
        self.hrgdus.connect(vista.produk2)
        self.jualdus.connect(vista.produk3)
        self.jualpcs.connect(vista.produk4)
        self.etalaseproduk.connect(vista.produk5)
        self.git_push.connect(vista.pushtext)
        self.showHutang.connect(vista.tampilanHutang)

        self.showHutang.emit(str(self.Hutang))
        # list_items = get_id()
        # model = ListModel(list_items)
        # self.list_id.emit(model)

    @pyqtSlot(str)
    def namabulan(self, value):
        a = value
        print(a)
        if a == 'statistik':
            pass
    @pyqtSlot('QString')
    def minimize(self, value):
       mini = str(value)
       if mini == 'minimize':
          self.showMinimized()

    @pyqtSlot(str)
    def slothutang(self,value):
        self.Hutang = int(value)
        self.Hutang = hutangToko().nambahHutang(self.Hutang)
        self.showHutang.emit(str(self.Hutang))

    #push button
    @pyqtSlot(str)
    def push(self,value):
        gitPush = str(value)
        if gitPush == "git push":
            try:
                push_debit_1()
                self.git_push.emit('push berhasil')
            except:
                push_debit_2()
                self.git_push.emit('tidak ada perubahan')
    #pull button
    @pyqtSlot(str)
    def pull(self,value):
        gitPull = str(value)
        if gitPull == "git pull":
            try:
                pull_debit()
            except:
                print('pull gagal')

    # quit button 
    @pyqtSlot('QString')
    def quit(self, value):
        dataquit = str(value)
        if dataquit == 'quit now':
            self.close()

    @pyqtSlot(str)
    def jumlahkeluar(self,text):
        global jumlah_belanjaan
        jumlah_belanjaan = text
        if jumlah_belanjaan =="":
            jumlah_belanjaan = 0
        # print(jumlah_belanjaan)
        arus_stok.etalase_masuk(produk_belanjaan,int(jumlah_belanjaan))

    @pyqtSlot(str)
    def hargakeluar(self,text):
        global harga_belanjaan
        harga_belanjaan = text
        if harga_belanjaan =="":
            harga_belanjaan = 0
        cell_F, cell_G = debit(namaprdk=namaproduk,jumlahprdk=bnykproduk,hrgprdk=hrg,produk_belanja=produk_belanjaan,jumlah_belanja=jumlah_belanjaan,harga_belanja=int(harga_belanjaan))
        # kasmasuk = get_duit(cell_F)
        # publish(kasmasuk)
        

    @pyqtSlot(str)
    def kaskeluar(self,text):
        global produk_belanjaan
        produk_belanjaan = text
        

    @pyqtSlot(str)
    def jmlhprdk(self, text):
       global namaproduk
       namaproduk = text

    @pyqtSlot(str)
    def namaprdk(self,text):
       global bnykproduk
       bnykproduk = text
       arus_stok.etalase_keluar(id_produk=namaproduk,eta_baru=int(bnykproduk))
       
    
    @pyqtSlot(str)
    def hrgproduk(self, text):
       global hrg
       hrg = text
       

    @pyqtSlot(str)
    def receiveid(self, text):
        global idprdk
        global produk
        idprdk = text
        try:
          produk,stok,hrg_beli_dus,hrg_jual_dus,hrg_jual_pcs,etalase = data_toko.get_data(idprdk)
          self.nama.emit(str(produk))
          self.stok.emit(str(stok))
          self.hrgdus.emit(str(hrg_beli_dus))
          self.jualdus.emit(str(hrg_jual_dus))
          self.jualpcs.emit(str(hrg_jual_pcs))
          self.etalaseproduk.emit(str(etalase))
        except:
           pass

    def sampling(self):
        s1 = quitbtn
        s2 = text 
        s3 = minibtn
        self.Quit.emit(str(s1))
        self.Mini.emit(str(s3))
        
        
if __name__ == '__main__':
    stok_habis()
    app = QApplication(sys.argv)
    w = Aplikasi()
    sys.exit(app.exec_())

