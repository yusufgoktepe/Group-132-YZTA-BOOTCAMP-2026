"""
CampusMatch MVP – Sentetik Veri Üretim Scripti
================================================
Açıklanabilir Öneri Sistemi (Classification) için kullanılacak
sentetik veriyi üretir ve 'data/sample/campusmatch_mvp_data.csv'
yoluna kaydeder.

Bağımlılıklar: pandas, numpy, faker
Çalıştırma  : python ml/generate_synthetic_data.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ──────────────────────────────────────────────
# Tekrarlanabilirlik
# ──────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
fake = Faker("tr_TR")
Faker.seed(SEED)

# ──────────────────────────────────────────────
# Sabitler
# ──────────────────────────────────────────────
N_USERS = 1_000
N_EVENTS = 200
N_INTERACTIONS = 50_000

N_KURUMSAL = 50
N_MIKRO = N_EVENTS - N_KURUMSAL  # 150

# Kategori haritası: 1=Spor, 2=Oyun, 3=Akademik
KATEGORI_MAP = {1: "dinamik_ilgi_spor", 2: "dinamik_ilgi_oyun", 3: "dinamik_ilgi_akademik"}

# Çıktı yolu (proje kökünden göreli)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "sample"
OUTPUT_FILE = OUTPUT_DIR / "campusmatch_mvp_data.csv"


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 1 – Kullanıcılar (Users)               ║
# ╚═══════════════════════════════════════════════╝
def generate_users(n: int = N_USERS) -> pd.DataFrame:
    """1000 satırlık kullanıcı tablosu üretir."""

    # Dirichlet dağılımı ile ilgi ağırlıkları (toplamları her zaman 1.0)
    ilgi_dagilimi = np.random.dirichlet(alpha=[1, 1, 1], size=n)

    df = pd.DataFrame(
        {
            "kullanici_id": range(1, n + 1),
            "kampus_id": np.random.randint(1, 4, size=n),           # 1–3
            "bolum_kodu": np.random.randint(1, 11, size=n),         # 1–10
            "sinif": np.random.choice([1, 2, 3, 4], size=n),
            "kullanici_guven_puani": np.round(
                np.random.uniform(4.5, 5.0, size=n), 2
            ),
            "dinamik_ilgi_spor": np.round(ilgi_dagilimi[:, 0], 4),
            "dinamik_ilgi_oyun": np.round(ilgi_dagilimi[:, 1], 4),
            "dinamik_ilgi_akademik": np.round(ilgi_dagilimi[:, 2], 4),
        }
    )

    # Yuvarlama sonrası toplamın tam 1.0 olmasını garanti et
    toplam = (
        df["dinamik_ilgi_spor"]
        + df["dinamik_ilgi_oyun"]
        + df["dinamik_ilgi_akademik"]
    )
    fark = np.round(1.0 - toplam, 4)
    df["dinamik_ilgi_akademik"] = df["dinamik_ilgi_akademik"] + fark

    return df


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 2 – Etkinlikler (Events)               ║
# ╚═══════════════════════════════════════════════╝
def generate_events(n: int = N_EVENTS) -> pd.DataFrame:
    """200 satırlık etkinlik tablosu üretir."""

    etkinlik_ids = list(range(1, n + 1))

    # Kurumsal (50) + Mikro (150)
    etkinlik_turu = [1] * N_KURUMSAL + [0] * N_MIKRO

    # Güven puanı: Kurumsal → 5.0 sabit, Mikro → 3.0–5.0 arası
    olusturan_guven = [5.0] * N_KURUMSAL + list(
        np.round(np.random.uniform(3.0, 5.0, size=N_MIKRO), 2)
    )

    df = pd.DataFrame(
        {
            "etkinlik_id": etkinlik_ids,
            "etkinlik_kategorisi": np.random.choice([1, 2, 3], size=n),
            "etkinlik_turu": etkinlik_turu,
            "olusturan_guven_puani": olusturan_guven,
            "etkinlik_ucreti": np.random.choice([0, 1], size=n),
            "zaman_lokasyon": np.random.choice([0, 1], size=n),
        }
    )

    return df


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 3 – Etkileşim Logları (Interactions)   ║
# ╚═══════════════════════════════════════════════╝
def generate_interactions(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    n: int = N_INTERACTIONS,
) -> pd.DataFrame:
    """50.000 satırlık etkileşim logu üretir.

    Hedef değişken `is_swiped_right` mantıksal kurallara
    dayalı olasılıklarla belirlenir.
    """

    # Rastgele kullanıcı–etkinlik eşleşmeleri
    sampled_users = df_users.sample(n=n, replace=True, random_state=SEED).reset_index(drop=True)
    sampled_events = df_events.sample(n=n, replace=True, random_state=SEED).reset_index(drop=True)

    # Etkileşim tablosu iskeleti
    df_inter = pd.DataFrame(
        {
            "kullanici_id": sampled_users["kullanici_id"].values,
            "etkinlik_id": sampled_events["etkinlik_id"].values,
            "zaman_farki_dk": np.random.randint(1, 1441, size=n),  # 1–1440
        }
    )

    # ── Hedef değişken hesaplama ────────────────────
    # Her satır için olasılık belirle
    proba = np.full(n, 0.40)  # Varsayılan olasılık

    for i in range(n):
        kategori = sampled_events.iloc[i]["etkinlik_kategorisi"]
        ucret = sampled_events.iloc[i]["etkinlik_ucreti"]
        guven = sampled_events.iloc[i]["olusturan_guven_puani"]

        # Kullanıcının ilgili kategorideki ağırlığı
        ilgi_col = KATEGORI_MAP[kategori]
        ilgi_degeri = sampled_users.iloc[i][ilgi_col]

        # Kural 1: İlgi alanı eşleşmesi (> 0.5) VE ücretsiz → %85
        if ilgi_degeri > 0.5 and ucret == 0:
            proba[i] = 0.85

        # Kural 2: Düşük güven puanı → %15
        if guven < 3.5:
            proba[i] = 0.15

    # Olasılıklara göre swipe kararı
    is_swiped_right = (np.random.rand(n) < proba).astype(int)
    df_inter["is_swiped_right"] = is_swiped_right

    # Ekranda kalma süresi: swiped_right=1 → 5-15 sn, 0 → 1-4 sn
    ekranda_kalma = np.where(
        is_swiped_right == 1,
        np.random.randint(5, 16, size=n),
        np.random.randint(1, 5, size=n),
    )
    df_inter["ekranda_kalma_suresi_sn"] = ekranda_kalma

    return df_inter


# ╔═══════════════════════════════════════════════╗
# ║  ADIM 4 – Birleştirme ve Kayıt               ║
# ╚═══════════════════════════════════════════════╝
def merge_and_save(
    df_users: pd.DataFrame,
    df_events: pd.DataFrame,
    df_interactions: pd.DataFrame,
) -> pd.DataFrame:
    """Tabloları birleştirir, tip dönüşümlerini yapar ve CSV olarak kaydeder."""

    # Merge: interactions ← users ← events
    df_master = df_interactions.merge(df_users, on="kullanici_id", how="left")
    df_master = df_master.merge(df_events, on="etkinlik_id", how="left")

    # Kategorik sütunları uygun tiplere dönüştür (model için hazır)
    int_cols = [
        "kullanici_id",
        "etkinlik_id",
        "kampus_id",
        "bolum_kodu",
        "sinif",
        "etkinlik_kategorisi",
        "etkinlik_turu",
        "etkinlik_ucreti",
        "zaman_lokasyon",
        "zaman_farki_dk",
        "is_swiped_right",
        "ekranda_kalma_suresi_sn",
    ]
    for col in int_cols:
        df_master[col] = df_master[col].astype(int)

    float_cols = [
        "kullanici_guven_puani",
        "dinamik_ilgi_spor",
        "dinamik_ilgi_oyun",
        "dinamik_ilgi_akademik",
        "olusturan_guven_puani",
    ]
    for col in float_cols:
        df_master[col] = df_master[col].astype(float)

    # Dizin yoksa oluştur
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CSV kayıt
    df_master.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    return df_master


# ──────────────────────────────────────────────
# Ana akış
# ──────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  CampusMatch MVP - Sentetik Veri Uretimi Basliyor")
    print("=" * 60)

    # Adım 1
    print("\n[1/4] Kullanicilar uretiliyor ...")
    df_users = generate_users()
    print(f"      [OK] {len(df_users):,} kullanici uretildi.")

    # Adım 2
    print("[2/4] Etkinlikler uretiliyor ...")
    df_events = generate_events()
    print(f"      [OK] {len(df_events):,} etkinlik uretildi.")

    # Adım 3
    print("[3/4] Etkilesim loglari uretiliyor ...")
    df_interactions = generate_interactions(df_users, df_events)
    print(f"      [OK] {len(df_interactions):,} etkilesim logu uretildi.")

    # Adım 4
    print("[4/4] Tablolar birlestiriliyor ve kaydediliyor ...")
    df_master = merge_and_save(df_users, df_events, df_interactions)
    print(f"      [OK] df_master boyutu: {df_master.shape}")
    print(f"      [OK] Dosya kaydedildi -> {OUTPUT_FILE}")

    # Özet istatistikler
    print("\n" + "-" * 60)
    print("  OZET ISTATISTIKLER")
    print("-" * 60)
    print(f"  Toplam satir        : {len(df_master):,}")
    print(f"  Toplam sutun        : {len(df_master.columns)}")
    print(f"  Sutunlar            : {list(df_master.columns)}")

    swipe_dist = df_master["is_swiped_right"].value_counts(normalize=True)
    print(f"\n  Hedef degisken dagilimi (is_swiped_right):")
    print(f"    0 (Sola kaydirdi) : {swipe_dist.get(0, 0):.2%}")
    print(f"    1 (Saga kaydirdi) : {swipe_dist.get(1, 0):.2%}")

    # İlgi alanı toplamı doğrulama
    ilgi_toplam = (
        df_master["dinamik_ilgi_spor"]
        + df_master["dinamik_ilgi_oyun"]
        + df_master["dinamik_ilgi_akademik"]
    )
    print(f"\n  Ilgi alani toplam dogrulama (hepsi 1.0 olmali):")
    print(f"    min = {ilgi_toplam.min():.4f}")
    print(f"    max = {ilgi_toplam.max():.4f}")

    print("\n" + "=" * 60)
    print("  Veri uretimi basariyla tamamlandi! [OK]")
    print("=" * 60)


if __name__ == "__main__":
    main()
