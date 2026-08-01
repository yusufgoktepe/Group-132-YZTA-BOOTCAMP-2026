# User Flows

## 1. İlk Giriş ve Cold Start

1. Öğrenci onboarding ekranını açar.
2. Üniversite, program ve sınıfını kontrollü listelerden seçer.
3. En az üç ilgi alanı ve en az bir katılım amacı seçer.
4. Katılım biçimi, ücret ve dil tercihlerini belirler.
5. Mobil uygulama `POST /profiles` ile profili kaydeder.
6. Dönen `profile_id` cihazda saklanır.
7. Backend onboarding ilgilerinden başlangıç ilgi vektörünü üretir.
8. Mobil uygulama `GET /feed?profile_id=...&limit=20` çağrısını yapar.
9. Backend filtrelenmiş resmî ve mikro kartları açıklanabilir skorla sıralar.
10. Ana keşif ekranı doğrudan ilk kartı gösterir.

## 2. Swipe ve Kuyruk Yenileme

1. Kart görünür olduğunda dwell time sayacı başlar.
2. Kullanıcı kartı sağa kaydırırsa `like`, sola kaydırırsa `skip` oluşur.
3. Mobil uygulama olayla birlikte `profile_id`, `event_id`, `dwell_ms` ve feed bağlamını gönderir.
4. Backend olayı idempotent biçimde kaydeder.
5. İlgi vektörü sınırlı bir öğrenme oranıyla güncellenir ve normalize edilir.
6. Kart yerel kuyruktan çıkarılır; sıradaki kart gösterilir.
7. Son beş karta gelindiğinde mobil uygulama `next_cursor` ile yeni sayfayı ister.
8. Yeni kartlar tekrar kimlik kontrolünden sonra kuyruğa eklenir.
9. Ağ hatasında olay yerel bekleme kuyruğuna alınır ve sonra tekrar gönderilir.

## 3. Detay, Kaydetme ve Katılım

1. Kullanıcı karta dokunur.
2. `view_detail` olayı kaydedilir ve klasik detay ekranı açılır.
3. Kullanıcı etkinliği `save` ile kaydedebilir veya `unsave` ile kaldırabilir.
4. Kaydedilenler backend'den ayrı ekranda listelenir.
5. Kullanıcı "Katıl/başvur" eylemini seçerse katılım kaydı oluşturulur.
6. Etkinlik tamamlandıktan sonra doğrulanmış katılımcı puanlama akışına alınabilir.

## 4. Mikro Etkinlik Oluşturma

1. Doğrulanmış öğrenci "Mikro etkinlik oluştur" akışını açar.
2. Başlık, kategori, zaman, sona erme, konum, kota ve açıklama girer.
3. Mobil uygulama istemci doğrulamasını yapar.
4. Backend kullanıcının güven ve hız limiti durumunu kontrol eder.
5. Geçerli etkinlik `micro` katmanında yayımlanır.
6. Etkinlik uygun adayların feed kuyruğuna katılır.
7. Süresi dolduğunda otomatik olarak feed dışına çıkar.

## 5. Resmî Etkinlik Oluşturma

1. Doğrulanmış organizatör etkinlik bilgilerini girer.
2. Etkinlik `official` ve onay bekleyen durumda kaydedilir.
3. Yetkili onayından sonra `published` durumuna geçer.
4. Candidate generation kurallarını sağladığında öğrenci feed'lerinde görünür.
5. Organizatör etkinliği güncelleyebilir veya iptal edebilir.

## 6. Anonim Puanlama ve Güven

1. Etkinlik tamamlanır.
2. Backend katılımı doğrulanmış kullanıcıları belirler.
3. Kullanıcı organizatöre bir defa 1-5 puan verir.
4. API puan veren kullanıcının kimliğini cevapta göstermez.
5. Güven ortalaması ve puan sayısı yeniden hesaplanır.
6. En az üç puan sonrası ortalama 2.0 altındaysa mikro etkinlik yayımlama engellenir.
7. Aktif mikro etkinlikler feed dışına çıkar ve moderasyon kaydı oluşturulur.
8. Kalıcı hesap yaptırımı insan incelemesiyle verilir.

## 7. Hata ve Boş Durumlar

- Profil oluşturulamazsa kullanıcı seçimlerini kaybetmeden tekrar deneyebilir.
- Feed boşsa filtre değişikliği ve daha sonra tekrar deneme seçenekleri gösterilir.
- Bir kart silinmiş veya iptal edilmişse kuyruktan sessizce çıkarılır.
- Etkileşim gönderilemezse kart geri gelmez; olay tekrar gönderim kuyruğunda tutulur.
- Model kullanılamazsa açıklanabilir kural bazlı sıralama kesintisiz devam eder.
