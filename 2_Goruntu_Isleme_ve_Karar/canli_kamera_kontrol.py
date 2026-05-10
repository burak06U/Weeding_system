from ultralytics import YOLO
import cv2
import socket
import select

# Kamera çözünürlüğü ve mm dönüşüm oranları
CAM_W, CAM_H = 640, 480
SCALE_X = 600.0 / CAM_W
SCALE_Y = 450.0 / CAM_H
CENTER_X, CENTER_Y = CAM_W // 2, CAM_H // 2

# 32-bit haberleşme
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 6000))
except:
    print("32-bit haberleşme kodunu çalıştırıp tekrar deneyin")
    exit()

# Evrensel model yolu
model = YOLO(r"C:\Users\burak\PycharmProjects\pythonProject2\best.pt")
print("MODELİN BİLDİĞİ SINIFLAR:", model.names)

cap = cv2.VideoCapture(0)
cap.set(3, CAM_W)
cap.set(4, CAM_H)

tamamlanan_idler = set()
aktif_hedef = None
plc_mesgul = False

print("Sistem çalışıyor...")

while True:
    success, img = cap.read()
    if not success: break

    results = model.track(img, persist=True, verbose=False)

    # PLC'den gelen görev bitiş sinyalini dinle
    readable, _, _ = select.select([client], [], [], 0.01)
    if readable:
        msg = client.recv(1024).decode('utf-8')
        if "IMHA_EDILDI" in msg and aktif_hedef is not None:
            tamamlanan_idler.add(aktif_hedef)
            aktif_hedef = None
            plc_mesgul = False
            client.sendall(f"0,0,0,0,{len(tamamlanan_idler)}".encode('utf-8'))

    bekleyenler = []

    for r in results:
        boxes = r.boxes

        # Takip ID'si olmayan nesneleri es geç
        if boxes.id is None:
            continue

        for i in range(len(boxes)):
            nesne_id = int(boxes.id[i])
            sinif_id = int(boxes.cls[i])  # Modelden gelen sınıf ID'si

            # Sadece Otları (1) kabul et, Susamları (0) geç
            if sinif_id != 1:
                continue

            x1, y1, x2, y2 = map(int, boxes.xyxy[i])
            gx = int((x1 + x2) / 2)
            gy = int((y1 + y2) / 2)

            alan = (x2 - x1) * (y2 - y1)
            z_eksen = 100 if alan > 20000 else 50

            # Vurulan otları gri çiz ve atla
            if nesne_id in tamamlanan_idler:
                cv2.rectangle(img, (x1, y1), (x2, y2), (128, 128, 128), 1)
                cv2.putText(img, "TAMAM", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
                continue

            bekleyenler.append({
                "id": nesne_id, "x": gx, "y": gy, "z": z_eksen, "kutu": (x1, y1, x2, y2)
            })

    # Hedefleri Y eksenine (aşağıdan yukarı) sırala ve PLC'ye gönder
    if bekleyenler:
        sirali = sorted(bekleyenler, key=lambda d: d['y'], reverse=True)

        for index, ot in enumerate(sirali):
            kx1, ky1, kx2, ky2 = ot["kutu"]

            if index == 0:
                cv2.rectangle(img, (kx1, ky1), (kx2, ky2), (0, 255, 0), 1)
                cv2.circle(img, (ot["x"], ot["y"]), 4, (0, 255, 0), -1)
                cv2.putText(img, f"HEDEF Z:{ot['z']}", (kx1, ky1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

                if not plc_mesgul:
                    aktif_hedef = ot["id"]
                    plc_mesgul = True

                    mm_x = int((ot["x"] - CENTER_X) * SCALE_X)
                    mm_y = int((CENTER_Y - ot["y"]) * SCALE_Y)

                    client.sendall(f"{mm_x},{mm_y},{ot['z']},1,{len(tamamlanan_idler)}".encode('utf-8'))
            else:
                cv2.rectangle(img, (kx1, ky1), (kx2, ky2), (255, 255, 0), 1)
                cv2.putText(img, "Bekliyor", (kx1, ky1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    cv2.imshow('Otonom Görüntü İşleme', img)

    tus = cv2.waitKey(1) & 0xFF
    if tus == ord('r'):
        tamamlanan_idler.clear()
        plc_mesgul = False
    elif tus == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.close()
