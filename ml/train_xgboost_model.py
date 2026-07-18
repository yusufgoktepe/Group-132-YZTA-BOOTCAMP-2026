"""
CampusMatch AI - XGBoost Siniflandirma Modeli (Baseline)
========================================================
Sentetik veri seti uzerinden is_swiped_right hedef degiskeni
icin bir XGBoost Classifier egitir, degerlendirir ve kaydeder.

Girdi  : data/sample/campusmatch_mvp_data.csv
Cikti  : ml/xgb_model.pkl
Calistir: python ml/train_xgboost_model.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from xgboost import XGBClassifier

# ──────────────────────────────────────────────
# Yollar
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "sample" / "campusmatch_mvp_data.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "xgb_model.pkl"

# ──────────────────────────────────────────────
# Sabitler
# ──────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE = 0.20
TARGET_COL = "is_swiped_right"
DROP_COLS = ["kullanici_id", "etkinlik_id", "ekranda_kalma_suresi_sn"]  # ID + leakage kolonlari


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 1 - Veri Hazirligi                     ║
# ╚═══════════════════════════════════════════════╝
def load_and_prepare(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """CSV'yi okur, hedef ve ozellik matrisini ayirir."""

    print(f"  Veri okunuyor: {path}")
    df = pd.read_csv(path)
    print(f"  Veri boyutu : {df.shape}")

    # Hedef degisken
    y = df[TARGET_COL]

    # Ozellik matrisi (ID kolonlari cikarilir)
    X = df.drop(columns=[TARGET_COL] + DROP_COLS)

    print(f"  Ozellikler  : {list(X.columns)}")
    print(f"  Hedef dagilimi:\n{y.value_counts().to_string()}")

    return X, y


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 2 - Veri Bolumleme                     ║
# ╚═══════════════════════════════════════════════╝
def split_data(
    X: pd.DataFrame, y: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Veriyi %80 egitim / %20 test olarak boler."""

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"  Egitim seti  : {X_train.shape[0]:,} satir")
    print(f"  Test seti    : {X_test.shape[0]:,} satir")

    return X_train, X_test, y_train, y_test


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 3 - Model Kurulumu ve Egitim           ║
# ╚═══════════════════════════════════════════════╝
def train_model(
    X_train: pd.DataFrame, y_train: pd.Series
) -> XGBClassifier:
    """XGBoost Classifier olusturur ve egitir."""

    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=RANDOM_STATE,
        verbosity=0,
    )

    print("  Model egitiliyor ...")
    model.fit(X_train, y_train)
    print("  [OK] Model egitimi tamamlandi.")

    return model


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 4 - Degerlendirme                      ║
# ╚═══════════════════════════════════════════════╝
def evaluate_model(
    model: XGBClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> None:
    """Test seti uzerinde tahmin yapar ve metrikleri yazdirir."""

    # Tahminler
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Accuracy
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  Accuracy : {acc:.4f}")

    # ROC-AUC
    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"  ROC-AUC  : {roc_auc:.4f}")

    # Classification Report
    print("\n  Classification Report:")
    print("  " + "-" * 56)
    report = classification_report(y_test, y_pred, target_names=["Sola (0)", "Saga (1)"])
    for line in report.split("\n"):
        print(f"  {line}")
    print("  " + "-" * 56)

    # Feature Importance (konsol ciktisi)
    print("\n  Feature Importance (Top 10):")
    print("  " + "-" * 40)
    importances = model.feature_importances_
    feature_names = model.feature_names_in_
    fi_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    for idx, row in fi_df.head(10).iterrows():
        bar = "#" * int(row["importance"] * 50)
        print(f"  {idx + 1:2d}. {row['feature']:<28s} {row['importance']:.4f}  {bar}")

    # Feature importance CSV kaydi (opsiyonel, analiz icin)
    fi_path = PROJECT_ROOT / "ml" / "feature_importance.csv"
    fi_df.to_csv(fi_path, index=False)
    print(f"\n  Feature importance tablosu -> {fi_path}")


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 5 - Model Kaydi                        ║
# ╚═══════════════════════════════════════════════╝
def save_model(model: XGBClassifier, path: Path) -> None:
    """Egitilmis modeli joblib ile diske kaydeder."""

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    print(f"  [OK] Model kaydedildi -> {path}")

    # Boyut bilgisi
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"  Dosya boyutu: {size_mb:.2f} MB")


# ──────────────────────────────────────────────
# Ana akis
# ──────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  CampusMatch AI - XGBoost Baseline Model Egitimi")
    print("=" * 60)

    # Adim 1
    print("\n[1/5] Veri Hazirligi")
    X, y = load_and_prepare(DATA_PATH)

    # Adim 2
    print("\n[2/5] Veri Bolumleme")
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Adim 3
    print("\n[3/5] Model Egitimi")
    model = train_model(X_train, y_train)

    # Adim 4
    print("\n[4/5] Model Degerlendirmesi")
    evaluate_model(model, X_test, y_test)

    # Adim 5
    print("\n[5/5] Model Kaydi")
    save_model(model, MODEL_PATH)

    print("\n" + "=" * 60)
    print("  Egitim sureci basariyla tamamlandi! [OK]")
    print("=" * 60)


if __name__ == "__main__":
    main()
