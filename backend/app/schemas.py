"""API istek ve cevap sözleşmeleri.

Alan adları `data/schemas/profile_v2.schema.json` ile aynı snake_case biçimini kullanır;
mobil uygulama gövdeyi bu biçimde gönderir.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

InteractionAction = Literal["like", "skip", "save", "unsave", "view_detail", "apply"]


class ProfileInput(BaseModel):
    """Öğrenci profili. Onboarding akışının çıktısıdır."""

    schema_version: Literal["2.0"] = "2.0"
    education_reference_version: str = Field(min_length=1)
    display_name: str = ""
    university_id: str = Field(min_length=1)
    university_name: str = Field(min_length=1)
    program_id: str = Field(min_length=1)
    program_name: str = Field(min_length=1)
    education_level: Literal["associate", "bachelor", "master", "doctorate"]
    program_duration: int = Field(ge=2, le=6)
    class_year: str = Field(pattern=r"^(prep|[1-6])$")
    interest_ids: list[str] = Field(min_length=3, max_length=10)
    participation_goal_ids: list[str] = Field(min_length=1)
    participation_modes: list[Literal["onsite", "online", "hybrid"]] = Field(min_length=1)
    fee_preference: Literal["free_only", "paid_ok", "no_preference"]
    language_preference: Literal["tr", "en", "no_preference"]
    campus_id: str | None = None


class InteractionInput(BaseModel):
    """Keşif ekranındaki kullanıcı hareketi."""

    profile_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    action: InteractionAction
    dwell_ms: int | None = Field(default=None, ge=0)
    interaction_key: str | None = Field(default=None, min_length=8, max_length=100)
    feed_token: str | None = Field(default=None, min_length=8, max_length=100)


class MicroEventInput(BaseModel):
    """Doğrulanmış öğrenci tarafından oluşturulan kısa ömürlü etkinlik."""

    creator_profile_id: str = Field(min_length=1)
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    category_id: str = Field(min_length=1, max_length=80)
    interest_ids: list[str] = Field(min_length=1, max_length=10)
    starts_at: str
    ends_at: str
    expires_at: str
    participation_mode: Literal["onsite", "online", "hybrid"]
    location_name: str = Field(min_length=2, max_length=200)
    quota: int = Field(ge=1, le=500)
    language: Literal["tr", "en", "mixed"] = "tr"
    target_goal_ids: list[str] = []

    @model_validator(mode="after")
    def validate_timeline(self):
        from datetime import datetime, timezone

        try:
            starts_at = datetime.fromisoformat(self.starts_at.replace("Z", "+00:00"))
            ends_at = datetime.fromisoformat(self.ends_at.replace("Z", "+00:00"))
            expires_at = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Tarih alanları ISO-8601 biçiminde olmalıdır.") from exc
        if not starts_at.tzinfo or not ends_at.tzinfo or not expires_at.tzinfo:
            raise ValueError("Tarih alanları saat dilimi içermelidir.")
        if not starts_at < ends_at <= expires_at:
            raise ValueError("Zaman sırası starts_at < ends_at <= expires_at olmalıdır.")
        if starts_at <= datetime.now(timezone.utc):
            raise ValueError("Mikro etkinlik başlangıcı gelecekte olmalıdır.")
        return self


class MicroEventUpdate(MicroEventInput):
    """MVP'de tutarlı validasyon için mikro etkinliğin tam güncelleme gövdesi."""


class ParticipationInput(BaseModel):
    profile_id: str = Field(min_length=1)


class ParticipationStatusInput(BaseModel):
    actor_profile_id: str = Field(min_length=1)
    status: Literal["approved", "rejected", "cancelled", "attended", "no_show"]


class RatingInput(BaseModel):
    profile_id: str = Field(min_length=1)
    score: int = Field(ge=1, le=5)


class OrganizerVerificationInput(BaseModel):
    verification_status: Literal["pending", "verified", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class OfficialEventApprovalInput(BaseModel):
    approval_status: Literal["pending", "approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[dict[str, Any]] = []


class ErrorResponse(BaseModel):
    error: ErrorDetail
