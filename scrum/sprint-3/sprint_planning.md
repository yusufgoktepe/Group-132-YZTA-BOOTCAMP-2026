# Sprint 3 Planning

**Başlangıç:** 1 Ağustos 2026  
**Sprint hedefi:** Faz 0 kararlarını tamamlamak ve Faz 1'de iki katmanlı etkinlik
veri modeline geçiş için uygulanabilir teknik iş sırasını hazırlamak.

## Sprint Kapsamı

### Tamamlanan Faz 0 işleri

| İş | Sorumlu alan | Durum | Doğrulama |
|---|---|---|---|
| Ürün hedefi ve hedef kitleyi sabitleme | Product | Done | Vizyon ve hedef kitle belgeleri güncel |
| Swipe hareket sözleşmesi | Product / Mobil | Done | Sağa like, sola skip, düğmeyle save |
| Resmî ve mikro etkinlik ayrımı | Product / Backend | Done | İki katman ve yaşam döngüsü tanımlı |
| Güven ve anonim rating kuralları | Product / Backend | Done | Eşik, asgari örnek ve moderasyon akışı tanımlı |
| Öneri sistemi MVP kararı | AI / Backend | Done | Açıklanabilir kural tabanı ve ML sınırı tanımlı |
| User story ve kullanıcı akışları | Product | Done | Kimlikli ve kabul özetli hikâyeler hazır |
| Product backlog eşitlemesi | Product / Scrum | Done | PB-01-PB-28 sıralaması hazır |

### Faz 1'e alınan işler

| Backlog | İş | Ana sahiplik | Bağımlılık | Çıkış koşulu |
|---|---|---|---|---|
| PB-06 | Event V3 ve ilişkili JSON şemaları | Backend / Veri | Faz 0 kararları | Done - tüm örnekler doğrulandı |
| PB-07 | SQLite migration ve seed | Backend | PB-06 | Done - veri koruma ve idempotency test edildi |
| PB-08 | V2 veriyi V3'e dönüştürme | AI / Veri | PB-06 | Done - 80 resmî, 170 mikro etkinlik üretildi |

## Çalışma Sırası

1. Veri alanları ve enum değerleri tek sözlükte kesinleştirilir.
2. Event V3 JSON Schema hazırlanır.
3. Organizer, participation, rating ve interest-weight şemaları hazırlanır.
4. En az bir resmî ve bir mikro etkinlik örneği doğrulanır.
5. Mevcut SQLite için geriye uyumlu migration yazılır.
6. V2 üretici betiği V3 hedefini üretecek şekilde genişletilir.
7. Seed, şema ve migration testleri çalıştırılır.
8. API ve mobil tipleri için Faz 2 giriş sözleşmesi yayımlanır.

## Definition of Done

- Şema alanları Faz 0 kararlarıyla çelişmez.
- Migration mevcut profil ve interaction verisini silmez.
- Seed tekrar çalıştırıldığında kayıt çoğaltmaz.
- Sentetik veri en az 50 resmî ve 100 mikro etkinlik içerir.
- Kara listeli organizatör ve süresi dolmuş mikro etkinlik test örnekleri vardır.
- JSON Schema, backend testleri ve Python derleme kontrolleri başarılıdır.
- README ve Sprint 3 durumu gerçek uygulamayla eşitlenmiştir.

## Riskler ve Önlemler

| Risk | Önlem |
|---|---|
| V2 alanlarının V3'e kayıpsız taşınamaması | Dönüşüm eşleme tablosu ve reddedilen kayıt raporu |
| Mevcut SQLite verisinin bozulması | Geçici test DB'si ve ileri yönlü migration |
| Mobil ve backend enum farklılığı | JSON Schema'yı tek sözleşme kaynağı yapmak |
| Mikro etkinliklerde güven açığı | Yayın öncesi trust ve süre kontrolünü DB/API seviyesinde uygulamak |
| ML kapsamının Faz 1'i büyütmesi | Faz 1'de model servisleme yapmamak |
