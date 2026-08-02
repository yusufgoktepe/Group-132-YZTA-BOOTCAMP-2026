# CampusMatch Mobil Uygulaması

React Native, Expo Router ve TypeScript tabanlı mobil MVP çalışır durumdadır.

## Mevcut ekranlar

- Onboarding ve kontrollü Profil V2 oluşturma
- Kişiselleştirilmiş etkinlik keşfi
- Etkinlik detayı ve açıklanabilir öneri nedenleri
- Kaydedilen etkinlikler
- Profil düzenleme
- Ana keşifte sağa/sola swipe kart kuyruğu
- Mikro etkinlik oluşturma formu
- Katılım geçmişi ve anonim organizatör puanlama ekranı

## Faz 2 API sözleşmeleri

Mobil servis katmanında:

- `profiles-api.ts`: `POST /profiles` ve `PUT /profiles/{profile_id}`
- `feed-api.ts`: cursor tabanlı `GET /feed`
- `interactions-api.ts`: idempotent swipe/detay/kaydetme olayları
- `recommendations-api.ts`: mevcut liste ekranının canlı öneri fallback'i
- `events-api.ts`: mikro etkinlik yayınlama ve kalıcı katılım isteği

Onboarding tamamlandığında profil backend'de kalıcılaştırılır. Profil ve `profileId`
AsyncStorage üzerinde saklanır; uygulama yeniden açıldığında oturum geri yüklenir.
Başarısız interaction istekleri aynı storage içinde kuyruğa alınır ve sonraki bağlantıda
aynı idempotency anahtarıyla yeniden gönderilir. Kaydedilen kartların kimlikleri ve
görüntülenebilir içerikleri de cihazda tutulur; backend geçici olarak kapalıyken liste
boşalmaz. Tüm yeni API isteklerinde beş saniyelik zaman aşımı ve anlaşılır hata mesajı
kullanılır.

Keşif ekranı canlı `GET /feed` cevabını kart kuyruğuna dönüştürür. Son beş kartta
cursor prefetch yapılır. Canlı API kullanılamadığında yerel açıklanabilir örnekler
gösterilir. Kaydedilenler ekranının ana veri kaynağı backend'dir.

Profil ekranındaki üniversite ve program seçimi, ÖSYM 2026-YKS Tablo 3/4 verilerinden
üretilen 202 üniversite ve 14.281 programlık resmî referansı kullanır. Serbest metin
yerine kontrollü seçim yapılır; sınıf seçenekleri program süresine göre oluşturulur.

Faz 5 ile `Oluştur` sekmesinden kota ve sona erme bilgili mikro etkinlik yayımlanır.
Etkinlik detayındaki katılım CTA'sı kalıcı ve idempotent participation isteği oluşturur.
Katılım organizatör tarafından doğrulandığında `Katılımlar` sekmesinde 1–5 yıldızlı
anonim puanlama açılır; daha önce puanlanan etkinlik yeniden puanlanamaz.

## Çalıştırma

```powershell
Copy-Item .env.example .env
npm.cmd install
npm.cmd run start
```

Fiziksel telefonda `EXPO_PUBLIC_API_URL` için bilgisayarın yerel ağ IP adresi
kullanılmalıdır.

## Doğrulama

```powershell
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run verify:contracts
npx.cmd expo export --platform web
npx.cmd expo export --platform ios
```
