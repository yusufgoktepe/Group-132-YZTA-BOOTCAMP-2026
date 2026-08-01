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
aynı idempotency anahtarıyla yeniden gönderilir.

Keşif ekranı canlı `GET /feed` cevabını kart kuyruğuna dönüştürür. Son beş kartta
cursor prefetch yapılır. Canlı API kullanılamadığında yerel açıklanabilir örnekler
gösterilir. Kaydedilenler ekranının ana veri kaynağı backend'dir.

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
```
