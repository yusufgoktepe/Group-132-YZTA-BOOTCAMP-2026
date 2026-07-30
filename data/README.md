# CampusMatch Veri Katmanları

Projede gerçek kullanıcı verisi kullanılmaz. Veri kaynakları kullanım amaçlarına göre ayrılmıştır.

| Veri | Amaç | Uygulamada Görünür mü? |
|---|---|---|
| `sample/v2/profiles_v2.csv` | Model eğitimi ve değerlendirme | Hayır |
| `sample/v2/events_v2.csv` | Model eğitimi ve değerlendirme | Hayır |
| `sample/v2/interactions_v2.csv` | Model eğitimi ve değerlendirme | Hayır |
| `sample/clubs_sample.csv` | Bootcamp demo kulüp kataloğu | Evet |
| `sample/events_sample.csv` | Bootcamp demo etkinlik kataloğu | Evet |
| `mobile/data/demo-events.json` | Backend kapalıyken mobil yedek katalog | Evet |

## Demo Kataloğu

Demo kataloğu 7 kategori, 14 kulüp ve 56 etkinlik içerir. Tüm kayıtlar sentetiktir;
gerçek bir kurum veya etkinlik ilanı olduğu iddia edilmez. Backend ve mobil yedek veri
aynı üreticiden çıktığı için etkinlik kimlikleri iki tarafta da eşleşir.

Kataloğu yeniden üretmek için proje kökünde:

```powershell
.\.venv\Scripts\python.exe ml\generate_demo_catalog.py
```

Üretimden sonra `clubs_sample.csv`, `events_sample.csv` ve `demo-events.json`
dosyalarının birlikte commit edilmesi gerekir.

## Gerçek Kullanıcı Akışı

Uygulamaya kayıt olan öğrenciler sentetik profil havuzuna eklenmez. Profil ve
interaction verileri Sprint 3 kalıcılık çalışmasında SQLite'a yazılacaktır. Yeni
kullanıcılar için mevcut açıklanabilir profil skoru cold-start önerisi üretir.
