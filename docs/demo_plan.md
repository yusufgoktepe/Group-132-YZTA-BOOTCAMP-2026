# Demo Plan

## Demo Amacı

Ürünün öğrenci ile kulüp/etkinlikleri yapay zeka destekli şekilde eşleştirdiğini kısa ve anlaşılır biçimde göstermek.

## Hedef Demo Akışı

1. Öğrenci uygulamaya giriş yapar.
2. Profil ve ilgi alanlarını seçer.
3. Sistem resmî ve mikro etkinliklerden oluşan kişiselleştirilmiş kart kuyruğunu açar.
4. Öğrenci bir kartı beğenir, bir kartı geçer ve bir etkinliğin detayını açar.
5. Öğrenci öneri nedenini ve davranış sonrası sıralama değişimini görür.
6. Öğrenci bir etkinliği kaydeder ve kaydedilenler ekranında tekrar bulur.
7. Doğrulanmış öğrenci kısa ömürlü mikro etkinlik oluşturur.
8. Etkinlik sonrası katılımcı organizatöre anonim puan verir.
9. Güven eşiği altındaki organizatörün mikro ilanının engellendiği gösterilir.
10. Kısa ürün özeti ve sonraki ML deneyleri anlatılır.

## 3 Dakikalık Jüri Akışı

| Süre | Gösterim | Beklenen kanıt |
|---:|---|---|
| 0:00–0:20 | Problem ve değer önerisi | Dağınık etkinlikler, açıklanabilir kişiselleştirme |
| 0:20–0:45 | Profil ve ilgi seçimi | Kontrollü üniversite/program/ilgi sözleşmesi |
| 0:45–1:20 | Swipe feed | Resmî + mikro kart, neden, like/skip/save |
| 1:20–1:40 | Detay ve kaydedilenler | Kalıcı kayıt ve katılım isteği |
| 1:40–2:10 | Mikro etkinlik oluşturma | Zaman, konum, kota ve sahiplik doğrulaması |
| 2:10–2:35 | Katılım ve anonim rating | Doğrulanmış katılım, kimliği gizli yıldızlama |
| 2:35–2:50 | Güven engeli | Üç düşük puan sonrası feed/yayın engeli ve moderasyon |
| 2:50–3:00 | ML sonucu | XGBoost kazancı eşik altında; açıklanabilir V3 korunuyor |

## Demo Öncesi Hazırlık

1. Backend'i yerel ağda `0.0.0.0:8000` üzerinde başlat.
2. Mobil `.env` içindeki `EXPO_PUBLIC_API_URL` değerini bilgisayarın LAN IP'sine ayarla.
3. `CAMPUSMATCH_MODERATOR_KEY` değerini yalnız demo bilgisayarında tanımla.
4. Expo Go önbelleğini temizleyerek uygulamayı aç.
5. Demo profili ve en az üç katılımcı profilinin hazır olduğunu kontrol et.
6. İnternet/LAN kesintisi için yerel fallback ve offline interaction senaryosunu prova et.
7. [`final_acceptance_checklist.md`](../scrum/sprint-3/final_acceptance_checklist.md) cihaz maddelerini işaretle.

## Güvenli Fallback

- Backend erişilemezse keşif yerel açıklanabilir kartları gösterir.
- Interaction gönderilemezse aynı idempotency anahtarıyla cihaz kuyruğunda tutulur.
- Demo moderasyon anahtarı videoda veya ekran görüntüsünde gösterilmez.
- Canlı akış bozulursa önceden alınmış ekran görüntüleri yalnız yedek anlatım için kullanılır.

## Final Video Notu

Bootcamp tesliminde 3 dakikalık proje videosu hazırlanacaktır.
