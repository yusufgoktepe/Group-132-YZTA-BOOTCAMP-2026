# Baseline ve Model Karsilastirmasi

Uretim tarihi: 2026-07-29  
Veri: `data/sample/campusmatch_mvp_data.csv` (50,000 satir, test bolumu 10,000 satir)  
Model kaynagi: kayitli model (ml/xgb_model.pkl)

Uretmek icin: `python ml/compare_baseline_vs_model.py`

## Sonuclar

| Metrik | Cogunluk | Kural bazli | XGBoost |
| --- | --- | --- | --- |
| Accuracy | 0.6049 | 0.6484 | 0.5811 |
| Precision | 0.0000 | 0.6108 | 0.4766 |
| Recall | 0.0000 | 0.3035 | 0.6145 |
| F1 | 0.0000 | 0.4055 | 0.5369 |
| ROC-AUC | 0.5000 | 0.6580 | 0.6552 |
| Precision@5 | 0.4008 | 0.4825 | 0.4837 |

## Yorum

- Kural bazli skor, cogunluk tabanina gore ROC-AUC'yi 0.5000 seviyesinden 0.6580 seviyesine tasiyor; yani siralama tesadufi degil.
- XGBoost ROC-AUC 0.6552 ile kural bazli skorun 0.0028 puan altinda.
- Fark anlamli degil. Sentetik veri, backend'in de kullandigi ilgi/ucret/guven kurallarindan uretildigi icin aciklanabilir skor bu veri setinde modelin yakaladigi sinyalin buyuk kismini zaten yakaliyor.
- MVP icin aciklanabilir kural bazli skor tercih edilmelidir: ayni isabetle geliyor, her oneri icin gerekce uretebiliyor ve calisma zamaninda model dosyasina bagimli degil.

## Metriklerin anlami

- **ROC-AUC**: Saga kaydirilan bir etkinligin, kaydirilmayan bir etkinligin
  onunde siralanma olasiligi. Oneri sistemi icin en anlamli metrik budur.
- **Precision@5**: Kullaniciya gosterilen ilk 5 etkinlikten kacinin
  gercekten begenildigi. Kullanicinin ekranda gordugu kaliteyi olcer.
- **Accuracy / F1**: Sabit 0.5 esigiyle alinan ikili karar kalitesi.

## Uretimde hangisi kullaniliyor

Backend `/recommendations/*` uclari kural bazli skorlamayi kullanir
(`backend/app/recommendation_service.py`). Skor, aciklanabilir profil
eslesmesinin %80'i, sentetik swipe populerliginin %20'si ve kullanicinin
kendi like/skip/save hareketlerinden gelen duzeltmenin toplamidir.
XGBoost modeli bu sprintte yalnizca karsilastirma amaciyla degerlendirildi;
servise baglanmadi. Bu nedenle model dosyasi bozuk veya eksik olsa bile
oneri akisi etkilenmez.
