# CampusMatch AI - Devralan Codex Ajanı İçin Çalışma Kılavuzu

Bu dosya, CampusMatch AI projesini devralan ajanın ürün bağlamını, çalışma kurallarını ve güncel önceliklerini anlaması için hazırlanmıştır. Çalışmaya başlamadan önce bu dosyayı ve `README.md` dosyasını oku.

## 1. Proje Özeti

CampusMatch AI, öğrencilerin ilgi alanları, bölümleri, hedefleri ve tercihleri doğrultusunda uygun kulüp ve etkinlikleri keşfetmesini sağlayacak yapay zeka destekli, mobil öncelikli bir platformdur.

Temel değer önerisi:

> Doğru öğrenci, doğru kulüp ve doğru etkinlikle daha hızlı buluşsun.

Ürün iki kullanıcı grubuna hizmet eder:

- Öğrenciler: Kendilerine uygun etkinlikleri keşfeder, detaylarını görür ve kaydeder.
- Kulüp yöneticileri: Kulüp profili oluşturur ve etkinlik yayımlar.

## 2. Ürün ve MVP Kararları

İlk çalışan sürümün ana odağı öğrenci tarafıdır. Kulüp yöneticisi tarafı önemlidir ancak öğrenci MVP'si tamamlanmadan kapsamı büyütme.

İlk MVP akışı:

1. Öğrenci profilini oluşturur.
2. İlgi alanlarını, hedeflerini ve tercihlerini girer.
3. Sistem, sentetik veri ve skor bazlı recommendation mantığıyla etkinlik önerir.
4. Öğrenci önerileri ve etkinlik detaylarını görür.
5. Sistem, önerinin neden yapıldığını açıklar.
6. Öğrenci ilgilendiği etkinliği kaydeder veya katılım isteği oluşturur.

Önemli ürün ilkeleri:

- Mobil-first ilerle.
- Recommendation sistemi ilk AI özelliği olmalıdır.
- İlk aşamada açıklanabilir, kural/skor bazlı öneri sistemi yeterlidir; gereksiz model karmaşıklığı ekleme.
- Gerçek kullanıcı verisi yerine sentetik veri kullan.
- Öğrenci deneyimi önceliklidir; kulüp yöneticisi tarafını ikinci aşamada genişlet.

## 3. UI / UX Yönü

Öğrenci keşif deneyimi için kart kaydırmalı (sağa/sola swipe) yapı takım tarafından değerlendirilmiştir. Bu fikir uygulanırsa:

- Swipe yalnızca öğrenci etkinlik keşfi için kullanılmalıdır.
- Ana keşif ekranı doğrudan swipe kartları olabilir; ayrı bir "swipe'a git" ekranı oluşturma.
- Etkinlik detay sayfası klasik detay ekranı olarak kalmalıdır.
- Kaydedilen/beğenilen etkinlikler için ayrı bir ekran olmalıdır.
- Profil ve ayarlar, alt menüde ayrı birincil öğeler yerine üst sağ profil alanında birleştirilebilir.
- Kulüp yöneticisi tarafı klasik form/panel yapısında kalmalıdır.

Bu karar henüz kesin uygulama emri değildir. Uygulamaya başlamadan önce kullanıcıdan veya Product Owner'dan teyit al. Onaylanmadıysa mevcut öneri listesi yaklaşımını koru.

## 4. Teknik Yön

Planlanan teknoloji yığını:

| Alan | Teknoloji |
|---|---|
| Mobil | React Native / Expo |
| Backend | FastAPI |
| Veri tabanı | Başlangıçta SQLite, ileride PostgreSQL |
| AI / Veri | Python, pandas, scikit-learn |
| Yönetim | GitHub Projects ve GitHub Issues |

Mevcut teknik başlangıç noktaları:

- `backend/app/main.py`: FastAPI iskeleti ve `GET /health` endpoint'i vardır.
- `ml/recommender_baseline.py`: Açıklanabilir, skor bazlı recommendation baseline'ı vardır.
- `data/`: Veri şeması ve örnek sentetik veri içerir.
- `mobile/`: Mobil uygulama planlama alanıdır; uygulama geliştirmesi Sprint 2 odaklarındandır.

Planlanan temel API'ler:

- `GET /health`
- `GET /students`
- `GET /clubs`
- `GET /events`
- `POST /recommendations/student/{student_id}`

Swipe yaklaşımı onaylanırsa ayrıca şu ihtiyaçları planla:

- Öğrenci-etkinlik interaction kaydı (`like`, `skip`, `save`, `view_detail`).
- `POST /interactions/swipe`
- `GET /students/{student_id}/liked-events`

## 5. Sprint Durumu ve Sonraki Öncelikler

Sprint 1 tamamlanmıştır. Sprint 1'in çıktıları:

- Ürün vizyonu, hedef kitle ve user story'ler belirlendi.
- Öğrenci ve kulüp yöneticisi akışları çıkarıldı.
- Product backlog'un ilk sürümü hazırlandı.
- Sentetik veri şeması ve recommendation kriterleri belirlendi.
- FastAPI temel iskeleti ile recommendation baseline'ı başlatıldı.
- Jüri için gerekli ürün ve sprint bilgileri `README.md` içinde birleştirildi.

Sprint 2'nin hedefi planları çalışan MVP parçalarına dönüştürmektir. Öncelik sırası:

1. Ürün backlog'unu ve ekran/API sözleşmesini netleştirme.
2. Mobil proje iskeleti, navigation, onboarding ve profil ekranı.
3. Öğrenci etkinlik önerileri ve etkinlik detay ekranı.
4. Backend'de öğrenciler, kulüpler, etkinlikler ve recommendation endpointleri.
5. Sentetik veriyle recommendation entegrasyonu ve açıklama metni.
6. Kaydedilen etkinlikler ve temel kulüp yöneticisi etkinlik oluşturma akışı.
7. Test, demo akışı ve dokümantasyon güncellemesi.

## 6. Ekip Çalışma Modeli

Takım 5 kişidir. Bu dağılım kesin kişi ataması değil, iş sahipliği modelidir:

| Alan | Ana Sorumluluk |
|---|---|
| Proje yönetimi / Product | Backlog, sprint planı, user flow, öncelik, ekip koordinasyonu, demo senaryosu |
| Mobil geliştirme 1 | Expo yapısı, navigation, onboarding, profil ekranı, ortak bileşenler |
| Mobil geliştirme 2 + entegrasyon | Öneriler, etkinlik detayları, kaydedilenler, backend bağlantısı, UI iyileştirmeleri |
| Backend / API | FastAPI, endpointler, veri modelleri, response sözleşmeleri |
| AI / veri + dokümantasyon | Sentetik veri, scoring, açıklanabilir öneri, test verileri, README/sprint desteği |

Çalışma ilkeleri:

- Her işin tek bir sahibi olsun.
- Gerektiğinde bir destekçi belirle, ancak sorumluluk belirsizleşmesin.
- İnsanların birbirini beklemesini azaltmak için mock data veya fake API response kullan.
- Mobil ekip backend tamamlanmadan ekranları mock veriyle geliştirebilir.
- Backend ekip AI tamamlanmadan geçici recommendation response dönebilir.
- AI/veri ekip mobil tamamlanmadan scoring ve veri testlerini yapabilir.
- Haftanın başında görev ve öncelik, ortasında kısa ilerleme kontrolü, sonunda entegrasyon ve eksik kontrolü yap.

## 7. Dokümantasyon ve Jüri Kuralları

- Jüri değerlendirmesi için gereken ürün ve Sprint 1 bilgileri tek `README.md` içinde tutulur.
- README Türkçe karakterleri desteklemeli ve okunabilir kalmalıdır.
- Uzun içerikleri sade tut; gerektiğinde `<details>` ve `<summary>` etiketleriyle açılır-kapanır bölümler kullan.
- `product/` ve `scrum/` klasörlerindeki eski belgeleri kullanıcı açıkça istemedikçe silme veya geri alma. README bunların jüri özeti olarak kullanılmalıdır.
- Yeni kararlar veya Sprint 2 ilerlemesi olduğunda README'deki "Sonraki Adımlar" ve ilgili özet alanlarını güncelle.
- Dokümantasyon değişikliklerini abartma; çalışan MVP'ye doğrudan katkısı olmayan tekrarlar ekleme.

## 8. Git ve Değişiklik Yönetimi

- Mevcut ana branch `main`dir. `main`i stabil tut.
- Yeni özellik veya dokümantasyon değişikliği için mümkünse ayrı branch aç:
  - `feature/<kısa-açıklama>`
  - `backend/<kısa-açıklama>`
  - `docs/<kısa-açıklama>`
  - `fix/<kısa-açıklama>`
- Küçük ve anlamlı commit'ler oluştur. Örnek: `docs: update jury README`, `feat: add event recommendations endpoint`.
- Push reddedilirse zorla push yapma. Önce uzak değişiklikleri güvenli şekilde al, çakışmaları çöz, sonra push et.
- Rebase sırasında çakışma varsa conflict işaretlerini (`<<<<<<<`, `=======`, `>>>>>>>`) dosyada bırakma. Çözümden sonra `git add <dosya>` ve `git rebase --continue` kullan.
- Kullanıcının veya başka ekip üyesinin yaptığı değişiklikleri geri alma, silme veya ezme.
- Çalışma ağacında kullanıcıya ait olabilecek takip edilmemiş dosyalar varsa, kullanıcı açıkça istemedikçe bunları silme veya commit'e ekleme.

## 9. Kod ve Uygulama Kuralları

- Önce mevcut kodu ve ilgili dokümanı oku; varsayımla büyük değişiklik yapma.
- MVP'yi küçük tut. Authentication, gelişmiş admin paneli, gerçek production veritabanı, embedding/LLM gibi ileri özellikleri temel akış çalışmadan ekleme.
- API response şekilleri mobil ve backend tarafından erken kararlaştırılmalı.
- Recommendation çıktısı en azından skor, etkinlik bilgisi ve açıklama nedenlerini içermeli.
- Örnek ve test verileri, öneri mantığını görünür kılacak kadar çeşitli olmalı.
- Mobilde backend hazır değilse aynı response sözleşmesine uygun mock data kullan.
- Her teknik değişiklikten sonra uygun doğrulama yap: backend için endpoint testi, recommendation için örnek veri testi, mobil için ekran/akış kontrolü.

## 10. İletişim Biçimi

- Kullanıcı Türkçe iletişim kuruyor; yanıtları Türkçe ve anlaşılır tut.
- Teknik terim gerektiğinde kısa açıklama ekle.
- Önce sonuç ve öneriyi ver, sonra gerekli teknik ayrıntıya in.
- Büyük kararlar, kapsam değişiklikleri veya geri döndürülemez işlemler öncesinde kullanıcıyla teyit et.
- Küçük, güvenli ve açıkça istenen değişikliklerde ilerlemek için gereksiz onay bekleme.

## 11. Başlangıç Kontrol Listesi

Yeni bir ajan çalışmaya başlarken:

1. `AGENTS.md` ve `README.md` dosyalarını oku.
2. `git status` ile mevcut çalışma ağacını kontrol et.
3. İlgili alanın kodunu ve dokümanlarını incele.
4. Görevin Sprint 2 öncelikleriyle uyumunu doğrula.
5. Gerekirse küçük, test edilebilir bir iş parçası belirle ve uygula.
6. Kullanıcıdan istenmeyen dosyaları silme, commit'leme veya geri alma.
