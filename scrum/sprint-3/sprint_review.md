# Sprint 3 Review

## Sonuç

Sprint 3'te Faz 0–8 kapsamındaki ürün, veri, feed, mobil swipe, davranış öğrenmesi,
mikro etkinlik, güven ve offline model değerlendirmesi tamamlandı. Ana öğrenci akışı
profil oluşturmadan öneri keşfine, kaydetmeye, katılım isteğine ve anonim puanlamaya
kadar backend ile kalıcı çalışır durumdadır.

## Kabul Edilen Çıktılar

- Resmî/mikro Event V3 veri modeli ve kayıpsız SQLite migration
- 306 etkinliklik birleşik katalog ve ÖSYM kaynaklı 202 üniversite/14.281 program referansı
- Cursor tabanlı, güven ve kota filtreli açıklanabilir feed
- Idempotent interaction ve çevrim dışı mobil tekrar kuyruğu
- Mobil swipe, detay, kaydedilenler, oluşturma ve katılımlar ekranları
- Final onboarding, swipe keşif ve açıklanabilir etkinlik detayı ekran kanıtları
- Dinamik ilgi vektörü ve dwell tabanlı ranking güncellemesi
- Mikro etkinlik sahipliği, kota, sona erme ve katılım durumları
- Anonim rating, güven eşiği, yayın engeli ve korumalı moderasyon
- Temporal XGBoost/hibrit karşılaştırması ve K-Means deneyi
- Tek senaryoda profil → feed → save retry → mikro etkinlik → katılım → rating → güven engeli testi

## Ölçülen Kalite

- Backend/ML testleri: final çalıştırmada 74 test
- Mobil TypeScript, Expo lint ve sözleşme kontrolü: başarılı
- Expo web production export, 13 statik rota ve iOS Hermes export: başarılı
- Kural bazlı test NDCG@10: `0.7992`
- XGBoost test NDCG@10: `0.8032`; `%2` promotion eşiğini aşmadığı için production'a alınmadı

## Açık Dış Kabul

Yeni Faz 5–6 ekranlarının fiziksel iPhone üzerinde dokunma, klavye, swipe ve VoiceOver
kontrolü bu çalışma ortamından yapılamaz. Otomatik kalite kapıları tamamlanmıştır;
cihaz kontrolü teslim öncesi insan kabul adımıdır.
