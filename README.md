# Group 132 - YZTA Bootcamp 2026

## CampusMatch AI

CampusMatch AI, öğrencilerin ilgi alanlarına, bölümlerine, hedeflerine ve tercihlerine göre kendilerine uygun kulüp ve etkinlikleri keşfetmesini sağlayan yapay zeka destekli mobil platform fikridir.

Bu README, jüri değerlendirmesi için proje hakkında gerekli olan ürün, sprint ve teknik bilgileri tek dosyada toplamak amacıyla hazırlanmıştır.

## Takım ve Roller

| İsim | Rol |
|---|---|
| Yusuf Göktepe | Scrum Master |
| Yusuf Öztop | Product Owner |
| Betül Tuba Gümüş | Developer |
| Gülşen Eymen Dediler | Developer |
| Cemal Faruk Tuğrul | Developer |

## Kısa Özet

- Problem: Öğrenciler uygun etkinlik ve kulüp fırsatlarını dağınık kanallarda kaçırabiliyor.
- Çözüm: Öğrenci profiline göre kişiselleştirilmiş ve açıklanabilir etkinlik önerileri sunmak.
- Hedef: Öğrenci ile doğru etkinliği daha hızlı buluşturmak, kulüplerin de doğru hedef kitleye ulaşmasını kolaylaştırmak.
- Platform yaklaşımı: Mobil-first.
- İlk AI özelliği: Skor bazlı ve açıklanabilir öneri sistemi.

## Ürün Vizyonu

**Doğru öğrenci, doğru kulüp ve doğru etkinlikle daha hızlı buluşsun.**

<details>
<summary><strong>Problem ve Çözüm</strong></summary>

### Problem

Öğrenciler kulüp ve etkinlik duyurularını çoğu zaman dağınık kanallardan takip eder. Bu durum, ilgi alanlarına ve hedeflerine uygun fırsatların kaçmasına neden olabilir.

Kulüpler ise etkinliklerini duyururken doğru hedef kitleye ulaşmakta zorlanabilir. Duyurular geniş kitlelere ulaşsa bile gerçekten ilgilenebilecek öğrencilerle kişiselleştirilmiş bir eşleşme çoğu zaman kurulamaz.

### Çözüm

CampusMatch AI; öğrenci profili, kulüp bilgileri ve etkinlik özelliklerini kullanarak kişiselleştirilmiş öneriler üretir. İlk aşamada skor bazlı ve açıklanabilir bir öneri sistemiyle ilerlenmesi planlanmıştır.
</details>

<details>
<summary><strong>Hedef Kitle</strong></summary>

### Birincil Hedef Kitle

- Üniversite öğrencileri
- Lise öğrencileri
- Kulüp ve topluluklara katılmak isteyen öğrenciler
- Kariyer, sosyal gelişim, teknik beceri veya topluluk deneyimi kazanmak isteyen öğrenciler

### İkincil Hedef Kitle

- Üniversite kulüpleri
- Lise toplulukları
- Etkinlik düzenleyen öğrenci organizasyonları
- Katılımcı kitlesini daha doğru belirlemek isteyen kulüp ekipleri

### Öncelik Dağılımı

- Öğrenci tarafı: 6/10
- Kulüp yöneticisi tarafı: 4/10

Ürün, öğrenci deneyimini ana vitrin olarak konumlandırır; ancak kulüp yöneticisi tarafı da final üründe anlamlı ve kullanılabilir bir panel olarak yer almalıdır.
</details>

<details>
<summary><strong>Temel Özellikler</strong></summary>

- Öğrenci profili oluşturma
- İlgi alanı ve hedef bazlı etkinlik önerileri
- Etkinlik detaylarını görüntüleme
- Etkinlik kaydetme
- Kulüp yöneticisi için etkinlik oluşturma
- Kulüp ve etkinlik yönetim mantığı
- Yapay zeka destekli öneri sistemi
- “Bu etkinlik neden önerildi?” açıklama mantığı

</details>

## MVP Kapsamı

İlk hedef, öğrencinin profil bilgilerini girip kendisine uygun etkinlik önerilerini görebildiği bir MVP oluşturmaktır.

1. Öğrenci profilini oluşturur.
2. İlgi alanlarını ve tercihlerini girer.
3. Sistem öğrenciye uygun kulüp ve etkinlikleri listeler.
4. Öğrenci etkinlik detayını inceler.
5. Sistem önerinin neden yapıldığını açıklar.

## Kullanıcı Hikayeleri ve Akışlar

<details>
<summary><strong>Öğrenci Tarafı</strong></summary>

### Öncelikli Kullanıcı Hikayeleri

- Bir öğrenci olarak profil oluşturmak istiyorum.
- Bir öğrenci olarak ilgi alanlarımı seçmek istiyorum.
- Bir öğrenci olarak bana önerilen etkinlikleri görmek istiyorum.
- Bir öğrenci olarak etkinlik detaylarını görüntülemek istiyorum.
- Bir öğrenci olarak etkinlikleri kaydetmek istiyorum.
- Bir öğrenci olarak önerinin neden yapıldığını görmek istiyorum.

### Öğrenci Akışı

1. Öğrenci uygulamaya girer.
2. Profil bilgilerini doldurur.
3. İlgi alanlarını ve hedeflerini seçer.
4. Sistem öğrenciye uygun kulüp ve etkinlikleri listeler.
5. Öğrenci etkinlik detayını inceler.
6. Öğrenci etkinliği kaydeder veya katılım isteği oluşturur.

</details>

<details>
<summary><strong>Kulüp Yöneticisi Tarafı</strong></summary>

### Öncelikli Kullanıcı Hikayeleri

- Bir kulüp yöneticisi olarak kulüp profili oluşturmak istiyorum.
- Bir kulüp yöneticisi olarak etkinlik oluşturmak istiyorum.
- Bir kulüp yöneticisi olarak etkinliğime ilgi gösteren öğrencileri görmek istiyorum.
- Bir kulüp yöneticisi olarak AI’dan hedef kitle önerisi almak istiyorum.

### Kulüp Yöneticisi Akışı

1. Kulüp yöneticisi uygulamaya veya panele girer.
2. Kulüp profilini oluşturur.
3. Etkinlik bilgilerini girer.
4. Hedef kitle etiketlerini belirler.
5. Etkinliği yayınlar.
6. Etkinliğe ilgi gösteren öğrencileri takip eder.

</details>

## Teknoloji Yığını

| Alan | Teknoloji |
|---|---|
| Mobil Uygulama | React Native / Expo |
| Backend | FastAPI |
| Veri Tabanı | SQLite / PostgreSQL |
| AI / Data Science | Python, pandas, scikit-learn |
| Proje Yönetimi | GitHub Projects, GitHub Issues |

<details>
<summary><strong>Neden Bu Teknolojiler?</strong></summary>

- React Native / Expo: Mobil-first ürün için hızlı prototipleme sağlar.
- FastAPI: Python tabanlı AI/ML entegrasyonu için uygundur.
- SQLite: İlk geliştirme aşamasında hızlı başlangıç sağlar.
- PostgreSQL: Proje büyüdüğünde daha güçlü veritabanı seçeneğidir.
- scikit-learn: İlk öneri sistemi prototipi için sade ve anlaşılır modelleme sunar.

</details>

## Sprint 1 Özeti

**Sprint Tarihi:** 19 Haziran 2026 - 5 Temmuz 2026  
**Sprint Amacı:** Ürün fikrini netleştirmek, takım içi görev dağılımını yapmak, veri ve AI yaklaşımını planlamak, proje yönetim düzenini kurmak ve Sprint 2 geliştirmesine temel olacak teknik çerçeveyi hazırlamak.

<details open>
<summary><strong>Sprint 1 Planlama ve Backlog</strong></summary>

| ID | Görev | Sorumlu Alan | Durum |
|---|---|---|---|
| S1-01 | README başlangıç dokümantasyonunun hazırlanması | Scrum / Dokümantasyon | Done |
| S1-02 | Product vision dokümanının hazırlanması | Product | Done |
| S1-03 | Hedef kitle ve user story dokümanlarının hazırlanması | Product / Takım | Done |
| S1-04 | Öğrenci kullanıcı akışının çıkarılması | Product / Developer Team | Done |
| S1-05 | Kulüp yöneticisi kullanıcı akışının çıkarılması | Product / Developer Team | Done |
| S1-06 | Sentetik veri şemasının planlanması | AI / Data Science | Done |
| S1-07 | Öneri sistemi kriterlerinin belirlenmesi | AI / Data Science | Done |
| S1-08 | Mobil uygulama ekran ihtiyaçlarının belirlenmesi | Mobile Team | Done |
| S1-09 | Backend API ihtiyaçlarının çıkarılması | Backend Team | Done |
| S1-10 | Recommendation baseline mantığının yazılması | AI / Backend | Done |

</details>

<details>
<summary><strong>Sprint 1 Boyunca Yapılanlar</strong></summary>

- Ürün vizyonu netleştirildi.
- Hedef kitle belirlendi.
- Öğrenci ve kulüp yöneticisi kullanıcı hikayeleri çıkarıldı.
- Temel kullanıcı akışları dokümante edildi.
- Product backlog’un ilk sürümü hazırlandı.
- Veri şeması ve örnek veri yapısı planlandı.
- Recommendation sistemi için skor bazlı ilk yaklaşım belirlendi.
- FastAPI tarafında temel backend iskeleti başlatıldı.

</details>

<details>
<summary><strong>Sprint 1 Sonunda Alınan Kararlar</strong></summary>

- Ürün mobil-first olarak ilerleyecek.
- Öğrenci deneyimi ana odak olacak.
- Kulüp yöneticisi tarafı da final ürünün önemli bir parçası olacak.
- İlk AI özelliği recommendation sistemi olacak.
- Başlangıçta sentetik veri ile ilerlenilecek.
- Sprint 2’de daha fazla kod, ekran ve entegrasyon çalışması yapılacak.

</details>

<details>
<summary><strong>Sprint 1 Retrospective</strong></summary>

### İyi Gidenler

- Proje fikri ekip içinde ortak bir noktaya getirildi.
- Öğrenci ve kulüp taraflarını birlikte ele alan net bir ürün yönü belirlendi.
- Mobil-first yaklaşım üzerinde hızlı şekilde uzlaşıldı.
- AI tarafında ilk aşama için sade ve açıklanabilir bir öneri yaklaşımı seçildi.

### Geliştirilebilecek Noktalar

- Görev sahipliği daha erken ve daha net belirlenmeli.
- GitHub Projects daha aktif kullanılmalı.
- Daily scrum notları daha düzenli tutulmalı.
- Sprint kapanışına bırakılan işler daha erken yayılmalı.

### Sprint 2 İçin Aksiyonlar

- GitHub Projects board aktif şekilde güncellenecek.
- Sprint görevleri issue olarak açılacak ve atanacak.
- Mobil ekran wireframe’leri netleştirilecek.
- Backend endpoint’leri kod seviyesinde genişletilecek.
- Recommendation akışı örnek veri ile test edilecek.

</details>

## Product Backlog Özeti

| ID | İş / User Story | Durum |
|---|---|---|
| PB-01 | Ürün fikrinin netleştirilmesi | Done |
| PB-02 | Hedef kitlenin belirlenmesi | Done |
| PB-03 | Teknoloji setinin belirlenmesi | Done |
| PB-04 | Öğrenci kullanıcı akışının çıkarılması | In Progress |
| PB-05 | Kulüp yöneticisi kullanıcı akışının çıkarılması | In Progress |
| PB-06 | Sentetik veri yapısının planlanması | In Progress |
| PB-07 | Öneri sistemi kriterlerinin belirlenmesi | In Progress |
| PB-08 | Mobil ekran taslaklarının hazırlanması | To Do |
| PB-09 | Backend API ihtiyaçlarının çıkarılması | To Do |
| PB-10 | İlk öneri sistemi prototipinin hazırlanması | To Do |
| PB-11 | Öğrenci profil ekranının geliştirilmesi | To Do |
| PB-12 | Etkinlik önerileri ekranının geliştirilmesi | To Do |
| PB-13 | Kulüp yöneticisi etkinlik oluşturma ekranının geliştirilmesi | To Do |

## Sonraki Adımlar

- Mobil ekranların geliştirilmesi
- Backend endpoint’lerinin genişletilmesi
- Sentetik veri ile recommendation akışının test edilmesi
- Öğrenci tarafı MVP’nin çalışır hale getirilmesi
- Kulüp yöneticisi tarafının temel seviyede eklenmesi

## Repo Yapısı

```text
.
|-- assets/
|-- backend/
|-- data/
|-- docs/
|-- ml/
|-- mobile/
|-- product/
|-- scrum/
```

## Son Not

Bu README, jüri değerlendirmesi için gerekli ürün, sprint ve teknik bilgileri sade ama yeterli bir yapıda tek yerde toplamak amacıyla hazırlanmıştır.
