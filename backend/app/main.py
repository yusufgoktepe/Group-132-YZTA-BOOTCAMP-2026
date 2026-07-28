"""CampusMatch AI FastAPI uygulaması.

Veri kaynağı SQLite'tır. Kulüp ve etkinlik referans verisi açılışta
`data/sample` altındaki CSV dosyalarından aktarılır; profiller ve kullanıcı
hareketleri veritabanında kalıcı olarak saklanır.
"""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import repository
from .db import get_connection, get_db_path, init_db
from .errors import error_body, register_error_handlers
from .recommendation_service import recommend_for_profile, recommend_for_student
from .schemas import InteractionInput, ProfileInput


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.seed_counts = init_db()
    yield


app = FastAPI(title="CampusMatch AI API", version="3.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)


def _not_found(code: str, message: str) -> HTTPException:
    return HTTPException(status_code=404, detail=error_body(code, message))


def _load_profile(connection: sqlite3.Connection, profile_id: str) -> dict:
    profile = repository.get_profile(connection, profile_id)
    if profile is None:
        raise _not_found("profile_not_found", f"'{profile_id}' kimlikli profil bulunamadı.")
    return profile


# --- Sağlık ---------------------------------------------------------------


@app.get("/health")
def health_check(connection: sqlite3.Connection = Depends(get_connection)):
    return {
        "status": "ok",
        "message": "CampusMatch AI backend is running",
        "database": {"path": str(get_db_path()), "counts": repository.interaction_counts(connection)},
    }


# --- Referans veri --------------------------------------------------------


@app.get("/students")
def get_students(connection: sqlite3.Connection = Depends(get_connection)):
    return {"students": repository.list_students(connection)}


@app.get("/clubs")
def get_clubs(connection: sqlite3.Connection = Depends(get_connection)):
    return {"clubs": repository.list_clubs(connection)}


@app.get("/events")
def get_events(
    category: str | None = Query(default=None, description="Etkinlik kategorisine göre filtreler."),
    connection: sqlite3.Connection = Depends(get_connection),
):
    events = repository.list_events(connection)
    if category:
        events = [event for event in events if event["category"].lower() == category.lower()]
    return {"count": len(events), "events": events}


@app.get("/events/{event_id}")
def get_event(event_id: str, connection: sqlite3.Connection = Depends(get_connection)):
    event = repository.get_event(connection, event_id)
    if event is None:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.")
    return event


# --- Profiller ------------------------------------------------------------


@app.post("/profiles", status_code=201)
def create_profile(
    profile: ProfileInput, connection: sqlite3.Connection = Depends(get_connection)
):
    return repository.create_profile(connection, profile.model_dump())


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: str, connection: sqlite3.Connection = Depends(get_connection)):
    return _load_profile(connection, profile_id)


@app.put("/profiles/{profile_id}")
def update_profile(
    profile_id: str,
    profile: ProfileInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    updated = repository.update_profile(connection, profile_id, profile.model_dump())
    if updated is None:
        raise _not_found("profile_not_found", f"'{profile_id}' kimlikli profil bulunamadı.")
    return updated


# --- Kullanıcı hareketleri ------------------------------------------------


@app.post("/interactions", status_code=201)
def create_interaction(
    interaction: InteractionInput, connection: sqlite3.Connection = Depends(get_connection)
):
    _load_profile(connection, interaction.profile_id)
    if not repository.event_exists(connection, interaction.event_id):
        raise _not_found(
            "event_not_found", f"'{interaction.event_id}' kimlikli etkinlik bulunamadı."
        )

    return repository.record_interaction(
        connection,
        interaction.profile_id,
        interaction.event_id,
        interaction.action,
        interaction.dwell_ms,
    )


@app.get("/profiles/{profile_id}/interactions")
def get_interactions(
    profile_id: str,
    action: str | None = Query(default=None, description="like, skip, save, unsave, view_detail"),
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, profile_id)
    interactions = repository.list_interactions(connection, profile_id, action)
    return {"count": len(interactions), "interactions": interactions}


@app.get("/profiles/{profile_id}/saved-events")
def get_saved_events(
    profile_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    _load_profile(connection, profile_id)
    events = repository.saved_events(connection, profile_id)
    return {"count": len(events), "events": events}


# --- Öneriler -------------------------------------------------------------


@app.post("/recommendations/profile")
def get_profile_recommendations(
    profile: ProfileInput, connection: sqlite3.Connection = Depends(get_connection)
):
    """Kaydedilmemiş profil için öneri üretir. Mobil uygulamanın kullandığı uçtur."""
    return recommend_for_profile(connection, profile.model_dump())


@app.post("/recommendations/profile/{profile_id}")
def get_saved_profile_recommendations(
    profile_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    """Kayıtlı profil için öneri üretir; kullanıcının geçmiş hareketlerini de dikkate alır."""
    profile = _load_profile(connection, profile_id)
    return recommend_for_profile(connection, profile, profile_id=profile_id)


@app.post("/recommendations/student/{student_id}")
def get_student_recommendations(
    student_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    result = recommend_for_student(connection, student_id)
    if result is None:
        raise _not_found("student_not_found", f"'{student_id}' kimlikli öğrenci bulunamadı.")
    return result
