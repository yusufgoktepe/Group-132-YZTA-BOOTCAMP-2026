# Group 132 - YZTA Bootcamp 2026

## Takim Ismi

**Group 132**

## Takim Uyeleri

| Isim | Rol |
|---|---|
| Yusuf Goktepe | Scrum Master |
| Yusuf Oztop | Product Owner |
| Betul Tuba Gumus | Developer |
| Gulsen Eymen Dediler | Developer |
| Cemal Faruk Tugrul | Developer |

---

## Urun Bilgisi

### Urun Ismi

**CampusMatch AI**

### Urun Aciklamasi

CampusMatch AI, ogrencilerin ilgi alanlarina, bolumlerine, hedeflerine ve tercihlerine gore kendilerine uygun kulup ve etkinlikleri kesfetmesini saglayan yapay zeka destekli mobil bir platformdur.

Platformun temel amaci, ogrenci ile dogru etkinligi daha hizli ve daha anlamli sekilde bulusturmaktir. Ayni zamanda kulup ve topluluklarin da etkinliklerini daha dogru ogrenci kitlesine ulastirabilmesine yardimci olur.

### Problem

- Ogrenciler etkinlik ve kulup duyurularini daginik kanallardan takip ediyor.
- Ilgi alanina uygun firsatlari kacirmak kolaylasiyor.
- Kulup yoneticileri hedef kitlelerine dogru sekilde ulasmakta zorlanabiliyor.

### Cozum

- Ogrenci profili ve ilgi alanlarina dayali etkinlik onerileri
- Aciklanabilir oneriler: "Bu etkinlik neden onerildi?"
- Mobil-first deneyim
- Ileride gelistirilebilir AI tabanli recommendation yapisi

### Hedef Kitle

- Universite ogrencileri
- Lise ogrencileri
- Kulup ve topluluklara katilmak isteyen ogrenciler
- Etkinlik duzenleyen ogrenci topluluklari
- Kulup yoneticileri

### Kullanilacak Teknolojiler

| Alan | Teknoloji |
|---|---|
| Mobil Uygulama | React Native / Expo |
| Backend | FastAPI |
| Veri Tabani | SQLite / PostgreSQL |
| AI / Data Science | Python, pandas, scikit-learn |
| Proje Yonetimi | GitHub Projects, GitHub Issues |

---

## MVP Kapsami

Ilk hedef, ogrencinin profil bilgilerini girip kendisine uygun etkinlik onerilerini gorebildigi bir MVP olusturmaktir.

MVP icindeki temel akis:

1. Ogrenci profilini olusturur.
2. Ilgi alanlarini ve tercihlerini belirtir.
3. Sistem sentetik veri ve skor bazli mantikla oneriler uretir.
4. Ogrenci kendisine onerilen etkinlikleri gorur.
5. Oneri nedeni kullaniciya aciklanir.

---

## Sprint 1 Ozeti

### Sprint Tarihi

**19 Haziran 2026 - 5 Temmuz 2026**

### Sprint Amaci

Sprint 1'de amac, urun fikrini netlestirmek, takim ici gorev dagilimini yapmak, proje yonetim yapisini kurmak ve Sprint 2 gelistirmesine temel olacak teknik ve urunsel cerceveyi olusturmaktir.

### Sprint 1 Boyunca Odaklanilan Basliklar

- Urun vizyonunun netlestirilmesi
- Hedef kitlenin belirlenmesi
- Ogrenci ve kulup yoneticisi kullanici akislarinin cikarilmasi
- Product backlog yapisinin olusturulmasi
- Veri semasi ve sentetik veri mantiginin planlanmasi
- Aciklanabilir recommendation yaklasiminin belirlenmesi
- Mobil ekran ve backend ihtiyaclarinin tanimlanmasi

### Sprint 1 Ciktilari

- README ve temel repo dokumantasyonu hazirlandi.
- Product vision, target audience, user stories ve user flows dokumanlari olusturuldu.
- Product backlog'un ilk versiyonu cikarildi.
- Veri semasi ve ornek veri yapisi planlandi.
- Recommendation sistemi icin skor bazli bir baseline mantik olusturuldu.
- FastAPI tarafinda temel backend iskeleti baslatildi.

### Sprint 1 Sonunda Projenin Durumu

Sprint 1 sonunda proje, planlama ve temel mimari kararlarini tamamlamis; Sprint 2'de kod gelistirmesine gecmeye hazir bir duruma gelmistir.

---

## Sprint 2 Icin Hazir Olan Alanlar

- Mobil ekran gelistirmesine uygun urun akislar
- Backend endpoint planlamasi
- Sentetik veri ve sema temeli
- Recommendation mantigi icin ilk prototip

Sprint 2'de odak, bu planlari calisan urun parcaciklarina donusturmek olacaktir.

---

## Repo Yapisi

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

### Klasor Aciklamalari

- `backend/`: FastAPI tabanli API iskeleti
- `mobile/`: React Native / Expo tarafinin planlama ve gelistirme alani
- `ml/`: Recommendation mantigi ve AI yaklasimi
- `data/`: Veri semasi ve ornek sentetik veri
- `product/`: Product vision, user story, user flow ve backlog dokumanlari
- `scrum/`: Sprint planning, review, retrospective ve scrum notlari
- `docs/`: Teknik kararlar ve destekleyici dokumantasyon

---

## Onemli Dokumanlar

- [Product Vision](./product/product_vision.md)
- [Product Backlog](./product/product_backlog.md)
- [User Stories](./product/user_stories.md)
- [User Flows](./product/user_flows.md)
- [Tech Stack](./docs/tech_stack.md)
- [Backend README](./backend/README.md)
- [Sprint 1 Planning](./scrum/sprint-1/sprint_planning.md)
- [Sprint 1 Review](./scrum/sprint-1/sprint_review.md)
- [Sprint 1 Retrospective](./scrum/sprint-1/sprint_retrospective.md)

---

## Product Backlog

GitHub Projects board linki eklendiginde bu bolum guncellenecektir.

---

## Not

Bu repo Sprint 1 sonunda urunsel planlama, veri kurgusu ve teknik temel olusturma asamasini belgelemektedir. Sprint 2 ile birlikte mobil, backend ve AI katmanlarinda daha fazla pratik gelistirme yapilacaktir.
