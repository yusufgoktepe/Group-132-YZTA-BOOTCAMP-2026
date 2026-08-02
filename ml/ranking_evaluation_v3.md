# Faz 7 Temporal Ranking Değerlendirmesi

Üretim tarihi: 2026-08-01

Veri: `data/sample/v2/interactions_v2.csv`

Zaman alanı: `interaction_id (proxy; source has no timestamp)`

## Veri ayrımı

- Train: 35,000 kayıt (ID ≤ 35000)
- Validation: 7,500 kayıt (ID 35001–42500)
- Test: 7,500 kayıt (ID ≥ 42501)
- Gerçek timestamp bulunmadığı için interaction ID yalnızca kronolojik proxy'dir.

## Test sonuçları

| Yaklaşım | ROC-AUC | Precision@5 | NDCG@10 |
|---|---:|---:|---:|
| Çoğunluk | 0.5000 | 0.5283 | 0.7701 |
| Kural bazlı V3 proxy | 0.5604 | 0.5398 | 0.7992 |
| XGBoost | 0.5633 | 0.5454 | 0.8032 |
| Hibrit | 0.5643 | 0.5470 | 0.8015 |

## Mikro etkinlik K-Means deneyi

- 170 mikro etkinlik üzerinde en iyi küme sayısı: `4`.
- Silhouette skoru: `0.2183`.
- Küme büyüklükleri: `{"0": 12, "1": 50, "2": 82, "3": 26}`.
- Deney yalnızca aday üretimini hızlandırma hipotezidir; production feed'e bağlanmadı.

## Production kararı

- XGBoost göreli NDCG@10 kazancı: `%0.50`.
- Validation ile seçilen `%55` model ağırlıklı hibritin göreli kazancı: `%0.29`.
- Her iki sonuç da `%2` promotion eşiğinin altındadır.

Canlı sistemde açıklanabilir `rule_based_v3` korunur. Model veya hibrit yaklaşım ancak gerçek
timestamp'li kullanıcı verisinde NDCG@10'u tekrarlanabilir biçimde en az %2 göreli artırırsa,
güven filtrelerini aşmadan ve kural bazlı fallback korunarak gölge trafikte denenebilir.
