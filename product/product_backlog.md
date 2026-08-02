# Product Backlog

Backlog, çalışan depo durumu ve Faz 0 ürün kararlarıyla 1 Ağustos 2026 tarihinde
yeniden eşitlenmiştir. GitHub Projects'e aktarılırken aynı kimlikler korunmalıdır.

| ID | Öncelik | İş / User story | Durum | Faz |
|---|---|---|---|---|
| PB-01 | P0 | Ürün vizyonu ve üniversite öğrencisi odağını sabitle | Done | 0 |
| PB-02 | P0 | Swipe hareket ve navigasyon sözleşmesini belirle | Done | 0 |
| PB-03 | P0 | Resmî ve mikro etkinlik ayrımını tanımla | Done | 0 |
| PB-04 | P0 | MVP içi/dışı kapsamı ve güven kurallarını belirle | Done | 0 |
| PB-05 | P0 | User story, kullanıcı akışı ve API ihtiyaçlarını güncelle | Done | 0 |
| PB-06 | P0 | Event V3, organizer, participation ve rating şemalarını oluştur | Done | 1 |
| PB-07 | P0 | SQLite migration ve V3 seed altyapısını kur | Done | 1 |
| PB-08 | P0 | V2 etkinliklerini PDF hedef boyutunda resmî/mikro V3 veriye dönüştür | Done | 1 |
| PB-09 | P0 | Cursor tabanlı `GET /feed` candidate generation ekle | Done | 2 |
| PB-10 | P0 | Interaction idempotency ve feed bağlamını ekle | Done | 2 |
| PB-11 | P0 | Mobil profili `/profiles` ile kalıcılaştır | Done | 2 |
| PB-12 | P0 | Ana keşfi swipe kart kuyruğuna dönüştür | Done | 3 |
| PB-13 | P0 | Mobil swipe olaylarını backend'e bağla | Done | 3 |
| PB-14 | P0 | Cursor prefetch ve çevrim dışı tekrar kuyruğu ekle | Done | 3 |
| PB-15 | P0 | Kaydedilenler ekranını backend kaynağına geçir | Done | 3 |
| PB-16 | P0 | Dinamik ilgi vektörü ve dwell güncellemesini uygula | Done | 4 |
| PB-17 | P0 | Açıklanabilir V3 ranking ve score breakdown ekle | Done | 4 |
| PB-18 | P1 | Mikro etkinlik oluşturma mobil akışını geliştir | Done | 5 |
| PB-19 | P1 | Etkinlik CRUD, kota ve sona erme kurallarını ekle | Done | 5 |
| PB-20 | P1 | Katılım isteği ve katılım doğrulamasını ekle | Done | 5 |
| PB-21 | P1 | Anonim rating ve organizatör güven skorunu ekle | Done | 6 |
| PB-22 | P1 | Güven eşiği, raporlama ve moderasyon kaydını ekle | Done | 6 |
| PB-23 | P1 | Resmî organizatör doğrulama ve yayın onayı ekle | Done | 6 |
| PB-24 | P2 | Ranking veri setini zaman bazlı ayır ve metrikleri ölç | Done | 7 |
| PB-25 | P2 | Hibrit XGBoost deneyini kural bazlı sistemle karşılaştır | Done | 7 |
| PB-26 | P2 | Mikro etkinlik aday üretimi için K-Means deneyi yap | Done | 7 |
| PB-27 | P1 | Uçtan uca mobil, API, güven ve offline testlerini tamamla | Done | 8 |
| PB-28 | P1 | Fiziksel cihaz demo senaryosu ve jüri dokümantasyonunu güncelle | Ready for acceptance | 8 |

## Tamamlanmış Teknik Temel

- Expo Router mobil iskeleti, onboarding, profil V2, liste keşfi ve detay ekranı
- FastAPI referans endpoint'leri
- SQLite profil ve interaction tabloları
- Profil CRUD, interaction ve kaydedilen etkinlik endpoint'leri
- Açıklanabilir kural bazlı recommendation servisi
- 1.000 profil, 500 etkinlik ve 50.000 etkileşimlik V2 sentetik veri
- XGBoost baseline ve kural bazlı karşılaştırma

Bu çıktılar yeniden geliştirilmez; V3 hedefi için genişletilir.
