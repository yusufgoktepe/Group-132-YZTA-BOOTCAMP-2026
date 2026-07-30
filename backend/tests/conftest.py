"""Test altyapısı: her test oturumu geçici bir SQLite dosyası kullanır."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Boş bir veritabanı üzerinde çalışan TestClient.

    `CAMPUSMATCH_DB_PATH` uygulama içe aktarılmadan önce ayarlanır; böylece
    geliştirme veritabanı testlerden etkilenmez.
    """
    monkeypatch.setenv("CAMPUSMATCH_DB_PATH", str(tmp_path / "test.sqlite"))

    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def valid_profile() -> dict:
    return {
        "schema_version": "2.0",
        "education_reference_version": "sample-2026-07",
        "display_name": "Zeynep Demir",
        "university_id": "yok-hacettepe",
        "university_name": "Hacettepe Üniversitesi",
        "program_id": "hacettepe-ai",
        "program_name": "Yapay Zekâ Mühendisliği",
        "education_level": "bachelor",
        "program_duration": 4,
        "class_year": "2",
        "interest_ids": ["ai", "data-science", "mobile-development"],
        "participation_goal_ids": ["learn", "career"],
        "participation_modes": ["onsite", "hybrid"],
        "fee_preference": "free_only",
        "language_preference": "tr",
        "campus_id": None,
    }


@pytest.fixture()
def created_profile(client, valid_profile) -> dict:
    response = client.post("/profiles", json=valid_profile)
    assert response.status_code == 201
    return response.json()
