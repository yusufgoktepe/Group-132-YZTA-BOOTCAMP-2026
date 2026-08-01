# CampusMatch AI Backend

FastAPI servisi; verisini **SQLite** üzerinde tutar. Kulüp, etkinlik ve örnek öğrenci
kayıtları uygulama açılışında `data/sample` altındaki CSV dosyalarından veritabanına
aktarılır. Kullanıcı profilleri ve kullanıcı hareketleri (`like`, `skip`, `save`,
`unsave`, `view_detail`) veritabanında kalıcı olarak saklanır; servis yeniden
başlatıldığında kaybolmaz.

Faz 1 ile mevcut kayıtları silmeyen ileri yönlü migration ve iki katmanlı Event V3
verisi eklenmiştir. Açılışta 4 geriye uyumlu demo etkinliğine ek olarak 1.000 sentetik
profil, 80 resmî ve 170 mikro etkinlik, 1.200 katılım, 800 rating ve 5.393 başlangıç
ilgi ağırlığı idempotent biçimde seed edilir.

Faz 4 ile interaction kayıtları dinamik ilgi vektörünü transaction içinde günceller;
dwell eşikleri ve açıklanabilir V3 ranking bu kalıcı vektörü kullanır.

## Kurulum ve çalıştırma

Proje kökünde:

```bash
python -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API dokümantasyonu: `http://localhost:8000/docs`

> Python 3.10 veya üzeri gerekir (tip birleşimleri `str | None` biçiminde yazılmıştır).

Fiziksel telefondan bağlanırken `--host 0.0.0.0` ile başlatın ve mobil `.env` dosyasına
bilgisayarın yerel ağ IP adresini yazın.

## Testler

```bash
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
backend/.venv/bin/python -m pytest
```

Testler geçici bir veritabanı dosyası kullanır (`CAMPUSMATCH_DB_PATH` fixture içinde
ayarlanır); geliştirme veritabanınız etkilenmez.

## Veritabanı

| Ayar | Değer |
|---|---|
| Dosya | `backend/campusmatch.sqlite` |
| Değiştirmek için | `CAMPUSMATCH_DB_PATH` ortam değişkeni |
| Şema kurulumu | Uygulama açılışında otomatik (`init_db`) |

Tablolar:

| Tablo | İçerik |
|---|---|
| `clubs`, `events`, `students` | CSV'den aktarılan referans veri. Aktarım idempotenttir: aynı kimlikler tekrar yüklendiğinde güncellenir, çoğaltılmaz. |
| `profiles` | Onboarding akışından gelen öğrenci profilleri. Liste alanları JSON metni olarak tutulur. |
| `interactions` | Kullanıcı hareketleri. `action` sütunu veritabanı düzeyinde `CHECK` ile sınırlandırılmıştır. |
| `organizers` | Öğrenci ve kurumsal organizatör kimliği, doğrulama ve güven durumu. |
| `participations` | Tekil katılım isteği ve katılım doğrulaması. |
| `ratings` | Etkinlik bazında tekil, istemci tarafında anonim organizatör puanı. |
| `user_interest_weights` | Profil bazında normalize dinamik ilgi ağırlıkları. |
| `moderation_actions` | Güven engeli, feed kaldırma ve insan incelemesi kayıtları. |
| `schema_migrations` | Uygulanan ileri yönlü migration sürümleri. |

V3 örnek verisini tekrar üretmek için:

```powershell
.\.venv\Scripts\python.exe ml\generate_v3_dataset.py
```

Veritabanını sıfırlamak için dosyayı silmek yeterlidir; sonraki açılışta yeniden kurulur.

```bash
rm backend/campusmatch.sqlite
```

Kaydedilen etkinlikler ayrı bir tabloda tutulmaz; her etkinlik için **en son**
`save` / `unsave` hareketi dikkate alınarak hesaplanır. Böylece kaydetme geçmişi de
korunur.

## Endpointler

### Sağlık

| Metot | Adres | Açıklama |
|---|---|---|
| `GET` | `/health` | Servis durumu, veritabanı yolu ve tablo satır sayıları |

### Referans veri

| Metot | Adres | Açıklama |
|---|---|---|
| `GET` | `/events` | Tüm etkinlikler. `?category=technology` ile filtrelenir. |
| `GET` | `/events/{event_id}` | Tek etkinlik |
| `GET` | `/clubs` | Kulüpler |
| `GET` | `/students` | Örnek öğrenci kayıtları (Sprint 1 verisi) |

### Profiller

| Metot | Adres | Açıklama |
|---|---|---|
| `POST` | `/profiles` | Profil oluşturur, `profile_id` döner (`201`) |
| `GET` | `/profiles/{profile_id}` | Profili okur |
| `PUT` | `/profiles/{profile_id}` | Profili günceller (profil düzenleme akışı) |

### Kullanıcı hareketleri

| Metot | Adres | Açıklama |
|---|---|---|
| `POST` | `/interactions` | `like`, `skip`, `save`, `unsave`, `view_detail`, `apply` kaydeder; `interaction_key` ile tekrarları tekilleştirir (`201`) |
| `GET` | `/profiles/{profile_id}/interactions` | Hareket geçmişi. `?action=save` ile filtrelenir. |
| `GET` | `/profiles/{profile_id}/saved-events` | Kaydedilen etkinlikler |
| `GET` | `/profiles/{profile_id}/interest-weights` | Normalize açık/davranış ilgi ağırlıkları |
| `POST` | `/events` | Profil sahibi adına mikro etkinlik yayımlar (`201`) |
| `PUT` | `/events/{event_id}` | Sahibinin mikro etkinliğini günceller |
| `DELETE` | `/events/{event_id}?actor_profile_id=...` | Mikro etkinliği `cancelled` durumuna geçirir |
| `POST` | `/events/{event_id}/apply` | İdempotent katılım isteği oluşturur (`201`) |
| `GET` | `/profiles/{profile_id}/participations` | Profilin katılım isteklerini listeler |
| `PATCH` | `/participations/{participation_id}` | Yetkiye ve durum geçişine göre katılımı günceller |
| `POST` | `/events/{event_id}/ratings` | Doğrulanmış katılım sonrası tekil anonim puan oluşturur |
| `GET` | `/organizers/{organizer_id}/trust-summary` | Puanlayan kimliklerini içermeyen güven özeti |
| `PATCH` | `/organizers/{organizer_id}/verification` | Moderatör anahtarıyla organizatör doğrulaması |
| `PATCH` | `/events/{event_id}/approval` | Moderatör anahtarıyla resmî yayın onayı |
| `GET` | `/moderation/actions` | Korumalı moderasyon kayıt listesi |

Moderasyon uçları `CAMPUSMATCH_MODERATOR_KEY` ortam değişkeni ve
`X-Moderator-Key` istek başlığı ile korunur. Anahtar yapılandırılmamışsa uçlar `503`,
yanlış anahtarda `403` döndürür.

### Kişiselleştirilmiş feed

| Metot | Adres | Açıklama |
|---|---|---|
| `GET` | `/feed?profile_id=...&limit=20&cursor=...` | En fazla 30 güvenli aday arasından sıralanmış, cursor tabanlı kart sayfası |

Feed; yayın/onay, başlangıç ve sona erme zamanı, kota, üniversite/katılım biçimi,
program/sınıf hedefi, organizatör doğrulaması, kara liste ve daha önce tüketilmiş
kart filtrelerini uygular. Her cevap sonraki interaction isteklerinde kullanılacak
bir `feed_token` taşır.

### Öneriler

| Metot | Adres | Açıklama |
|---|---|---|
| `POST` | `/recommendations/profile` | Kaydedilmemiş profil için öneri. **Mobil uygulamanın kullandığı uçtur.** |
| `POST` | `/recommendations/profile/{profile_id}` | Kayıtlı profil için öneri; kullanıcının geçmiş hareketlerini de hesaba katar |
| `POST` | `/recommendations/student/{student_id}` | Sprint 1 öğrenci kayıtları için öneri |

## Öneri skoru

Skor üç sinyalin toplamıdır ve `0-100` aralığına sıkıştırılır:

| Sinyal | Ağırlık |
|---|---|
| Açıklanabilir profil eşleşmesi (ilgi, program, amaç, katılım biçimi, ücret, dil) | %80 |
| Sentetik swipe verisindeki sağa kaydırma oranı | %20 |
| Kullanıcının kendi hareketleri (`save` +12, `like` +8, `skip` −25) | doğrudan ekleme |

Her öneri `score_breakdown` ile hangi sinyalin ne kadar katkı yaptığını, `reasons` ile de
kullanıcıya gösterilecek gerekçeleri döner. Skorlama tamamen kural bazlıdır; çalışma
zamanında bir model dosyasına bağımlı değildir.

Eğitilmiş XGBoost modeli servise bağlı değildir. Kural bazlı skorla karşılaştırması
`ml/model_comparison.md` ve `ml/metrics.json` dosyalarındadır; üretmek için:

```bash
python ml/compare_baseline_vs_model.py
```

## Hata cevapları

Tüm hatalar aynı gövde biçiminde döner:

```json
{
  "detail": "İstek gövdesi geçersiz. Kontrol edilmesi gereken alanlar: class_year.",
  "error": {
    "code": "validation_error",
    "message": "İstek gövdesi geçersiz. Kontrol edilmesi gereken alanlar: class_year.",
    "fields": [
      { "field": "class_year", "message": "Değer beklenen biçimde değil.", "type": "string_pattern_mismatch" }
    ]
  }
}
```

| Durum | `error.code` |
|---|---|
| `422` | `validation_error` — eksik veya biçimi hatalı alanlar `fields` içinde listelenir |
| `404` | `profile_not_found`, `event_not_found`, `student_not_found` |
| `500` | `internal_error` — iç ayrıntılar istemciye sızdırılmaz |

`detail` alanı FastAPI'nin varsayılan sözleşmesiyle uyumlu kalması için korunur.

## Mobil sözleşme

Mobil uygulama `profile_v2.schema.json` biçimindeki gövdeyi `/recommendations/profile`
ucuna gönderir ve cevaptan `event.event_id`, `score`, `reasons` alanlarını okur. Bu üç
alan `backend/tests/test_api.py::test_mobile_contract_fields_are_stable` testiyle
korunmaktadır.

Eğitim referansı sürümlenir (`education_reference_version`); üniversite/program listesi
güncellendiğinde eski profillerin hangi listeyle oluşturulduğu takip edilebilir.
