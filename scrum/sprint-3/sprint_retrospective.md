# Sprint 3 Retrospective

## İyi Gidenler

- Fazlar birbirinin sözleşmesini genişletti; önceki veri ve API'ler yeniden yazılmadı.
- Idempotency, güven ve sahiplik kuralları endpoint yerine repository transaction'larında korundu.
- Açıklanabilir production ranking, ölçüm sonucu model değişikliğine karşı korundu.
- Her faz otomatik test, derleme ve dokümantasyon güncellemesiyle kapatıldı.

## Geliştirilecek Noktalar

- Sentetik interaction kaynağında gerçek timestamp bulunmuyor; temporal değerlendirme proxy kullanıyor.
- Fiziksel cihaz ve VoiceOver kontrolü CI ortamında otomatik değil.
- Starlette TestClient bağımlılığında deprecation uyarısı var.
- Mikro etkinlik tarih alanı MVP'de ISO metin girişidir; production öncesi native tarih seçici gerekir.

## Alınan Aksiyonlar

- Production model promotion eşiği gerçek timestamp'li veride göreli `%2` NDCG@10 olarak belirlendi.
- Fiziksel cihaz kontrolü ayrı final kabul listesine taşındı.
- Mobil route, API, offline queue ve erişilebilirlik için bağımsız sözleşme kontrolü eklendi.
- TestClient geçişi ve native tarih seçici, teslim sonrası teknik borç olarak kaydedildi.
