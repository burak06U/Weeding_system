Otonom Yabancı Ot Tespit ve Müdahale Sistemi

Bu proje, Akdeniz Üniversitesi Elektrik-Elektronik Mühendisliği bitirme çalışmam kapsamında geliştirilmiştir. Temel amacım; tarım arazilerinde yetişen yabani otları derin öğrenme yöntemleriyle gerçek zamanlı olarak tespit etmek ve endüstriyel bir PLC sistemiyle otonom olarak müdahale etmektir. Bu çalışmamda ana mahsul susam bitkisidir.
Klasik tarım ilaçlarının (herbisit) kullanımını azaltmayı ve çevre dostu, akıllı tarım teknolojilerine yerli bir alternatif sunmayı hedefledim.

Sistem Nasıl Çalışıyor?
1.Görsel Algılama: Kameradan alınan anlık görüntüler YOLOv8 yapay zeka modeliyle işlenir. Sistem, ana mahsul olan susam ile yabani ot ayrımını gerçek zamanlı olarak yapar.
2.Koordinat Hesabı: Tespit edilen otun ekrandaki konumu, mekanizmanın anlayabileceği milimetre cinsinden gerçek dünya koordinatlarına dönüştürülür.
3.Asenkron Haberleşme: 64-bit Python ortamında çalışan yapay zeka, hesapladığı koordinatları ve güncel istatistikleri TCP/IP soketleri üzerinden 32-bit bir haberleşme sunucusuna aktarır.
4.PLC ile Fiziksel Müdahale: Haberleşme sunucusu, MX Component üzerinden Mitsubishi FX5U PLC'ye bağlanarak hedef koordinatlarını iletir ve sistemi tetikler. PLC, kartezyen sistemin hareket sürecini yönetir ve işlem bittiğinde yapay zekaya geri bildirim gönderir.
5.HMI ile Canlı Takip: Sistemin o anki fiziksel durumu (X-Y-Z eksenlerindeki hareketleri), başarıyla temizlenen toplam ot sayısı ve olası bağlantı hataları, endüstriyel HMI ekranı üzerinden anlık olarak izlenir.

Kullanılan Teknolojiler
Yapay Zeka & Görüntü İşleme: YOLOv8, Google Colab
Programlama: Python 3.11 (64-bit Görüntü İşleme & 32-bit Haberleşme)
Haberleşme Protokolleri: TCP/IP Sockets, Mitsubishi MX Component (ActUtlType)
Donanım & Kontrol: Mitsubishi FX5U PLC
HMI (Ekran) Tasarımı: Mitsubishi GT Designer3
Geliştirme Ortamı: PyCharm, GX Works3

Proje Klasör Yapısı
1_Yapay_Zeka_Egitimi: YOLOv8 modelinin eğitildiği Google Colab dosyası (.ipynb) ve modelin başarı oranını gösteren örnek tahmin çıktıları.
2_Goruntu_Isleme_ve_Karar: Sistemde kullanılan canlı kamera kontrol yazılımı, Kamera test çıktıları, eğitilmiş yapay zeka ağırlık dosyası (best.pt), kamerasız test yazılımı ve test fotoğrafları.
3_32Bit_haberlesme: 64-bit yapay zeka ile donanım arasındaki köprüyü kuran, arka planda PLC'ye veri yazan/okuyan 32-bit Python haberleşme sunucusu.
4_PLC_Ladder_Diyagrami: Mitsubishi FX5U PLC'nin GX Works3 proje dosyası ve çalışma mantığını anlatan ladder diyagramı ekran görüntüleri.
5_HMI_ekran: GT Designer3 arayüz proje dosyası (.GTX) ve tasarımın ekran görüntüsü.
6_kamera_HMI_sonuclar: Kameradan alınan canlı tespitlerin ve HMI ekranındaki hareket/istatistik güncellemelerinin senkronize çalıştığını gösteren ekran görüntüleri.

Eklemeyi Hedeflediklerim
*Ana mahsül sayımı yapmak ve HMI ekranda kullanıcıyı bilgilendirmek
*Zararlı böcek tespiti
*Ana mahsülün kalite durumunu analizi

Geliştirici
Burak - Akdeniz Üniversitesi Elektrik-Elektronik Mühendisliği (4. Sınıf)