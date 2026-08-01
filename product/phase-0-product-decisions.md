# Faz 0 - Ürün Kararları ve Kapsam Sözleşmesi

**Durum:** Tamamlandı  
**Karar tarihi:** 1 Ağustos 2026  
**Dayanak:** CampusMatch AI mevcut MVP'si ve stratejik proje raporu  
**Sonraki aşama:** Faz 1 - Veri modelini resmî ve mikro etkinlikleri destekleyecek şekilde genişletme

Bu belge, CampusMatch AI'ın mevcut etkinlik listesi MVP'sinden kart kaydırmalı,
iki katmanlı ve davranış sinyalleriyle gelişen ürün hedefine geçişte uygulanacak ürün
kararlarını sabitler. Teknik uygulama sırasında bu kararları değiştiren işler kapsam
değişikliği sayılır ve Product Owner onayı gerektirir.

## 1. Ürün Hedefi

CampusMatch AI, üniversite öğrencilerinin resmî kampüs etkinlikleriyle kısa ömürlü
öğrenci aktivitelerini tek, güvenli ve kişiselleştirilmiş kart kuyruğunda keşfetmesini
sağlar. Sistem yalnızca sıralama yapmaz; her önerinin neden gösterildiğini açıklar ve
kullanıcının davranışlarından kontrollü biçimde öğrenir.

### Başarı tanımı

Bir öğrenci:

1. Profilini oluşturur ve kalıcı olarak kaydeder.
2. Resmî ve mikro etkinliklerden oluşan kişiselleştirilmiş kart kuyruğunu görür.
3. Kartı beğenir, geçer, kaydeder veya detayını açar.
4. Davranışlarının sonraki sıralamayı ölçülebilir biçimde etkilediğini görür.
5. Uygun olduğunda mikro etkinlik oluşturur ve katıldığı etkinlikten sonra organizatörü puanlar.

## 2. Hedef Kullanıcılar

### Birincil kullanıcı

Türkiye'deki üniversitelerin ön lisans, lisans ve lisansüstü öğrencileri.

### İkincil kullanıcılar

- Öğrenci kulüpleri ve toplulukları
- Üniversite birimleri ve rektörlükler
- Belediye veya doğrulanmış profesyonel organizatörler
- Mikro etkinlik oluşturan doğrulanmış üniversite öğrencileri

Lise öğrencileri mevcut ürün kapsamından çıkarılmıştır. Üniversite dışındaki genel
etkinlik keşfi de MVP kapsamında değildir.

## 3. Ana Keşif Deneyimi Kararı

Ana keşif ekranı doğrudan kart kuyruğudur. Kullanıcıyı ayrı bir "swipe ekranına"
gönderen ara sayfa oluşturulmaz. Liste görünümü ilk MVP tamamlanana kadar geri dönüş
seçeneği olarak korunabilir ancak ana navigasyon değildir.

### Etkileşim sözleşmesi

| Kullanıcı hareketi | Olay | Anlamı |
|---|---|---|
| Sağa kaydırma | `like` | İlgileniyorum; benzer içerikler güçlenebilir |
| Sola kaydırma | `skip` | Şimdilik ilgilenmiyorum |
| Yer imi düğmesi | `save` / `unsave` | Daha sonra erişmek için kaydet veya kaldır |
| Karta dokunma | `view_detail` | Etkinlik detayını aç |
| Detaydaki katılım CTA'sı | `apply` | Katılım isteği veya başvuru oluştur |

Yukarı kaydırma MVP'de kullanılmaz. Negatif hareketin sola kaydırma olması mobil
arayüzlerdeki yerleşik beklentiyle daha uyumludur. Her olay en fazla bir kez
kaydedilmeli; ağ hatası tekrar denemelerinde çoğaltılmamalıdır.

### Kart kuyruğu kuralları

- İlk istek 20 kartı geçmez.
- Son 5 karta gelindiğinde yeni sayfa arka planda istenir.
- Aynı etkinlik aynı oturum kuyruğunda iki kez gösterilmez.
- Tükenmiş, süresi dolmuş, iptal edilmiş veya güven engeline takılmış etkinlik gösterilmez.
- Karttan ayrı klasik etkinlik detay ekranı korunur.
- Kaydedilen etkinlikler ayrı ekranda gösterilir.
- Profil ve ayarlar üst sağ profil alanında birleştirilir.

## 4. İki Katmanlı Etkinlik Kararı

Her etkinlik tam olarak bir katmana aittir:

### `official` - Resmî ve büyük etkinlik

Kulüp, üniversite birimi, belediye veya doğrulanmış şirket tarafından düzenlenir.
Yayınlanmadan önce onay durumu taşır. Konferans, konser, kariyer günü, panel,
atölye ve yarışmalar bu kapsamdadır.

### `micro` - Kullanıcı tabanlı mikro etkinlik

Doğrulanmış öğrenci tarafından oluşturulan kısa ömürlü, kampüs veya yakın çevre
odaklı aktivitedir. Spor grubu kurma, masa oyunu katılımcısı arama veya birlikte
çalışma buluşması örnekleridir.

Mikro etkinlik için zorunlu alanlar: başlangıç zamanı, sona erme zamanı, konum,
kategori, kota ve organizatör kimliği. Süresi dolan mikro etkinlik otomatik olarak
feed dışına çıkar.

## 5. Güven ve Topluluk Kontrolü

- Puan yalnızca etkinliğe katılımı doğrulanmış kullanıcı tarafından verilebilir.
- Bir kullanıcı aynı etkinlik ve organizatör için yalnızca bir puan verebilir.
- Puan 1-5 aralığındadır.
- Puanlayanın kimliği organizatöre ve genel API cevabına gösterilmez.
- İlk üç puan tamamlanmadan güven skoru cezai karar üretmez.
- En az üç puandan sonra güven ortalaması `2.0` altına düşerse organizatör yeni mikro
  etkinlik yayımlayamaz ve aktif mikro ilanları feed'den çıkarılır.
- Engel bir moderasyon kaydı oluşturur; kalıcı hesap kapatma insan incelemesi gerektirir.
- Resmî organizatörler ayrıca doğrulama ve yayın onayı taşır.

Bu kurallar MVP güven çerçevesidir. Otomatik içerik analizi, gelişmiş dolandırıcılık
tespiti ve itiraz paneli sonraki sürümdedir.

## 6. Öneri Sistemi Kararı

### MVP yaklaşımı

Üretimde açıklanabilir kural bazlı sıralama korunur. Mevcut XGBoost modeli araştırma
çıktısıdır; kural bazlı sistemi çevrim dışı metriklerde anlamlı biçimde geçmeden canlı
sıralamanın tek karar vericisi yapılmaz.

### İki aşamalı akış

1. **Aday üretimi:** Durum, zaman, kota, güven, üniversite/kampüs ve tekrar gösterim
   kurallarıyla 20-30 aday seçilir.
2. **Sıralama:** Profil uyumu, dinamik ilgi, lokasyon/zaman, güven, popülerlik ve
   kişisel davranış sinyalleri birleştirilir.

Her öneri `score`, `score_breakdown` ve en fazla üç anlaşılır `reasons` değeri döndürür.

### Dinamik ilgi ve dwell time

- Onboarding seçimleri başlangıç ilgi vektörünü oluşturur.
- `like`, `save` ve `apply` güçlü pozitif sinyaldir.
- `view_detail` ve uzun görüntüleme destekleyici pozitif sinyaldir.
- Kısa görüntüleme sonrası `skip` negatif sinyaldir.
- Beş saniye dwell eşiği başlangıç varsayımıdır; test verisiyle ayarlanır.
- Tek bir hareket profili sert biçimde değiştiremez; güncellemeler yumuşatılır ve normalize edilir.

K-Means, çalışan davranış döngüsünden sonra yalnızca mikro etkinlik aday üretimini
hızlandıran destekleyici deney olarak ele alınır.

## 7. MVP Kapsamı

### MVP içinde

- Kalıcı öğrenci profili
- Resmî ve mikro etkinlik veri modeli
- Cursor tabanlı kart kuyruğu
- Swipe ve detay etkileşimlerinin backend'e kaydı
- Kaydedilen etkinliklerin kalıcı saklanması
- Açıklanabilir kural bazlı sıralama
- Davranışla güncellenen ilgi ağırlıkları
- Mikro etkinlik oluşturma
- Katılım isteği
- Etkinlik sonrası anonim puanlama
- Temel güven engeli ve moderasyon kaydı
- Sentetik veri, API ve fiziksel cihaz demo testi

### MVP dışında

- Gerçek zamanlı mesajlaşma ve sosyal akış
- Ödeme alma
- Gelişmiş web yönetim paneli
- Production push notification altyapısı
- LLM veya embedding tabanlı öneri
- Tam otomatik içerik moderasyonu
- K-Means'in production zorunluluğu
- XGBoost'un tek başına production sıralaması
- PostgreSQL'e geçiş ve çok bölgeli dağıtım

## 8. Gizlilik ve Güvenlik İlkeleri

- Gerçek kişisel veri yerine geliştirme ve demo aşamasında sentetik veri kullanılır.
- Puan veren kullanıcının kimliği istemci cevaplarından çıkarılır.
- Ham davranış verisi yalnızca ürün ve öneri kalitesi için gereken alanları taşır.
- Kimlik doğrulama eklenene kadar uygulama production kullanıcılarına açılmaz.
- Production öncesinde CORS sınırlandırılır, hız limiti ve üniversite doğrulaması eklenir.
- Hesap/veri silme ve KVKK aydınlatma akışları production çıkış kriteridir.

## 9. API Taslak Sözleşmesi

| Yöntem | Uç | Amaç |
|---|---|---|
| `POST` | `/profiles` | Onboarding profilini kalıcılaştırır |
| `PUT` | `/profiles/{profile_id}` | Profili günceller |
| `GET` | `/feed` | Cursor ile kişiselleştirilmiş kart kuyruğu döndürür |
| `POST` | `/interactions` | Swipe, kaydetme ve detay olayını kaydeder |
| `GET` | `/profiles/{profile_id}/saved-events` | Kalıcı kaydedilenleri döndürür |
| `POST` | `/events` | Resmî veya mikro etkinlik oluşturur |
| `PUT` | `/events/{event_id}` | Yetkili organizatörün etkinliğini günceller |
| `POST` | `/events/{event_id}/apply` | Katılım isteği oluşturur |
| `POST` | `/events/{event_id}/ratings` | Katılım sonrası anonim puan kaydeder |
| `GET` | `/organizers/{organizer_id}/trust-summary` | Toplu güven bilgisini döndürür |

Kesin istek/cevap JSON şemaları Faz 1'de veri modeliyle birlikte sürümlenecektir.

## 10. Faz 0 Kabul Kriterleri

- [x] Birincil hedef kitle üniversite öğrencileri olarak sabitlendi.
- [x] Ana keşif deneyiminin swipe kart kuyruğu olduğu kararlaştırıldı.
- [x] Swipe yönleri ve olay adları belirlendi.
- [x] Resmî ve mikro etkinlik ayrımı tanımlandı.
- [x] Etkinlik detayı, kaydedilenler ve profil navigasyonu belirlendi.
- [x] Anonim puanlama ve güven eşiği kuralları belirlendi.
- [x] Aday üretimi ve ranking sorumlulukları ayrıldı.
- [x] Dinamik ilgi ve dwell time davranışı sınırlandırıldı.
- [x] MVP içi ve dışı kapsam yazıldı.
- [x] API ihtiyaçları uç seviyesinde çıkarıldı.
- [x] User story ve kullanıcı akışları güncellendi.
- [x] Backlog mevcut kodla ve yeni hedefle eşitlendi.

## 11. Değişiklik Yönetimi

Aşağıdaki kararlar Product Owner onayı olmadan değiştirilemez:

- Ana keşfin swipe kuyruğu olması
- `official` ve `micro` etkinlik ayrımı
- Sağa `like`, sola `skip` sözleşmesi
- Güven eşiğinin otomatik yayın engeli üretmesi
- Kural bazlı açıklanabilir sistemin MVP production yaklaşımı olması
- MVP kapsamına yeni büyük özellik eklenmesi

