"""API istek ve cevap sözleşmeleri.

Alan adları `data/schemas/profile_v2.schema.json` ile aynı snake_case biçimini kullanır;
mobil uygulama gövdeyi bu biçimde gönderir.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

InteractionAction = Literal["like", "skip", "save", "unsave", "view_detail"]


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


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[dict[str, Any]] = []


class ErrorResponse(BaseModel):
    error: ErrorDetail
