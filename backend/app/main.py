from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .recommendation_service import (
    list_clubs,
    list_events,
    list_students,
    recommend_for_profile,
    recommend_for_student,
)


class ProfileRecommendationRequest(BaseModel):
    schema_version: Literal["2.0"] = "2.0"
    education_reference_version: str
    display_name: str = ""
    university_id: str
    university_name: str
    program_id: str
    program_name: str
    education_level: Literal["associate", "bachelor", "master", "doctorate"]
    program_duration: int = Field(ge=2, le=6)
    class_year: str = Field(pattern=r"^(prep|[1-6])$")
    interest_ids: list[str] = Field(min_length=3, max_length=10)
    participation_goal_ids: list[str] = Field(min_length=1)
    participation_modes: list[Literal["onsite", "online", "hybrid"]] = Field(min_length=1)
    fee_preference: Literal["free_only", "paid_ok", "no_preference"]
    language_preference: Literal["tr", "en", "no_preference"]
    campus_id: str | None = None

app = FastAPI(title="CampusMatch AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "CampusMatch AI backend is running"}


@app.get("/students")
def get_students():
    return {"students": list_students()}


@app.get("/events")
def get_events():
    return {"events": list_events()}


@app.get("/clubs")
def get_clubs():
    return {"clubs": list_clubs()}


@app.post("/recommendations/student/{student_id}")
def get_student_recommendations(student_id: str):
    result = recommend_for_student(student_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@app.post("/recommendations/profile")
def get_profile_recommendations(profile: ProfileRecommendationRequest):
    return recommend_for_profile(profile.model_dump())
