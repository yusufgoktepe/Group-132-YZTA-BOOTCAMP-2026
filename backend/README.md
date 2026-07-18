# CampusMatch AI Backend

FastAPI servisi öğrenci, kulüp ve etkinlik örneklerini sunar. Öneri endpoint'i profil
eşleşmesini `data` branch'inden gelen sentetik swipe sinyaliyle birleştirir.

## Çalıştırma

Proje kökünde:

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API dokümantasyonu: `http://localhost:8000/docs`

## Endpointler

- `GET /health`
- `GET /students`
- `GET /clubs`
- `GET /events`
- `POST /recommendations/student/{student_id}`
- `POST /recommendations/profile`

Öneri skoru, açıklanabilir profil eşleşmesinin `%80` ve sentetik etkileşimlerdeki sağa
kaydırma oranının `%20` ağırlıklı birleşimidir. Eğitilmiş `.pkl` model mobil uygulamaya
yüklenmez; model dosyaları yalnızca backend/ML tarafında tutulur.

Mobil uygulama `profile_v2.schema.json` sözleşmesini `/recommendations/profile`
endpoint'ine gönderir. Eğitim referansı sürümlenir; üniversite/program listesi
güncellendiğinde eski profillerin hangi listeyle oluşturulduğu takip edilebilir.
