from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox as mb
import sqlite3 as sql
import datetime as t
import calendar as cl

# TODO fonkisyon dışında kullanılmayacak değişkenlerin self'lerini sil
# TODO entry cbox larda sorunları hallet + "öncesi" kullanımını sil

class BookAssistantDataBase:

    def veriDegistir(self, tabloIsim="", dataSet="", where=""):
        self.cur.execute("UPDATE {} SET {} WHERE {}".format(tabloIsim, dataSet, where))
        self.conn.commit()

    def veriCek(self, tabloIsim="", howMany="", condition=""):
        if condition:
            self.cur.execute("SELECT * FROM {} WHERE {}".format(tabloIsim, condition))
        else:
            self.cur.execute("SELECT * FROM {}".format(self.tabloIsim))

        if howMany == "one":
            data = self.cur.fetchone()
        elif howMany == "all":
            data = self.cur.fetcall()
        else:
            data = self.cur.fetchmany(howMany)

        return data
    
    def veriCekIndex(self, tabloIsim="", index=0, condition=""):
        if condition:
            self.cur.execute("SELECT * FROM {} WHERE {}")
        else:
            self.cur.execute("SELECT * FROM {}")

        data = self.cur.fetchmany(index+1)
        return data[len(data)-1]

    def veriSil(self, tabloIsmi="", condition=""):
        if condition:
            self.cur.execute("DELETE FROM {} WHERE {}".format(tabloIsmi, condition))
        else:
            self.cur.execute("DELETE FROM {}".format(tabloIsmi))
        self.conn.commit()


# veri ekleniyor veriyi göstermek için
# ayıklama yapılıyor 
# başlangıçda oluşturmak için 

class BookAssistant:

    def __init__(self):
        
        def tabloOlustur(*data):
            data = self.cnvTupleToString(data)
            self.cur.execute("CREATE TABLE IF NOT EXISTS {} {}".format(self.tabloIsim, data))

        # db kodlari
        path = "books.db"
        self.conn = sql.connect(path)
        self.cur = self.conn.cursor()
        self.tabloIsim = "kitaplar"
        self.kitapVerileri = ["İsmi", "Türü", "Yayınevi", "Sayfa Sayısı", 
        "Okunduğu gün", "Okunduğu Ay", "Okunduğu Yıl", "Derece", "Favori mi?"]
        tabloOlustur("isim", "tür", "yayinevi", "sayfa_sayisi", 
        "tarih_gün", "tarih_ay", "tarih_yil", "yildiz", "favoriler")    # TODO sütun isimleri

        self.ayiklaVerisi = ["", []]

        # gui kodları
        self.p = 10 # padding ayarı genel 

        self.yilListesi = [*range(2019, self.tarihCek("yıl")+1)]
        print(self.yilListesi)
        self.ayListesi =  [ "Ocak", "Şubat", "Mart", "Nisan", 
                            "Mayıs", "Haziran", "Temmuz", "Ağustos", 
                            "Eylül", "Ekim", "Kasım", "Aralık"]
        self.günListesi = []

        self.mainRoot = Tk()
        self.mainRoot.title("Book Assistant")
        self.guiAc()
        self.mainRoot.mainloop()

    def guiAc(self):

        #variables
        yillikKitapSayisiVar = IntVar()
        yillikKitapSayisiVar.set(len(self.durumaGoreVeriCek("tarih_yil", str(self.tarihCek("yıl"))))) 

        #frames
        labelsFrame = Frame(self.mainRoot)
        kitapListesiFrame = Frame(self.mainRoot)
        buttonsFrame = Frame(self.mainRoot)

        buttonsFrame.grid(row=2, column=0, sticky=W)
        kitapListesiFrame.grid(row=1, column=0, padx=self.p, pady=self.p)
        labelsFrame.grid(row=0, column=0, sticky=W)

        #menu
        menubar = Menu(self.mainRoot)
        menuSecme = Menu(menubar, tearoff=0)
        menuSecme.add_command(label="Gelişmiş", command=lambda: self.kitapListesi.configure(selectmode="extended"))
        menuSecme.add_command(label="Gezin", command=lambda: self.kitapListesi.configure(selectmode="browse"))
        menuSecme.add_command(label="Hiçbiri", command=lambda: self.kitapListesi.configure(selectmode="none"))

        menuSirala = Menu(menubar, tearoff=0) # FIXME treeYaz'larda tv haqngi ayıklama durumunda olduğunu kontrol etmiyor. direk tüm listeyi yazdırıyot
        menuSirala.add_command(label="Ekleme tarihi en erken", command=lambda: self.treeWrite("eklenme tarihi", "düz"))
        menuSirala.add_command(label="Ekleme tarihi en geç", command=lambda: self.treeWrite("eklenme tarihi", "ters"))
        menuSirala.add_separator()
        menuSirala.add_command(label="Okunma tarihi en geç", command=lambda: self.treeWrite("okunma tarihi", "düz"))
        menuSirala.add_command(label="Okunma tarihi en erken", command=lambda: self.treeWrite("okunma tarihi", "ters"))
        menuSirala.add_separator()
        menuSirala.add_command(label="A - Z", command=lambda: self.treeWrite("alfabetik", "düz"))
        menuSirala.add_command(label="Z - A", command=lambda: self.treeWrite("alfabetik", "ters"))
        menuSirala.add_separator()
        menuSirala.add_command(label="Derecesi en yüksek", command=lambda: self.treeWrite("derece", "düz"))
        menuSirala.add_command(label="Derecesi en düşük", command=lambda: self.treeWrite("derece", "ters"))
        menuSirala.add_separator()
        menuSirala.add_command(label="Sayfası en fazla", command=lambda: self.treeWrite("sayfa", "düz"))
        menuSirala.add_command(label="Sayfası en az", command=lambda: self.treeWrite("sayfa", "ters"))

        menubar.add_cascade(label="Seçme Tipi", menu=menuSecme)
        menubar.add_cascade(label="Sırala", menu=menuSirala)
        menubar.add_command(label="Ayıkla...", command=self.ayiklaToplevel)
        self.mainRoot.config(menu=menubar)
               
        #labels
        def updateValues_insideCbox():
            insideCBox.configure(values=self.sütunVeriTürleriCek("tarih_yil"))

        label00 = Label(labelsFrame, text="Bugünün tarihi:")
        label10 = Label(labelsFrame, text="Toplam okunan kitap sayısı:")
        label01 = Label(labelsFrame, text=self.tarihCek())
        label11 = Label(labelsFrame, text=len(self.tabloyuCek()))
        label21 = Label(labelsFrame, textvariable=yillikKitapSayisiVar)

        insideFrame = Frame(labelsFrame)


        label00.grid    (row=0, column=0, sticky=W, padx=self.p, pady=self.p)
        label10.grid    (row=1, column=0, sticky=W, padx=self.p, pady=self.p)
        label01.grid    (row=0, column=1, sticky=W, padx=self.p, pady=self.p)
        label11.grid    (row=1, column=1, sticky=W, padx=self.p, pady=self.p)
        insideFrame.grid(row=2, column=0, sticky=W, padx=self.p, pady=self.p)
        label21.grid    (row=2, column=1, sticky=W, padx=self.p, pady=self.p)


        insideCBox = Combobox(insideFrame, width=13, values=self.sütunVeriTürleriCek("tarih_yil"), postcommand=updateValues_insideCbox)
        insideLabel = Label(insideFrame, text="yılında okunan kitap:")

        insideCBox.grid(row=0, column=0)
        insideLabel.grid(row=0, column=1)

        #booklist
        self.kitapListesi = Treeview(kitapListesiFrame, columns=list(range(len(self.kitapVerileri))), selectmode="browse")
        self.kitapListesi.column("#0", width=40, minwidth=40)
        self.kitapListesi.heading("#0", text="No")

        for index in list(range(len(self.kitapVerileri))):
            self.kitapListesi.column(index, width=100 if index!=0 else 150, minwidth=120 if index==0 else 100 if index==4 or index==5 or index==6 else 75)
            self.kitapListesi.heading(index, text=self.kitapVerileri[index])
        self.treeWrite()
        self.kitapListesi.grid(row=1, column=0)


        #buttons
        button1 = Button(buttonsFrame, text="ekle...", command=self.ekleToplevel)
        button2 = Button(buttonsFrame, text="sil...", command=self.silToplevel)
        button3 = Button(buttonsFrame, text="favorilere ekle/kaldır...", command=self.favoriToplevel)
 
        button1.grid(row=0, column=0, sticky=W, padx=self.p, pady=self.p)
        button2.grid(row=0, column=1, sticky=W, padx=self.p, pady=self.p)
        button3.grid(row=0, column=2, sticky=W, padx=self.p, pady=self.p)

        #events
        def cboxLabelGüncelle():
            data = self.durumaGoreVeriCek("tarih_yil", insideCBox.get())
            yillikKitapSayisiVar.set(len(data))

        insideCBox.bind("<<ComboboxSelected>>", lambda event: cboxLabelGüncelle())
        try:
            insideCBox.current(self.sütunVeriTürleriCek("tarih_yil").index(str(self.tarihCek("yıl"))))
        except:
            pass

    def ekleToplevel(self):

        def buttonUserChange(butNo):
            self.kitapYildiz = butNo
            for a in range(1, 6):
                if a <= butNo:
                    butVarDict[a].set(1)
                elif a > butNo:
                    butVarDict[a].set(0)
            return
        
        def applyChanges():

            def veriEkle(argmnt):
                data = self.cnvTupleToString(argmnt)
                self.cur.execute("INSERT INTO {} VALUES {}".format(self.tabloIsim, data))
                self.conn.commit()
 
            self.yeniKitapVerisi[0] = kitapİsimVar.get()           
            self.yeniKitapVerisi[1] = kitapTürVar.get()
            self.yeniKitapVerisi[2] = kitapYayineviVar.get()
            self.yeniKitapVerisi[3] = kitapSayfasayisiVar.get()
            self.yeniKitapVerisi[4] = kitapTarihGünVar.get()
            self.yeniKitapVerisi[5] = kitapTarihAyVar.get()
            self.yeniKitapVerisi[6] = kitapTarihYilVar.get()
            self.yeniKitapVerisi[7] = self.kitapYildiz                  
            self.yeniKitapVerisi[8] = kitapFavorilerVar.get()  

            error = False
            for index, data in enumerate(self.yeniKitapVerisi):
                if index == 7 and data == 0:
                    error = True
                    break
                elif data == "":
                    error = True
                    break

            if error:
                mb.showerror("Error", "Boş alan bırakmayınız.")
                self.yeniKitapVerisi = ["" for a in range(9)]
                return
            
            try:
                int(self.yeniKitapVerisi[6])

                self.yeniKitapVerisi[5] = self.ayListesi.index(self.yeniKitapVerisi[5]) + 1 # TODO veri türleri 2
            except:
                mb.showerror("Error", "Girdiğiniz değerleri kontrol ediniz.")
                self.yeniKitapVerisi = ["" for a in range(9)]
                return

            self.ekle.destroy()
            self.yeniKitapVerisi[7] = str(self.yeniKitapVerisi[7])
            veriEkle(self.yeniKitapVerisi)
            self.treeWrite()  # FIXME şuan treeview hangi duruma göre gösteriyor olursa olsun tüm listeyi göstermeye başlayacak. İçine bir veri atanmalı.


        #variables
        self.yeniKitapVerisi = ["" for b in range(9)]
        a = 6  # padding=6
        k_türleri = self.sütunVeriTürleriCek("tür")
        k_yayinevleri = self.sütunVeriTürleriCek("yayinevi")
        
        kitapİsimVar        = StringVar()  # TODO veri tipleri 1
        kitapTürVar         = StringVar()
        kitapYayineviVar    = StringVar()
        kitapSayfasayisiVar = StringVar()
        kitapTarihGünVar    = StringVar()
        kitapTarihAyVar     = StringVar()
        kitapTarihYilVar    = StringVar()
        kitapFavorilerVar   = StringVar()  
        self.kitapYildiz    = 0

        kitapFavorilerVar.set(0)
        

        but1Var = IntVar()
        but2Var = IntVar()
        but3Var = IntVar()
        but4Var = IntVar()
        but5Var = IntVar()

        butVarDict =    {  
                        1: but1Var, 
                        2: but2Var, 
                        3: but3Var, 
                        4: but4Var, 
                        5: but5Var
                        }

        #main
        self.ekle = Toplevel(self.mainRoot)
        self.ekle.title("Kitap ekle...")
        self.ekle.resizable(height=0, width=0)
        
        #frames
        ekleRadioFrame = Frame(self.ekle)
        ekleDateFrame =  Frame(self.ekle)
        ekleButtFrame =  Frame(self.ekle)

        ekleDateFrame.grid(row=1, column=2, columnspan=1, sticky=W, padx=a, pady=a)
        ekleRadioFrame.grid(row=3, column=2, columnspan=1, sticky=W, padx=a, pady=a)
        ekleButtFrame.grid(row=4, column=2, columnspan=2, sticky=E)

        #favori
        ekleFavoriCheckbutton = Checkbutton(self.ekle, text="Bu kitap favorilerinize alınsın mı?", variable=kitapFavorilerVar)
        ekleFavoriCheckbutton.grid(row=4, column=0, columnspan=2, padx=a, pady=a, sticky=W)

        #labels-1
        ekleEntLabel1 = Label(self.ekle, text="Kitap ismi:")
        ekleEntLabel2 = Label(self.ekle, text="Kitap türü:")
        ekleEntLabel3 = Label(self.ekle, text="Yayınevi:")
        ekleEntLabel4 = Label(self.ekle, text="Sayfa sayısı:")

        ekleEntLabel1.grid(row=0, column=0, sticky=W, padx=a, pady=a)
        ekleEntLabel2.grid(row=1, column=0, sticky=W, padx=a, pady=a)
        ekleEntLabel3.grid(row=2, column=0, sticky=W, padx=a, pady=a)
        ekleEntLabel4.grid(row=3, column=0, sticky=W, padx=a, pady=a)

        #enrtys-1
        ekleEntry1 = Entry(self.ekle, width=22, textvariable=kitapİsimVar)
        ekleCBoxTür =      Combobox(self.ekle, width=20, values=k_türleri,     textvariable=kitapTürVar)
        ekleCBoxYayinevi = Combobox(self.ekle, width=20, values=k_yayinevleri, textvariable=kitapYayineviVar)
        ekleEntry4 = Entry(self.ekle, width=10, textvariable=kitapSayfasayisiVar)

        ekleEntry1      .grid(row=0, column=1, sticky=W, padx=a, pady=a)
        ekleCBoxTür     .grid(row=1, column=1, sticky=W, padx=a, pady=a)
        ekleCBoxYayinevi.grid(row=2, column=1, sticky=W, padx=a, pady=a)
        ekleEntry4      .grid(row=3, column=1, sticky=W, padx=a, pady=a)

        #labels-2
        ekleLabel1 = Label(self.ekle, text="Okunma tarihi:")
        ekleLabel1 = Label(self.ekle, text="Yıldız:")

        ekleLabel1.grid(row=0 ,column=2, sticky=W, padx=a, pady=a)
        ekleLabel1.grid(row=2, column=2, sticky=W, padx=a, pady=a)

        #entrys-2
    
        def updateValues_gün():
            ekleCBoxTarih_gün.configure(values=self.makeCalendar(int(kitapTarihYilVar.get()), self.ayListesi.index(kitapTarihAyVar.get()) + 1))

        ekleCBoxTarih_yil = Combobox(ekleDateFrame, width=5, values=self.yilListesi, textvariable=kitapTarihYilVar)
        ekleCBoxTarih_ay  = Combobox(ekleDateFrame, width=5, values=self.ayListesi, textvariable=kitapTarihAyVar)
        ekleCBoxTarih_gün = Combobox(ekleDateFrame, width=5, values=self.günListesi, textvariable=kitapTarihGünVar, postcommand=updateValues_gün)

        ekleCBoxTarih_yil.grid(row=0, column=0, sticky=W, padx=a, pady=a)
        ekleCBoxTarih_ay .grid(row=0, column=1, sticky=W, padx=a, pady=a)
        ekleCBoxTarih_gün.grid(row=0, column=2, sticky=W, padx=a, pady=a)

        #checkbuttons
        ekleButt1 = Checkbutton(ekleRadioFrame, text=1, variable=but1Var, command=lambda: buttonUserChange(1))
        ekleButt2 = Checkbutton(ekleRadioFrame, text=2, variable=but2Var, command=lambda: buttonUserChange(2))
        ekleButt3 = Checkbutton(ekleRadioFrame, text=3, variable=but3Var, command=lambda: buttonUserChange(3))
        ekleButt4 = Checkbutton(ekleRadioFrame, text=4, variable=but4Var, command=lambda: buttonUserChange(4))
        ekleButt5 = Checkbutton(ekleRadioFrame, text=5, variable=but5Var, command=lambda: buttonUserChange(5))

        ekleButt1.grid(row=0, column=0)
        ekleButt2.grid(row=0, column=1)
        ekleButt3.grid(row=0, column=2)
        ekleButt4.grid(row=0, column=3)
        ekleButt5.grid(row=0, column=4 )

        #buttons
        self.ekleOk = Button(ekleButtFrame, text="Ok", width=10, command=applyChanges)
        self.ekleCancel = Button(ekleButtFrame, text="Cancel", width=10, command=self.ekle.destroy)

        self.ekleOk.grid(row=0, column=0, padx=a, pady=a)
        self.ekleCancel.grid(row=0, column=1, padx=a, pady=a)

    def silToplevel(self):


        self.sil = Toplevel(self.mainRoot)
        self.sil.title("Kitap sil...")
        self.sil.resizable(height=0, width=0)

    def favoriToplevel(self):

        self.fvr = Toplevel(self.mainRoot)
        self.fvr.title("Favorileri değiştir")
        self.fvr.resizable(height=False, width=False)

    def ayiklaToplevel(self):

        self.ayikla = Toplevel(self.mainRoot)
        self.ayikla.title("Kitapları ayıkla")
        self.ayikla.resizable(height=0, width=0)

        #variables
        #box
        self.radioVar = IntVar()
        self.radioVar.set(0)

        ayiklaPadd = 8
        self.ayiklaDatas = ["Tarih", "Derece", "Sayfa", "Tür"]
        self.ayiklamaDurumu = ""

        #tarihe göre
        self.ayiklaYil = StringVar() # 'öncesi': str
        self.ayiklaAy = StringVar()  # "hepsi": str - 1, 2...: int
        self.ayiklaGun = StringVar() # "hepsi": str"

        self.yilListesiAyikla = [*range(2019, self.tarihCek("yıl")+1)]
        self.ayListesiAyikla = [    "Ocak", "Şubat", "Mart", "Nisan", 
                                    "Mayıs", "Haziran", "Temmuz", "Ağustos", 
                                    "Eylül", "Ekim", "Kasım", "Aralık"]
        self.günListesiAyikla = [*range(1, 31)]

        #dereceye göre
        self.derece1Var = IntVar()
        self.derece2Var = IntVar()
        self.derece3Var = IntVar()
        self.derece4Var = IntVar()
        self.derece5Var = IntVar()

        #tarihe göre
        self.topTurSayisi = 0
        self.secTurSayisi = 0

        self.turler = self.sütunVeriTürleriCek("tür")

        #frames
        self.boxFrame      = Frame(self.ayikla)
        self.okCancelFrame = Frame(self.ayikla)
        self.bosFrame      = Frame(self.ayikla)
        self.tarihFrame  = Labelframe(self.ayikla, text="Tarihi Belirleyin")
        self.dereceFrame = Labelframe(self.ayikla, text="Dereceleri Seçin")
        self.sayfaFrame  = Labelframe(self.ayikla, text="Sayfa Aralığını Girin")
        self.türFrame    = Labelframe(self.ayikla, text="Türleri Seçin")

        self.uselessFrame = Frame(self.dereceFrame)
        self.uselessFrame.grid(padx=ayiklaPadd*2, pady=ayiklaPadd)

        self.uselessFrame2 = Frame(self.sayfaFrame)
        self.uselessFrame2.grid(padx=ayiklaPadd*2, pady=ayiklaPadd)

        self.boxFrame.grid      (row=0, column=0)
        self.tarihFrame.grid    (row=2, column=0, padx=ayiklaPadd*1.5, pady=ayiklaPadd*1.5)
        self.dereceFrame.grid   (row=2, column=0, padx=ayiklaPadd*1.5, pady=ayiklaPadd*1.5)
        self.sayfaFrame.grid    (row=2, column=0, padx=ayiklaPadd*1.5, pady=ayiklaPadd*1.5)
        self.türFrame.grid      (row=2, column=0, padx=ayiklaPadd*1.5, pady=ayiklaPadd*1.5)
        self.bosFrame.grid      (row=2, column=0)
        self.okCancelFrame.grid (row=4, column=0, sticky=E)

        self.tarihFrame .grid_remove()
        self.dereceFrame.grid_remove()
        self.sayfaFrame .grid_remove()
        self.türFrame   .grid_remove()

        self.Frames =   { 
                        "Tarih": self.tarihFrame,
                        "Derece": self.dereceFrame,
                        "Sayfa": self.sayfaFrame,
                        "Tür": self.türFrame,
                        "Hepsi": self.bosFrame,
                        "Favoriler": self.bosFrame
                        }

        #radios in box

        def updateAyiklaRadio(radioSit):
            if radioSit == 1:
                self.ayiklaCBox.configure(state="disabled")
                self.ayiklamaDurumu = "Hepsi"
            
            elif radioSit == 2:
                self.ayiklaCBox.configure(state="disabled")
                self.ayiklamaDurumu = "Favoriler"
                
            elif radioSit == 3:
                self.ayiklaCBox.configure(state="readonly")
                self.ayiklamaDurumu = self.ayiklaCBox.get()
                
            updateAyiklaGenel()

        def updateAyiklaGenel():
            for frame in self.Frames.values():
                frame.grid_remove()
            self.Frames[self.ayiklamaDurumu].grid()

        self.ayiklaRadio1 = Radiobutton(self.boxFrame, text="tüm kitapları göster",  variable=self.radioVar, value=1, command=lambda: updateAyiklaRadio(1))
        self.ayiklaRadio2 = Radiobutton(self.boxFrame, text="favorileri göster",     variable=self.radioVar, value=2, command=lambda: updateAyiklaRadio(2))
        self.ayiklaRadio3 = Radiobutton(self.boxFrame, text="özelliklere göre seç:", variable=self.radioVar, value=3, command=lambda: updateAyiklaRadio(3))

        self.ayiklaRadio1.grid(row=0, column=0, sticky=W, padx=ayiklaPadd, pady=ayiklaPadd)
        self.ayiklaRadio2.grid(row=1, column=0, sticky=W, padx=ayiklaPadd, pady=ayiklaPadd)
        self.ayiklaRadio3.grid(row=2, column=0, sticky=W, padx=ayiklaPadd, pady=ayiklaPadd)

        #combobox in box
        self.ayiklaCBox = Combobox(self.boxFrame, values=self.ayiklaDatas, state="disabled")
        self.ayiklaCBox.current(0)
        self.ayiklaCBox.grid(row=2, column=1, padx=ayiklaPadd, pady=ayiklaPadd)

        #bindings in box

        def updateAyiklaCBox(sit):
            self.ayiklamaDurumu = sit
            updateAyiklaGenel()

        self.ayiklaCBox.bind("<<ComboboxSelected>>", lambda event: updateAyiklaCBox(self.ayiklaCBox.get()))

        #okCancelFrame
        def applyChangesAyikla():               #TODO veri türleri

            data = [self.ayiklamaDurumu, []]

            if self.ayiklamaDurumu == "":
                mb.showwarning("Hata", "Herhangi bir seçeneği işaretlemeniz lazım!")
                return
            elif self.ayiklamaDurumu == "Tarih":    # [yıl, ay, gün]
                data[1] = [self.ayiklaYil.get(), self.ayListesiAyikla.index(self.ayiklaAy.get())+1, self.ayiklaGun.get()]
                print("data> ", data)
            elif self.ayiklamaDurumu == "Derece":   # [btt1, btt2, btt3, btt4, btt5]
                data[1] = [self.derece1Var.get(), self.derece2Var.get(), self.derece3Var.get(),self.derece4Var.get(), self.derece5Var.get()]
            elif self.ayiklamaDurumu == "Sayfa":    # [start, stop]
                data[1] = [self.start.get(), self.stop.get()]

                try:
                    data[1][0], data[1][1] = int(data[1][0]), int(data[1][1])
                except:
                    mb.showwarning("Hata", "Bir sayı girmeniz lazım!")
                    return

                if data[1][1] < data[1][0]:
                    mb.showwarning("Hata", "İkinci sayfanın birinci sayfadan büyük veya eşit olması lazım!")
                    return
            elif self.ayiklamaDurumu == "Tür":      # [*türler]
                data[1] = [*self.ayiklaTurler.get(0, "end")]
            else:                                   # []
                data[1] = []

            self.ayiklaVerisi = data.copy()
            print(data)
            self.ayikla.destroy()
            self.treeWrite()

        self.ayiklaOk = Button(self.okCancelFrame, text="Tamam", width=10, command=applyChangesAyikla)
        self.ayiklaCancel = Button(self.okCancelFrame, text="İptal", width=10, command=self.ayikla.destroy)

        self.ayiklaOk.grid      (row=0, column=0, padx=ayiklaPadd, pady=ayiklaPadd)
        self.ayiklaCancel.grid  (row=0, column=1, padx=ayiklaPadd, pady=ayiklaPadd)

        #tarihFrame
        title1 = Label(self.tarihFrame, text="yıl:")
        title2 = Label(self.tarihFrame, text="ay:")
        title3 = Label(self.tarihFrame, text="gün:")

        title1.grid(row=0, column=0, padx=ayiklaPadd, pady=ayiklaPadd, sticky="w")
        title2.grid(row=1, column=0, padx=ayiklaPadd, pady=ayiklaPadd, sticky="w")
        title3.grid(row=2, column=0, padx=ayiklaPadd, pady=ayiklaPadd, sticky="w")

        self.tarihComboYil = Combobox(self.tarihFrame, values=self.yilListesiAyikla, textvariable=self.ayiklaYil, state="readonly") # TODO yıl listesinin 'önceki' elemanı niye sonra ['so...']+liste diye eklemiyoruz
        self.tarihComboAy =  Combobox(self.tarihFrame, values=["Hepsi"]+ self.ayListesiAyikla,  textvariable=self.ayiklaAy,  state="disabled")
        self.tarihComboGun = Combobox(self.tarihFrame, values=["Hepsi"]+ self.günListesiAyikla, textvariable=self.ayiklaGun, state="disabled")

        self.tarihComboYil.current(0)
        self.tarihComboAy.current (0)
        self.tarihComboGun.current(0)

        self.tarihComboYil.grid(row=0, column=1, padx=ayiklaPadd, pady=ayiklaPadd)
        self.tarihComboAy.grid( row=1, column=1, padx=ayiklaPadd, pady=ayiklaPadd)
        self.tarihComboGun.grid(row=2, column=1, padx=ayiklaPadd, pady=ayiklaPadd)

        #tarihFrame-Bind
        def ayiklaTarihCombo(zaman): 
            if zaman == "ay":
                self.tarihComboGun.configure(state="readonly")
                if self.ayiklaAy.get() == "Hepsi":
                    self.tarihComboGun.configure(values=["Hepsi"])
                    self.tarihComboGun.current(0)
                else:
                    self.tarihComboGun.configure(values=["Hepsi"]+self.makeCalendar(int(self.ayiklaYil.get()), self.ayListesi.index(self.ayiklaAy.get())+1))

            elif zaman == "yıl":
                self.tarihComboAy.configure (state="readonly")
                self.tarihComboGun.configure(state="disabled")
                self.tarihComboGun.current(0)

        self.tarihComboAy .bind("<<ComboboxSelected>>", lambda event: ayiklaTarihCombo("ay" ))
        self.tarihComboYil.bind("<<ComboboxSelected>>", lambda event: ayiklaTarihCombo("yıl"))

        #dereceFrame
        derece1 = Checkbutton(self.uselessFrame, text=1, variable=self.derece1Var)
        derece2 = Checkbutton(self.uselessFrame, text=2, variable=self.derece2Var)
        derece3 = Checkbutton(self.uselessFrame, text=3, variable=self.derece3Var)
        derece4 = Checkbutton(self.uselessFrame, text=4, variable=self.derece4Var)
        derece5 = Checkbutton(self.uselessFrame, text=5, variable=self.derece5Var)

        derece1.grid(row=0, column=0, pady=ayiklaPadd)
        derece2.grid(row=0, column=1, pady=ayiklaPadd)
        derece3.grid(row=0, column=2, pady=ayiklaPadd)
        derece4.grid(row=0, column=3, pady=ayiklaPadd)
        derece5.grid(row=0, column=4, pady=ayiklaPadd)
        
        #sayfaFrame
        self.start = Entry(self.uselessFrame2, width=ayiklaPadd)
        self.stop =  Entry(self.uselessFrame2, width=ayiklaPadd)
        cizgi = Label(self.uselessFrame2, text="-")

        self.start.grid(row=0, column=0, padx=ayiklaPadd/3, pady=ayiklaPadd)
        self.stop .grid(row=0, column=2, padx=ayiklaPadd/3, pady=ayiklaPadd)
        cizgi.grid(row=0, column=1, padx=ayiklaPadd/3, pady=ayiklaPadd)

        #türFrame
        def ayiklaTurFonksiyon(durum=None):

            if durum == "listeEkle":
                liste = self.ayiklaTurler.get(0, "end")

                kutuDeger = self.turEkleEntry.get()
                if liste.count(kutuDeger) == 0:
                    self.ayiklaTurler.insert("end", kutuDeger)
                
                liste = self.ayiklaTurler.get(0, "end")

                kutuliste = self.turler.copy()
                for member in liste:
                    kutuliste.remove(member)
                self.turEkleEntry.configure(values=kutuliste)
                self.turEkleEntry.current(0)
                self.turCikarEntry.configure(values=self.ayiklaTurler.get(0, "end"))
                self.turCikarEntry.current(0)
          
            elif durum == "cikarEntry":
                self.turCikarEntry.configure(values=self.ayiklaTurler.get(0, "end"))
                self.turCikarEntry.current(0)

            elif durum == "listeCikar":
                liste = self.ayiklaTurler.get(0, "end")
                kutuDeger = self.turCikarEntry.get()
                self.ayiklaTurler.delete(liste.index(kutuDeger))
    
                self.turCikarEntry.configure(values=self.ayiklaTurler.get(0, "end"))
                self.turCikarEntry.current(0)

        buttons = Frame(self.türFrame)
        labels = Frame(self.türFrame)
        self.ayiklaTurler = Listbox(self.türFrame, selectmode="extended")

        buttons.grid(row=0, column=1, sticky="n")
        labels.grid(row=1, column=1, sticky="w")
        self.ayiklaTurler.grid(row=0, column=0, rowspan=2, padx=ayiklaPadd, pady=ayiklaPadd)


        ekle = Frame(buttons)
        cikar = Frame(buttons)

        ekle.grid(padx=ayiklaPadd, pady=ayiklaPadd)
        cikar.grid(row=1, padx=ayiklaPadd, pady=ayiklaPadd)

        self.turEkleEntry =   Combobox(ekle,  state="readonly", values=self.turler)
        self.turCikarEntry =  Combobox(cikar, state="readonly", values=self.ayiklaTurler.get(0, "end"), postcommand=lambda: ayiklaTurFonksiyon("cikarEntry"))
        self.turEkleButton =  Button(ekle,  text="Ekle",  command=lambda: ayiklaTurFonksiyon("listeEkle"))
        self.turCikarButton = Button(cikar, text="Çıkar", command=lambda: ayiklaTurFonksiyon("listeCikar"))

        self.turEkleEntry.current(0)

        self.turEkleEntry.grid  (row=1, column=1)
        self.turEkleButton.grid (row=1, column=2)
        self.turCikarEntry.grid (row=2, column=1)
        self.turCikarButton.grid(row=2, column=2)

        label1 = Label(labels, text="Toplam kitap türü: "+str(self.topTurSayisi), justify="left")
        label2 = Label(labels, text="Seçilen kitap türü:  "+str(self.secTurSayisi), justify="left")
        label1.grid(row=0, column=0, padx=ayiklaPadd, pady=ayiklaPadd, sticky="wn")
        label2.grid(row=1, column=0, padx=ayiklaPadd, pady=ayiklaPadd, sticky="wn")

    def treeWrite(self, siralaTip="", siralaDogruluk="düz"):

        def intMatrisSirala(indexDeger):
            yeniTabloVerileri = []
            degerler = [a[indexDeger] for a in tabloVerileri]
            maxDeger = max(degerler)
            minDeger = min(degerler)

            for b in range(minDeger, maxDeger+1, 1):
                while True:
                    try:
                        index = degerler.index(b)
                    except Exception as error:
                        break
                    else:
                        yeniTabloVerileri.insert(0, tabloVerileri[index])
                        degerler[index] = ""

            return yeniTabloVerileri

        def strMatrisSirala(indexDeger):
            yeniTabloVerileri = []
            degerler = [a[indexDeger] for a in tabloVerileri]

            while True:
                degerler2 = degerler.copy()
                while True:
                    try:
                        degerler2.remove("")
                    except ValueError:
                        break

                if len(degerler2) == 0:
                    break

                minDeger = min(degerler2)
                maxDeger = max(degerler)
                index = degerler.index(minDeger)

                if maxDeger == "":
                    break
                else:
                    yeniTabloVerileri.append(tabloVerileri[index])
                    degerler[index] = ""
            
            return yeniTabloVerileri
        
        def tarihMatrisSirala():
            gunDeger = [a[4] for a in tabloVerileri]
            ayDeger = [a[5] for a in tabloVerileri]
            yilDeger = [a[6] for a in tabloVerileri]
            tarihStrDeger =    [str(yilDeger[a]) +
                                    (2-len(str(ayDeger[a])))*"0" + str(ayDeger[a]) +
                                    (2-len(str(gunDeger[a])))*"0" + str(gunDeger[a]) 
                                    for a in range(len(tabloVerileri))]
            
            yeniTabloVerileri = []
            
            while True:
                tarihStrDeger2 = tarihStrDeger.copy()
                while True:
                    try:
                        tarihStrDeger2.remove("")
                    except ValueError:
                        break

                if len(tarihStrDeger2) == 0:
                    break

                minDeger = min(tarihStrDeger2)
                maxDeger = max(tarihStrDeger)
                index = tarihStrDeger.index(maxDeger)

                if maxDeger == "":
                    break
                else:
                    yeniTabloVerileri.append(tabloVerileri[index])
                    tarihStrDeger[index] = ""
            
            return yeniTabloVerileri

        if self.ayiklaVerisi[0] == "":
            tabloVerileri = self.tabloyuCek()
        
        else:
            tabloVerileri = []
            if self.ayiklaVerisi[0] == "Tarih":
                self.ayiklaVerisi[1][0], self.ayiklaVerisi[1][1], self.ayiklaVerisi[1][2] = int(self.ayiklaVerisi[1][0]), int(self.ayiklaVerisi[1][1]), int(self.ayiklaVerisi[1][2])
                tabloVerileri = self.durumaGoreVeriCek(["tarih_yil", "tarih_ay", "tarih_gün"], self.ayiklaVerisi[1], [1, 2])
                print(tabloVerileri)

            elif self.ayiklaVerisi[0] == "Derece":
                for index, sit in enumerate(self.ayiklaVerisi[1]):
                    if sit == 1:
                        tabloVerileri.extend(self.durumaGoreVeriCek("yildiz", index+1))

            elif self.ayiklaVerisi[0] == "Sayfa":
                tabloVerileri = self.durumaGoreVeriCekAralık("sayfa_sayisi", self.ayiklaVerisi[1][0], self.ayiklaVerisi[1][1])

            elif self.ayiklaVerisi[0] == "Tür":
                for data in self.ayiklaVerisi[1]:
                    tabloVerileri.extend(self.durumaGoreVeriCek("tür", data))

            elif self.ayiklaVerisi[0] == "Hepsi":
                tabloVerileri = self.tabloyuCek()

            elif self.ayiklaVerisi[0] == "Favoriler":
                tabloVerileri = self.durumaGoreVeriCek("favoriler", 1)

        self.ayiklaVerisi = ["", []]
            
        self.tiplerList = ["okunma tarihi", "eklenme tarihi", "alfabetik", "derece", "sayfa"]
        
        if self.tiplerList.count(siralaTip) != 0:

            if siralaTip == "okunma tarihi":
                tabloVerileri = tarihMatrisSirala()
            if siralaTip == "eklenme tarihi":
                tabloVerileri = tabloVerileri
            if siralaTip == "alfabetik":
                tabloVerileri = strMatrisSirala(0)
            if siralaTip == "derece":
                tabloVerileri = intMatrisSirala(7)
            if siralaTip == "sayfa":
                tabloVerileri = intMatrisSirala(3)

            if siralaDogruluk == "ters":
                tabloVerileri.reverse()


        self.kitapListesi.delete(*self.kitapListesi.get_children())
        for index, data in enumerate(tabloVerileri):
            "print(data)"
            self.kitapListesi.insert("", index, text=index+1, values=data)

    def tabloyuCek(self):
        self.cur.execute("SELECT * FROM {}".format(self.tabloIsim))
        self.data = self.cur.fetchall()
        return self.data

    def sütunVeriTürleriCek(self, columnName):
        hamVeriTürleri = []
        self.cur.execute("SELECT {} FROM {}".format(columnName, self.tabloIsim))
        data = self.cur.fetchall()
        for current in data:
            if hamVeriTürleri.count(current) == 0:
                hamVeriTürleri.append(current)
        veriTürleri = [a[0] for a in hamVeriTürleri]
        return veriTürleri

    def sütunCek(self, columnName, columnData):
        columnData = "\"{}\"".format(columnData)
        self.cur.execute("SELECT {} FROM {} WHERE {} = {}".format(columnName, self.tabloIsim, columnName, columnData))
        data = self.cur.fetchall()
        data = [a[0] for a in data]

        return data

    def durumaGoreVeriCek(self, columnName, columnData, ints=[]):
        if type(columnData) == list:
            self.cur.execute("SELECT * FROM {} WHERE {}".format(self.tabloIsim, self.cnvListToCmd(columnData, columnName, intPos=ints)))
        elif type(columnData) == str:
            columnData = "'{}'".format(columnData)
            self.cur.execute("SELECT * FROM {} WHERE {} = {}".format(self.tabloIsim, columnName, columnData))
        else:
            self.cur.execute("SELECT * FROM {} WHERE {} = {}".format(self.tabloIsim, columnName, columnData))

        data = self.cur.fetchall()
        return data

    def durumaGoreVeriCekAralık(self, name, start_index, stop_index):
        self.cur.execute("SELECT * FROM {} WHERE {} >= {} and {} <= {}".format(self.tabloIsim, name, start_index, name, stop_index))
        return self.cur.fetchall()

    def makeCalendar(self, yil, ay):
        calendar = cl.monthcalendar(yil, ay)
        cleanCl = []
        for index_a in calendar:
            for index_b in index_a:
                if index_b != 0:
                    cleanCl.append(index_b)
        return cleanCl

    def cnvTupleToString(self, data):
        dataNew=""
        tekrar = 0
        for a in data:
            tekrar += 1
            if tekrar == 1:
                dataNew += "("
            if type(a) == str:
                a = "'{}'".format(a)
            dataNew += str(a)
            if not tekrar == len(data):
                dataNew += ", "
            else:
                dataNew += ")"
        return dataNew

    def cnvListToCmd(self, liste, clmNames, intPos=[]): 
        if type(liste) != list:
            raise Exception("Argument liste must be a list.")
            return

        if type(clmNames) != list and type(clmNames) != str:
            raise Exception("Argument clmNames must be a list or a string, either way it works.")
            return

        if type(clmNames) == list and len(clmNames) != len(liste):
            raise Exception("Lenght of liste and clmNames must be equal.")
            return

        dataNew = ""

        for index, data in enumerate(liste):
            if type(clmNames) == str:
                dataNew += clmNames
            else:
                dataNew += clmNames[index]

            dataNew += " = "

            if intPos.count(index) != 0:
                dataNew += str(data)
            else:
                dataNew += "'{}'".format(data)

            if index+1 != len(liste):
                dataNew += " AND "

        print("this is sql command: ", dataNew)
        return dataNew

    def tarihCek(self, format="all"):
        now = t.datetime.now()
        gün = int(now.strftime("%d"))
        ay = int(now.strftime("%m"))
        yil = int(now.strftime("%Y"))

        if format == "gün":
            return gün
        elif format == "ay":
            return ay
        elif format == "yıl":
            return yil
        return "{}/{}/{}".format(gün, ay, yil)

    def deleteByQueue(self, queue):
        return



if __name__ == "__main__":
    myAssistant = BookAssistant()
