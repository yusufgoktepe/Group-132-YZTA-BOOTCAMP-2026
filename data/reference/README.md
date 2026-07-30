# Türkiye Eğitim Referans Verisi

Mobil uygulama üniversite ve programları serbest metin olarak kabul etmez. Güncel
referans, 30 Temmuz 2026 tarihinde yayımlanan ÖSYM 2026-YKS tablolarından üretilmiştir.

- Referans sürümü: `osym-yks-2026-2026-07-30`
- Kapsam: 202 aktif üniversite, 14.281 ön lisans ve lisans programı
- Ön lisans kaynağı: [ÖSYM 2026-YKS Tablo 3](https://dokuman.osym.gov.tr/web//2026/7/tablo-3-29u1s7pl.xls)
- Lisans kaynağı: [ÖSYM 2026-YKS Tablo 4](https://dokuman.osym.gov.tr/web//2026/7/tablo-4-295piovw.xls)
- Üretilen mobil veri: `mobile/data/education-reference.generated.json`
- Dönüştürme aracı: `scripts/generate_education_reference.py`

Program süresi doğrudan resmî tablodan alınır ve sınıf seçenekleri bu süreye göre
oluşturulur. Hazırlık seçeneği, program adında yabancı öğretim dili belirtilmesine göre
türetilir; üretim kullanımı öncesinde zorunlu hazırlık bilgisi YÖK Atlas ile ayrıca
doğrulanmalıdır.

Gelecek veri güncellemelerinde:

1. Resmî üniversite kimlikleri ve aktiflik durumları alınmalı.
2. Lisans ve ön lisans programları üniversite kimliğiyle eşleştirilmeli.
3. Programın standart süresi ve hazırlık bilgisi doğrulanmalı.
4. Veri kaynağı yılı `reference_version` alanında tutulmalı.
5. Kaldırılan veya adı değişen programlar silinmemeli, pasif olarak işaretlenmeli.

Kaynaklar: ÖSYM 2026-YKS Yükseköğretim Programları ve Kontenjanları Kılavuzu
Tablo 3/4 ve hazırlık doğrulaması için YÖK Atlas üniversite/program sayfaları.
