# User Stories

Bu hikâyelerde `P0` çalışan swipe MVP'si, `P1` mikro etkinlik ve güven kapsamı,
`P2` ise deney/production hazırlığıdır.

## Öğrenci Profili ve Keşif

| ID | Öncelik | User story | Kabul özeti |
|---|---|---|---|
| US-01 | P0 | Bir öğrenci olarak kontrollü alanlarla profil oluşturmak istiyorum. | Profil backend'de kalıcı kimlik alır. |
| US-02 | P0 | Bir öğrenci olarak resmî ve mikro etkinlikleri tek kart kuyruğunda görmek istiyorum. | Feed uygun, aktif ve güvenli kartları cursor ile döndürür. |
| US-03 | P0 | Bir öğrenci olarak kartı sağa kaydırarak ilgimi belirtmek istiyorum. | Tek `like` olayı dwell süresiyle kaydedilir. |
| US-04 | P0 | Bir öğrenci olarak ilgilenmediğim kartı sola kaydırmak istiyorum. | Tek `skip` olayı kaydedilir ve sıralama sinyaline dönüşür. |
| US-05 | P0 | Bir öğrenci olarak etkinlik detayını görmek istiyorum. | `view_detail` olayı kaydedilir; klasik detay ekranı açılır. |
| US-06 | P0 | Bir öğrenci olarak etkinliği kaydetmek istiyorum. | Save/unsave backend'de kalıcıdır ve ayrı ekranda görünür. |
| US-07 | P0 | Bir öğrenci olarak neden bu kartı gördüğümü bilmek istiyorum. | Kart en fazla üç anlaşılır neden ve skor gösterir. |
| US-08 | P0 | Bir öğrenci olarak kuyruk biterken kesinti yaşamamak istiyorum. | Son beş kartta sonraki sayfa arka planda yüklenir. |
| US-09 | P0 | Bir öğrenci olarak internet kesildiğinde akışın bozulmamasını istiyorum. | Bekleyen olaylar tekrar gönderilir; mevcut kartlar kullanılabilir kalır. |

## Katılım, Mikro Etkinlik ve Güven

| ID | Öncelik | User story | Kabul özeti |
|---|---|---|---|
| US-10 | P1 | Bir öğrenci olarak mikro etkinlik oluşturmak istiyorum. | Zaman, konum, kategori, kota ve sona erme alanları zorunludur. |
| US-11 | P1 | Bir öğrenci olarak bir etkinliğe katılım isteği göndermek istiyorum. | Katılım kaydı çift gönderimde çoğalmaz. |
| US-12 | P1 | Bir katılımcı olarak etkinlik sonrası organizatörü anonim puanlamak istiyorum. | Yalnız doğrulanmış katılımcı bir kez 1-5 puan verir. |
| US-13 | P1 | Bir öğrenci olarak düşük güvenli organizatörlerin ilanlarından korunmak istiyorum. | Eşik altındaki organizatörün mikro ilanı feed'e girmez. |
| US-14 | P1 | Bir kullanıcı olarak uygunsuz mikro etkinliği bildirmek istiyorum. | Bildirim moderasyon kaydı oluşturur. |

## Kurumsal Organizatör

| ID | Öncelik | User story | Kabul özeti |
|---|---|---|---|
| US-15 | P1 | Bir doğrulanmış organizatör olarak resmî etkinlik oluşturmak istiyorum. | Etkinlik onay durumu taşır ve yayınlanmadan görünmez. |
| US-16 | P1 | Bir organizatör olarak etkinliğimi güncellemek veya iptal etmek istiyorum. | Yalnız yetkili organizatör değişiklik yapar. |
| US-17 | P2 | Bir organizatör olarak toplu ilgi ve katılım sayılarını görmek istiyorum. | Kişisel öğrenci verisi açığa çıkmadan özet gösterilir. |

## Öneri ve Veri Bilimi

| ID | Öncelik | User story | Kabul özeti |
|---|---|---|---|
| US-18 | P0 | Bir ürün ekibi olarak davranışların ilgi vektörünü kontrollü güncellemesini istiyorum. | Tek olay profili sert değiştirmez; ağırlıklar normalize edilir. |
| US-19 | P0 | Bir ürün ekibi olarak öneri skorunu açıklayabilmek istiyorum. | Cevap score breakdown ve nedenler içerir. |
| US-20 | P2 | Bir veri ekibi olarak ML modelini kural bazlı sistemle karşılaştırmak istiyorum. | Aynı test setinde ranking metrikleri raporlanır. |
| US-21 | P2 | Bir sistem olarak model çalışmadığında öneri sunmaya devam etmek istiyorum. | Kural bazlı fallback otomatik çalışır. |
