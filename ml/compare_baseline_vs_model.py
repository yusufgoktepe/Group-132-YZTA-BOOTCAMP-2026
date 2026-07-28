"""
CampusMatch AI - Baseline / XGBoost Karsilastirmasi
===================================================
Uc yaklasimi ayni test bolumu uzerinde karsilastirir:

1. `majority`  : Cogunluk sinifini tahmin eden trivial taban.
2. `rule_based`: Backend'de calisan aciklanabilir skor mantiginin bu veri
                 setindeki karsiligi (ilgi uyumu + ucret + olusturan guveni +
                 egitim bolumunden hesaplanan etkinlik populerligi).
3. `xgboost`   : `ml/xgb_model.pkl` icindeki egitilmis model. Dosya yoksa veya
                 yuklenemezse ayni yapilandirmayla yeniden egitilir; o da
                 basarisiz olursa karsilastirma kural bazli sonucla devam eder.

Girdi  : data/sample/campusmatch_mvp_data.csv
Cikti  : ml/metrics.json, ml/model_comparison.md
Calistir: python ml/compare_baseline_vs_model.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "sample" / "campusmatch_mvp_data.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "xgb_model.pkl"
METRICS_PATH = PROJECT_ROOT / "ml" / "metrics.json"
REPORT_PATH = PROJECT_ROOT / "ml" / "model_comparison.md"

# train_xgboost_model.py ile ayni bolumleme; model o split ile egitildi.
RANDOM_STATE = 42
TEST_SIZE = 0.20
TARGET_COL = "is_swiped_right"
DROP_COLS = ["kullanici_id", "etkinlik_id", "ekranda_kalma_suresi_sn"]

# generate_synthetic_data.py icindeki kategori -> ilgi kolonu eslemesi.
KATEGORI_MAP = {1: "dinamik_ilgi_spor", 2: "dinamik_ilgi_oyun", 3: "dinamik_ilgi_akademik"}

DECISION_THRESHOLD = 0.5
TOP_K = 5


# ──────────────────────────────────────────────
# Veri
# ──────────────────────────────────────────────
def load_split() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Egitim ve test bolumlerini tum kolonlariyla birlikte dondurur."""
    frame = pd.read_csv(DATA_PATH)
    train_frame, test_frame = train_test_split(
        frame,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=frame[TARGET_COL],
    )
    return train_frame.reset_index(drop=True), test_frame.reset_index(drop=True)


# ──────────────────────────────────────────────
# Yaklasim 1 - Cogunluk sinifi
# ──────────────────────────────────────────────
def majority_scores(train_frame: pd.DataFrame, test_frame: pd.DataFrame) -> np.ndarray:
    positive_rate = float(train_frame[TARGET_COL].mean())
    return np.full(len(test_frame), positive_rate)


# ──────────────────────────────────────────────
# Yaklasim 2 - Aciklanabilir kural bazli skor
# ──────────────────────────────────────────────
def rule_based_scores(train_frame: pd.DataFrame, test_frame: pd.DataFrame) -> np.ndarray:
    """Backend skorlamasinin bu veri setindeki karsiligi.

    Populerlik sinyali yalnizca egitim bolumunden hesaplanir; test bolumunun
    etiketleri hicbir asamada kullanilmaz.
    """
    global_rate = float(train_frame[TARGET_COL].mean())
    popularity = train_frame.groupby("etkinlik_id")[TARGET_COL].mean()

    interest = np.array(
        [
            row[KATEGORI_MAP[int(row["etkinlik_kategorisi"])]]
            for _, row in test_frame.iterrows()
        ]
    )
    is_free = (test_frame["etkinlik_ucreti"] == 0).to_numpy()
    trusted = (test_frame["olusturan_guven_puani"] >= 3.5).to_numpy()
    event_popularity = (
        test_frame["etkinlik_id"].map(popularity).fillna(global_rate).to_numpy()
    )

    # Backend'deki agirliklandirmanin ayni mantigi: profil uyumu %80, populerlik %20.
    profile_match = np.where(
        (interest > 0.5) & is_free,
        0.85,
        np.where(interest > 0.5, 0.55, 0.35),
    )
    scores = 0.8 * profile_match + 0.2 * event_popularity

    # Dusuk guvenilirlikli etkinlikler geriye alinir.
    return np.where(trusted, scores, scores * 0.25)


# ──────────────────────────────────────────────
# Yaklasim 3 - XGBoost
# ──────────────────────────────────────────────
def xgboost_scores(
    train_frame: pd.DataFrame, test_frame: pd.DataFrame
) -> tuple[np.ndarray | None, str]:
    """Model olasiliklarini dondurur. Basarisiz olursa (None, sebep) doner."""
    feature_columns = [
        column for column in train_frame.columns if column not in [TARGET_COL, *DROP_COLS]
    ]
    x_test = test_frame[feature_columns]

    if MODEL_PATH.exists():
        try:
            import joblib

            model = joblib.load(MODEL_PATH)
            return model.predict_proba(x_test)[:, 1], "kayitli model (ml/xgb_model.pkl)"
        except Exception as error:  # noqa: BLE001 - hangi hata olursa olsun yedege gec
            print(f"  [UYARI] Kayitli model yuklenemedi: {error}")

    try:
        from xgboost import XGBClassifier

        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            verbosity=0,
        )
        model.fit(train_frame[feature_columns], train_frame[TARGET_COL])
        return model.predict_proba(x_test)[:, 1], "oturumda yeniden egitildi"
    except Exception as error:  # noqa: BLE001
        print(f"  [UYARI] Model egitilemedi: {error}")
        return None, f"kullanilamadi ({type(error).__name__})"


# ──────────────────────────────────────────────
# Metrikler
# ──────────────────────────────────────────────
def precision_at_k(test_frame: pd.DataFrame, scores: np.ndarray, k: int = TOP_K) -> float:
    """Kullanici basina en yuksek skorlu k etkinligin isabet orani.

    Siralama kalitesini olcer; oneri ekraninda gorulen sey budur.
    """
    ranked = test_frame.assign(_score=scores)
    hits, total = 0, 0
    for _, group in ranked.groupby("kullanici_id"):
        if len(group) < k:
            continue
        top = group.nlargest(k, "_score")
        hits += int(top[TARGET_COL].sum())
        total += k
    return hits / total if total else float("nan")


def evaluate(test_frame: pd.DataFrame, scores: np.ndarray) -> dict[str, float]:
    y_true = test_frame[TARGET_COL].to_numpy()
    y_pred = (scores >= DECISION_THRESHOLD).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, scores)), 4),
        f"precision_at_{TOP_K}": round(precision_at_k(test_frame, scores), 4),
    }


# ──────────────────────────────────────────────
# Rapor
# ──────────────────────────────────────────────
METRIC_LABELS = {
    "accuracy": "Accuracy",
    "precision": "Precision",
    "recall": "Recall",
    "f1": "F1",
    "roc_auc": "ROC-AUC",
    f"precision_at_{TOP_K}": f"Precision@{TOP_K}",
}


def write_report(payload: dict[str, Any]) -> None:
    results = payload["results"]
    names = list(results)
    header = " | ".join(["Metrik", *(results[name]["label"] for name in names)])
    divider = " | ".join(["---"] * (len(names) + 1))

    rows = []
    for key, label in METRIC_LABELS.items():
        cells = [f"{results[name]['metrics'][key]:.4f}" for name in names]
        rows.append(" | ".join([label, *cells]))

    lines = [
        "# Baseline ve Model Karsilastirmasi",
        "",
        f"Uretim tarihi: {payload['generated_on']}  ",
        f"Veri: `{payload['dataset']}` ({payload['row_count']:,} satir, "
        f"test bolumu {payload['test_row_count']:,} satir)  ",
        f"Model kaynagi: {payload['model_source']}",
        "",
        "Uretmek icin: `python ml/compare_baseline_vs_model.py`",
        "",
        "## Sonuclar",
        "",
        f"| {header} |",
        f"| {divider} |",
        *(f"| {row} |" for row in rows),
        "",
        "## Yorum",
        "",
        *payload["notes"],
        "",
        "## Metriklerin anlami",
        "",
        "- **ROC-AUC**: Saga kaydirilan bir etkinligin, kaydirilmayan bir etkinligin",
        "  onunde siralanma olasiligi. Oneri sistemi icin en anlamli metrik budur.",
        f"- **Precision@{TOP_K}**: Kullaniciya gosterilen ilk {TOP_K} etkinlikten kacinin",
        "  gercekten begenildigi. Kullanicinin ekranda gordugu kaliteyi olcer.",
        "- **Accuracy / F1**: Sabit 0.5 esigiyle alinan ikili karar kalitesi.",
        "",
        "## Uretimde hangisi kullaniliyor",
        "",
        "Backend `/recommendations/*` uclari kural bazli skorlamayi kullanir",
        "(`backend/app/recommendation_service.py`). Skor, aciklanabilir profil",
        "eslesmesinin %80'i, sentetik swipe populerliginin %20'si ve kullanicinin",
        "kendi like/skip/save hareketlerinden gelen duzeltmenin toplamidir.",
        "XGBoost modeli bu sprintte yalnizca karsilastirma amaciyla degerlendirildi;",
        "servise baglanmadi. Bu nedenle model dosyasi bozuk veya eksik olsa bile",
        "oneri akisi etkilenmez.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_notes(results: dict[str, dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    rule = results["rule_based"]["metrics"]
    majority = results["majority"]["metrics"]

    notes.append(
        f"- Kural bazli skor, cogunluk tabanina gore ROC-AUC'yi "
        f"{majority['roc_auc']:.4f} seviyesinden {rule['roc_auc']:.4f} seviyesine tasiyor; "
        "yani siralama tesadufi degil."
    )

    if "xgboost" in results:
        model = results["xgboost"]["metrics"]
        delta = model["roc_auc"] - rule["roc_auc"]
        direction = "ustunde" if delta > 0 else "altinda" if delta < 0 else "ayni seviyede"
        notes.append(
            f"- XGBoost ROC-AUC {model['roc_auc']:.4f} ile kural bazli skorun "
            f"{abs(delta):.4f} puan {direction}."
        )
        if abs(delta) < 0.02:
            notes.append(
                "- Fark anlamli degil. Sentetik veri, backend'in de kullandigi ilgi/ucret/"
                "guven kurallarindan uretildigi icin aciklanabilir skor bu veri setinde "
                "modelin yakaladigi sinyalin buyuk kismini zaten yakaliyor."
            )
            notes.append(
                "- MVP icin aciklanabilir kural bazli skor tercih edilmelidir: ayni "
                "isabetle geliyor, her oneri icin gerekce uretebiliyor ve calisma zamaninda "
                "model dosyasina bagimli degil."
            )
        elif delta > 0:
            notes.append(
                "- Model olculebilir bir kazanc sagliyor. Gercek kullanici etkilesimi "
                "biriktikce servise baglanmasi degerlendirilmelidir; bu asamada oneri "
                "gerekcelerinin nasil uretilecegi de cozulmelidir."
            )
        else:
            notes.append(
                "- Model kural bazli skorun gerisinde kaldigi icin servise baglanmasi "
                "icin bir neden yok."
            )
    else:
        notes.append(
            "- XGBoost degerlendirilemedi; karsilastirma yalnizca kural bazli skorla yapildi. "
            "Bu, uretim akisini etkilemez cunku backend zaten kural bazli skoru kullanir."
        )

    return notes


# ──────────────────────────────────────────────
# Ana akis
# ──────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  CampusMatch AI - Baseline / Model Karsilastirmasi")
    print("=" * 60)

    train_frame, test_frame = load_split()
    print(f"\n  Egitim: {len(train_frame):,} satir | Test: {len(test_frame):,} satir")

    results: dict[str, dict[str, Any]] = {
        "majority": {
            "label": "Cogunluk",
            "metrics": evaluate(test_frame, majority_scores(train_frame, test_frame)),
        },
        "rule_based": {
            "label": "Kural bazli",
            "metrics": evaluate(test_frame, rule_based_scores(train_frame, test_frame)),
        },
    }

    scores, model_source = xgboost_scores(train_frame, test_frame)
    if scores is not None:
        results["xgboost"] = {"label": "XGBoost", "metrics": evaluate(test_frame, scores)}

    payload = {
        "generated_on": date.today().isoformat(),
        "dataset": str(DATA_PATH.relative_to(PROJECT_ROOT)),
        "row_count": len(train_frame) + len(test_frame),
        "test_row_count": len(test_frame),
        "split": {"test_size": TEST_SIZE, "random_state": RANDOM_STATE, "stratified": True},
        "decision_threshold": DECISION_THRESHOLD,
        "model_source": model_source,
        "production_scorer": "rule_based",
        "results": results,
    }
    payload["notes"] = build_notes(results)

    METRICS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(payload)

    print("\n  Sonuclar:")
    width = max(len(entry["label"]) for entry in results.values())
    for entry in results.values():
        metrics = entry["metrics"]
        print(
            f"    {entry['label']:<{width}}  ROC-AUC {metrics['roc_auc']:.4f}  "
            f"Acc {metrics['accuracy']:.4f}  F1 {metrics['f1']:.4f}  "
            f"P@{TOP_K} {metrics[f'precision_at_{TOP_K}']:.4f}"
        )

    print(f"\n  [OK] {METRICS_PATH.relative_to(PROJECT_ROOT)}")
    print(f"  [OK] {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
