"""CampusMatch AI FastAPI uygulaması.

Veri kaynağı SQLite'tır. Kulüp ve etkinlik referans verisi açılışta
`data/sample` altındaki CSV dosyalarından aktarılır; profiller ve kullanıcı
hareketleri veritabanında kalıcı olarak saklanır.
"""

from __future__ import annotations

import sqlite3
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import repository
from .db import get_connection, get_db_path, init_db
from .errors import error_body, register_error_handlers
from .feed_service import build_feed
from .recommendation_service import recommend_for_profile, recommend_for_student
from .schemas import (
    InteractionInput,
    MicroEventInput,
    MicroEventUpdate,
    ParticipationInput,
    ParticipationStatusInput,
    ProfileInput,
    RatingInput,
    OrganizerVerificationInput,
    OfficialEventApprovalInput,
)


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


def _require_moderator(x_moderator_key: str | None = Header(default=None)) -> None:
    configured = os.getenv("CAMPUSMATCH_MODERATOR_KEY")
    if not configured:
        raise HTTPException(
            status_code=503,
            detail=error_body("moderation_not_configured", "Moderasyon anahtarı yapılandırılmamış."),
        )
    if not x_moderator_key or not secrets.compare_digest(x_moderator_key, configured):
        raise HTTPException(
            status_code=403, detail=error_body("moderator_authorization_required", "Geçersiz moderasyon anahtarı.")
        )


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


@app.post("/events", status_code=201)
def create_event(
    payload: MicroEventInput, connection: sqlite3.Connection = Depends(get_connection)
):
    profile = _load_profile(connection, payload.creator_profile_id)
    try:
        return repository.create_micro_event(connection, profile, payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=error_body("organizer_not_allowed", str(exc))) from exc


@app.put("/events/{event_id}")
def update_event(
    event_id: str,
    payload: MicroEventUpdate,
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, payload.creator_profile_id)
    try:
        return repository.update_micro_event(
            connection, event_id, payload.creator_profile_id, payload.model_dump()
        )
    except LookupError as exc:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=error_body("event_owner_required", str(exc))) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=error_body("event_not_editable", str(exc))) from exc


@app.delete("/events/{event_id}")
def cancel_event(
    event_id: str,
    actor_profile_id: str = Query(min_length=1),
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, actor_profile_id)
    try:
        return repository.cancel_micro_event(connection, event_id, actor_profile_id)
    except LookupError as exc:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=error_body("event_owner_required", str(exc))) from exc


@app.post("/events/{event_id}/apply", status_code=201)
def apply_to_event(
    event_id: str,
    payload: ParticipationInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, payload.profile_id)
    try:
        participation, is_duplicate = repository.request_participation(
            connection, payload.profile_id, event_id
        )
        repository.record_interaction(
            connection,
            payload.profile_id,
            event_id,
            "apply",
            interaction_key=f"participation-{participation['participation_id']}",
        )
        return {**participation, "is_duplicate": is_duplicate}
    except LookupError as exc:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.") from exc
    except OverflowError as exc:
        raise HTTPException(status_code=409, detail=error_body("event_quota_full", str(exc))) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=error_body("event_not_open", str(exc))) from exc


@app.get("/profiles/{profile_id}/participations")
def get_participations(
    profile_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    _load_profile(connection, profile_id)
    items = repository.list_participations(connection, profile_id)
    return {"count": len(items), "participations": items}


@app.patch("/participations/{participation_id}")
def update_participation(
    participation_id: str,
    payload: ParticipationStatusInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, payload.actor_profile_id)
    try:
        return repository.update_participation_status(
            connection, participation_id, payload.actor_profile_id, payload.status
        )
    except LookupError as exc:
        raise _not_found(
            "participation_not_found", f"'{participation_id}' kimlikli katılım bulunamadı."
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=403, detail=error_body("participation_owner_required", str(exc))
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=409, detail=error_body("invalid_participation_transition", str(exc))
        ) from exc


@app.post("/events/{event_id}/ratings", status_code=201)
def rate_event(
    event_id: str,
    payload: RatingInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    _load_profile(connection, payload.profile_id)
    try:
        return repository.create_rating(connection, event_id, payload.profile_id, payload.score)
    except LookupError as exc:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=error_body("verified_attendance_required", str(exc))) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=error_body("rating_already_exists", str(exc))) from exc


@app.get("/organizers/{organizer_id}/trust-summary")
def get_organizer_trust_summary(
    organizer_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    summary = repository.organizer_trust_summary(connection, organizer_id)
    if not summary:
        raise _not_found("organizer_not_found", f"'{organizer_id}' kimlikli organizatör bulunamadı.")
    return summary


@app.patch("/organizers/{organizer_id}/verification", dependencies=[Depends(_require_moderator)])
def verify_organizer(
    organizer_id: str,
    payload: OrganizerVerificationInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    try:
        return repository.set_organizer_verification(
            connection, organizer_id, payload.verification_status, payload.reason
        )
    except LookupError as exc:
        raise _not_found("organizer_not_found", f"'{organizer_id}' kimlikli organizatör bulunamadı.") from exc


@app.patch("/events/{event_id}/approval", dependencies=[Depends(_require_moderator)])
def approve_official_event(
    event_id: str,
    payload: OfficialEventApprovalInput,
    connection: sqlite3.Connection = Depends(get_connection),
):
    try:
        return repository.set_official_event_approval(
            connection, event_id, payload.approval_status, payload.reason
        )
    except LookupError as exc:
        raise _not_found("event_not_found", f"'{event_id}' kimlikli etkinlik bulunamadı.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=error_body("official_event_required", str(exc))) from exc


@app.get("/moderation/actions", dependencies=[Depends(_require_moderator)])
def get_moderation_actions(connection: sqlite3.Connection = Depends(get_connection)):
    actions = repository.list_moderation_actions(connection)
    return {"count": len(actions), "actions": actions}


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

    try:
        return repository.record_interaction(
            connection,
            interaction.profile_id,
            interaction.event_id,
            interaction.action,
            interaction.dwell_ms,
            interaction.interaction_key,
            interaction.feed_token,
        )
    except repository.InteractionKeyConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=error_body("interaction_key_conflict", str(exc)),
        ) from exc


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


@app.get("/profiles/{profile_id}/interest-weights")
def get_interest_weights(
    profile_id: str, connection: sqlite3.Connection = Depends(get_connection)
):
    """Faz 4 davranış öğrenmesini demo ve hata ayıklama için görünür kılar."""
    _load_profile(connection, profile_id)
    weights = repository.list_interest_weights(connection, profile_id)
    return {"schema_version": "3.0", "profile_id": profile_id, "weights": weights}


# --- Kişiselleştirilmiş feed ---------------------------------------------


@app.get("/feed")
def get_feed(
    profile_id: str = Query(min_length=1),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=30),
    connection: sqlite3.Connection = Depends(get_connection),
):
    profile = _load_profile(connection, profile_id)
    try:
        return build_feed(connection, profile, cursor=cursor, limit=limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=error_body("invalid_feed_cursor", str(exc)),
        ) from exc


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
