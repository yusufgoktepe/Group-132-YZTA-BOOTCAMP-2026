# Sprint 3

## Sprint Hedefi

CampusMatch AI'ı resmî eğitim referansı, iki katmanlı etkinlik kataloğu, açıklanabilir
swipe feed'i, kalıcı kullanıcı hareketleri, mikro etkinlik ve güven döngüsüyle çalışan,
test edilmiş ve jüriye sunulabilir bir son MVP hâline getirmek.

## Faz 0 Sonucu

Faz 0 ürün kararları 1 Ağustos 2026 tarihinde tamamlandı:

- Ana keşif doğrudan swipe kart kuyruğu olarak onaylandı.
- Sağa `like`, sola `skip`, düğmeyle `save`, dokunmayla `view_detail` belirlendi.
- `official` ve `micro` etkinlik katmanları tanımlandı.
- Anonim puanlama ve güven eşiği kuralları belirlendi.
- Açıklanabilir kural bazlı sistem MVP production yaklaşımı olarak korundu.
- User story, kullanıcı akışları ve product backlog güncellendi.

Ayrıntılar: [`product/phase-0-product-decisions.md`](../../product/phase-0-product-decisions.md)

## Faz 1 Sonucu

Faz 1 tamamlandı ve otomatik testlerle doğrulandı:

- Event, organizer, participation, rating, interest weight ve moderation action V3 şemaları eklendi.
- Mevcut event kayıtlarını silmeyen idempotent SQLite migration uygulandı.
- Organizer, participation, rating, interest weight ve moderation tabloları eklendi.
- V2 kaynağından 80 resmî ve 170 mikro etkinlik üretildi.
- 80 organizatör, 1.200 katılım, 800 rating ve 5.393 ilgi ağırlığı üretildi.
- 1.000 sentetik profil ile V3 organizer, etkinlik, katılım, rating ve ilgi ağırlıkları çalışan backend seed akışına bağlandı.
- Şema, ilişki, normalizasyon, migration veri koruması ve seed idempotency testleri eklendi.

## Faz 2 Sonucu

Faz 2 tamamlandı ve otomatik testlerle doğrulandı:

- Cursor tabanlı `GET /feed` endpoint'i eklendi.
- Candidate pool 30 etkinlikle sınırlandı ve yalnız seçilen adaylar sıralandı.
- Durum, zaman, sona erme, kota, üniversite, program, sınıf, doğrulama ve güven filtreleri eklendi.
- `like`, `skip` ve `apply` sonrası kartın sonraki feed'de tekrar görünmesi engellendi.
- Cursor profile bağlandı; bozuk veya başka profile ait cursor reddediliyor.
- Her feed cevabına `feed_token` eklendi.
- Interaction sözleşmesine `interaction_key`, `feed_token` ve `apply` eklendi.
- Aynı `interaction_key` ile yeniden gönderilen istekler tek kayıt üretiyor.
- Eski interaction kayıtlarını koruyan migration eklendi.
- Mobil profile, feed ve interaction API istemcileri oluşturuldu.
- Onboarding profili backend'de oluşturma/güncelleme akışına bağlandı.

## Faz 3 Sonucu

Faz 3 tamamlandı ve teknik kontrollerle doğrulandı:

- Ana keşif ekranı doğrudan swipe kart kuyruğuna dönüştürüldü.
- Sağa `like`, sola `skip`; ayrı düğmelerle geçme, kaydetme ve beğenme eklendi.
- Kart gösterim başlangıcından swipe/detail anına kadar dwell süresi ölçülüyor.
- `like`, `skip`, `save`, `unsave`, `view_detail` ve `apply` backend'e idempotent anahtarla gönderiliyor.
- Kuyruk son beş karta geldiğinde cursor ile arka plan prefetch çalışıyor.
- Feed oturumunda aynı kartın iki kez kuyruğa eklenmesi engellendi.
- Profil ve `profile_id` AsyncStorage ile cihazda saklanıyor; mevcut oturum açılışta geri yükleniyor.
- Kaydedilen etkinlik kimlikleri ve kart içerikleri cihazda saklanıyor; eski kimlikler açılışta güncel sözleşmeye taşınıyor.
- Başarısız interaction istekleri cihaz kuyruğuna eklenip sonraki bağlantıda yeniden gönderiliyor.
- Kaydedilenler ekranı backend `/saved-events` kaynağına geçirildi.
- Canlı feed kullanılamadığında açıklanabilir yerel örnek kartlara fallback korunuyor.
- Yeni mobil API çağrıları beş saniyelik ortak zaman aşımı ve kullanıcı dostu hata sözleşmesini kullanıyor.
- Feed kartları detay ekranında kullanılmak üzere uygulama context'inde kayıt altına alınıyor.

## Faz 4 Sonucu

Faz 4 tamamlandı ve otomatik testlerle doğrulandı:

- `like`, `skip`, `save`, `unsave`, `view_detail` ve `apply` hareketleri etkinliğin ilgi etiketlerine kalıcı davranış sinyali uygular.
- 2 saniyenin altındaki dwell zayıf negatif, 2–8 saniye arası nötr, 8 saniye ve üzeri pozitif sinyal olarak ele alınır.
- Davranış ağırlıkları `[-1, 1]` aralığında sınırlandırılır; birleşik ilgi vektörü profil başına tekrar 1'e normalize edilir.
- Interaction kaydı ile ilgi güncellemesi aynı transaction içindedir; idempotent retry ağırlığı ikinci kez değiştirmez.
- V3 ranking; profil uyumu, dinamik ilgi, organizatör güveni, popülerlik ve kişisel düzeltme katkılarını birleştirir.
- `score_breakdown` her katkıyı ayrı gösterir; öneri nedenleri güncel ilgi uyumunu ve yüksek organizatör güvenini açıklar.
- `GET /profiles/{profile_id}/interest-weights` ile öğrenilen vektör demo ve hata ayıklama için izlenebilir.
- Davranış sonrası ilgili başka bir etkinliğin skor değişimi kısa/uzun dwell karşılaştırmalı otomatik testle doğrulandı.

## Faz 5 Sonucu

Faz 5 tamamlandı ve otomatik testlerle doğrulandı:

- Mobil uygulamaya üçüncü bir `Oluştur` sekmesi ve mikro etkinlik formu eklendi.
- Profil, doğrulanmış öğrenci organizatörü olarak mikro etkinlik yayımlayabiliyor.
- Başlık, açıklama, kategori, ilgi, zaman, konum, katılım biçimi ve kota backend tarafından doğrulanıyor.
- Başlangıç gelecekte olmalı; zaman sırası `başlangıç < bitiş <= sona erme` olmalıdır.
- Etkinliği yalnızca oluşturan profil güncelleyebilir veya geri kazanılabilir biçimde iptal edebilir.
- Kota aktif isteklerin altına indirilemez; dolu etkinlik yeni katılım isteğini reddeder.
- Katılım isteği idempotenttir; tekrar gönderim ikinci kayıt oluşturmaz.
- Etkinlik sahibi isteği onaylayabilir, reddedebilir ve katılımı doğrulayabilir; öğrenci kendi isteğini iptal edebilir.
- Detay ekranındaki `İlgileniyorum` CTA'sı gerçek participation endpoint'ine geçirildi.
- İptal edilen, süresi dolan veya kotası dolan etkinlik feed dışında kalır.

## Faz 6 Sonucu

Faz 6 tamamlandı ve otomatik testlerle doğrulandı:

- Yalnızca `attended` ve `attendance_verified` katılımcılar 1–5 arasında puan verebilir.
- Aynı öğrenci aynı etkinliği yalnızca bir kez puanlayabilir.
- Puanlayan profil veritabanında denetim amacıyla tutulur ancak genel API cevabından çıkarılır.
- Mobil uygulamaya katılım geçmişi ve doğrulanmış etkinlikler için anonim yıldızlama ekranı eklendi.
- Organizatör güven puanı doğrulanmış rating ortalamasından güncellenir.
- İlk üç puan tamamlanmadan cezai güven eşiği uygulanmaz.
- En az üç puan ve `2.0` altı ortalamada organizatör engellenir, yeni mikro yayın reddedilir ve aktif etkinlikleri feed'den çıkar.
- Güven engeli tekil açık `publish_block` moderasyon kaydı üretir ve otomatik olarak kaldırılmaz.
- Toplu güven özeti puan sayısı, eşik durumu, yayın engeli ve açık moderasyon sayısını gösterir.
- Resmî organizatör doğrulama ve resmî etkinlik yayın onayı moderatör anahtarıyla korunur.
- Moderasyon listesi yalnızca yapılandırılmış `CAMPUSMATCH_MODERATOR_KEY` ile okunabilir.

## Faz 7 Sonucu

Faz 7 tamamlandı ve tekrarlanabilir offline deneylerle doğrulandı:

- V2 etkileşimleri `interaction_id` zaman proxy'siyle `%70/%15/%15` train/validation/test ayrıldı.
- Gerçek timestamp bulunmaması deney sınırlaması olarak açıkça kaydedildi.
- Hedef, action, dwell ve kimlik alanlarının ranking özelliklerine sızması otomatik testle engellendi.
- Kural bazlı V3 proxy, XGBoost ve validation ile seçilen hibrit aynı test bölümünde karşılaştırıldı.
- Kural bazlı NDCG@10 `0.7992`, XGBoost `0.8032`, hibrit `0.8015` ölçüldü.
- XGBoost'un göreli kazancı yaklaşık `%0.50`; hibritin `%0.29` olduğu için `%2` promotion eşiği aşılmadı.
- Açıklanabilir `rule_based_v3` production sıralayıcı olarak korundu.
- 170 mikro etkinlikte K-Means için en iyi sonuç 4 küme ve `0.2183` silhouette oldu.
- Zayıf küme ayrışması nedeniyle K-Means production candidate generation'a bağlanmadı.
- JSON model, makine-okunur metrik ve insan-okunur değerlendirme raporu üretildi.

## Faz 8 Kapsamı

1. Mobil, API, offline kuyruk ve güven akışlarını uçtan uca test etme
2. Fiziksel cihaz kabul senaryosunu çalıştırma
3. Demo verisini ve jüri anlatımını sabitleme
4. Performans, hata mesajı ve erişilebilirlik eksiklerini kapatma
5. Sprint review, retrospective ve final dokümantasyonu tamamlama

## Faz 8 Sonucu

Faz 8'in kod, otomasyon ve dokümantasyon kapsamı tamamlandı:

- Profil → feed → idempotent save retry → kaydedilenler → mikro etkinlik → katılım → attendance → anonim rating → güven engeli tek E2E testte doğrulandı.
- Öneri nedenleri Faz 0 sözleşmesine uygun biçimde en fazla üç değerle sınırlandı.
- Mobil ana aksiyonlara erişilebilirlik rolü, etiketi ve gerekli durum bilgileri eklendi.
- Mobil route, API, offline queue ve erişilebilirlik kaynak sözleşmesi otomatik kontrole bağlandı.
- Sprint review, retrospective, board, daily özet ve final kabul listesi oluşturuldu.
- 3 dakikalık jüri demosu süreli senaryo ve güvenli fallback ile güncellendi.
- Otomatik kalite kapıları tamamlandı; fiziksel iPhone kabulü dış ortam gerektirdiği için PB-28 `Ready for acceptance` durumundadır.

## Birleşik Son Ürün Sonucu

- Arkadaş ekibin Event V3 veri seti ve Faz 0–8 geliştirmeleri, mevcut SQLite ve mobil ürün akışıyla kayıpsız birleştirildi.
- 56 geriye uyumlu etkinlik ile 250 V3 etkinlik aynı API kataloğunda korunarak toplam 306 etkinliğe ulaşıldı.
- ÖSYM 2026-YKS kaynaklı 202 üniversite ve 14.281 programlık referans, V3 üniversite/program hedefleriyle uyumlu hâle getirildi.
- Eski `event-<sayı>` ve yeni etkinlik kimlikleri mobil kayıt, interaction, katılım ve rating çağrılarında tek sözleşmeye taşındı.
- Backend ve ML paketi 74 testle; mobil uygulama TypeScript, Expo lint ve sözleşme kontrolüyle doğrulandı.

Planlanan geliştirme yol haritasında Faz 8 son fazdır. Fiziksel cihaz kabul listesi
tamamlandığında Sprint 3 tamamen kapatılabilir.

## Sprint Dosyaları

Sprint ilerledikçe şu dosyalar eklenir:

- `sprint_planning.md`
- `daily_scrum_notes.md`
- `sprint_board_updates.md`
- `sprint_review.md`
- `sprint_retrospective.md`
