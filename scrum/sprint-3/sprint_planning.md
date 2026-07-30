# CampusMatch AI - Sprint 3 Bitirme Planı

## 1. Sprint Kimliği

| Alan | Açıklama |
|---|---|
| Sprint | Sprint 3 - Ürün Tamamlama ve Final Teslim |
| Başlangıç | 22 Temmuz 2026 |
| Süre | 10 çalışma günü; bootcamp final tarihine göre takvime uyarlanabilir |
| Sprint amacı | Öğrenci MVP'sini kalıcı veri, gerçek backend akışı, interaction kaydı, öneri modeli, test ve jüri dokümantasyonuyla tamamlamak |
| Ana kullanıcı | Türkiye'deki üniversite öğrencisi |
| Başarı ölçütü | Temiz kurulumdan sonra onboarding → profil → öneri → detay → kaydet/like akışının kesintisiz çalışması |

## 2. Sprint Sonunda Teslim Edilecek Ürün

Sprint sonunda aşağıdaki senaryo tek telefonda ve canlı backend ile gösterilebilmelidir:

1. Öğrenci uygulamayı açar.
2. Üniversitesini, programını ve sınıfını kontrollü listelerden seçer.
3. İlgi alanlarını ve etkinlik tercihlerini tamamlar.
4. Profil backend'e kaydedilir ve uygulama yeniden açıldığında korunur.
5. Backend gerçek etkinlik verisini döndürür.
6. Öneri sistemi profil ve interaction sinyallerini kullanarak etkinlikleri sıralar.
7. Öğrenci önerinin nedenini görür.
8. Öğrenci etkinliği sağa/sola kaydırır, detayını açar veya kaydeder.
9. Interaction backend'e yazılır ve kaydedilen etkinlikler tekrar görüntülenir.
10. Backend kapalıysa kullanıcı açık bir uyarıyla yerel demo akışına dönebilir.

## 3. Bootcamp ve Jüri Teslim İhtiyaçları

Proje boyunca kabul edilen değerlendirme ihtiyaçlarına göre final paketi şunları içermelidir:

- Çalışan ve tekrar kurulabilir mobil MVP
- Yapay zekâ/öneri özelliğinin ürün içinde görünür kullanımı
- Kullanılan veri, özellikler, model yaklaşımı ve metriklerin açıklanması
- Sprint 1, Sprint 2 ve Sprint 3 plan/review/retrospective bilgilerinin kök README'de bulunması
- Güncel product backlog ve tamamlanan görevlerin kanıtlanması
- Uygulama ekran görüntüleri ve kısa demo senaryosu
- GitHub commit/branch geçmişinde ekip katkılarının görünmesi
- Kurulum ve çalıştırma komutlarının doğrulanması
- Sentetik veri kullanımı ve kişisel veri yaklaşımının açıklanması
- Bilinen kısıtlar ve sonraki geliştirmelerin dürüstçe belirtilmesi

## 4. Kapsam Kararı

### Mutlaka Tamamlanacaklar - P0

- Kalıcı profil ve kaydedilen etkinlik verisi
- Gerçek mobil → backend profil ve etkinlik akışı
- `like`, `skip`, `save`, `view_detail` interaction kaydı
- Açıklanabilir öneri endpoint'i
- V2 veriyle model değerlendirmesi ve güvenli fallback
- Üniversite/program referans verisinin sürümlü ve aranabilir hâle gelmesi
- Yükleniyor, boş durum ve bağlantı hatası ekranları
- Uçtan uca test, README, demo ve final sunum kanıtları

### Tamamlanması Beklenenler - P1

- Kart kaydırma deneyimi
- Temel kulüp yöneticisi etkinlik oluşturma akışı
- Paylaşılabilir Expo/EAS preview build
- Basit profil düzenleme ve çıkış/sıfırlama işlemi

### Zaman Kalırsa - P2

- Gelişmiş filtreler ve arama
- Kulüp doğrulama rozeti
- Basit yönetici etkinlik listesi
- Öneri geri bildirimi: “Bunu neden gördüm?” detayları

### Bu Sprintte Yapılmayacaklar

- Production seviyesinde kimlik doğrulama ve yetkilendirme
- Ödeme sistemi
- Push notification altyapısı
- Gelişmiş admin analitiği
- LLM/embedding tabanlı yeni öneri mimarisi
- App Store / Play Store production yayını
- Sosyal mesajlaşma veya takip sistemi

Bu sınırlar final MVP'nin tamamlanmasını korumak için kapsam dondurma kuralıdır.

## 5. Önerilen Ekip Dağılımı

Bu dağılım öneridir; ekip ilk gün teyit edebilir. Her görevin tek sahibi bulunmalı, destekçi sorumluluğu devralmamalıdır.

| Kişi | Ana Sorumluluk | Sprint 3 Çıktısı |
|---|---|---|
| Yusuf Göktepe | Scrum Master, mobil-backend entegrasyonu, release koordinasyonu | Günlük takip, entegrasyon branch'i, canlı API bağlantısı, final build |
| Yusuf Öztop | Product Owner, kabul testleri, dokümantasyon ve demo | Kapsam kararı, acceptance kontrolü, README, demo metni ve jüri akışı |
| Betül Tuba Gümüş | Mobil uygulama ve UI/UX | Swipe, loading/error durumları, kaydedilenler, profil düzenleme |
| Gülşen Eymen Dediler | Backend, API ve veritabanı | SQLite modelleri, CRUD endpoint'leri, interaction ve kalıcı kayıt |
| Cemal Faruk Tuğrul | AI, veri ve model değerlendirme | YÖK referans verisi, V2 model eğitimi, metrikler, model servis adaptörü |

### Destek Eşleşmeleri

| Ana İş | Sahip | Destekçi |
|---|---|---|
| Mobil-backend API sözleşmesi | Yusuf Göktepe | Gülşen Eymen Dediler |
| Swipe ve interaction akışı | Betül Tuba Gümüş | Yusuf Göktepe |
| Model servisleme | Cemal Faruk Tuğrul | Gülşen Eymen Dediler |
| Kabul testleri | Yusuf Öztop | Tüm ekip |
| README ve demo kanıtları | Yusuf Öztop | Yusuf Göktepe |

## 6. Sprint 3 Backlog

Efor değerleri göreli tahmindir: `S` küçük, `M` orta, `L` büyük. Saat karşılığı değildir.

| ID | Öncelik | Görev | Sahip | Efor | Bağımlılık | Durum |
|---|---|---|---|---|---|---|
| S3-00 | P0 | MVP kapsamını ve swipe kararını dondurmak | Yusuf Öztop | S | Yok | To Do |
| S3-01 | P0 | GitHub Issues ve Sprint 3 board'unu açmak | Yusuf Göktepe | S | S3-00 | To Do |
| S3-02 | P0 | Profil, etkinlik, kulüp, kayıt ve interaction DB tabloları | Gülşen | L | S3-00 | To Do |
| S3-03 | P0 | DB başlatma ve örnek veriyi yükleme komutu | Gülşen | M | S3-02 | To Do |
| S3-04 | P0 | Profil oluşturma/güncelleme/getirme endpoint'leri | Gülşen | M | S3-02 | To Do |
| S3-05 | P0 | Etkinlik ve kulüp endpoint'lerini DB'ye bağlamak | Gülşen | M | S3-02 | To Do |
| S3-06 | P0 | `POST /interactions` endpoint'i | Gülşen | M | S3-02 | To Do |
| S3-07 | P0 | Kaydedilen/beğenilen etkinlik endpoint'leri | Gülşen | M | S3-06 | To Do |
| S3-08 | P0 | Mobil profilin backend'e kalıcı kaydı | Yusuf Göktepe | M | S3-04 | To Do |
| S3-09 | P0 | Mobil etkinlikleri gerçek API'den almak | Yusuf Göktepe | M | S3-05 | To Do |
| S3-10 | P1 | Swipe kartı ve like/skip hareketleri | Betül | L | S3-00 | To Do |
| S3-11 | P0 | Save/view_detail/like/skip olaylarını API'ye göndermek | Betül | M | S3-06, S3-10 | To Do |
| S3-12 | P0 | Kaydedilenler ekranını backend verisine bağlamak | Betül | M | S3-07 | To Do |
| S3-13 | P0 | Loading, hata, boş durum ve retry bileşenleri | Betül | M | S3-09 | To Do |
| S3-14 | P0 | Tam üniversite listesini sürümlü referans veriye aktarmak | Cemal | L | Resmî kaynak | To Do |
| S3-15 | P0 | Üniversiteye bağlı program listesini normalize etmek | Cemal | L | S3-14 | To Do |
| S3-16 | P0 | V2 dataset kalite ve dağılım analizini yapmak | Cemal | M | Yok | To Do |
| S3-17 | P0 | V2 modelini eğitmek ve metrikleri kaydetmek | Cemal | L | S3-16 | To Do |
| S3-18 | P0 | Model tahminini FastAPI'ye bağlamak ve fallback korumak | Cemal | M | S3-17, S3-05 | To Do |
| S3-19 | P1 | Temel kulüp etkinlik oluşturma formu | Betül | L | S3-05 | To Do |
| S3-20 | P0 | Uçtan uca iPhone test senaryosu | Yusuf Öztop | M | S3-08–S3-18 | To Do |
| S3-21 | P0 | Backend endpoint ve hata testleri | Gülşen | M | S3-04–S3-07 | To Do |
| S3-22 | P0 | Model metrikleri ve açıklanabilirlik raporu | Cemal | S | S3-17 | To Do |
| S3-23 | P0 | Sprint 3 README, review ve retrospective | Yusuf Öztop | M | Tüm işler | To Do |
| S3-24 | P0 | Demo videosu/senaryosu ve jüri prova akışı | Yusuf Öztop | M | S3-20 | To Do |
| S3-25 | P1 | Expo/EAS paylaşılabilir preview build | Yusuf Göktepe | M | S3-20 | To Do |

## 7. Görevlerin Ayrıntılı Kabul Kriterleri

### 7.1 Veritabanı ve Backend

- Uygulama yeniden başlatıldığında profil ve kayıtlar kaybolmamalı.
- DB ilk kurulum komutu README'de bulunmalı.
- Endpoint'ler uygun `2xx`, `4xx` ve anlaşılır hata gövdeleri döndürmeli.
- API modelleri Profil V2 ve Etkinlik V2 sözleşmeleriyle uyumlu olmalı.
- Mobil uygulama demo öğrenci `1/2` eşlemesine ihtiyaç duymamalı.
- Interaction kaydında `student_id`, `event_id`, `action`, `timestamp` ve uygun olduğunda `dwell_time` bulunmalı.
- Aynı etkinliğin tekrar kaydedilmesi çoğaltılmış kayıt oluşturmamalı.

### 7.2 Mobil Uygulama

- Onboarding yalnızca ilk girişte gösterilmeli veya kullanıcı tarafından sıfırlanabilmeli.
- Profil verisi backend'den yüklenebilmeli ve düzenlenebilmeli.
- Etkinlik listesi mock dosyadan değil API'den gelmeli; fallback yalnızca hata durumunda kullanılmalı.
- Kullanıcı backend kaynağının canlı/yerel olduğunu görebilmeli.
- Swipe seçilirse sağa kaydırma `like`, sola kaydırma `skip` üretmeli.
- Butonla kullanım swipe hareketine alternatif olarak korunmalı.
- Kaydetme durumu keşif, detay ve Kaydedilenler ekranında tutarlı olmalı.
- iPhone 11 ekranında taşma, kesilme veya erişilemeyen buton olmamalı.

### 7.3 Üniversite ve Program Referansı

- Üniversite serbest metin olmamalı.
- Üniversite listesi aranabilir olmalı.
- Programlar yalnızca seçilen üniversiteye göre gösterilmeli.
- Sınıf seçenekleri program süresinden üretilmeli.
- Referans veri `reference_version`, kaynak ve güncelleme tarihi içermeli.
- Eksik üniversite/program için serbest giriş yerine bildirim mekanizması bulunmalı.
- Kaynak erişimi veya lisans problemi çıkarsa D3 sonunda Product Owner'a kapsam riski bildirilmeli.

### 7.4 AI ve Öneri Sistemi

- Eğitim ve test verisi ayrılmalı; veri sızıntısı oluşturan kolonlar modele verilmemeli.
- En az accuracy, precision, recall, F1 ve ROC-AUC raporlanmalı.
- Baseline ile V2 model sonucu karşılaştırılmalı.
- Model dosyası mobil uygulamaya gömülmemeli.
- Tahmin başarısız olursa açıklanabilir kural/skor fallback'i çalışmalı.
- Her öneri skorla birlikte en az bir insan tarafından anlaşılır neden döndürmeli.
- Kullanılan sentetik kurallar README'de açıklanmalı; gerçek kullanıcı verisi izlenimi verilmemeli.

### 7.5 Dokümantasyon ve Jüri

- Kök README tek başına proje vizyonunu, kurulumunu ve üç sprinti anlatmalı.
- Sprint 3 backlog, review, retrospective ve final durumları README'ye aktarılmalı.
- Final ekran görüntüleri gerçek çalışan uygulamadan alınmalı.
- Bilinen eksikler gizlenmemeli; “tamamlandı”, “kısmi”, “planlandı” ayrımı korunmalı.
- Demo en fazla 3–5 dakikada ana değeri göstermeli.
- Her ekip üyesi kendi katkısını ve teknik kararını açıklayabilmeli.

## 8. 10 Günlük Timeline

| Gün | Ortak Hedef | Paralel Çalışmalar | Gün Sonu Çıktısı |
|---|---|---|---|
| D1 | Kapsam ve API sözleşmesi dondurma | Board/issues, DB şeması, model hedefi, mobil ekran listesi | Onaylı kapsam ve sözleşme |
| D2 | Kalıcı veri temeli | DB modelleri, üniversite veri aktarımı, swipe prototipi | DB ve referans veri ilk sürümü |
| D3 | Temel endpoint'ler | Profil/events API, program normalizasyonu, mobil hata bileşenleri | Çalışan profil ve etkinlik API'si |
| D4 | Interaction akışı | Interaction endpoint, swipe UI, V2 veri analizi | Like/skip/save kayıt zinciri |
| D5 | İlk entegrasyon | Mobil gerçek API, model eğitimi, kaydedilenler | Uçtan uca akışın ilk sürümü |
| D6 | Öneri entegrasyonu | Model servisleme, fallback, profil düzenleme | Canlı kişiselleştirilmiş öneri |
| D7 | Feature freeze | Kulüp formu P1, hata düzeltme, API testleri | Yeni özellik ekleme kapanır |
| D8 | QA ve performans | iPhone testleri, edge case, veri/model kontrolü | Kritik hata listesi kapanır |
| D9 | Jüri hazırlığı | README, ekran görüntüsü, demo videosu, sunum | Teslim adayı sürüm |
| D10 | Buffer ve release | Temiz kurulum testi, son prova, tag/build | Final sürüm ve teslim paketi |

### Sprint Kontrol Noktaları

- D1 sonu: Kapsam kilidi
- D3 sonu: Üniversite/program veri riski kararı
- D5 sonu: İlk uçtan uca demo
- D7 sonu: Feature freeze
- D8 sonu: Code freeze
- D10: Final release

## 9. Bağımlılıklar ve Bekleme Yönetimi

| Bekleyen İş | Bağımlılık | Beklemeden İlerleme Yöntemi |
|---|---|---|
| Mobil profil kaydı | Profil API | Profil V2 sözleşmesine uygun mock response |
| Mobil etkinlik listesi | Event API/DB | Aynı response yapısındaki mevcut mock etkinlikler |
| Swipe interaction | Interaction API | Lokal queue ve console/mock adapter |
| Model endpoint'i | V2 model | Mevcut açıklanabilir skor fallback'i |
| Program seçimi | Tam referans veri | Aynı veri yapısındaki pilot üniversite listesi |
| Demo build | Entegrasyon | Expo Go ile ara demo |

Kimse bağımlılık nedeniyle boşta beklememeli; API sözleşmesi sabitse mock/fake response ile ilerlemelidir.

## 10. Git ve Çalışma Düzeni

- `main` her zaman çalışır durumda tutulmalı.
- Her issue için ayrı branch kullanılmalı.
- Önerilen branch'ler: `feature/swipe`, `backend/persistence`, `ai/v2-model`, `data/yok-reference`, `docs/sprint3-final`.
- Branch'ler kısa ömürlü olmalı; günlük veya görev bittiğinde PR açılmalı.
- En az bir ekip üyesi PR kontrolü yapmalı.
- Büyük dataset ve model değişiklikleri açıklamasız commit edilmemeli.
- Force push yapılmamalı.
- Her gün entegrasyon branch'i yerine doğrudan küçük ve doğrulanmış PR'larla `main` güncel tutulmalı.
- D7 sonrası yeni özellik PR'ı açılmamalı; yalnızca bugfix, test ve dokümantasyon kabul edilmeli.

## 11. Daily Scrum Şablonu

Her gün 10–15 dakikalık toplantıda herkes şu dört bilgiyi verir:

1. Dün hangi çıktıyı tamamladım?
2. Bugün hangi issue üzerinde çalışacağım?
3. Beni engelleyen bağımlılık veya karar var mı?
4. Görevim D5/D7 kontrol noktasını riske atıyor mu?

Toplantı sonunda yalnızca engeller, sahipleri ve çözüm tarihleri kaydedilir.

## 12. Definition of Done

Bir görev ancak aşağıdakilerin tamamı sağlandığında `Done` kabul edilir:

- Kabul kriteri karşılandı.
- Kod ilgili branch'te ve PR üzerinden birleştirildi.
- TypeScript/lint veya Python testleri geçti.
- Hata ve boş durumlar kontrol edildi.
- Fiziksel cihaz veya API üzerinden davranış doğrulandı.
- Gerekli dokümantasyon güncellendi.
- Başka bir ekip üyesi sonucu gözden geçirdi.
- Kullanıcıya veya jüriye gösterilebilecek somut çıktı oluştu.

## 13. Test Matrisi

| Test Alanı | Kontrol |
|---|---|
| Temiz kurulum | Yeni clone sonrası backend ve mobil komutları çalışıyor mu? |
| Profil | Oluşturma, düzenleme, yeniden açma ve eksik alan doğrulaması |
| Referans veri | Üniversite arama, program filtreleme, sınıf süresi |
| Keşif | Loading, canlı veri, fallback, filtre ve boş sonuç |
| Etkinlik | Detay, kaydetme, tekrar kaydetme, kayıt kaldırma |
| Swipe | Like/skip olayı bir kez ve doğru event ID ile gidiyor mu? |
| Öneri | Farklı iki profil farklı sıralama üretiyor mu? |
| Backend | Başarılı, bulunamadı, doğrulama hatası ve bağlantı hatası |
| Model | Metrikler, feature sırası, fallback ve açıklama |
| Cihaz | iPhone 11, Expo Go, aynı Wi-Fi ve tunnel senaryosu |

## 14. Demo Senaryosu

1. Problem cümlesi: Öğrenciler uygun kampüs etkinliklerini dağınık kanallarda kaçırıyor.
2. Onboarding ve kontrollü üniversite/program seçimi gösterilir.
3. İki farklı ilgi/amaç tercihi seçilir.
4. Canlı öneri göstergesi ve değişen sıralama gösterilir.
5. Bir kart sağa kaydırılır veya beğenilir.
6. Etkinlik detayında öneri nedeni açıklanır.
7. Etkinlik kaydedilir ve Kaydedilenler ekranında gösterilir.
8. Backend'deki interaction kaydı veya API çıktısı kısa biçimde gösterilir.
9. Model yaklaşımı, sentetik veri ve metrikler tek slaytta anlatılır.
10. Bilinen kısıtlar ve sonraki adım dürüstçe paylaşılır.

## 15. Riskler ve Önlemler

| Risk | Etki | Önlem |
|---|---|---|
| Tam YÖK/program verisinin zamanında alınamaması | Profil seçimi eksik kalır | D3 karar kapısı, sürümlü importer, pilot veri fallback'i |
| Mobil-backend response uyuşmazlığı | Entegrasyon kırılır | D1 sözleşme kilidi ve ortak örnek JSON |
| Modelin V2 veride beklenenden düşük kalması | AI demosu zayıflar | Baseline karşılaştırması ve açıklanabilir fallback |
| Aynı dosyada paralel değişiklik | Merge conflict | Dosya/iş sahipliği ve küçük PR'lar |
| Final gününe özellik kalması | Demo riski | D7 feature freeze, D8 code freeze |
| Yerel IP değişmesi | Telefon API'ye bağlanamaz | `.env.local`, kısa bağlantı kontrol listesi, tunnel alternatifi |
| Büyük kapsam | Ana akış tamamlanamaz | P0 dışındaki işleri ilk kesilecek işler olarak tutmak |

## 16. Final Teslim Kontrol Listesi

### Ürün

- [ ] Onboarding çalışıyor.
- [ ] Profil backend'de kalıcı.
- [ ] Üniversite/program/sınıf kontrollü.
- [ ] Etkinlikler gerçek API'den geliyor.
- [ ] Öneri skoru ve nedeni görünür.
- [ ] Like/skip/save/view interaction kaydediliyor.
- [ ] Kaydedilenler kalıcı.
- [ ] Hata ve fallback durumları görünür.

### Teknik

- [ ] `main` temiz ve çalışır.
- [ ] Kurulum komutları temiz clone üzerinde test edildi.
- [ ] Backend testleri geçti.
- [ ] TypeScript ve Expo lint geçti.
- [ ] Model metrikleri kaydedildi.
- [ ] Secret, kişisel IP ve `.env.local` commit edilmedi.
- [ ] Dataset ve model kaynakları açıklandı.

### Scrum ve Jüri

- [ ] GitHub board güncel.
- [ ] Sprint 3 backlog durumları kapatıldı.
- [ ] Sprint review yazıldı.
- [ ] Sprint retrospective yazıldı.
- [ ] Kök README üç sprinti içeriyor.
- [ ] Final ekran görüntüleri eklendi.
- [ ] Demo videosu veya canlı demo akışı hazır.
- [ ] Tüm ekip en az bir prova yaptı.
- [ ] Release tag veya final commit oluşturuldu.

## 17. Product Owner İçin Kesme Sırası

Sprint riske girerse işler aşağıdaki sırayla kapsamdan çıkarılır:

1. Gelişmiş filtreler
2. Kulüp doğrulama rozeti
3. Yönetici etkinlik listesi
4. EAS preview build; Expo Go demo korunur
5. Kulüp yöneticisi formu

Kalıcı profil, gerçek etkinlik API'si, interaction kaydı, açıklanabilir öneri, test ve jüri dokümantasyonu kapsamdan çıkarılamaz.
