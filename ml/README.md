# CampusMatch AI ML Deneyleri

Canlı backend açıklanabilir `rule_based_v3` sıralamasını kullanır. Bu klasördeki model
dosyaları offline araştırma çıktılarıdır; doğrudan mobil uygulamada çalıştırılmaz.

## Faz 7 temporal değerlendirme

```powershell
.\.venv\Scripts\python.exe ml\evaluate_ranking_v3.py
```

Betik:

1. `interactions_v2.csv` dosyasını artan `interaction_id` ile sıralar.
2. İlk `%70` bölümü train, sonraki `%15` validation ve son `%15` test yapar.
3. Çoğunluk, açıklanabilir kural proxy'si, XGBoost ve validation ile seçilen hibriti karşılaştırır.
4. ROC-AUC, Precision@5 ve NDCG@10 metriklerini üretir.
5. 170 mikro etkinlik üzerinde 2–8 küme için K-Means silhouette deneyi yapar.

Kaynak veri gerçek timestamp içermediğinden `interaction_id` yalnızca zaman proxy'sidir.
Production promotion için gerçek zaman damgalı veride en az `%2` göreli NDCG@10 artışı,
güven filtrelerinin korunması ve kural bazlı fallback şarttır.

Çıktılar:

- `ranking_evaluation_v3.json`: makine tarafından okunabilir metrik ve karar kaydı
- `ranking_evaluation_v3.md`: insan tarafından okunabilir değerlendirme raporu
- `xgb_temporal_v3.json`: yalnız offline deney için eğitilmiş XGBoost modeli

Eski `metrics.json`, `model_comparison.md` ve `xgb_model.pkl` rastgele split kullanılan
Sprint 2 araştırma çıktılarıdır; Faz 7 production kararının dayanağı değildir.
