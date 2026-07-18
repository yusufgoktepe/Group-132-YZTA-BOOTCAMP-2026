# CampusMatch Mobil Kurulum

## Uygulamayı çalıştırma

```powershell
cd mobile
npm install
npx expo start
```

Expo Go ile QR kodu tarayın. Telefon ve bilgisayarın aynı Wi-Fi ağında olması gerekir.

## Backend bağlantısı

Fiziksel iPhone, bilgisayarın `localhost` adresine erişemez. `mobile/.env` dosyasında
bilgisayarın yerel ağ IP adresini kullanın:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
```

Adresi değiştirdikten sonra Expo sunucusunu yeniden başlatın. Backend kapalıysa mobil
uygulama otomatik olarak yerel mock önerileri kullanır.
