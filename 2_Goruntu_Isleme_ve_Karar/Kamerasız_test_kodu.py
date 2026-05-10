from ultralytics import YOLO
import cv2

# Kamera çözünürlüğü ve mm dönüşüm oranları
CAM_W, CAM_H = 640, 480
SCALE_X = 600.0 / CAM_W
SCALE_Y = 450.0 / CAM_H
CENTER_X, CENTER_Y = CAM_W // 2, CAM_H // 2

model = YOLO("best.pt")
print("MODELİN BİLDİĞİ SINIFLAR:", model.names)

# TEST EDİLECEK FOTOĞRAFIN YOLu
TEST_FOTO_YOLU = "agri_0_113.jpeg"

orijinal_img = cv2.imread(TEST_FOTO_YOLU)
if orijinal_img is None:
    print("HATA: Fotoğraf bulunamadı. Dosya yolunu kontrol edin.")
    exit()

# Fotoğrafı kamera boyutlarına kalibre et
orijinal_img = cv2.resize(orijinal_img, (CAM_W, CAM_H))

tamamlanan_idler = set()
aktif_hedef = None
plc_mesgul = False

print("Sanal test çalışıyor... Otu 'imha etmek' için BOŞLUK (SPACE) tuşuna basın.")

while True:
    # Her döngüde fotoğrafın temiz bir kopyasını al
    img = orijinal_img.copy()

    results = model.track(img, persist=True, verbose=False)

    bekleyenler = []

    for r in results:
        boxes = r.boxes

        if boxes.id is None:
            continue

        for i in range(len(boxes)):
            nesne_id = int(boxes.id[i])
            sinif_id = int(boxes.cls[i])

            # Sadece Otları (1) kabul et, Susamları (0) es geç
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
                    print(f"SİMÜLASYON: Hedef kilitlendi (X:{mm_x}, Y:{mm_y}). Vurmak için SPACE tuşuna basın.")
            else:
                cv2.rectangle(img, (kx1, ky1), (kx2, ky2), (255, 255, 0), 1)
                cv2.putText(img, "Bekliyor", (kx1, ky1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    cv2.imshow('Sanal Test Ekranı', img)

    # Klavye Simülasyon Kontrolleri
    tus = cv2.waitKey(100) & 0xFF
    if tus == ord('r'):
        tamamlanan_idler.clear()
        plc_mesgul = False
        print("Hafıza sıfırlandı.")
    elif tus == ord(' '):  # SPACE (Boşluk) tuşuna basıldığında PLC'nin işi bitirdiğini varsay
        if aktif_hedef is not None:
            tamamlanan_idler.add(aktif_hedef)
            aktif_hedef = None
            plc_mesgul = False
            print("SİMÜLASYON: Ot başarıyla imha edildi!")
    elif tus == ord('q'):
        break

cv2.destroyAllWindows()
