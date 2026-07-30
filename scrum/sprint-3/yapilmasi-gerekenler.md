# Sprint 3 - Yapılması Gerekenler

Bu sprintin amacı CampusMatch AI projesini çalışan, test edilmiş ve jüriye sunulabilir bir MVP hâline getirmektir.

## 1. Mobil Uygulama

- [x] Profil bilgilerinin kalıcı olarak saklanması
- [x] Etkinliklerin backend üzerinden alınması
- [x] Etkinlik detay ekranının tamamlanması
- [x] Etkinlik kaydetme ve kayıttan çıkarma işlemlerinin çalışması
- [ ] Beğenme tamamlandı; geçme/swipe işleminin eklenmesi
- [x] Kaydedilen etkinliklerin uygulama yeniden açıldığında korunması
- [ ] Yükleniyor, bağlantı hatası ve boş sonuç ekranlarının hazırlanması
- [x] Profil düzenleme özelliğinin tamamlanması
- [ ] Uygulamanın fiziksel telefonda kontrol edilmesi

## 2. Backend ve Veritabanı

- [x] SQLite veritabanının kurulması
- [x] Kullanıcı profillerinin veritabanına kaydedilmesi
- [x] Kulüp ve etkinlik verilerinin veritabanına aktarılması
- [x] Beğenme, geçme, kaydetme ve detay görüntüleme hareketlerinin kaydedilmesi
- [x] Etkinlik, profil ve öneri endpoint'lerinin tamamlanması
- [x] Hatalı ve eksik istekler için anlaşılır cevaplar hazırlanması
- [x] Backend testlerinin yazılması ve çalıştırılması

## 3. Etkinlik ve Referans Verileri

- [x] Demo için geniş etkinlik ve kulüp havuzunun hazırlanması
- [x] Etkinliklerin farklı kategorilere dengeli dağıtılması
- [x] Mobil ve backend kataloglarının aynı etkinlik kimliklerini kullanması
- [ ] Türkiye'deki üniversitelerin güncel referans listesinin hazırlanması
- [ ] Üniversitelere bağlı programların düzenlenmesi
- [ ] Program süresine uygun sınıf seçeneklerinin gösterilmesi
- [ ] Veri kaynağı ve güncelleme tarihinin belirtilmesi

## 4. Öneri Sistemi

- [x] Profil bilgilerinin öneri sistemine doğru gönderilmesi
- [x] Etkinliklerin kullanıcıya uygunluğa göre sıralanması
- [x] Her öneri için eşleşme puanı gösterilmesi
- [x] Her önerinin neden gösterildiğinin açıklanması
- [x] Yeni model ile mevcut baseline sonucunun karşılaştırılması
- [x] Model çalışmadığında temel skor sisteminin devreye girmesi
- [x] Model metriklerinin kaydedilmesi

## 5. Entegrasyon ve Test

- [x] Mobil uygulama ile backend bağlantısının teknik olarak doğrulanması
- [ ] Profil oluşturma → öneri → detay → kaydetme akışının kontrol edilmesi
- [x] Farklı profillerin farklı öneriler almasının doğrulanması
- [x] İnternet veya backend bağlantısı olmadığında yedek akışın çalışması
- [x] TypeScript, Expo lint ve Python testlerinin hatasız tamamlanması
- [ ] Temiz kurulumdan sonra projenin tekrar çalıştırılması
- [x] Tespit edilen kritik kalıcılık hatalarının kapatılması

## 6. Dokümantasyon ve Jüri Hazırlığı

- [x] Ana README'nin son ürün durumuna göre güncellenmesi
- [ ] Sprint 3 backlog durumlarının işaretlenmesi
- [ ] Sprint Review bölümünün yazılması
- [ ] Sprint Retrospective bölümünün yazılması
- [ ] Güncel uygulama ekran görüntülerinin eklenmesi
- [x] Kurulum ve çalıştırma komutlarının kontrol edilmesi
- [x] Kullanılan sentetik verilerin açıklanması
- [x] Bilinen eksiklerin ve sonraki adımların belirtilmesi
- [ ] 3-5 dakikalık demo senaryosunun hazırlanması
- [ ] Final sunum provasının yapılması

## Önerilen Çalışma Sırası

1. Veritabanı ve API yapısını tamamla.
2. Mobil uygulamayı gerçek backend verisine bağla.
3. Kullanıcı hareketlerini kalıcı hâle getir.
4. Öneri sistemini ve açıklama metinlerini doğrula.
5. Uçtan uca testleri gerçekleştir.
6. Kritik hataları düzelt ve yeni özellik eklemeyi durdur.
7. README, ekran görüntüleri ve demo hazırlığını tamamla.

## Projenin Bitmiş Sayılması İçin

- Kullanıcı profilini oluşturabilmeli.
- Profil bilgileri uygulama kapandığında kaybolmamalı.
- Kullanıcı yeterli sayıda kişiselleştirilmiş etkinlik görebilmeli.
- Etkinlik detayları açılabilmeli ve etkinlik kaydedilebilmeli.
- Kullanıcı hareketleri backend tarafından kaydedilebilmeli.
- Öneri puanı ve öneri nedeni görünür olmalı.
- Uygulama fiziksel telefonda sorunsuz çalışmalı.
- Kurulum, test ve demo adımları README'de anlaşılır olmalı.
