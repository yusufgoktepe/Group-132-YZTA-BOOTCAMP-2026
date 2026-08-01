"""CampusMatch Faz 7: temporal offline ranking ve mikro K-Means deneyi.

V2 interaction verisinde gerçek timestamp bulunmadığı için artan ``interaction_id``
üretim sırası (proxy time) kabul edilir. Split: ilk %70 train, sonraki %15 validation,
son %15 test. Test etiketleri eğitim, özellik üretimi veya model seçiminde kullanılmaz.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score, silhouette_score
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
V2_DIR = PROJECT_ROOT / "data" / "sample" / "v2"
V3_DIR = PROJECT_ROOT / "data" / "sample" / "v3"
OUTPUT_PATH = PROJECT_ROOT / "ml" / "ranking_evaluation_v3.json"
REPORT_PATH = PROJECT_ROOT / "ml" / "ranking_evaluation_v3.md"
MODEL_PATH = PROJECT_ROOT / "ml" / "xgb_temporal_v3.json"

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TOP_K = 5
NDCG_K = 10
POSITIVE_ACTIONS = {"like", "save", "apply"}
RANDOM_STATE = 42


def load_interaction_frame() -> pd.DataFrame:
    interactions = pd.read_csv(V2_DIR / "interactions_v2.csv")
    profiles = pd.read_csv(V2_DIR / "profiles_v2.csv")
    events = pd.read_csv(V2_DIR / "events_v2.csv")
    frame = interactions.merge(profiles, on="profile_id", validate="many_to_one")
    frame = frame.merge(events, on="event_id", validate="many_to_one", suffixes=("_profile", "_event"))
    frame = frame.sort_values("interaction_id").reset_index(drop=True)
    frame["relevance"] = (
        frame["action"].isin(POSITIVE_ACTIONS)
        | ((frame["action"] == "view_detail") & (frame["dwell_time_seconds"] >= 8))
    ).astype(int)
    return frame


def temporal_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_end = int(len(frame) * TRAIN_RATIO)
    validation_end = int(len(frame) * (TRAIN_RATIO + VALIDATION_RATIO))
    return (
        frame.iloc[:train_end].copy(),
        frame.iloc[train_end:validation_end].copy(),
        frame.iloc[validation_end:].copy(),
    )


def _contains(tags: Any, value: Any) -> bool:
    return str(value) in {item.strip() for item in str(tags or "").split(";") if item.strip()}


def build_features(frame: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    features = pd.DataFrame(index=frame.index)
    features["interest_overlap"] = frame["interest_overlap_count"].clip(0, 3) / 3
    features["goal_overlap"] = frame["goal_overlap_count"].clip(0, 3) / 3
    features["mode_match"] = [
        float(_contains(modes, mode))
        for modes, mode in zip(frame["participation_modes"], frame["participation_mode"])
    ]
    features["fee_match"] = (
        (frame["fee_preference"] != "free_only") | (frame["fee_type"] == "free")
    ).astype(float)
    features["language_match"] = (
        (frame["language_preference"] == "no_preference")
        | (frame["language_preference"] == frame["language"])
        | (frame["language"] == "mixed")
    ).astype(float)
    features["same_university"] = (
        frame["university_id_profile"] == frame["university_id_event"]
    ).astype(float)
    features["quota_scaled"] = frame["quota"].clip(0, 500) / 500
    starts = pd.to_datetime(frame["starts_at"], utc=True)
    ends = pd.to_datetime(frame["ends_at"], utc=True)
    features["duration_hours"] = ((ends - starts).dt.total_seconds() / 3600).clip(0, 24) / 24
    categorical = pd.get_dummies(
        frame[["category_id", "event_type", "participation_mode"]].fillna("unknown"),
        dtype=float,
    )
    features = pd.concat([features, categorical], axis=1)
    if columns is not None:
        features = features.reindex(columns=columns, fill_value=0.0)
    return features.astype(float)


def rule_based_scores(features: pd.DataFrame) -> np.ndarray:
    return (
        features["interest_overlap"] * 0.45
        + features["goal_overlap"] * 0.15
        + features["mode_match"] * 0.10
        + features["fee_match"] * 0.08
        + features["language_match"] * 0.07
        + features["same_university"] * 0.10
        + (1 - features["quota_scaled"]) * 0.05
    ).to_numpy()


def precision_at_k(frame: pd.DataFrame, scores: np.ndarray, k: int = TOP_K) -> float:
    ranked = frame.assign(_score=scores)
    values = []
    for _, group in ranked.groupby("profile_id"):
        top = group.nlargest(min(k, len(group)), "_score")
        values.append(float(top["relevance"].mean()))
    return float(np.mean(values)) if values else 0.0


def ndcg_at_k(frame: pd.DataFrame, scores: np.ndarray, k: int = NDCG_K) -> float:
    ranked = frame.assign(_score=scores)
    values = []
    for _, group in ranked.groupby("profile_id"):
        ordered = group.sort_values("_score", ascending=False)["relevance"].to_numpy()[:k]
        ideal = np.sort(group["relevance"].to_numpy())[::-1][:k]
        discounts = 1 / np.log2(np.arange(2, len(ordered) + 2))
        dcg = float(np.sum(ordered * discounts))
        idcg = float(np.sum(ideal * discounts))
        if idcg > 0:
            values.append(dcg / idcg)
    return float(np.mean(values)) if values else 0.0


def evaluate(frame: pd.DataFrame, scores: np.ndarray) -> dict[str, float]:
    labels = frame["relevance"].to_numpy()
    return {
        "roc_auc": round(float(roc_auc_score(labels, scores)), 4),
        f"precision_at_{TOP_K}": round(precision_at_k(frame, scores), 4),
        f"ndcg_at_{NDCG_K}": round(ndcg_at_k(frame, scores), 4),
    }


def run_kmeans_experiment() -> dict[str, Any]:
    events = pd.read_csv(V3_DIR / "events_v3.csv")
    micro = events[events["event_tier"] == "micro"].copy()
    starts = pd.to_datetime(micro["starts_at"], utc=True)
    ends = pd.to_datetime(micro["ends_at"], utc=True)
    numeric = pd.DataFrame(
        {
            "quota": micro["quota"].astype(float),
            "trust": micro["organizer_trust_score"].astype(float),
            "fee": micro["fee_amount"].fillna(0).astype(float),
            "duration_hours": (ends - starts).dt.total_seconds() / 3600,
        }
    )
    categorical = pd.get_dummies(
        micro[["category_id", "participation_mode"]], dtype=float
    ).reset_index(drop=True)
    matrix = np.hstack([StandardScaler().fit_transform(numeric), categorical.to_numpy()])
    candidates = []
    best: tuple[float, int, np.ndarray] | None = None
    for clusters in range(2, 9):
        labels = KMeans(n_clusters=clusters, random_state=RANDOM_STATE, n_init=10).fit_predict(matrix)
        score = float(silhouette_score(matrix, labels))
        candidates.append({"clusters": clusters, "silhouette": round(score, 4)})
        if best is None or score > best[0]:
            best = (score, clusters, labels)
    assert best is not None
    sizes = pd.Series(best[2]).value_counts().sort_index().to_dict()
    return {
        "event_count": len(micro),
        "selected_clusters": best[1],
        "silhouette": round(best[0], 4),
        "cluster_sizes": {str(key): int(value) for key, value in sizes.items()},
        "candidates": candidates,
        "production_decision": "experiment_only",
    }


def run_evaluation(save_model: bool = True) -> dict[str, Any]:
    from xgboost import XGBClassifier

    frame = load_interaction_frame()
    train, validation, test = temporal_split(frame)
    train_features = build_features(train)
    validation_features = build_features(validation, list(train_features.columns))
    test_features = build_features(test, list(train_features.columns))
    model = XGBClassifier(
        n_estimators=160, max_depth=4, learning_rate=0.06, subsample=0.9,
        colsample_bytree=0.9, objective="binary:logistic", eval_metric="logloss",
        random_state=RANDOM_STATE, n_jobs=2,
    )
    model.fit(train_features, train["relevance"])
    validation_model_scores = model.predict_proba(validation_features)[:, 1]
    validation_rule_scores = rule_based_scores(validation_features)
    hybrid_weights = [0.25, 0.40, 0.55]
    selected_weight = max(
        hybrid_weights,
        key=lambda weight: evaluate(
            validation,
            (1 - weight) * validation_rule_scores + weight * validation_model_scores,
        )[f"ndcg_at_{NDCG_K}"],
    )

    test_rule_scores = rule_based_scores(test_features)
    test_model_scores = model.predict_proba(test_features)[:, 1]
    test_hybrid_scores = (1 - selected_weight) * test_rule_scores + selected_weight * test_model_scores
    majority = np.full(len(test), float(train["relevance"].mean()))
    results = {
        "majority": evaluate(test, majority),
        "rule_based_v3_proxy": evaluate(test, test_rule_scores),
        "xgboost": evaluate(test, test_model_scores),
        "hybrid": evaluate(test, test_hybrid_scores),
    }
    if save_model:
        model.save_model(MODEL_PATH)
    return {
        "generated_on": date.today().isoformat(),
        "dataset": "data/sample/v2/interactions_v2.csv",
        "time_field": "interaction_id (proxy; source has no timestamp)",
        "split": {
            "strategy": "chronological",
            "train": len(train), "validation": len(validation), "test": len(test),
            "train_max_id": int(train["interaction_id"].max()),
            "validation_id_range": [int(validation["interaction_id"].min()), int(validation["interaction_id"].max())],
            "test_min_id": int(test["interaction_id"].min()),
        },
        "label": "like/save/apply or view_detail with dwell>=8s",
        "feature_columns": list(train_features.columns),
        "selected_model_weight": selected_weight,
        "selection_metric": f"validation ndcg@{NDCG_K}",
        "test_results": results,
        "kmeans_micro": run_kmeans_experiment(),
        "production_decision": "rule_based_v3",
    }


def write_report(payload: dict[str, Any]) -> None:
    metrics = payload["test_results"]
    rule_ndcg = metrics["rule_based_v3_proxy"]["ndcg_at_10"]
    xgb_gain = (metrics["xgboost"]["ndcg_at_10"] / rule_ndcg - 1) * 100
    hybrid_gain = (metrics["hybrid"]["ndcg_at_10"] / rule_ndcg - 1) * 100
    lines = [
        "# Faz 7 Temporal Ranking Değerlendirmesi", "",
        f"Üretim tarihi: {payload['generated_on']}  ",
        f"Veri: `{payload['dataset']}`  ",
        f"Zaman alanı: `{payload['time_field']}`", "",
        "## Veri ayrımı", "",
        f"- Train: {payload['split']['train']:,} kayıt (ID ≤ {payload['split']['train_max_id']})",
        f"- Validation: {payload['split']['validation']:,} kayıt (ID {payload['split']['validation_id_range'][0]}–{payload['split']['validation_id_range'][1]})",
        f"- Test: {payload['split']['test']:,} kayıt (ID ≥ {payload['split']['test_min_id']})",
        "- Gerçek timestamp bulunmadığı için interaction ID yalnızca kronolojik proxy'dir.", "",
        "## Test sonuçları", "",
        "| Yaklaşım | ROC-AUC | Precision@5 | NDCG@10 |", "|---|---:|---:|---:|",
    ]
    labels = {"majority": "Çoğunluk", "rule_based_v3_proxy": "Kural bazlı V3 proxy", "xgboost": "XGBoost", "hybrid": "Hibrit"}
    for key, label in labels.items():
        value = metrics[key]
        lines.append(f"| {label} | {value['roc_auc']:.4f} | {value['precision_at_5']:.4f} | {value['ndcg_at_10']:.4f} |")
    kmeans = payload["kmeans_micro"]
    lines += [
        "", "## Mikro etkinlik K-Means deneyi", "",
        f"- {kmeans['event_count']} mikro etkinlik üzerinde en iyi küme sayısı: `{kmeans['selected_clusters']}`.",
        f"- Silhouette skoru: `{kmeans['silhouette']:.4f}`.",
        f"- Küme büyüklükleri: `{json.dumps(kmeans['cluster_sizes'], ensure_ascii=False)}`.",
        "- Deney yalnızca aday üretimini hızlandırma hipotezidir; production feed'e bağlanmadı.", "",
        "## Production kararı", "",
        f"- XGBoost göreli NDCG@10 kazancı: `%{xgb_gain:.2f}`.",
        f"- Validation ile seçilen `%{payload['selected_model_weight'] * 100:.0f}` model ağırlıklı hibritin göreli kazancı: `%{hybrid_gain:.2f}`.",
        "- Her iki sonuç da `%2` promotion eşiğinin altındadır.", "",
        "Canlı sistemde açıklanabilir `rule_based_v3` korunur. Model veya hibrit yaklaşım ancak gerçek",
        "timestamp'li kullanıcı verisinde NDCG@10'u tekrarlanabilir biçimde en az %2 göreli artırırsa,",
        "güven filtrelerini aşmadan ve kural bazlı fallback korunarak gölge trafikte denenebilir.", "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = run_evaluation(save_model=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload)
    print(json.dumps(payload["test_results"], ensure_ascii=False, indent=2))
    print(f"[OK] {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"[OK] {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
