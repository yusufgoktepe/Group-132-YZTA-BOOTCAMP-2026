"""Faz 7 veri sızıntısı, metrik ve K-Means deney kontrolleri."""

from __future__ import annotations

from ml.evaluate_ranking_v3 import (
    build_features,
    evaluate,
    load_interaction_frame,
    rule_based_scores,
    run_kmeans_experiment,
    temporal_split,
)


def test_temporal_split_is_ordered_and_non_overlapping():
    frame = load_interaction_frame()
    train, validation, test = temporal_split(frame)
    assert len(train) == 35_000
    assert len(validation) == 7_500
    assert len(test) == 7_500
    assert train["interaction_id"].max() < validation["interaction_id"].min()
    assert validation["interaction_id"].max() < test["interaction_id"].min()


def test_ranking_features_do_not_include_target_action_or_dwell_leakage():
    train, _, _ = temporal_split(load_interaction_frame())
    features = build_features(train.head(100))
    forbidden = {"relevance", "action", "dwell_time_seconds", "interaction_id", "profile_id", "event_id"}
    assert forbidden.isdisjoint(features.columns)
    assert features.notna().all().all()


def test_rule_metrics_are_bounded():
    _, _, test = temporal_split(load_interaction_frame())
    features = build_features(test.head(1_000))
    metrics = evaluate(test.head(1_000), rule_based_scores(features))
    assert set(metrics) == {"roc_auc", "precision_at_5", "ndcg_at_10"}
    assert all(0 <= value <= 1 for value in metrics.values())


def test_micro_kmeans_is_deterministic_and_non_degenerate():
    first = run_kmeans_experiment()
    second = run_kmeans_experiment()
    assert first == second
    assert first["event_count"] == 170
    assert 2 <= first["selected_clusters"] <= 8
    assert first["silhouette"] > 0
    assert sum(first["cluster_sizes"].values()) == 170
    assert first["production_decision"] == "experiment_only"
