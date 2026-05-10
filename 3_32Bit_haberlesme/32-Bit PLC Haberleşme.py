import win32com.client
import socket
import select
import time

print("-32-Bit PLC Haberleşme-")

plc = None

try:
    plc = win32com.client.Dispatch("ActUtlType.ActUtlType")
    plc.ActLogicalStationNumber = 1 
    
    if plc.Open() != 0:
        print("PLC'ye bağlanılamadı.")
        exit()
        
    print("PLC bağlantısı sağlandı.")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 6000))
    server.listen(1)
    conn, addr = server.accept()
    print("Sistem bağlandı")

    # YENİ: Kalp atışı için değişkenler
    son_kalp_atisi = time.time()
    kalp_durumu = 0

    while True:
        # YENİ: Her 1 saniyede bir D111'i 0 veya 1 yap
        su_an = time.time()
        if su_an - son_kalp_atisi >= 1.0:
            kalp_durumu = 1 if kalp_durumu == 0 else 0
            plc.SetDevice("D111", kalp_durumu)
            son_kalp_atisi = su_an

        # 1.Sistemden gelen koordinatları dinle
        readable, _, _ = select.select([conn], [], [], 0.05)
        if readable:
            data = conn.recv(1024).decode('utf-8')
            if not data: 
                break
            
            veriler = data.split(',')
            if len(veriler) == 5:
                cx, cy, cz, tetik, temizlenen_ot = map(int, veriler)
                
                plc.SetDevice("D110", temizlenen_ot)
                
                if tetik == 1:
                    plc.SetDevice("D100", cx)
                    plc.SetDevice("D101", cy)
                    plc.SetDevice("D102", cz)
                    plc.SetDevice("D103", 1) 
                    print(f"🎯 Yeni hedef İletildi -> X:{cx} Y:{cy} Z:{cz} | Temizlenen: {temizlenen_ot}")

        # 2. PLC'nin işlemi bitirme durumunu (D104) kontrol et
        deger = plc.GetDevice("D104")
        islem_tamam = deger[1] if type(deger) is tuple else deger

        if islem_tamam == 1:
            print("✅ PLC İşlemi bitirdi.")
            conn.sendall("IMHA_EDILDI".encode('utf-8'))
            
            plc.SetDevice("D104", 0)
            plc.SetDevice("D103", 0)
            time.sleep(0.5)

except Exception as e:
    print(f"Haberleşme Kesintisi: {e}")
finally:
    if plc is not None:
        plc.Close()
