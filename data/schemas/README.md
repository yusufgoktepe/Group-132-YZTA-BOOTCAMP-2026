# CampusMatch Veri Sözleşmeleri

## Aktif sürümler

- Profile V2, mevcut mobil onboarding sözleşmesidir.
- Event V3, Faz 1 ile eklenen iki katmanlı etkinlik sözleşmesidir.
- Organizer, participation, rating, interest weight ve moderation action V3,
  güvenli mikro etkinlik akışının veri temelidir.

| Şema | Amaç |
|---|---|
| `profile_v2.schema.json` | Mevcut öğrenci onboarding profili |
| `event_v3.schema.json` | `official` ve `micro` etkinlikler |
| `organizer_v3.schema.json` | Öğrenci ve kurumsal organizatörler |
| `participation_v3.schema.json` | Katılım isteği ve doğrulama durumu |
| `rating_v3.schema.json` | Sunucu tarafında kimlikli, istemciye anonim rating |
| `interest_weight_v3.schema.json` | Normalize dinamik ilgi ağırlıkları |
| `moderation_action_v3.schema.json` | Güven engeli ve insan incelemesi kayıtları |

## V3 temel kuralları

- Her etkinlik `official` veya `micro` katmanındadır.
- Mikro etkinlikte `expires_at` ve `location_name` zorunludur.
- Mikro etkinlikte `approval_status=not_required` kullanılır.
- Resmî etkinlikte onay durumu `pending`, `approved` veya `rejected` olur.
- Rating 1-5 aralığındadır ve puanlayan profil genel API cevabına taşınmaz.
- İlgi `weight` değerleri profil bazında toplam 1 olacak şekilde normalize edilir.
- Güven engeli yalnız veriyi silmez; ayrı moderation action kaydıyla izlenir.

## Örnek veri

`data/sample/v3` altındaki örnekler
`python ml/generate_v3_dataset.py` komutuyla tekrar üretilebilir:

- 80 organizatör
- 1.000 sentetik profil
- 80 resmî etkinlik
- 170 mikro etkinlik
- 1.200 katılım
- 800 rating
- 1.000 profil için 5.393 başlangıç ilgi ağırlığı

V2 dosyaları geriye uyumluluk ve model karşılaştırması için korunur. V3 seed akışı,
V2 profillerini kalıcı profil sözleşmesine dönüştürerek ilişkili katılım, rating ve
ilgi ağırlıklarının yabancı anahtar bütünlüğüyle yüklenmesini sağlar.

## Doğrulama

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_phase1_schema.py -q
```

Testler tüm örnek satırları JSON Schema kurallarına göre doğrular; event-organizer
ilişkisini, ilgi normalizasyonunu, migration veri korumasını ve seed idempotency'yi
kontrol eder.
